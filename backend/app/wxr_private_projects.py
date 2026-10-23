"""WXR-09.3: signed-session private projects and native research-file persistence.

Additive route. Reuses the existing revisioned Workspace project registry and
content-addressed artifact store; it does not read or mutate recovery archives.
"""
from __future__ import annotations

import base64
import hashlib
import re
from pathlib import PurePath
from urllib.parse import quote
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from .db import session_scope
from . import repository, object_store
from .models import ProjectHead
from .schemas import ProjectStoreRequest, ArtifactStoreRequest
from .session_auth import session_payload_from_request

router = APIRouter(prefix="/v1/private-research/persistent-projects", tags=["Private Research"])
ORIGIN = "https://workspace.sustainablecatalyst.com"
HEADERS = {
    "Cache-Control": "private, no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Robots-Tag": "noindex, nofollow",
}
SUPPORTED = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".ipynb": "application/x-ipynb+json",
    ".csv": "text/csv",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
MAX_ENCODED_LENGTH = 35_000_000  # resource guard; configured artifact limits also apply


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=160)


class ResearchUpload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filename: str = Field(min_length=1, max_length=255)
    contentBase64: str = Field(min_length=1, max_length=MAX_ENCODED_LENGTH)


def _subject(request: Request) -> str:
    session = session_payload_from_request(request)
    sub = session.get("sub") if isinstance(session, dict) else None
    if not isinstance(sub, str) or not sub.strip() or len(sub) > 128:
        raise HTTPException(401, "A valid Workspace browser session is required.")
    return sub


def _write(request: Request) -> None:
    # The signed HttpOnly cookie authenticates; strict Origin protects writes.
    if request.headers.get("origin") != ORIGIN:
        raise HTTPException(403, "Research write origin is not authorized.")


def _project(db, subject: str, project_id: str):
    row = repository.get_project(db, subject, project_id)
    if row is None:
        raise HTTPException(404, "Private project was not found.")
    return row


def _locked_project(db, subject: str, project_id: str):
    # Serialize uploads for one owned project before scanning existing names
    # and hashes. PostgreSQL holds this row lock until the artifact commits.
    row = db.scalar(select(ProjectHead).where(
        ProjectHead.user_key == subject,
        ProjectHead.project_id == project_id,
    ).with_for_update())
    if row is None:
        raise HTTPException(404, "Private project was not found.")
    return row


def _files(db, subject: str, project_id: str) -> list[dict]:
    return [item for item in object_store.list_artifacts(db, subject)
            if item["projectId"] == project_id]


def _filename(value: str) -> tuple[str, str]:
    if (value in {".", ".."} or "/" in value or "\\" in value
            or re.search(r"[\x00-\x1f\x7f]", value)
            or value != PurePath(value).name):
        raise HTTPException(400, "Unsafe research filename.")
    extension = "." + value.rsplit(".", 1)[-1].lower() if "." in value else ""
    if extension not in SUPPORTED:
        raise HTTPException(415, "Unsupported research file extension.")
    return value, SUPPORTED[extension]


@router.get("")
def list_private_projects(request: Request):
    subject = _subject(request)
    with session_scope() as db:
        items = repository.list_projects(db, subject)
        return JSONResponse({"projects": items}, headers=HEADERS)


@router.post("", status_code=201)
def create_private_project(request: Request, body: ProjectCreate):
    subject = _subject(request)
    _write(request)
    project_id = "research-" + uuid4().hex
    project = {"schema": "sc-workspace-project/20.0",
               "title": body.title.strip(),
               "objects": []}
    payload = ProjectStoreRequest.model_validate({
        "schema": "sc-workspace-sync-push/1.0",
        "sourceProjectId": project_id,
        "projectTitle": body.title.strip(),
        "expectedRevision": 0,
        "operationId": "private-research-create-" + project_id,
        "project": project,
    })
    with session_scope() as db:
        row, _ = repository.store_project(db, subject, payload)
        return JSONResponse(repository.project_metadata(row), status_code=201, headers=HEADERS)


