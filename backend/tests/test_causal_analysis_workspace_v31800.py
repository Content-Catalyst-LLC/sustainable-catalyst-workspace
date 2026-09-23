import pytest
from app.causal_analysis_workspace import CausalQuestionRequest, CausalStructureRequest, AlternativeExplanationRequest, IdentificationAssumptionRequest, CausalAnalysisHandoffRequest, profile, _has_cycle
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_causal_question_schema():
    x=CausalQuestionRequest(schema="sc-workspace-causal-question-request/1.0",projectId="p1",title="Does exposure affect outcome?",questionText="Estimate the effect of X on Y",estimand="ATE")
    assert x.estimand=="ATE"

def test_causal_structure_dag_semantics():
    variables=[{"variableId":"x","name":"Exposure","role":"exposure"},{"variableId":"y","name":"Outcome","role":"outcome"}]
    x=CausalStructureRequest(schema="sc-workspace-causal-structure-request/1.0",questionId="q1",title="Primary DAG",variables=variables,edges=[{"from":"x","to":"y","relation":"causes"}])
    assert x.structureKind=="dag" and _has_cycle({"x","y"},x.edges) is False
    assert _has_cycle({"x","y"},[{"from":"x","to":"y"},{"from":"y","to":"x"}]) is True

def test_alternative_explanations_and_identification_assumptions_are_explicit():
    a=AlternativeExplanationRequest(schema="sc-workspace-alternative-explanation-request/1.0",questionId="q1",title="Selection mechanism",explanation="Selection could generate the observed pattern")
    i=IdentificationAssumptionRequest(schema="sc-workspace-causal-identification-assumption-request/1.0",questionId="q1",assumptionType="no-unmeasured-confounding",statement="No relevant unmeasured common causes remain")
    assert a.status=="open" and i.status=="asserted"

def test_causal_handoff_supports_quasi_experimental_methods():
    x=CausalAnalysisHandoffRequest(schema="sc-workspace-causal-analysis-handoff-request/1.0",questionId="q1",method="difference-in-differences",destinationProduct="catalyst-analytics-r")
    assert x.method=="difference-in-differences" and x.destinationProduct=="catalyst-analytics-r"

def test_v318_typed_endpoints():
    expected={"causalAnalysisWorkspace","causalQuestionStore","causalQuestions","causalQuestion","causalQuestionRevisions","causalStructureCreate","causalStructures","alternativeExplanationCreate","alternativeExplanations","identificationAssumptionCreate","identificationAssumptions","causalAnalysisHandoffCreate","causalAnalysisHandoffs","causalResultBindingCreate","causalResultBindings","causalProjectAnalysis","causalInvestigationSnapshotCreate","causalInvestigationSnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=272

def test_openapi_causal_routes():
    paths=app.openapi()["paths"]
    assert "/v1/causal-analysis-workspace" in paths
    assert "/v1/causal-analysis-workspace/alternative-explanations" in paths
    assert "/v1/causal-analysis-workspace/projects/{project_id}/analysis" in paths

def test_causal_epistemic_boundaries():
    p=profile(); assert p["automaticCausalityInference"] is False; assert p["automaticCausalDiscovery"] is False; assert p["automaticConfounderSelection"] is False; assert p["automaticIdentificationClaim"] is False; assert p["automaticAlternativeExplanationRanking"] is False; assert p["automaticEvidenceRanking"] is False; assert p["automaticTruthDetermination"] is False; assert p["causalResultsModelConditional"] is True

def test_store_question_creates_head_and_single_revision(monkeypatch):
    import app.causal_analysis_workspace as caw
    from app.models import CausalQuestionHead, CausalQuestionRevision
    class FakeDB:
        def __init__(self): self.added=[]
        def add(self,obj): self.added.append(obj)
        def flush(self): pass
    monkeypatch.setattr(caw,"_project",lambda db,user_key,project_id:object())
    monkeypatch.setattr(caw,"_question",lambda db,user_key,question_id:None)
    db=FakeDB(); req=caw.CausalQuestionRequest(schema="sc-workspace-causal-question-request/1.0",projectId="p1",title="constructor",questionText="Does X cause Y?")
    result=caw.store_question(db,"u1",req)
    assert result["revision"]==1
    assert sum(isinstance(x,CausalQuestionHead) for x in db.added)==1
    assert sum(isinstance(x,CausalQuestionRevision) for x in db.added)==1
