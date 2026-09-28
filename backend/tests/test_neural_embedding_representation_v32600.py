from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN="v326-embedding-token"

def load_runtime(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN",TOKEN)
    path=ROOT/"neural-runtime"/"service.py"; spec=importlib.util.spec_from_file_location("scw_neural_v32600",path)
    assert spec and spec.loader; module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload): return {"schema":"sc-workspace-polyglot-execution-envelope/1.0","workspaceVersion":"3.27.0","jobId":"job-v326-embedding","language":"neural","operation":op,"payload":payload,"arbitraryCodeExecution":False}
def post(c,op,payload): return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def mlp_model():
    return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"mlp","layers":[
        {"weights":[[1.0,0.0],[0.0,1.0]],"bias":[0.0,0.0],"activation":"relu"},
        {"weights":[[1.0,1.0]],"bias":[0.0],"activation":"identity"},
    ]}

def linear_model(): return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[1.0,0.0],[0.0,1.0]],"bias":[0.0,0.0],"activation":"identity"}

def generate(c,**extra):
    payload={"modelSpec":mlp_model(),"features":[[1.0,2.0],[-1.0,3.0]],"representation":"penultimate","rowIds":["r1","r2"]}
    payload.update(extra); r=post(c,'workspace.neural.embedding-generate',payload); assert r.status_code==200,r.text; return r.json()['result']

def test_health_exposes_v326_embedding_representation(monkeypatch):
    _,c=load_runtime(monkeypatch); x=c.get('/health').json()
    assert x['version']=='3.27.0'; assert len(x['operations'])==31
    assert x['embeddingRepresentationRuntimeEnabled'] is True
    assert x['embeddingArtifactSchema']=='sc-workspace-neural-embedding-artifact/1.0'
    assert x['representationAnalysisArtifactSchema']=='sc-workspace-neural-representation-analysis-artifact/1.0'
    assert x['devicePolicy'] in {'cpu-only-embedding-representation','cpu-only-inference-prediction-provenance'}

def test_penultimate_embedding_is_exact_and_governed(monkeypatch):
    _,c=load_runtime(monkeypatch); x=generate(c)
    assert x['vectors']==[[1.0,2.0],[0.0,3.0]]
    a=x['embeddingArtifact']; assert a['representation']=={'kind':'penultimate','layerIndex':0,'activation':'relu'}
    assert a['rows']==2 and a['dimensions']==2 and a['rowIds']==['r1','r2']
    assert len(a['artifactFingerprint'])==64 and a['schema']=='sc-workspace-neural-embedding-artifact/1.0'

def test_l2_normalization_is_bounded_and_deterministic(monkeypatch):
    _,c=load_runtime(monkeypatch); x=generate(c,normalization='l2'); a=x['embeddingArtifact']
    assert abs(a['vectorNorms'][0]-1.0)<1e-6 and abs(a['vectorNorms'][1]-1.0)<1e-6
    assert a['normalization']=='l2'

def test_pairwise_similarity_uses_governed_embedding(monkeypatch):
    _,c=load_runtime(monkeypatch); a=generate(c)['embeddingArtifact']
    r=post(c,'workspace.neural.embedding-similarity',{'embeddingArtifact':a,'metric':'cosine','pairs':[[0,1]]}); assert r.status_code==200,r.text
    x=r.json()['result']; assert x['representationArtifact']['analysisType']=='pairwise-similarity'
    assert x['pairs'][0]['leftRowId']=='r1' and x['pairs'][0]['rightRowId']=='r2'; assert 0.89<x['pairs'][0]['similarity']<0.90
    bad=deepcopy(a); bad['vectors'][0][0]=99.0; rej=post(c,'workspace.neural.embedding-similarity',{'embeddingArtifact':bad,'pairs':[[0,1]]})
    assert rej.status_code==400 and 'fingerprint verification failed' in rej.text

def test_nearest_neighbors_rank_expected_rows(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.embedding-generate',{'modelSpec':linear_model(),'features':[[1.0,0.0],[0.9,0.1],[-1.0,0.0]],'representation':'input','rowIds':['a','b','c'],'normalization':'none'}); assert r.status_code==200,r.text
    a=r.json()['result']['embeddingArtifact']
    nr=post(c,'workspace.neural.embedding-neighbors',{'embeddingArtifact':a,'metric':'cosine','queryIndices':[0],'k':2}); assert nr.status_code==200,nr.text
    q=nr.json()['result']['queries'][0]; assert [x['rowId'] for x in q['neighbors']]==['b','c']

def test_representation_summary_has_centroid_and_norms(monkeypatch):
    _,c=load_runtime(monkeypatch); a=generate(c)['embeddingArtifact']
    r=post(c,'workspace.neural.representation-summary',{'embeddingArtifact':a}); assert r.status_code==200,r.text
    x=r.json()['result']; assert x['summary']['centroid']==[0.5,2.5]
    assert x['representationArtifact']['schema']=='sc-workspace-neural-representation-analysis-artifact/1.0'
    assert x['representationArtifact']['sourceEmbeddingArtifactFingerprint']==a['artifactFingerprint']

def training_spec(): return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':2,'outputFeatures':1,'epochs':2,'batchSize':2,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}
def test_embedding_binds_checkpoint_model_lineage(monkeypatch):
    _,c=load_runtime(monkeypatch)
    t={'seed':17,'features':[[0.0,0.0],[1.0,1.0],[2.0,2.0],[3.0,3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],'trainingSpec':training_spec()}
    tr=post(c,'workspace.neural.train-linear',t); assert tr.status_code==200,tr.text; rr=tr.json()['result']
    payload={'modelSpec':rr['trainedModelSpec'],'checkpointArtifact':rr['checkpointArtifact'],'features':[[1.0,1.0]],'representation':'output'}
    ok=post(c,'workspace.neural.embedding-generate',payload); assert ok.status_code==200,ok.text
    x=ok.json()['result']; assert x['checkpointFingerprint']==rr['checkpointArtifactFingerprint']
    bad=deepcopy(payload); bad['modelSpec']={"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[2.0,3.0]],"bias":[1.0],"activation":"identity"}
    rej=post(c,'workspace.neural.embedding-generate',bad); assert rej.status_code==400 and 'checkpoint trained model fingerprint' in rej.text

def test_workspace_registry_and_contract_expose_v326():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==31
    for op in ['workspace.neural.embedding-generate','workspace.neural.representation-summary','workspace.neural.embedding-similarity','workspace.neural.embedding-neighbors']: assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion']=='3.27.0'; assert cp['typedEndpointCount']==291; assert cp['missingOpenApiOperations']==[]
