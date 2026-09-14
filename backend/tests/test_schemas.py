import pytest
from pydantic import ValidationError

from app.schemas import ArtifactStoreRequest, LegacyMigrationRequest, NotebookStoreRequest, ProjectStoreRequest, RecoverySnapshotRequest


def test_project_sync_schema_accepts_existing_contract():
    item = ProjectStoreRequest(schema="sc-workspace-sync-push/1.0", sourceProjectId="p1", expectedRevision=0, operationId="op1", project={"schema": "sc-workspace-project/20.0"})
    assert item.sourceProjectId == "p1"


def test_project_store_rejects_unknown_transport_schema():
    with pytest.raises(ValidationError):
        ProjectStoreRequest(schema="unknown", sourceProjectId="p1", project={"schema": "sc-workspace-project/20.0"})


def test_notebook_store_accepts_existing_contract():
    item = NotebookStoreRequest(schema="sc-workspace-notebook-cloud-backup/1.0", sourceNotebookId="n1", notebook={"schema": "sc-workspace-notebook/3.0"})
    assert item.sourceNotebookId == "n1"


def test_legacy_migration_schema_accepts_plan_payload():
    item = LegacyMigrationRequest(schema="sc-workspace-legacy-user-meta-migration/1.0", projects=[], notebooks=[])
    assert item.dryRun is True


def test_artifact_schema_accepts_revision_precondition():
    item = ArtifactStoreRequest(schema="sc-workspace-artifact-store/1.0", artifactId="a1", contentBase64="YQ==", expectedRevision=0)
    assert item.artifactId == "a1"


def test_recovery_snapshot_schema_is_explicit():
    item = RecoverySnapshotRequest(schema="sc-workspace-recovery-snapshot-request/1.0", reason="before-migration")
    assert item.reason == "before-migration"
