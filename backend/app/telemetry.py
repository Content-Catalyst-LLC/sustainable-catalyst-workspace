from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ExecutionPolicyDecision, JobRecord, ReproductionExecutionPlan, RuntimeExecutionAttestation, RuntimeHandoffReceipt
from .schemas import RuntimeExecutionAttestationRequest
from .utils import iso, sha256_hex

TERMINAL = {"succeeded", "failed", "blocked", "cancelled"}
BUDGET_CHECK_NAMES = {
    "cpuCoreSeconds": "budget-cpuCoreSeconds",
    "peakMemoryMb": "budget-peakMemoryMb",
    "wallSeconds": "budget-wallSeconds",
    "outputBytes": "budget-outputBytes",
    "pidsPeak": "budget-pidsPeak",
    "tempStorageMbPeak": "budget-tempStorageMbPeak",
}
SANDBOX_CHECK_NAMES = {
    "mode": "sandbox-mode",
    "networkMode": "sandbox-networkMode",
    "readOnlyRootFilesystem": "sandbox-readOnlyRootFilesystem",
    "noNewPrivileges": "sandbox-noNewPrivileges",
    "dropAllCapabilities": "sandbox-dropAllCapabilities",
    "hostFilesystemAccess": "sandbox-hostFilesystemAccess",
    "dockerSocketAccess": "sandbox-dockerSocketAccess",
    "privilegedExecution": "sandbox-privilegedExecution",
    "pinnedContainer": "sandbox-pinnedContainer",
}


def _now():
    return datetime.now(timezone.utc)


def attestation_metadata(row: RuntimeExecutionAttestation) -> dict:
    return {
        "attestationId": row.attestation_id,
        "handoffReceiptId": row.handoff_receipt_id,
        "executionPlanId": row.execution_plan_id,
        "reproductionRunId": row.reproduction_run_id,
        "jobId": row.job_id,
        "policyDecisionId": row.policy_decision_id,
        "policyDecisionFingerprint": row.policy_decision_fingerprint,
        "source": row.source,
        "classification": row.classification,
        "executionSucceeded": bool(row.execution_succeeded),
        "budgetCompliant": bool(row.budget_compliant),
        "sandboxCompliant": bool(row.sandbox_compliant),
        "observedUsage": row.observed_usage_json,
        "budgetAccounting": row.budget_accounting_json,
        "sandboxAttestation": row.sandbox_attestation_json,
        "checks": row.checks_json,
        "notes": row.notes,
        "fingerprint": row.fingerprint,
        "createdAt": iso(row.created_at),
    }


def _metric(name, observed, limit, checks, accounting, required=True):
    if observed is None:
        checks.append({"check": BUDGET_CHECK_NAMES[name], "status": "unknown", "reason": "runtime metric not reported"})
        accounting[name] = {"limit": limit, "observed": None, "headroom": None, "utilizationPct": None}
        return True
    ok = float(observed) <= float(limit)
    headroom = float(limit) - float(observed)
    pct = None if float(limit) == 0 else round((float(observed) / float(limit)) * 100.0, 4)
    accounting[name] = {"limit": limit, "observed": observed, "headroom": headroom, "utilizationPct": pct}
    checks.append({"check": BUDGET_CHECK_NAMES[name], "status": "pass" if ok else "fail", "limit": limit, "observed": observed})
    return ok


def evaluate_runtime_attestation(decision: ExecutionPolicyDecision, job: JobRecord, payload: RuntimeExecutionAttestationRequest) -> dict:
    budget = decision.resource_budget_json or {}
    usage = payload.observedUsage.model_dump()
    sandbox = payload.sandboxAttestation.model_dump()
    expected = decision.sandbox_json or {}
    checks = []
    accounting = {}

    budget_ok = True
    cpu_limit = float(budget.get("cpuCores", 0)) * float(budget.get("wallSeconds", 0))
    budget_ok = _metric("cpuCoreSeconds", usage.get("cpuCoreSeconds"), cpu_limit, checks, accounting) and budget_ok
    budget_ok = _metric("peakMemoryMb", usage.get("peakMemoryMb"), int(budget.get("memoryMb", 0)), checks, accounting) and budget_ok
    budget_ok = _metric("wallSeconds", usage.get("wallSeconds"), float(budget.get("wallSeconds", 0)), checks, accounting) and budget_ok
    budget_ok = _metric("outputBytes", usage.get("outputBytes"), int(budget.get("outputBytes", 0)), checks, accounting) and budget_ok
    budget_ok = _metric("pidsPeak", usage.get("pidsPeak"), int(budget.get("pids", 0)), checks, accounting) and budget_ok
    budget_ok = _metric("tempStorageMbPeak", usage.get("tempStorageMbPeak"), int(budget.get("tempStorageMb", 0)), checks, accounting) and budget_ok

    sandbox_checks = {
        "mode": sandbox.get("mode") == expected.get("mode"),
        "networkMode": sandbox.get("networkMode") == expected.get("networkMode"),
        "readOnlyRootFilesystem": (not expected.get("readOnlyRootFilesystem", False)) or bool(sandbox.get("readOnlyRootFilesystem")),
        "noNewPrivileges": (not expected.get("noNewPrivileges", False)) or bool(sandbox.get("noNewPrivileges")),
        "dropAllCapabilities": (not expected.get("dropAllCapabilities", False)) or bool(sandbox.get("dropAllCapabilities")),
        "hostFilesystemAccess": sandbox.get("hostFilesystemAccess") is False,
        "dockerSocketAccess": sandbox.get("dockerSocketAccess") is False,
        "privilegedExecution": sandbox.get("privilegedExecution") is False,
        "pinnedContainer": (not expected.get("requirePinnedContainer", False)) or bool(sandbox.get("pinnedContainer")),
    }
    for name, ok in sandbox_checks.items():
        checks.append({"check": SANDBOX_CHECK_NAMES[name], "status": "pass" if ok else "fail"})
    sandbox_ok = all(sandbox_checks.values())
    execution_succeeded = job.status == "succeeded"
    checks.append({"check": "job-terminal-state", "status": "pass" if job.status in TERMINAL else "fail", "statusValue": job.status})
    checks.append({"check": "job-succeeded", "status": "pass" if execution_succeeded else "fail", "statusValue": job.status})

    missing = any(x["status"] == "unknown" for x in checks)
    if not execution_succeeded:
        classification = "execution-failed"
    elif not budget_ok:
        classification = "budget-exceeded"
    elif not sandbox_ok:
        classification = "sandbox-deviation"
    elif missing:
        classification = "incomplete"
    else:
        classification = "compliant"
    return {
        "classification": classification,
        "executionSucceeded": execution_succeeded,
        "budgetCompliant": bool(budget_ok and not missing),
        "sandboxCompliant": sandbox_ok,
        "observedUsage": usage,
        "budgetAccounting": accounting,
        "sandboxAttestation": sandbox,
        "checks": checks,
    }


