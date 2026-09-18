from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import LocalFirstSyncReceipt
from .repository import (
    delete_notebook, delete_project, get_notebook, get_project, list_projects,
    notebook_metadata, project_metadata, store_notebook, store_project,
)
from .schemas import LocalFirstSyncEnvelope, LocalFirstSyncReconcileRequest, NotebookStoreRequest, ProjectStoreRequest
from .utils import iso, sha256_hex

PROFILE_SCHEMA = "sc-workspace-local-first-sync/1.0"
RECEIPT_SCHEMA = "sc-workspace-local-first-sync-receipt/1.0"
BOOTSTRAP_SCHEMA = "sc-workspace-local-first-sync-bootstrap/1.0"
RECONCILE_SCHEMA = "sc-workspace-local-first-sync-reconciliation/1.0"


def profile() -> dict[str, Any]:
    return {
        "schema": PROFILE_SCHEMA,
        "mode": "local-first-server-authoritative",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "canonicalStore": "postgresql",
        "localDraftsAllowed": True,
        "offlineOutboxAllowed": True,
        "offlineOutboxAuthoritative": False,
        "pendingMutationsAreDrafts": True,
        "clientGeneratedEnvelopeIds": True,
        "clientGeneratedOperationIds": True,
        "baseRevisionRequired": True,
        "baseFingerprintSupported": True,
        "retrySafeIdempotency": True,
        "conflictDetection": "base-revision-and-fingerprint",
        "automaticSemanticMerge": False,
        "serverRehydrationAfterApply": True,
        "serverRehydrationAfterConflict": True,
        "revisionVectorReconciliation": True,
        "durableSyncReceipts": True,
        "supportedObjectKinds": ["project", "notebook"],
        "supportedMutations": ["put", "delete"],
        "canonicalCachePersistent": False,
        "arbitraryCodeExecution": False,
    }


def _receipt_metadata(row: LocalFirstSyncReceipt) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "receiptId": row.receipt_id,
        "envelopeId": row.envelope_id,
        "operationId": row.operation_id,
        "deviceId": row.device_id,
        "objectKind": row.object_kind,
        "objectId": row.object_id,
        "baseRevision": row.base_revision,
        "serverRevision": row.server_revision,
        "status": row.status,
        "requestFingerprint": row.request_fingerprint,
        "canonicalFingerprint": row.canonical_fingerprint,
        "result": row.result_json,
        "createdAt": iso(row.created_at),
    }


def list_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(LocalFirstSyncReceipt).where(LocalFirstSyncReceipt.user_key == user_key)
        .order_by(LocalFirstSyncReceipt.created_at.desc()).limit(max(1, min(int(limit), 500)))
    ).all()
    return [_receipt_metadata(r) for r in rows]


def _find_replay(db: Session, user_key: str, envelope_id: str, operation_id: str) -> LocalFirstSyncReceipt | None:
    return db.scalar(select(LocalFirstSyncReceipt).where(
        LocalFirstSyncReceipt.user_key == user_key,
        ((LocalFirstSyncReceipt.envelope_id == envelope_id) | (LocalFirstSyncReceipt.operation_id == operation_id)),
    ).order_by(LocalFirstSyncReceipt.created_at.desc()).limit(1))


def _head(db: Session, user_key: str, kind: str, object_id: str):
    return get_project(db, user_key, object_id) if kind == "project" else get_notebook(db, user_key, object_id)


def _metadata(row, kind: str) -> dict[str, Any] | None:
    if row is None:
        return None
    return project_metadata(row) if kind == "project" else notebook_metadata(row)


def _fingerprint(row, kind: str) -> str:
    if row is None:
        return ""
    return str(row.project_fingerprint if kind == "project" else row.notebook_fingerprint)


def _record(db: Session, user_key: str, env: LocalFirstSyncEnvelope, status: str, server_revision: int, canonical_fingerprint: str, result: dict[str, Any]) -> LocalFirstSyncReceipt:
    row = LocalFirstSyncReceipt(
        user_key=user_key, receipt_id=f"sync_{uuid4().hex}", envelope_id=env.envelopeId,
        operation_id=env.operationId, device_id=env.deviceId, object_kind=env.objectKind,
        object_id=env.objectId, base_revision=env.baseRevision, server_revision=server_revision,
        status=status, request_fingerprint=sha256_hex(env.model_dump(mode="json", by_alias=True)),
        canonical_fingerprint=canonical_fingerprint, envelope_json=env.model_dump(mode="json", by_alias=True),
        result_json=result,
    )
    db.add(row); db.commit(); db.refresh(row); return row


def bootstrap(db: Session, user_key: str) -> dict[str, Any]:
    projects = list_projects(db, user_key)
    vector = {str(x.get("projectId")): int(x.get("revision") or 0) for x in projects if x.get("projectId")}
    payload = {"revisionVector": vector, "projectCount": len(projects)}
    return {
        "schema": BOOTSTRAP_SCHEMA, "generatedServerSide": True, "backendAuthoritative": True,
        "revisionVector": vector, "checkpoint": sha256_hex(payload),
        "clientPolicy": {"queueOfflineMutations": True, "queuedMutationsAuthoritative": False,
            "requireBaseRevision": True, "rehydrateAfterApply": True, "rehydrateAfterConflict": True},
    }


