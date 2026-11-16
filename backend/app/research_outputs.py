"""SC-PUB-ENDTOEND-01 — Outputs & Publishing: one Workspace project, several independently governed Research outputs.

An output is an existing Reporting Studio publication (``documentId``). Its immutable, hash-identified revisions,
figures and frozen bibliography stay where they are; nothing here copies or rewrites them. This module adds only:

* the binding of that output to one Research article (a ``research-output`` object in the same immutable project
  store the Studio and Citation Studio already use; no new table, container or account);
* the Research editorial lifecycle, driven server-side for the signed-in person. For each call Workspace signs the
  existing 5-minute ``sc-workspace-research-session/1.0`` (SC-UP-01) and sends it to Research; the browser never holds
  a Research credential and never chooses an owner.

Research stays the authority. Every state shown is Research's confirmed response, and Workspace records only the
receipts Research returned. Approvals are the existing SC-ED-01 Workspace records (self-approval prohibited, explicit
grants, step-up where SC Identity is deployed); this module raises requests for the exact Research revision and hands
Research the signed records. Each output is its own article, so publishing one never exposes a sibling.
"""
from __future__ import annotations

import base64
import json
import re
from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Callable, Literal
from urllib.parse import quote, urlsplit

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .config import get_settings

SCHEMA = "sc-workspace-research-output/1.0"
OBJECT_TYPE = "research-output"
API = "/api/research/v1"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIMENSIONS = ("scientific", "rights", "ownership", "publication")
REFERENCE_ROLES = ("figure", "result", "notebook", "study-package", "dataset", "model", "citation")
MAX_RECEIPTS = 200
TIMEOUT = 15.0
# Tests replace this with an httpx.MockTransport; production uses the default network transport.
TRANSPORT: httpx.BaseTransport | None = None
ISSUER_TRANSPORT: httpx.BaseTransport | None = None  # the backend's session issuer (tests inject a MockTransport)
_REQUEST: ContextVar[Request | None] = ContextVar("sc_outputs_request", default=None)


# ---------------------------------------------------------------------------
# Research client


def research_origin() -> str:
    settings = get_settings()
    value = (settings.research_api_origin or "").strip().rstrip("/")
    parts = urlsplit(value)
    if not value or parts.path or parts.query or parts.fragment or parts.username or parts.password or not parts.hostname:
        raise HTTPException(503, "Research publishing is not configured for this Workspace.")
    if parts.scheme != "https" and not (parts.scheme == "http" and settings.research_api_allow_http):
        raise HTTPException(503, "Research publishing is not configured for this Workspace.")
    return value


def _issued_by_backend(identity, issuer: str) -> dict:
    """The person's Research session from the Workspace backend, which alone holds the Research signing key.

    Sent with the person's own session cookie, so the backend applies its own identity and method rules; the returned
    document must name exactly the person and sign-in method this request was authenticated with."""
    from .config import browser_origins
    from .research_access import SESSION_SCHEMA
    settings = get_settings()
    request = _REQUEST.get()
    cookie = request.cookies.get(settings.session_cookie_name) if request is not None else None
    if not cookie:
        raise HTTPException(401, "A valid Workspace browser session is required.")
    origins = browser_origins(settings)
    origin = request.headers.get("origin") if request.headers.get("origin") in origins else min(origins, default="")
    try:
        with httpx.Client(transport=ISSUER_TRANSPORT, timeout=TIMEOUT, follow_redirects=False) as client:
            response = client.post(issuer, headers={"Cookie": f"{settings.session_cookie_name}={cookie}", "Origin": origin,
                                                    "Accept": "application/json"})
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Research is unavailable; nothing was changed in Workspace.") from exc
    if response.status_code in (401, 403):
        raise HTTPException(response.status_code, _detail(response))
    try:
        doc = response.json() if response.status_code == 200 else None
    except ValueError:
        doc = None
    if not isinstance(doc, dict) or doc.get("schema") != SESSION_SCHEMA \
            or doc.get("subject") != f"workspace-user:{identity.user_key}" \
            or doc.get("authentication") != identity.authentication_method:
        raise HTTPException(502, "Research is unavailable; nothing was changed in Workspace.")
    return doc


