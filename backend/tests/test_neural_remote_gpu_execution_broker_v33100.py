from __future__ import annotations
import importlib.util
import json
import time
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN='v331-broker-token'
SECRET='v331-remote-shared-secret'
WORKERS=json.dumps([{'workerId':'gpu-east-1','url':'https://gpu.example.invalid','device':'cuda:0','enabled':True,'tags':['gpu','test']}])

def load_runtime(monkeypatch, *, broker=False, worker=False, workers=WORKERS):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED','false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ALLOWED_DEVICES','cpu')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_BROKER_ENABLED','true' if broker else 'false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKER_MODE','true' if worker else 'false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_HMAC_SECRET',SECRET)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKERS_JSON',workers)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKER_ID','gpu-east-1')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKER_DEVICE','cuda:0')
    path=ROOT/'neural-runtime'/'service.py'
    spec=importlib.util.spec_from_file_location(f'scw_neural_v33100_{broker}_{worker}_{time.time_ns()}',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload):
    return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.31.0','jobId':'job-v331-broker','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}

def post(c,op,payload):
    return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def remote_payload():
    return {
      'remoteOperation':'workspace.neural.infer-regression',
      'remotePayload':{
        'modelSpec':{'schema':'sc-workspace-neural-model-spec/1.0','modelType':'linear','weights':[[2.0]],'bias':[1.0],'activation':'identity'},
        'features':[[3.0]],'rowIds':['r1'],'seed':17,
      },
    }

def test_health_and_registry_expose_v331_broker_contract(monkeypatch):
    _,c=load_runtime(monkeypatch); h=c.get('/health').json()
    assert h['version'] in {'3.31.0','3.32.0'} and len(h['operations'])>=48
    assert h['devicePolicy']=='governed-remote-gpu-execution-broker'
    assert h['remoteGpuExecutionBrokerEnabled'] is False
    assert h['remoteExecutionReceiptSchema']=='sc-workspace-neural-remote-execution-receipt/1.0'
    assert h['clientSuppliedRemoteWorkerUrlsAllowed'] is False

def test_inventory_redacts_operator_endpoint(monkeypatch):
    _,c=load_runtime(monkeypatch,broker=True)
    r=post(c,'workspace.neural.remote-worker-inventory',{}); assert r.status_code==200,r.text
    inv=r.json()['result']['remoteWorkerInventory']; assert inv['workerCount']==1
    assert inv['workers'][0]['workerId']=='gpu-east-1' and inv['workers'][0]['endpointConfigured'] is True
    assert 'url' not in inv['workers'][0] and len(inv['inventoryFingerprint'])==64

def test_dispatch_plan_uses_only_registered_worker_and_fingerprints_payload(monkeypatch):
    _,c=load_runtime(monkeypatch,broker=True); p=remote_payload(); p['workerUrl']='https://attacker.invalid'
    r=post(c,'workspace.neural.remote-dispatch-plan',p); assert r.status_code==200,r.text
    plan=r.json()['result']['dispatchPlan']; assert plan['workerId']=='gpu-east-1' and plan['selectedDevice']=='cuda:0'
    assert plan['clientSuppliedWorkerUrlsAllowed'] is False and 'url' not in plan
    assert len(plan['payloadFingerprint'])==64 and len(plan['planFingerprint'])==64

def test_disabled_broker_rejects_remote_dispatch(monkeypatch):
    _,c=load_runtime(monkeypatch,broker=False)
    r=post(c,'workspace.neural.remote-dispatch-plan',remote_payload())
    assert r.status_code==409 and 'disabled by operator policy' in r.text

def test_broker_rejects_recursive_or_unregistered_remote_operations(monkeypatch):
    _,c=load_runtime(monkeypatch,broker=True)
    p=remote_payload(); p['remoteOperation']='workspace.neural.remote-execute'
    r=post(c,'workspace.neural.remote-dispatch-plan',p); assert r.status_code==400
    p=remote_payload(); p['remoteOperation']='workspace.neural.tensor-summary'
    r=post(c,'workspace.neural.remote-dispatch-plan',p); assert r.status_code==400

def make_receipt(m, *, result_fp='a'*64):
    base={'schema':m.REMOTE_EXECUTION_RECEIPT_SCHEMA,'dispatchId':'ngd_test','workerId':'gpu-east-1','operation':'workspace.neural.infer-regression','payloadFingerprint':'b'*64,'dispatchPlanFingerprint':'c'*64,'resultFingerprint':result_fp,'selectedDevice':'cuda:0','devicePlanFingerprint':'d'*64,'runtimeVersion':'3.31.0','engineVersion':'2.10.0','startedAt':1,'finishedAt':2}
    fp=m._canonical_sha256(base); sigbase=dict(base); sigbase['receiptFingerprint']=fp
    out=dict(sigbase); out['signature']=m._remote_hmac(sigbase); return out

