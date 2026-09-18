import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
def load():
    spec=importlib.util.spec_from_file_location('sc_uncertainty_service',ROOT/'uncertainty-runtime'/'service.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_uncertainty_runtime_health_and_registered_ops():
    c=TestClient(load().app); h=c.get('/health').json(); assert h['ok'] is True and h['version']=='2.20.0' and len(h['operations'])==8 and h['arbitraryCodeExecution'] is False

def test_seeded_monte_carlo_is_reproducible():
    c=TestClient(load().app); payload={'terms':[{'name':'x','coefficient':2,'distribution':{'kind':'normal','mean':3,'sd':1}}],'draws':1200,'seed':23}
    a=c.post('/v1/execute',json={'operation':'workspace.uncertainty.monte-carlo-weighted-sum','payload':payload}).json()['result']
    b=c.post('/v1/execute',json={'operation':'workspace.uncertainty.monte-carlo-weighted-sum','payload':payload}).json()['result']
    assert a['summary']['mean']==b['summary']['mean'] and a['draws']==1200 and a['seed']==23

def test_bootstrap_interval_and_latin_hypercube():
    c=TestClient(load().app)
    r=c.post('/v1/execute',json={'operation':'workspace.uncertainty.bootstrap-interval','payload':{'values':[1,2,3,4,5,6],'statistic':'mean','draws':1000,'seed':7}}); assert r.status_code==200; d=r.json()['result']; assert d['interval']['lower'] < d['estimate'] < d['interval']['upper']
    r=c.post('/v1/execute',json={'operation':'workspace.uncertainty.latin-hypercube','payload':{'variables':[{'name':'a','min':0,'max':1},{'name':'b','min':10,'max':20}],'samples':20,'seed':9}}); assert r.status_code==200; d=r.json()['result']; assert len(d['rows'])==20 and len(d['rows'][0])==2

def test_rank_sensitivity_identifies_monotonic_driver():
    c=TestClient(load().app); rows=[{'x':i,'z':(-1)**i,'y':3*i+1} for i in range(1,30)]
    r=c.post('/v1/execute',json={'operation':'workspace.uncertainty.rank-correlation-sensitivity','payload':{'rows':rows,'outcome':'y','features':['x','z']}}); assert r.status_code==200; s=r.json()['result']['sensitivity']['scores']; assert s[0]['feature']=='x' and s[0]['spearman']>0.99

def test_variance_contribution_and_scenario_envelope():
    c=TestClient(load().app)
    r=c.post('/v1/execute',json={'operation':'workspace.uncertainty.variance-contribution-linear','payload':{'terms':[{'name':'a','coefficient':2,'sd':3},{'name':'b','coefficient':1,'sd':1}]}}); assert r.status_code==200; assert r.json()['result']['summary']['dominantTerm']=='a'
    r=c.post('/v1/execute',json={'operation':'workspace.uncertainty.scenario-envelope','payload':{'scenarios':[{'name':'low','value':2},{'name':'high','value':9},{'name':'mid','value':5}]}}); assert r.status_code==200; assert r.json()['result']['minimumScenario']['name']=='low' and r.json()['result']['maximumScenario']['name']=='high'

def test_unregistered_operation_rejected():
    c=TestClient(load().app); assert c.post('/v1/execute',json={'operation':'python.exec','payload':{}}).status_code==400
