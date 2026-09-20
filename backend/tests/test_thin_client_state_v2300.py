from unittest.mock import patch

from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.main import app, health
from app.thin_client_state import CANONICAL_STATE_KINDS, TRANSIENT_STATE_KEYS, bootstrap, profile


def test_thin_client_profile_declares_backend_authority_and_transient_persistence_only():
    item=profile()
    assert item['schema']=='sc-workspace-thin-client-state/1.0'
    assert item['mode']=='backend-authoritative-thin-client'
    assert item['backendAuthoritative'] is True and item['browserAuthoritativeState'] is False
    assert item['canonicalStore']=='postgresql' and item['canonicalCache']=='memory-only-rehydratable'
    assert item['canonicalCachePersistent'] is False and item['persistentBrowserState']=='transient-only'
    assert item['canonicalMutations']=='command-api-only' and item['canonicalReads']=='server-read-models-only'


def test_transient_and_canonical_state_catalogs_are_separated():
    assert 'activeProjectId' in TRANSIENT_STATE_KEYS and 'viewport' in TRANSIENT_STATE_KEYS
    assert 'projects' in CANONICAL_STATE_KINDS and 'executionRuns' in CANONICAL_STATE_KINDS
    assert not set(TRANSIENT_STATE_KEYS).intersection(CANONICAL_STATE_KINDS)


def test_bootstrap_is_server_generated_and_fingerprinted():
    overview={'schema':'sc-workspace-read-model/workspace-overview/1.0','projects':[{'projectId':'p1','revision':4}], 'counts':{'projects':1}}
    detail={'schema':'sc-workspace-read-model/project-detail/1.0','project':{'projectId':'p1','revision':4}}
    with patch('app.thin_client_state.workspace_overview', return_value=overview), patch('app.thin_client_state.project_read_model', return_value=detail):
        item=bootstrap(object(),'u1','p1')
    assert item['schema']=='sc-workspace-thin-client-bootstrap/1.0'
    assert item['generatedServerSide'] is True and item['backendAuthoritative'] is True
    assert item['canonical']['revisionVector']=={'p1':4}
    assert item['canonical']['project']==detail
    assert len(item['projectionFingerprint'])==64
    assert item['clientPolicy']['persistCanonicalCache'] is False


def test_bootstrap_without_project_is_still_valid():
    overview={'schema':'sc-workspace-read-model/workspace-overview/1.0','projects':[], 'counts':{'projects':0}}
    with patch('app.thin_client_state.workspace_overview', return_value=overview):
        item=bootstrap(object(),'u1',None)
    assert item['canonical']['project'] is None and item['canonical']['revisionVector']=={}


def test_typed_contract_includes_thin_state_endpoints():
    item=client_profile(app.openapi())
    assert item['workspaceVersion'] in {'2.30.0','2.31.0','2.32.0','2.34.0','2.36.0'}
    assert item['typedEndpointCount']==len(TYPED_ENDPOINTS) and item['typedEndpointCount']>=15
    assert item['typedEndpoints']['thinClientState']['path']=='/v1/thin-client-state'
    assert item['typedEndpoints']['thinClientBootstrap']['path']=='/v1/thin-client-state/bootstrap'
    assert item['missingOpenApiOperations']==[]


def test_health_advertises_thin_client_state_architecture():
    item=health()
    assert item['version'] in {'2.30.0','2.31.0','2.32.0','2.34.0','2.36.0'}
    assert item['thinClientStateArchitecture'] is True
    assert item['canonicalClientCachePersistent'] is False
    assert item['persistentBrowserState']=='transient-only'
    assert item['canonicalMutationsViaCommandsOnly'] is True
