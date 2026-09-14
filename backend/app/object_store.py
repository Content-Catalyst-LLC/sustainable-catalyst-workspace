from __future__ import annotations

import base64
import binascii
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ArtifactHead, ArtifactRevision
from .schemas import ArtifactStoreRequest
from .utils import iso


def artifact_metadata(row: ArtifactHead) -> dict:
    return {
        "artifactId": row.artifact_id,
        "projectId": row.project_id,
        "filename": row.filename,
        "mediaType": row.media_type,
        "bytes": row.bytes,
        "sha256": row.sha256,
        "revision": row.revision,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _root() -> Path:
    root = Path(get_settings().object_storage_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _storage_key(digest: str) -> str:
    return f"sha256/{digest[:2]}/{digest[2:4]}/{digest}"


def _path_for_key(key: str) -> Path:
    root = _root()
    path = (root / key).resolve()
    if root != path and root not in path.parents:
        raise HTTPException(status_code=500, detail="Invalid object storage path.")
    return path


def _decode(content: str) -> bytes:
    try:
        return base64.b64decode(content.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError, binascii.Error):
        raise HTTPException(status_code=400, detail="Artifact contentBase64 is not valid base64.")


def list_artifacts(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(ArtifactHead).where(ArtifactHead.user_key == user_key).order_by(ArtifactHead.updated_at.desc())).all()
    return [artifact_metadata(r) for r in rows]


def get_artifact(db: Session, user_key: str, artifact_id: str) -> ArtifactHead | None:
    return db.get(ArtifactHead, {"user_key": user_key, "artifact_id": artifact_id})


def artifact_account_bytes(db: Session, user_key: str, replacing_artifact_id: str | None = None) -> int:
    stmt = select(func.coalesce(func.sum(ArtifactHead.bytes), 0)).where(ArtifactHead.user_key == user_key)
    if replacing_artifact_id:
        stmt = stmt.where(ArtifactHead.artifact_id != replacing_artifact_id)
    return int(db.scalar(stmt) or 0)


def store_artifact(db: Session, user_key: str, payload: ArtifactStoreRequest) -> ArtifactHead:
    settings = get_settings()
    content = _decode(payload.contentBase64)
    byte_count = len(content)
    if byte_count > settings.max_artifact_bytes:
        raise HTTPException(status_code=413, detail="Workspace artifact exceeds the configured artifact size limit.")

    artifact_id = payload.artifactId.strip()
    existing = get_artifact(db, user_key, artifact_id)
    current_revision = existing.revision if existing else 0
    if existing is not None:
        if payload.expectedRevision is None or payload.expectedRevision != current_revision:
            raise HTTPException(status_code=409, detail={"message": "Workspace artifact revision conflict.", "currentRevision": current_revision, "current": artifact_metadata(existing)})
    elif payload.expectedRevision not in (None, 0):
        raise HTTPException(status_code=409, detail={"message": "Workspace artifact revision conflict.", "currentRevision": 0, "current": None})

    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(ArtifactHead).where(ArtifactHead.user_key == user_key)) or 0)
        if count >= settings.max_artifacts_per_account:
            raise HTTPException(status_code=409, detail="Workspace artifact count limit reached.")
    if artifact_account_bytes(db, user_key, artifact_id) + byte_count > settings.max_artifact_account_bytes:
        raise HTTPException(status_code=409, detail="Workspace artifact account storage limit reached.")

    digest = hashlib.sha256(content).hexdigest()
    key = _storage_key(digest)
    path = _path_for_key(key)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + f".tmp-{os.getpid()}")
        temp.write_bytes(content)
        os.replace(temp, path)
    elif path.stat().st_size != byte_count:
        raise HTTPException(status_code=500, detail="Content-addressed object collision detected.")

    revision = current_revision + 1
    now = datetime.now(timezone.utc)
    if existing is None:
        existing = ArtifactHead(user_key=user_key, artifact_id=artifact_id, created_at=now)
        db.add(existing)
    existing.project_id = (payload.projectId or "")[:160]
    existing.filename = payload.filename.strip() or "artifact"
    existing.media_type = payload.mediaType.strip() or "application/octet-stream"
    existing.bytes = byte_count
    existing.sha256 = digest
    existing.storage_key = key
    existing.revision = revision
    existing.metadata_json = payload.metadata
    existing.updated_at = now
    db.add(ArtifactRevision(
        user_key=user_key,
        artifact_id=artifact_id,
        revision=revision,
        project_id=existing.project_id,
        filename=existing.filename,
        media_type=existing.media_type,
        bytes=byte_count,
        sha256=digest,
        storage_key=key,
        metadata_json=payload.metadata,
        created_at=now,
    ))
    db.commit()
    db.refresh(existing)
    return existing


def read_artifact_content(row: ArtifactHead) -> bytes:
    path = _path_for_key(row.storage_key)
    if not path.is_file():
        raise HTTPException(status_code=503, detail="Artifact blob is missing from object storage.")
    content = path.read_bytes()
    if len(content) != row.bytes or hashlib.sha256(content).hexdigest() != row.sha256:
        raise HTTPException(status_code=503, detail="Artifact blob failed integrity verification.")
    return content


def delete_artifact(db: Session, user_key: str, artifact_id: str) -> bool:
    row = get_artifact(db, user_key, artifact_id)
    if row is None:
        return False
    revisions = db.scalars(select(ArtifactRevision).where(ArtifactRevision.user_key == user_key, ArtifactRevision.artifact_id == artifact_id)).all()
    for revision in revisions:
        db.delete(revision)
    db.delete(row)
    db.commit()
    # Blob garbage collection is deliberately deferred because content-addressed blobs may be shared by revisions/users.
    return True


def verify_artifact_storage(db: Session, user_key: str) -> dict:
    rows = db.scalars(select(ArtifactHead).where(ArtifactHead.user_key == user_key)).all()
    checked = 0
    missing: list[str] = []
    corrupt: list[str] = []
    for row in rows:
        checked += 1
        path = _path_for_key(row.storage_key)
        if not path.is_file():
            missing.append(row.artifact_id)
            continue
        content = path.read_bytes()
        if len(content) != row.bytes or hashlib.sha256(content).hexdigest() != row.sha256:
            corrupt.append(row.artifact_id)
    return {"ok": not missing and not corrupt, "checked": checked, "missing": missing, "corrupt": corrupt}
