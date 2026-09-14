from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import MigrationReceipt, NotebookHead, NotebookRevision, ProjectHead, ProjectRevision
from .schemas import LegacyMigrationRequest, NotebookStoreRequest, ProjectStoreRequest
from .utils import canonical_bytes, ordered_sha256_hex, sha256_hex, workspace_project_fingerprint


def _parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def _source_fingerprint(payload: LegacyMigrationRequest) -> str:
    source = {
        "source": payload.source,
        "projects": [r.model_dump(mode="json") for r in payload.projects],
        "notebooks": [r.model_dump(mode="json") for r in payload.notebooks],
    }
    return sha256_hex(source)


def migration_plan(db: Session, user_key: str, payload: LegacyMigrationRequest) -> dict:
    items: list[dict] = []
    conflicts: list[dict] = []
    for record in payload.projects:
        current = db.get(ProjectHead, {"user_key": user_key, "project_id": record.id})
        incoming_fp = sha256_hex(record.payload)
        if current is None:
            action = "import"
        elif current.fingerprint == incoming_fp:
            action = "skip-identical"
        else:
            action = "conflict"
            conflicts.append({"kind": "project", "id": record.id, "backendRevision": current.revision, "legacyRevision": record.revision})
        items.append({"kind": "project", "id": record.id, "revision": record.revision, "action": action})
    for record in payload.notebooks:
        current = db.get(NotebookHead, {"user_key": user_key, "notebook_id": record.id})
        incoming_fp = sha256_hex(record.payload)
        if current is None:
            action = "import"
        elif current.fingerprint == incoming_fp:
            action = "skip-identical"
        else:
            action = "conflict"
            conflicts.append({"kind": "notebook", "id": record.id, "backendRevision": current.revision, "legacyRevision": record.revision})
        items.append({"kind": "notebook", "id": record.id, "revision": record.revision, "action": action})
    return {
        "schema": "sc-workspace-legacy-migration-plan/1.0",
        "sourceFingerprint": _source_fingerprint(payload),
        "projectCount": len(payload.projects),
        "notebookCount": len(payload.notebooks),
        "conflictCount": len(conflicts),
        "safeToApply": not conflicts,
        "items": items,
        "conflicts": conflicts,
        "destructive": False,
        "legacyStoreRetained": True,
    }


def _import_project(db: Session, user_key: str, record) -> None:
    validated = ProjectStoreRequest.model_validate(record.payload)
    project = validated.project
    if validated.sourceProjectId.strip() != record.id:
        raise HTTPException(status_code=400, detail=f"Legacy project id mismatch for {record.id}.")
    if project.get("schema") not in {f"sc-workspace-project/{n}.0" for n in range(12, 21)}:
        raise HTTPException(status_code=400, detail=f"Legacy project {record.id} has an incompatible project schema.")
    now = _parse_time(record.backedUpAt)
    package_fp = sha256_hex(record.payload)
    project_fp = workspace_project_fingerprint(project)
    title = (validated.projectTitle or str(project.get("title") or "Workspace project")).strip()[:1000]
    object_count = len(project.get("objects") or []) if isinstance(project.get("objects"), list) else 0
    row = ProjectHead(
        user_key=user_key, project_id=record.id, title=title,
        client_updated_at=validated.clientUpdatedAt or str(project.get("updatedAt") or ""),
        backed_up_at=now, fingerprint=package_fp, project_fingerprint=project_fp,
        revision=record.revision, storage_mode=record.storageMode, bytes=len(canonical_bytes(record.payload)),
        object_count=object_count, last_operation_id=(validated.operationId or ""), package=record.payload,
        created_at=now, updated_at=now,
    )
    db.add(row)
    db.add(ProjectRevision(
        user_key=user_key, project_id=record.id, revision=record.revision, title=title,
        backed_up_at=now, fingerprint=package_fp, project_fingerprint=project_fp,
        storage_mode=record.storageMode, bytes=row.bytes, object_count=object_count,
        operation_id=(validated.operationId or ""), package=record.payload, created_at=now,
    ))


