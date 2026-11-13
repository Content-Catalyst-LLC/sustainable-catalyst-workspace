"""SC-NB-01 strict validation of executable notebook cells (``sc-workspace-notebook/3.0`` ``cells[]``).

Mirrors ``schemas/sc-workspace-notebook-cell-v1.schema.json`` rule for rule (the parity test runs both
over one fixture corpus), and adds the graph rules a JSON Schema cannot express. Pure Python, no
dependencies, so the backend image needs no schema engine. Sections and blocks remain frontend-owned.
"""
from __future__ import annotations

import re
from typing import Any

CELL_TYPES = {"markdown", "code", "decision-studio"}
LANGUAGES = {"r", "julia", "python", "rust", "sql"}
TARGETS = {"workspace", "core", "lab", "workbench", "decision-studio", "library", "site-intelligence"}
EXECUTION_SCHEMA = "sc-workspace-notebook-cell-execution/1.0"
MAX_CELLS = 200
CELL_KEYS = {"id", "type", "kind", "title", "language", "source", "fingerprint", "scenarioRef", "execution"}
EXECUTION_KEYS = {"schema", "targetProduct", "operation", "dependsOnCellIds", "inputArtifactIds", "datasetRefs", "modelRef",
                  "priority", "maxAttempts", "executionPolicy", "resourceBudget", "sandbox", "payload"}
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")
SHA = re.compile(r"^[0-9a-f]{64}$")


class CellValidationError(ValueError):
    def __init__(self, path: str, message: str):
        super().__init__(f"{path}: {message}")
        self.path, self.message = path, message


def _str(v: Any, path: str, max_len: int, min_len: int = 0) -> None:
    if not isinstance(v, str) or not min_len <= len(v) <= max_len:
        raise CellValidationError(path, f"must be a string of {min_len}..{max_len} characters")


def _int(v: Any, path: str, lo: int, hi: int | None = None) -> None:
    if not isinstance(v, int) or isinstance(v, bool) or v < lo or (hi is not None and v > hi):
        raise CellValidationError(path, f"must be an integer >= {lo}" + (f" and <= {hi}" if hi is not None else ""))


def _obj(v: Any, path: str, allowed: set[str] | None = None, required: tuple[str, ...] = ()) -> dict:
    if not isinstance(v, dict):
        raise CellValidationError(path, "must be an object")
    if allowed is not None:
        extra = sorted(set(v) - allowed)
        if extra:
            raise CellValidationError(path, f"unknown properties {extra}")
    for key in required:
        if key not in v:
            raise CellValidationError(f"{path}.{key}", "is required")
    return v


def _list(v: Any, path: str, max_items: int, min_items: int = 0, unique: bool = False) -> list:
    if not isinstance(v, list) or not min_items <= len(v) <= max_items:
        raise CellValidationError(path, f"must be an array of {min_items}..{max_items} items")
    if unique and len({repr(x) for x in v}) != len(v):
        raise CellValidationError(path, "items must be unique")
    return v


def _transform(v: Any, path: str, kinds: set[str]) -> None:
    _obj(v, path, required=("kind",))
    if v["kind"] not in kinds:
        raise CellValidationError(f"{path}.kind", f"must be one of {sorted(kinds)}")


def _payload(p: Any, path: str) -> None:
    _obj(p, path)
    if "datasetInput" in p and "upstreamInput" in p:
        raise CellValidationError(path, "datasetInput and upstreamInput are mutually exclusive")
    if "datasetInput" in p:
        d = _obj(p["datasetInput"], f"{path}.datasetInput",
                 {"datasetId", "datasetRevision", "format", "artifactSha256", "transform"}, ("datasetId", "datasetRevision"))
        _str(d["datasetId"], f"{path}.datasetInput.datasetId", 160, 1)
        _int(d["datasetRevision"], f"{path}.datasetInput.datasetRevision", 1)
        if "format" in d and d["format"] not in ("json-records", "csv"):
            raise CellValidationError(f"{path}.datasetInput.format", "must be json-records or csv")
        if "artifactSha256" in d and not (isinstance(d["artifactSha256"], str) and SHA.match(d["artifactSha256"])):
            raise CellValidationError(f"{path}.datasetInput.artifactSha256", "must be a lowercase SHA-256 hex digest")
        if "transform" in d:
            _transform(d["transform"], f"{path}.datasetInput.transform", {"least-squares-normal-equations"})
    if "upstreamInput" in p:
        u = _obj(p["upstreamInput"], f"{path}.upstreamInput", {"cells", "transform"}, ("cells", "transform"))
        for i, ref in enumerate(_list(u["cells"], f"{path}.upstreamInput.cells", 8, 1)):
            rp = f"{path}.upstreamInput.cells[{i}]"
            _obj(ref, rp, {"cellId", "role"}, ("cellId",))
            _str(ref["cellId"], f"{rp}.cellId", 160, 1)
            if "role" in ref and ref["role"] not in ("primary", "cross-check"):
                raise CellValidationError(f"{rp}.role", "must be primary or cross-check")
        _transform(u["transform"], f"{path}.upstreamInput.transform", {"linear-scenario-scores"})