def session_header(identity) -> str:
    issuer = (get_settings().research_session_issuer_url or "").strip()
    if issuer:
        doc = _issued_by_backend(identity, issuer)
    else:
        from .research_access import issue_session
        doc = issue_session(identity)
    return "SC-Workspace " + base64.urlsafe_b64encode(json.dumps(doc, separators=(",", ":")).encode()).decode().rstrip("=")


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return "Research refused the request."
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, dict):
        detail = detail.get("message") or detail.get("code") or json.dumps(detail)[:300]
    return str(detail)[:600]


def call(identity, method: str, path: str, body: dict | None = None) -> dict:
    """One Research request as the signed-in person. Research's refusals keep their status and reason."""
    url = research_origin() + API + path
    headers = {"Authorization": session_header(identity), "Accept": "application/json"}
    try:
        with httpx.Client(transport=TRANSPORT, timeout=TIMEOUT, follow_redirects=False) as client:
            response = client.request(method, url, headers=headers, json=body)
    except httpx.HTTPError as exc:
        raise HTTPException(502, "Research is unavailable; nothing was changed in Workspace.") from exc
    if response.status_code in (400, 401, 403, 404, 409, 410, 422):
        raise HTTPException(response.status_code, _detail(response))
    if response.status_code != 200:
        raise HTTPException(502, "Research is unavailable; nothing was changed in Workspace.")
    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(502, "Research returned an invalid response.") from exc
    if not isinstance(data, dict):
        raise HTTPException(502, "Research returned an invalid response.")
    return data


# ---------------------------------------------------------------------------
# Bindings (project objects)


def bindings(package: dict) -> dict[str, dict]:
    return {o["output"]["documentId"]: o["output"] for o in package.get("project", {}).get("objects", [])
            if isinstance(o, dict) and o.get("type") == OBJECT_TYPE and isinstance(o.get("output"), dict)
            and o["output"].get("schema") == SCHEMA}


def _put_binding(project: dict, output: dict) -> dict:
    project = deepcopy(project)
    objects = [o for o in project.get("objects", []) if not (
        isinstance(o, dict) and o.get("type") == OBJECT_TYPE and (o.get("output") or {}).get("documentId") == output["documentId"])]
    objects.append({"id": "research-output-" + output["documentId"], "type": OBJECT_TYPE, "output": output})
    project["objects"] = objects
    return project


def receipt_entry(action: str, research: dict, **extra) -> dict:
    """What Workspace keeps of a Research response: the action, Research's own receipt (if any) and the revision."""
    receipt = research.get("receipt") if isinstance(research.get("receipt"), dict) else None
    entry = {"action": action, "at": datetime.now(timezone.utc).isoformat(), **extra}
    if receipt:
        entry["receipt"] = {k: receipt.get(k) for k in ("schema", "action", "article", "seq", "eventSha256", "at")
                            if k in receipt}
    for key in ("revision", "documentSha256", "publishedRevision", "publicationStatus"):
        if key in research:
            entry.setdefault("research", {})[key] = research[key]
    return entry


