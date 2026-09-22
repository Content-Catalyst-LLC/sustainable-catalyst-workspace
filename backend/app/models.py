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


class DomainMutationReceipt(Base):
    __tablename__ = "workspace_domain_mutation_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    object_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    object_id: Mapped[str] = mapped_column(String(160), nullable=False)
    command: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="applied")
    from_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    to_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    validation_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    policy_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    provenance_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class LocalFirstSyncReceipt(Base):
    __tablename__ = "workspace_local_first_sync_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    envelope_id: Mapped[str] = mapped_column(String(96), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False)
    device_id: Mapped[str] = mapped_column(String(160), nullable=False)
    object_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    object_id: Mapped[str] = mapped_column(String(160), nullable=False)
    base_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    server_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    envelope_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AuthorizationDecisionReceipt(Base):
    __tablename__ = "workspace_authorization_decision_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    principal_id: Mapped[str] = mapped_column(String(192), nullable=False)
    principal_type: Mapped[str] = mapped_column(String(64), nullable=False)
    service_principal: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(96), nullable=False)
    resource_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    effect: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[str] = mapped_column(String(96), nullable=False)
    policy_id: Mapped[str] = mapped_column(String(96), nullable=False)
    policy_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class CrossProductResearchHandoff(Base):
    __tablename__ = "workspace_cross_product_research_handoffs"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    handoff_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    source_product: Mapped[str] = mapped_column(String(96), nullable=False)
    destination_product: Mapped[str] = mapped_column(String(96), nullable=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="prepared")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    package_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    object_refs_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    destination_result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CrossProductResearchHandoffReceipt(Base):
    __tablename__ = "workspace_cross_product_research_handoff_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    handoff_id: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    source_product: Mapped[str] = mapped_column(String(96), nullable=False)
    destination_product: Mapped[str] = mapped_column(String(96), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    package_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class CommandReceipt(Base):
    __tablename__ = "workspace_command_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    command_id: Mapped[str] = mapped_column(String(96), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    command: Mapped[str] = mapped_column(String(96), nullable=False)
    target_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    target_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="applied")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    linked_mutation_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)



class NotebookExecutionPlan(Base):
    __tablename__ = "workspace_notebook_execution_plans"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    notebook_id: Mapped[str] = mapped_column(String(160), nullable=False)
    notebook_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    notebook_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    dependency_graph_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    artifact_bindings_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    steps_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    job_ids_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class NotebookOrchestrationReceipt(Base):
    __tablename__ = "workspace_notebook_orchestration_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ScientificStudyPackage(Base):
    __tablename__ = "workspace_scientific_study_packages"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    package_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    project_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manifest_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    bundle_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    bundle_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    bundle_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    component_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    embedded_artifact_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    closure_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    manifest_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ScientificStudyPackageReceipt(Base):
    __tablename__ = "workspace_scientific_study_package_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    package_id: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    manifest_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    bundle_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class VisualizationSpecHead(Base):
    __tablename__ = "workspace_visualization_specs"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    visualization_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False, default="Visualization")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    spec_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    scene_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="single")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spec_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class VisualizationSpecRevision(Base):
    __tablename__ = "workspace_visualization_spec_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    visualization_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False, default="Visualization")
    spec_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    scene_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="single")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    spec_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class VisualizationSpecReceipt(Base):
    __tablename__ = "workspace_visualization_spec_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    visualization_id: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="applied")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spec_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
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


