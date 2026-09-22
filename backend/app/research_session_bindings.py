from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .cross_product_handoffs import get_handoff
from .models import ResearchSessionObjectBinding
from .platform_core_runtime import (
    PlatformCoreRuntimeError,
    PlatformCoreSessionRequest,
    PlatformCoreObjectBindingRequest,
    PlatformCoreExecutionBindingRequest,
    PlatformCoreVisualBindingRequest,
    PlatformCorePackageBindingRequest,
    PlatformCoreHandoffBindingRequest,
    bind_object,
    bind_execution,
    bind_visual,
    bind_package,
    bind_handoff,
    ensure_session,
    get_mapping,
)
from .registry import get_execution_run, run_metadata
from .scientific_objects import OBJECT_KINDS, get_object
from .utils import iso, sha256_hex

BINDING_RUNTIME_SCHEMA = "sc-workspace-research-session-object-binding-runtime/1.0"
BINDING_REQUEST_SCHEMA = "sc-workspace-research-session-binding-request/1.0"
RECONCILE_REQUEST_SCHEMA = "sc-workspace-research-session-binding-reconcile-request/1.0"
BINDING_TYPES = ("scientific-object", "execution", "visualization", "study-package", "handoff")


class ResearchSessionBindingRequest(BaseModel):
    schema: Literal["sc-workspace-research-session-binding-request/1.0"]
    bindingType: Literal["scientific-object", "execution", "visualization", "study-package", "handoff"]
    objectId: str = Field(min_length=1, max_length=160)
    objectKind: str | None = Field(default=None, max_length=96)
    role: str = Field(default="context", min_length=1, max_length=120)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)
    ensureSession: bool = True

    @model_validator(mode="after")
    def validate_kind(self):
        if self.bindingType == "scientific-object":
            if not self.objectKind or self.objectKind not in OBJECT_KINDS:
                raise ValueError("scientific-object binding requires a supported objectKind")
        return self


class ResearchSessionBindingReconcileRequest(BaseModel):
    schema: Literal["sc-workspace-research-session-binding-reconcile-request/1.0"]
    bindings: list[ResearchSessionBindingRequest] = Field(default_factory=list, max_length=100)
    ensureSession: bool = True
    stopOnError: bool = False
    sessionTitle: str = Field(default="", max_length=400)


def profile() -> dict[str, Any]:
    return {
        "schema": BINDING_RUNTIME_SCHEMA,
        "workspaceVersion": "3.4.0",
        "release": "Research Session & Object Binding Runtime",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "referenceFirst": True,
        "platformCoreSessionRegistryAuthority": "platform-core-v3",
        "workspaceBindingRegistryAuthority": "workspace-postgresql",
        "specialistObjectAuthorityPreserved": True,
        "objectContentReplicatedToCore": False,
        "durableBindingRegistry": True,
        "bindingFingerprintPinning": True,
        "idempotentBindingReplay": True,
        "explicitReconciliation": True,
        "automaticMassBinding": False,
        "supportedBindingTypes": list(BINDING_TYPES),
        "automaticScientificInference": False,
        "automaticEvidenceRanking": False,
        "automaticDecisionAuthority": False,
    }


