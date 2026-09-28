from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN='v328-package-token'

def load_runtime(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    path=ROOT/'neural-runtime'/'service.py'; spec=importlib.util.spec_from_file_location('scw_neural_v32800',path)
    assert spec and spec.loader; module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload): return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.28.0','jobId':'job-v328-package','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}
def post(c,op,payload): return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})
def linear(weights,bias,activation='identity'): return {'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':weights,'bias':bias,'activation':activation}

def create(c,task='regression',**extra):
    model=extra.pop('modelSpec',linear([[2.0,-1.0]],[0.5]))
    payload={'modelSpec':model,'task':task,'featureNames':['x1','x2']}; payload.update(extra)
    r=post(c,'workspace.neural.package-create',payload); assert r.status_code==200,r.text; return r.json()['result']

def test_health_exposes_reproducible_model_packages(monkeypatch):
    _,c=load_runtime(monkeypatch); x=c.get('/health').json()
    assert x['version'] in {'3.28.0','3.29.0'} and len(x['operations'])>=35
    assert x['reproducibleModelPackagesEnabled'] is True
    assert x['modelPackageSchema']=='sc-workspace-neural-model-package/1.0'
    assert x['modelPackageFormat']=='sc-workspace-neural-reproducible-model-package/1.0'
    assert x['modelPackageDependencyPins']=={'torch':'2.10.0','numpy':'2.2.6'}
    assert x['modelPackageArbitraryCodeAllowed'] is False and x['modelPackageSerializedPyTorchAllowed'] is False
    assert x['devicePolicy'] in {'cpu-only-reproducible-model-packages','governed-explicit-device-orchestration'}

def test_package_create_is_portable_fingerprinted_and_dependency_explicit(monkeypatch):
    _,c=load_runtime(monkeypatch); x=create(c); p=x['modelPackage']
    assert p['portable'] is True and p['selfContainedInference'] is True
    assert p['manifest']['containsArbitraryCode'] is False and p['manifest']['containsSerializedPyTorchModel'] is False
    assert p['runtimeContract']['requiredDependencyPins']=={'torch':'2.10.0','numpy':'2.2.6'}
    assert p['inferenceContract']['featureNames']==['x1','x2'] and p['inferenceContract']['targetsAccepted'] is False
    assert p['packageId'].startswith('nmp_') and len(p['artifactFingerprint'])==64 and p['modelSpecFingerprint']==x['modelSpecFingerprint']

def test_package_verify_detects_tampering(monkeypatch):
    _,c=load_runtime(monkeypatch); p=create(c)['modelPackage']
    ok=post(c,'workspace.neural.package-verify',{'modelPackage':p}); assert ok.status_code==200,ok.text
    body=ok.json()['result']; assert body['valid'] is True and body['compatible'] is True
    bad=deepcopy(p); bad['modelSpec']['weights'][0][0]=99.0
    rej=post(c,'workspace.neural.package-verify',{'modelPackage':bad}); assert rej.status_code==400 and 'fingerprint verification failed' in rej.text

def test_package_inspect_returns_reproducibility_contract(monkeypatch):
    _,c=load_runtime(monkeypatch); p=create(c)['modelPackage']
    r=post(c,'workspace.neural.package-inspect',{'modelPackage':p}); assert r.status_code==200,r.text
    x=r.json()['result']; assert x['portable'] is True and x['selfContainedInference'] is True
    assert x['inputFeatures']==2 and x['outputFeatures']==1 and x['featureNames']==['x1','x2']
    assert x['manifest']['runtimeContractFingerprint']==p['manifest']['runtimeContractFingerprint']

