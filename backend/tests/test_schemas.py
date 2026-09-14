import pytest
from pydantic import ValidationError

from app.schemas import NotebookStoreRequest, ProjectStoreRequest


def test_project_sync_schema_accepts_existing_contract():
    item = ProjectStoreRequest(schema="sc-workspace-sync-push/1.0", sourceProjectId="p1", expectedRevision=0, operationId="op1", project={"schema": "sc-workspace-project/20.0"})
    assert item.sourceProjectId == "p1"


def test_project_store_rejects_unknown_transport_schema():
    with pytest.raises(ValidationError):
        ProjectStoreRequest(schema="unknown", sourceProjectId="p1", project={"schema": "sc-workspace-project/20.0"})


def test_notebook_store_accepts_existing_contract():
    item = NotebookStoreRequest(schema="sc-workspace-notebook-cloud-backup/1.0", sourceNotebookId="n1", notebook={"schema": "sc-workspace-notebook/3.0"})
    assert item.sourceNotebookId == "n1"
