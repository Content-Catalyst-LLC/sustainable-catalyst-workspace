"""Exercise unchanged deployed bridge with synthetic local identity fixtures only."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
settings=SimpleNamespace(session_signing_secret='synthetic-local-test-secret-not-production',service_token='',session_cookie_name='sc_workspace_session',session_issuer='synthetic-test-issuer',session_audience='workspace.sustainablecatalyst.com',session_ttl_seconds=120,token_configured=False)
from app import erw_identity_bridge as bridge, session_auth

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(bridge,'get_settings',lambda: settings)
    monkeypatch.setattr(session_auth,'get_settings',lambda: settings)
    monkeypatch.setattr(bridge,'RATE_DB',str(tmp_path/'rate.sqlite'))
    monkeypatch.setattr(bridge,'ERW_BASE','http://sc-workbench:8088')
    app=FastAPI();app.include_router(bridge.router);app.include_router(session_auth.router)
    with TestClient(app,base_url='https://workspace.sustainablecatalyst.com') as c:yield c

HEADERS={'Origin':'https://workspace.sustainablecatalyst.com','X-WXR-Login':'1'}
CREDS={'username':'synthetic-test-user','password':'synthetic-test-password'}

def upstream(monkeypatch,owner='sc:synthetic-owner'):
    def post(url,payload,headers=None):
        assert url=='http://sc-workbench:8088/erw/v1.2.1/identity/login'
        assert payload==CREDS
        return {'ok':True,'identityId':'sc:synthetic-owner','token':'synthetic-bearer-'+'x'*32}
    def get(url,token):
        assert url=='http://sc-workbench:8088/erw/v1.2.1/identity/me'
        return {'ok':True,'identityId':owner}
    monkeypatch.setattr(bridge,'_post_json',post);monkeypatch.setattr(bridge,'_get_json',get)

def test_verified_upstream_identity_issues_secure_native_cookie(client,monkeypatch):
    upstream(monkeypatch)
    response=client.post('/v1/private-research/auth/login',headers=HEADERS,json=CREDS)
    assert response.status_code==200
    assert response.json()=={'authenticated':True}
    cookie=response.headers['set-cookie'].lower()
    assert all(x in cookie for x in ('secure','httponly','samesite=lax'))
    identity=client.get('/v1/session').json()
    assert identity['authenticated'] is True and identity['subject']=='erw:sc:synthetic-owner'
    assert 'synthetic-bearer' not in response.text

def test_missing_verifier_configuration_fails_closed(client,monkeypatch):
    monkeypatch.setattr(bridge,'ERW_BASE','')
    assert client.post('/v1/private-research/auth/login',headers=HEADERS,json=CREDS).status_code==503

@pytest.mark.parametrize('headers',[{}, {'Origin':'https://attacker.invalid','X-WXR-Login':'1'},{'Origin':HEADERS['Origin']}])
def test_untrusted_origin_or_missing_header_rejected(client,headers):
    assert client.post('/v1/private-research/auth/login',headers=headers,json=CREDS).status_code==403

def test_identity_mismatch_cannot_issue_session(client,monkeypatch):
    upstream(monkeypatch,owner='sc:different-owner')
    response=client.post('/v1/private-research/auth/login',headers=HEADERS,json=CREDS)
    assert response.status_code==401
    assert 'set-cookie' not in response.headers

@pytest.mark.parametrize('profile',[{}, {'ok':False,'identityId':'sc:a'}, {'ok':True,'identityId':'sc:a','anonymous':True},{'ok':True,'identityId':'sc:a','authenticated':False},{'ok':True,'identityId':'bad/subject'},{'ok':True,'identityId':'x'*91},None])
def test_invalid_provider_identity_rejected(profile):
    assert bridge._verified_owner({},profile) is None

def test_forged_browser_identity_headers_are_not_sessions(client):
    result=client.get('/v1/session',headers={'X-SC-User-ID':'sc:forged','Authorization':'Bearer forged'})
    assert result.json()['authenticated'] is False

def test_rate_limit_is_durable_between_calls(client):
    for _ in range(8):bridge._rate_limit('synthetic-ip','synthetic-user')
    with pytest.raises(Exception) as err:bridge._rate_limit('synthetic-ip','synthetic-user')
    assert err.value.status_code==429


def test_reconciled_main_mounts_live_routes_once():
    from app.main import app

    for path, method in (
        ('/v1/private-research/auth/login', 'POST'),
        ('/v1/private-research/wexford-recovery/catalog', 'GET'),
        ('/v1/private-research/wexford-recovery/access-status', 'GET'),
        ('/v1/private-research/wexford-recovery/ui', 'GET'),
        ('/v1/private-research/persistent-projects', 'GET'),
        ('/v1/private-research/persistent-projects', 'POST'),
    ):
        assert len([route for route in app.routes if getattr(route, 'path', None) == path and method in getattr(route, 'methods', set())]) == 1
