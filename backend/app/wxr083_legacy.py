"""WXR-08.3: fail-closed legacy ERW registry overlay, no database migrations.
Registry is operator-curated, owner-scoped and read-only to browser callers.
"""
import hashlib
import json
import os
import re
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from .private_research import session_owner

router = APIRouter(prefix='/v1/private-research', tags=['legacy-erw-link'])
REGISTRY = os.environ.get('WXR083_REGISTRY', '/data/private-research/wxr083-legacy-links.json')
OWNER = re.compile(r'^erw:[A-Za-z0-9_:.-]{1,90}$')
PROJECT = re.compile(r'^[A-Za-z0-9_:.-]{1,160}$')
SHA = re.compile(r'^[0-9a-f]{64}$')

def _validate_record(record):
    if not isinstance(record, dict): return False
    return (isinstance(record.get('owner'),str) and OWNER.fullmatch(record['owner']) is not None
            and isinstance(record.get('legacyProjectId'),str) and PROJECT.fullmatch(record['legacyProjectId']) is not None
            and isinstance(record.get('title'),str) and 1 <= len(record['title']) <= 180
            and isinstance(record.get('evidenceSha256'),str) and SHA.fullmatch(record['evidenceSha256']) is not None
            and record.get('approved') is True)

def registry_for_owner(owner, file_path=None):
    if not OWNER.fullmatch(owner): return []
    path=Path(file_path or REGISTRY)
    if path.is_symlink() or not path.is_file(): return []
    if path.stat().st_size > 128*1024: return []
    try:
        obj=json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError): return []
    if not isinstance(obj,dict) or obj.get('version') != 1 or not isinstance(obj.get('projects'),list): return []
    seen=set(); output=[]
    for p in obj['projects']:
        if not _validate_record(p) or p['owner'] != owner: continue
        if p['legacyProjectId'] in seen: continue
        seen.add(p['legacyProjectId'])
        output.append({'projectId':p['legacyProjectId'],'title':p['title'],
                       'kind':'legacy-erw','launchMode':'existing-erw-editor-local-tunnel',
                       'evidenceSha256':p['evidenceSha256'],'readOnlyLink':True})
    return output

@router.get('/legacy/projects')
def legacy_projects(owner: str = Depends(session_owner)):
    return {'projects':registry_for_owner(owner),'authoritativeSystem':'Workbench/ERW',
            'migrationPerformed':False, 'workspaceProjectCreated':False}

@router.get('/legacy/ui', response_class=HTMLResponse)
def legacy_ui(owner: str = Depends(session_owner)):
    return HTMLResponse('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Wexford · Private Research</title>
<style>body{font:16px system-ui;background:#0b0b0c;color:#eee;max-width:900px;margin:3em auto;padding:1em}a{color:#ff9ca6}article{padding:1.2em;border:1px solid #444;margin:1em 0;border-radius:8px}.muted{color:#bbb}</style>
<h1>SUSTAINABLE <span style="color:#db303d">CATALYST</span></h1><h2>Private Research · Existing ERW projects</h2>
<p class="muted">Read-only Workspace index. The original Workbench editor retains all manuscripts, models and saved research. An SSH tunnel to the original editor must be active for Launch to work.</p>
<div id="projects">Loading…</div><p><a href="/v1/private-research/ui">Return to Private Research</a></p>
<script>fetch('/v1/private-research/legacy/projects',{credentials:'same-origin',cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Authentication required');return r.json()}).then(d=>{let root=document.querySelector('#projects');root.textContent='';if(!d.projects.length){root.textContent='No approved legacy project mapping found. The existing editor and data have not been changed.';return;}for(let p of d.projects){let a=document.createElement('article');let h=document.createElement('h3');h.textContent=p.title;let x=document.createElement('p');x.textContent='Verified operator-linked ERW project · ID: '+p.projectId;let link=document.createElement('a');link.href='http://127.0.0.1:18088/erw/report';link.textContent='Launch original ERW editor (local SSH tunnel)';link.rel='noopener noreferrer';link.target='_blank';a.append(h,x,link);root.append(a);}}).catch(()=>{document.querySelector('#projects').textContent='Project index unavailable.'});</script></html>''',headers={'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"})
