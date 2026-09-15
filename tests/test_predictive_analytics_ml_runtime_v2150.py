from pathlib import Path
import importlib.util
from fastapi.testclient import TestClient
from app.polyglot import RUNTIMES, OPERATION_LANGUAGE
ROOT=Path(__file__).resolve().parents[1]
ML_OPS={"workspace.ml.linear-regression","workspace.ml.logistic-classification","workspace.ml.random-forest-regression","workspace.ml.random-forest-classification","workspace.ml.gradient-boosting-regression","workspace.ml.gradient-boosting-classification","workspace.ml.cross-validate","workspace.ml.predict"}

def test_version_lineage_and_runtime_catalog():
    assert 'service_version: str = "2.15.0"' in (ROOT/'backend/app/config.py').read_text()
    dep=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text(); assert "const PREVIOUS_RELEASE = '2.14.0';" in dep; assert "const ROLLBACK_RELEASE = '2.14.0';" in dep
    spec=next(r for r in RUNTIMES if r.language=='ml'); assert spec.runtime=='python-sklearn-predictive'; assert set(spec.operations)==ML_OPS; assert all(OPERATION_LANGUAGE[x]=='ml' for x in ML_OPS)

def test_security_and_migration_contract():
    service=(ROOT/'backend/ml-runtime/service.py').read_text(); compose=(ROOT/'backend/docker-compose.example.yml').read_text(); mig=(ROOT/'backend/migrations/015_predictive_analytics_machine_learning_runtime.sql').read_text()
    for unsafe in ('eval(', 'exec(', 'pickle.loads', 'joblib.load('): assert unsafe not in service
    assert 'clientSuppliedSerializedModelsAllowed":False' in service
    assert 'sc-workspace-ml-runtime:' in compose and 'internal: true' in compose and 'read_only: true' in compose and 'no-new-privileges:true' in compose
    assert 'workspace_predictive_model_receipts' in mig and 'workspace_model_evaluation_receipts' in mig and 'GRANT SELECT, INSERT, UPDATE, DELETE' in mig

def test_ml_sidecar_linear_regression(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_ML_RUNTIME_TOKEN','test-secret')
    spec=importlib.util.spec_from_file_location('sc_workspace_ml_service_v2150',ROOT/'backend/ml-runtime/service.py'); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    rows=[{'x':float(i),'y':2.0*float(i)+1.0} for i in range(1,31)]
    envelope={'schema':'sc-workspace-polyglot-execution-envelope/1.0','workspaceVersion':'2.15.0','jobId':'job-test','language':'ml','operation':'workspace.ml.linear-regression','payload':{'rows':rows,'features':['x'],'target':'y','seed':7,'testFraction':0.2},'arbitraryCodeExecution':False}
    with TestClient(module.app) as client:
        assert client.post('/v1/execute',json=envelope).status_code==401
        r=client.post('/v1/execute',json=envelope,headers={'Authorization':'Bearer test-secret'})
    assert r.status_code==200, r.text
    result=r.json()['result']; assert result['modelKind']=='linear-regression'; assert result['metrics']['r2']>0.999; assert result['modelArtifact']['bytes']>0; assert len(result['modelArtifact']['sha256'])==64

def test_wordpress_read_only_proxies_and_release_contract():
    php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();
    for token in ('backend-ml-runtime-status','backend-predictive-model-receipts','backend-model-evaluation-receipts'): assert token in php
    m=__import__('json').loads((ROOT/'release-manifest-v2.15.0.json').read_text())['ml_runtime']; assert m['trusted_model_artifacts'] is True; assert m['client_supplied_serialized_models_allowed'] is False; assert m['arbitrary_code_execution'] is False
