from pathlib import Path
import json
from app.polyglot import RUNTIMES, OPERATION_LANGUAGE
ROOT=Path(__file__).resolve().parents[1]
JULIA_OPS={"workspace.polyglot.julia.ode-linear-rk4","workspace.polyglot.julia.lotka-volterra","workspace.polyglot.julia.monte-carlo-normal","workspace.polyglot.julia.quadratic-optimize","workspace.polyglot.julia.eigen-analysis","workspace.polyglot.julia.integrate-series","workspace.polyglot.julia.polynomial-roots","workspace.polyglot.julia.parameter-sweep"}

def test_version_and_lineage():
    assert 'service_version: str = "2.14.0"' in (ROOT/'backend/app/config.py').read_text()
    dep=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text(); assert "const PREVIOUS_RELEASE = '2.13.0';" in dep; assert "const ROLLBACK_RELEASE = '2.13.0';" in dep

def test_julia_runtime_has_eight_bounded_operations():
    spec=next(r for r in RUNTIMES if r.language=='julia'); assert spec.runtime=='julia-simulation-numerical'; assert set(spec.operations)==JULIA_OPS; assert all(OPERATION_LANGUAGE[x]=='julia' for x in JULIA_OPS)

def test_julia_sidecar_is_fixed_operation_only():
    service=(ROOT/'backend/julia-runtime/service.py').read_text(); runner=(ROOT/'backend/julia-runtime/runner.jl').read_text(); assert 'shell=False' in service; assert '["/usr/local/bin/julia", "--startup-file=no", "--history-file=no", str(RUNNER)' in service; assert 'OPERATIONS = {' in service
    for unsafe in ('eval(', 'exec(', 'shell=True'): assert unsafe not in service
    for unsafe in ('eval(', 'Meta.parse(', 'run(`', 'pipeline('): assert unsafe not in runner

def test_julia_container_has_independent_sandbox_and_internal_network():
    compose=(ROOT/'backend/docker-compose.example.yml').read_text(); assert 'sc-workspace-julia-runtime:' in compose; assert 'build: ./julia-runtime' in compose; assert 'internal: true' in compose; assert 'cpus: 2.0' in compose; assert 'mem_limit: 2g' in compose; assert 'pids_limit: 128' in compose; assert 'read_only: true' in compose; assert 'no-new-privileges:true' in compose; assert 'SC_WORKSPACE_RUNTIME_JULIA_URL: ${SC_WORKSPACE_RUNTIME_JULIA_URL:-http://sc-workspace-julia-runtime:8091/v1/execute}' in compose

def test_migration_014_and_numerical_receipt_model():
    mig=(ROOT/'backend/migrations/014_julia_simulation_numerical_runtime.sql').read_text(); model=(ROOT/'backend/app/models.py').read_text(); assert 'workspace_numerical_simulation_receipts' in mig; assert 'GRANT SELECT, INSERT, UPDATE, DELETE' in mig; assert 'class NumericalSimulationReceipt' in model

def test_backend_routes_and_wordpress_read_only_proxies():
    main=(ROOT/'backend/app/main.py').read_text(); php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();
    for token in ('/v1/polyglot/runtimes/julia/status','/v1/numerical-simulation-receipts'): assert token in main
    for token in ('backend-julia-runtime-status','backend-numerical-simulation-receipts'): assert token in php

def test_release_contract_is_bounded():
    m=json.loads((ROOT/'release-manifest-v2.14.0.json').read_text())['julia_runtime']; assert m['operation_count']==8; assert m['internal_only_network'] is True; assert m['numerical_simulation_receipts'] is True; assert m['client_supplied_code_allowed'] is False; assert m['client_supplied_packages_allowed'] is False; assert m['client_supplied_runtime_urls_allowed'] is False; assert m['client_supplied_credentials_allowed'] is False; assert m['arbitrary_code_execution'] is False

def test_deployer_runs_real_julia_ode_smoke():
    deploy=(ROOT/'scripts/deploy_workspace_backend_v2_14_0_vps.sh').read_text(); assert 'migrations/014_julia_simulation_numerical_runtime.sql' in deploy; assert 'workspace.polyglot.julia.ode-linear-rk4' in deploy; assert 'numericalSimulationReceiptId' in deploy; assert 'sc-workspace-julia-runtime' in deploy; assert 'internal-only network' in deploy

def test_julia_service_auth_and_fixed_runner_dispatch(monkeypatch):
    import importlib.util
    from types import SimpleNamespace
    from fastapi.testclient import TestClient
    monkeypatch.setenv('SC_WORKSPACE_JULIA_RUNTIME_TOKEN','test-secret')
    spec=importlib.util.spec_from_file_location('sc_julia_runtime_service_v2140',ROOT/'backend/julia-runtime/service.py'); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    def fake_run(cmd,**kwargs):
        assert cmd[:4]==['/usr/local/bin/julia','--startup-file=no','--history-file=no','/app/runner.jl']; assert kwargs['shell'] is False; Path(cmd[5]).write_text('{"ok":true,"schema":"sc-workspace-julia-runtime-result/1.0","runtime":"julia-simulation-numerical","operation":"workspace.polyglot.julia.ode-linear-rk4","boundedOperationsOnly":true,"arbitraryCodeExecution":false,"result":{"kind":"linear-ode","solver":"rk4","steps":10,"metrics":{}}}'); return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(module.subprocess,'run',fake_run)
    envelope={'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'2.14.0','jobId':'job-test','language':'julia','operation':'workspace.polyglot.julia.ode-linear-rk4','payload':{'A':[[-1]],'initialState':[1],'dt':.1,'steps':10},'arbitraryCodeExecution':False}
    with TestClient(module.app) as client:
        assert client.get('/health').status_code==200; assert client.post('/v1/execute',json=envelope).status_code==401; response=client.post('/v1/execute',json=envelope,headers={'Authorization':'Bearer test-secret'})
    assert response.status_code==200; assert response.json()['runtime']=='julia-simulation-numerical'