def create_runtime_attestation(db: Session, user_key: str, handoff_receipt_id: str, payload: RuntimeExecutionAttestationRequest):
    receipt = db.get(RuntimeHandoffReceipt, {"user_key": user_key, "receipt_id": handoff_receipt_id})
    if receipt is None:
        raise HTTPException(status_code=404, detail="Workspace runtime-handoff receipt not found.")
    existing = db.scalar(select(RuntimeExecutionAttestation).where(RuntimeExecutionAttestation.user_key == user_key, RuntimeExecutionAttestation.handoff_receipt_id == handoff_receipt_id))
    if existing is not None:
        return existing, True
    count = int(db.scalar(select(func.count()).select_from(RuntimeExecutionAttestation).where(RuntimeExecutionAttestation.user_key == user_key)) or 0)
    if count >= get_settings().max_runtime_execution_attestations_per_account:
        raise HTTPException(status_code=409, detail="Workspace runtime-execution attestation limit reached.")
    plan = db.get(ReproductionExecutionPlan, {"user_key": user_key, "execution_plan_id": receipt.execution_plan_id})
    if plan is None:
        raise HTTPException(status_code=409, detail="Runtime handoff no longer has its frozen execution plan.")
    details = receipt.details_json or {}
    decision_id = str(details.get("executionPolicyDecisionId") or "")
    decision = db.get(ExecutionPolicyDecision, {"user_key": user_key, "decision_id": decision_id})
    if decision is None or not decision.eligible:
        raise HTTPException(status_code=409, detail="Runtime handoff no longer has an eligible frozen policy decision.")
    if decision.fingerprint != str(details.get("executionPolicyDecisionFingerprint") or ""):
        raise HTTPException(status_code=409, detail="Runtime handoff policy decision fingerprint no longer matches its receipt.")
    job = db.get(JobRecord, {"user_key": user_key, "job_id": receipt.job_id})
    if job is None or job.status not in TERMINAL:
        raise HTTPException(status_code=409, detail="Runtime execution must be terminal before attestation can be recorded.")
    evaluation = evaluate_runtime_attestation(decision, job, payload)
    attestation_id = (payload.attestationId or f"runtime-attestation-{uuid4()}").strip()
    if db.get(RuntimeExecutionAttestation, {"user_key": user_key, "attestation_id": attestation_id}) is not None:
        raise HTTPException(status_code=409, detail="Workspace runtime-execution attestation id already exists.")
    document = {
        "handoffReceiptId": receipt.receipt_id,
        "executionPlanId": receipt.execution_plan_id,
        "runId": receipt.reproduction_run_id,
        "jobId": receipt.job_id,
        "policyDecisionId": decision.decision_id,
        "policyDecisionFingerprint": decision.fingerprint,
        "source": payload.source,
        **evaluation,
        "notes": payload.notes,
    }
    row = RuntimeExecutionAttestation(
        user_key=user_key,
        attestation_id=attestation_id,
        handoff_receipt_id=receipt.receipt_id,
        execution_plan_id=receipt.execution_plan_id,
        reproduction_run_id=receipt.reproduction_run_id,
        job_id=receipt.job_id,
        policy_decision_id=decision.decision_id,
        policy_decision_fingerprint=decision.fingerprint,
        source=payload.source,
        classification=evaluation["classification"],
        execution_succeeded=evaluation["executionSucceeded"],
        budget_compliant=evaluation["budgetCompliant"],
        sandbox_compliant=evaluation["sandboxCompliant"],
        observed_usage_json=evaluation["observedUsage"],
        budget_accounting_json=evaluation["budgetAccounting"],
        sandbox_attestation_json=evaluation["sandboxAttestation"],
        checks_json=evaluation["checks"],
        notes=payload.notes,
        fingerprint=sha256_hex(document),
        created_at=_now(),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A concurrent Workspace runtime-execution attestation was detected.")
    db.refresh(row)
    return row, False


def get_runtime_attestation(db: Session, user_key: str, attestation_id: str):
    return db.get(RuntimeExecutionAttestation, {"user_key": user_key, "attestation_id": attestation_id})


def list_runtime_attestations(db: Session, user_key: str):
    rows = db.scalars(select(RuntimeExecutionAttestation).where(RuntimeExecutionAttestation.user_key == user_key).order_by(RuntimeExecutionAttestation.created_at.desc())).all()
    return [attestation_metadata(row) for row in rows]
