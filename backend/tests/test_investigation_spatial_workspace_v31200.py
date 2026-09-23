from app.investigation_spatial_workspace import profile, SPATIAL_WORKSPACE_SCHEMA, InvestigationSpatialObservationRequest, InvestigationSpatialRelationRequest
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_profile_boundaries():
 p=profile(); assert p["schema"]==SPATIAL_WORKSPACE_SCHEMA; assert p["workspaceVersion"]=="3.12.0"; assert p["mapReadyProjection"] is True; assert p["automaticGeolocationInference"] is False; assert p["automaticTruthDetermination"] is False
def test_observation_requires_location():
 try: InvestigationSpatialObservationRequest(schema="sc-workspace-investigation-spatial-observation-request/1.0",projectId="p",observationType="point",label="x",sourceRef="s",sourceFingerprint="12345678")
 except ValueError: pass
 else: raise AssertionError("expected validation error")
def test_relation_endpoints_differ():
 try: InvestigationSpatialRelationRequest(schema="sc-workspace-investigation-spatial-relation-request/1.0",projectId="p",fromObservationId="a",toObservationId="a",relation="near")
 except ValueError: pass
 else: raise AssertionError("expected validation error")
def test_v312_typed_endpoints():
 expected={"spatialEvidenceWorkspace","spatialObservationStore","spatialObservations","spatialObservation","spatialObservationRevisions","spatialContextLinkCreate","spatialContextLinks","spatialRelationCreate","spatialRelations","spatialMapProjection","spatialGraph","spatialDiagnostics","spatialSnapshotCreate","spatialSnapshots"}; assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=164
def test_openapi_has_spatial_routes():
 paths=app.openapi()["paths"]; assert "/v1/spatial-evidence-workspace" in paths; assert "/v1/spatial-evidence-workspace/projects/{project_id}/map" in paths; assert "/v1/spatial-evidence-workspace/projects/{project_id}/diagnostics" in paths
def test_no_automatic_inference_contract():
 p=profile(); assert p["automaticRelationshipInference"] is False; assert p["automaticCausalityInference"] is False; assert p["automaticNarrativeSelection"] is False
