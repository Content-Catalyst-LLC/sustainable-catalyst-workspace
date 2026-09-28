from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN="v325-explain-token"

def load_runtime(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN",TOKEN)
    path=ROOT/"neural-runtime"/"service.py"; spec=importlib.util.spec_from_file_location("scw_neural_v32500",path)
    assert spec and spec.loader; module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload):
    return {"schema":"sc-workspace-polyglot-execution-envelope/1.0","workspaceVersion":"3.28.0","jobId":"job-v325-explain","language":"neural","operation":op,"payload":payload,"arbitraryCodeExecution":False}

def post(c,op,payload): return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def linear_regression_model(): return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[2.0,3.0]],"bias":[1.0],"activation":"identity"}
def binary_model(): return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[4.0,-2.0]],"bias":[-1.0],"activation":"identity"}
def multiclass_model(): return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[-2.0,0.0],[0.0,1.0],[2.0,0.0]],"bias":[1.0,0.0,-1.0],"activation":"identity"}

def test_health_exposes_v325_explainability(monkeypatch):
    _,c=load_runtime(monkeypatch); x=c.get('/health').json()
    assert x['version'] in {'3.28.0','3.29.0','3.30.0','3.31.0'}; assert len(x['operations'])>=35
    assert x['explainabilityRuntimeEnabled'] is True
    assert x['explainabilityArtifactSchema']=='sc-workspace-neural-explainability-artifact/1.0'
    assert set(x['explainabilityMethods'])=={'input-gradient','integrated-gradients','feature-occlusion','global-gradient-sensitivity'}
    assert x['devicePolicy'] in {'cpu-only-neural-explainability','cpu-only-embedding-representation','cpu-only-inference-prediction-provenance','cpu-only-reproducible-model-packages','governed-explicit-device-orchestration','governed-remote-gpu-execution-broker'}

def test_regression_gradient_is_exact(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'modelSpec':linear_regression_model(),'features':[[1.0,2.0],[3.0,4.0]],'task':'regression','featureNames':['a','b']}
    r=post(c,'workspace.neural.explain-gradient',payload); assert r.status_code==200,r.text
    x=r.json()['result']; assert x['attributions']==[[2.0,3.0],[2.0,3.0]]
    assert x['featureSummary'][0]['featureName']=='b'
    assert x['explainabilityArtifact']['schema']=='sc-workspace-neural-explainability-artifact/1.0'
    assert len(x['explainabilityArtifact']['artifactFingerprint'])==64

def test_integrated_gradients_linear_completeness(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'modelSpec':linear_regression_model(),'features':[[1.0,2.0]],'task':'regression','featureNames':['a','b'],'steps':32}
    r=post(c,'workspace.neural.explain-integrated-gradients',payload); assert r.status_code==200,r.text
    x=r.json()['result']; attrs=x['attributions'][0]
    assert abs(attrs[0]-2.0)<1e-6 and abs(attrs[1]-6.0)<1e-6
    assert abs(x['completenessDelta'][0])<1e-5

def test_binary_occlusion_is_probability_delta(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'modelSpec':binary_model(),'features':[[1.0,1.0]],'task':'binary-classification','featureNames':['positive','negative']}
    r=post(c,'workspace.neural.explain-occlusion',payload); assert r.status_code==200,r.text
    x=r.json()['result']; a=x['attributions'][0]
    assert a[0]>0 and a[1]<0
    assert x['explainabilityArtifact']['targetSelection']['mode']=='positive-class-probability'

def test_multiclass_predicted_target_is_fixed_for_integrated_gradients(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'modelSpec':multiclass_model(),'features':[[2.0,0.0],[-2.0,0.0]],'task':'multiclass-classification','steps':16}
    r=post(c,'workspace.neural.explain-integrated-gradients',payload); assert r.status_code==200,r.text
    art=r.json()['result']['explainabilityArtifact']; assert art['targetSelection']['selectedTargets']==[2,0]
    assert art['targetSelection']['mode']=='selected-class-probability'

def test_global_sensitivity_orders_linear_regression_features(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'modelSpec':linear_regression_model(),'features':[[1.0,2.0],[3.0,4.0]],'task':'regression','featureNames':['a','b']}
    r=post(c,'workspace.neural.explain-global-sensitivity',payload); assert r.status_code==200,r.text
    s=r.json()['result']['sensitivity']; assert s[0]['featureName']=='b' and s[0]['meanAbsoluteGradient']==3.0
    assert s[1]['featureName']=='a' and s[1]['meanAbsoluteGradient']==2.0

def training_spec(): return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':2,'outputFeatures':1,'epochs':2,'batchSize':2,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}
def test_explainability_binds_checkpoint_model_lineage(monkeypatch):
    _,c=load_runtime(monkeypatch)
    t={'seed':17,'features':[[0.0,0.0],[1.0,1.0],[2.0,2.0],[3.0,3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],'trainingSpec':training_spec()}
    tr=post(c,'workspace.neural.train-linear',t); assert tr.status_code==200,tr.text; rr=tr.json()['result']
    payload={'modelSpec':rr['trainedModelSpec'],'checkpointArtifact':rr['checkpointArtifact'],'features':[[1.0,1.0]],'task':'regression'}
    ok=post(c,'workspace.neural.explain-gradient',payload); assert ok.status_code==200,ok.text
    x=ok.json()['result']; assert x['checkpointFingerprint']==rr['checkpointArtifactFingerprint']
    bad=deepcopy(payload); bad['modelSpec']=linear_regression_model(); rej=post(c,'workspace.neural.explain-gradient',bad)
    assert rej.status_code==400 and 'checkpoint trained model fingerprint' in rej.text

def test_bounds_and_workspace_registry():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)>=35
    for op in ['workspace.neural.explain-gradient','workspace.neural.explain-integrated-gradients','workspace.neural.explain-occlusion','workspace.neural.explain-global-sensitivity']: assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion'] in {'3.28.0','3.29.0','3.30.0','3.31.0'}; assert cp['typedEndpointCount']==291; assert cp['missingOpenApiOperations']==[]
