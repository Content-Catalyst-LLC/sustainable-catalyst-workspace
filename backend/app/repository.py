from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import NotebookHead, NotebookRevision, ProjectHead, ProjectRevision
from .schemas import NotebookStoreRequest, ProjectStoreRequest
from .utils import canonical_bytes, iso, ordered_sha256_hex, sha256_hex, workspace_project_fingerprint


def project_metadata(row: ProjectHead) -> dict:
    return {
        "projectId": row.project_id,
        "title": row.title,
        "clientUpdatedAt": row.client_updated_at,
        "backedUpAt": iso(row.backed_up_at),
        "fingerprint": row.fingerprint,
        "projectFingerprint": row.project_fingerprint,
        "revision": row.revision,
        "storageMode": row.storage_mode,
        "bytes": row.bytes,
        "objectCount": row.object_count,
    }


def notebook_metadata(row: NotebookHead) -> dict:
    return {
        "notebookId": row.notebook_id,
        "projectId": row.project_id,
        "title": row.title,
        "clientUpdatedAt": row.client_updated_at,
        "backedUpAt": iso(row.backed_up_at),
        "fingerprint": row.fingerprint,
        "notebookFingerprint": row.notebook_fingerprint,
        "revision": row.revision,
        "storageMode": row.storage_mode,
        "bytes": row.bytes,
    }


def list_projects(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(ProjectHead).where(ProjectHead.user_key == user_key).order_by(ProjectHead.backed_up_at.desc())).all()
    return [project_metadata(row) for row in rows]


def get_project(db: Session, user_key: str, project_id: str) -> ProjectHead | None:
    return db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})


def _account_bytes(db: Session, user_key: str, replacing_project_id: str | None = None) -> int:
    stmt = select(func.coalesce(func.sum(ProjectHead.bytes), 0)).where(ProjectHead.user_key == user_key)
    if replacing_project_id:
        stmt = stmt.where(ProjectHead.project_id != replacing_project_id)
    return int(db.scalar(stmt) or 0)


