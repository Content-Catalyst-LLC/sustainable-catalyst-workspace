"""SC-NB-01: the frontend notebook schema and the backend executable-cell validator agree.

One fixture corpus runs through the JSON Schemas (sc-workspace-notebook-v3 + cell-v1, via jsonschema)
and through backend/app/notebook_cells.py. Structural verdicts must match exactly; graph rules
(dangling or undeclared dependencies, duplicates) are backend-only and are asserted separately.
"""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
_spec = importlib.util.spec_from_file_location("notebook_cells", ROOT / "backend" / "app" / "notebook_cells.py")
cells_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cells_mod)

FIT = {"id": "fit", "type": "code", "language": "r", "source": "fit <- lm(y ~ x, data = rows)",
       "execution": {"schema": "sc-workspace-notebook-cell-execution/1.0", "operation": "workspace.polyglot.r.linear-model",
                     "modelRef": {"modelId": "m-r"}, "maxAttempts": 1,
                     "payload": {"datasetInput": {"datasetId": "ds", "datasetRevision": 1, "format": "json-records",
                                                  "artifactSha256": "a" * 64}, "outcome": "y", "predictors": ["x"]}}}
REPLAY = {"id": "replay", "type": "code", "language": "julia", "source": "solve(Q, c)",
          "execution": {"operation": "workspace.polyglot.julia.quadratic-optimize", "dependsOnCellIds": ["fit"],
                        "payload": {"datasetInput": {"datasetId": "ds", "datasetRevision": 1,
                                                     "transform": {"kind": "least-squares-normal-equations", "outcome": "y", "predictors": ["x"]}}}}}
SCENARIO = {"id": "scenario", "type": "decision-studio", "source": "", "title": "Scenarios",
            "execution": {"operation": "workspace.decision.minimax-regret", "dependsOnCellIds": ["fit", "replay"],
                          "datasetRefs": [{"datasetId": "ds", "revision": 1}],
                          "payload": {"upstreamInput": {"cells": [{"cellId": "fit", "role": "primary"}, {"cellId": "replay", "role": "cross-check"}],
                                                        "transform": {"kind": "linear-scenario-scores", "rates": [10, 25, 40]}}}}}
EDITOR = {"schema": "sc-workspace-notebook/3.0", "id": "nb-1", "title": "Synthetic", "description": "",
          "sections": [{"id": "s1", "title": "Notes", "blocks": [], "createdAt": "2026-11-10T00:00:00.000Z",
                        "updatedAt": "2026-11-10T00:00:00.000Z"}],
          "activeSectionId": "s1", "createdAt": "2026-11-10T00:00:00.000Z", "updatedAt": "2026-11-10T00:00:00.000Z"}


def with_cells(*cells, base=None):
    doc = copy.deepcopy(base or {"schema": "sc-workspace-notebook/3.0", "title": "Executable"})
    doc["cells"] = copy.deepcopy(list(cells))
    return doc


def mutate(cell, path, value):
    c = copy.deepcopy(cell)
    node = c
    for key in path[:-1]:
        node = node[key]
    if value is DELETE:
        del node[path[-1]]
    else:
        node[path[-1]] = value
    return c


DELETE = object()

