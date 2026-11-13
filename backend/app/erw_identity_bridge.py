"""WXR-08.1.3 experimental ERW credential bridge. Requires verified ERW identity.
Does not accept anonymous ERW sessions or trust client-supplied owners.
"""
from __future__ import annotations
import json, os, time, hashlib, sqlite3, pathlib
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from .session_auth import issue_session_token, session_cookie_name
from .config import get_settings

router = APIRouter(prefix='/v1/private-research', tags=['erw-identity-bridge'])
ERW_BASE = os.getenv('WXR0813_ERW_INTERNAL_URL','').rstrip('/')
PUBLIC_ORIGIN = 'https://workspace.sustainablecatalyst.com'
RATE_DB = os.getenv('WXR0813_RATE_DB', '/data/wxr0813_rate_limit.sqlite')

def _rate_limit(ip: str, username: str) -> None:
    """Transactional SQLite limit across processes using shared persistent mounted DB.
    Account and remote IP are hashed, avoiding usernames in the limiter database.
    """
    key = hashlib.sha256((ip + '\x00' + username.casefold()).encode()).hexdigest()
    now = int(time.time())
    try:
        with sqlite3.connect(RATE_DB, timeout=5, isolation_level=None) as db:
            db.execute('PRAGMA busy_timeout=5000')
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS attempts (k TEXT PRIMARY KEY, started INTEGER NOT NULL, n INTEGER NOT NULL)')
            db.execute('DELETE FROM attempts WHERE started < ?', (now-900,))
            row = db.execute('SELECT started,n FROM attempts WHERE k=?',(key,)).fetchone()
            started, count = (row[0],row[1]) if row else (now,0)
            if now-started >= 900: started,count=now,0
            count+=1
            db.execute('INSERT INTO attempts(k,started,n) VALUES(?,?,?) ON CONFLICT(k) DO UPDATE SET started=excluded.started,n=excluded.n',(key,started,count))
            db.commit()
        if count>8: raise HTTPException(429, 'Too many attempts; retry later')
    except HTTPException: raise
    except (OSError, sqlite3.Error):
        raise HTTPException(503, 'Login protection temporarily unavailable') from None


class Login(BaseModel):
    username: str = Field(min_length=1,max_length=160)
    password: str = Field(min_length=1,max_length=256)

def _post_json(url, obj, headers=None):
    data = json.dumps(obj).encode('utf8')
    req = urlrequest.Request(url,data=data,headers={'Content-Type':'application/json',**(headers or {})},method='POST')
    try:
        with urlrequest.urlopen(req,timeout=5) as r:
            if r.status != 200: raise ValueError('ERW authentication failure')
            return json.loads(r.read(16384))
    except (HTTPError,URLError,TimeoutError,ValueError) as e:
        raise ValueError('ERW authentication failure') from None

def _get_json(url,token):
    req=urlrequest.Request(url,headers={'Authorization':'Bearer '+token},method='GET')
    try:
        with urlrequest.urlopen(req,timeout=5) as r:
            if r.status!=200: raise ValueError('ERW session verification failure')
            return json.loads(r.read(16384))
    except (HTTPError,URLError,TimeoutError,ValueError):
        raise ValueError('ERW session verification failure') from None

def _verified_owner(login_data, me_data):
    """ERW identity/me uses owner_from_auth, which requires registered account
    bearer type; compare immutable identity from login and introspection.
    Never accept generic /standalone/v1/auth/session/me anonymous accounts.
    """
    if not isinstance(login_data, dict) or not isinstance(me_data, dict):
        return None
    if me_data.get('ok') is not True or me_data.get('authenticated') is False:
        return None
    if me_data.get('anonymous') is True or me_data.get('type') == 'anonymous':
        return None
    owner = me_data.get('identityId')
    if not isinstance(owner, str) or not 1 <= len(owner) <= 90:
        return None
    if any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:.' for c in owner):
        return None
    login_owner = login_data.get('identityId')
    if login_owner is not None and login_owner != owner:
        return None
    return 'erw:' + owner

LOGIN_HTML='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ERW Sign in | Private Research</title><style>body{background:#0b0b0c;color:#eee;font:16px system-ui;max-width:480px;margin:7vh auto;padding:20px}input{width:100%;padding:12px;background:#222;color:white;border:1px solid #555;box-sizing:border-box;margin:8px 0 18px}button{background:#ad242e;color:white;padding:12px 20px;border:0;cursor:pointer}a{color:#e88}</style><h1>SUSTAINABLE CATALYST</h1><h2>Private Research · ERW sign in</h2><p>Use your existing ERW account. Do not create another account.</p><form id="form"><label>Username<input id="username" autocomplete="username" required></label><label>Password<input id="password" type="password" autocomplete="current-password" required></label><button>Sign in</button></form><p role="alert" id="status"></p><script>document.querySelector('#form').onsubmit=async e=>{e.preventDefault();let p=document.querySelector('#password'),s=document.querySelector('#status');s.textContent='Signing in…';try{let r=await fetch('/v1/private-research/auth/login',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WXR-Login':'1'},body:JSON.stringify({username:document.querySelector('#username').value,password:p.value}),cache:'no-store'});p.value='';if(!r.ok)throw Error('Authentication was not accepted ('+r.status+')');location.assign('/v1/private-research/ui')}catch(e){p.value='';s.textContent=e.message}};</script></html>'''

@router.get('/login',response_class=HTMLResponse)
def login_page():
    return HTMLResponse(LOGIN_HTML,headers={'Cache-Control':'no-store','Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",'X-Content-Type-Options':'nosniff'})

@router.post('/auth/login')
def login(req:Login,request:Request,response:Response):
    origin=request.headers.get('origin','')
    if origin!=PUBLIC_ORIGIN: raise HTTPException(403,'Invalid origin')
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':
        raise HTTPException(415,'JSON content type required')
    if request.headers.get('x-wxr-login')!='1':
        raise HTTPException(403,'Login request header required')
    _rate_limit(request.client.host if request.client else 'unknown', req.username)
    if not ERW_BASE or not ERW_BASE.startswith('http://'):
        raise HTTPException(503,'ERW internal verifier not configured')
    try:
        identity=_post_json(ERW_BASE+'/erw/v1.2.1/identity/login',req.model_dump())
        bearer=identity.get('token') if isinstance(identity,dict) else None
        if not isinstance(bearer,str) or not 16<=len(bearer)<=4096: raise ValueError('bad bearer')
        profile=_get_json(ERW_BASE+'/erw/v1.2.1/identity/me',bearer)
        subject=_verified_owner(identity,profile)
        if not subject: raise ValueError('ERW account attestation missing')
    except (ValueError,KeyError,TypeError):
        raise HTTPException(401,'ERW account authentication could not be verified') from None
    token=issue_session_token(subject, req.username)
    response.set_cookie(key=session_cookie_name(),value=token,max_age=int(get_settings().session_ttl_seconds),path='/',secure=True,httponly=True,samesite='lax')
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    return {'authenticated':True}
