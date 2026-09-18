from unittest.mock import MagicMock, patch
from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.local_first_sync import profile, bootstrap, reconcile
from app.main import app, health
from app.schemas import LocalFirstSyncReconcileRequest

def test_profile_preserves_server_authority_and_allows_offline_drafts():
    p=profile(); assert p['schema']=='sc-workspace-local-first-sync/1.0'; assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False
    assert p['offlineOutboxAllowed'] is True and p['offlineOutboxAuthoritative'] is False; assert p['baseRevisionRequired'] is True; assert p['automaticSemanticMerge'] is False

def test_bootstrap_emits_revision_vector_and_checkpoint():
    with patch('app.local_first_sync.list_projects',return_value=[{'projectId':'p1','revision':3},{'projectId':'p2','revision':1}]):
        b=bootstrap(MagicMock(),'u1')
    assert b['revisionVector']=={'p1':3,'p2':1}; assert len(b['checkpoint'])==64; assert b['clientPolicy']['queueOfflineMutations'] is True

def test_reconciliation_classifies_server_and_client_drift_without_merging():
    req=LocalFirstSyncReconcileRequest.model_validate({'schema':'sc-workspace-sync-reconcile-request/1.0','deviceId':'d1','clientRevisionVector':{'p1':1,'p2':4,'p3':2}})
    with patch('app.local_first_sync.list_projects',return_value=[{'projectId':'p1','revision':3},{'projectId':'p2','revision':2},{'projectId':'p4','revision':1}]):
        r=reconcile(MagicMock(),'u1',req)
    by={x['projectId']:x for x in r['items']}; assert by['p1']['status']=='server-ahead'; assert by['p2']['status']=='client-ahead'; assert by['p3']['status']=='missing-server'; assert by['p4']['status']=='server-ahead'; assert r['automaticMerge'] is False

def test_typed_contract_includes_all_sync_routes():
    item=client_profile(app.openapi()); assert item['workspaceVersion']=='2.31.0'; assert item['typedEndpointCount']==len(TYPED_ENDPOINTS)==20; assert item['missingOpenApiOperations']==[]
    assert item['typedEndpoints']['syncEnvelope']['path']=='/v1/sync/envelopes'; assert item['requestSchemas']['syncEnvelope']=='sc-workspace-sync-envelope/1.0'

def test_health_advertises_local_first_protocol():
    h=health(); assert h['version']=='2.31.0'; assert h['localFirstSynchronizationProtocol'] is True; assert h['offlineOutboxAuthoritative'] is False; assert h['syncAutomaticSemanticMerge'] is False
