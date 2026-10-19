import hashlib
import copy
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.lab_live_figure_acceptance_v3844 import router, accept, _stable, _verify_lab
from app.lab_live_figure_acceptance_v3844 import RequestFigure

app=FastAPI();app.include_router(router)
client=TestClient(app)
BASE={'sourceObjectId':'synthetic-test','sourceFingerprint':'illustrative-reference','title':'Synthetic test ECDF',
      'xLabel':'Input (unitless)','caption':'Synthetic test fixture; not Wexford measurements',
      'units':'unitless','evidenceStatus':'illustrative','samples':[1.0,2.0,3.0,4.0]}

def lab_response(body):
    assert body['mode']=='ecdf' and body['samples']==BASE['samples']
    points=[{'x':x,'y':(i+1)/4} for i,x in enumerate(body['samples'])]
    response={'ok':True,'schema':'sc-lab-advanced-statistical-figure/0.115.0','version':'0.115.0',
              'engine_version':'3.1.0','graphic_type':'ecdf',
              'spec':{'kind':'ecdf','title':body['title'],'axes':{'x':{'label':body['x_label']},'y':{'label':'Cumulative probability'}},
                      'series':[{'label':'ECDF','points':points}], 'bars':[],'bins':[],'boxes':[],'violins':[]},
              'statistical_metadata':{'descriptive':{'n':4}}, 'design_system_version':'0.114.0',
              'boundaries':{'automatic_statistical_inference':False,
                            'automatic_scientific_validity_certification':False,'automatic_truth_determination':False}}
    response['fingerprint']=hashlib.sha256(_stable(response).encode()).hexdigest()
    return response

def test_disabled_and_approval_gate(monkeypatch):
    monkeypatch.delenv('SC_WORKSPACE_LAB_LIVE_V3844_ENABLED',raising=False)
    monkeypatch.delenv('SC_WORKSPACE_LAB_LIVE_EXECUTION_APPROVED',raising=False)
    assert client.post('/v1/lab-publication/v3844/ecdf/accept',json=BASE).status_code==503
    monkeypatch.setenv('SC_WORKSPACE_LAB_LIVE_V3844_ENABLED','1')
    assert client.post('/v1/lab-publication/v3844/ecdf/accept',json=BASE).status_code==503

def test_verified_lab_envelope_and_deterministic_render():
    p=RequestFigure.model_validate(BASE)
    a=accept(p,loader=lab_response);b=accept(p,loader=lab_response)
    assert a==b
    assert a['labResponseIntegrityVerified'] is True and a['labFingerprintVerified'] is True
    assert a['labOriginAuthenticated'] is False and a['scientificVerificationPerformed'] is False
    assert a['writesPerformed'] is False and a['sampleCount']==4
    assert 'Synthetic test ECDF' in a['svg']

def test_reject_forged_fingerprint():
    def forged(body):
        r=lab_response(body);r['spec']['title']='Tampered title';return r
    with pytest.raises(HTTPException) as info:
        accept(RequestFigure.model_validate(BASE),loader=forged)
    assert info.value.status_code==502

def test_malformed_nonfinite_and_unsupported():
    with pytest.raises(HTTPException) as nonfinite:
        accept(RequestFigure.model_validate({**BASE,'samples':[1.0,float('inf')]}),loader=lab_response)
    assert nonfinite.value.status_code==422
    def wrong(body):
        r=lab_response(body);r['schema']='unknown';return r
    with pytest.raises(HTTPException):
        accept(RequestFigure.model_validate(BASE),loader=wrong)
