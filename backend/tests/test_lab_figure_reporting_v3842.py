import os
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.lab_figure_reporting_v3842 import router

app=FastAPI();app.include_router(router)
client=TestClient(app)
HASH='a'*64
P={'labObjectId':'wexford-demo','labObjectHash':HASH,'labRelease':'0.163.1.3','method':'declared example','assessment':'illustrative','sourceDescription':'Synthetic fixture; not Irish field evidence'}
F={'schemaName':'sc-lab-report-figure/1.0','title':'Illustrative sensitivity','xLabel':'Assumption','yLabel':'Output (unitless)','caption':'Synthetic values only','series':[{'label':'Model demo','points':[{'x':0,'y':1},{'x':1,'y':2}]}],'provenance':P}
S={'schemaName':'sc-lab-report-scene/1.0','title':'Illustrative Wexford time slices','xLabel':'x (m)','yLabel':'y (m)','zLabel':'depth (m)','tLabel':'year','caption':'Schematic projection; not 3D volumetric evidence','frames':[{'time':'2026','points':[{'x':0,'y':1},{'x':1,'y':2}]},{'time':'2027','points':[{'x':0,'y':2},{'x':1,'y':1}]}],'provenance':P}

def test_disabled(monkeypatch):
    monkeypatch.delenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED',raising=False)
    assert client.post('/v1/lab-figure-reporting/v3842/figure/preview',json=F).status_code==503

def test_read_only_figure_and_svg(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED','1')
    path='/v1/lab-figure-reporting/v3842'
    r=client.post(path+'/figure/preview',json=F);assert r.status_code==200
    assert not r.json()['writesPerformed'] and not r.json()['scientificVerificationPerformed']
    assert r.json()['workspaceDigest']==client.post(path+'/figure/preview',json=F).json()['workspaceDigest']
    svg=client.post(path+'/export/svg',json={'kind':'figure','figure':F});assert svg.status_code==200
    assert svg.json()['svg'].startswith('<svg') and HASH in svg.json()['svg']

def test_scene_frame_bounds_and_provenance(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED','1')
    path='/v1/lab-figure-reporting/v3842'
    assert client.post(path+'/scene/preview',json=S).status_code==200
    assert client.post(path+'/export/svg',json={'kind':'scene','scene':S,'frameIndex':1}).status_code==200
    assert client.post(path+'/export/svg',json={'kind':'scene','scene':S,'frameIndex':2}).status_code==422

def test_bad_and_nonfinite_input(monkeypatch):
    monkeypatch.setenv('SC_WORKSPACE_LAB_FIGURE_REPORTING_ENABLED','1')
    broken={**F,'provenance':{**P,'labObjectHash':'not-a-hash'}}
    assert client.post('/v1/lab-figure-reporting/v3842/figure/preview',json=broken).status_code==422
    from fastapi import HTTPException
    from app.lab_figure_reporting_v3842 import Figure, _result
    broken2={**F,'series':[{'label':'broken','points':[{'x':0,'y':float('inf')}]}]}
    try:
        _result('figure',Figure.model_validate(broken2))
    except HTTPException as exc:
        assert exc.status_code==422
    else:
        assert False, 'Nonfinite values must be rejected'
