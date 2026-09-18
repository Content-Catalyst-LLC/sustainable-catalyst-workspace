import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient

P=Path(__file__).resolve().parents[1]/"optimization-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_workspace_optimization_runtime",P)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
client=TestClient(mod.app)

def test_health_and_registry():
    d=client.get('/health').json(); assert d['ok'] is True; assert d['version']=='2.21.0'; assert len(d['operations'])==8; assert d['arbitraryCodeExecution'] is False

def test_linear_box_exact_minimum():
    payload={"operation":"workspace.optimize.linear-box","payload":{"direction":"minimize","bounds":[{"name":"x","min":0,"max":10},{"name":"y","min":-2,"max":3}],"objective":{"kind":"linear","coefficients":[2,-4],"intercept":1}}}
    r=client.post('/v1/execute',json=payload); assert r.status_code==200; d=r.json()['result']; assert d['bestParameters']=={'x':0.0,'y':3.0}; assert d['bestValue']==-11.0

def test_random_search_seeded_and_bounded():
    body={"operation":"workspace.optimize.random-search","payload":{"direction":"minimize","seed":2210,"samples":1000,"bounds":[{"name":"x","min":-2,"max":2}],"objective":{"kind":"quadratic","linear":[-2],"quadratic":[[2]],"intercept":1}}}
    a=client.post('/v1/execute',json=body).json()['result']; b=client.post('/v1/execute',json=body).json()['result']; assert a==b; assert abs(a['bestParameters']['x']-1)<0.05; assert a['evaluationCount']==1000

def test_grid_limit_rejects_explosion():
    body={"operation":"workspace.optimize.grid-search","payload":{"bounds":[{"name":f"x{i}","min":0,"max":1} for i in range(6)],"pointsPerDimension":41,"objective":{"kind":"linear","coefficients":[1]*6}}}
    assert client.post('/v1/execute',json=body).status_code==400
