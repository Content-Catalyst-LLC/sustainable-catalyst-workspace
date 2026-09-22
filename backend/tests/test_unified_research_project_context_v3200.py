from app.unified_research_context import profile, UnifiedResearchContextSnapshotRequest, CONTEXT_SCHEMA

def test_v3200_profile_preserves_specialist_authority():
    item=profile()
    assert item['workspaceVersion']=='3.2.0'
    assert item['backendAuthoritative'] is True
    assert item['referenceFirst'] is True
    assert item['specialistObjectAuthorityPreserved'] is True
    assert item['objectContentReplicatedToContext'] is False
    assert item['immutableContextSnapshots'] is True
    assert item['automaticScientificInference'] is False
    assert item['automaticDecisionAuthority'] is False


def test_v3200_snapshot_request_contract():
    req=UnifiedResearchContextSnapshotRequest(schema='sc-workspace-unified-research-project-context-snapshot-request/1.0')
    assert req.includeCoreViews is True


def test_v3200_health_and_typed_contract():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    health=TestClient(app).get('/health').json()
    assert health['version']=='3.2.0'
    assert health['unifiedResearchProjectContext'] is True
    assert health['unifiedResearchProjectContextSchema']==CONTEXT_SCHEMA
    assert health['researchContextImmutableSnapshots'] is True
    assert health['researchContextSpecialistAuthorityPreserved'] is True
    typed=client_profile(app.openapi())
    assert typed['workspaceVersion']=='3.2.0'
    assert typed['typedEndpointCount']==len(TYPED_ENDPOINTS)==55
    assert typed['typedEndpoints']['unifiedResearchProjectContext']['path']=='/v1/research-context/projects/{project_id}'
    assert typed['typedEndpoints']['unifiedResearchContextSnapshotCreate']['method']=='POST'
    assert typed['missingOpenApiOperations']==[]


def test_v3200_context_routes_are_protected():
    from fastapi.testclient import TestClient
    from app.main import app
    c=TestClient(app)
    for path in ('/v1/research-context','/v1/research-context/projects/test','/v1/research-context/projects/test/snapshots'):
        assert c.get(path).status_code in (401,503)
