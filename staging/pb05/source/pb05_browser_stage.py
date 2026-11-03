"""PB05 browser-only test harness. Never mount in the public/production Workspace.

This module is intentionally inert unless its isolated-stage guard is present.
It reuses the native Workspace project and PB04 publication routers and existing
signed session cookie. A high-entropy test-only login code issues an isolated
synthetic-owner cookie, not a real user login or OAuth exchange.
"""
from __future__ import annotations

import hmac
import os
from html import escape
from urllib.parse import parse_qs, quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.routing import APIRoute

if os.environ.get('PB05_STAGE_ENABLED') != 'ISOLATED_TEST_ONLY':
    raise RuntimeError('PB05 stage forbidden outside isolated test environment')
if os.environ.get('SC_WORKSPACE_ENVIRONMENT') != 'pb05-isolated':
    raise RuntimeError('PB05 requires isolated Workspace environment')

ORIGIN = 'https://localhost:18443'
if os.environ.get('PB05_STAGE_ORIGIN') != ORIGIN:
    raise RuntimeError('PB05 staging origin mismatch')

CODE = os.environ.get('PB05_STAGE_LOGIN_CODE', '')
CODE_B = os.environ.get('PB05_STAGE_SECOND_LOGIN_CODE', '')
OWNER = os.environ.get('PB05_STAGE_TEST_OWNER', '')
OWNER_B = os.environ.get('PB05_STAGE_TEST_OTHER_OWNER', '')
if len(CODE) < 48 or not all(x in '0123456789abcdef' for x in CODE):
    raise RuntimeError('PB05 test code must be random lowercase hex >= 48 chars')
if len(CODE_B) < 48 or not all(x in '0123456789abcdef' for x in CODE_B) or CODE == CODE_B:
    raise RuntimeError('PB05 second independent test code is invalid')
if (not OWNER.startswith('pb05-synthetic-owner-') or len(OWNER) > 100
        or not OWNER_B.startswith('pb05-synthetic-owner-') or len(OWNER_B) > 100
        or OWNER == OWNER_B):
    raise RuntimeError('PB05 distinct synthetic test identities are required')

from .session_auth import issue_session_token, session_cookie_name, session_payload_from_request
from .repository import list_projects
from .db import session_scope
from .wxr_private_projects import router as private_router
from .rd014_publication_records import router as publication_router, _row as publication_row

if getattr(private_router, 'prefix', '') != '/v1/private-research/persistent-projects':
    raise RuntimeError('PB05 private router prefix mismatch')
if getattr(publication_router, 'prefix', '') != private_router.prefix:
    raise RuntimeError('PB05 publication router prefix mismatch')

def _signatures(router):
    return [(method, route.path) for route in router.routes if isinstance(route, APIRoute)
            for method in route.methods if method not in ('HEAD', 'OPTIONS')]

project_signatures = _signatures(private_router)
publication_signatures = _signatures(publication_router)
if (len(project_signatures) != 7 or len(publication_signatures) != 7
        or len(project_signatures + publication_signatures) != len(set(project_signatures + publication_signatures))):
    raise RuntimeError('PB05 project/publication router count or collision mismatch')

