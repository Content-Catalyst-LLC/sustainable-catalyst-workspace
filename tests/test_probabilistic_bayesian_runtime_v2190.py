import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
def load():
    spec=importlib.util.spec_from_file_location('sc_probability_service',ROOT/'probability-runtime'/'service.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_probability_runtime_health_and_registered_ops():
    c=TestClient(load().app); h=c.get('/health').json(); assert h['ok'] is True and h['version']=='2.19.0' and len(h['operations'])==6 and h['arbitraryCodeExecution'] is False

def test_beta_binomial_update_is_deterministic():
    c=TestClient(load().app); r=c.post('/v1/execute',json={'operation':'workspace.probability.beta-binomial-update','payload':{'alpha':2,'beta':2,'successes':8,'trials':10,'seed':7,'draws':2000}}); assert r.status_code==200; p=r.json()['result']['posterior']; assert p['alpha']==10 and p['beta']==4 and abs(p['mean']-10/14)<1e-12

def test_normal_normal_update():
    c=TestClient(load().app); r=c.post('/v1/execute',json={'operation':'workspace.probability.normal-normal-update','payload':{'priorMean':0,'priorSd':10,'knownSd':2,'observations':[9,10,11]}}); assert r.status_code==200; p=r.json()['result']['posterior']; assert 9.8 < p['mean'] < 10.1 and p['credibleInterval']['lower'] < p['mean'] < p['credibleInterval']['upper']

def test_uncertainty_propagation_is_bounded():
    c=TestClient(load().app); r=c.post('/v1/execute',json={'operation':'workspace.probability.uncertainty-propagate','payload':{'terms':[{'coefficient':2,'mean':3,'sd':1}], 'draws':1000,'seed':11}}); assert r.status_code==200; d=r.json()['result']; assert d['draws']==1000 and d['termCount']==1

def test_unregistered_operation_rejected():
    c=TestClient(load().app); assert c.post('/v1/execute',json={'operation':'python.exec','payload':{}}).status_code==400
