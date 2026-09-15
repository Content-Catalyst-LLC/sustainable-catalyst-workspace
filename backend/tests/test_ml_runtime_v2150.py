from pathlib import Path
import importlib.util
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]

def test_ml_health_and_linear_fit(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_ML_RUNTIME_TOKEN','secret')
    spec=importlib.util.spec_from_file_location('mlsvc',ROOT/'ml-runtime/service.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    rows=[{'x':i,'y':3*i-2} for i in range(1,25)]
    env={'schema':'sc-workspace-polyglot-execution-envelope/1.0','language':'ml','operation':'workspace.ml.linear-regression','payload':{'rows':rows,'target':'y','features':['x'],'seed':9},'arbitraryCodeExecution':False}
    with TestClient(m.app) as c:
        h=c.get('/health'); assert h.status_code==200 and len(h.json()['operations'])==8
        r=c.post('/v1/execute',json=env,headers={'Authorization':'Bearer secret'})
    assert r.status_code==200; assert r.json()['result']['metrics']['r2']>.999

def test_client_serialized_models_rejected(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_ML_RUNTIME_TOKEN','secret')
    spec=importlib.util.spec_from_file_location('mlsvc2',ROOT/'ml-runtime/service.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    env={'schema':'sc-workspace-polyglot-execution-envelope/1.0','language':'ml','operation':'workspace.ml.predict','payload':{'rows':[{'x':1}],'joblibBase64':'abc'},'arbitraryCodeExecution':False}
    with TestClient(m.app) as c: r=c.post('/v1/execute',json=env,headers={'Authorization':'Bearer secret'})
    assert r.status_code==400
