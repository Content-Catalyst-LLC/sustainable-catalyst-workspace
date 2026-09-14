from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectStoreRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    schema_: Literal["sc-workspace-cloud-backup/1.0", "sc-workspace-sync-push/1.0"] = Field(alias="schema")
    sourceProjectId: str = Field(min_length=1, max_length=160)
    projectTitle: str | None = None
    clientUpdatedAt: str | None = None
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)
    project: dict[str, Any]


class NotebookStoreRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    schema_: Literal["sc-workspace-notebook-cloud-backup/1.0", "sc-workspace-notebook-sync-push/1.0"] = Field(alias="schema")
    sourceNotebookId: str = Field(min_length=1, max_length=160)
    sourceProjectId: str | None = Field(default=None, max_length=160)
    notebookTitle: str | None = None
    clientUpdatedAt: str | None = None
    notebookFingerprint: str | None = None
    expectedRevision: int | None = Field(default=None, ge=0)
    operationId: str | None = Field(default=None, max_length=160)
    notebook: dict[str, Any]


class LegacyMigrationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(min_length=1, max_length=160)
    revision: int = Field(default=1, ge=1)
    storageMode: str = Field(default="manual-backup", max_length=32)
    backedUpAt: str | None = None
    fingerprint: str | None = Field(default=None, max_length=128)
    payload: dict[str, Any]


class LegacyMigrationRequest(BaseModel):
    schema_: Literal["sc-workspace-legacy-user-meta-migration/1.0"] = Field(alias="schema")
    source: Literal["wordpress-user-meta"] = "wordpress-user-meta"
    dryRun: bool = True
    projects: list[LegacyMigrationRecord] = Field(default_factory=list)
    notebooks: list[LegacyMigrationRecord] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ArtifactStoreRequest(BaseModel):
    schema_: Literal["sc-workspace-artifact-store/1.0"] = Field(alias="schema")
    artifactId: str = Field(min_length=1, max_length=160)
    projectId: str | None = Field(default=None, max_length=160)
    filename: str = Field(default="artifact", max_length=1024)
    mediaType: str = Field(default="application/octet-stream", max_length=255)
    contentBase64: str = Field(min_length=1)
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class RecoverySnapshotRequest(BaseModel):
    schema_: Literal["sc-workspace-recovery-snapshot-request/1.0"] = Field(alias="schema")
    reason: str = Field(default="manual", max_length=160)

    model_config = ConfigDict(populate_by_name=True)