VALID = {
    "editor-notebook-without-cells": EDITOR,
    "editor-notebook-with-cells": with_cells(FIT, REPLAY, SCENARIO, base=EDITOR),
    "executable-notebook": with_cells({"id": "q", "type": "markdown", "source": "Question"}, FIT, REPLAY, SCENARIO),
    "legacy-id-only-cells": with_cells({"id": "c1"}, {"id": "c2"}),
    "scenario-reference-cell": with_cells({"id": "s", "type": "decision-studio", "source": "",
                                           "scenarioRef": {"authority": "decision-studio", "scenarioSetId": "synthetic"}}),
    "client-fingerprint-hint": with_cells(dict(FIT, fingerprint="f" * 64)),
}
INVALID = {
    "unknown-cell-property": with_cells(dict(FIT, outputs=[1])),
    "unknown-cell-type": with_cells(dict(FIT, type="raw")),
    "unknown-language": with_cells(dict(FIT, language="cobol")),
    "code-cell-without-language": with_cells(mutate(FIT, ["language"], DELETE)),
    "bad-cell-id": with_cells(dict(FIT, id="-fit")),
    "execution-without-operation": with_cells(mutate(FIT, ["execution", "operation"], DELETE)),
    "unknown-execution-property": with_cells(mutate(FIT, ["execution", "runtimeUrl"], "http://x")),
    "unknown-target-product": with_cells(mutate(FIT, ["execution", "targetProduct"], "browser")),
    "max-attempts-out-of-range": with_cells(mutate(FIT, ["execution", "maxAttempts"], 9)),
    "dataset-ref-without-revision": with_cells(mutate(SCENARIO, ["execution", "datasetRefs"], [{"datasetId": "ds"}])),
    "dataset-input-revision-zero": with_cells(mutate(FIT, ["execution", "payload", "datasetInput", "datasetRevision"], 0)),
    "dataset-input-bad-sha": with_cells(mutate(FIT, ["execution", "payload", "datasetInput", "artifactSha256"], "XYZ")),
    "dataset-input-unknown-transform": with_cells(mutate(REPLAY, ["execution", "payload", "datasetInput", "transform"], {"kind": "eval"})),
    "upstream-unknown-transform": with_cells(mutate(SCENARIO, ["execution", "payload", "upstreamInput", "transform"], {"kind": "eval"})),
    "upstream-bad-role": with_cells(mutate(SCENARIO, ["execution", "payload", "upstreamInput", "cells"], [{"cellId": "fit", "role": "owner"}])),
    "upstream-empty": with_cells(mutate(SCENARIO, ["execution", "payload", "upstreamInput", "cells"], [])),
    "dataset-and-upstream-input": with_cells(mutate(SCENARIO, ["execution", "payload", "datasetInput"], {"datasetId": "ds", "datasetRevision": 1})),
    "duplicate-dependency": with_cells(mutate(REPLAY, ["execution", "dependsOnCellIds"], ["fit", "fit"])),
    "wrong-notebook-schema": dict(with_cells(FIT), schema="sc-workspace-notebook/2.0"),
}
GRAPH_INVALID = {
    "duplicate-cell-id": with_cells(FIT, FIT),
    "dangling-dependency": with_cells(REPLAY),
    "self-dependency": with_cells(mutate(FIT, ["execution", "dependsOnCellIds"], ["fit"])),
    "undeclared-upstream": with_cells(FIT, REPLAY, mutate(SCENARIO, ["execution", "dependsOnCellIds"], ["fit"])),
}


def backend_accepts(doc):
    if doc.get("schema") != "sc-workspace-notebook/3.0":
        return False
    try:
        cells_mod.validate_cells(doc.get("cells"))
        return True
    except cells_mod.CellValidationError:
        return False


@pytest.fixture(scope="module")
def schema_validator():
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    resources = []
    for name in ("sc-workspace-notebook-v3", "sc-workspace-notebook-block-v3", "sc-workspace-notebook-cell-v1"):
        doc = json.loads((SCHEMAS / f"{name}.schema.json").read_text())
        resources.append((doc["$id"], referencing.Resource.from_contents(doc)))
    registry = referencing.Registry().with_resources(resources)
    root = json.loads((SCHEMAS / "sc-workspace-notebook-v3.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(root)
    return jsonschema.Draft202012Validator(root, registry=registry)


@pytest.mark.parametrize("name", sorted(VALID))
def test_valid_documents_pass_both(schema_validator, name):
    doc = VALID[name]
    assert not list(schema_validator.iter_errors(doc)), name
    assert backend_accepts(doc), name


@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid_documents_fail_both(schema_validator, name):
    doc = INVALID[name]
    assert list(schema_validator.iter_errors(doc)), f"schema accepted {name}"
    assert not backend_accepts(doc), f"backend accepted {name}"


@pytest.mark.parametrize("name", sorted(GRAPH_INVALID))
def test_graph_rules_are_backend_only(schema_validator, name):
    doc = GRAPH_INVALID[name]
    assert not backend_accepts(doc), name
    if name != "duplicate-cell-id":
        assert not list(schema_validator.iter_errors(doc)), "graph rule unexpectedly expressible in schema"


def test_cell_schema_enums_match_backend_constants():
    cell = json.loads((SCHEMAS / "sc-workspace-notebook-cell-v1.schema.json").read_text())
    assert set(cell["properties"]["type"]["enum"]) == cells_mod.CELL_TYPES
    assert set(cell["properties"]["language"]["enum"]) == cells_mod.LANGUAGES
    assert set(cell["properties"]) == cells_mod.CELL_KEYS
    ex = cell["$defs"]["execution"]
    assert set(ex["properties"]) == cells_mod.EXECUTION_KEYS
    assert set(ex["properties"]["targetProduct"]["enum"]) == cells_mod.TARGETS
    assert ex["properties"]["schema"]["const"] == cells_mod.EXECUTION_SCHEMA
    nb = json.loads((SCHEMAS / "sc-workspace-notebook-v3.schema.json").read_text())
    assert nb["properties"]["cells"]["maxItems"] == cells_mod.MAX_CELLS
