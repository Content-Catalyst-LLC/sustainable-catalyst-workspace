from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[1]
TOKEN='v332-cert-token'

def load_runtime(monkeypatch, *, broker=False, workers='[]', secret='v332-cert-secret'):
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_RUNTIME_TOKEN',TOKEN)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED','false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_ALLOWED_DEVICES','cpu')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_BROKER_ENABLED','true' if broker else 'false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKER_MODE','false')
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_HMAC_SECRET',secret)
    monkeypatch.setenv('SC_WORKSPACE_NEURAL_REMOTE_WORKERS_JSON',workers)
    path=ROOT/'neural-runtime'/'service.py'
    spec=importlib.util.spec_from_file_location(f'scw_neural_v33200_{broker}',path)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module,TestClient(module.app)

def env(op,payload):
    return {'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'3.32.0','jobId':'job-v332-cert','language':'neural','operation':op,'payload':payload,'arbitraryCodeExecution':False}

def post(c,op,payload):
    return c.post('/v1/execute',json=env(op,payload),headers={'Authorization':f'Bearer {TOKEN}'})

def execute_cert(c):
    r=post(c,'workspace.neural.certification-execute',{})
    assert r.status_code==200,r.text
    return r.json()['result']

def test_health_exposes_v332_production_certification(monkeypatch):
    _,c=load_runtime(monkeypatch); h=c.get('/health').json()
    assert h['version']=='3.32.0' and len(h['operations'])==52
    assert h['productionCertificationEnabled'] is True
    assert h['productionCertificationProfile']=='workspace-neural-production/1.0'
    assert h['productionCertificationArtifactSchema']=='sc-workspace-neural-production-certification-artifact/1.0'
    assert h['productionCertificationReportSchema']=='sc-workspace-neural-production-certification-report/1.0'
    assert h['clientSuppliedRemoteWorkerUrlsAllowed'] is False

def test_certification_plan_is_deterministic_and_complete(monkeypatch):
    _,c=load_runtime(monkeypatch)
    a=post(c,'workspace.neural.certification-plan',{}); b=post(c,'workspace.neural.certification-plan',{})
    assert a.status_code==200 and b.status_code==200
    pa=a.json()['result']['certificationPlan']; pb=b.json()['result']['certificationPlan']
    assert pa['planFingerprint']==pb['planFingerprint'] and len(pa['planFingerprint'])==64
    assert pa['expectedOperationCount']==52 and len(pa['requiredChecks'])==9
    assert pa['conditionalChecks']==['remote-gpu-worker-transport']

def test_certification_execute_passes_required_checks_and_is_honest_about_remote_gpu(monkeypatch):
    _,c=load_runtime(monkeypatch,broker=False); x=execute_cert(c); a=x['certificationArtifact']
    assert x['allRequiredPassed'] is True and a['productionStatus']=='certified'
    assert a['requiredCheckCount']==9 and a['passedRequiredCheckCount']==9
    assert a['remoteGpuTransportStatus']=='not-exercised-no-worker-attached'
    assert len(a['artifactFingerprint'])==64 and a['certificationId'].startswith('nrc_')
    checks={v['checkId']:v for v in a['checks']}
    assert checks['deterministic-inference']['details']['observed']==7.0
    assert checks['reproducible-model-package-roundtrip']['passed'] is True
    assert checks['remote-gpu-worker-transport']['conditional'] is True and checks['remote-gpu-worker-transport']['passed'] is False

def test_certification_verify_detects_tampering(monkeypatch):
    _,c=load_runtime(monkeypatch); a=execute_cert(c)['certificationArtifact']
    ok=post(c,'workspace.neural.certification-verify',{'certificationArtifact':a}); assert ok.status_code==200,ok.text
    assert ok.json()['result']['valid'] is True and ok.json()['result']['productionStatus']=='certified'
    bad=deepcopy(a); bad['checks'][0]['passed']=False
    rej=post(c,'workspace.neural.certification-verify',{'certificationArtifact':bad}); assert rej.status_code==400 and 'fingerprint verification failed' in rej.text

def test_certification_report_is_machine_verifiable_summary(monkeypatch):
    _,c=load_runtime(monkeypatch); a=execute_cert(c)['certificationArtifact']
    r=post(c,'workspace.neural.certification-report',{'certificationArtifact':a}); assert r.status_code==200,r.text
    rep=r.json()['result']['certificationReport']
    assert rep['schema']=='sc-workspace-neural-production-certification-report/1.0'
    assert rep['productionStatus']=='certified' and rep['requiredChecksPassed']==9 and rep['requiredChecksTotal']==9
    assert rep['failedRequiredChecks']==[] and len(rep['reportFingerprint'])==64

def test_certification_with_registered_broker_reports_ready_not_exercised(monkeypatch):
    workers='[{"workerId":"gpu-cert-1","url":"https://gpu.example.invalid","device":"cuda:0","enabled":true,"tags":["cert"]}]'
    _,c=load_runtime(monkeypatch,broker=True,workers=workers)
    a=execute_cert(c)['certificationArtifact']; checks={v['checkId']:v for v in a['checks']}
    assert a['productionStatus']=='certified'
    assert checks['remote-broker-safety']['passed'] is True
    assert checks['remote-broker-safety']['details']['workerCount']==1
    assert a['remoteGpuTransportStatus']=='ready-worker-registered'
    assert checks['remote-gpu-worker-transport']['conditional'] is True

def test_certification_rejects_unregistered_profile_and_blocked_payload_keys(monkeypatch):
    _,c=load_runtime(monkeypatch)
    bad=post(c,'workspace.neural.certification-plan',{'profile':'unknown-profile'}); assert bad.status_code==400
    blocked=post(c,'workspace.neural.certification-execute',{'code':'print(1)'}); assert blocked.status_code==400

def test_certification_artifact_identity_is_derived_from_fingerprint(monkeypatch):
    _,c=load_runtime(monkeypatch); a=execute_cert(c)['certificationArtifact']
    bad=deepcopy(a); bad['certificationId']='nrc_wrong'
    rej=post(c,'workspace.neural.certification-verify',{'certificationArtifact':bad}); assert rej.status_code==400 and 'identity verification failed' in rej.text

def test_workspace_registry_persistence_and_typed_contract_expose_v332():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    n=RUNTIME_BY_LANGUAGE['neural']; assert len(n.operations)==52
    for op in ['workspace.neural.certification-plan','workspace.neural.certification-execute','workspace.neural.certification-verify','workspace.neural.certification-report']:
        assert op in n.operations
    cp=profile(app.openapi()); assert cp['workspaceVersion']=='3.32.0' and cp['typedEndpointCount']==291 and cp['missingOpenApiOperations']==[]
    poly=(ROOT/'app'/'polyglot.py').read_text()
    assert 'application/vnd.sc.workspace.neural-production-certification+json' in poly
    assert 'workspaceProductionCertificationArtifactId' in poly
    main=(ROOT/'app'/'main.py').read_text()
    assert '"neuralRuntimeBoundedOperations": 52' in main and 'neuralRuntimeProductionCertification' in main