def summarize_article(view: dict, hub_url: str) -> dict:
    """The Research-confirmed state the dashboard shows. No optimistic flags."""
    revisions = view.get("revisions") or []
    status = view.get("publicationStatus")
    public = None
    if status in ("published", "unlisted") and view.get("publishedRevision"):
        public = hub_url + ("&" if "?" in hub_url else "?") + "article=" + quote(view["slug"], safe="")
    head = view.get("head") or {}
    origins = (head.get("publication") or {}).get("derivedFrom") or []
    studio = next((o for o in origins if o.get("kind") == "workspace-studio-revision"), None)
    return {"slug": view.get("slug"), "area": view.get("area"), "headRevision": view.get("headRevision"),
            "submittedRevision": view.get("submittedRevision"), "publishedRevision": view.get("publishedRevision"),
            "reviewStatus": view.get("reviewStatus"), "publicationStatus": status, "entryState": view.get("entryState"),
            "publicUrl": public, "headStudioRevision": studio,
            "headReferences": [{k: r.get(k) for k in ("objectId", "role", "status", "problems") if k in r}
                               for r in view.get("headReferences") or []],
            "revisions": [{k: r.get(k) for k in ("revision", "documentSha256", "createdAt", "changeSummary",
                                                  "subjectRef", "signedApprovals")} for r in revisions]}


def controls(article: dict | None, configured: bool) -> dict:
    """Which actions Research's confirmed state allows. The server re-checks every one; Research checks again."""
    if not configured:
        return {k: False for k in ("bind", "pushRevision", "submit", "requestApproval", "publish", "unlist", "relist", "withdraw")}
    if article is None:
        return {"bind": True, **{k: False for k in ("pushRevision", "submit", "requestApproval", "publish", "unlist",
                                                     "relist", "withdraw")}}
    status, head, submitted = article["publicationStatus"], article["headRevision"] or 0, article["submittedRevision"]
    withdrawn = status in ("withdrawn", "retracted")
    approvals = {}
    if submitted:
        approvals = next((r.get("signedApprovals") or {} for r in article["revisions"] if r["revision"] == submitted), {})
    return {"bind": False, "pushRevision": not withdrawn,
            "submit": not withdrawn and head > 0 and submitted != head,
            "requestApproval": not withdrawn and bool(submitted),
            "publish": not withdrawn and bool(submitted) and bool(approvals) and all(approvals.values()),
            "unlist": status == "published", "relist": status == "unlisted",
            "withdraw": status in ("published", "unlisted")}


# ---------------------------------------------------------------------------
# HTTP


class BindIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    areaSlug: str = Field(min_length=1, max_length=120)
    articleSlug: str = Field(min_length=1, max_length=150)
    title: str = Field(default="", max_length=300)
    summary: str = Field(default="", max_length=2000)


class ReferenceIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objectId: str = Field(min_length=1, max_length=64)
    role: Literal[REFERENCE_ROLES]
    caption: str = Field(default="", max_length=300)


class RevisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    studioRevision: int = Field(ge=1)
    publicationType: Literal["report", "working-paper", "policy-brief", "interactive-analysis"]
    summary: str = Field(default="", max_length=10000)
    references: list[ReferenceIn] = Field(default_factory=list, max_length=200)


class ResearchRevisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    researchRevision: int = Field(ge=1)


class ApprovalIn(ResearchRevisionIn):
    dimension: Literal[DIMENSIONS]
    reason: str = Field(default="", max_length=2000)


class AttachIn(ResearchRevisionIn):
    approvalId: str = Field(min_length=1, max_length=80)


class PublishIn(ResearchRevisionIn):
    confirmArticleSlug: str = Field(min_length=1, max_length=150)


class ReasonIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(min_length=1, max_length=2000)


class WithdrawIn(ReasonIn):
    publicNotice: str = Field(min_length=1, max_length=2000)
    confirmArticleSlug: str = Field(min_length=1, max_length=150)


class ObjectApprovalIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dimension: Literal[DIMENSIONS]
    reason: str = Field(default="", max_length=2000)


class ObjectAttachIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approvalId: str = Field(min_length=1, max_length=80)


class ReasonOptionalIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(default="", max_length=2000)


class AreaPublishIn(ObjectAttachIn):
    confirmAreaSlug: str = Field(min_length=1, max_length=120)


class DecideIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["approve", "reject", "request_revision"]
    note: str = Field(default="", max_length=2000)
    expectedSubjectRef: str = Field(min_length=1, max_length=300)


