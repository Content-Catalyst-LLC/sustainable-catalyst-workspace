from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ArtifactHead, ArtifactRevision, ExecutionEnvironmentHead, ExecutionEnvironmentRevision
from .schemas import ExecutionEnvironmentStoreRequest
from .utils import iso, sha256_hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_names(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()[:255]
        if not value or "=" in value:
            continue
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key); out.append(value)
    return sorted(out, key=str.casefold)[:200]


def _artifact_ref(db: Session, user_key: str, artifact_id: str, revision: int | None) -> dict:
    if revision is None:
        row = db.get(ArtifactHead, {"user_key": user_key, "artifact_id": artifact_id})
    else:
        row = db.get(ArtifactRevision, {"user_key": user_key, "artifact_id": artifact_id, "revision": revision})
    if row is None:
        raise HTTPException(status_code=409, detail="Execution environment lock artifact does not reference a stored Workspace artifact revision.")
    return {
        "artifactId": row.artifact_id,
        "revision": int(row.revision),
        "filename": row.filename,
        "mediaType": row.media_type,
        "sha256": row.sha256,
        "bytes": int(row.bytes),
    }


def environment_metadata(row) -> dict:
    return {
        "environmentId": row.environment_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "revision": int(row.revision),
        "fingerprint": row.fingerprint,
        "runtime": row.runtime_json,
        "dependencies": row.dependencies_json,
        "lockArtifacts": row.lock_artifacts_json,
        "container": row.container_json,
        "system": row.system_json,
        "hardware": row.hardware_json,
        "randomSeeds": row.random_seeds_json,
        "environmentVariableNames": row.env_var_names_json,
        "configuration": row.configuration_json,
        "metadata": row.metadata_json,
        "secretsCaptured": False,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def _document(payload: ExecutionEnvironmentStoreRequest, lock_artifacts: list[dict]) -> dict:
    return {
        "runtime": payload.runtime,
        "dependencies": payload.dependencies,
        "lockArtifacts": lock_artifacts,
        "container": payload.container,
        "system": payload.system,
        "hardware": payload.hardware,
        "randomSeeds": payload.randomSeeds,
        "environmentVariableNames": _clean_names(payload.environmentVariableNames),
        "configuration": payload.configuration,
    }


def _revision_guard(existing, expected_revision: int | None) -> int:
    current = int(existing.revision) if existing is not None else 0
    if existing is None:
        if expected_revision not in (None, 0):
            raise HTTPException(status_code=409, detail={"message": "Workspace execution-environment revision conflict.", "currentRevision": 0, "current": None})
        return 0
    if expected_revision is None or int(expected_revision) != current:
        raise HTTPException(status_code=409, detail={"message": "Workspace execution-environment revision conflict.", "currentRevision": current, "current": environment_metadata(existing)})
    return current


def store_environment(db: Session, user_key: str, payload: ExecutionEnvironmentStoreRequest):
    settings = get_settings()
    existing = db.get(ExecutionEnvironmentHead, {"user_key": user_key, "environment_id": payload.environmentId})
    operation_id = (payload.operationId or "").strip()
    lock_artifacts = [_artifact_ref(db, user_key, ref.artifactId, ref.revision) for ref in payload.lockArtifacts]
    document = _document(payload, lock_artifacts)
    fingerprint = sha256_hex(document)
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Execution-environment operationId was already used for a different manifest.")
        return existing, True
    current = _revision_guard(existing, payload.expectedRevision)
    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(ExecutionEnvironmentHead).where(ExecutionEnvironmentHead.user_key == user_key)) or 0)
        if count >= settings.max_execution_environments_per_account:
            raise HTTPException(status_code=409, detail="Workspace execution-environment registry limit reached.")
    revision = current + 1; now = _now(); names = _clean_names(payload.environmentVariableNames)
    values = dict(
        project_id=(payload.projectId or "").strip(), name=payload.name.strip(), description=payload.description.strip(),
        revision=revision, fingerprint=fingerprint, runtime_json=payload.runtime, dependencies_json=payload.dependencies,
        lock_artifacts_json=lock_artifacts, container_json=payload.container, system_json=payload.system, hardware_json=payload.hardware,
        random_seeds_json=payload.randomSeeds, env_var_names_json=names, configuration_json=payload.configuration, metadata_json=payload.metadata,
    )
    if existing is None:
        existing = ExecutionEnvironmentHead(user_key=user_key, environment_id=payload.environmentId, last_operation_id=operation_id, created_at=now, updated_at=now, **values)
        db.add(existing)
    else:
        for key, value in values.items(): setattr(existing, key, value)
        existing.last_operation_id = operation_id; existing.updated_at = now
    db.add(ExecutionEnvironmentRevision(
        user_key=user_key, environment_id=payload.environmentId, operation_id=operation_id, created_at=now, **values
    ))
    try:
        db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="A concurrent Workspace execution-environment revision was detected.")
    db.refresh(existing); return existing, False


def get_environment(db: Session, user_key: str, environment_id: str):
    return db.get(ExecutionEnvironmentHead, {"user_key": user_key, "environment_id": environment_id})


def get_environment_revision(db: Session, user_key: str, environment_id: str, revision: int):
    return db.get(ExecutionEnvironmentRevision, {"user_key": user_key, "environment_id": environment_id, "revision": revision})


def list_environments(db: Session, user_key: str, project_id: str | None = None) -> list[dict]:
    stmt = select(ExecutionEnvironmentHead).where(ExecutionEnvironmentHead.user_key == user_key)
    if project_id: stmt = stmt.where(ExecutionEnvironmentHead.project_id == project_id)
    rows = db.scalars(stmt.order_by(ExecutionEnvironmentHead.updated_at.desc())).all()
    return [environment_metadata(r) for r in rows]


def list_environment_revisions(db: Session, user_key: str, environment_id: str) -> list[dict]:
    rows = db.scalars(select(ExecutionEnvironmentRevision).where(
        ExecutionEnvironmentRevision.user_key == user_key, ExecutionEnvironmentRevision.environment_id == environment_id
    ).order_by(ExecutionEnvironmentRevision.revision.desc())).all()
    return [environment_metadata(r) for r in rows]


def resolve_environment_ref(db: Session, user_key: str, ref) -> tuple[dict, object | None]:
    if ref is None:
        return {}, None
    row = get_environment_revision(db, user_key, ref.environmentId, ref.revision) if ref.revision else get_environment(db, user_key, ref.environmentId)
    if row is None:
        raise HTTPException(status_code=409, detail="Execution run references an unavailable Workspace execution environment.")
    return {"environmentId": row.environment_id, "revision": int(row.revision), "fingerprint": row.fingerprint}, row
