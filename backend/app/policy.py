from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ExecutionPolicyDecision, ExecutionPolicyHead, ExecutionPolicyRevision, RuntimeAdapterRevision
from .schemas import ExecutionPolicyStoreRequest, ResourceBudget
from .utils import iso, sha256_hex

TRUST_ORDER = {"untrusted": 0, "bounded": 1, "trusted": 2}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean(values: list[str], limit: int) -> list[str]:
    out, seen = [], set()
    for raw in values:
        value = str(raw).strip()[:160]
        if not value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out[:limit]


def policy_metadata(row) -> dict:
    return {
        "policyId": row.policy_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "revision": int(row.revision),
        "fingerprint": row.fingerprint,
        "allowedTargetProducts": row.allowed_targets_json,
        "allowedOperations": row.allowed_operations_json,
        "minimumAdapterTrust": row.minimum_adapter_trust,
        "resourceLimits": row.resource_limits_json,
        "sandbox": row.sandbox_json,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def policy_decision_metadata(row: ExecutionPolicyDecision) -> dict:
    return {
        "decisionId": row.decision_id,
        "executionPlanId": row.execution_plan_id,
        "policyRef": {"policyId": row.policy_id, "revision": int(row.policy_revision), "fingerprint": row.policy_fingerprint},
        "eligible": bool(row.eligible),
        "classification": row.classification,
        "resourceBudget": row.resource_budget_json,
        "sandbox": row.sandbox_json,
        "checks": row.checks_json,
        "fingerprint": row.fingerprint,
        "createdAt": iso(row.created_at),
    }


def _document(payload: ExecutionPolicyStoreRequest) -> dict:
    return {
        "allowedTargetProducts": _clean(payload.allowedTargetProducts, 20),
        "allowedOperations": _clean(payload.allowedOperations, 100),
        "minimumAdapterTrust": payload.minimumAdapterTrust,
        "resourceLimits": payload.resourceLimits.model_dump(),
        "sandbox": {
            "mode": payload.sandboxMode,
            "networkMode": payload.networkMode,
            "readOnlyRootFilesystem": payload.readOnlyRootFilesystem,
            "noNewPrivileges": payload.noNewPrivileges,
            "dropAllCapabilities": payload.dropAllCapabilities,
            "allowHostFilesystem": False,
            "allowDockerSocket": False,
            "allowPrivileged": False,
            "requirePinnedContainer": payload.requirePinnedContainer,
        },
    }


def store_policy(db: Session, user_key: str, payload: ExecutionPolicyStoreRequest):
    settings = get_settings()
    policy_id = payload.policyId.strip()
    existing = db.get(ExecutionPolicyHead, {"user_key": user_key, "policy_id": policy_id})
    operation_id = (payload.operationId or "").strip()
    document = _document(payload)
    fingerprint = sha256_hex(document)
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Execution-policy operationId was already used for a different policy.")
        return existing, True
    current = int(existing.revision) if existing is not None else 0
    if existing is None:
        if payload.expectedRevision not in (None, 0):
            raise HTTPException(status_code=409, detail={"message": "Workspace execution-policy revision conflict.", "currentRevision": 0, "current": None})
        count = int(db.scalar(select(func.count()).select_from(ExecutionPolicyHead).where(ExecutionPolicyHead.user_key == user_key)) or 0)
        if count >= settings.max_execution_policies_per_account:
            raise HTTPException(status_code=409, detail="Workspace execution-policy registry limit reached.")
    elif payload.expectedRevision is None or int(payload.expectedRevision) != current:
        raise HTTPException(status_code=409, detail={"message": "Workspace execution-policy revision conflict.", "currentRevision": current, "current": policy_metadata(existing)})

    revision = current + 1
    now = _now()
    values = dict(
        project_id=(payload.projectId or "").strip(),
        name=payload.name.strip(),
        description=payload.description.strip(),
        revision=revision,
        fingerprint=fingerprint,
        allowed_targets_json=document["allowedTargetProducts"],
        allowed_operations_json=document["allowedOperations"],
        minimum_adapter_trust=document["minimumAdapterTrust"],
        resource_limits_json=document["resourceLimits"],
        sandbox_json=document["sandbox"],
        metadata_json=payload.metadata,
    )
    if existing is None:
        existing = ExecutionPolicyHead(user_key=user_key, policy_id=policy_id, last_operation_id=operation_id, created_at=now, updated_at=now, **values)
        db.add(existing)
    else:
        for key, value in values.items():
            setattr(existing, key, value)
        existing.last_operation_id = operation_id
        existing.updated_at = now
    db.add(ExecutionPolicyRevision(user_key=user_key, policy_id=policy_id, operation_id=operation_id, created_at=now, **values))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A concurrent Workspace execution-policy revision was detected.")
    db.refresh(existing)
    return existing, False


def get_policy(db: Session, user_key: str, policy_id: str):
    return db.get(ExecutionPolicyHead, {"user_key": user_key, "policy_id": policy_id})


def get_policy_revision(db: Session, user_key: str, policy_id: str, revision: int):
    return db.get(ExecutionPolicyRevision, {"user_key": user_key, "policy_id": policy_id, "revision": revision})


def list_policies(db: Session, user_key: str, project_id: str | None = None) -> list[dict]:
    stmt = select(ExecutionPolicyHead).where(ExecutionPolicyHead.user_key == user_key)
    if project_id:
        stmt = stmt.where(ExecutionPolicyHead.project_id == project_id)
    rows = db.scalars(stmt.order_by(ExecutionPolicyHead.updated_at.desc())).all()
    return [policy_metadata(row) for row in rows]


def list_policy_revisions(db: Session, user_key: str, policy_id: str) -> list[dict]:
    rows = db.scalars(select(ExecutionPolicyRevision).where(ExecutionPolicyRevision.user_key == user_key, ExecutionPolicyRevision.policy_id == policy_id).order_by(ExecutionPolicyRevision.revision.desc())).all()
    return [policy_metadata(row) for row in rows]


def resolve_policy_ref(db: Session, user_key: str, ref):
    row = get_policy_revision(db, user_key, ref.policyId, ref.revision) if ref.revision else get_policy(db, user_key, ref.policyId)
    if row is None:
        raise HTTPException(status_code=409, detail="Execution plan references an unavailable Workspace execution policy.")
    return {"policyId": row.policy_id, "revision": int(row.revision), "fingerprint": row.fingerprint}, row


def _operation_allowed(patterns: list[str], operation: str) -> bool:
    if not patterns:
        return False
    if "*" in patterns:
        return True
    return operation in patterns


def _pinned_container(adapter_row) -> bool:
    container = adapter_row.container_json or {}
    digest = str(container.get("digest") or "").strip().lower()
    image = str(container.get("image") or "").strip().lower()
    return digest.startswith("sha256:") or "@sha256:" in image


def evaluate_policy(
    db: Session,
    user_key: str,
    execution_plan_id: str,
    policy_row,
    adapter_row: RuntimeAdapterRevision,
    target_product: str,
    operation: str,
    budget: ResourceBudget,
    route: dict,
):
    settings = get_settings()
    count = int(db.scalar(select(func.count()).select_from(ExecutionPolicyDecision).where(ExecutionPolicyDecision.user_key == user_key)) or 0)
    if count >= settings.max_execution_policy_decisions_per_account:
        raise HTTPException(status_code=409, detail="Workspace execution-policy decision limit reached.")

    checks = []
    def add(name: str, ok: bool, **details):
        checks.append({"check": name, "status": "pass" if ok else "fail", **details})

    add("target-product-allowed", target_product in (policy_row.allowed_targets_json or []), targetProduct=target_product, allowed=policy_row.allowed_targets_json or [])
    add("operation-allowed", _operation_allowed(policy_row.allowed_operations_json or [], operation), operation=operation, allowed=policy_row.allowed_operations_json or [])
    actual_trust = str(getattr(adapter_row, "trust_level", "bounded") or "bounded")
    minimum_trust = str(policy_row.minimum_adapter_trust or "bounded")
    add("adapter-trust", TRUST_ORDER.get(actual_trust, 0) >= TRUST_ORDER.get(minimum_trust, 1), actual=actual_trust, minimum=minimum_trust)

    requested = budget.model_dump()
    limits = policy_row.resource_limits_json or {}
    resource_checks = (
        ("cpuCores", "resource-cpuCores"),
        ("memoryMb", "resource-memoryMb"),
        ("wallSeconds", "resource-wallSeconds"),
        ("outputBytes", "resource-outputBytes"),
        ("pids", "resource-pids"),
        ("tempStorageMb", "resource-tempStorageMb"),
    )
    for field, check_name in resource_checks:
        limit = limits.get(field)
        value = requested.get(field)
        add(check_name, limit is not None and value <= limit, requested=value, limit=limit)

    sandbox = policy_row.sandbox_json or {}
    mode = str(sandbox.get("mode") or "metadata-gate")
    adapter_config = adapter_row.configuration_json or {}
    sandbox_ok = True
    if mode == "adapter-attested":
        sandbox_ok = bool(adapter_config.get("sandboxAttested"))
    elif mode == "container-required":
        sandbox_ok = adapter_row.adapter_type == "container"
    elif mode == "remote-sandbox-required":
        sandbox_ok = adapter_row.adapter_type == "remote-service" and bool(adapter_config.get("sandboxAttested"))
    add("sandbox-mode", sandbox_ok, mode=mode, adapterType=adapter_row.adapter_type)

    if sandbox.get("requirePinnedContainer"):
        add("pinned-container", _pinned_container(adapter_row), container=adapter_row.container_json or {})
    else:
        add("pinned-container", True, required=False)

    network_mode = str(sandbox.get("networkMode") or "server-routed-only")
    if network_mode == "none":
        network_ok = route.get("transport") == "in-process"
    elif network_mode == "server-routed-only":
        network_ok = route.get("transport") in {"in-process", "server-configured-http"} and bool(route.get("serverConfiguredOnly"))
    else:
        network_ok = bool(adapter_config.get("networkAllowlist"))
    add("network-policy", network_ok, mode=network_mode, routeTransport=route.get("transport", ""))

    for key in ("allowHostFilesystem", "allowDockerSocket", "allowPrivileged"):
        add(f"sandbox-{key}", sandbox.get(key) is False, required=False)
    add("no-new-privileges", sandbox.get("noNewPrivileges") is True, required=True)
    add("drop-all-capabilities", sandbox.get("dropAllCapabilities") is True, required=True)

    eligible = all(item["status"] == "pass" for item in checks)
    classification = "eligible" if eligible else "blocked"
    decision_id = f"policy-decision-{uuid4()}"
    fingerprint_doc = {
        "executionPlanId": execution_plan_id,
        "policyRef": {"policyId": policy_row.policy_id, "revision": int(policy_row.revision), "fingerprint": policy_row.fingerprint},
        "adapterRef": {"adapterId": adapter_row.adapter_id, "revision": int(adapter_row.revision), "fingerprint": adapter_row.fingerprint, "trustLevel": actual_trust},
        "targetProduct": target_product,
        "operation": operation,
        "resourceBudget": requested,
        "sandbox": sandbox,
        "checks": checks,
    }
    row = ExecutionPolicyDecision(
        user_key=user_key,
        decision_id=decision_id,
        execution_plan_id=execution_plan_id,
        policy_id=policy_row.policy_id,
        policy_revision=int(policy_row.revision),
        policy_fingerprint=policy_row.fingerprint,
        eligible=eligible,
        classification=classification,
        resource_budget_json=requested,
        sandbox_json=sandbox,
        checks_json=checks,
        fingerprint=sha256_hex(fingerprint_doc),
        created_at=_now(),
    )
    db.add(row)
    db.flush()
    return row


def get_policy_decision(db: Session, user_key: str, decision_id: str):
    return db.get(ExecutionPolicyDecision, {"user_key": user_key, "decision_id": decision_id})


def list_policy_decisions(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(ExecutionPolicyDecision).where(ExecutionPolicyDecision.user_key == user_key).order_by(ExecutionPolicyDecision.created_at.desc())).all()
    return [policy_decision_metadata(row) for row in rows]
