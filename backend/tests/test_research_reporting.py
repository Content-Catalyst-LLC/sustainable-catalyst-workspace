"""Private reporting integration; fixtures are synthetic, never Wexford claims."""
import base64
from copy import deepcopy
import hashlib
import json
import shutil
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from test_wxr_private_projects import env, ORIGIN, ROOT
from test_lab_live_figure_acceptance_v3844 import lab_response, BASE
from app import research_reporting as reporting, repository, object_store, session_auth

REPORTING = '/v1/private-research/reporting-studio'

@pytest.fixture
def setup(env, monkeypatch):
    client, engine, settings = env
    monkeypatch.setenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED','1')
    monkeypatch.setattr(reporting,'session_scope',lambda: Session(engine,expire_on_commit=False))
    client.app.include_router(reporting.router)
    pid=client.post(ROOT,json={'title':'Isolated reporting proof'},headers=ORIGIN).json()['projectId']
    return client,engine,settings,pid


def stage(setup, obj=None):
    client,engine,settings,pid=setup
    obj = lab_response({'mode':'ecdf','samples':BASE['samples'],'title':'Synthetic ECDF','x_label':'Unitless'}) if obj is None else obj
    raw=json.dumps(obj,ensure_ascii=False).encode()
    response=client.post(f'{ROOT}/{pid}/files',json={'filename':'lab-export.json','contentBase64':base64.b64encode(raw).decode()},headers=ORIGIN)
    assert response.status_code==201,response.text
    source=response.json()
    ref={'artifact_id':source['artifactId'],'sha256':source['sha256'],'source_revision':source['revision'],
         'expected_project_revision':1,'dataset_refs':['synthetic:unitless'],
         'computation_refs':['fixture:ecdf'],'evidence_refs':['synthetic:no-field-evidence'],
         'rights_ref':'Synthetic test only','reproduction':'Run this fixture; not Wexford data.',
         'display':{'color':'#175a3b','line_width':3,'frame_index':0}}
    return ref,raw


def save(client,pid,ref):
    r=client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN)
    assert r.status_code==201,r.text
    return r.json()['report']


def url(pid,report):
    return f"{REPORTING}/projects/{pid}/revisions/{report['revision_id']}/reports/{report['asset_id']}"


def test_reference_display_revision_and_source_immutability(setup):
    client,engine,_,pid=setup
    ref,raw=stage(setup)
    preview=client.post(f'{REPORTING}/projects/{pid}/preview',json=ref,headers=ORIGIN)
    assert preview.status_code==200,preview.text
    assert '#175a3b' in preview.json()['svg']
    assert preview.json()['source']['source_fingerprint_verified'] is True
    report=save(client,pid,ref)
    assert report['revision_id']=='2'
    assert report['fifth_dimension']['availability']=='undeclared'
    assert report['reference']['evidence_refs']==ref['evidence_refs']
    assert report['provenance_verification']['remote_origin_authenticated'] is False
    changed=deepcopy(ref);changed['expected_project_revision']=2;changed['display']['color']='#ab182b'
    second=save(client,pid,changed)
    first=client.get(url(pid,report));later=client.get(url(pid,second))
    assert '#175a3b' in first.json()['view']['svg']
    assert '#ab182b' in later.json()['view']['svg']
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==409
    assert client.get(f"{ROOT}/{pid}/files/{ref['artifact_id']}/download").content==raw
    with Session(engine) as db:
        assert len(repository.list_project_revisions(db,'alice',pid))==3
        assert object_store.get_artifact(db,'alice',ref['artifact_id']).revision==1


def test_guards_and_failure_leave_revision_unchanged(setup,monkeypatch):
    client,engine,_,pid=setup
    ref,_=stage(setup)
    for patch,status in [({'sha256':'0'*64},409),({'artifact_id':'missing'},404),({'source_revision':2},409),({'display':{'color':'url(javascript:bad)'}},422)]:
        response=client.post(f'{REPORTING}/projects/{pid}/reports',json={**ref,**patch},headers=ORIGIN)
        assert response.status_code==status,response.text
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref).status_code==403
    with Session(engine) as db:
        assert repository.get_project(db,'alice',pid).revision==1
    second=client.post(ROOT,json={'title':'Other project'},headers=ORIGIN).json()['projectId']
    assert client.post(f'{REPORTING}/projects/{second}/reports',json=ref,headers=ORIGIN).status_code==404
    report=save(client,pid,ref)
    client.cookies.clear()
    assert client.get(REPORTING).status_code==401
    assert client.get(url(pid,report)).status_code==401
    client.cookies.set('sc_workspace_session',session_auth.issue_session_token('bob'))
    assert client.get(url(pid,report)).status_code==404
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==404
    monkeypatch.delenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED')
    assert client.get(REPORTING).status_code==503