app = FastAPI(title='PB05 isolated browser acceptance — NOT PRODUCTION', docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1'])
app.include_router(private_router)
app.include_router(publication_router)

NO_STORE = {'Cache-Control':'private, no-store', 'X-Content-Type-Options':'nosniff', 'X-Robots-Tag':'noindex, nofollow'}
CSP = "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"


def _guard_host(request: Request) -> None:
    if request.headers.get('host') != 'localhost:18443':
        raise HTTPException(status_code=403, detail='PB05 browser host must be SSH-tunneled localhost.')


def _require_origin(request: Request) -> None:
    _guard_host(request)
    if request.headers.get('origin') != ORIGIN:
        raise HTTPException(status_code=403, detail='PB05 stage CSRF/origin denied.')


def _owner(request: Request) -> str:
    _guard_host(request)
    payload = session_payload_from_request(request)
    sub = payload.get('sub') if isinstance(payload, dict) else ''
    if sub not in (OWNER, OWNER_B):
        raise HTTPException(status_code=401, detail='PB05 synthetic signed session required.')
    return sub


def _html(text: str, code: int = 200) -> HTMLResponse:
    return HTMLResponse(text, status_code=code, headers={**NO_STORE, 'Content-Security-Policy': CSP})


@app.get('/__pb05__/status')
def status(request: Request):
    _guard_host(request)
    return JSONResponse({'schema':'sc-pb05-staging-status/1.0', 'mode':'isolated-synthetic-browser', 'ok':True, 'production':False}, headers=NO_STORE)


@app.get('/__pb05__/login')
def login_page(request: Request):
    _guard_host(request)
    return _html('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PB05 test sign in</title>
<style>body{font:16px/1.5 system-ui;max-width:680px;margin:60px auto;background:#14202b;color:#fff;padding:24px}input,button{font:inherit;padding:12px;max-width:100%}input{width:90%;box-sizing:border-box}button{cursor:pointer}small{color:#c2ccd5}</style>
<h1>PB05 — isolated test sign in</h1><p>Only synthetic research data belongs here. This is not the live Workspace login.</p>
<form method="post" action="/__pb05__/login"><label for="code">Staging access code (one of two synthetic owners)</label><p><input id="code" name="code" type="password" autocomplete="off" required></p><button>Sign in to staging</button></form>
<p><small>Requires an SSH tunnel, HTTPS, and a separate signed HttpOnly test session.</small></p></html>''')


@app.post('/__pb05__/login')
async def login(request: Request):
    _require_origin(request)
    if request.headers.get('content-type', '').split(';')[0].strip() != 'application/x-www-form-urlencoded':
        raise HTTPException(415, 'Expected form submission.')
    raw = await request.body()
    if len(raw) > 1024:
        raise HTTPException(413, 'Submission is too long.')
    try:
        supplied = parse_qs(raw.decode('utf-8'), strict_parsing=True).get('code', [''])[0]
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(400, 'Invalid form encoding.')
    if hmac.compare_digest(supplied, CODE):
        owner = OWNER
    elif hmac.compare_digest(supplied, CODE_B):
        owner = OWNER_B
    else:
        raise HTTPException(401, 'Invalid staging access code.')
    response = RedirectResponse('/__pb05__/catalog', status_code=303, headers=NO_STORE)
    response.set_cookie(session_cookie_name(), issue_session_token(owner), path='/',
                        secure=True, httponly=True, samesite='strict', max_age=3600)
    return response


@app.post('/__pb05__/logout')
def logout(request: Request):
    _require_origin(request)
    response = RedirectResponse('/__pb05__/login', status_code=303, headers=NO_STORE)
    response.delete_cookie(session_cookie_name(), path='/', secure=True, httponly=True, samesite='strict')
    return response


@app.get('/__pb05__/receipt')
def receipt(request: Request):
    """Owner-bound synthetic acceptance proof; never returns manuscript bytes or secrets."""
    subject = _owner(request)
    with session_scope() as db:
        projects = list_projects(db, subject)
        records = []
        for project in projects:
            pid = str(project['projectId'])
            documents = []
            for kind in ('scientific-report', 'policy-brief'):
                row = publication_row(db, subject, pid, kind)
                documents.append({
                    'kind': kind, 'saved': row is not None,
                    'revision': row.revision if row else 0,
                    'sha256': row.sha256 if row else None,
                })
            records.append({'projectId': pid, 'title': project.get('title',''), 'documents': documents})
    return JSONResponse({'schema':'sc-pb05-browser-acceptance/1.0',
                         'mode':'isolated-synthetic-browser', 'projects': records,
                         'production':False, 'ownerAlias':'A' if subject == OWNER else 'B'},
                        headers=NO_STORE)


@app.get('/__pb05__/catalog')
def catalog(request: Request):
    subject = _owner(request)
    with session_scope() as db:
        projects = list_projects(db, subject)
    items = []
    for p in projects:
        pid = str(p['projectId'])
        title = escape(str(p.get('title', pid)))
        url = '/v1/private-research/persistent-projects/' + quote(pid, safe='') + '/publications/ui'
        items.append('<li>' + title + ' — <a href="' + url + '">Open two-publication editor</a></li>')
    if not items:
        items = ['<li>No synthetic projects yet. Use the native Create Project interface.</li>']
    return _html('''<!doctype html><html lang="en"><meta charset="utf-8"><title>PB05 staged research catalog</title>
<style>body{font:16px/1.5 system-ui;max-width:780px;margin:50px auto;background:#14202b;color:white;padding:20px}a{color:#9ce7c5}button{padding:10px}</style>
<h1>PB05 — synthetic research catalog</h1><p>One synthetic owner, isolated database and object store. Nothing here is your live Wexford project.</p>
<p><a href="/v1/private-research/persistent-projects/ui">Open native Create Project interface</a></p>
<p><a href="/__pb05__/receipt">View JSON acceptance receipt (no document text)</a></p>
<h2>Saved synthetic projects</h2><ul>'''+''.join(items)+'''</ul>
<p>After creating a project, reload this page to open its Assignment 1 and Assignment 2 editors.</p>
<form method="post" action="/__pb05__/logout"><button type="submit">Sign out of synthetic staging</button></form></html>''')
