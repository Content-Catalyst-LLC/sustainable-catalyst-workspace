import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.compute import (
    OPERATION_MAP,
    _describe,
    _integrate_series,
    _linear_algebra,
    _optimize_quadratic,
    _roots_polynomial,
    _symbolic,
    _transform,
    compute_catalog,
)

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_is_bounded_and_has_four_scientific_engines():
    items = compute_catalog()
    assert len(items) == 7
    assert set(OPERATION_MAP) == {item["operation"] for item in items}
    assert {item["engine"] for item in items} == {"numpy", "pandas", "scipy", "sympy"}
    assert all(item["arbitraryCode"] is False for item in items)


def test_describe_table_returns_numeric_summary():
    result = _describe({"rows": [{"x": 1, "group": "a"}, {"x": 3, "group": "b"}, {"x": None, "group": "b"}]}, None)
    assert result["rowCount"] == 3
    assert result["columns"]["x"]["missing"] == 1
    assert result["columns"]["x"]["numeric"]["mean"] == 2.0


def test_transform_is_declarative_not_code_execution():
    result = _transform({
        "rows": [{"group": "a", "x": 1}, {"group": "a", "x": 3}, {"group": "b", "x": 10}],
        "filters": [{"column": "x", "op": "gte", "value": 2}],
        "groupBy": ["group"],
        "aggregations": {"x": "mean"},
        "sort": [{"column": "x", "direction": "desc"}],
    }, None)
    assert result["rowCount"] == 2
    assert result["rows"][0]["group"] == "b"
    assert result["rows"][0]["x"] == 10.0


def test_linear_algebra_solve_and_determinant():
    solved = _linear_algebra({"action": "solve", "a": [[2, 0], [0, 4]], "b": [6, 8]}, None)
    assert solved["solution"] == [3.0, 2.0]
    det = _linear_algebra({"action": "determinant", "a": [[2, 0], [0, 4]]}, None)
    assert det["determinant"] == pytest.approx(8.0)


def test_symbolic_operations_use_declared_identifier_allowlist():
    result = _symbolic({"action": "differentiate", "expression": "sin(x) + x^2", "variables": ["x"], "variable": "x"}, None)
    assert "2*x" in result["result"] and "cos(x)" in result["result"]
    with pytest.raises(HTTPException):
        _symbolic({"action": "simplify", "expression": "__import__(os)", "variables": ["x"]}, None)


def test_sampled_series_integration():
    result = _integrate_series({"x": [0, 1, 2], "y": [0, 1, 2], "method": "trapezoid"}, None)
    assert result["integral"] == pytest.approx(2.0)


def test_quadratic_optimization():
    result = _optimize_quadratic({"q": [[2.0]], "c": [-4.0], "x0": [0.0], "maxIterations": 100}, None)
    assert result["success"] is True
    assert result["solution"][0] == pytest.approx(2.0, abs=1e-5)


def test_polynomial_roots_support_complex_results():
    result = _roots_polynomial({"coefficients": [1, 0, 1]}, None)
    assert result["degree"] == 2
    assert sorted(round(abs(x["imag"]), 6) for x in result["roots"]) == [1.0, 1.0]


def test_compute_schema_and_migration_contract():
    schema = json.loads((ROOT / "schemas/sc-workspace-scientific-compute-v1.schema.json").read_text())
    assert schema["properties"]["version"]["const"] == "2.11.0"
    assert schema["properties"]["arbitraryCodeExecution"]["const"] is False
    migration = (ROOT / "backend/migrations/011_python_scientific_compute_runtime.sql").read_text()
    assert "workspace_compute_execution_receipts" in migration
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in migration


def test_worker_route_integrates_compute_without_shell_execution():
    routing = (ROOT / "backend/app/routing.py").read_text()
    compute = (ROOT / "backend/app/compute.py").read_text()
    compose = (ROOT / "backend/docker-compose.example.yml").read_text()
    assert 'row.operation.startswith("workspace.compute.")' in routing
    assert "subprocess" not in compute
    assert "os.system" not in compute
    assert "eval(" not in compute
    assert "cap_drop:" in compose and "no-new-privileges:true" in compose
    assert "read_only: true" in compose


def test_release_identity_and_lineage_are_v2110_over_v2100():
    plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
    dep = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php").read_text()
    cert = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php").read_text()
    backend = (ROOT / "backend/app/config.py").read_text()
    workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    assert "Version: 2.11.0" in plugin
    assert "define('SC_WORKSPACE_VERSION', '2.11.0')" in plugin
    assert 'service_version: str = "2.11.0"' in backend
    assert "const PREVIOUS_RELEASE = '2.10.0';" in dep
    assert "const ROLLBACK_RELEASE = '2.10.0';" in dep
    assert "const PREVIOUS_RELEASE = '2.10.0';" in cert
    assert "workspace-v2.11.0.js" in workspace and "workspace-v2.11.0.css" in workspace
    assert "python-scientific-compute-runtime-execution-engine" in workspace
