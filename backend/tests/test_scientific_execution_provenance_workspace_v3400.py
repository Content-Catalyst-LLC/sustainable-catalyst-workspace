import pytest
from pydantic import ValidationError

from app.execution_provenance import (
    EXECUTION_PROVENANCE_SCHEMA,
    ScientificExecutionProvenanceSnapshotRequest,
    _graph,
    profile,
)


def test_v3400_profile_preserves_research_authority_boundaries():
    item = profile()
    assert item['workspaceVersion'] == '3.4.0'
    assert item['schema'] == EXECUTION_PROVENANCE_SCHEMA
    assert item['backendAuthoritative'] is True
    assert item['browserAuthoritativeState'] is False
    assert item['referenceFirst'] is True
    assert item['specialistObjectAuthorityPreserved'] is True
    assert item['provenanceGraph'] is True
    assert item['immutableProvenanceSnapshots'] is True
    assert item['automaticScientificInterpretation'] is False
    assert item['automaticEvidenceRanking'] is False
    assert item['automaticDecisionAuthority'] is False


def test_v3400_snapshot_request_contract():
    req = ScientificExecutionProvenanceSnapshotRequest(
        schema='sc-workspace-scientific-execution-provenance-snapshot-request/1.0',
        runId='run-1',
    )
    assert req.runId == 'run-1'
    assert req.includeEvents is True
    assert req.includeReceipts is True
    with pytest.raises(ValidationError):
        ScientificExecutionProvenanceSnapshotRequest(schema='wrong')


def test_v3400_graph_links_inputs_outputs_receipts_and_core_session():
    run = {'runId':'run-1','reproducibilityFingerprint':'a'*64}
    inputs = {
        'datasets':[{'ref':{'datasetId':'d1','revision':2},'resolved':None}],
        'model':{'ref':{'modelId':'m1','revision':3},'resolved':None},
        'parameterSet':{'ref':{'parameterSetId':'p1','revision':1},'resolved':None},
        'environment':{'ref':{'environmentId':'e1','revision':4},'resolved':None},
        'runtimeAdapter':{'ref':{'adapterId':'a1','revision':5},'resolved':None},
    }
    outputs=[{'outputId':'o1','artifactId':'artifact-1','sha256':'b'*64}]
    receipts=[{'receiptId':'r1','receiptKind':'predictive-model'}]
    binding={'coreSessionId':'session-1'}
    graph=_graph(run,inputs,outputs,receipts,binding)
    relations={edge['relation'] for edge in graph['edges']}
    assert {'consumed-by','used-by','parameterized','executed-in','executed-via','produced','evidenced-by','bound-to'} <= relations
    assert graph['nodeCount'] == len(graph['nodes'])
    assert graph['edgeCount'] == len(graph['edges'])


def test_v3400_health_and_typed_contract():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    c = TestClient(app)
    health = c.get('/health').json()
    assert health['version'] == '3.4.0'
    assert health['scientificExecutionProvenanceWorkspace'] is True
    assert health['scientificExecutionProvenanceSchema'] == EXECUTION_PROVENANCE_SCHEMA
    assert health['executionProvenanceGraph'] is True
    assert health['executionProvenanceImmutableSnapshots'] is True
    assert health['releaseMigrationLineage'] == '035_scientific_execution_provenance_workspace.sql'
    typed = client_profile(app.openapi())
    assert typed['workspaceVersion'] == '3.4.0'
    assert typed['typedEndpointCount'] == len(TYPED_ENDPOINTS) == 64
    assert typed['typedEndpoints']['executionProvenanceRun']['method'] == 'GET'
    assert typed['typedEndpoints']['executionProvenanceSnapshotCreate']['method'] == 'POST'
    assert typed['missingOpenApiOperations'] == []


def test_v3400_execution_provenance_routes_are_protected():
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    assert c.get('/v1/execution-provenance').status_code in (401, 503)
    assert c.get('/v1/execution-provenance/projects/p1').status_code in (401, 503)
    assert c.get('/v1/execution-provenance/projects/p1/runs/r1').status_code in (401, 503)
    assert c.get('/v1/execution-provenance/projects/p1/snapshots').status_code in (401, 503)
    assert c.post('/v1/execution-provenance/projects/p1/snapshots', json={}).status_code in (401, 422, 503)
