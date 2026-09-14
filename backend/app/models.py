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


class JobRecord(Base):
    __tablename__ = "workspace_jobs"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    job_type: Mapped[str] = mapped_column(String(96), nullable=False, default="workspace-task")
    target_product: Mapped[str] = mapped_column(String(64), nullable=False, default="workspace")
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    error_code: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cancellation_requested: Mapped[bool] = mapped_column(nullable=False, default=False)
    worker_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class JobEvent(Base):
    __tablename__ = "workspace_job_events"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class WorkerHeartbeat(Base):
    __tablename__ = "workspace_worker_heartbeats"

    worker_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="idle")
    active_job_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class DatasetHead(Base):
    __tablename__ = "workspace_dataset_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dataset_type: Mapped[str] = mapped_column(String(64), nullable=False, default="other")
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="metadata")
    artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    external_uri: Mapped[str] = mapped_column(Text, nullable=False, default="")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lineage_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class DatasetRevision(Base):
    __tablename__ = "workspace_dataset_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dataset_type: Mapped[str] = mapped_column(String(64), nullable=False, default="other")
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="metadata")
    artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    external_uri: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lineage_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ModelHead(Base):
    __tablename__ = "workspace_model_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="custom")
    framework: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    algorithm: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    version_label: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    source_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    execution_target: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    execution_operation: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    input_schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lineage_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ModelRevision(Base):
    __tablename__ = "workspace_model_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="custom")
    framework: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    algorithm: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    version_label: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    source_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    execution_target: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    execution_operation: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    input_schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_schema_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lineage_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ParameterSetHead(Base):
    __tablename__ = "workspace_parameter_set_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    parameter_set_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    model_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ParameterSetRevision(Base):
    __tablename__ = "workspace_parameter_set_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    parameter_set_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    model_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ExecutionEnvironmentHead(Base):
    __tablename__ = "workspace_execution_environment_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    environment_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    runtime_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dependencies_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lock_artifacts_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    container_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    system_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hardware_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    random_seeds_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    env_var_names_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ExecutionEnvironmentRevision(Base):
    __tablename__ = "workspace_execution_environment_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    environment_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    runtime_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dependencies_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    lock_artifacts_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    container_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    system_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hardware_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    random_seeds_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    env_var_names_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ExecutionRun(Base):
    __tablename__ = "workspace_execution_runs"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False, default="Execution run")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    target_product: Mapped[str] = mapped_column(String(64), nullable=False, default="workspace")
    operation: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    dataset_refs: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    model_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    parameter_set_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    environment_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    environment_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    environment_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    runtime_adapter_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    runtime_adapter_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    input_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    reproducibility_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_summary: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    error_code: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ExecutionRunOutput(Base):
    __tablename__ = "workspace_execution_run_outputs"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    output_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="result")
    label: Mapped[str] = mapped_column(Text, nullable=False, default="")
    media_type: Mapped[str] = mapped_column(String(255), nullable=False, default="application/octet-stream")
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ExecutionRunEvent(Base):
    __tablename__ = "workspace_execution_run_events"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class RuntimeAdapterHead(Base):
    __tablename__ = "workspace_runtime_adapter_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    adapter_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    runtime_family: Mapped[str] = mapped_column(String(64), nullable=False, default="custom")
    runtime_version: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    adapter_type: Mapped[str] = mapped_column(String(64), nullable=False, default="metadata")
    trust_level: Mapped[str] = mapped_column(String(32), nullable=False, default="bounded")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    dependency_managers_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    container_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    platform_constraints_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    capabilities_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class RuntimeAdapterRevision(Base):
    __tablename__ = "workspace_runtime_adapter_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    adapter_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    runtime_family: Mapped[str] = mapped_column(String(64), nullable=False, default="custom")
    runtime_version: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    adapter_type: Mapped[str] = mapped_column(String(64), nullable=False, default="metadata")
    trust_level: Mapped[str] = mapped_column(String(32), nullable=False, default="bounded")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    dependency_managers_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    container_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    platform_constraints_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    capabilities_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    configuration_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ReproductionPlan(Base):
    __tablename__ = "workspace_reproduction_plans"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    original_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    runtime_adapter_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    environment_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    expected_outputs_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    compatibility_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ReproductionVerification(Base):
    __tablename__ = "workspace_reproduction_verifications"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    verification_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    original_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    reproduction_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    exact_inputs: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_environment: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_runtime_adapter: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_outputs: Mapped[bool] = mapped_column(nullable=False, default=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ReproductionExecutionPlan(Base):
    __tablename__ = "workspace_reproduction_execution_plans"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    execution_plan_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    reproduction_plan_id: Mapped[str] = mapped_column(String(96), nullable=False)
    original_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    reproduction_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    target_product: Mapped[str] = mapped_column(String(64), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    input_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    environment_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    runtime_adapter_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    environment_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    runtime_adapter_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    job_request_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    readiness_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    policy_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class RuntimeHandoffReceipt(Base):
    __tablename__ = "workspace_runtime_handoff_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    execution_plan_id: Mapped[str] = mapped_column(String(96), nullable=False)
    reproduction_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    target_product: Mapped[str] = mapped_column(String(64), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    route_transport: Mapped[str] = mapped_column(String(64), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class ExecutionPolicyHead(Base):
    __tablename__ = "workspace_execution_policy_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    allowed_targets_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_operations_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    minimum_adapter_trust: Mapped[str] = mapped_column(String(32), nullable=False, default="bounded")
    resource_limits_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sandbox_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ExecutionPolicyRevision(Base):
    __tablename__ = "workspace_execution_policy_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    allowed_targets_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_operations_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    minimum_adapter_trust: Mapped[str] = mapped_column(String(32), nullable=False, default="bounded")
    resource_limits_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sandbox_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ExecutionPolicyDecision(Base):
    __tablename__ = "workspace_execution_policy_decisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    execution_plan_id: Mapped[str] = mapped_column(String(96), nullable=False)
    policy_id: Mapped[str] = mapped_column(String(160), nullable=False)
    policy_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    eligible: Mapped[bool] = mapped_column(nullable=False, default=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False, default="blocked")
    resource_budget_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sandbox_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    checks_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