def _workspace_descriptor(db: Session, user_key: str, project_id: str, req: ResearchSessionBindingRequest) -> dict[str, Any]:
    if req.bindingType == "scientific-object":
        item = get_object(db, user_key, str(req.objectKind), req.objectId)
        if item is None:
            raise PlatformCoreRuntimeError("Workspace scientific object not found.", 404, "workspace-scientific-object-not-found")
        if str(item.get("projectId") or "") not in ("", project_id):
            raise PlatformCoreRuntimeError("Workspace object belongs to a different project.", 409, "workspace-project-scope-mismatch")
        return {
            "workspaceRef": f"workspace:{req.objectKind}:{req.objectId}",
            "workspaceKind": str(req.objectKind),
            "workspaceObjectId": req.objectId,
            "revision": int(item.get("revision") or 0),
            "fingerprint": str(item.get("objectFingerprint") or item.get("fingerprint") or sha256_hex(item)),
        }
    if req.bindingType == "execution":
        row = get_execution_run(db, user_key, req.objectId)
        if row is None:
            raise PlatformCoreRuntimeError("Workspace execution run not found.", 404, "workspace-execution-not-found")
        item = run_metadata(row)
        if str(item.get("projectId") or "") not in ("", project_id):
            raise PlatformCoreRuntimeError("Workspace execution belongs to a different project.", 409, "workspace-project-scope-mismatch")
        return {
            "workspaceRef": f"workspace:execution-run:{req.objectId}",
            "workspaceKind": "execution-run",
            "workspaceObjectId": req.objectId,
            "revision": int(item.get("revision") or 0),
            "fingerprint": str(item.get("reproducibilityFingerprint") or item.get("inputFingerprint") or sha256_hex(item)),
        }
    if req.bindingType == "visualization":
        item = get_object(db, user_key, "visualization-spec", req.objectId)
        if item is None:
            raise PlatformCoreRuntimeError("Workspace visualization specification not found.", 404, "workspace-visualization-not-found")
        if str(item.get("projectId") or "") not in ("", project_id):
            raise PlatformCoreRuntimeError("Workspace visualization belongs to a different project.", 409, "workspace-project-scope-mismatch")
        return {
            "workspaceRef": f"workspace:visualization-spec:{req.objectId}", "workspaceKind": "visualization-spec",
            "workspaceObjectId": req.objectId, "revision": int(item.get("revision") or 0),
            "fingerprint": str(item.get("objectFingerprint") or item.get("fingerprint") or sha256_hex(item)),
        }
    if req.bindingType == "study-package":
        item = get_object(db, user_key, "study-package", req.objectId)
        if item is None:
            raise PlatformCoreRuntimeError("Workspace scientific study package not found.", 404, "workspace-study-package-not-found")
        if str(item.get("projectId") or "") not in ("", project_id):
            raise PlatformCoreRuntimeError("Workspace study package belongs to a different project.", 409, "workspace-project-scope-mismatch")
        return {
            "workspaceRef": f"workspace:study-package:{req.objectId}", "workspaceKind": "study-package",
            "workspaceObjectId": req.objectId, "revision": int(item.get("revision") or 0),
            "fingerprint": str(item.get("objectFingerprint") or item.get("fingerprint") or sha256_hex(item)),
        }
    handoff = get_handoff(db, user_key, req.objectId)
    if handoff is None:
        raise PlatformCoreRuntimeError("Workspace research handoff not found.", 404, "workspace-handoff-not-found")
    if str(handoff.get("projectId") or "") not in ("", project_id):
        raise PlatformCoreRuntimeError("Workspace handoff belongs to a different project.", 409, "workspace-project-scope-mismatch")
    return {
        "workspaceRef": f"workspace:handoff:{req.objectId}", "workspaceKind": "research-handoff",
        "workspaceObjectId": req.objectId, "revision": 0,
        "fingerprint": str(handoff.get("packageFingerprint") or sha256_hex(handoff)),
    }


def _existing(db: Session, user_key: str, project_id: str, binding_type: str, workspace_ref: str) -> ResearchSessionObjectBinding | None:
    return db.scalar(select(ResearchSessionObjectBinding).where(
        ResearchSessionObjectBinding.user_key == user_key,
        ResearchSessionObjectBinding.project_id == project_id,
        ResearchSessionObjectBinding.binding_type == binding_type,
        ResearchSessionObjectBinding.workspace_ref == workspace_ref,
    ).limit(1))


def _payload(row: ResearchSessionObjectBinding) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-research-session-object-binding/1.0",
        "bindingId": row.binding_id, "projectId": row.project_id, "coreSessionId": row.core_session_id,
        "bindingType": row.binding_type, "workspaceRef": row.workspace_ref, "workspaceKind": row.workspace_kind,
        "workspaceObjectId": row.workspace_object_id, "workspaceRevision": row.workspace_revision,
        "workspaceFingerprint": row.workspace_fingerprint, "coreBindingId": row.core_binding_id,
        "role": row.role, "status": row.status, "requestFingerprint": row.request_fingerprint,
        "metadata": row.metadata_json, "createdAt": iso(row.created_at), "updatedAt": iso(row.updated_at),
    }


def _ensure_project_session(db: Session, user_key: str, project_id: str, ensure: bool, title: str = ""):
    mapping = get_mapping(db, user_key, project_id)
    if mapping is not None:
        return mapping
    if not ensure:
        raise PlatformCoreRuntimeError("Workspace project is not bound to a Platform Core unified research session.", 409, "platform-core-session-required")
    result = ensure_session(db, user_key, PlatformCoreSessionRequest(
        schema="sc-workspace-platform-core-session-request/1.0", projectId=project_id, title=title
    ))
    mapping = get_mapping(db, user_key, project_id)
    if mapping is None:
        raise PlatformCoreRuntimeError("Platform Core session mapping was not created.", 502, "platform-core-session-mapping-missing")
    return mapping


