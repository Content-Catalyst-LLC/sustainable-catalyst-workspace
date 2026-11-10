"""SC-NB-01 strict executable-cell validation on the backend store path.

The schema/validator parity corpus lives in the repository-level tests/test_notebook_cell_schema_parity.py;
this file checks that the backend enforces the rules where notebooks enter Workspace. Synthetic data only.
"""
from uuid import uuid4

import pytest

from test_input_integrity_sc_nb01 import PG, client, hdr  # noqa: F401 (client is a fixture)
from test_upstream_binding_sc_nb01 import chain_notebook

from app.domain_authority import DomainValidationError, validate_notebook_document  # noqa: E402
from app.notebook_cells import CellValidationError, validate_cells  # noqa: E402

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")


def test_executable_notebooks_and_legacy_cells_are_accepted():
    assert validate_cells(chain_notebook("ds-1")["cells"]) == 3
    assert validate_notebook_document({"schema": "sc-workspace-notebook/3.0", "title": "N", "cells": [{"id": "c1"}]})["accepted"]
    assert validate_cells(None) == 0


@pytest.mark.parametrize("mutate,path", [
    (lambda c: c[0].update(outputs=[]), "notebook.cells[0]"),
    (lambda c: c[0]["execution"].update(runtimeUrl="http://x"), "notebook.cells[0].execution"),
    (lambda c: c[2]["execution"]["payload"]["upstreamInput"]["transform"].update(kind="eval"),
     "notebook.cells[2].execution.payload.upstreamInput.transform.kind"),
    (lambda c: c[2]["execution"].update(dependsOnCellIds=["fit"]), "notebook.cells[2].execution.payload.upstreamInput"),
    (lambda c: c[1]["execution"].update(dependsOnCellIds=["missing"]), "notebook.cells[1].execution.dependsOnCellIds"),
    (lambda c: c.append(dict(c[0])), "notebook.cells[3].id"),
])
def test_invalid_cells_are_refused_with_a_path(mutate, path):
    cells = chain_notebook("ds-1")["cells"]
    mutate(cells)
    with pytest.raises(CellValidationError) as exc:
        validate_cells(cells)
    assert exc.value.path == path
    with pytest.raises(DomainValidationError) as exc:
        validate_notebook_document({"schema": "sc-workspace-notebook/3.0", "cells": cells})
    assert exc.value.code == "invalid-notebook-cell" and exc.value.path == path


@pg
def test_store_route_refuses_invalid_cells(client):
    doc = chain_notebook("ds-1")
    doc["cells"][0]["execution"]["targetProduct"] = "browser"
    r = client.post("/v1/notebooks", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-notebook-sync-push/1.0", "sourceNotebookId": f"bad-{uuid4().hex[:8]}",
        "sourceProjectId": "nb-proj", "expectedRevision": 0, "operationId": uuid4().hex, "notebook": doc})
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "invalid-notebook-cell" and body["path"] == "notebook.cells[0].execution.targetProduct"
