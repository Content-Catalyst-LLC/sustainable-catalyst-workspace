from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app import session_auth,config,research_session_introspection as service
from app.research_introspection_entry import app
from app.research_bridge_proof import request_proof, verify_response


def signed_request(token,project_id=None):
    payload={'schema_version':'rh-prod-05.1/1.0','session_token':token,'project_id':project_id}
    nonce='c'*64  # Fixed synthetic nonce only in fixture; real Research uses secrets.token_hex.
    return payload,{'X-SC-Request-Nonce':nonce,'X-SC-Request-Proof':request_proof('s'*64,nonce,payload)}


@pytest.fixture
def authority(monkeypatch,tmp_path):
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    with engine.begin() as c:
        c.execute(text('CREATE TABLE workspace_revoked_sessions(token_fingerprint varchar(64) PRIMARY KEY,user_key varchar(128),expires_at timestamp,revoked_at timestamp)'))
        c.execute(text('CREATE TABLE workspace_project_heads(user_key varchar(128),project_id varchar(160),PRIMARY KEY(user_key,project_id))'))
        c.execute(text("INSERT INTO workspace_project_heads VALUES ('owner-a','a'),('owner-b','b')"))
    key=tmp_path/'service-key';key.write_text('s'*64)
    settings=SimpleNamespace(session_signing_secret='synthetic-session-signing-key',service_token='',session_cookie_name='sc_workspace_session',session_issuer='workspace',session_audience='workspace-origin',session_ttl_seconds=600,session_revocation_enforced=True,cors_allowed_origins='https://workspace.test',research_introspection_token='',research_introspection_token_file=str(key))
    monkeypatch.setattr(config,'get_settings',lambda:settings)
    monkeypatch.setattr(session_auth,'get_settings',lambda:settings)
    monkeypatch.setattr(session_auth,'session_scope',lambda:Session(engine))
    monkeypatch.setattr(service,'session_scope',lambda:Session(engine))
    return TestClient(app),session_auth.issue_session_token('owner-a'),engine


def test_project_membership_is_authoritative_and_owner_scoped(authority):
    client,token,engine=authority
    payload,headers=signed_request(token,'a')
    good=client.post('/internal/v1/workspace/session/introspect',headers=headers,json=payload)
    assert good.status_code==200
    assert verify_response('s'*64,headers['X-SC-Request-Nonce'],good.json(),good.headers.get('X-SC-Response-Proof'))
    assert good.json()['authorized_projects']==['a']
    assert 'owner_scope' not in good.json()
    bad_payload,bad_headers=signed_request(token,'b')
    bad=client.post('/internal/v1/workspace/session/introspect',headers=bad_headers,json=bad_payload)
    assert bad.status_code==404
    assert bad.headers['cache-control']=='no-store'
    assert client.post('/internal/v1/workspace/session/introspect',headers=headers,json=dict(payload,owner_scope='owner-b')).status_code==422
    # Grant replacement cannot be hidden behind a valid proof for the original request.
    assert client.post('/internal/v1/workspace/session/introspect',headers=headers,json=dict(payload,project_id='b')).status_code==401


def test_revocation_and_credentials_fail_closed(authority):
    client,token,engine=authority
    path='/internal/v1/workspace/session/introspect'
    assert client.post(path,json={'session_token':token}).status_code==401
    valid,h=signed_request(token)
    assert client.post(path,headers={'X-SC-Request-Nonce':h['X-SC-Request-Nonce'],
                                     'X-SC-Request-Proof':'0'*64},json=valid).status_code==401
    from app.session_revocation import revoke_session
    import time
    with Session(engine) as s:
        revoke_session(s,token,subject='owner-a',expires_at=int(time.time())+600);s.commit()
    assert client.post(path,headers=h,json=valid).status_code==401


def test_private_entry_has_no_public_surface_and_bounded_body(authority):
    client,token,engine=authority
    assert client.get('/openapi.json').status_code==404
    assert client.get('/v1/session').status_code==404
    assert client.get('/internal/v1/workspace/session/introspect').status_code==405
    assert client.post('/internal/v1/workspace/session/introspect',content='x'*13000,headers={'content-type':'application/json'}).status_code==413


def test_rhpub01a_large_portfolio_uses_exact_authoritative_project_scope(authority):
    """A selected publication parent project works without enumerating >100 grants."""
    client,token,engine=authority
    with Session(engine) as s:
        s.execute(text("INSERT INTO workspace_project_heads(user_key,project_id) VALUES "+
                       ",".join("('owner-a','extra-"+str(n)+"')" for n in range(115))))
        s.commit()
    whole,h=signed_request(token)
    bounded=client.post('/internal/v1/workspace/session/introspect',headers=h,json=whole)
    assert bounded.status_code==409
    scoped,scoped_headers=signed_request(token,'a')
    good=client.post('/internal/v1/workspace/session/introspect',
                     headers=scoped_headers,json=scoped)
    assert good.status_code==200
    assert good.json()['authorized_projects']==['a']
    assert verify_response('s'*64,scoped_headers['X-SC-Request-Nonce'],
                           good.json(),good.headers['X-SC-Response-Proof'])
    other,other_headers=signed_request(token,'b')
    assert client.post('/internal/v1/workspace/session/introspect',
                       headers=other_headers,json=other).status_code==404
