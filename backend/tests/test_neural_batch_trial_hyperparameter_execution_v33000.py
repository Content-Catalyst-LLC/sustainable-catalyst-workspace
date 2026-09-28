from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN='v330-trial-token'

def load_runtime(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED','false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ALLOWED_DEVICES','cpu')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_MAX_TRAINING_SECONDS','30')
    path=ROOT/'neural-runtime'/'service.py'
    spec=importlib.util.spec_from_file_location('scw_neural_v33000',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload):
    return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.30.0','jobId':'job-v330-trial','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}

def post(c,op,payload):
    return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def base_payload():
    return {
      'trainingSpec':{'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'optimizer':{'name':'sgd','learningRate':0.05,'weightDecay':0.0},'epochs':2,'batchSize':4,'shuffle':False},
      'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],
      'validationFeatures':[[4.0],[5.0]],'validationTargets':[[9.0],[11.0]],
      'objective':{'dataset':'validation','metric':'loss','direction':'minimize'},'seed':17,'deviceRequest':'cpu'
    }

def test_health_and_registry_expose_v330(monkeypatch):
    _,c=load_runtime(monkeypatch); h=c.get('/health').json()
    assert h['version']=='3.30.0' and len(h['operations'])==44
    assert h['batchTrialHyperparameterExecutionEnabled'] is True
    assert h['trialArtifactSchema']=='sc-workspace-neural-trial-artifact/1.0'
    assert h['batchArtifactSchema']=='sc-workspace-neural-batch-artifact/1.0'
    assert h['hyperparameterSearchArtifactSchema']=='sc-workspace-neural-hyperparameter-search-artifact/1.0'

def test_trial_plan_is_bounded_and_fingerprinted(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['hyperparameters']={'optimizer.learningRate':0.02,'epochs':3}
    r=post(c,'workspace.neural.trial-plan',p); assert r.status_code==200,r.text
    plan=r.json()['result']['trialPlan']; assert plan['trainingSpec']['optimizer']['learningRate']==0.02
    assert plan['trainingSpec']['epochs']==3 and plan['device']=='cpu' and len(plan['planFingerprint'])==64

def test_single_trial_executes_and_emits_governed_artifact(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['hyperparameters']={'optimizer.learningRate':0.03}
    r=post(c,'workspace.neural.trial-execute',p); assert r.status_code==200,r.text
    art=r.json()['result']['trialArtifact']; assert art['schema']=='sc-workspace-neural-trial-artifact/1.0'
    assert art['trialId'].startswith('ntr_') and art['checkpointArtifact']['schema']=='sc-workspace-neural-checkpoint-artifact/1.0'
    assert art['objective']['dataset']=='validation' and isinstance(art['objectiveValue'],float)

def test_batch_execution_ranks_explicit_trials(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['trials']=[{'optimizer.learningRate':0.01},{'optimizer.learningRate':0.05},{'optimizer.learningRate':0.1}]
    r=post(c,'workspace.neural.batch-execute',p); assert r.status_code==200,r.text
    x=r.json()['result']; art=x['batchArtifact']; assert art['schema']=='sc-workspace-neural-batch-artifact/1.0'
    assert art['trialCount']==3 and len(art['trials'])==3 and len(art['ranking'])==3
    assert art['bestTrialId']==art['ranking'][0]['trialId'] and 'checkpointArtifact' not in art['trials'][0]
    assert x['bestTrial']['checkpointArtifact']['schema']=='sc-workspace-neural-checkpoint-artifact/1.0'

def test_grid_search_is_deterministic_and_bounded(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['parameterGrid']={'optimizer.learningRate':[0.01,0.05],'batchSize':[2,4]}
    a=post(c,'workspace.neural.hyperparameter-grid',deepcopy(p)); b=post(c,'workspace.neural.hyperparameter-grid',deepcopy(p))
    assert a.status_code==200 and b.status_code==200
    aa=a.json()['result']['searchArtifact']; bb=b.json()['result']['searchArtifact']
    assert aa['trialCount']==4 and aa['searchKind']=='grid' and aa['artifactFingerprint']==bb['artifactFingerprint']
    assert aa['ranking']==bb['ranking']

def test_random_search_is_seeded_and_reproducible(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['trialCount']=3; p['searchSpace']={
      'optimizer.learningRate':{'type':'loguniform','low':0.005,'high':0.1},
      'batchSize':{'type':'choice','values':[2,4]},
    }
    a=post(c,'workspace.neural.hyperparameter-random',deepcopy(p)); b=post(c,'workspace.neural.hyperparameter-random',deepcopy(p))
    assert a.status_code==200 and b.status_code==200
    aa=a.json()['result']['searchArtifact']; bb=b.json()['result']['searchArtifact']
    assert aa['trialCount']==3 and aa['searchKind']=='random' and aa['artifactFingerprint']==bb['artifactFingerprint']
    assert aa['trials']==bb['trials']

def test_unsupported_parameter_and_epoch_explosion_are_rejected(monkeypatch):
    _,c=load_runtime(monkeypatch); p=base_payload(); p['parameterGrid']={'hiddenLayers':[1,2]}
    r=post(c,'workspace.neural.hyperparameter-grid',p); assert r.status_code==400 and 'unsupported hyperparameter' in r.text
    p=base_payload(); p['trials']=[{'epochs':200},{'epochs':200}]
    r=post(c,'workspace.neural.batch-execute',p); assert r.status_code==413 and 'epoch budget' in r.text

def test_workspace_registry_persistence_and_typed_contract_expose_v330():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==44
    for op in ['workspace.neural.trial-plan','workspace.neural.trial-execute','workspace.neural.batch-execute','workspace.neural.hyperparameter-grid','workspace.neural.hyperparameter-random']:
        assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion']=='3.30.0' and cp['typedEndpointCount']==291 and cp['missingOpenApiOperations']==[]
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'application/vnd.sc.workspace.neural-trial+json' in poly
    assert 'application/vnd.sc.workspace.neural-batch+json' in poly
    assert 'application/vnd.sc.workspace.neural-hyperparameter-search+json' in poly