def bind_reference(db: Session, user_key: str, project_id: str, req: ResearchSessionBindingRequest) -> dict[str, Any]:
    mapping = _ensure_project_session(db, user_key, project_id, req.ensureSession)
    source = _workspace_descriptor(db, user_key, project_id, req)
    existing = _existing(db, user_key, project_id, req.bindingType, source["workspaceRef"])
    if existing is not None and existing.workspace_fingerprint == source["fingerprint"] and existing.status == "active":
        return {"ok": True, "replayed": True, "item": _payload(existing)}

    meta = {"researchSessionBindingRuntime": "3.4.0", **req.metadata}
    if req.bindingType == "scientific-object":
        result = bind_object(db, user_key, PlatformCoreObjectBindingRequest(
            schema="sc-workspace-platform-core-object-binding-request/1.0", projectId=project_id,
            kind=str(req.objectKind), objectId=req.objectId, role=req.role, visibility=req.visibility, metadata=meta))
    elif req.bindingType == "execution":
        result = bind_execution(db, user_key, PlatformCoreExecutionBindingRequest(
            schema="sc-workspace-platform-core-execution-binding-request/1.0", projectId=project_id,
            executionRunId=req.objectId, visibility=req.visibility, metadata=meta))
    elif req.bindingType == "visualization":
        result = bind_visual(db, user_key, PlatformCoreVisualBindingRequest(
            schema="sc-workspace-platform-core-visual-binding-request/1.0", projectId=project_id,
            visualizationId=req.objectId, visibility=req.visibility, metadata=meta))
    elif req.bindingType == "study-package":
        result = bind_package(db, user_key, PlatformCorePackageBindingRequest(
            schema="sc-workspace-platform-core-package-binding-request/1.0", projectId=project_id,
            packageId=req.objectId, visibility=req.visibility, metadata=meta))
    else:
        result = bind_handoff(db, user_key, PlatformCoreHandoffBindingRequest(
            schema="sc-workspace-platform-core-handoff-binding-request/1.0", projectId=project_id,
            handoffId=req.objectId, visibility=req.visibility, metadata=meta))

    core_item = result.get("item") or {}
    core_id = str(core_item.get("id") or "")[:96]
    request_fingerprint = str((result.get("receipt") or {}).get("requestFingerprint") or sha256_hex({
        "projectId": project_id, "request": req.model_dump(), "source": source,
    }))
    now = datetime.now(timezone.utc)
    row = existing or ResearchSessionObjectBinding(
        user_key=user_key, binding_id="research-binding-" + uuid4().hex[:24], project_id=project_id,
        core_session_id=mapping.core_session_id, binding_type=req.bindingType, workspace_ref=source["workspaceRef"],
        workspace_kind=source["workspaceKind"], workspace_object_id=source["workspaceObjectId"],
        created_at=now,
    )
    row.core_session_id = mapping.core_session_id
    row.workspace_revision = source["revision"]
    row.workspace_fingerprint = source["fingerprint"]
    row.core_binding_id = core_id
    row.role = req.role
    row.status = "active"
    row.request_fingerprint = request_fingerprint
    row.metadata_json = meta
    row.response_json = core_item
    row.updated_at = now
    db.add(row); db.commit(); db.refresh(row)
    return {"ok": True, "replayed": False, "item": _payload(row), "core": result}


def list_bindings(db: Session, user_key: str, project_id: str, binding_type: str | None = None, limit: int = 250) -> list[dict[str, Any]]:
    query = select(ResearchSessionObjectBinding).where(
        ResearchSessionObjectBinding.user_key == user_key,
        ResearchSessionObjectBinding.project_id == project_id,
    )
    if binding_type:
        query = query.where(ResearchSessionObjectBinding.binding_type == binding_type)
    rows = db.scalars(query.order_by(ResearchSessionObjectBinding.updated_at.desc()).limit(limit)).all()
    return [_payload(row) for row in rows]


def project_binding_state(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    mapping = get_mapping(db, user_key, project_id)
    items = list_bindings(db, user_key, project_id, None, 500)
    counts = {kind: 0 for kind in BINDING_TYPES}
    for item in items:
        counts[item["bindingType"]] = counts.get(item["bindingType"], 0) + 1
    return {
        "schema": "sc-workspace-research-session-binding-state/1.0",
        "projectId": project_id,
        "sessionBound": mapping is not None,
        "coreSessionId": mapping.core_session_id if mapping else "",
        "counts": counts,
        "bindings": items,
        "referenceFirst": True,
        "specialistObjectAuthorityPreserved": True,
    }


def reconcile(db: Session, user_key: str, project_id: str, req: ResearchSessionBindingReconcileRequest) -> dict[str, Any]:
    _ensure_project_session(db, user_key, project_id, req.ensureSession, req.sessionTitle)
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for binding in req.bindings:
        if not binding.ensureSession:
            binding.ensureSession = req.ensureSession
        try:
            results.append(bind_reference(db, user_key, project_id, binding))
        except PlatformCoreRuntimeError as exc:
            failure = {"bindingType": binding.bindingType, "objectId": binding.objectId, "code": exc.code, "message": str(exc)}
            failures.append(failure)
            if req.stopOnError:
                raise
    state = project_binding_state(db, user_key, project_id)
    return {
        "ok": len(failures) == 0,
        "schema": "sc-workspace-research-session-binding-reconciliation/1.0",
        "projectId": project_id,
        "requested": len(req.bindings), "succeeded": len(results), "failed": len(failures),
        "results": results, "failures": failures, "state": state,
    }