class ComputeExecutionReceipt(Base):
    __tablename__ = "workspace_compute_execution_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    engine: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    result_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    wall_seconds: Mapped[float] = mapped_column(nullable=False, default=0.0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class PolyglotExecutionReceipt(Base):
    __tablename__ = "workspace_polyglot_execution_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    result_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    transport: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="succeeded")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class StatisticalModelReceipt(Base):
    __tablename__ = "workspace_statistical_model_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="r")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    model_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    outcome: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    predictors_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class NumericalSimulationReceipt(Base):
    __tablename__ = "workspace_numerical_simulation_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="julia")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    model_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    solver: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class PredictiveModelReceipt(Base):
    __tablename__ = "workspace_predictive_model_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    model_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    task: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    target: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    features_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    preprocessing_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hyperparameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    dataset_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    train_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    test_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    model_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    model_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ModelEvaluationReceipt(Base):
    __tablename__ = "workspace_model_evaluation_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    predictive_model_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    evaluation_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    fold_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dataset_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ForecastReceipt(Base):
    __tablename__ = "workspace_forecast_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    model_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    value_column: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    time_column: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    frequency: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    horizon: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    seasonal_period: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dataset_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    intervals_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class ForecastEvaluationReceipt(Base):
    __tablename__ = "workspace_forecast_evaluation_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    forecast_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    evaluation_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    train_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    test_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dataset_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ProbabilisticInferenceReceipt(Base):
    __tablename__ = "workspace_probabilistic_inference_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    inference_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    posterior_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    interval_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class UncertaintyAnalysisReceipt(Base):
    __tablename__ = "workspace_uncertainty_analysis_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    interval_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    summary_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sensitivity_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class OptimizationReceipt(Base):
    __tablename__ = "workspace_optimization_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    optimization_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    objective_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    direction: Mapped[str] = mapped_column(String(16), nullable=False, default="minimize")
    best_value: Mapped[float] = mapped_column(nullable=False, default=0.0)
    best_parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    evaluation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    iteration_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    converged: Mapped[bool] = mapped_column(nullable=False, default=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class DecisionOptimizationReceipt(Base):
    __tablename__ = "workspace_decision_optimization_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    selected_alternative: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scenario_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    criterion: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    summary_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class ReliabilityAnalysisReceipt(Base):
    __tablename__ = "workspace_reliability_analysis_receipts"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    polyglot_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    runtime: Mapped[str] = mapped_column(String(96), nullable=False)
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    model_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    horizon: Mapped[float] = mapped_column(nullable=False, default=0.0)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False)
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class InterchangeReceipt(Base):
    __tablename__ = "workspace_interchange_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    operation: Mapped[str] = mapped_column(String(160), nullable=False)
    source_format: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    result_format: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    source_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    schema_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class CrossRuntimeVerificationReceipt(Base):
    __tablename__ = "workspace_cross_runtime_verification_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    original_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    reproduction_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    source_runtime: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    target_runtime: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    comparison_mode: Mapped[str] = mapped_column(String(64), nullable=False, default="auto")
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    exact_inputs: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_environment: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_runtime: Mapped[bool] = mapped_column(nullable=False, default=False)
    exact_outputs: Mapped[bool] = mapped_column(nullable=False, default=False)
    equivalent_outputs: Mapped[bool] = mapped_column(nullable=False, default=False)
    absolute_tolerance: Mapped[float] = mapped_column(nullable=False, default=1e-9)
    relative_tolerance: Mapped[float] = mapped_column(nullable=False, default=1e-7)
    compared_output_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result_artifact_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    result_sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


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



class RuntimeExecutionAttestation(Base):
    __tablename__ = "workspace_runtime_execution_attestations"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    attestation_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    handoff_receipt_id: Mapped[str] = mapped_column(String(96), nullable=False)
    execution_plan_id: Mapped[str] = mapped_column(String(96), nullable=False)
    reproduction_run_id: Mapped[str] = mapped_column(String(96), nullable=False)
    job_id: Mapped[str] = mapped_column(String(96), nullable=False)
    policy_decision_id: Mapped[str] = mapped_column(String(96), nullable=False)
    policy_decision_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    execution_succeeded: Mapped[bool] = mapped_column(nullable=False, default=False)
    budget_compliant: Mapped[bool] = mapped_column(nullable=False, default=False)
    sandbox_compliant: Mapped[bool] = mapped_column(nullable=False, default=False)
    observed_usage_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    budget_accounting_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sandbox_attestation_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    checks_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class RuntimeTrustPolicyHead(Base):
    __tablename__ = "workspace_runtime_trust_policy_heads"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    trust_policy_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last_operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    allowed_sources_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_attestors_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    accepted_classifications_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    require_budget_compliant: Mapped[bool] = mapped_column(nullable=False, default=True)
    require_sandbox_compliant: Mapped[bool] = mapped_column(nullable=False, default=True)
    require_evidence_digest: Mapped[bool] = mapped_column(nullable=False, default=True)
    allowed_sandbox_modes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    downstream_scopes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class RuntimeTrustPolicyRevision(Base):
    __tablename__ = "workspace_runtime_trust_policy_revisions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    trust_policy_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    allowed_sources_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_attestors_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    accepted_classifications_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    require_budget_compliant: Mapped[bool] = mapped_column(nullable=False, default=True)
    require_sandbox_compliant: Mapped[bool] = mapped_column(nullable=False, default=True)
    require_evidence_digest: Mapped[bool] = mapped_column(nullable=False, default=True)
    allowed_sandbox_modes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    downstream_scopes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class ComplianceWaiver(Base):
    __tablename__ = "workspace_compliance_waivers"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    waiver_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    attestation_id: Mapped[str] = mapped_column(String(96), nullable=False)
    downstream_scopes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    waived_checks_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    human_authorized: Mapped[bool] = mapped_column(nullable=False, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AttestationVerificationReceipt(Base):
    __tablename__ = "workspace_attestation_verification_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    verification_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    attestation_id: Mapped[str] = mapped_column(String(96), nullable=False)
    attestation_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    trust_policy_id: Mapped[str] = mapped_column(String(160), nullable=False)
    trust_policy_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    trust_policy_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    downstream_scope: Mapped[str] = mapped_column(String(64), nullable=False)
    waiver_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    eligible: Mapped[bool] = mapped_column(nullable=False, default=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False)
    checks_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


# v3.1.0 Platform Core v3 Unified Research Runtime Integration
class PlatformCoreResearchSessionBinding(Base):
    __tablename__ = "workspace_platform_core_research_sessions"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    core_session_id: Mapped[str] = mapped_column(String(96), nullable=False)
    core_session_key: Mapped[str] = mapped_column(String(180), nullable=False)
    core_contract: Mapped[str] = mapped_column(String(160), nullable=False)
    core_release: Mapped[str] = mapped_column(String(32), nullable=False, default="3.0.0")
    core_product_binding_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    project_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    project_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    core_session_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    last_error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class PlatformCoreRuntimeReceipt(Base):
    __tablename__ = "workspace_platform_core_runtime_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    core_session_id: Mapped[str] = mapped_column(String(96), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    binding_kind: Mapped[str] = mapped_column(String(48), nullable=False, default="")
    workspace_ref: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    core_ref: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="recorded")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