def build_router(deps: dict[str, Callable]) -> APIRouter:
    """``deps``: subject, write, project, locked_project, store, session, headers, saved, documents, research_revision."""
    router = APIRouter(tags=["Outputs & Publishing"])
    H = deps["headers"]

    def identity(request: Request):
        from .security import _session_identity
        owner = deps["subject"](request)
        ident = _session_identity(request)
        if ident is None or ident.user_key != owner:
            raise HTTPException(401, "A valid Workspace browser session is required.")
        _REQUEST.set(request)
        return ident

    def writer(request: Request):
        ident = identity(request)
        deps["write"](request)
        return ident

    def configured() -> bool:
        try:
            research_origin()
            return True
        except HTTPException:
            return False

    def bound(db, owner: str, project_id: str, document_id: str) -> tuple[Any, dict]:
        row = deps["project"](db, owner, project_id)
        binding = bindings(row.package).get(document_id)
        if binding is None:
            raise HTTPException(404, "This output is not bound to a Research article yet.")
        return row, binding

    def record(owner: str, project_id: str, document_id: str, entry: dict, operation: str) -> dict:
        """Append a Research-confirmed receipt to the binding (optimistic concurrency via the project store)."""
        with deps["session"]() as db:
            row = deps["locked_project"](db, owner, project_id)
            binding = deepcopy(bindings(row.package).get(document_id))
            if binding is None:
                raise HTTPException(404, "This output is not bound to a Research article yet.")
            binding["receipts"] = (binding.get("receipts") or [])[-(MAX_RECEIPTS - 1):] + [entry]
            deps["store"](db, owner, row, _put_binding(row.package["project"], binding), operation)
            return binding

    def article(ident, slug: str) -> dict:
        return summarize_article(call(ident, "GET", f"/editorial/articles/{quote(slug, safe='')}"),
                                 get_settings().research_hub_url)

    @router.get("/projects/{project_id}/outputs")
    def list_outputs(project_id: str, request: Request):
        ident = identity(request)
        with deps["session"]() as db:
            row = deps["project"](db, ident.user_key, project_id)
            documents = deps["documents"](row.package)
            links = bindings(row.package)
        ok = configured()
        items = []
        for doc in documents:
            binding = links.get(doc["documentId"])
            research, error = None, None
            if binding and ok:
                try:
                    research = article(ident, binding["articleSlug"])
                except HTTPException as exc:
                    error = {"status": exc.status_code, "message": str(exc.detail)}
            items.append({**doc, "binding": binding, "research": research, "researchError": error,
                          "controls": controls(research, ok) if not error else {}})
        return JSONResponse({"projectId": project_id, "researchConfigured": ok, "outputs": items}, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/bind")
    def bind(project_id: str, document_id: str, body: BindIn, request: Request):
        ident = writer(request)
        if not SLUG.fullmatch(body.areaSlug) or not SLUG.fullmatch(body.articleSlug):
            raise HTTPException(422, "Area and article identifiers use lowercase letters, digits and hyphens.")
        with deps["session"]() as db:
            row = deps["project"](db, ident.user_key, project_id)
            docs = {d["documentId"]: d for d in deps["documents"](row.package)}
            if document_id not in docs:
                raise HTTPException(404, "Publication not found in this project.")
            links = bindings(row.package)
        existing = links.get(document_id)
        if existing:
            if (existing["articleSlug"], existing["areaSlug"]) != (body.articleSlug, body.areaSlug):
                raise HTTPException(409, "This output is already bound to another Research article.")
            return JSONResponse({"binding": existing, "created": False}, headers=H)
        if any(b["articleSlug"] == body.articleSlug for b in links.values()):
            raise HTTPException(409, "Another output of this project already uses that Research article.")
        project_key = re.sub(r"[^a-z0-9]+", "-", project_id.lower()).strip("-")[:120] or "workspace-project"
        created = call(ident, "POST", "/editorial/articles", {
            "areaSlug": body.areaSlug, "projectKey": project_key, "workspaceProjectId": project_id,
            "slug": body.articleSlug, "title": (body.title or docs[document_id]["title"]).strip()[:300],
            "summary": body.summary})
        output = {"schema": SCHEMA, "documentId": document_id, "articleSlug": created.get("slug", body.articleSlug),
                  "areaSlug": created.get("area", body.areaSlug), "boundAt": datetime.now(timezone.utc).isoformat(),
                  "receipts": [receipt_entry("bound", created, researchCreated=bool(created.get("created")))]}
        with deps["session"]() as db:
            row = deps["locked_project"](db, ident.user_key, project_id)
            if document_id in bindings(row.package):  # a concurrent bind won; Research's create is idempotent
                return JSONResponse({"binding": bindings(row.package)[document_id], "created": False}, headers=H)
            deps["store"](db, ident.user_key, row, _put_binding(row.package["project"], output),
                          "research-output-bind-" + document_id)
        return JSONResponse({"binding": output, "created": True}, status_code=201, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/research-revisions")
    def push_revision(project_id: str, document_id: str, body: RevisionIn, request: Request):
        """Send one exact, saved Studio revision to Research as the article's next revision (idempotent)."""
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
            _, pub = deps["saved"](db, ident.user_key, project_id, document_id, body.studioRevision)
        payload = deps["research_revision"](project_id, pub, body.publicationType, body.summary)
        refs = []
        for ref in body.references:
            obj = call(ident, "GET", f"/console/objects/{quote(ref.objectId, safe='')}")
            pin = obj.get("pin")
            if not isinstance(pin, str) or not pin:
                raise HTTPException(422, f"Research object {ref.objectId} has no current pin; it cannot be cited.")
            refs.append({"objectId": ref.objectId, "role": ref.role, "pin": pin,
                         **({"caption": ref.caption} if ref.caption else {})})
        slug = quote(binding["articleSlug"], safe="")
        view = call(ident, "GET", f"/editorial/articles/{slug}")
        head = view.get("head") or {}
        origin = next((o for o in (head.get("publication") or {}).get("derivedFrom") or []
                       if o.get("kind") == "workspace-studio-revision"), {})
        same_refs = [(r["objectId"], r["role"], r["pin"]) for r in head.get("references") or []] == \
                    [(r["objectId"], r["role"], r["pin"]) for r in refs]
        if (origin.get("documentId"), origin.get("revision"), origin.get("documentSha256")) == (
                document_id, pub["revision"], pub["markdownSHA256"]) and same_refs \
                and (head.get("publication") or {}).get("type") == body.publicationType:
            return JSONResponse({"researchRevision": view.get("headRevision"), "created": False,
                                 "notCarried": payload["notCarried"]}, headers=H)
        created = call(ident, "POST", f"/editorial/articles/{slug}/revisions", {
            "baseRevision": view.get("headRevision") or 0, "title": payload["title"], "summary": payload["summary"],
            "sections": payload["sections"], "references": refs, "changeSummary": payload["changeSummary"],
            "publication": payload["publication"]})
        record(ident.user_key, project_id, document_id, receipt_entry(
            "revision-pushed", created, studioRevision=pub["revision"], studioSha256=pub["markdownSHA256"]),
            f"research-output-revision-{document_id}-{created.get('revision')}")
        return JSONResponse({"researchRevision": created.get("revision"), "documentSha256": created.get("documentSha256"),
                             "subjectRef": created.get("subjectRef"), "created": True,
                             "notCarried": payload["notCarried"]}, status_code=201, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/submit")
    def submit(project_id: str, document_id: str, body: ResearchRevisionIn, request: Request):
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        slug = quote(binding["articleSlug"], safe="")
        done = call(ident, "POST", f"/editorial/articles/{slug}/revisions/{body.researchRevision}/submit")
        record(ident.user_key, project_id, document_id, receipt_entry("submitted", done, researchRevision=body.researchRevision),
               f"research-output-submit-{document_id}-{body.researchRevision}")
        return JSONResponse(done, headers=H)

    def _subject_for(ident, binding: dict, revision: int) -> str:
        view = call(ident, "GET", f"/editorial/articles/{quote(binding['articleSlug'], safe='')}")
        if view.get("submittedRevision") != revision:
            raise HTTPException(409, "Only the Research revision currently in review can be approved.")
        rev = next((r for r in view.get("revisions") or [] if r.get("revision") == revision), None)
        if rev is None or not rev.get("subjectRef"):
            raise HTTPException(409, "Research has no reviewable subject for that revision.")
        return rev["subjectRef"]

    @router.post("/projects/{project_id}/outputs/{document_id}/approval-requests")
    def request_approval(project_id: str, document_id: str, body: ApprovalIn, request: Request):
        """Raise a Workspace approval request for the exact Research revision in review."""
        from . import research_approvals as ra
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        subject = _subject_for(ident, binding, body.researchRevision)
        return JSONResponse(ra.create_request_route(ra.ApprovalRequestIn(
            projectId=project_id, dimension=body.dimension, subjectRef=subject,
            subjectTitle=f"{binding['articleSlug']} revision {body.researchRevision}", reason=body.reason), ident),
            status_code=201, headers=H)

    @router.get("/projects/{project_id}/outputs/{document_id}/approval-requests")
    def list_approvals(project_id: str, document_id: str, request: Request):
        from . import research_approvals as ra
        ident = identity(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        items = ra.list_requests_route(role="owner", status="any", identity=ident)["items"]
        prefix = f"{binding['articleSlug']} revision "
        return JSONResponse({"items": [i for i in items if i["projectId"] == project_id
                                       and str(i.get("subjectTitle") or "").startswith(prefix)]}, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/approvals/attach")
    def attach(project_id: str, document_id: str, body: AttachIn, request: Request):
        """Hand Research the signed record of a decided approval for the revision in review."""
        from . import research_approvals as ra
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        signed = ra.record_route(body.approvalId, ident)
        subject = _subject_for(ident, binding, body.researchRevision)
        if signed.get("subjectRef") != subject or signed.get("projectId") != project_id:
            raise HTTPException(409, "That approval is for a different revision or project.")
        dimension = signed.get("dimension")
        if dimension not in DIMENSIONS:
            raise HTTPException(422, "That approval is not an article approval.")
        slug = quote(binding["articleSlug"], safe="")
        done = call(ident, "POST", f"/editorial/articles/{slug}/revisions/{body.researchRevision}/approvals/{dimension}",
                    {"record": signed})
        record(ident.user_key, project_id, document_id, receipt_entry(
            "approval-recorded", done, researchRevision=body.researchRevision, dimension=dimension,
            approvalId=body.approvalId), f"research-output-approval-{document_id}-{body.approvalId}")
        return JSONResponse(done, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/publish")
    def publish(project_id: str, document_id: str, body: PublishIn, request: Request):
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        if body.confirmArticleSlug != binding["articleSlug"]:
            raise HTTPException(422, "Type the article identifier to confirm public release.")
        slug = quote(binding["articleSlug"], safe="")
        done = call(ident, "POST", f"/editorial/articles/{slug}/revisions/{body.researchRevision}/publish")
        record(ident.user_key, project_id, document_id, receipt_entry("published", done, researchRevision=body.researchRevision),
               f"research-output-publish-{document_id}-{body.researchRevision}")
        return JSONResponse(done, headers=H)

    def lifecycle(action: str, project_id: str, document_id: str, request: Request, payload: dict, confirm: str | None):
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        if confirm is not None and confirm != binding["articleSlug"]:
            raise HTTPException(422, "Type the article identifier to confirm withdrawal.")
        done = call(ident, "POST", f"/editorial/articles/{quote(binding['articleSlug'], safe='')}/{action}", payload)
        record(ident.user_key, project_id, document_id, receipt_entry(action + "ed" if action != "withdraw" else "withdrawn", done),
               f"research-output-{action}-{document_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}")
        return JSONResponse(done, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/unlist")
    def unlist(project_id: str, document_id: str, body: ReasonIn, request: Request):
        return lifecycle("unlist", project_id, document_id, request, {"reason": body.reason}, None)

    @router.post("/projects/{project_id}/outputs/{document_id}/relist")
    def relist(project_id: str, document_id: str, body: ReasonIn, request: Request):
        return lifecycle("relist", project_id, document_id, request, {"reason": body.reason}, None)

    @router.post("/projects/{project_id}/outputs/{document_id}/withdraw")
    def withdraw(project_id: str, document_id: str, body: WithdrawIn, request: Request):
        return lifecycle("withdraw", project_id, document_id, request,
                         {"reason": body.reason, "publicNotice": body.publicNotice}, body.confirmArticleSlug)

    @router.get("/projects/{project_id}/outputs/{document_id}/receipts")
    def receipts(project_id: str, document_id: str, request: Request):
        ident = identity(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        research = call(ident, "GET", f"/editorial/articles/{quote(binding['articleSlug'], safe='')}/receipts")
        return JSONResponse({"workspace": binding.get("receipts") or [], "research": research.get("items") or []},
                            headers=H)

    # Cited evidence and the Research area pass the same approval rules as the article: requests name the exact
    # current subject Research reports, and only Research decides whether the signed records release them.
    def _owned_project(ident, project_id: str) -> None:
        with deps["session"]() as db:
            deps["project"](db, ident.user_key, project_id)

    def _object_subject(ident, object_id: str) -> tuple[str, dict]:
        obj = call(ident, "GET", f"/console/objects/{quote(object_id, safe='')}")
        if not obj.get("subjectRef"):
            raise HTTPException(409, "Research has no reviewable subject for that object.")
        return obj["subjectRef"], obj

    @router.get("/projects/{project_id}/research-objects/{object_id}")
    def research_object(project_id: str, object_id: str, request: Request):
        from . import research_approvals as ra
        ident = identity(request)
        _owned_project(ident, project_id)
        subject, obj = _object_subject(ident, object_id)
        items = [i for i in ra.list_requests_route(role="owner", status="any", identity=ident)["items"]
                 if i["subjectRef"] == subject and i["projectId"] == project_id]
        return JSONResponse({"object": {k: obj.get(k) for k in ("id", "kind", "title", "visibility", "reviewState",
                                                                 "approvals", "reproduction", "verification", "subjectRef")},
                             "requests": items}, headers=H)

    @router.post("/projects/{project_id}/research-objects/{object_id}/approval-requests")
    def request_object_approval(project_id: str, object_id: str, body: ObjectApprovalIn, request: Request):
        from . import research_approvals as ra
        ident = writer(request)
        _owned_project(ident, project_id)
        subject, obj = _object_subject(ident, object_id)
        return JSONResponse(ra.create_request_route(ra.ApprovalRequestIn(
            projectId=project_id, dimension=body.dimension, subjectRef=subject,
            subjectTitle=f"Research object: {str(obj.get('title') or object_id)[:200]}", reason=body.reason), ident),
            status_code=201, headers=H)

    @router.post("/projects/{project_id}/research-objects/{object_id}/approvals/attach")
    def attach_object_approval(project_id: str, object_id: str, body: ObjectAttachIn, request: Request):
        from . import research_approvals as ra
        ident = writer(request)
        _owned_project(ident, project_id)
        signed = ra.record_route(body.approvalId, ident)
        subject, _ = _object_subject(ident, object_id)
        if signed.get("subjectRef") != subject or signed.get("projectId") != project_id \
                or signed.get("dimension") not in DIMENSIONS:
            raise HTTPException(409, "That approval is for a different object, revision or project.")
        return JSONResponse(call(ident, "POST", f"/console/objects/{quote(object_id, safe='')}/approvals/"
                                 f"{signed['dimension']}", {"record": signed}), headers=H)

    @router.post("/projects/{project_id}/research-objects/{object_id}/release")
    def release_object(project_id: str, object_id: str, request: Request):
        """Release cited evidence for publication. Research applies its own rule; nothing is public until the
        article that cites it, and its area, are published."""
        ident = writer(request)
        _owned_project(ident, project_id)
        return JSONResponse(call(ident, "POST", f"/console/objects/{quote(object_id, safe='')}/public-projection"),
                            headers=H)

    @router.get("/projects/{project_id}/outputs/{document_id}/area")
    def area(project_id: str, document_id: str, request: Request):
        from . import research_approvals as ra
        ident = identity(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        view = call(ident, "GET", f"/editorial/areas/{quote(binding['areaSlug'], safe='')}")
        items = [i for i in ra.list_requests_route(role="owner", status="any", identity=ident)["items"]
                 if i["subjectRef"] == view.get("subjectRef")]
        return JSONResponse({"area": {k: view.get(k) for k in ("slug", "title", "summary", "visibility", "subjectRef")},
                             "requests": items}, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/area/approval-requests")
    def request_area(project_id: str, document_id: str, body: ReasonOptionalIn, request: Request):
        from . import research_approvals as ra
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        view = call(ident, "GET", f"/editorial/areas/{quote(binding['areaSlug'], safe='')}")
        return JSONResponse(ra.create_request_route(ra.ApprovalRequestIn(
            projectId=project_id, dimension="area-publication", subjectRef=str(view.get("subjectRef") or ""),
            subjectTitle=f"Research area: {binding['areaSlug']}", reason=body.reason), ident), status_code=201, headers=H)

    @router.post("/projects/{project_id}/outputs/{document_id}/area/publish")
    def publish_area(project_id: str, document_id: str, body: AreaPublishIn, request: Request):
        from . import research_approvals as ra
        ident = writer(request)
        with deps["session"]() as db:
            _, binding = bound(db, ident.user_key, project_id, document_id)
        if body.confirmAreaSlug != binding["areaSlug"]:
            raise HTTPException(422, "Type the area identifier to confirm publishing the Research area.")
        signed = ra.record_route(body.approvalId, ident)
        done = call(ident, "POST", f"/editorial/areas/{quote(binding['areaSlug'], safe='')}/publish", {"record": signed})
        record(ident.user_key, project_id, document_id, receipt_entry("area-published", done, area=binding["areaSlug"]),
               f"research-output-area-{document_id}-{body.approvalId}")
        return JSONResponse(done, headers=H)

    @router.get("/research-objects")
    def research_objects(request: Request):
        """The signed-in person's own Research objects that a revision may cite (Research Console graph)."""
        ident = identity(request)
        graph = call(ident, "GET", "/console/graph")
        nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else graph.get("items") or []
        return JSONResponse({"items": [{k: n.get(k) for k in ("id", "kind", "title", "reviewState", "visibility")
                                        if k in n} for n in nodes if isinstance(n, dict)][:500]}, headers=H)

    # Reviewers: the approval inbox and decisions, through the existing SC-ED-01 rules (no self-approval, grants,
    # step-up where SC Identity is deployed, exact-revision confirmation).
    @router.get("/research-approvals/inbox")
    def inbox(request: Request):
        from . import research_approvals as ra
        ident = identity(request)
        return JSONResponse(ra.list_requests_route(role="approver", status="pending", identity=ident), headers=H)

    @router.post("/research-approvals/{approval_id}/decide")
    def decide(approval_id: str, body: DecideIn, request: Request):
        from . import research_approvals as ra
        ident = writer(request)
        return JSONResponse(ra.decide_route(approval_id, ra.DecisionIn(**body.model_dump()), request, ident), headers=H)

    return router
