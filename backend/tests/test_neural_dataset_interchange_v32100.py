from pathlib import Path
import importlib.util
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
TOKEN="neural-secret"
def load(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN",TOKEN)
    spec=importlib.util.spec_from_file_location("neural_runtime_v32100",ROOT/"neural-runtime"/"service.py")
    module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module
def env(op,payload):
    return {"schema":"sc-workspace-polyglot-execution-envelope/1.0","workspaceVersion":"3.23.0","jobId":"job-v321-test","language":"neural","operation":op,"payload":payload,"arbitraryCodeExecution":False}
def post(client,op,payload): return client.post("/v1/execute",json=env(op,payload),headers={"Authorization":f"Bearer {TOKEN}"})
def test_health_declares_v321_interchange(monkeypatch):
    m=load(monkeypatch)
    with TestClient(m.app) as c: body=c.get('/health').json()
    assert body['version']=='3.23.0'; assert len(body['operations'])==14
    assert body['tensorDatasetTransformationInterchange'] is True
    assert body['transformationLineage'] is True
    assert body['externalDatasetReadEnabled'] is False
    assert body['trainingEnabled'] is True
    assert body['checkpointPersistenceEnabled'] is True
def test_tensor_contract(monkeypatch):
    m=load(monkeypatch)
    with TestClient(m.app) as c: r=post(c,'workspace.neural.tensor-contract',{'tensor':[[1,2],[3,4]],'dtype':'float32','logicalName':'features','role':'features'})
    assert r.status_code==200,r.text; x=r.json()['result']; assert x['contract']['shape']==[2,2]; assert len(x['tensorFingerprint'])==64
def test_dataset_manifest_is_reference_only(monkeypatch):
    m=load(monkeypatch); spec={'schema':'sc-workspace-neural-dataset-manifest/1.0','datasetId':'ds-1','sourceDatasetRef':'workspace-dataset:abc','split':'train','rowCount':100,'featureNames':['a','b'],'targetName':'y','contentFingerprint':'sha256:abc','tensorBindings':[{'logicalName':'x','role':'features','tensorFingerprint':'abc123'}]}
    with TestClient(m.app) as c: r=post(c,'workspace.neural.dataset-manifest',{'datasetSpec':spec})
    assert r.status_code==200,r.text; x=r.json()['result']; assert x['externalDatasetReadPerformed'] is False; assert x['manifest']['sourceDatasetRef']=='workspace-dataset:abc'; assert x['manifest']['tensorBindings'][0]['role']=='features'
def test_batch_plan(monkeypatch):
    m=load(monkeypatch)
    with TestClient(m.app) as c: r=post(c,'workspace.neural.batch-plan',{'rowCount':10,'batchSize':4,'dropLast':False,'shuffle':True,'seed':9})
    x=r.json()['result']['plan']; assert x['batchCount']==3; assert x['remainderRows']==2; assert x['deterministicShuffle'] is True; assert 'rowIndices' in x['preview'][0]
def test_transformation_apply_lineage(monkeypatch):
    m=load(monkeypatch); payload={'tensor':[[1.0,10.0],[3.0,20.0]],'transforms':[{'op':'standardize','mean':[2.0,15.0],'scale':[1.0,5.0]},{'op':'select-columns','columns':[1]},{'op':'clip','min':-0.5,'max':0.5}]}
    with TestClient(m.app) as c: r=post(c,'workspace.neural.transformation-apply',payload)
    assert r.status_code==200,r.text; x=r.json()['result']; assert x['transformationCount']==3; assert x['outputSummary']['shape']==[2,1]; assert x['values']==[[-0.5],[0.5]]; assert len(x['lineage'])==3
def test_polyglot_preserves_interchange_operations_with_training_extension():
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert n.runtime=='python-pytorch-neural'; assert len(n.operations)==14; assert 'workspace.neural.transformation-apply' in n.operations
    assert RUNTIME_BY_LANGUAGE['ml'].runtime=='python-sklearn-predictive'; assert set(n.operations).isdisjoint(set(RUNTIME_BY_LANGUAGE['ml'].operations))
def test_client_contract_version_and_count():
    from app.client_contracts import TYPED_ENDPOINTS,profile
    from app.main import app
    cp=profile(app.openapi()); assert cp['workspaceVersion']=='3.23.0'; assert cp['typedEndpointCount']==291; assert cp['missingOpenApiOperations']==[]
