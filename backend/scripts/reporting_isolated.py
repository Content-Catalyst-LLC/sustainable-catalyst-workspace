"""RS-MIG-01 loopback-only SQLite/browser acceptance harness, never production.

PYTHONPATH=. python scripts/reporting_isolated.py --state-dir /tmp/rs-mig-proof \
  --seed-export /path/to/verified/lab-export.json
Requires the normal backend test dependencies (pytest/httpx/SQLite compiler).
Its synthetic signed-session owner is NOT an existing real-account acceptance.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import secrets
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
import uvicorn

from app import config, repository, object_store, session_auth, wxr_private_projects, research_reporting
from app.models import Base, ProjectHead, ProjectRevision, ArtifactHead, ArtifactRevision, DomainMutationReceipt

@compiles(JSONB,'sqlite')
def sqlite_json(element,compiler,**kw): return 'JSON'

def build(state_dir):
    state=Path(state_dir).resolve()
    marker=state/'.isolated-reporting-proof'
    if state.exists() and not marker.exists():
        raise RuntimeError('Refusing non-harness state directory')
    state.mkdir(mode=0o700,parents=True,exist_ok=True);marker.touch()
    secret=state/'session-secret'
    if not secret.exists():
        fd=os.open(secret,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(48))
    settings=SimpleNamespace(max_project_bytes=5_000_000,max_account_bytes=20_000_000,
        max_projects_per_account=100,max_artifact_bytes=2_000_000,
        max_artifact_account_bytes=10_000_000,max_artifacts_per_account=100,
        object_storage_root=str(state/'objects'),session_signing_secret=secret.read_text(),
        service_token='',session_cookie_name='sc_workspace_session',session_issuer='isolated-reporting-proof',
        session_audience='workspace.sustainablecatalyst.com',session_ttl_seconds=3600)
    engine=create_engine('sqlite:///'+str(state/'workspace.sqlite'),connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine,tables=[m.__table__ for m in (ProjectHead,ProjectRevision,ArtifactHead,ArtifactRevision,DomainMutationReceipt)])
    for module in (repository,object_store,session_auth,config):module.get_settings=lambda:settings
    for module in (wxr_private_projects,research_reporting):module.session_scope=lambda:Session(engine,expire_on_commit=False)
    os.environ['SC_WORKSPACE_REPORTING_STUDIO_ENABLED']='1'
    app=FastAPI();app.include_router(wxr_private_projects.router);app.include_router(research_reporting.router)
    # Loopback-only synthetic browser bootstrap, never mounted by app.main.
    # Production cookie verification remains unchanged; no real account involved.
    @app.middleware('http')
    async def isolated_origin(request, call_next):
        if request.headers.get('origin') == 'http://127.0.0.1:8079':
            request.scope['headers'] = [(k, b'https://workspace.sustainablecatalyst.com' if k == b'origin' else v)
                                        for k,v in request.scope['headers']]
        return await call_next(request)
    @app.get('/isolated-session')
    def isolated_login_page():
        return HTMLResponse('<h1>Isolated reporting test</h1><p>Synthetic owner; no real account or production service.</p><form method="post"><button>Start synthetic Workspace session</button></form>')
    @app.post('/isolated-session')
    def isolated_login(request: Request):
        if request.headers.get('origin') != 'https://workspace.sustainablecatalyst.com':
            from fastapi import HTTPException
            raise HTTPException(403,'Loopback test origin required')
        response=RedirectResponse('/v1/private-research/reporting-studio',status_code=303)
        response.set_cookie('sc_workspace_session',session_auth.issue_session_token('isolated-reporting-owner'),httponly=True,samesite='strict')
        return response
    token=session_auth.issue_session_token('isolated-reporting-owner')
    fd=os.open(state/'browser-cookie',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:f.write(token)
    return app,token

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--state-dir',required=True)
    parser.add_argument('--seed-export');parser.add_argument('--port',type=int,default=8079)
    args=parser.parse_args();app,token=build(args.state_dir)
    if args.seed_export:
        with TestClient(app,base_url='https://workspace.sustainablecatalyst.com') as client:
            client.cookies.set('sc_workspace_session',token)
            if not client.get('/v1/private-research/persistent-projects').json()['projects']:
                origin={'Origin':'https://workspace.sustainablecatalyst.com'}
                r=client.post('/v1/private-research/persistent-projects',json={
                    'title':'Wexford reporting proof — historical local subset, not EMP-07.5'},headers=origin)
                r.raise_for_status();pid=r.json()['projectId']
                r=client.post('/v1/private-research/persistent-projects/'+pid+'/files',json={
                    'filename':'lab-scientific-export.json',
                    'contentBase64':base64.b64encode(Path(args.seed_export).read_bytes()).decode()},headers=origin)
                r.raise_for_status()
    uvicorn.run(app,host='127.0.0.1',port=args.port)
