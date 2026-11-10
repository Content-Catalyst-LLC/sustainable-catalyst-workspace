"""RD-01.4: two independently revisioned publications in existing Workspace storage.

ADDITIVE router for existing signed-session Private Research project context.
Requires deployment source parity and explicit app.include_router(router).
No new authentication, database, object store, or published document output.
"""
from __future__ import annotations

import base64
import hashlib
from html import escape
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import session_scope
from . import repository, object_store
from .models import ArtifactRevision
from .schemas import ArtifactStoreRequest
from .session_auth import session_payload_from_request

ORIGIN = "https://workspace.sustainablecatalyst.com"
PREFIX = "/v1/private-research/persistent-projects"
SCHEMA = "sc-rd014-publication-record/1.0"
KIND_NAMES = {
    "scientific-report": "Assignment 1 — Scientific Research Report",
    "policy-brief": "Assignment 2 — Evidence-Based Policy Brief",
}
KIND_FILES = {
    "scientific-report": "assignment-1-scientific-report.md",
    "policy-brief": "assignment-2-policy-brief.md",
}
HEADERS = {
    "Cache-Control": "private, no-store",
    "X-Content-Type-Options": "nosniff",
    "X-Robots-Tag": "noindex, nofollow",
}

router = APIRouter(prefix=PREFIX, tags=["Private Research Publications"])


