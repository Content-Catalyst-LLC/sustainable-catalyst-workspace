from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .cross_product_handoffs import get_handoff
from .models import PlatformCoreResearchSessionBinding, PlatformCoreRuntimeReceipt
from .repository import get_project
from .scientific_objects import OBJECT_KINDS, get_object
from .registry import get_execution_run, list_run_outputs, run_metadata, output_metadata
from .utils import iso, sha256_hex

INTEGRATION_SCHEMA = "sc-workspace-platform-core-v3-unified-research-runtime-integration/1.0"
SESSION_REQUEST_SCHEMA = "sc-workspace-platform-core-session-request/1.0"
OBJECT_BINDING_REQUEST_SCHEMA = "sc-workspace-platform-core-object-binding-request/1.0"
EXECUTION_BINDING_REQUEST_SCHEMA = "sc-workspace-platform-core-execution-binding-request/1.0"
VISUAL_BINDING_REQUEST_SCHEMA = "sc-workspace-platform-core-visual-binding-request/1.0"
PACKAGE_BINDING_REQUEST_SCHEMA = "sc-workspace-platform-core-package-binding-request/1.0"
HANDOFF_BINDING_REQUEST_SCHEMA = "sc-workspace-platform-core-handoff-binding-request/1.0"
CORE_CONTRACT = "sc.research.unified-research-scientific-investigation-runtime.v1"
CORE_API_ROOT = "/v1/research/unified-runtime"


class PlatformCoreRuntimeError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502, code: str = "platform-core-runtime-error"):
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class PlatformCoreSessionRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-session-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    title: str = Field(default="", max_length=400)
    workflowRef: str | None = Field(default=None, max_length=1000)
    projectStateRef: str | None = Field(default=None, max_length=1000)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)


class PlatformCoreObjectBindingRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-object-binding-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    kind: str
    objectId: str = Field(min_length=1, max_length=160)
    role: str = Field(default="context", min_length=1, max_length=120)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_kind(self):
        if self.kind not in OBJECT_KINDS:
            raise ValueError("unsupported Workspace scientific object kind")
        return self


class PlatformCoreExecutionBindingRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-execution-binding-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    executionRunId: str = Field(min_length=1, max_length=160)
    runtime: str | None = Field(default=None, max_length=120)
    methodRef: str | None = Field(default=None, max_length=1000)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlatformCoreVisualBindingRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-visual-binding-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    visualizationId: str = Field(min_length=1, max_length=160)
    visualType: str = Field(default="workspace-visualization-spec", max_length=120)
    sceneRef: str | None = Field(default=None, max_length=1000)
    viewRef: str | None = Field(default=None, max_length=1000)
    sourceRefs: list[str] = Field(default_factory=list, max_length=200)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlatformCorePackageBindingRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-package-binding-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    packageId: str = Field(min_length=1, max_length=160)
    packageType: str = Field(default="workspace-scientific-study-package", max_length=120)
    memberRefs: list[str] = Field(default_factory=list, max_length=500)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PlatformCoreHandoffBindingRequest(BaseModel):
    schema: Literal["sc-workspace-platform-core-handoff-binding-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    handoffId: str = Field(min_length=1, max_length=96)
    visibility: Literal["internal", "public"] = "internal"
    metadata: dict[str, Any] = Field(default_factory=dict)


def profile() -> dict[str, Any]:
    settings = get_settings()
    return {
        "schema": INTEGRATION_SCHEMA,
        "workspaceVersion": settings.service_version,
        "release": "Platform Core v3 Unified Research Runtime Integration",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "referenceFirst": True,
        "platformCoreConfigured": settings.platform_core_configured,
        "platformCoreWriteConfigured": settings.platform_core_write_configured,
        "platformCoreContract": CORE_CONTRACT,
        "coreApiRoot": CORE_API_ROOT,
        "workspaceOwnsProjectData": True,
        "workspaceOwnsScientificObjects": True,
        "workspaceOwnsScientificExecution": True,
        "coreOwnsUnifiedSessionRegistry": True,
        "coreOwnsDeclaredCrossProductLineage": True,
        "objectContentReplicatedToCore": False,
        "coreExecutesWorkspaceScientificWork": False,
        "coreInfersWorkspaceFindings": False,
        "coreAuthorizesWorkspaceUsers": False,
        "serviceCredentialBrowserVisible": False,
        "durableSessionMappings": True,
        "durableIntegrationReceipts": True,
        "supportedWorkspaceBindings": ["object", "execution", "visual", "package", "handoff"],
    }


def _base() -> str:
    value = get_settings().platform_core_url.strip().rstrip("/")
    if not value:
        raise PlatformCoreRuntimeError("Platform Core runtime URL is not configured.", 503, "platform-core-unconfigured")
    return value


def _request(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    method = method.upper()
    headers = {"Accept": "application/json"}
    if method != "GET":
        if not settings.platform_core_write_api_key.strip():
            raise PlatformCoreRuntimeError("Platform Core write credential is not configured.", 503, "platform-core-write-unconfigured")
        headers["X-SC-API-Key"] = settings.platform_core_write_api_key.strip()
        headers["Content-Type"] = "application/json"
    elif settings.platform_core_write_api_key.strip():
        headers["X-SC-API-Key"] = settings.platform_core_write_api_key.strip()
    try:
        response = httpx.request(method, _base() + path, json=body, headers=headers, timeout=settings.platform_core_timeout_seconds)
    except httpx.HTTPError as exc:
        raise PlatformCoreRuntimeError(f"Platform Core transport failed: {exc.__class__.__name__}", 502, "platform-core-transport-failed") from exc
    if not (200 <= response.status_code < 300):
        message = f"Platform Core returned HTTP {response.status_code}."
        try:
            detail = response.json()
            if isinstance(detail, dict):
                message = str(detail.get("detail") or detail.get("message") or message)[:1000]
        except ValueError:
            pass
        raise PlatformCoreRuntimeError(message, 502 if response.status_code >= 500 else response.status_code, "platform-core-request-failed")
    try:
        payload = response.json()
    except ValueError as exc:
        raise PlatformCoreRuntimeError("Platform Core returned a non-JSON response.", 502, "platform-core-invalid-response") from exc
    if not isinstance(payload, dict):
        raise PlatformCoreRuntimeError("Platform Core returned an invalid response envelope.", 502, "platform-core-invalid-response")
    return payload


def readiness() -> dict[str, Any]:
    local = profile()
    if not get_settings().platform_core_configured:
        return {"ok": False, "configured": False, "compatible": False, "item": local}
    remote = _request("GET", CORE_API_ROOT + "/readiness")
    compatible = remote.get("contract") == CORE_CONTRACT and bool(remote.get("reference_first_runtime_by_core")) and bool(remote.get("underlying_objects_remain_authoritative_in_specialist_layers"))
    return {
        "ok": compatible,
        "configured": True,
        "writeConfigured": get_settings().platform_core_write_configured,
        "compatible": compatible,
        "item": local,
        "core": remote,
    }


def _mapping_payload(row: PlatformCoreResearchSessionBinding) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-platform-core-session-binding/1.0",
        "projectId": row.project_id,
        "coreSessionId": row.core_session_id,
        "coreSessionKey": row.core_session_key,
        "coreContract": row.core_contract,
        "coreRelease": row.core_release,
        "coreProductBindingId": row.core_product_binding_id,
        "status": row.status,
        "projectRevision": row.project_revision,
        "projectFingerprint": row.project_fingerprint,
        "coreSession": row.core_session_json,
        "lastError": row.last_error,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _receipt_payload(row: PlatformCoreRuntimeReceipt) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-platform-core-runtime-receipt/1.0",
        "receiptId": row.receipt_id,
        "projectId": row.project_id,
        "coreSessionId": row.core_session_id,
        "action": row.action,
        "bindingKind": row.binding_kind,
        "workspaceRef": row.workspace_ref,
        "coreRef": row.core_ref,
        "status": row.status,
        "requestFingerprint": row.request_fingerprint,
        "response": row.response_json,
        "createdAt": iso(row.created_at),
    }


def _record(db: Session, user_key: str, project_id: str, core_session_id: str, action: str, binding_kind: str, workspace_ref: str, core_ref: str, request: dict[str, Any], response: dict[str, Any], status: str = "recorded") -> PlatformCoreRuntimeReceipt:
    row = PlatformCoreRuntimeReceipt(
        user_key=user_key,
        receipt_id="core-runtime-" + uuid4().hex[:24],
        project_id=project_id,
        core_session_id=core_session_id,
        action=action,
        binding_kind=binding_kind,
        workspace_ref=workspace_ref,
        core_ref=core_ref,
        status=status,
        request_fingerprint=sha256_hex(request),
        response_json=response,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_mapping(db: Session, user_key: str, project_id: str) -> PlatformCoreResearchSessionBinding | None:
    return db.get(PlatformCoreResearchSessionBinding, {"user_key": user_key, "project_id": project_id})


def _mapping_by_session(db: Session, user_key: str, session_id: str) -> PlatformCoreResearchSessionBinding | None:
    return db.scalar(select(PlatformCoreResearchSessionBinding).where(PlatformCoreResearchSessionBinding.user_key == user_key, PlatformCoreResearchSessionBinding.core_session_id == session_id).limit(1))


def _session_key(user_key: str, project_id: str) -> str:
    return "workspace-" + sha256_hex({"userKey": user_key, "projectId": project_id})[:40]


def _ensure_product_binding(db: Session, row: PlatformCoreResearchSessionBinding) -> dict[str, Any] | None:
    if row.core_product_binding_id:
        return None
    request = {
        "data": {
            "session_id": row.core_session_id,
            "product_ref": "workspace",
            "product_version": get_settings().service_version,
            "runtime_binding_ref": f"workspace:project:{row.project_id}",
            "context_ref": f"workspace:project:{row.project_id}:revision:{row.project_revision}",
            "declared_capabilities": [
                "backend-native-project-workspace",
                "scientific-object-registry",
                "bounded-scientific-execution",
                "visualization-specifications",
                "reproducible-study-packages",
                "cross-product-research-handoffs",
            ],
            "visibility": "internal",
            "metadata": {"referenceFirst": True, "workspaceOwnsUnderlyingObjects": True},
        }
    }
    try:
        response = _request("POST", CORE_API_ROOT + "/product-bindings", request)
        row.core_product_binding_id = str(response.get("id") or "")[:96]
        row.last_error = ""
        row.updated_at = datetime.now(timezone.utc)
        db.add(row)
        db.commit()
        _record(db, row.user_key, row.project_id, row.core_session_id, "bind-product", "product", f"workspace:project:{row.project_id}", str(response.get("id") or ""), request, response)
        return response
    except PlatformCoreRuntimeError as exc:
        row.last_error = str(exc)[:2000]
        row.updated_at = datetime.now(timezone.utc)
        db.add(row)
        db.commit()
        return {"ok": False, "code": exc.code, "message": str(exc)}


def ensure_session(db: Session, user_key: str, payload: PlatformCoreSessionRequest) -> dict[str, Any]:
    project = get_project(db, user_key, payload.projectId)
    if project is None:
        raise PlatformCoreRuntimeError("Workspace project not found.", 404, "workspace-project-not-found")
    existing = get_mapping(db, user_key, payload.projectId)
    if existing is not None:
        product = _ensure_product_binding(db, existing)
        return {"ok": True, "replayed": True, "item": _mapping_payload(existing), "productBinding": product}
    session_key = _session_key(user_key, payload.projectId)
    state_ref = payload.projectStateRef or f"workspace:project:{payload.projectId}:revision:{project.revision}"
    request = {
        "data": {
            "session_key": session_key,
            "title": payload.title.strip() or project.title,
            "project_ref": f"workspace:project:{payload.projectId}",
            "status": "active",
            "workflow_ref": payload.workflowRef,
            "project_state_ref": state_ref,
            "runtime_contract_ref": CORE_CONTRACT,
            "visibility": payload.visibility,
            "metadata": {
                "workspaceVersion": get_settings().service_version,
                "workspaceProjectRevision": project.revision,
                "workspaceProjectFingerprint": project.project_fingerprint,
                "referenceFirst": True,
                **payload.metadata,
            },
            "provenance": {
                "sourceProduct": "workspace",
                "sourceProjectRef": f"workspace:project:{payload.projectId}",
                "workspaceProjectRevision": project.revision,
                "workspaceProjectFingerprint": project.project_fingerprint,
                **payload.provenance,
            },
            "created_by": "workspace-backend",
        }
    }
    response = _request("POST", CORE_API_ROOT + "/sessions", request)
    core_session_id = str(response.get("id") or "")
    if not core_session_id:
        raise PlatformCoreRuntimeError("Platform Core session response did not include an id.", 502, "platform-core-invalid-session")
    row = PlatformCoreResearchSessionBinding(
        user_key=user_key,
        project_id=payload.projectId,
        core_session_id=core_session_id[:96],
        core_session_key=session_key,
        core_contract=str(response.get("runtime_contract_ref") or CORE_CONTRACT)[:160],
        core_release="3.0.0",
        status=str(response.get("status") or "active")[:32],
        project_revision=project.revision,
        project_fingerprint=project.project_fingerprint,
        core_session_json=response,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    session_receipt = _record(db, user_key, payload.projectId, row.core_session_id, "create-session", "session", f"workspace:project:{payload.projectId}", row.core_session_id, request, response)
    product = _ensure_product_binding(db, row)
    return {"ok": True, "replayed": False, "item": _mapping_payload(row), "receipt": _receipt_payload(session_receipt), "productBinding": product}


def project_context(db: Session, user_key: str, project_id: str) -> dict[str, Any] | None:
    row = get_mapping(db, user_key, project_id)
    if row is None:
        return None
    summary = _request("GET", f"{CORE_API_ROOT}/sessions/{row.core_session_id}/summary")
    return {"schema": "sc-workspace-platform-core-project-context/1.0", "item": _mapping_payload(row), "coreSummary": summary}


def _session_for_project(db: Session, user_key: str, project_id: str) -> PlatformCoreResearchSessionBinding:
    row = get_mapping(db, user_key, project_id)
    if row is None:
        raise PlatformCoreRuntimeError("Workspace project is not bound to a Platform Core unified research session.", 409, "platform-core-session-required")
    return row


def _check_project_scope(item: dict[str, Any], project_id: str) -> None:
    object_project = str(item.get("projectId") or "")
    if object_project and object_project != project_id:
        raise PlatformCoreRuntimeError("Workspace object belongs to a different project.", 409, "workspace-project-scope-mismatch")


def bind_object(db: Session, user_key: str, payload: PlatformCoreObjectBindingRequest) -> dict[str, Any]:
    session = _session_for_project(db, user_key, payload.projectId)
    item = get_object(db, user_key, payload.kind, payload.objectId)
    if item is None:
        raise PlatformCoreRuntimeError("Workspace scientific object not found.", 404, "workspace-scientific-object-not-found")
    _check_project_scope(item, payload.projectId)
    workspace_ref = f"workspace:{payload.kind}:{payload.objectId}"
    request = {"data": {"session_id": session.core_session_id, "object_type": payload.kind, "object_ref": workspace_ref, "version_ref": str(item.get("revision")) if item.get("revision") is not None else None, "content_hash": item.get("fingerprint"), "role": payload.role, "visibility": payload.visibility, "metadata": {"workspaceObjectFingerprint": item.get("objectFingerprint"), "workspaceProjectId": payload.projectId, **payload.metadata}}}
    response = _request("POST", CORE_API_ROOT + "/object-bindings", request)
    receipt = _record(db, user_key, payload.projectId, session.core_session_id, "bind-object", "object", workspace_ref, str(response.get("id") or ""), request, response)
    return {"ok": True, "item": response, "receipt": _receipt_payload(receipt)}


def bind_execution(db: Session, user_key: str, payload: PlatformCoreExecutionBindingRequest) -> dict[str, Any]:
    session = _session_for_project(db, user_key, payload.projectId)
    row = get_execution_run(db, user_key, payload.executionRunId)
    if row is None:
        raise PlatformCoreRuntimeError("Workspace execution run not found.", 404, "workspace-execution-not-found")
    meta = run_metadata(row)
    if str(meta.get("projectId") or "") and str(meta.get("projectId")) != payload.projectId:
        raise PlatformCoreRuntimeError("Workspace execution belongs to a different project.", 409, "workspace-project-scope-mismatch")
    workspace_ref = f"workspace:execution-run:{payload.executionRunId}"
    env = meta.get("environmentRef") or {}
    environment_ref = None
    if isinstance(env, dict) and env:
        env_id = env.get("environmentId") or env.get("id")
        environment_ref = f"workspace:execution-environment:{env_id}" if env_id else f"workspace:execution-environment:{sha256_hex(env)[:24]}"
    inputs: list[str] = []
    for ref in meta.get("datasetRefs") or []:
        if isinstance(ref, dict):
            rid = ref.get("datasetId") or ref.get("id")
            if rid: inputs.append(f"workspace:dataset:{rid}")
    for key, kind in (("modelRef", "model"), ("parameterSetRef", "parameter-set")):
        ref = meta.get(key) or {}
        if isinstance(ref, dict):
            rid = ref.get("modelId") or ref.get("parameterSetId") or ref.get("id")
            if rid: inputs.append(f"workspace:{kind}:{rid}")
    outputs = []
    for out in list_run_outputs(db, user_key, payload.executionRunId):
        om = output_metadata(out) if not isinstance(out, dict) else out
        if om.get("artifactId"):
            outputs.append(f"workspace:artifact:{om['artifactId']}")
        elif om.get("outputId"):
            outputs.append(f"workspace:execution-output:{payload.executionRunId}:{om['outputId']}")
    request = {"data": {"session_id": session.core_session_id, "execution_ref": workspace_ref, "runtime": payload.runtime or str(meta.get("targetProduct") or meta.get("operation") or "workspace"), "environment_ref": environment_ref, "method_ref": payload.methodRef or (f"workspace:operation:{meta.get('operation')}" if meta.get("operation") else None), "input_refs": inputs, "output_refs": outputs, "visibility": payload.visibility, "metadata": {"workspaceExecutionFingerprint": meta.get("reproducibilityFingerprint"), "workspaceInputFingerprint": meta.get("inputFingerprint"), "workspaceRuntimeAdapterFingerprint": meta.get("runtimeAdapterFingerprint"), "workspaceProjectId": payload.projectId, **payload.metadata}}}
    response = _request("POST", CORE_API_ROOT + "/execution-bindings", request)
    receipt = _record(db, user_key, payload.projectId, session.core_session_id, "bind-execution", "execution", workspace_ref, str(response.get("id") or ""), request, response)
    return {"ok": True, "item": response, "receipt": _receipt_payload(receipt)}


def bind_visual(db: Session, user_key: str, payload: PlatformCoreVisualBindingRequest) -> dict[str, Any]:
    session = _session_for_project(db, user_key, payload.projectId)
    item = get_object(db, user_key, "visualization-spec", payload.visualizationId)
    if item is None:
        raise PlatformCoreRuntimeError("Workspace visualization specification not found.", 404, "workspace-visualization-not-found")
    _check_project_scope(item, payload.projectId)
    workspace_ref = f"workspace:visualization-spec:{payload.visualizationId}"
    request = {"data": {"session_id": session.core_session_id, "visual_ref": workspace_ref, "visual_type": payload.visualType, "scene_ref": payload.sceneRef, "view_ref": payload.viewRef, "source_refs": payload.sourceRefs, "visibility": payload.visibility, "metadata": {"workspaceVisualizationFingerprint": item.get("fingerprint"), "workspaceProjectId": payload.projectId, **payload.metadata}}}
    response = _request("POST", CORE_API_ROOT + "/visual-bindings", request)
    receipt = _record(db, user_key, payload.projectId, session.core_session_id, "bind-visual", "visual", workspace_ref, str(response.get("id") or ""), request, response)
    return {"ok": True, "item": response, "receipt": _receipt_payload(receipt)}


def bind_package(db: Session, user_key: str, payload: PlatformCorePackageBindingRequest) -> dict[str, Any]:
    session = _session_for_project(db, user_key, payload.projectId)
    item = get_object(db, user_key, "study-package", payload.packageId)
    if item is None:
        raise PlatformCoreRuntimeError("Workspace scientific study package not found.", 404, "workspace-study-package-not-found")
    _check_project_scope(item, payload.projectId)
    workspace_ref = f"workspace:study-package:{payload.packageId}"
    request = {"data": {"session_id": session.core_session_id, "package_ref": workspace_ref, "package_type": payload.packageType, "version_ref": str(item.get("revision")) if item.get("revision") is not None else None, "content_hash": item.get("fingerprint"), "member_refs": payload.memberRefs, "visibility": payload.visibility, "metadata": {"workspaceObjectFingerprint": item.get("objectFingerprint"), "workspaceProjectId": payload.projectId, **payload.metadata}}}
    response = _request("POST", CORE_API_ROOT + "/package-bindings", request)
    receipt = _record(db, user_key, payload.projectId, session.core_session_id, "bind-package", "package", workspace_ref, str(response.get("id") or ""), request, response)
    return {"ok": True, "item": response, "receipt": _receipt_payload(receipt)}


def bind_handoff(db: Session, user_key: str, payload: PlatformCoreHandoffBindingRequest) -> dict[str, Any]:
    session = _session_for_project(db, user_key, payload.projectId)
    handoff = get_handoff(db, user_key, payload.handoffId)
    if handoff is None:
        raise PlatformCoreRuntimeError("Workspace research handoff not found.", 404, "workspace-handoff-not-found")
    if str(handoff.get("projectId") or "") and str(handoff.get("projectId")) != payload.projectId:
        raise PlatformCoreRuntimeError("Workspace handoff belongs to a different project.", 409, "workspace-project-scope-mismatch")
    workspace_ref = f"workspace:handoff:{payload.handoffId}"
    request = {"data": {"session_id": session.core_session_id, "handoff_ref": workspace_ref, "source_product_ref": handoff.get("sourceProduct"), "target_product_ref": handoff.get("destinationProduct"), "context_ref": f"workspace:handoff:{payload.handoffId}:package:{handoff.get('packageFingerprint')}", "status": handoff.get("status") or "recorded", "visibility": payload.visibility, "metadata": {"workspaceHandoffIntent": handoff.get("intent"), "workspacePackageFingerprint": handoff.get("packageFingerprint"), "workspaceProjectId": payload.projectId, **payload.metadata}}}
    response = _request("POST", CORE_API_ROOT + "/handoff-bindings", request)
    receipt = _record(db, user_key, payload.projectId, session.core_session_id, "bind-handoff", "handoff", workspace_ref, str(response.get("id") or ""), request, response)
    return {"ok": True, "item": response, "receipt": _receipt_payload(receipt)}


def session_view(db: Session, user_key: str, session_id: str, view: Literal["summary", "lineage", "bundle"]) -> dict[str, Any]:
    if _mapping_by_session(db, user_key, session_id) is None:
        raise PlatformCoreRuntimeError("Platform Core session is not bound to this Workspace account.", 404, "platform-core-session-not-found")
    return _request("GET", f"{CORE_API_ROOT}/sessions/{session_id}/{view}")


def list_receipts(db: Session, user_key: str, project_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    query = select(PlatformCoreRuntimeReceipt).where(PlatformCoreRuntimeReceipt.user_key == user_key)
    if project_id:
        query = query.where(PlatformCoreRuntimeReceipt.project_id == project_id)
    rows = db.scalars(query.order_by(PlatformCoreRuntimeReceipt.created_at.desc()).limit(limit)).all()
    return [_receipt_payload(row) for row in rows]