def store_project(db: Session, user_key: str, payload: ProjectStoreRequest) -> tuple[ProjectHead, bool]:
    settings = get_settings()
    package = payload.model_dump(mode="json", exclude_none=True)
    project = payload.project
    if project.get("schema") not in {f"sc-workspace-project/{n}.0" for n in range(12, 21)}:
        raise HTTPException(status_code=400, detail="A compatible Workspace project schema (12.0 through 20.0) is required.")
    raw = canonical_bytes(package)
    byte_count = len(raw)
    if byte_count > settings.max_project_bytes:
        raise HTTPException(status_code=413, detail="Workspace project exceeds the configured backend project limit.")

    project_id = payload.sourceProjectId.strip()
    existing = get_project(db, user_key, project_id)
    current_revision = existing.revision if existing else 0
    is_sync = payload.schema_ == "sc-workspace-sync-push/1.0"
    storage_mode = "sync-head" if is_sync else "manual-backup"
    operation_id = (payload.operationId or "").strip() if is_sync else ""

    if is_sync and operation_id and existing and existing.last_operation_id == operation_id:
        return existing, True
    if not is_sync and existing and existing.storage_mode == "sync-head":
        raise HTTPException(status_code=409, detail="Manual backup cannot replace an active sync head.")
    if is_sync:
        if payload.expectedRevision is None or payload.expectedRevision != current_revision:
            raise HTTPException(
                status_code=409,
                detail={"message": "Workspace sync revision conflict.", "currentRevision": current_revision, "current": project_metadata(existing) if existing else None},
            )

    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(ProjectHead).where(ProjectHead.user_key == user_key)) or 0)
        if count >= settings.max_projects_per_account:
            raise HTTPException(status_code=409, detail="Workspace project count limit reached.")

    if _account_bytes(db, user_key, project_id) + byte_count > settings.max_account_bytes:
        raise HTTPException(status_code=409, detail="Workspace account storage limit reached.")

    revision = current_revision + 1
    now = datetime.now(timezone.utc)
    title = (payload.projectTitle or str(project.get("title") or "Workspace project")).strip()[:1000]
    project_fp = workspace_project_fingerprint(project)
    package_fp = sha256_hex(package)
    object_count = len(project.get("objects") or []) if isinstance(project.get("objects"), list) else 0

    if existing is None:
        existing = ProjectHead(user_key=user_key, project_id=project_id)
        db.add(existing)
    existing.title = title
    existing.client_updated_at = payload.clientUpdatedAt or str(project.get("updatedAt") or "")
    existing.backed_up_at = now
    existing.fingerprint = package_fp
    existing.project_fingerprint = project_fp
    existing.revision = revision
    existing.storage_mode = storage_mode
    existing.bytes = byte_count
    existing.object_count = object_count
    existing.last_operation_id = operation_id
    existing.package = package
    existing.updated_at = now

    db.add(ProjectRevision(
        user_key=user_key,
        project_id=project_id,
        revision=revision,
        title=title,
        backed_up_at=now,
        fingerprint=package_fp,
        project_fingerprint=project_fp,
        storage_mode=storage_mode,
        bytes=byte_count,
        object_count=object_count,
        operation_id=operation_id,
        package=package,
    ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A concurrent Workspace revision was detected.")
    db.refresh(existing)
    return existing, False


def delete_project(db: Session, user_key: str, project_id: str) -> bool:
    head = get_project(db, user_key, project_id)
    if head is None:
        return False
    revisions = db.scalars(select(ProjectRevision).where(ProjectRevision.user_key == user_key, ProjectRevision.project_id == project_id)).all()
    for row in revisions:
        db.delete(row)
    db.delete(head)
    db.commit()
    return True


def list_project_revisions(db: Session, user_key: str, project_id: str) -> list[dict]:
    rows = db.scalars(select(ProjectRevision).where(ProjectRevision.user_key == user_key, ProjectRevision.project_id == project_id).order_by(ProjectRevision.revision.desc())).all()
    return [{"revision": r.revision, "title": r.title, "backedUpAt": iso(r.backed_up_at), "fingerprint": r.fingerprint, "projectFingerprint": r.project_fingerprint, "storageMode": r.storage_mode, "bytes": r.bytes, "objectCount": r.object_count} for r in rows]


def get_project_revision(db: Session, user_key: str, project_id: str, revision: int) -> ProjectRevision | None:
    return db.get(ProjectRevision, {"user_key": user_key, "project_id": project_id, "revision": revision})


def list_notebooks(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(NotebookHead).where(NotebookHead.user_key == user_key).order_by(NotebookHead.backed_up_at.desc())).all()
    return [notebook_metadata(row) for row in rows]


def get_notebook(db: Session, user_key: str, notebook_id: str) -> NotebookHead | None:
    return db.get(NotebookHead, {"user_key": user_key, "notebook_id": notebook_id})


def store_notebook(db: Session, user_key: str, payload: NotebookStoreRequest) -> tuple[NotebookHead, bool]:
    settings = get_settings()
    package = payload.model_dump(mode="json", exclude_none=True)
    notebook = payload.notebook
    if notebook.get("schema") != "sc-workspace-notebook/3.0":
        raise HTTPException(status_code=400, detail="A sc-workspace-notebook/3.0 notebook is required.")
    raw = canonical_bytes(package)
    byte_count = len(raw)
    if byte_count > settings.max_notebook_bytes:
        raise HTTPException(status_code=413, detail="Workspace notebook exceeds the configured backend notebook limit.")

    notebook_id = payload.sourceNotebookId.strip()
    existing = get_notebook(db, user_key, notebook_id)
    current_revision = existing.revision if existing else 0
    is_sync = payload.schema_ == "sc-workspace-notebook-sync-push/1.0"
    storage_mode = "sync-head" if is_sync else "manual-backup"
    operation_id = (payload.operationId or "").strip() if is_sync else ""

    if is_sync and operation_id and existing and existing.last_operation_id == operation_id:
        return existing, True
    if not is_sync and existing and existing.storage_mode == "sync-head":
        raise HTTPException(status_code=409, detail="Manual notebook backup cannot replace an active sync head.")
    if is_sync and (payload.expectedRevision is None or payload.expectedRevision != current_revision):
        raise HTTPException(status_code=409, detail={"message": "Notebook sync revision conflict.", "currentRevision": current_revision, "current": notebook_metadata(existing) if existing else None})

    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(NotebookHead).where(NotebookHead.user_key == user_key)) or 0)
        if count >= settings.max_notebooks_per_account:
            raise HTTPException(status_code=409, detail="Workspace notebook count limit reached.")

    revision = current_revision + 1
    now = datetime.now(timezone.utc)
    title = (payload.notebookTitle or str(notebook.get("title") or "Research Notebook")).strip()[:1000]
    package_fp = sha256_hex(package)
    notebook_fp = (payload.notebookFingerprint or ordered_sha256_hex(notebook)).strip()[:128]

    if existing is None:
        existing = NotebookHead(user_key=user_key, notebook_id=notebook_id)
        db.add(existing)
    existing.project_id = (payload.sourceProjectId or "")[:160]
    existing.title = title
    existing.client_updated_at = payload.clientUpdatedAt or str(notebook.get("updatedAt") or "")
    existing.backed_up_at = now
    existing.fingerprint = package_fp
    existing.notebook_fingerprint = notebook_fp
    existing.revision = revision
    existing.storage_mode = storage_mode
    existing.bytes = byte_count
    existing.last_operation_id = operation_id
    existing.package = package
    existing.updated_at = now

    db.add(NotebookRevision(
        user_key=user_key,
        notebook_id=notebook_id,
        revision=revision,
        project_id=existing.project_id,
        title=title,
        backed_up_at=now,
        fingerprint=package_fp,
        notebook_fingerprint=notebook_fp,
        storage_mode=storage_mode,
        bytes=byte_count,
        operation_id=operation_id,
        package=package,
    ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A concurrent Workspace notebook revision was detected.")
    db.refresh(existing)
    return existing, False


def delete_notebook(db: Session, user_key: str, notebook_id: str) -> bool:
    head = get_notebook(db, user_key, notebook_id)
    if head is None:
        return False
    revisions = db.scalars(select(NotebookRevision).where(NotebookRevision.user_key == user_key, NotebookRevision.notebook_id == notebook_id)).all()
    for row in revisions:
        db.delete(row)
    db.delete(head)
    db.commit()
    return True
