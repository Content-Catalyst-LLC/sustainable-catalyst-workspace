"""All identities, grants and catalogs in these tests are synthetic and local."""
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import session_auth, wxr_recovery_review as review

SUBJECT='synthetic-verified-owner'

@pytest.fixture
def setup(tmp_path,monkeypatch):
    settings=SimpleNamespace(session_signing_secret='synthetic-test-secret-never-production',service_token='',session_cookie_name='synthetic_session',session_issuer='synthetic-test',session_audience='workspace.sustainablecatalyst.com',session_ttl_seconds=300)
    monkeypatch.setattr(session_auth,'get_settings',lambda:settings)
    catalog=tmp_path/'catalog.json'
    catalog.write_text(json.dumps({'projects':[{'project_id':'historical-project','name':'<script>untrusted</script>','owner_fingerprint':'historical-owner','curation_status':'unreviewed','private_internal_field':'not-exported'}],'calculations':[{'record_id':'historical-calculation','project_id':'historical-project'}],'artifacts':[{'artifact_id':'artifact-one','sha256':'a'*64,'relative_path':'research.pdf','original_source_path':'/private/path/not-exported'},{'artifact_id':'artifact-two','sha256':'a'*64}]}))
    now=datetime.now(timezone.utc)
    grant={'schema':review.SCHEMA,'scope':review.SCOPE,'status':'approved','subject_sha256':hashlib.sha256(SUBJECT.encode()).hexdigest(),'catalog_sha256':hashlib.sha256(catalog.read_bytes()).hexdigest(),'approved_by':'synthetic-human-reviewer','approval_reference':'synthetic-approval','issued_at':(now-timedelta(seconds=2)).isoformat(),'expires_at':(now+timedelta(hours=1)).isoformat()}
    path=tmp_path/'grant.json'
    def save():
        path.write_text(json.dumps(grant));path.chmod(0o600)
    save()
    monkeypatch.setenv('WXR_REVIEW_GRANT_FILE',str(path))
    monkeypatch.setenv('WXR_REVIEW_CATALOG_FILE',str(catalog))
    app=FastAPI();app.include_router(review.router)
    client=TestClient(app,base_url='https://workspace.sustainablecatalyst.com')
    client.cookies.set(settings.session_cookie_name,session_auth.issue_session_token(SUBJECT))
    return client,grant,path,catalog,save,settings

BASE='/v1/private-research/wexford-recovery'


def test_granted_inventory_is_read_only_and_preserves_original_identity(setup):
    c,g,p,cat,save,s=setup
    before=cat.read_bytes()
    response=c.get(BASE+'/catalog');assert response.status_code==200
    d=response.json();assert d['summary']=={'projects':1,'calculations':1,'artifact_occurrences':2,'unique_artifacts':1}
    assert d['projects'][0]['owner_fingerprint']=='historical-owner'
    assert d['historical_ownership']=='UNRESOLVED' and d['scientific_validity']=='NOT_ASSESSED'
    assert d['staging']=='NOT_PERFORMED' and d['publication']=='DISABLED'
    assert '/private/path' not in response.text and 'private_internal_field' not in response.text
    assert cat.read_bytes()==before
    assert response.headers['cache-control']=='private, no-store'
    assert c.post(BASE+'/catalog').status_code==405
    assert c.post(BASE+'/initialize').status_code==404

@pytest.mark.parametrize('path',['/ui','/catalog','/access-status'])
def test_anonymous_denial_all_surfaces(setup,path):
    c,*_=setup;c.cookies.clear()
    assert c.get(BASE+path).status_code==401

@pytest.mark.parametrize('path',['/ui','/catalog','/access-status'])
def test_other_genuinely_signed_local_subject_is_denied(setup,path):
    c,g,p,cat,save,s=setup
    c.cookies.set(s.session_cookie_name,session_auth.issue_session_token('synthetic-other-account'))
    assert c.get(BASE+path).status_code==403


def test_forged_headers_and_invalid_cookie_do_not_establish_identity(setup):
    c,*_=setup;c.cookies.clear()
    assert c.get(BASE+'/catalog',headers={'X-SC-User-ID':SUBJECT,'Authorization':'Bearer invalid'}).status_code==401
    c.cookies.set('synthetic_session','forged.cookie')
    assert c.get(BASE+'/catalog').status_code==401

@pytest.mark.parametrize('mutation',[
    {'scope':'wexford-recovery:stage-initialize'}, {'status':'pending'}, {'schema':'other'},
    {'approved_by':''}, {'approval_reference':''}, {'catalog_sha256':'z'*64},
    {'expires_at':(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()},
    {'expires_at':(datetime.now(timezone.utc)+timedelta(days=2)).isoformat()},
    {'issued_at':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()},
    {'expires_at':'invalid'}, {'expires_at':'2030-01-01T00:00:00'},
])
def test_invalid_or_expired_grants_fail_closed(setup,mutation):
    c,g,p,cat,save,s=setup;g.update(mutation);save()
    assert c.get(BASE+'/catalog').status_code==403


def test_extra_grant_fields_are_not_authority(setup):
    c,g,p,cat,save,s=setup;g['owner_verified']=True;save()
    assert c.get(BASE+'/catalog').status_code==403


def test_missing_grant_config_denied(setup,monkeypatch):
    c,*_=setup;monkeypatch.delenv('WXR_REVIEW_GRANT_FILE')
    assert c.get(BASE+'/catalog').status_code==403


def test_world_readable_or_symlinked_grant_denied(setup):
    c,g,p,cat,save,s=setup;p.chmod(0o644)
    assert c.get(BASE+'/catalog').status_code==403
    p.chmod(0o600);target=p.with_name('target.json');p.rename(target);p.symlink_to(target)
    assert c.get(BASE+'/catalog').status_code==403


def test_changed_catalog_and_symlinks_are_rejected(setup):
    c,g,p,cat,save,s=setup;original=cat.read_bytes();cat.write_bytes(original+b' ')
    assert c.get(BASE+'/catalog').status_code==503
    cat.write_bytes(original);target=cat.with_name('target-catalog.json');cat.rename(target);cat.symlink_to(target)
    assert c.get(BASE+'/catalog').status_code==503


def test_ui_uses_bound_script_and_no_unescaped_catalog_html(setup):
    c,*_=setup;r=c.get(BASE+'/ui');assert r.status_code==200
    assert '<script>untrusted</script>' not in r.text
    assert 'textContent' in r.text
    csp=r.headers['content-security-policy']
    assert "script-src 'sha256-" in csp and "frame-ancestors 'none'" in csp
    assert 'noindex' in r.headers['x-robots-tag']
    assert c.get(BASE+'/access-status').json()['research_access']=='PRIVATE_READ_ONLY'