# v3.2.0 Unified Research Project Context
class UnifiedResearchContextSnapshot(Base):
    __tablename__ = "workspace_unified_research_context_snapshots"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    project_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    project_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    context_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    core_session_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    component_counts_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

# v3.3.0 Research Session & Object Binding Runtime
class ResearchSessionObjectBinding(Base):
    __tablename__ = "workspace_research_session_object_bindings"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    binding_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    core_session_id: Mapped[str] = mapped_column(String(96), nullable=False)
    binding_type: Mapped[str] = mapped_column(String(48), nullable=False)
    workspace_ref: Mapped[str] = mapped_column(String(1000), nullable=False)
    workspace_kind: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    workspace_object_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    workspace_revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    workspace_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    core_binding_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    role: Mapped[str] = mapped_column(String(120), nullable=False, default="context")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    response_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


# v3.4.0 Scientific Execution & Provenance Workspace
class ScientificExecutionProvenanceSnapshot(Base):
    __tablename__ = "workspace_scientific_execution_provenance_snapshots"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    run_id: Mapped[str] = mapped_column(String(96), nullable=False, default="")
    provenance_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    execution_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provenance_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


# v3.5.0 Catalyst Analytics R Runtime Adapter
class AnalyticalProviderReceipt(Base):
    __tablename__ = "workspace_analytical_provider_receipts"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    receipt_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    request_key: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_key: Mapped[str] = mapped_column(String(96), nullable=False)
    provider_version: Mapped[str] = mapped_column(String(32), nullable=False)
    core_contract: Mapped[str] = mapped_column(String(160), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(128), nullable=False)
    method_ref: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    external_execution_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    environment_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    result_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    request_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    error: Mapped[str] = mapped_column(Text, nullable=False, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

# v3.6.0 Platform Core Visual Analysis & Research Object Workspace
class VisualResearchWorkspaceSnapshot(Base):
    __tablename__ = "workspace_visual_research_workspace_snapshots"

    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    visualization_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    graph_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    visualization_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    binding_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

# v3.7.0 Claims, Evidence & Investigative Research Workspace
class InvestigationStatementHead(Base):
    __tablename__ = "workspace_investigation_statement_heads"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    statement_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    statement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    statement_text: Mapped[str] = mapped_column(Text, nullable=False)
    review_state: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    statement_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

class InvestigationStatementRevision(Base):
    __tablename__ = "workspace_investigation_statement_revisions"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    statement_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    statement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    statement_text: Mapped[str] = mapped_column(Text, nullable=False)
    review_state: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    statement_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class InvestigationEvidenceLink(Base):
    __tablename__ = "workspace_investigation_evidence_links"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    evidence_link_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    statement_id: Mapped[str] = mapped_column(String(160), nullable=False)
    evidence_ref: Mapped[str] = mapped_column(String(1200), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(String(120), nullable=False, default="external-reference")
    relation: Mapped[str] = mapped_column(String(48), nullable=False)
    source_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    locator: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    link_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class InvestigationStatementRelation(Base):
    __tablename__ = "workspace_investigation_statement_relations"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    relation_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    from_statement_id: Mapped[str] = mapped_column(String(160), nullable=False)
    to_statement_id: Mapped[str] = mapped_column(String(160), nullable=False)
    relation: Mapped[str] = mapped_column(String(48), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    relation_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

class InvestigativeResearchWorkspaceSnapshot(Base):
    __tablename__ = "workspace_investigative_research_workspace_snapshots"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    graph_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    workspace_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    statement_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_link_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    statement_relation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    context_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


# v3.8.0 Investigation Graph, Contradiction & Competing Hypothesis Workspace
class InvestigationHypothesisSet(Base):
    __tablename__ = "workspace_investigation_hypothesis_sets"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    hypothesis_set_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    question_statement_id: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    hypothesis_ids_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    set_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

class InvestigationGraphSnapshot(Base):
    __tablename__ = "workspace_investigation_graph_snapshots"
    user_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(160), nullable=False)
    graph_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    contradiction_cluster_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hypothesis_set_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    graph_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