def _execution(ex: Any, path: str) -> None:
    _obj(ex, path, EXECUTION_KEYS, ("operation",))
    if "schema" in ex and ex["schema"] != EXECUTION_SCHEMA:
        raise CellValidationError(f"{path}.schema", f"must be {EXECUTION_SCHEMA}")
    if "targetProduct" in ex and ex["targetProduct"] not in TARGETS:
        raise CellValidationError(f"{path}.targetProduct", f"must be one of {sorted(TARGETS)}")
    _str(ex["operation"], f"{path}.operation", 160, 1)
    for key in ("dependsOnCellIds", "inputArtifactIds"):
        if key in ex:
            for i, x in enumerate(_list(ex[key], f"{path}.{key}", 64, unique=True)):
                _str(x, f"{path}.{key}[{i}]", 160, 1)
    if "datasetRefs" in ex:
        for i, ref in enumerate(_list(ex["datasetRefs"], f"{path}.datasetRefs", 64)):
            _obj(ref, f"{path}.datasetRefs[{i}]", {"datasetId", "revision"}, ("datasetId", "revision"))
            _str(ref["datasetId"], f"{path}.datasetRefs[{i}].datasetId", 160, 1)
            _int(ref["revision"], f"{path}.datasetRefs[{i}].revision", 1)
    if "modelRef" in ex:
        m = _obj(ex["modelRef"], f"{path}.modelRef", {"modelId", "revision"}, ("modelId",))
        _str(m["modelId"], f"{path}.modelRef.modelId", 160, 1)
        if "revision" in m:
            _int(m["revision"], f"{path}.modelRef.revision", 1)
    if "priority" in ex:
        _int(ex["priority"], f"{path}.priority", 0, 9)
    if "maxAttempts" in ex:
        _int(ex["maxAttempts"], f"{path}.maxAttempts", 1, 5)
    for key in ("executionPolicy", "resourceBudget", "sandbox"):
        if key in ex:
            _obj(ex[key], f"{path}.{key}")
    if "payload" in ex:
        _payload(ex["payload"], f"{path}.payload")


def validate_cell(cell: Any, path: str = "cell") -> None:
    """Structural rules of the cell schema."""
    _obj(cell, path, CELL_KEYS, ("id",))
    _str(cell["id"], f"{path}.id", 160, 1)
    if not ID.match(cell["id"]):
        raise CellValidationError(f"{path}.id", "must start with a letter or digit and use only A-Z a-z 0-9 _ . : -")
    if "type" in cell and cell["type"] not in CELL_TYPES:
        raise CellValidationError(f"{path}.type", f"must be one of {sorted(CELL_TYPES)}")
    for key, limit in (("kind", 64), ("title", 240), ("source", 100000), ("fingerprint", 128)):
        if key in cell:
            _str(cell[key], f"{path}.{key}", limit)
    if "language" in cell and cell["language"] not in LANGUAGES:
        raise CellValidationError(f"{path}.language", f"must be one of {sorted(LANGUAGES)}")
    if cell.get("type") == "code":
        for key in ("language", "source"):
            if key not in cell:
                raise CellValidationError(f"{path}.{key}", "is required for code cells")
    if "scenarioRef" in cell:
        s = _obj(cell["scenarioRef"], f"{path}.scenarioRef", {"authority", "scenarioSetId", "revision"}, ("authority",))
        if s["authority"] not in ("decision-studio", "workspace"):
            raise CellValidationError(f"{path}.scenarioRef.authority", "must be decision-studio or workspace")
        if "scenarioSetId" in s:
            _str(s["scenarioSetId"], f"{path}.scenarioRef.scenarioSetId", 160)
        if "revision" in s:
            _int(s["revision"], f"{path}.scenarioRef.revision", 1)
    if "execution" in cell:
        _execution(cell["execution"], f"{path}.execution")


def validate_cells(cells: Any) -> int:
    """Structural and graph rules for a notebook's cells[]; returns the cell count."""
    if cells is None:
        return 0
    _list(cells, "notebook.cells", MAX_CELLS)
    ids: set[str] = set()
    for i, cell in enumerate(cells):
        validate_cell(cell, f"notebook.cells[{i}]")
        if cell["id"] in ids:
            raise CellValidationError(f"notebook.cells[{i}].id", f"duplicate cell id {cell['id']!r}")
        ids.add(cell["id"])
    executable = {c["id"] for c in cells if "execution" in c}
    for i, cell in enumerate(cells):
        ex = cell.get("execution") or {}
        deps = ex.get("dependsOnCellIds") or []
        missing = sorted(set(deps) - executable)
        if missing:
            raise CellValidationError(f"notebook.cells[{i}].execution.dependsOnCellIds", f"unknown executable cells {missing}")
        if cell["id"] in deps:
            raise CellValidationError(f"notebook.cells[{i}].execution.dependsOnCellIds", "a cell cannot depend on itself")
        up = ((ex.get("payload") or {}).get("upstreamInput") or {}).get("cells") or []
        undeclared = sorted({r["cellId"] for r in up} - set(deps))
        if undeclared:
            raise CellValidationError(f"notebook.cells[{i}].execution.payload.upstreamInput", f"cells {undeclared} must be declared in dependsOnCellIds")
    return len(cells)