@pytest.mark.parametrize('obj',[{'schema':'unsupported'}, {'schema':'sc-lab-advanced-statistical-figure/0.115.0','fingerprint':'0'*64},[1,2]])
def test_invalid_source_rejected(setup,obj):
    client,engine,_,pid=setup
    ref,_=stage(setup,obj)
    r=client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN)
    assert r.status_code==422,r.text
    with Session(engine) as db: assert repository.get_project(db,'alice',pid).revision==1


def test_commit_failure_rolls_back(setup,monkeypatch):
    client,engine,_,pid=setup
    ref,_=stage(setup)
    def fail_commit(self):
        self.flush()  # exercise rollback after SQL writes, before durable commit
        raise RuntimeError('injected persistence failure')
    monkeypatch.setattr(Session,'commit',fail_commit)
    with pytest.raises(RuntimeError):
        client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN)
    with Session(engine) as db:
        assert repository.get_project(db,'alice',pid).revision==1
        assert len(repository.list_project_revisions(db,'alice',pid))==1


def test_restored_database_and_objects_reopen(setup,monkeypatch,tmp_path):
    client,engine,settings,pid=setup
    ref,raw=stage(setup);report=save(client,pid,ref)
    original=client.get(url(pid,report)).json()
    backup=tmp_path/'restored.sqlite'
    with sqlite3.connect(engine.url.database) as src,sqlite3.connect(backup) as dest:src.backup(dest)
    restored_blobs=tmp_path/'restored-blobs'
    shutil.copytree(settings.object_storage_root,restored_blobs)
    engine.dispose()
    restored=create_engine('sqlite:///'+str(backup),connect_args={'check_same_thread':False})
    monkeypatch.setattr(reporting,'session_scope',lambda: Session(restored,expire_on_commit=False))
    settings.object_storage_root=str(restored_blobs)
    app=FastAPI();app.include_router(reporting.router)
    with TestClient(app,base_url='https://workspace.sustainablecatalyst.com') as reopened:
        reopened.cookies.set('sc_workspace_session',session_auth.issue_session_token('alice'))
        assert reopened.get(url(pid,report)).json()==original
        reopened.cookies.clear();reopened.cookies.set('sc_workspace_session',session_auth.issue_session_token('bob'))
        assert reopened.get(url(pid,report)).status_code==404
    with Session(restored) as db:
        artifact=object_store.get_artifact(db,'alice',ref['artifact_id'])
        assert object_store.read_artifact_content(artifact)==raw
        path=object_store._path_for_key(artifact.storage_key)
        path.write_bytes(b'tampered')
    with TestClient(app,base_url='https://workspace.sustainablecatalyst.com') as reopened:
        reopened.cookies.set('sc_workspace_session',session_auth.issue_session_token('alice'))
        assert reopened.get(url(pid,report)).status_code==503  # native blob integrity guard
    restored.dispose()


def test_saved_lab_scene_is_preserved_without_fake_5d(setup):
    client,_,_,pid=setup
    original={'schema':reporting.LAB_REVISION,'id':'revision:1','assetId':'lab:1',
        'revision':1,'scene':{'sceneState':{'model':'logistic-growth','w':0.25}},
        'provenance':{'source':'synthetic'},'revisionHash':'lab-declared-hash'}
    ref,raw=stage(setup,original)
    report=save(client,pid,ref)
    d=client.get(url(pid,report)).json()
    assert d['view']['svg'] is None
    assert d['report']['source']['source_identity']['revision_id']=='revision:1'
    assert d['report']['source']['source_provenance']==original['provenance']
    assert client.get(f"{ROOT}/{pid}/files/{ref['artifact_id']}/download").content==raw