def test_receipt_verification_detects_tampering(monkeypatch):
    m,c=load_runtime(monkeypatch,broker=True); receipt=make_receipt(m)
    ok=post(c,'workspace.neural.remote-receipt-verify',{'remoteReceipt':receipt}); assert ok.status_code==200,ok.text
    assert ok.json()['result']['valid'] is True
    bad=deepcopy(receipt); bad['workerId']='gpu-west-9'
    rej=post(c,'workspace.neural.remote-receipt-verify',{'remoteReceipt':bad}); assert rej.status_code==400

def test_remote_execute_validates_signed_worker_response(monkeypatch):
    m,c=load_runtime(monkeypatch,broker=True)
    class FakeResponse:
        def __init__(self,b): self.b=b
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def read(self,n=-1): return self.b
    def fake_urlopen(req,timeout=None):
        dispatch=json.loads(req.data.decode())
        assert req.full_url=='https://gpu.example.invalid/v1/remote/execute'
        assert dispatch['operation']=='workspace.neural.infer-regression'
        assert dispatch['requestedDevice']=='cuda:0'
        result={'ok':True,'schema':'sc-workspace-neural-runtime-result/1.0','runtimeVersion':'3.31.0','device':'cuda:0','devicePlan':{'planFingerprint':'d'*64},'operation':dispatch['operation'],'result':{'predictions':[{'rowId':'r1','outputs':[7.0]}]}}
        rfp=m._canonical_sha256(result)
        base={'schema':m.REMOTE_EXECUTION_RECEIPT_SCHEMA,'dispatchId':dispatch['dispatchId'],'workerId':dispatch['workerId'],'operation':dispatch['operation'],'payloadFingerprint':dispatch['payloadFingerprint'],'dispatchPlanFingerprint':dispatch['dispatchPlanFingerprint'],'resultFingerprint':rfp,'selectedDevice':'cuda:0','devicePlanFingerprint':'d'*64,'runtimeVersion':'3.31.0','engineVersion':'2.10.0','startedAt':1,'finishedAt':2}
        fp=m._canonical_sha256(base); sigbase=dict(base); sigbase['receiptFingerprint']=fp
        receipt=dict(sigbase); receipt['signature']=m._remote_hmac(sigbase)
        body={'ok':True,'schema':m.REMOTE_WORKER_RESPONSE_SCHEMA,'result':result,'receipt':receipt}
        return FakeResponse(json.dumps(body).encode())
    monkeypatch.setattr(m.urllib.request,'urlopen',fake_urlopen)
    r=post(c,'workspace.neural.remote-execute',remote_payload()); assert r.status_code==200,r.text
    x=r.json()['result']; art=x['remoteExecutionArtifact']; assert art['schema']=='sc-workspace-neural-remote-execution-artifact/1.0'
    assert art['workerId']=='gpu-east-1' and art['selectedDevice']=='cuda:0' and len(art['artifactFingerprint'])==64
    assert x['remoteResult']['result']['predictions'][0]['outputs']==[7.0]

def test_worker_endpoint_rejects_unsigned_dispatch_and_nonce_cache_replay(monkeypatch):
    m,c=load_runtime(monkeypatch,worker=True)
    r=c.post('/v1/remote/execute',json={'schema':m.REMOTE_DISPATCH_ENVELOPE_SCHEMA})
    assert r.status_code==401
    m._prune_and_claim_remote_nonce('1234567890abcdef',int(time.time())+60)
    try:
        m._prune_and_claim_remote_nonce('1234567890abcdef',int(time.time())+60)
        assert False,'expected replay rejection'
    except Exception as exc:
        assert getattr(exc,'status_code',None)==409

def test_workspace_registry_persistence_and_typed_contract_expose_v331():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)>=48
    for op in ['workspace.neural.remote-worker-inventory','workspace.neural.remote-dispatch-plan','workspace.neural.remote-execute','workspace.neural.remote-receipt-verify']:
        assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion'] in {'3.31.0','3.32.0'} and cp['typedEndpointCount']==291 and cp['missingOpenApiOperations']==[]
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'application/vnd.sc.workspace.neural-remote-execution+json' in poly
    assert 'workspaceRemoteExecutionArtifactId' in poly and 'clientSuppliedRemoteWorkerUrlsAllowed' in poly