def _import_notebook(db: Session, user_key: str, record) -> None:
    validated = NotebookStoreRequest.model_validate(record.payload)
    notebook = validated.notebook
    if validated.sourceNotebookId.strip() != record.id:
        raise HTTPException(status_code=400, detail=f"Legacy notebook id mismatch for {record.id}.")
    if notebook.get("schema") != "sc-workspace-notebook/3.0":
        raise HTTPException(status_code=400, detail=f"Legacy notebook {record.id} has an incompatible notebook schema.")
    now = _parse_time(record.backedUpAt)
    package_fp = sha256_hex(record.payload)
    notebook_fp = (validated.notebookFingerprint or ordered_sha256_hex(notebook)).strip()[:128]
    title = (validated.notebookTitle or str(notebook.get("title") or "Research Notebook")).strip()[:1000]
    row = NotebookHead(
        user_key=user_key, notebook_id=record.id, project_id=(validated.sourceProjectId or "")[:160],
        title=title, client_updated_at=validated.clientUpdatedAt or str(notebook.get("updatedAt") or ""),
        backed_up_at=now, fingerprint=package_fp, notebook_fingerprint=notebook_fp,
        revision=record.revision, storage_mode=record.storageMode, bytes=len(canonical_bytes(record.payload)),
        last_operation_id=(validated.operationId or ""), package=record.payload, created_at=now, updated_at=now,
    )
    db.add(row)
    db.add(NotebookRevision(
        user_key=user_key, notebook_id=record.id, revision=record.revision, project_id=row.project_id,
        title=title, backed_up_at=now, fingerprint=package_fp, notebook_fingerprint=notebook_fp,
        storage_mode=record.storageMode, bytes=row.bytes, operation_id=(validated.operationId or ""),
        package=record.payload, created_at=now,
    ))


def apply_migration(db: Session, user_key: str, payload: LegacyMigrationRequest) -> dict:
    plan = migration_plan(db, user_key, payload)
    if not plan["safeToApply"]:
        raise HTTPException(status_code=409, detail={"message": "Legacy Workspace migration has conflicts; nothing was imported.", "plan": plan})
    source_fp = plan["sourceFingerprint"]
    existing_receipt = db.scalar(select(MigrationReceipt).where(MigrationReceipt.user_key == user_key, MigrationReceipt.source_fingerprint == source_fp))
    if existing_receipt:
        return {"ok": True, "replayed": True, "receipt": receipt_payload(existing_receipt), "legacyStoreRetained": True}

    imported_projects = 0
    imported_notebooks = 0
    skipped = 0
    actions = {(i["kind"], i["id"]): i["action"] for i in plan["items"]}
    for record in payload.projects:
        if actions[("project", record.id)] == "import":
            _import_project(db, user_key, record)
            imported_projects += 1
        else:
            skipped += 1
    for record in payload.notebooks:
        if actions[("notebook", record.id)] == "import":
            _import_notebook(db, user_key, record)
            imported_notebooks += 1
        else:
            skipped += 1

    receipt_id = "legacy-" + source_fp[:24]
    receipt = MigrationReceipt(
        user_key=user_key, receipt_id=receipt_id, source=payload.source,
        source_fingerprint=source_fp, project_count=len(payload.projects), notebook_count=len(payload.notebooks),
        imported_project_count=imported_projects, imported_notebook_count=imported_notebooks,
        skipped_count=skipped, status="complete", details={"plan": plan},
    )
    db.add(receipt)
    db.commit()
    return {"ok": True, "replayed": False, "receipt": receipt_payload(receipt), "legacyStoreRetained": True}


def receipt_payload(row: MigrationReceipt) -> dict:
    return {
        "receiptId": row.receipt_id,
        "source": row.source,
        "sourceFingerprint": row.source_fingerprint,
        "projectCount": row.project_count,
        "notebookCount": row.notebook_count,
        "importedProjectCount": row.imported_project_count,
        "importedNotebookCount": row.imported_notebook_count,
        "skippedCount": row.skipped_count,
        "status": row.status,
        "createdAt": row.created_at.isoformat() if row.created_at else "",
    }


def list_receipts(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(MigrationReceipt).where(MigrationReceipt.user_key == user_key).order_by(MigrationReceipt.created_at.desc())).all()
    return [receipt_payload(r) for r in rows]