def test_packaged_binary_inference_binds_prediction_to_package(monkeypatch):
    _,c=load_runtime(monkeypatch)
    p=create(c,task='binary-classification',modelSpec=linear([[1.0]],[0.0]),featureNames=['signal'],threshold=0.6)['modelPackage']
    r=post(c,'workspace.neural.package-infer',{'modelPackage':p,'features':[[0.0],[2.0]],'rowIds':['zero','two']}); assert r.status_code==200,r.text
    x=r.json()['result']; a=x['predictionArtifact']
    assert x['kind']=='neural-packaged-inference-result' and x['packageVerified'] is True
    assert [v['predictedClass'] for v in x['predictions']]==[0,1]
    assert a['sourceModelPackageFingerprint']==p['artifactFingerprint'] and a['sourceModelPackageId']==p['packageId']
    assert a['evidenceBoundary']['isObservedEvidence'] is False and a['predictionPolicy']['threshold']==0.6
    inspect=post(c,'workspace.neural.prediction-inspect',{'predictionArtifact':a}); assert inspect.status_code==200,inspect.text

def test_packaged_inference_rejects_targets(monkeypatch):
    _,c=load_runtime(monkeypatch); p=create(c)['modelPackage']
    r=post(c,'workspace.neural.package-infer',{'modelPackage':p,'features':[[1.0,2.0]],'targets':[[1.0]]})
    assert r.status_code==400 and 'does not accept targets' in r.text

def training_spec(): return {'schema':'sc-workspace-neural-training-spec/1.0','modelType':'linear','task':'regression','inputFeatures':1,'outputFeatures':1,'epochs':2,'batchSize':2,'shuffle':True,'optimizer':{'name':'adam','learningRate':0.05,'weightDecay':0.0}}
def test_package_can_embed_governed_checkpoint_lineage(monkeypatch):
    _,c=load_runtime(monkeypatch)
    tr=post(c,'workspace.neural.train-linear',{'seed':19,'features':[[0.0],[1.0],[2.0],[3.0]],'targets':[[1.0],[3.0],[5.0],[7.0]],'trainingSpec':training_spec()}); assert tr.status_code==200,tr.text
    rr=tr.json()['result']
    cr=post(c,'workspace.neural.package-create',{'modelSpec':rr['trainedModelSpec'],'checkpointArtifact':rr['checkpointArtifact'],'task':'regression','featureNames':['x']}); assert cr.status_code==200,cr.text
    p=cr.json()['result']['modelPackage']; assert p['checkpointFingerprint']==rr['checkpointArtifactFingerprint']
    assert p['manifest']['containsCheckpoint'] is True and p['provenance']['trainingDatasetFingerprint']==rr['checkpointArtifact']['trainingDatasetFingerprint']
    inf=post(c,'workspace.neural.package-infer',{'modelPackage':p,'features':[[1.5]],'rowIds':['future']}); assert inf.status_code==200,inf.text
    assert inf.json()['result']['predictionArtifact']['checkpointFingerprint']==rr['checkpointArtifactFingerprint']

def test_package_feature_and_task_contracts_are_enforced(monkeypatch):
    _,c=load_runtime(monkeypatch)
    bad=post(c,'workspace.neural.package-create',{'modelSpec':linear([[1.0,2.0]],[0.0]),'task':'regression','featureNames':['x']})
    assert bad.status_code==400 and 'featureNames' in bad.text
    dup=post(c,'workspace.neural.package-create',{'modelSpec':linear([[1.0,2.0]],[0.0]),'task':'regression','featureNames':['x','x']})
    assert dup.status_code==400 and 'unique' in dup.text
    wrong=post(c,'workspace.neural.package-create',{'modelSpec':linear([[1.0,2.0],[2.0,3.0]],[0.0,0.0]),'task':'binary-classification','featureNames':['a','b']})
    assert wrong.status_code==400 and 'one model output' in wrong.text

def test_workspace_registry_and_persistence_contract_expose_v328():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)>=35
    for op in ['workspace.neural.package-create','workspace.neural.package-verify','workspace.neural.package-inspect','workspace.neural.package-infer']: assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion'] in {'3.28.0','3.29.0'} and cp['typedEndpointCount']==291 and cp['missingOpenApiOperations']==[]
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'application/vnd.sc.workspace.neural-model-package+json' in poly
    assert 'workspaceModelPackageArtifactId' in poly and 'sourceModelPackageFingerprint' in poly
