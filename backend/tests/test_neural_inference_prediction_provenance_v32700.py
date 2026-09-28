from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN="v327-inference-token"

def load_runtime(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN",TOKEN)
    path=ROOT/"neural-runtime"/"service.py"; spec=importlib.util.spec_from_file_location("scw_neural_v32700",path)
    assert spec and spec.loader; module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload): return {"schema":"sc-workspace-polyglot-execution-envelope/1.0","workspaceVersion":"3.28.0","jobId":"job-v327-inference","language":"neural","operation":op,"payload":payload,"arbitraryCodeExecution":False}
def post(c,op,payload): return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def linear(weights,bias,activation='identity'):
    return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":weights,"bias":bias,"activation":activation}

def test_health_exposes_v327_inference_prediction_provenance(monkeypatch):
    _,c=load_runtime(monkeypatch); x=c.get('/health').json()
    assert x['version'] in {'3.28.0','3.29.0'}; assert len(x['operations'])>=35
    assert x['neuralInferencePredictionProvenanceEnabled'] is True
    assert x['predictionArtifactSchema']=='sc-workspace-neural-prediction-artifact/1.0'
    assert x['inferenceTargetsAccepted'] is False
    assert x['devicePolicy'] in {'cpu-only-inference-prediction-provenance','cpu-only-reproducible-model-packages','governed-explicit-device-orchestration'}

def test_regression_inference_exact_and_uncertainty_is_not_invented(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.infer-regression',{'modelSpec':linear([[2.0,-1.0]],[0.5]),'features':[[3.0,1.0]],'rowIds':['obs-a']})
    assert r.status_code==200,r.text; x=r.json()['result']; p=x['predictions'][0]
    assert abs(p['outputs'][0]-5.5)<1e-6
    assert p['uncertainty']=={'status':'not-estimated','method':None}
    a=x['predictionArtifact']; assert a['evidenceBoundary']['isObservedEvidence'] is False and a['evidenceBoundary']['targetsAccepted'] is False
    assert a['uncertaintySemantics']['status']=='not-estimated'

def test_binary_inference_probability_confidence_entropy(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.infer-binary',{'modelSpec':linear([[1.0]],[0.0]),'features':[[0.0],[2.0]],'rowIds':['zero','two'],'threshold':0.6})
    assert r.status_code==200,r.text; x=r.json()['result']; p0,p1=x['predictions']
    assert abs(p0['probability']-0.5)<1e-6 and p0['predictedClass']==0
    assert p1['probability']>0.88 and p1['predictedClass']==1 and p1['confidence']>0.88
    assert 0<=p1['normalizedEntropy']<=1
    assert x['predictionArtifact']['predictionPolicy']['calibrationStatus']=='not-assessed'

def test_multiclass_inference_probabilities_margin_and_provenance(monkeypatch):
    _,c=load_runtime(monkeypatch)
    model=linear([[2.0,0.0],[0.0,2.0],[-1.0,-1.0]],[0.0,0.0,0.0])
    r=post(c,'workspace.neural.infer-multiclass',{'modelSpec':model,'features':[[2.0,0.0],[0.0,2.0]],'rowIds':['a','b']})
    assert r.status_code==200,r.text; x=r.json()['result']; a=x['predictionArtifact']
    assert [p['predictedClass'] for p in x['predictions']]==[0,1]
    assert all(abs(sum(p['probabilities'])-1.0)<1e-6 for p in x['predictions'])
    assert all(p['margin']>0 for p in x['predictions'])
    assert len(a['modelSpecFingerprint'])==64 and len(a['inferenceDatasetFingerprint'])==64 and len(a['artifactFingerprint'])==64

def test_inference_rejects_targets_and_requires_evaluation_for_outcomes(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.infer-regression',{'modelSpec':linear([[1.0]],[0.0]),'features':[[1.0]],'targets':[[1.0]]})
    assert r.status_code==400 and 'do not accept targets' in r.text

def test_prediction_inspect_verifies_fingerprint_and_boundary(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.infer-regression',{'modelSpec':linear([[1.0]],[0.0]),'features':[[1.0]],'rowIds':['r1']}); assert r.status_code==200,r.text
    a=r.json()['result']['predictionArtifact']; ok=post(c,'workspace.neural.prediction-inspect',{'predictionArtifact':a}); assert ok.status_code==200,ok.text
    assert ok.json()['result']['summary']['evidenceBoundary']['isObservedEvidence'] is False
    bad=deepcopy(a); bad['predictions'][0]['outputs'][0]=99.0
    rej=post(c,'workspace.neural.prediction-inspect',{'predictionArtifact':bad}); assert rej.status_code==400 and 'fingerprint verification failed' in rej.text

def training_spec(): return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':2,'batchSize':2,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}
def test_inference_binds_checkpoint_model_lineage(monkeypatch):
    _,c=load_runtime(monkeypatch)
    tr=post(c,'workspace.neural.train-linear',{'seed':17,'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],'trainingSpec':training_spec()}); assert tr.status_code==200,tr.text
    rr=tr.json()['result']; payload={'modelSpec':rr['trainedModelSpec'],'checkpointArtifact':rr['checkpointArtifact'],'features':[[1.5]],'rowIds':['future-1']}
    inf=post(c,'workspace.neural.infer-regression',payload); assert inf.status_code==200,inf.text
    x=inf.json()['result']; assert x['checkpointFingerprint']==rr['checkpointArtifactFingerprint']
    assert x['predictionArtifact']['checkpointFingerprint']==rr['checkpointArtifactFingerprint']
    bad=deepcopy(payload); bad['modelSpec']=linear([[9.0]],[0.0]); rej=post(c,'workspace.neural.infer-regression',bad)
    assert rej.status_code==400 and 'checkpoint trained model fingerprint' in rej.text

def test_input_row_ids_are_governed_and_affect_dataset_fingerprint(monkeypatch):
    _,c=load_runtime(monkeypatch); model=linear([[1.0]],[0.0])
    a=post(c,'workspace.neural.infer-regression',{'modelSpec':model,'features':[[1.0]],'rowIds':['a']}).json()['result']
    b=post(c,'workspace.neural.infer-regression',{'modelSpec':model,'features':[[1.0]],'rowIds':['b']}).json()['result']
    assert a['inferenceDatasetFingerprint']!=b['inferenceDatasetFingerprint']
    dup=post(c,'workspace.neural.infer-regression',{'modelSpec':model,'features':[[1.0],[2.0]],'rowIds':['x','x']})
    assert dup.status_code==400 and 'unique' in dup.text

def test_workspace_registry_and_contract_expose_v327():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)>=35
    for op in ['workspace.neural.infer-regression','workspace.neural.infer-binary','workspace.neural.infer-multiclass','workspace.neural.prediction-inspect']: assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion'] in {'3.28.0','3.29.0'}; assert cp['typedEndpointCount']==291; assert cp['missingOpenApiOperations']==[]
