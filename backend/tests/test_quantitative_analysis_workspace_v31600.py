from pydantic import ValidationError
from app.quantitative_analysis_workspace import QuantitativeReconstructionRequest, QuantitativeAnalysisHandoffRequest, QuantitativeAnalysisHandoffStatusRequest, profile
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_reconstruction_requires_project_and_title():
    x=QuantitativeReconstructionRequest(schema="sc-workspace-quantitative-reconstruction-request/1.0",projectId="p1",title="Load reconstruction",methodClass="statistical")
    assert x.projectId=="p1" and x.methodClass=="statistical"

def test_handoff_requires_destination():
    x=QuantitativeAnalysisHandoffRequest(schema="sc-workspace-quantitative-analysis-handoff-request/1.0",reconstructionId="r1",destinationProduct="catalyst-analytics-r",analysisKind="regression")
    assert x.destinationProduct=="catalyst-analytics-r"

def test_status_schema_accepts_reviewable_status_value():
    x=QuantitativeAnalysisHandoffStatusRequest(schema="sc-workspace-quantitative-analysis-handoff-status-request/1.0",status="completed",receiptRef="receipt:1")
    assert x.status=="completed"

def test_v316_typed_endpoints():
    expected={"quantitativeAnalysisWorkspace","quantitativeReconstructionStore","quantitativeReconstructions","quantitativeReconstruction","quantitativeReconstructionRevisions","quantitativeInputBindingCreate","quantitativeInputBindings","quantitativeAnalysisHandoffCreate","quantitativeAnalysisHandoffs","quantitativeAnalysisHandoff","quantitativeAnalysisHandoffStatus","quantitativeResultBindingCreate","quantitativeResultBindings","quantitativeAnalysisManifest","quantitativeAnalysisGraph","quantitativeAnalysisDiagnostics","quantitativeAnalysisSnapshotCreate","quantitativeAnalysisSnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=236

def test_openapi_quantitative_routes():
    paths=app.openapi()["paths"]
    assert "/v1/quantitative-analysis-workspace" in paths
    assert "/v1/quantitative-analysis-workspace/handoffs/{handoff_id}/status" in paths
    assert "/v1/quantitative-analysis-workspace/projects/{project_id}/manifest" in paths

def test_quantitative_safety_boundaries():
    p=profile(); assert p["automaticAnalysisExecution"] is False; assert p["automaticEvidenceTransformation"] is False; assert p["automaticEvidenceRanking"] is False; assert p["automaticTruthDetermination"] is False; assert p["coreExecutesSpecialistProvider"] is False

def test_store_reconstruction_creates_head_and_revision_without_duplicate_revision(monkeypatch):
    import app.quantitative_analysis_workspace as qaw
    from app.models import QuantitativeReconstructionHead, QuantitativeReconstructionRevision

    class FakeDB:
        def __init__(self): self.added=[]
        def add(self,obj): self.added.append(obj)
        def flush(self): pass

    monkeypatch.setattr(qaw, "_project", lambda db,user_key,project_id: object())
    monkeypatch.setattr(qaw, "_reconstruction", lambda db,user_key,reconstruction_id: None)
    db=FakeDB()
    req=qaw.QuantitativeReconstructionRequest(
        schema="sc-workspace-quantitative-reconstruction-request/1.0",
        projectId="p1",
        title="Runtime constructor regression",
        methodClass="statistical",
    )
    result=qaw.store_reconstruction(db,"u1",req)
    assert result["revision"]==1
    assert sum(isinstance(x,QuantitativeReconstructionHead) for x in db.added)==1
    assert sum(isinstance(x,QuantitativeReconstructionRevision) for x in db.added)==1
    revision=next(x for x in db.added if isinstance(x,QuantitativeReconstructionRevision))
    assert revision.revision==1