def test_ui_private_csp_and_same_origin(setup):
    client,_,_,_=setup
    r=client.get(REPORTING)
    assert r.status_code==200
    assert '2580 px wide' in r.text
    assert 'script-src \'sha256-' in r.headers['content-security-policy']
    assert 'connect-src \'self\'' in r.headers['content-security-policy']
    assert r.headers['cache-control']=='private, no-store'


def math_object(latex='x^{2}'):
    value={'schema':'sc-workbench-math-object/1.0','version':'5.1.0','kind':'expression',
           'operation':'parse','source':'x**2','exactText':'x**2','decimalText':'x**2',
           'latex':latex,'freeSymbols':['x'],'precision':15,
           'arbitraryCodeExecutionAuthorized':False,'pythonEvalAuthorized':False}
    value['mathObjectHash']=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    return value


def add_math_source(client,pid,obj):
    raw=json.dumps(obj).encode()
    r=client.post(f'{ROOT}/{pid}/files',json={'filename':'workbench-math.json','contentBase64':base64.b64encode(raw).decode()},headers=ORIGIN)
    assert r.status_code==201,r.text
    item=r.json()
    return {'artifact_id':item['artifactId'],'sha256':item['sha256'],'source_revision':1,
            'execution_ref':'synthetic:unit-test-not-attested','field':'latex'}


def test_bound_equation_table_exact_precision_and_parameter_inspection(setup):
    client,_,_,pid=setup
    ref,raw=stage(setup)
    binding=add_math_source(client,pid,math_object())
    ref['composition']={'equations':[{'latex':'x^{2}','alt_text':'x squared','binding':binding}],
        'table':{'title':'Source results, not measured data','columns':[{'label':'Value','unit':'unitless','definition':'Immutable expression','significant_figures':15}],
          'rows':[[{'binding':{**binding,'field':'exactText'},'uncertainty':'not quantified','citations':['Synthetic fixture']}]]},
        'method_notes':'No evaluation is performed by Reporting Studio.','source_citations':['Unit test only']}
    report=save(client,pid,ref)
    d=client.get(url(pid,report)).json()
    assert 'x squared' in d['view']['svg'] and '<path' in d['view']['svg']
    assert d['report']['execution_bindings'][0]['freeSymbols']==['x']
    assert d['report']['execution_bindings'][0]['precision']==15
    assert d['report']['execution_bindings'][0]['execution_ref_attested'] is False
    assert d['report']['reference']['composition']['table']['rows'][0][0]['binding']['field']=='exactText'
    ref['expected_project_revision']=2
    ref['composition']['equations'][0]['latex']='x^{3}'
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==409


@pytest.mark.parametrize('latex',[r'\frac{a}{b}',r'\begin{pmatrix}1&2\\3&4\end{pmatrix}',r'\begin{aligned}y&=mx+b\\z&=y^2\end{aligned}'])
def test_latex_base_ams_and_inline(latex):
    from app.reporting_composition import render_math
    for mode in ('inline','display'):
        result=render_math(latex,mode)
        assert 'viewBox' in result.attrib
        assert any(n.tag.endswith('path') for n in result.iter())


@pytest.mark.parametrize('latex',[r'\href{https://example.com}{x}',r'\require{html}',r'\def\x{bad}\x',r'\input{/etc/passwd}',r'\unknowncommand{broken}'])
def test_math_unsafe_or_invalid_commands_rejected(latex):
    from app.reporting_composition import render_math
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as caught:render_math(latex,'display')
    assert caught.value.status_code==422


def test_binding_forgery_and_foreign_project_fail_closed(setup):
    client,_,_,pid=setup
    ref,_=stage(setup)
    forged=math_object();forged['decimalText']='fabricated result'
    binding=add_math_source(client,pid,forged)
    ref['composition']={'equations':[{'latex':'x^{2}','alt_text':'x squared','binding':binding}]}
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==409
    ref['composition']['equations'][0]['binding']['artifact_id']='foreign-artifact'
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==404


