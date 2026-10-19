import copy
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.lab_publication_adapter_v3843 import router
app=FastAPI();app.include_router(router)
client=TestClient(app)
PATH='/v1/lab-publication/v3843/render/ecdf/svg'
BASE={'labResponse':{'ok':True,'schema':'sc-lab-advanced-statistical-figure/1.0','fingerprint':'synthetic-lab-hash','graphic_type':'distribution', 'spec':{'kind':'ecdf','title':'Synthetic ECDF','axes':{'x':{'label':'Example value'},'y':{'label':'Cumulative probability'}},'series':[{'label':'Illustrative only','points':[{'x':1,'y':0.25},{'x':2,'y':0.75},{'x':3,'y':1.0}]}], 'bars':[], 'bins':[], 'boxes':[], 'violins':[]}},'sourceObjectId':'demo','sourceFingerprint':'declared-synthetic','caption':'Synthetic; not field measurements','evidenceStatus':'illustrative'}
def test_disabled(monkeypatch):
    monkeypatch.delenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED',raising=False)
    assert client.post(PATH,json=BASE).status_code==503

def test_ecdf_determinism_and_disclosures(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED','1')
    a=client.post(PATH,json=BASE); b=client.post(PATH,json=BASE)
    assert a.status_code==200 and a.json()==b.json()
    assert '<svg ' in a.json()['svg'] and 'Synthetic ECDF' in a.json()['svg']
    assert a.json()['scientificVerificationPerformed'] is False
    assert a.json()['labOriginAuthenticated'] is False
    assert a.json()['writesPerformed'] is False

def test_fail_closed_unsupported_and_bad_numbers(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED','1')
    for mutation in ('kind','x','y','bars','fingerprint'):
        p=copy.deepcopy(BASE)
        if mutation=='kind':p['labResponse']['spec']['kind']='histogram'
        if mutation=='x':p['labResponse']['spec']['series'][0]['points'][1]['x']=-10
        if mutation=='y':p['labResponse']['spec']['series'][0]['points'][0]['y']=1.2
        if mutation=='bars':p['labResponse']['spec']['bars']=[{'value':1}]
        if mutation=='fingerprint':p['labResponse']['fingerprint']=''
        assert client.post(PATH,json=p).status_code==422,mutation

def test_xml_escaping(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_PUBLICATION_V3843_ENABLED','1')
    p=copy.deepcopy(BASE);p['labResponse']['spec']['title']='<script>alert(1)</script>'
    r=client.post(PATH,json=p)
    assert r.status_code==200 and '<script>' not in r.json()['svg'] and '&lt;script&gt;' in r.json()['svg']
