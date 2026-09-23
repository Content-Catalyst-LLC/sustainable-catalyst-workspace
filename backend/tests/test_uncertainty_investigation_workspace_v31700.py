from app.uncertainty_investigation_workspace import UncertaintyAssessmentRequest, UncertaintyParameterRequest, SensitivityAnalysisRequest, profile
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_uncertainty_assessment_schema():
    x=UncertaintyAssessmentRequest(schema="sc-workspace-uncertainty-assessment-request/1.0",projectId="p1",title="Demand uncertainty",methodFamily="monte-carlo")
    assert x.methodFamily=="monte-carlo"

def test_uncertainty_parameter_distribution_schema():
    x=UncertaintyParameterRequest(schema="sc-workspace-uncertainty-parameter-request/1.0",assessmentId="a1",name="growth",distribution="triangular",distributionParameters={"min":0,"mode":1,"max":2})
    assert x.distribution=="triangular"

def test_sensitivity_request_supports_sobol_morris_destinations():
    x=SensitivityAnalysisRequest(schema="sc-workspace-sensitivity-analysis-request/1.0",assessmentId="a1",method="sobol",destinationProduct="catalyst-analytics-r")
    assert x.method=="sobol" and x.destinationProduct=="catalyst-analytics-r"

def test_v317_typed_endpoints():
    expected={"uncertaintyInvestigationWorkspace","uncertaintyAssessmentStore","uncertaintyAssessments","uncertaintyAssessment","uncertaintyAssessmentRevisions","uncertaintyParameterCreate","uncertaintyParameters","uncertaintyScenarioCreate","uncertaintyScenarios","sensitivityAnalysisRequestCreate","sensitivityAnalysisRequests","probabilisticResultBindingCreate","probabilisticResultBindings","uncertaintyInvestigationManifest","uncertaintyInvestigationGraph","uncertaintyInvestigationDiagnostics","uncertaintyInvestigationSnapshotCreate","uncertaintyInvestigationSnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=254

def test_openapi_uncertainty_routes():
    paths=app.openapi()["paths"]
    assert "/v1/uncertainty-investigation-workspace" in paths
    assert "/v1/uncertainty-investigation-workspace/sensitivity-requests" in paths
    assert "/v1/uncertainty-investigation-workspace/projects/{project_id}/manifest" in paths

def test_uncertainty_epistemic_boundaries():
    p=profile(); assert p["automaticProbabilityAsTruth"] is False; assert p["automaticDistributionInference"] is False; assert p["automaticSensitivityExecution"] is False; assert p["automaticEvidenceRanking"] is False; assert p["automaticTruthDetermination"] is False; assert p["automaticCausalityInference"] is False

def test_store_assessment_creates_head_and_single_revision(monkeypatch):
    import app.uncertainty_investigation_workspace as uaw
    from app.models import UncertaintyAssessmentHead, UncertaintyAssessmentRevision
    class FakeDB:
        def __init__(self): self.added=[]
        def add(self,obj): self.added.append(obj)
        def flush(self): pass
    monkeypatch.setattr(uaw,"_project",lambda db,user_key,project_id:object())
    monkeypatch.setattr(uaw,"_assessment",lambda db,user_key,assessment_id:None)
    db=FakeDB(); req=uaw.UncertaintyAssessmentRequest(schema="sc-workspace-uncertainty-assessment-request/1.0",projectId="p1",title="constructor",methodFamily="monte-carlo")
    result=uaw.store_assessment(db,"u1",req)
    assert result["revision"]==1
    assert sum(isinstance(x,UncertaintyAssessmentHead) for x in db.added)==1
    assert sum(isinstance(x,UncertaintyAssessmentRevision) for x in db.added)==1