class FigureRef(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figureId: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{1,79}$")
    artifactId: str = Field(min_length=1, max_length=160)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    includeInExport: bool = False


class PublicationWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contentMarkdown: str = Field(min_length=1, max_length=500_000)
    expectedRevision: int = Field(ge=0)
    figures: list[FigureRef] | None = Field(default=None, max_length=30)
    originalSubmissionArtifactId: str | None = Field(default=None, min_length=1, max_length=160)


def _subject(request: Request) -> str:
    payload = session_payload_from_request(request)
    sub = payload.get("sub") if isinstance(payload, dict) else None
    if not isinstance(sub, str) or not sub.strip() or len(sub) > 128:
        raise HTTPException(status_code=401, detail="A valid Workspace browser session is required.")
    return sub


def _write_origin(request: Request) -> None:
    if request.headers.get("origin") != ORIGIN:
        raise HTTPException(status_code=403, detail="Research write origin is not authorized.")


def _kind(kind: str) -> None:
    if kind not in KIND_NAMES:
        raise HTTPException(status_code=404, detail="Unknown publication kind.")


def _project(db, owner: str, project_id: str) -> None:
    if repository.get_project(db, owner, project_id) is None:
        raise HTTPException(status_code=404, detail="Private project was not found.")


def _publication_id(project_id: str, kind: str) -> str:
    _kind(kind)
    digest = hashlib.sha256(f"{project_id}\0{kind}".encode("utf-8")).hexdigest()[:40]
    return f"rd014pub-{digest}"


def _row(db, owner: str, project_id: str, kind: str):
    art_id = _publication_id(project_id, kind)
    row = object_store.get_artifact(db, owner, art_id)
    if row is None:
        return None
    meta = row.metadata_json if isinstance(row.metadata_json, dict) else {}
    if (row.project_id != project_id or meta.get("schema") != SCHEMA
            or meta.get("publicationKind") != kind):
        raise HTTPException(status_code=409, detail="Publication identity collision or provenance mismatch.")
    return row


def _original(db, owner: str, project_id: str, kind: str, source_id: str | None, publication_id: str):
    if source_id is None:
        return None
    if kind != "scientific-report" or source_id == publication_id:
        raise HTTPException(status_code=422, detail="Original submission may only be attached to the scientific report.")
    item = object_store.get_artifact(db, owner, source_id)
    if item is None or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Original submission artifact is not in this project.")
    if item.media_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        raise HTTPException(status_code=422, detail="Original submission must be an owner-scoped DOCX or PDF.")
    # Do not modify this artifact. It is a preserved source reference, not a copy.
    return {"artifactId": source_id, "sha256": item.sha256, "revision": item.revision}


def _figures(db, owner: str, project_id: str, figures: list[FigureRef]) -> list[dict]:
    result = []
    seen = set()
    for figure in figures:
        if figure.figureId in seen or figure.artifactId in seen:
            raise HTTPException(status_code=422, detail="Duplicate figure reference.")
        seen.update((figure.figureId, figure.artifactId))
        item = object_store.get_artifact(db, owner, figure.artifactId)
        if item is None or item.project_id != project_id or item.sha256 != figure.sha256:
            raise HTTPException(status_code=422, detail="Figure bytes are not verified as owner-scoped project assets.")
        metadata = item.metadata_json if isinstance(item.metadata_json, dict) else {}
        if figure.includeInExport:
            # Global PB03.2 review gate: this specific Wexford source is not approved.
            # Metadata alone must never silently promote it to final export.
            if figure.figureId == "FIG-GEO01":
                raise HTTPException(status_code=422, detail="FIG-GEO01 is review-only pending geospatial and cloud-quality acceptance.")
            review = metadata.get("publicationReview") or {}
            if (review.get("status") != "approved"
                    or review.get("rights") != "approved"
                    or review.get("science") != "approved"):
                raise HTTPException(status_code=422, detail="Figure is not independently approved for publication.")
        result.append({"figureId": figure.figureId, "artifactId": figure.artifactId,
                       "sha256": figure.sha256, "includeInExport": figure.includeInExport})
    return result


def _serialize(row, *, include_content: bool = False) -> dict:
    meta = row.metadata_json if isinstance(row.metadata_json, dict) else {}
    record = {
        "schema": SCHEMA,
        "projectId": row.project_id,
        "publicationId": row.artifact_id,
        "kind": meta.get("publicationKind"),
        "title": meta.get("publicationTitle"),
        "revision": row.revision,
        "sha256": row.sha256,
        "figures": meta.get("figures", []),
        "originalSubmission": meta.get("originalSubmission"),
        "published": False,
    }
    if include_content:
        record["contentMarkdown"] = object_store.read_artifact_content(row).decode("utf-8")
    return record


def _save(db, owner: str, project_id: str, kind: str, body: PublicationWrite, *, create: bool) -> dict:
    _project(db, owner, project_id)
    _kind(kind)
    publication_id = _publication_id(project_id, kind)
    current = _row(db, owner, project_id, kind)
    if create and (current is not None or body.expectedRevision != 0):
        raise HTTPException(status_code=409, detail="Publication already exists or expectedRevision is not zero.")
    if not create and current is None:
        raise HTTPException(status_code=404, detail="Publication does not exist.")
    if not create and body.expectedRevision != current.revision:
        raise HTTPException(status_code=409, detail="Publication revision conflict.")

    existing_meta = current.metadata_json if current is not None and isinstance(current.metadata_json, dict) else {}
    previous_original = existing_meta.get("originalSubmission")
    source_id = body.originalSubmissionArtifactId
    if previous_original and source_id and source_id != previous_original.get("artifactId"):
        raise HTTPException(status_code=409, detail="Original submission reference cannot be replaced.")
    original = _original(db, owner, project_id, kind, source_id, publication_id) if source_id else previous_original
    if original is not None:
        actual = object_store.get_artifact(db, owner, original["artifactId"])
        if (actual is None or actual.project_id != project_id or actual.sha256 != original["sha256"]
                or actual.revision != original["revision"]):
            raise HTTPException(status_code=409, detail="Linked original submission has changed.")
    verified_figures = (_figures(db, owner, project_id, body.figures)
                        if body.figures is not None else existing_meta.get("figures", []))
    metadata = {
        "schema": SCHEMA, "publicationKind": kind, "publicationTitle": KIND_NAMES[kind],
        "originalSubmission": original, "figures": verified_figures,
        "source": "rd014-native-publication", "unverifiedPublicationStatus": "DRAFT",
    }
    content = body.contentMarkdown.encode("utf-8")
    payload = ArtifactStoreRequest.model_validate({
        "schema": "sc-workspace-artifact-store/1.0",
        "artifactId": publication_id,
        "projectId": project_id,
        "filename": KIND_FILES[kind],
        "mediaType": "text/markdown; charset=utf-8",
        "contentBase64": base64.b64encode(content).decode("ascii"),
        "expectedRevision": body.expectedRevision,
        "metadata": metadata,
    })
    try:
        saved = object_store.store_artifact(db, owner, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Concurrent publication revision conflict.") from exc
    return _serialize(saved)


# This is a view within the existing signed-session Private Research area, not a new app.
UI_SCRIPT = r"""
const base=location.pathname.replace(/\/ui$/, '');
let active='scientific-report', revision=0;
const pick=id=>document.getElementById(id);
const status=text=>{pick('status').textContent=text;};
async function call(path,options={}) {
  const res=await fetch(base+path,{credentials:'same-origin',cache:'no-store',...options,
    headers:{...(options.body?{'content-type':'application/json'}:{}),...(options.headers||{})}});
  if(res.status===404)return null;
  if(!res.ok)throw Error(`Workspace ${res.status}: ${String(await res.text()).slice(0,150)}`);
  return res.json();
}
async function load() {
  active=pick('kind').value;
  const data=await call('/'+active);
  revision=data?.revision||0;
  pick('body').value=data?.contentMarkdown||'';
  pick('original').value=data?.originalSubmission?.artifactId||'';
  pick('original').disabled=!!data?.originalSubmission||active!=='scientific-report';
  pick('figures').textContent=data?.figures?.length?`${data.figures.length} linked figure(s); see API record for metadata`:'No linked figures';
  status(data?`Revision ${revision} loaded. Draft only; no PDF/DOCX publication export in this view.`:'No draft yet. Create the first saved revision.');
}
pick('kind').addEventListener('change',()=>load().catch(e=>status(e.message)));
pick('save').addEventListener('click',async()=>{
  try {
    const body={contentMarkdown:pick('body').value,expectedRevision:revision};
    if(active==='scientific-report'&&pick('original').value.trim())
      body.originalSubmissionArtifactId=pick('original').value.trim();
    const saved=await call('/'+active,{method:revision?'PUT':'POST',body:JSON.stringify(body)});
    if(saved){revision=saved.revision;await load();status(`Saved ${active}, revision ${revision}. Reopen to verify persisted text.`);}
  }catch(e){status(e.message);}
});
load().catch(e=>status(e.message));
"""

@router.get("/{project_id}/publications/ui", response_class=HTMLResponse)
def publication_editor_ui(project_id: str, request: Request):
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
    script_hash = base64.b64encode(hashlib.sha256(UI_SCRIPT.encode('utf-8')).digest()).decode('ascii')
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sustainable Catalyst | Research Publications</title><style>
body{font:16px/1.55 system-ui,sans-serif;max-width:1050px;margin:40px auto;padding:0 20px;background:#14191e;color:#e6f1f0}
main,section{margin:1.2rem 0}textarea{width:100%;box-sizing:border-box;min-height:55vh;padding:16px;color:#121c1e;background:#f7fafb}
button,input,select{padding:10px;font:inherit}button{cursor:pointer}label{display:block;margin:12px 0}
#status{background:#26313a;padding:12px;min-height:1.5rem}small{color:#aabfc5}a{color:#acdcca}
</style></head><body><main><h1>Research publications</h1>
<p>One project · two independently versioned manuscripts · signed Workspace account</p>
<label>Publication <select id="kind"><option value="scientific-report">Assignment 1 — Scientific Report</option>
<option value="policy-brief">Assignment 2 — Policy Brief</option></select></label>
<label>Original submitted DOCX/PDF artifact ID (scientific report only; optional)<input id="original" autocomplete="off" size="55"></label>
<small id="figures">Linked figures: none</small>
<label>Working manuscript (Markdown)<textarea id="body" spellcheck="true"></textarea></label>
<button id="save">Save independent revision</button><p id="status" role="status"></p>
<p><small>Preserves submitted source by reference. Does not approve figures or publish to PDF/DOCX. No automatic import of historical Wexford archives.</small></p>
</main><script>"""+UI_SCRIPT+"""</script></body></html>"""
    return HTMLResponse(html,headers={
        **HEADERS,
        "Content-Security-Policy": "default-src 'none'; script-src 'sha256-"+script_hash+"'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    })


@router.get("/{project_id}/publications")
def list_publications(project_id: str, request: Request, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        records = []
        for kind in KIND_NAMES:
            row = _row(db, owner, project_id, kind)
            if row is not None:
                records.append(_serialize(row))
        return {"schema": "sc-rd014-publication-catalog/1.0", "projectId": project_id,
                "publications": records, "expectedKinds": list(KIND_NAMES)}


@router.get("/{project_id}/publications/{kind}")
def get_publication(project_id: str, kind: str, request: Request, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        row = _row(db, owner, project_id, kind)
        if row is None:
            raise HTTPException(status_code=404, detail="Publication not found.")
        return _serialize(row, include_content=True)


@router.post("/{project_id}/publications/{kind}", status_code=201)
def create_publication(project_id: str, kind: str, request: Request, body: PublicationWrite, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    _write_origin(request)
    with session_scope() as db:
        return _save(db, owner, project_id, kind, body, create=True)


@router.put("/{project_id}/publications/{kind}")
def save_publication(project_id: str, kind: str, request: Request, body: PublicationWrite, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    _write_origin(request)
    with session_scope() as db:
        return _save(db, owner, project_id, kind, body, create=False)


@router.get("/{project_id}/publications/{kind}/revisions")
def publication_revisions(project_id: str, kind: str, request: Request, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    with session_scope() as db:
        _project(db, owner, project_id)
        row = _row(db, owner, project_id, kind)
        if row is None:
            raise HTTPException(status_code=404, detail="Publication not found.")
        revisions = db.scalars(select(ArtifactRevision).where(
            ArtifactRevision.user_key == owner,
            ArtifactRevision.artifact_id == row.artifact_id,
        ).order_by(ArtifactRevision.revision.asc())).all()
        return {"publicationId": row.artifact_id, "kind": kind,
                "revisions": [{"revision": item.revision, "sha256": item.sha256,
                               "bytes": item.bytes} for item in revisions]}


@router.get("/{project_id}/publications/{kind}/revisions/{revision}")
def publication_revision(project_id: str, kind: str, revision: int, request: Request, response: Response):
    response.headers.update(HEADERS)
    owner = _subject(request)
    if revision < 1:
        raise HTTPException(status_code=404, detail="Publication revision not found.")
    with session_scope() as db:
        _project(db, owner, project_id)
        row = _row(db, owner, project_id, kind)
        if row is None:
            raise HTTPException(status_code=404, detail="Publication not found.")
        historical = db.get(ArtifactRevision, {"user_key": owner, "artifact_id": row.artifact_id,
                                               "revision": revision})
        if historical is None or historical.project_id != project_id:
            raise HTTPException(status_code=404, detail="Publication revision not found.")
        result = _serialize(historical, include_content=True)
        return result