def apply_envelope(db: Session, user_key: str, env: LocalFirstSyncEnvelope) -> tuple[int, dict[str, Any]]:
    replay = _find_replay(db, user_key, env.envelopeId, env.operationId)
    if replay is not None:
        return (409 if replay.status == "conflict" else 200), {
            "schema": "sc-workspace-sync-result/1.0", "ok": replay.status != "conflict",
            "replayed": True, "status": replay.status, "receipt": _receipt_metadata(replay), **replay.result_json,
        }

    head = _head(db, user_key, env.objectKind, env.objectId)
    current_revision = int(head.revision if head is not None else 0)
    current_fp = _fingerprint(head, env.objectKind)
    metadata = _metadata(head, env.objectKind)
    conflict_reason = ""
    if env.baseRevision != current_revision:
        conflict_reason = "base-revision-mismatch"
    elif env.baseFingerprint and current_revision > 0 and env.baseFingerprint != current_fp:
        conflict_reason = "base-fingerprint-mismatch"
    if conflict_reason:
        result = {"conflict": {"reason": conflict_reason, "baseRevision": env.baseRevision,
            "serverRevision": current_revision, "serverFingerprint": current_fp, "canonicalHead": metadata},
            "rehydrateRequired": True, "canonicalHead": metadata}
        receipt = _record(db, user_key, env, "conflict", current_revision, current_fp, result)
        return 409, {"schema":"sc-workspace-sync-result/1.0","ok":False,"replayed":False,"status":"conflict","receipt":_receipt_metadata(receipt),**result}

    mutation = dict(env.mutation or {})
    action = str(mutation.get("action") or "put")
    if action not in {"put", "delete"}:
        raise HTTPException(status_code=400, detail={"code":"unsupported-sync-mutation","message":"Sync mutation action must be put or delete."})

    if action == "delete":
        deleted = delete_project(db, user_key, env.objectId) if env.objectKind == "project" else delete_notebook(db, user_key, env.objectId)
        result = {"mutation":"delete","deleted":deleted,"serverRevision":current_revision,"rehydrateRequired":True,"canonicalHead":None}
        receipt = _record(db, user_key, env, "applied", current_revision, current_fp, result)
        return 200, {"schema":"sc-workspace-sync-result/1.0","ok":True,"replayed":False,"status":"applied","receipt":_receipt_metadata(receipt),**result}

    document = mutation.get("document")
    if not isinstance(document, dict):
        raise HTTPException(status_code=400, detail={"code":"sync-document-required","message":"put mutation requires a document object."})
    if env.objectKind == "project":
        req = ProjectStoreRequest.model_validate({"schema":"sc-workspace-sync-push/1.0","sourceProjectId":env.objectId,
            "projectTitle":mutation.get("title"),"clientUpdatedAt":env.clientUpdatedAt,"expectedRevision":env.baseRevision,
            "operationId":env.operationId,"project":document})
        row, replayed = store_project(db, user_key, req)
        metadata = project_metadata(row); fp = row.project_fingerprint
    else:
        req = NotebookStoreRequest.model_validate({"schema":"sc-workspace-notebook-sync-push/1.0","sourceNotebookId":env.objectId,
            "sourceProjectId":mutation.get("projectId"),"notebookTitle":mutation.get("title"),"clientUpdatedAt":env.clientUpdatedAt,
            "expectedRevision":env.baseRevision,"operationId":env.operationId,"notebook":document})
        row, replayed = store_notebook(db, user_key, req)
        metadata = notebook_metadata(row); fp = row.notebook_fingerprint
    result = {"mutation":"put","serverRevision":int(row.revision),"canonicalFingerprint":str(fp),
        "canonicalHead":metadata,"rehydrateRequired":True,"underlyingMutationReplayed":replayed}
    receipt = _record(db, user_key, env, "applied", int(row.revision), str(fp), result)
    return 200, {"schema":"sc-workspace-sync-result/1.0","ok":True,"replayed":False,"status":"applied","receipt":_receipt_metadata(receipt),**result}


def reconcile(db: Session, user_key: str, request: LocalFirstSyncReconcileRequest) -> dict[str, Any]:
    server = {str(x.get("projectId")): int(x.get("revision") or 0) for x in list_projects(db, user_key) if x.get("projectId")}
    ids = set(server) | set(request.clientRevisionVector)
    if request.projectIds:
        ids &= set(request.projectIds)
    items=[]
    for project_id in sorted(ids):
        sr=int(server.get(project_id,0)); cr=int(request.clientRevisionVector.get(project_id,0))
        if sr==cr: status="up-to-date"
        elif sr>cr: status="server-ahead"
        elif sr==0 and cr>0: status="missing-server"
        else: status="client-ahead"
        items.append({"projectId":project_id,"clientRevision":cr,"serverRevision":sr,"status":status,
            "action":"none" if status=="up-to-date" else ("rehydrate" if status=="server-ahead" else "push-pending-envelope")})
    payload={"schema":RECONCILE_SCHEMA,"generatedServerSide":True,"backendAuthoritative":True,"deviceId":request.deviceId,
        "items":items,"serverRevisionVector":server,"automaticMerge":False}
    payload["reconciliationFingerprint"]=sha256_hex(payload)
    return payload
