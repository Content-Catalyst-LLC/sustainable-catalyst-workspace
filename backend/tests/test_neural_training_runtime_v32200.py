import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient

TOKEN='v322-test-token'

def load_runtime(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_MAX_TRAINING_SECONDS','10')
    path=Path(__file__).resolve().parents[1]/'neural-runtime'/'service.py'
    spec=importlib.util.spec_from_file_location('scw_neural_v322',path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod,TestClient(mod.app)

def env(op,payload):
    return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.28.0','jobId':'job-v322','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}

def post(client,op,payload):
    return client.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def linear_spec(epochs=8):
    return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':epochs,'batchSize':4,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}

def test_health_enables_bounded_training_but_not_checkpoints(monkeypatch):
    _,c=load_runtime(monkeypatch); body=c.get('/health').json()
    assert body['version'] in {'3.28.0','3.29.0','3.30.0','3.31.0'}; assert len(body['operations'])>=11
    assert body['trainingEnabled'] is True
    assert body['checkpointPersistenceEnabled'] is True and body['resumeTrainingEnabled'] is True
    assert body['acceleratorExecutionEnabled'] is False and body['devicePolicy'] in {'cpu-only-evaluation-calibration-uncertainty','cpu-only-neural-explainability','cpu-only-embedding-representation','cpu-only-inference-prediction-provenance','cpu-only-reproducible-model-packages','governed-explicit-device-orchestration','governed-remote-gpu-execution-broker'}
    assert body['trainingSpecSchema']=='sc-workspace-neural-training-spec/1.0'

def test_training_plan_is_bounded_and_fingerprinted(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.training-plan',{'seed':7,'trainingSpec':linear_spec()})
    assert r.status_code==200,r.text
    x=r.json()['result']; assert x['kind']=='neural-training-plan'; assert x['plan']['parameterCount']==2
    assert x['plan']['checkpointPersistenceEnabled'] is True and len(x['planFingerprint'])==64

def test_linear_training_is_deterministic_and_learns(monkeypatch):
    _,c=load_runtime(monkeypatch)
    payload={'seed':11,'features':[[0.],[1.],[2.],[3.],[4.],[5.]],'targets':[[1.],[3.],[5.],[7.],[9.],[11.]],'trainingSpec':linear_spec(epochs=40)}
    a=post(c,'workspace.neural.train-linear',payload); b=post(c,'workspace.neural.train-linear',payload)
    assert a.status_code==200,a.text; assert b.status_code==200,b.text
    ar=a.json()['result']; br=b.json()['result']
    run=ar['trainingRun']; assert run['completedEpochs']==40 and run['stoppedReason']=='completed'
    assert run['trainingMetrics']['loss'] < run['telemetry'][0]['trainingLoss']
    assert ar['trainedModelSpecFingerprint']==br['trainedModelSpecFingerprint']
    assert isinstance(ar['checkpointArtifact'],dict) and run['checkpointCreated'] is True

def test_mlp_binary_training_and_validation_telemetry(monkeypatch):
    _,c=load_runtime(monkeypatch)
    spec={'schema':'sc-workspace-neural-training-spec/1.0','modelType':'mlp','task':'binary-classification','inputFeatures':2,'hiddenLayers':[{'units':4,'activation':'tanh'}],'outputFeatures':1,'epochs':20,'batchSize':4,'optimizer':{'name':'adam','learningRate':0.05}}
    payload={'seed':5,'features':[[0,0],[0,1],[1,0],[1,1]],'targets':[0,1,1,1],'validationFeatures':[[0,0],[1,1]],'validationTargets':[0,1],'trainingSpec':spec}
    r=post(c,'workspace.neural.train-mlp',payload); assert r.status_code==200,r.text
    run=r.json()['result']['trainingRun']; assert run['modelType']=='mlp' and run['validationRows']==2
    assert 'validationLoss' in run['telemetry'][-1]; assert 0.0 <= run['trainingMetrics']['accuracy'] <= 1.0

def test_training_rejects_hidden_layers_for_linear_and_serialized_models(monkeypatch):
    _,c=load_runtime(monkeypatch)
    bad=linear_spec(); bad['hiddenLayers']=[{'units':4,'activation':'relu'}]
    r=post(c,'workspace.neural.train-linear',{'features':[[0.],[1.]],'targets':[0.,1.],'trainingSpec':bad})
    assert r.status_code==400
    r=post(c,'workspace.neural.train-linear',{'features':[[0.],[1.]],'targets':[0.,1.],'trainingSpec':linear_spec(),'stateDictBase64':'AA=='})
    assert r.status_code==400

def test_training_parameter_and_epoch_bounds(monkeypatch):
    _,c=load_runtime(monkeypatch)
    spec=linear_spec(epochs=201)
    r=post(c,'workspace.neural.training-plan',{'trainingSpec':spec}); assert r.status_code==400
