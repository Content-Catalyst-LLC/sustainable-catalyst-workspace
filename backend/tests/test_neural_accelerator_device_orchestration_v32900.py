from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN='v329-device-token'

def load_runtime(monkeypatch, *, accelerator=False, allowed='cpu'):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED','true' if accelerator else 'false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ALLOWED_DEVICES',allowed)
    path=ROOT/'neural-runtime'/'service.py'
    spec=importlib.util.spec_from_file_location('scw_neural_v32900_'+('a' if accelerator else 'c'),path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload):
    return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.29.0','jobId':'job-v329-device','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}

def post(c,op,payload):
    return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def test_health_exposes_governed_device_orchestration(monkeypatch):
    _,c=load_runtime(monkeypatch); h=c.get('/health').json()
    assert h['version']in {'3.29.0','3.30.0'} and len(h['operations'])>=39
    assert h['devicePolicy']=='governed-explicit-device-orchestration'
    assert h['deviceOrchestrationEnabled'] is True and h['acceleratorDeviceOrchestrationEnabled'] is True
    assert h['devicePlanSchema']=='sc-workspace-neural-device-plan/1.0'
    assert h['deviceInventorySchema']=='sc-workspace-neural-device-inventory/1.0'
    assert h['availableDevices']==['cpu'] and h['acceleratorPolicyEnabled'] is False

def test_cpu_default_inventory_plan_and_smoke(monkeypatch):
    _,c=load_runtime(monkeypatch)
    inv=post(c,'workspace.neural.device-inventory',{}); assert inv.status_code==200,inv.text
    body=inv.json()['result']; assert body['deviceInventory']['devices'][0]['device']=='cpu'
    plan=post(c,'workspace.neural.device-plan',{'deviceRequest':'cpu'}); assert plan.status_code==200,plan.text
    p=plan.json()['result']['devicePlan']; assert p['selectedDevice']=='cpu' and p['acceleratorSelected'] is False and len(p['planFingerprint'])==64
    smoke=post(c,'workspace.neural.accelerator-smoke',{'deviceRequest':'cpu'}); assert smoke.status_code==200,smoke.text
    s=smoke.json(); assert s['device']=='cpu' and s['devicePlan']['selectedDevice']=='cpu'
    assert s['result']['acceleratorUsed'] is False and s['result']['output']==[[1.0,2.0],[3.0,4.0]]

def test_auto_falls_back_to_cpu_when_accelerator_policy_disabled(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.device-plan',{'deviceRequest':{'preference':'auto','allowFallback':True}}); assert r.status_code==200,r.text
    p=r.json()['result']['devicePlan']; assert p['selectedDevice']=='cpu'
    assert p['fallbackReason']=='no-policy-allowed-accelerator-available'

def test_strict_accelerator_request_rejects_when_unavailable(monkeypatch):
    _,c=load_runtime(monkeypatch)
    r=post(c,'workspace.neural.device-plan',{'deviceRequest':{'preference':'accelerator','strict':True,'allowFallback':False}})
    assert r.status_code==409 and 'accelerator is unavailable' in r.text

def test_device_plan_verification_detects_tampering(monkeypatch):
    _,c=load_runtime(monkeypatch)
    p=post(c,'workspace.neural.device-plan',{'deviceRequest':'cpu'}).json()['result']['devicePlan']
    ok=post(c,'workspace.neural.device-verify',{'devicePlan':p}); assert ok.status_code==200,ok.text
    bad=deepcopy(p); bad['selectedDevice']='cuda:0'
    rej=post(c,'workspace.neural.device-verify',{'devicePlan':bad}); assert rej.status_code==400 and 'fingerprint verification failed' in rej.text

def test_existing_inference_carries_governed_device_plan(monkeypatch):
    _,c=load_runtime(monkeypatch)
    model={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0]],'bias':[1.0],'activation':'identity'}
    r=post(c,'workspace.neural.infer-regression',{'deviceRequest':'cpu','modelSpec':model,'features':[[3.0]],'rowIds':['r1']}); assert r.status_code==200,r.text
    x=r.json(); assert x['device']=='cpu' and x['devicePlan']['selectedDevice']=='cpu'
    assert x['result']['predictions'][0]['outputs']==[7.0]

def test_model_package_runtime_contract_is_device_orchestration_aware(monkeypatch):
    _,c=load_runtime(monkeypatch)
    model={'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[1.0]],'bias':[0.0],'activation':'identity'}
    r=post(c,'workspace.neural.package-create',{'modelSpec':model,'task':'regression','featureNames':['x']}); assert r.status_code==200,r.text
    contract=r.json()['result']['modelPackage']['runtimeContract']
    assert contract['devicePolicy']=='governed-explicit-device-orchestration'
    assert contract['supportedDeviceClasses']==['cpu','cuda'] and contract['acceleratorRequired'] is False

def test_workspace_registry_compose_and_typed_contract_expose_v329():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)>=39
    for op in ['workspace.neural.device-inventory','workspace.neural.device-plan','workspace.neural.device-verify','workspace.neural.accelerator-smoke']:
        assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion'] in {'3.29.0','3.30.0'} and cp['typedEndpointCount']==291 and cp['missingOpenApiOperations']==[]
    compose=(ROOT/'docker-compose.example.yml').read_text(); gpu=(ROOT/'docker-compose.neural-gpu.example.yml').read_text()
    assert 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED' in compose and 'SC_WORKSPACE_NEURAL_ALLOWED_DEVICES' in compose
    assert 'gpus: all' in gpu and 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED: "true"' in gpu
