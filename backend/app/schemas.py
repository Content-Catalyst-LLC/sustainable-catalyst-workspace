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
