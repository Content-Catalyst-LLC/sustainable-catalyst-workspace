from app.investigation_graph_workspace import profile, INVESTIGATION_GRAPH_WORKSPACE_SCHEMA
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_profile_boundaries():
    p=profile(); assert p['workspaceVersion']=='3.8.0'; assert p['schema']==INVESTIGATION_GRAPH_WORKSPACE_SCHEMA
    assert p['automaticTruthDetermination'] is False
    assert p['automaticEvidenceRanking'] is False
    assert p['automaticHypothesisRanking'] is False
    assert p['preferredHypothesisSelection'] is False

def test_typed_operations_present():
    expected={'investigationGraphWorkspace','investigationHypothesisSetStore','investigationHypothesisSets','investigationHypothesisSet','investigationGraph','investigationContradictions','investigationHypothesisMatrix','investigationCoverage','investigationGraphSnapshotCreate','investigationGraphSnapshots'}
    assert expected <= set(TYPED_ENDPOINTS)

def test_openapi_operations_present():
    schema=app.openapi(); paths=schema['paths']
    for name,e in TYPED_ENDPOINTS.items():
        if name.startswith('investigation'):
            assert e['path'] in paths
            assert e['method'].lower() in paths[e['path']]

def test_release_lineage():
    from app.config import get_settings
    assert get_settings().service_version=='3.8.0'
