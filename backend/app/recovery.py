from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ArtifactHead, NotebookHead, ProjectHead, RecoverySnapshot
from .object_store import artifact_metadata
from .repository import notebook_metadata, project_metadata
from .utils import iso, sha256_hex


def create_snapshot(db: Session, user_key: str, reason: str) -> RecoverySnapshot:
    settings = get_settings()
    count = int(db.scalar(select(func.count()).select_from(RecoverySnapshot).where(RecoverySnapshot.user_key == user_key)) or 0)
    if count >= settings.max_recovery_snapshots_per_account:
        oldest = db.scalars(select(RecoverySnapshot).where(RecoverySnapshot.user_key == user_key).order_by(RecoverySnapshot.created_at.asc()).limit(count - settings.max_recovery_snapshots_per_account + 1)).all()
        for row in oldest:
            db.delete(row)
        db.flush()

    projects = db.scalars(select(ProjectHead).where(ProjectHead.user_key == user_key).order_by(ProjectHead.project_id)).all()
    notebooks = db.scalars(select(NotebookHead).where(NotebookHead.user_key == user_key).order_by(NotebookHead.notebook_id)).all()
    artifacts = db.scalars(select(ArtifactHead).where(ArtifactHead.user_key == user_key).order_by(ArtifactHead.artifact_id)).all()
    manifest = {
        "schema": "sc-workspace-recovery-manifest/1.0",
        "projects": [project_metadata(r) for r in projects],
        "notebooks": [notebook_metadata(r) for r in notebooks],
        "artifacts": [artifact_metadata(r) for r in artifacts],
    }
    fingerprint = sha256_hex(manifest)
    row = RecoverySnapshot(
        user_key=user_key,
        snapshot_id=str(uuid4()),
        reason=reason.strip() or "manual",
        fingerprint=fingerprint,
        project_count=len(projects),
        notebook_count=len(notebooks),
        artifact_count=len(artifacts),
        manifest=manifest,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def snapshot_metadata(row: RecoverySnapshot) -> dict:
    return {
        "snapshotId": row.snapshot_id,
        "reason": row.reason,
        "fingerprint": row.fingerprint,
        "projectCount": row.project_count,
        "notebookCount": row.notebook_count,
        "artifactCount": row.artifact_count,
        "createdAt": iso(row.created_at),
    }


def list_snapshots(db: Session, user_key: str) -> list[dict]:
    rows = db.scalars(select(RecoverySnapshot).where(RecoverySnapshot.user_key == user_key).order_by(RecoverySnapshot.created_at.desc())).all()
    return [snapshot_metadata(r) for r in rows]


def get_snapshot(db: Session, user_key: str, snapshot_id: str) -> RecoverySnapshot:
    row = db.get(RecoverySnapshot, {"user_key": user_key, "snapshot_id": snapshot_id})
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace recovery snapshot not found.")
    return row
