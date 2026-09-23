import pytest
from app.predictive_investigation_workspace import (
    PredictiveScenarioRequestModel, PredictiveModelBindingRequestModel, PredictiveForecastRequestModel,
    PredictiveForecastResultBindingRequestModel, PredictiveScenarioComparisonRequestModel, profile,
)
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app


def test_predictive_scenario_schema_and_explicit_assumptions():
    x=PredictiveScenarioRequestModel(schema="sc-workspace-predictive-scenario-request/1.0",projectId="p1",title="Baseline demand",scenarioKind="baseline",horizon="12 months",assumptions=[{"name":"growth","value":0.02}])
    assert x.scenarioKind=="baseline" and x.assumptions[0]["name"]=="growth"


def test_model_binding_requires_fingerprint_at_schema_boundary():
    with pytest.raises(Exception):
        PredictiveModelBindingRequestModel(schema="sc-workspace-predictive-model-binding-request/1.0",scenarioId="s1",modelFamily="time-series",modelRef="model://a",modelFingerprint="short")
    x=PredictiveModelBindingRequestModel(schema="sc-workspace-predictive-model-binding-request/1.0",scenarioId="s1",modelFamily="time-series",modelRef="model://a",modelFingerprint="12345678")
    assert x.modelFamily=="time-series"


def test_forecast_request_preserves_calibration_and_backtest_plans():
    x=PredictiveForecastRequestModel(schema="sc-workspace-predictive-forecast-request/1.0",scenarioId="s1",forecastKind="distribution",destinationProduct="catalyst-analytics-r",calibrationPlan={"metric":"brier"},backtestPlan={"window":"rolling"})
    assert x.calibrationPlan["metric"]=="brier" and x.backtestPlan["window"]=="rolling"


def test_forecast_result_is_explicitly_model_conditional():
    x=PredictiveForecastResultBindingRequestModel(schema="sc-workspace-predictive-forecast-result-binding-request/1.0",scenarioId="s1",resultKind="probability",resultRef="result://1",resultFingerprint="12345678")
    assert x.modelConditional is True


def test_scenario_comparison_requires_two_scenarios():
    with pytest.raises(Exception):
        PredictiveScenarioComparisonRequestModel(schema="sc-workspace-predictive-scenario-comparison-request/1.0",projectId="p1",title="bad",scenarioIds=["s1"])
    x=PredictiveScenarioComparisonRequestModel(schema="sc-workspace-predictive-scenario-comparison-request/1.0",projectId="p1",title="baseline vs stress",scenarioIds=["s1","s2"])
    assert len(x.scenarioIds)==2


def test_v319_typed_endpoints():
    expected={"predictiveInvestigationWorkspace","predictiveScenarioStore","predictiveScenarios","predictiveScenario","predictiveScenarioRevisions","predictiveModelBindingCreate","predictiveModelBindings","predictiveForecastRequestCreate","predictiveForecastRequests","predictiveForecastResultBindingCreate","predictiveForecastResultBindings","predictiveScenarioComparisonCreate","predictiveScenarioComparisons","predictiveInvestigationManifest","predictiveInvestigationGraph","predictiveInvestigationDiagnostics","predictiveInvestigationSnapshotCreate","predictiveInvestigationSnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=290


def test_openapi_predictive_routes_and_safety_profile():
    paths=app.openapi()["paths"]
    assert "/v1/predictive-investigation-workspace" in paths
    assert "/v1/predictive-investigation-workspace/forecast-requests" in paths
    assert "/v1/predictive-investigation-workspace/projects/{project_id}/diagnostics" in paths
    p=profile(); assert p["automaticForecastExecution"] is False; assert p["automaticScenarioSelection"] is False; assert p["automaticModelSelection"] is False; assert p["automaticProbabilityAsTruth"] is False; assert p["automaticForecastAsTruth"] is False; assert p["automaticTruthDetermination"] is False; assert p["modelConditionalForecasts"] is True


def test_store_scenario_creates_head_and_single_revision(monkeypatch):
    import app.predictive_investigation_workspace as pw
    from app.models import PredictiveScenarioHead, PredictiveScenarioRevision
    class FakeDB:
        def __init__(self): self.added=[]
        def add(self,obj): self.added.append(obj)
        def flush(self): pass
    monkeypatch.setattr(pw,"_project",lambda db,user_key,project_id:object())
    monkeypatch.setattr(pw,"_scenario",lambda db,user_key,scenario_id:None)
    db=FakeDB(); req=pw.PredictiveScenarioRequestModel(schema="sc-workspace-predictive-scenario-request/1.0",projectId="p1",title="constructor",assumptions=[{"name":"a","value":1}])
    result=pw.store_scenario(db,"u1",req)
    assert result["revision"]==1
    assert sum(isinstance(x,PredictiveScenarioHead) for x in db.added)==1
    assert sum(isinstance(x,PredictiveScenarioRevision) for x in db.added)==1
