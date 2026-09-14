from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectHead(Base):
    __tablename__ = "workspace_project_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    client_updated_at: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    backed_up_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    project_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    object_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    package: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ProjectRevision(Base):
    __tablename__ = "workspace_project_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    backed_up_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    project_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    object_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    package: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class NotebookHead(Base):
    __tablename__ = "workspace_notebook_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    notebook_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    client_updated_at: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    backed_up_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    notebook_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    package: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class NotebookRevision(Base):
    __tablename__ = "workspace_notebook_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    notebook_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    backed_up_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    notebook_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    package: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class MigrationReceipt(Base):
    __tablename__ = "workspace_migration_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    source: Mapped[str] = mapped_column(String(96), nullable=False)
    source_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    project_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notebook_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_project_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_notebook_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="complete")
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ArtifactHead(Base):
    __tablename__ = "workspace_artifact_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    filename: Mapped[str] = mapped_column(Text, nullable=False, default="artifact")
    media_type: Mapped[str] = mapped_column(String(255), nullable=False, default="application/octet-stream")
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ArtifactRevision(Base):
    __tablename__ = "workspace_artifact_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    filename: Mapped[str] = mapped_column(Text, nullable=False, default="artifact")
    media_type: Mapped[str] = mapped_column(String(255), nullable=False, default="application/octet-stream")
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class RecoverySnapshot(Base):
    __tablename__ = "workspace_recovery_snapshots"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    reason: Mapped[str] = mapped_column(String(160), nullable=False, default="manual")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    project_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notebook_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    artifact_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
