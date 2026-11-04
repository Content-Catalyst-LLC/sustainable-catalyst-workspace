"""In-process tests of isolated stage auth contract, not real browser/Contabo acceptance."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import types
from contextlib import contextmanager

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

SRC = Path(__file__).resolve().parents[1] / 'source' / 'pb05_browser_stage.py'
ORIGIN = 'https://localhost:18443'
CODE = 'a' * 64


@pytest.fixture
def stage(monkeypatch):
    monkeypatch.setenv('PB05_STAGE_ENABLED', 'ISOLATED_TEST_ONLY')
    monkeypatch.setenv('SC_WORKSPACE_ENVIRONMENT', 'pb05-isolated')
    monkeypatch.setenv('PB05_STAGE_ORIGIN', ORIGIN)
    monkeypatch.setenv('PB05_STAGE_LOGIN_CODE', CODE)
    monkeypatch.setenv('PB05_STAGE_SECOND_LOGIN_CODE', 'b'*64)
    monkeypatch.setenv('PB05_STAGE_TEST_OTHER_OWNER','pb05-synthetic-owner-otherfixture')
    monkeypatch.setenv('PB05_STAGE_TEST_OWNER', 'pb05-synthetic-owner-fixture')
    pkg = types.ModuleType('app')
    pkg.__path__ = [str(SRC.parent)]
    monkeypatch.setitem(sys.modules, 'app', pkg)
    a = types.ModuleType('app.session_auth')
    a.session_cookie_name = lambda: 'pb05_stage_session'
    a.issue_session_token = lambda subject: 'signed:'+subject
    a.session_payload_from_request = lambda request: (
        {'sub':request.cookies['pb05_stage_session'][7:]}
        if request.cookies.get('pb05_stage_session','').startswith('signed:') else None)
    monkeypatch.setitem(sys.modules, 'app.session_auth', a)
    db = types.ModuleType('app.db')
    @contextmanager
    def session_scope():
        yield object()
    db.session_scope = session_scope
    monkeypatch.setitem(sys.modules, 'app.db', db)
    repo = types.ModuleType('app.repository')
    repo.list_projects = lambda db, owner: ([{'projectId':'research-abc-123', 'title':'PB05 synthetic Wexford & Study'}] if owner == 'pb05-synthetic-owner-fixture' else [])
    monkeypatch.setitem(sys.modules, 'app.repository', repo)
    private = types.ModuleType('app.wxr_private_projects')
    private.router = APIRouter(prefix='/v1/private-research/persistent-projects')
    for i in range(7):
        private.router.add_api_route('/p'+str(i), lambda: {'ok':True}, methods=['GET'])
    monkeypatch.setitem(sys.modules, 'app.wxr_private_projects', private)
    pb04 = types.ModuleType('app.rd014_publication_records')
    pb04.router = APIRouter(prefix='/v1/private-research/persistent-projects')
    for i in range(7):
        pb04.router.add_api_route('/d'+str(i), lambda: {'ok':True}, methods=['GET'])
    pb04._row = lambda db,owner,pid,kind: None
    monkeypatch.setitem(sys.modules, 'app.rd014_publication_records', pb04)
    spec = importlib.util.spec_from_file_location('app.pb05_browser_stage', SRC)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, 'app.pb05_browser_stage', mod)
    spec.loader.exec_module(mod)
    return mod, TestClient(mod.app, base_url=ORIGIN)


def test_staging_status_contains_no_secrets(stage):
    _, client = stage
    r = client.get('/__pb05__/status')
    assert r.status_code == 200
    assert r.json()['mode'] == 'isolated-synthetic-browser'
    assert CODE not in r.text
    assert 'no-store' in r.headers['cache-control']


def test_catalog_not_anonymous(stage):
    _, client = stage
    assert client.get('/__pb05__/catalog').status_code == 401
    assert client.get('/__pb05__/login').status_code == 200


def test_login_requires_strict_origin_and_correct_code(stage):
    _, client = stage
    path = '/__pb05__/login'
    assert client.post(path, data={'code':CODE}, headers={'origin':'https://workspace.sustainablecatalyst.com'}).status_code == 403
    assert client.post(path, data={'code':'bad'}, headers={'origin':ORIGIN}).status_code == 401
    r = client.post(path, data={'code':CODE}, headers={'origin':ORIGIN}, follow_redirects=False)
    assert r.status_code == 303
    cookie = r.headers['set-cookie']
    assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=strict' in cookie
    assert 'Domain=' not in cookie
    assert r.headers['location'] == '/__pb05__/catalog'


def test_login_reopen_catalog_and_logout(stage):
    _, client = stage
    r = client.post('/__pb05__/login', data={'code':CODE}, headers={'origin':ORIGIN}, follow_redirects=True)
    assert r.status_code == 200
    assert 'PB05 synthetic Wexford &amp; Study' in r.text
    assert '/v1/private-research/persistent-projects/research-abc-123/publications/ui' in r.text
    assert client.get('/__pb05__/catalog').status_code == 200
    assert client.post('/__pb05__/logout', headers={'origin':'https://wrong.example'}).status_code == 403
    r2 = client.post('/__pb05__/logout', headers={'origin':ORIGIN}, follow_redirects=False)
    assert r2.status_code == 303
    assert client.get('/__pb05__/catalog').status_code == 401


def test_host_restriction(stage):
    _, client = stage
    assert client.get('/__pb05__/status', headers={'host':'workspace.sustainablecatalyst.com'}).status_code in (400,403)
    assert client.get('/__pb05__/login', headers={'host':'localhost:18444'}).status_code == 403


def test_nonstage_import_fails(monkeypatch):
    monkeypatch.delenv('PB05_STAGE_ENABLED', raising=False)
    spec=importlib.util.spec_from_file_location('app.pb05_inert', SRC)
    module=importlib.util.module_from_spec(spec)
    with pytest.raises(RuntimeError, match='forbidden outside'):
        spec.loader.exec_module(module)


def test_second_synthetic_owner_isolated(stage):
    _, client = stage
    r = client.post('/__pb05__/login', data={'code':'b'*64}, headers={'origin':ORIGIN}, follow_redirects=True)
    assert r.status_code == 200
    assert 'No synthetic projects yet' in r.text
    assert 'research-abc-123' not in r.text
    assert client.cookies.get('pb05_stage_session') == 'signed:pb05-synthetic-owner-otherfixture'


def test_authenticated_receipt_never_leaks_manuscript_or_credentials(stage):
    _,client=stage
    assert client.get('/__pb05__/receipt').status_code == 401
    client.post('/__pb05__/login',data={'code':CODE},headers={'origin':ORIGIN})
    result=client.get('/__pb05__/receipt')
    assert result.status_code==200
    assert result.json()['ownerAlias']=='A'
    assert len(result.json()['projects'][0]['documents'])==2
    assert result.json()['projects'][0]['documents'][0]['saved'] is False
    assert CODE not in result.text
