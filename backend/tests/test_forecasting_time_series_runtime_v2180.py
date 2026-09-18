from pathlib import Path
import importlib.util, os
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
def _load():
    os.environ['SC_WORKSPACE_FORECAST_RUNTIME_TOKEN']='test-token'
    spec=importlib.util.spec_from_file_location('sc_forecast_service',ROOT/'forecast-runtime'/'service.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
def test_registry_health():
    d=TestClient(_load().app).get('/health').json(); assert d['ok'] and d['version']=='2.18.0' and len(d['operations'])==8 and d['arbitraryCodeExecution'] is False
def test_naive_and_linear_trend():
    c=TestClient(_load().app); h={'Authorization':'Bearer test-token'}; values=list(range(10,20)); env={'operation':'workspace.forecast.naive','payload':{'values':values,'horizon':3}}
    assert c.post('/v1/execute',headers=h,json=env).json()['result']['forecast']==[19.0,19.0,19.0]
    env['operation']='workspace.forecast.linear-trend'; f=c.post('/v1/execute',headers=h,json=env).json()['result']['forecast']; assert len(f)==3 and abs(f[0]-20)<1e-6
def test_backtest_and_evaluate():
    c=TestClient(_load().app); h={'Authorization':'Bearer test-token'}; values=[float(i) for i in range(1,25)]
    d=c.post('/v1/execute',headers=h,json={'operation':'workspace.forecast.backtest','payload':{'values':values,'modelType':'linear-trend','testPoints':4}}).json()['result']; assert d['testPoints']==4 and d['metrics']['rmse']<1e-6
    d=c.post('/v1/execute',headers=h,json={'operation':'workspace.forecast.evaluate','payload':{'actual':[1,2,3],'predicted':[1,2,4]}}).json()['result']; assert 'mae' in d['metrics']

def test_all_registered_direct_forecast_models_execute():
    c=TestClient(_load().app); h={'Authorization':'Bearer test-token'}
    values=[10,12,11,13,12,14,13,15,14,16,15,17,16,18,17,19,18,20,19,21,20,22,21,23]
    cases=[
        ('workspace.forecast.naive',{}),
        ('workspace.forecast.seasonal-naive',{'seasonalPeriod':4}),
        ('workspace.forecast.linear-trend',{}),
        ('workspace.forecast.exponential-smoothing',{'alpha':0.3}),
        ('workspace.forecast.holt-winters',{'seasonalPeriod':4,'trend':'add','seasonal':'add'}),
        ('workspace.forecast.arima',{'order':[1,1,0]}),
    ]
    for op,extra in cases:
        payload={'values':values,'horizon':4,**extra}
        r=c.post('/v1/execute',headers=h,json={'operation':op,'payload':payload})
        assert r.status_code==200,(op,r.text)
        result=r.json()['result']; assert len(result['forecast'])==4 and result['datasetFingerprint']

def test_auth_and_registry_bounds():
    c=TestClient(_load().app); assert c.post('/v1/execute',json={'operation':'workspace.forecast.naive','payload':{'values':[1,2,3,4,5,6]}}).status_code==401; assert c.post('/v1/execute',headers={'Authorization':'Bearer test-token'},json={'operation':'workspace.forecast.python','payload':{}}).status_code==400
def test_repository_contract():
    assert (ROOT/'migrations'/'018_forecasting_time_series_runtime.sql').exists(); compose=(ROOT/'docker-compose.example.yml').read_text(); assert 'sc-workspace-forecast-runtime' in compose and 'internal: true' in compose; poly=(ROOT/'app'/'polyglot.py').read_text(); assert 'python-statsmodels-forecasting' in poly and 'workspace.forecast.arima' in poly