def test_tables_never_accept_measured_classification_or_implicit_computation(setup):
    client,_,_,pid=setup
    ref,_=stage(setup)
    ref['composition']={'table':{'title':'Unverified inputs','columns':[{'label':'C','unit':'t','definition':'Example'}],
        'rows':[[{'value':'1.2300','uncertainty':'unknown','measured':True}]]}}
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422
    del ref['composition']['table']['rows'][0][0]['measured']
    ref['composition']['table']['rows'][0][0]['binding']={'artifact_id':'missing','sha256':'0'*64,'source_revision':1,'execution_ref':'run','field':'decimalText'}
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422


def heatmap_object():
    return {'schema':'sc-lab-scientific-visualization/1.0','kind':'heatmap','title':'Synthetic matrix',
        'description':'Test only; no Wexford results','xLabel':'x','yLabel':'y','xValues':[1,2],'yValues':[3,4],
        'cells':[{'x':1,'y':3,'z':-1,'xIndex':0,'yIndex':0},{'x':2,'y':4,'z':1,'xIndex':1,'yIndex':1}]}


def test_existing_lab_heatmap_render_scale_and_masked_cells(setup):
    client,_,_,pid=setup
    ref,_=stage(setup,heatmap_object());ref['heatmap_unit']='unitless';ref['evidence_classification']='design-sensitivity'
    ref['display']['palette']='diverging';ref['display']['color_domain']=[-1,1]
    report=save(client,pid,ref)
    view=client.get(url(pid,report)).json()['view']
    assert 'data-sve-version="0.44.0"' in view['svg']
    assert view['source']['source_provenance']['missing_cells']==2
    assert '#2166ac' in view['svg'] and '#b2182b' in view['svg']
    assert 'unitless' in view['svg']
    assert 'design-sensitivity' in view['svg']
    assert view['source_sha256']==ref['sha256']


@pytest.mark.parametrize('patch',[{'xValues':[1,1]}, {'cells':[{'x':1,'y':3,'z':1,'xIndex':4,'yIndex':0}]},
    {'cells':[{'x':2,'y':3,'z':1,'xIndex':0,'yIndex':0}]},
    {'cells':[{'x':1,'y':3,'z':1,'xIndex':0,'yIndex':0}]*2}])
def test_invalid_heatmap_geometry_rejected(setup,patch):
    client,_,_,pid=setup
    ref,_=stage(setup,{**heatmap_object(),**patch});ref['heatmap_unit']='mm'
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422


def test_heatmap_units_and_color_clipping_fail_closed(setup):
    client,_,_,pid=setup
    ref,_=stage(setup,heatmap_object())
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422
    ref['heatmap_unit']='mm';ref['display']['color_domain']=[0,1]
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422


def test_pdf_export_saved_revision_deterministic_and_private(setup):
    pytest.importorskip('svglib')
    client,_,_,pid=setup
    ref,_=stage(setup);report=save(client,pid,ref)
    first=client.get(url(pid,report)+'/export.pdf')
    assert first.status_code==200,first.text
    assert first.content.startswith(b'%PDF-')
    assert first.content==client.get(url(pid,report)+'/export.pdf').content
    assert first.headers['x-research-sha256']==ref['sha256']
    client.cookies.clear()
    assert client.get(url(pid,report)+'/export.pdf').status_code==401


def test_historical_snapshot_does_not_recompute_after_renderer_change(setup,monkeypatch):
    client,_,_,pid=setup
    ref,_=stage(setup);report=save(client,pid,ref)
    original=client.get(url(pid,report)).json()['view']
    monkeypatch.setattr(reporting,'_view',lambda *_: (_ for _ in ()).throw(RuntimeError('renderer changed')))
    assert client.get(url(pid,report)).json()['view']==original


def test_log_heatmap_scale_rejects_nonpositive_values(setup):
    client,_,_,pid=setup
    ref,_=stage(setup,heatmap_object());ref['heatmap_unit']='unitless';ref['display']['color_transform']='log10'
    assert client.post(f'{REPORTING}/projects/{pid}/reports',json=ref,headers=ORIGIN).status_code==422


def test_saved_reference_matches_versioned_scientific_contract(setup):
    import jsonschema
    from pathlib import Path
    client,_,_,pid=setup
    ref,_=stage(setup);report=save(client,pid,ref)
    contract=Path(__file__).resolve().parents[2]/'schemas/sc-research-visual-asset-1.0.schema.json'
    jsonschema.Draft202012Validator(json.loads(contract.read_text())).validate(report)
