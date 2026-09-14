from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .jobs import create_job, job_metadata
from .models import ExecutionRun, ReproductionExecutionPlan, ReproductionPlan, RuntimeAdapterRevision, RuntimeHandoffReceipt
from .policy import evaluate_policy, get_policy_decision, policy_decision_metadata, resolve_policy_ref
from .routing import route_registry
from .schemas import ControlledRuntimeHandoffRequest, JobCreateRequest, ReproductionExecutionPlanCreateRequest
from .utils import iso, sha256_hex


def _now():
    return datetime.now(timezone.utc)


def execution_plan_metadata(row: ReproductionExecutionPlan) -> dict:
    return {
        "executionPlanId": row.execution_plan_id,
        "reproductionPlanId": row.reproduction_plan_id,
        "originalRunId": row.original_run_id,
        "reproductionRunId": row.reproduction_run_id,
        "status": row.status,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "fingerprint": row.fingerprint,
        "inputFingerprint": row.input_fingerprint,
        "environmentFingerprint": row.environment_fingerprint,
        "runtimeAdapterFingerprint": row.runtime_adapter_fingerprint,
        "environmentRef": row.environment_ref,
        "runtimeAdapterRef": row.runtime_adapter_ref,
        "jobRequest": row.job_request_json,
        "readiness": row.readiness_json,
        "policy": row.policy_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def handoff_receipt_metadata(row: RuntimeHandoffReceipt) -> dict:
    return {
        "receiptId": row.receipt_id,
        "executionPlanId": row.execution_plan_id,
        "reproductionRunId": row.reproduction_run_id,
        "jobId": row.job_id,
        "status": row.status,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "routeTransport": row.route_transport,
        "requestFingerprint": row.request_fingerprint,
        "fingerprint": row.fingerprint,
        "details": row.details_json,
        "createdAt": iso(row.created_at),
    }


def _adapter_capability_check(db: Session, user_key: str, run: ExecutionRun) -> dict:
    ref = run.runtime_adapter_ref or {}
    adapter_id = str(ref.get("adapterId") or "")
    revision = int(ref.get("revision") or 0)
    if not adapter_id or not revision:
        return {"check": "runtime-adapter-capability", "status": "fail", "reason": "missing-runtime-adapter"}
    adapter = db.get(RuntimeAdapterRevision, {"user_key": user_key, "adapter_id": adapter_id, "revision": revision})
    if adapter is None:
        return {"check": "runtime-adapter-capability", "status": "fail", "reason": "runtime-adapter-revision-unavailable"}
    capabilities = [str(x) for x in (adapter.capabilities_json or [])]
    ok = run.operation in capabilities
    return {"check": "runtime-adapter-capability", "status": "pass" if ok else "fail", "required": run.operation, "available": capabilities}


def create_execution_plan(db: Session, user_key: str, payload: ReproductionExecutionPlanCreateRequest):
    settings = get_settings()
    repro_plan = db.get(ReproductionPlan, {"user_key": user_key, "plan_id": payload.reproductionPlanId})
    if repro_plan is None:
        raise HTTPException(status_code=404, detail="Workspace reproduction plan not found.")
    original = db.get(ExecutionRun, {"user_key": user_key, "run_id": repro_plan.original_run_id})
    reproduced = db.get(ExecutionRun, {"user_key": user_key, "run_id": payload.reproductionRunId})
    if original is None or reproduced is None:
        raise HTTPException(status_code=404, detail="Original and reproduction Workspace runs are required.")
    if reproduced.status not in {"planned", "blocked"}:
        raise HTTPException(status_code=409, detail="Controlled reproduction handoff requires a planned reproduction run.")

    count = int(db.scalar(select(func.count()).select_from(ReproductionExecutionPlan).where(ReproductionExecutionPlan.user_key == user_key)) or 0)
    if count >= settings.max_reproduction_execution_plans_per_account:
        raise HTTPException(status_code=409, detail="Workspace reproduction execution-plan limit reached.")

    target = original.target_product or reproduced.target_product or "workspace"
    operation = original.operation or reproduced.operation
    routes = route_registry()
    route = routes.get(target) or {"targetProduct": target, "configured": False, "transport": "unavailable", "serverConfiguredOnly": True}

    checks = []
    def add(name: str, ok: bool, **details):
        checks.append({"check": name, "status": "pass" if ok else "fail", **details})

    add("reproduction-plan-ready", repro_plan.status == "ready", actual=repro_plan.status)
    add("input-fingerprint", original.input_fingerprint == reproduced.input_fingerprint, original=original.input_fingerprint, reproduction=reproduced.input_fingerprint)
    add("environment-fingerprint", original.environment_fingerprint == reproduced.environment_fingerprint and bool(original.environment_fingerprint), original=original.environment_fingerprint, reproduction=reproduced.environment_fingerprint)
    add("runtime-adapter-fingerprint", original.runtime_adapter_fingerprint == reproduced.runtime_adapter_fingerprint and bool(original.runtime_adapter_fingerprint), original=original.runtime_adapter_fingerprint, reproduction=reproduced.runtime_adapter_fingerprint)
    add("target-product", original.target_product == reproduced.target_product, original=original.target_product, reproduction=reproduced.target_product)
    add("operation", original.operation == reproduced.operation and bool(operation), original=original.operation, reproduction=reproduced.operation)
    capability = _adapter_capability_check(db, user_key, reproduced)
    checks.append(capability)
    add("server-configured-route", bool(route.get("configured")), targetProduct=target, transport=route.get("transport", ""))
    compatibility = repro_plan.compatibility_json or {}
    add("runtime-environment-compatibility", compatibility.get("readiness") == "ready", readiness=compatibility.get("readiness", "unknown"))

    ready = all(item.get("status") == "pass" for item in checks)
    status_value = "ready" if ready else "blocked"
    execution_plan_id = (payload.executionPlanId or f"repro-exec-{uuid4()}").strip()
    if db.get(ReproductionExecutionPlan, {"user_key": user_key, "execution_plan_id": execution_plan_id}) is not None:
        raise HTTPException(status_code=409, detail="Workspace reproduction execution-plan id already exists.")

    policy_ref, policy_row = resolve_policy_ref(db, user_key, payload.executionPolicyRef)
    adapter_ref = reproduced.runtime_adapter_ref or {}
    adapter_row = db.get(RuntimeAdapterRevision, {"user_key": user_key, "adapter_id": str(adapter_ref.get("adapterId") or ""), "revision": int(adapter_ref.get("revision") or 0)})
    if adapter_row is None:
        raise HTTPException(status_code=409, detail="Reproduction run does not have an available frozen runtime adapter revision for policy evaluation.")
    policy_decision = evaluate_policy(
        db, user_key, execution_plan_id, policy_row, adapter_row, target, operation, payload.resourceBudget, route
    )
    checks.append({"check": "execution-policy", "status": "pass" if policy_decision.eligible else "fail", "classification": policy_decision.classification, "decisionId": policy_decision.decision_id})
    ready = ready and bool(policy_decision.eligible)
    status_value = "ready" if ready else "blocked"

    job_request = {
        "schema": "sc-workspace-job-request/1.0",
        "jobType": "workspace-task" if target == "workspace" else "compute-handoff",
        "targetProduct": target,
        "operation": operation,
        "projectId": reproduced.project_id or original.project_id,
        "priority": payload.priority,
        "maxAttempts": payload.maxAttempts,
        "idempotencyKey": f"reproduction-execution:{execution_plan_id}",
        "inputArtifactIds": [str(x)[:160] for x in payload.inputArtifactIds],
        "executionRunId": reproduced.run_id,
        "executionPolicy": {"policyRef": policy_ref, "decisionId": policy_decision.decision_id, "decisionFingerprint": policy_decision.fingerprint},
        "resourceBudget": payload.resourceBudget.model_dump(),
        "sandbox": policy_decision.sandbox_json,
        "payload": payload.payload,
    }
    policy = {
        "humanAuthorizationRequired": True,
        "automaticDispatch": False,
        "serverConfiguredRouteOnly": True,
        "clientSuppliedRouteUrlAllowed": False,
        "arbitraryCodeExecution": False,
        "credentialsAcceptedFromClient": False,
        "frozenTargetAndOperation": True,
        "executionPolicyRef": policy_ref,
        "executionPolicyDecisionId": policy_decision.decision_id,
        "executionPolicyDecisionFingerprint": policy_decision.fingerprint,
        "executionEligible": bool(policy_decision.eligible),
        "resourceBudget": payload.resourceBudget.model_dump(),
        "sandbox": policy_decision.sandbox_json,
    }
    readiness = {"ready": ready, "status": status_value, "checks": checks, "route": {k: v for k, v in route.items() if k != "serviceCredentialConfigured"}, "policyDecision": policy_decision_metadata(policy_decision)}
    fingerprint_doc = {
        "reproductionPlanId": repro_plan.plan_id,
        "originalRunId": original.run_id,
        "reproductionRunId": reproduced.run_id,
        "inputFingerprint": reproduced.input_fingerprint,
        "environmentFingerprint": reproduced.environment_fingerprint,
        "runtimeAdapterFingerprint": reproduced.runtime_adapter_fingerprint,
        "jobRequest": job_request,
        "policy": policy,
    }
    row = ReproductionExecutionPlan(
        user_key=user_key,
        execution_plan_id=execution_plan_id,
        reproduction_plan_id=repro_plan.plan_id,
        original_run_id=original.run_id,
        reproduction_run_id=reproduced.run_id,
        status=status_value,
        target_product=target,
        operation=operation,
        fingerprint=sha256_hex(fingerprint_doc),
        input_fingerprint=reproduced.input_fingerprint,
        environment_fingerprint=reproduced.environment_fingerprint,
        runtime_adapter_fingerprint=reproduced.runtime_adapter_fingerprint,
        environment_ref=reproduced.environment_ref or {},
        runtime_adapter_ref=reproduced.runtime_adapter_ref or {},
        job_request_json=job_request,
        readiness_json=readiness,
        policy_json={**policy, "notes": payload.notes},
        created_at=_now(), updated_at=_now(),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A concurrent Workspace reproduction execution plan was detected.")
    db.refresh(row)
    return row


def get_execution_plan(db: Session, user_key: str, execution_plan_id: str):
    return db.get(ReproductionExecutionPlan, {"user_key": user_key, "execution_plan_id": execution_plan_id})


def list_execution_plans(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(ReproductionExecutionPlan).where(ReproductionExecutionPlan.user_key == user_key).order_by(ReproductionExecutionPlan.created_at.desc())).all()
    return [execution_plan_metadata(row) for row in rows]


def dispatch_execution_plan(db: Session, user_key: str, execution_plan_id: str, payload: ControlledRuntimeHandoffRequest):
    row = get_execution_plan(db, user_key, execution_plan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace reproduction execution plan not found.")
    if row.status not in {"ready", "dispatched"}:
        raise HTTPException(status_code=409, detail="Workspace reproduction execution plan is not ready for controlled handoff.")

    existing = db.scalar(select(RuntimeHandoffReceipt).where(RuntimeHandoffReceipt.user_key == user_key, RuntimeHandoffReceipt.execution_plan_id == execution_plan_id).order_by(RuntimeHandoffReceipt.created_at.desc()))
    if existing is not None:
        return existing, True, None
    receipt_count = int(db.scalar(select(func.count()).select_from(RuntimeHandoffReceipt).where(RuntimeHandoffReceipt.user_key == user_key)) or 0)
    if receipt_count >= get_settings().max_runtime_handoff_receipts_per_account:
        raise HTTPException(status_code=409, detail="Workspace runtime-handoff receipt limit reached.")

    current_run = db.get(ExecutionRun, {"user_key": user_key, "run_id": row.reproduction_run_id})
    if current_run is None or current_run.status not in {"planned", "blocked"}:
        raise HTTPException(status_code=409, detail="Reproduction run is no longer eligible for controlled handoff.")
    if current_run.input_fingerprint != row.input_fingerprint or current_run.environment_fingerprint != row.environment_fingerprint or current_run.runtime_adapter_fingerprint != row.runtime_adapter_fingerprint:
        raise HTTPException(status_code=409, detail="Reproduction run changed after execution-plan creation.")
    if current_run.target_product != row.target_product or current_run.operation != row.operation:
        raise HTTPException(status_code=409, detail="Reproduction target or operation changed after execution-plan creation.")

    frozen_policy = row.policy_json or {}
    decision_id = str(frozen_policy.get("executionPolicyDecisionId") or "")
    decision = get_policy_decision(db, user_key, decision_id) if decision_id else None
    if decision is None or not decision.eligible:
        raise HTTPException(status_code=409, detail="Workspace execution policy does not authorize this controlled handoff.")
    if decision.fingerprint != str(frozen_policy.get("executionPolicyDecisionFingerprint") or ""):
        raise HTTPException(status_code=409, detail="Workspace execution-policy decision fingerprint changed after execution-plan creation.")

    route = route_registry().get(row.target_product) or {}
    if not route.get("configured"):
        raise HTTPException(status_code=409, detail="The frozen Workspace runtime route is no longer configured.")

    job_payload = JobCreateRequest.model_validate(row.job_request_json)
    job, replayed = create_job(db, user_key, job_payload)
    receipt_id = (payload.receiptId or f"runtime-handoff-{uuid4()}").strip()
    if db.get(RuntimeHandoffReceipt, {"user_key": user_key, "receipt_id": receipt_id}) is not None:
        raise HTTPException(status_code=409, detail="Workspace runtime-handoff receipt id already exists.")

    details = {
        "reason": payload.reason,
        "humanAuthorized": True,
        "automaticDispatch": False,
        "serverConfiguredRouteOnly": True,
        "clientSuppliedRouteUrlAllowed": False,
        "arbitraryCodeExecution": False,
        "credentialsAcceptedFromClient": False,
        "jobReplayed": replayed,
        "executionPlanFingerprint": row.fingerprint,
        "executionPolicyDecisionId": decision.decision_id,
        "executionPolicyDecisionFingerprint": decision.fingerprint,
        "executionPolicyEligible": True,
        "resourceBudget": decision.resource_budget_json,
        "sandbox": decision.sandbox_json,
    }
    receipt_doc = {
        "executionPlanId": row.execution_plan_id,
        "reproductionRunId": row.reproduction_run_id,
        "jobId": job.job_id,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "routeTransport": route.get("transport", ""),
        "requestFingerprint": job.request_fingerprint,
        "details": details,
    }
    receipt = RuntimeHandoffReceipt(
        user_key=user_key, receipt_id=receipt_id, execution_plan_id=row.execution_plan_id,
        reproduction_run_id=row.reproduction_run_id, job_id=job.job_id, status=job.status,
        target_product=row.target_product, operation=row.operation, route_transport=str(route.get("transport") or ""),
        request_fingerprint=job.request_fingerprint, fingerprint=sha256_hex(receipt_doc), details_json=details, created_at=_now(),
    )
    db.add(receipt)
    row.status = "dispatched"
    row.updated_at = _now()
    db.commit()
    db.refresh(receipt)
    return receipt, False, job_metadata(job)


def get_handoff_receipt(db: Session, user_key: str, receipt_id: str):
    return db.get(RuntimeHandoffReceipt, {"user_key": user_key, "receipt_id": receipt_id})


def list_handoff_receipts(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(RuntimeHandoffReceipt).where(RuntimeHandoffReceipt.user_key == user_key).order_by(RuntimeHandoffReceipt.created_at.desc())).all()
    return [handoff_receipt_metadata(row) for row in rows]
