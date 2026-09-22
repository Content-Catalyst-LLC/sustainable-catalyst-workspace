from app.client_contracts import TYPED_ENDPOINTS, REQUEST_SCHEMAS, profile as client_profile
from app.frontend_runtime import profile as frontend_profile
from app.production_certification import profile as certification_profile
from app.visual_research_workspace import profile as visual_profile
from app.main import app

def test_v360_visual_research_profile_boundaries():
    item=visual_profile(); assert item["workspaceVersion"]=="3.6.0"; assert item["referenceFirst"] is True; assert item["objectContentReplicatedToCore"] is False; assert item["sceneGraphProjection"] is True; assert item["sourceProvenancePinning"] is True; assert item["automaticMassBinding"] is False

def test_v360_typed_contract_has_70_operations_and_new_requests():
    item=client_profile(app.openapi()); assert len(TYPED_ENDPOINTS)>=70; assert item["typedEndpointCount"]==len(TYPED_ENDPOINTS); assert not item["missingOpenApiOperations"]; assert REQUEST_SCHEMAS["visualResearchVisualizationBind"]=="sc-workspace-visual-research-binding-request/1.0"; assert REQUEST_SCHEMAS["visualResearchSnapshotCreate"]=="sc-workspace-visual-research-workspace-snapshot-request/1.0"

def test_v360_release_lineage_and_frontend():
    cert=certification_profile(); assert cert["workspaceVersion"]=="3.6.0"; assert cert["migrationLineage"]=="037_platform_core_visual_analysis_research_object_workspace.sql"; assert cert["rollbackBaseline"]=="3.5.0"; assert cert["certificationGates"]["platformCoreVisualResearchWorkspace"]=="release-gate"; frontend=frontend_profile(); assert frontend["workspaceVersion"]=="3.6.0"; assert "v3.6.0" in frontend["activeShell"]

def test_v360_routes_are_present():
    paths=app.openapi()["paths"]; expected=["/v1/visual-research-workspace","/v1/visual-research-workspace/projects/{project_id}","/v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}","/v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}/bind","/v1/visual-research-workspace/projects/{project_id}/snapshots"]; [(_ for _ in ()).throw(AssertionError(path)) for path in expected if path not in paths]
