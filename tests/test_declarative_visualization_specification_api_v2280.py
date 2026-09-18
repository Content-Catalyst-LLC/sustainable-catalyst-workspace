import pytest
from fastapi import HTTPException

from app.schemas import VisualizationSpecStoreRequest
from app.visualization_specs import SPEC_SCHEMA, VIEW_TYPES, compile_spec, profile


def sample_spec():
    return {
        "schema": SPEC_SCHEMA,
        "title": "Uncertainty comparison",
        "sources": [
            {"id": "forecast", "kind": "inline", "rows": [
                {"x": 1, "mean": 10.0, "lower": 8.0, "upper": 12.0},
                {"x": 2, "mean": 11.0, "lower": 9.0, "upper": 13.5},
            ]}
        ],
        "scene": {
            "layout": "grid",
            "views": [
                {"id": "trend", "type": "uncertainty-band", "source": "forecast", "encoding": {"x": {"field": "x"}, "y": {"field": "mean"}, "lower": {"field": "lower"}, "upper": {"field": "upper"}}},
                {"id": "table", "type": "table", "source": "forecast", "encoding": {}},
            ],
        },
        "links": [{"sourceViewId": "trend", "targetViewId": "table", "mode": "filter", "field": "x"}],
    }


def test_profile_is_backend_authoritative_and_renderer_neutral():
    p = profile()
    assert p["backendAuthoritative"] is True
    assert p["rendererNeutral"] is True
    assert p["linkedViews"] is True
    assert p["browserDefinesAnalyticalMeaning"] is False
    assert p["arbitraryCodeExecution"] is False
    assert set(VIEW_TYPES) >= {"table", "line", "scatter", "distribution", "uncertainty-band", "network"}


def test_request_contract():
    request = VisualizationSpecStoreRequest.model_validate({
        "schema": "sc-workspace-visualization-spec-request/1.0",
        "projectId": "p1",
        "expectedRevision": 0,
        "spec": sample_spec(),
    })
    assert request.projectId == "p1"
    assert request.expectedRevision == 0


def test_compile_spec_is_deterministic_and_renderer_neutral():
    a = compile_spec(None, "u1", sample_spec())
    b = compile_spec(None, "u1", sample_spec())
    assert a == b
    assert len(a["specFingerprint"]) == 64
    assert a["rendererContract"]["rendererNeutral"] is True
    assert a["scene"]["layout"] == "grid"
    assert len(a["scene"]["views"]) == 2
    assert a["sources"][0]["rowCount"] == 2


def test_linked_view_contract_is_preserved():
    compiled = compile_spec(None, "u1", sample_spec())
    assert compiled["links"] == [{"sourceViewId": "trend", "targetViewId": "table", "mode": "filter", "field": "x"}]


def test_renderer_specific_or_executable_fields_are_rejected():
    spec = sample_spec()
    spec["scene"]["views"][0]["javascript"] = "alert(1)"
    with pytest.raises(HTTPException) as exc:
        compile_spec(None, "u1", spec)
    assert exc.value.status_code == 400


def test_missing_source_reference_is_rejected():
    spec = sample_spec()
    spec["scene"]["views"][0]["source"] = "missing"
    with pytest.raises(HTTPException) as exc:
        compile_spec(None, "u1", spec)
    assert exc.value.status_code == 400


def test_view_type_is_bounded():
    spec = sample_spec()
    spec["scene"]["views"][0]["type"] = "custom-javascript-chart"
    with pytest.raises(HTTPException) as exc:
        compile_spec(None, "u1", spec)
    assert exc.value.status_code == 400