@router.get("/ui", response_class=HTMLResponse)
def private_projects_ui(request: Request):
    _subject(request)
    script_hash = base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode()
    return HTMLResponse(HTML, headers={
        **HEADERS,
        "Content-Security-Policy": (
            "default-src 'none'; script-src 'sha256-" + script_hash
            + "'; style-src 'unsafe-inline'; connect-src 'self';"
              " base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        ),
    })


@router.get("/{project_id}")
def open_private_project(project_id: str, request: Request):
    subject = _subject(request)
    with session_scope() as db:
        row = _project(db, subject, project_id)
        return JSONResponse({
            "project": repository.project_metadata(row),
            "package": row.package,
            "files": _files(db, subject, project_id),
        }, headers=HEADERS)


@router.get("/{project_id}/files")
def list_private_files(project_id: str, request: Request):
    subject = _subject(request)
    with session_scope() as db:
        _project(db, subject, project_id)
        return JSONResponse({"files": _files(db, subject, project_id)}, headers=HEADERS)


@router.post("/{project_id}/files", status_code=201)
def upload_private_file(project_id: str, body: ResearchUpload, request: Request):
    subject = _subject(request)
    _write(request)
    filename, media_type = _filename(body.filename)
    # Avoid decoding unexpectedly large payloads before the existing store checks.
    from .config import get_settings
    limit = get_settings().max_artifact_bytes
    if len(body.contentBase64) > 4 * ((limit + 2) // 3):
        raise HTTPException(413, "Research upload exceeds the configured limit.")
    try:
        raw = base64.b64decode(body.contentBase64, validate=True)
    except Exception as exc:
        # The native object store independently verifies base64.
        raise HTTPException(400, "Invalid research-file encoding.") from exc
    if not raw:
        raise HTTPException(400, "Empty file.")
    digest = hashlib.sha256(raw).hexdigest()
    with session_scope() as db:
        _locked_project(db, subject, project_id)
        existing = _files(db, subject, project_id)
        for item in existing:
            if item["sha256"] == digest:
                raise HTTPException(409, "This file already exists in the project.")
            if item["filename"] == filename:
                raise HTTPException(409, "This filename already exists; replacement is disabled.")
        artifact_id = "research-file-" + uuid4().hex
        payload = ArtifactStoreRequest.model_validate({
            "schema": "sc-workspace-artifact-store/1.0",
            "artifactId": artifact_id,
            "projectId": project_id,
            "filename": filename,
            "mediaType": media_type,
            "contentBase64": body.contentBase64,
            "expectedRevision": 0,
            "metadata": {"source": "private-research", "researchProjectId": project_id},
        })
        row = object_store.store_artifact(db, subject, payload)
        return JSONResponse(object_store.artifact_metadata(row), status_code=201, headers=HEADERS)


@router.get("/{project_id}/files/{artifact_id}/download")
def download_private_file(project_id: str, artifact_id: str, request: Request):
    subject = _subject(request)
    with session_scope() as db:
        _project(db, subject, project_id)
        artifact = object_store.get_artifact(db, subject, artifact_id)
        if artifact is None or artifact.project_id != project_id:
            raise HTTPException(404, "Private research file was not found.")
        data = object_store.read_artifact_content(artifact)
        return Response(content=data, media_type="application/octet-stream", headers={
            **HEADERS,
            "Content-Disposition": "attachment; filename*=UTF-8''" + quote(artifact.filename, safe=""),
            "Content-Security-Policy": "sandbox",
            "X-Research-SHA256": artifact.sha256,
        })


SCRIPT = r"""
const root='/v1/private-research/persistent-projects';
const status=document.getElementById('status');
const projects=document.getElementById('projects');
const files=document.getElementById('files');
const encode=bytes=>{let out='';for(let i=0;i<bytes.length;i+=32768){out+=String.fromCharCode(...bytes.slice(i,i+32768));}return btoa(out)};
async function api(path,options={}) {
 const r=await fetch(root+path,{credentials:'same-origin',cache:'no-store',...options,
 headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(options.headers||{})}});
 if(!r.ok)throw Error('Request failed ('+r.status+'): '+(await r.text()).slice(0,300));
 return r.json();
}
async function refresh() {
 const d=await api('');projects.replaceChildren();
 for(const p of d.projects){const button=document.createElement('button');button.textContent=p.title+' — '+p.projectId;
 button.onclick=()=>openProject(p.projectId);projects.append(button)}
}
let current=null;
async function openProject(id) {
 const d=await api('/'+encodeURIComponent(id));current=id;
 document.getElementById('selected').textContent=d.project.title;
 files.replaceChildren();
 for(const f of d.files){const a=document.createElement('a');
 a.href=root+'/'+encodeURIComponent(id)+'/files/'+encodeURIComponent(f.artifactId)+'/download';
 a.textContent=f.filename+' ('+f.bytes+' bytes, SHA-256 '+f.sha256+')';
 files.append(a)}
 document.getElementById('uploader').hidden=false;
}
document.getElementById('create').onsubmit=async e=>{
 e.preventDefault();try{const d=await api('',{method:'POST',body:JSON.stringify({title:document.getElementById('title').value})});
 await refresh();await openProject(d.projectId);status.textContent='Private project created and saved.';
 }catch(err){status.textContent=err.message}
};
document.getElementById('upload').onsubmit=async e=>{
 e.preventDefault();try{const file=document.getElementById('file').files[0];
 if(!file||!current)return;
 status.textContent='Uploading '+file.name+'...';
 const contentBase64=encode(new Uint8Array(await file.arrayBuffer()));
 await api('/'+encodeURIComponent(current)+'/files',{method:'POST',
 body:JSON.stringify({filename:file.name,contentBase64})});
 await openProject(current);status.textContent='Uploaded and saved. Download links verify stored content.';
 }catch(err){status.textContent=err.message}
};
refresh().catch(err=>status.textContent=err.message);
"""
HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Private Research | Sustainable Catalyst</title>
<style>body{font:16px/1.5 system-ui;max-width:900px;margin:40px auto;padding:0 20px;background:#111;color:#eee}
a{display:block;color:#9edac4;margin:10px 0}button,input{padding:10px;margin:8px 0}#projects button{display:block}
section{border:1px solid #555;padding:18px;margin:20px 0}#status{min-height:30px}</style></head><body>
<h1>Sustainable Catalyst — Private Research</h1><p>Signed-session Workspace projects. Research stays private.</p>
<p id="status" role="status"></p>
<section><h2>Create project</h2><form id="create"><input id="title" required maxlength="160" placeholder="Project title"><button>Create</button></form></section>
<section><h2>My projects</h2><div id="projects"></div></section>
<section><h2 id="selected">Select a project</h2><div id="files"></div>
<div id="uploader" hidden><form id="upload"><input id="file" type="file" required><button>Upload file</button></form></div></section>
<script>""" + SCRIPT + """</script></body></html>"""


