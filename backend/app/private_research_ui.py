"""WXR-08.1.2: session-protected private research interface.
Mount this router in the same FastAPI app as the WXR-08.1.1 router.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from .private_research import session_owner

router = APIRouter(prefix='/v1/private-research', tags=['private-research-ui'])

HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Private Research | Sustainable Catalyst</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif}body{background:#090a0b;color:#f5f5f5;max-width:1060px;margin:2rem auto;padding:0 1rem}
h1{letter-spacing:.04em}small,.muted{color:#b8b8b8}a{color:#ffb3b3}button{background:#a51f29;color:white;border:0;padding:.7rem 1rem;border-radius:4px;cursor:pointer}
button:disabled{opacity:.5;cursor:not-allowed}input,select{background:#202124;color:#fff;border:1px solid #555;padding:.65rem;border-radius:4px;min-width:0}
section{padding:1rem;border:1px solid #383838;border-radius:8px;margin:1rem 0}form{display:flex;flex-wrap:wrap;gap:.6rem;margin:.6rem 0}
.row{display:flex;gap:.7rem;align-items:center;flex-wrap:wrap}li{margin:.6rem 0}#status{white-space:pre-wrap} .error{color:#ff8888}
</style></head><body>
<h1>SUSTAINABLE <span style="color:#cc2936">CATALYST</span></h1>
<p>Private Research Workspace <small>· Existing Workspace session required · Research remains unpublished</small></p>
<div id="status" role="status" aria-live="polite">Loading private research…</div>
<section><h2>Research projects</h2><p class="muted">Only Workspace projects already owned by your signed-in account can be attached.</p>
<form id="attach"><label>Existing Workspace project ID <input name="projectId" required autocomplete="off"></label>
<label>Private research title <input name="title" required maxlength="500"></label><button type="submit">Attach</button></form>
<ul id="projects"></ul></section>
<section><h2>Branches and artifacts</h2><div class="row"><label>Project <select id="project"></select></label><button id="refresh" type="button">Refresh</button></div>
<form id="branch"><label>Branch name <input name="name" required maxlength="160"></label><button type="submit">Create branch</button></form>
<ul id="branches"></ul></section>
<p class="muted">Files are review-only until the authentication and download gates are certified. This screen deliberately does not enable uploads yet.</p>
<script>
(()=>{'use strict';
const base='/v1/private-research',status=document.querySelector('#status'),project=document.querySelector('#project');
const esc=s=>String(s??'');const setStatus=(s,err=false)=>{status.textContent=s;status.className=err?'error':''};
async function request(path,method='GET',data=null){const headers={'Accept':'application/json'};if(data)headers['Content-Type']='application/json';
const r=await fetch(base+path,{method,headers,body:data?JSON.stringify(data):undefined,credentials:'same-origin',cache:'no-store'});
if(r.status===401||r.status===403){setStatus('Session missing or expired. Return to Workspace and sign in again.',true);throw Error('Authentication required')}
if(!r.ok){throw Error('Request failed ('+r.status+'): '+(await r.text()).slice(0,250))};return r.status===204?null:r.json()}
function items(v){if(Array.isArray(v))return v;if(v&&Array.isArray(v.projects))return v.projects;if(v&&Array.isArray(v.branches))return v.branches;return []}
async function projects(){const data=items(await request('/projects'));const ul=document.querySelector('#projects');ul.replaceChildren();project.replaceChildren();
for(const x of data){let id=esc(x.project_id??x.projectId),title=esc(x.title??id);let li=document.createElement('li');li.textContent=title+' · '+id;ul.append(li);
let opt=document.createElement('option');opt.value=id;opt.textContent=title;project.append(opt)};
if(!data.length)ul.textContent='No private research projects attached.';setStatus('Private session accepted · '+data.length+' project(s)');await branches()}
async function branches(){const ul=document.querySelector('#branches');ul.replaceChildren();if(!project.value)return;
let data=items(await request('/projects/'+encodeURIComponent(project.value)+'/branches'));
for(const x of data){let li=document.createElement('li');li.textContent=esc(x.name??x.branch_id)+' · '+esc(x.branch_id??x.branchId);ul.append(li)};
if(!data.length)ul.textContent='No branches yet.'}
document.querySelector('#attach').addEventListener('submit',async e=>{e.preventDefault();try{const f=new FormData(e.target);await request('/projects','POST',{projectId:esc(f.get('projectId')),title:esc(f.get('title'))});e.target.reset();await projects()}catch(err){setStatus(err.message,true)}});
document.querySelector('#branch').addEventListener('submit',async e=>{e.preventDefault();if(!project.value)return;try{const f=new FormData(e.target);await request('/projects/'+encodeURIComponent(project.value)+'/branches','POST',{name:esc(f.get('name'))});e.target.reset();await branches();setStatus('Branch created')}catch(err){setStatus(err.message,true)}});
document.querySelector('#refresh').addEventListener('click',()=>projects().catch(e=>setStatus(e.message,true)));
project.addEventListener('change',()=>branches().catch(e=>setStatus(e.message,true)));
projects().catch(e=>setStatus(e.message,true));
})();
</script></body></html>'''

@router.get('/ui', response_class=HTMLResponse, include_in_schema=False)
def private_research_ui(_owner: str = Depends(session_owner)):
    return HTMLResponse(HTML, headers={'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer', 'Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"})
