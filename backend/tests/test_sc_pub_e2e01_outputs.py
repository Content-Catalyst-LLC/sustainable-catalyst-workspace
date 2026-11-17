"""SC-PUB-ENDTOEND-01 — Outputs & Publishing routes against a fake Research that verifies every signed session.

Synthetic owners and documents, an in-memory owner-scoped project store and an httpx MockTransport standing in for
Research's editorial API. Not a PostgreSQL or production acceptance; those run in the isolated staging gate.
"""
import base64
import json
import os
import secrets
from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace

import httpx
import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-pub-e2e01-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ["SC_WORKSPACE_RESEARCH_EXPORT_ENABLED"] = "true"
os.environ["SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE"] = SEED_FILE
os.environ["SC_WORKSPACE_RESEARCH_SESSION_METHODS"] = "erw-account-session"

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402
from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import research_access, research_exports as rx, research_outputs as ro, security  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.reporting_publication import research_revision  # noqa: E402
from app.utils import canonical_bytes  # noqa: E402

ORIGIN = "https://workspace.sustainablecatalyst.com"
RESEARCH = "https://research-api.example.org"


def _doc(document_id, revision, markdown, kind="report"):
    import hashlib
    return {"schema": "sc-scientific-publication/1.0", "documentId": document_id, "revision": revision,
            "title": "Metrics overview", "markdown": markdown, "publicationType": kind,
            "markdownSHA256": hashlib.sha256(markdown.encode()).hexdigest(), "createdAt": "2026-11-16T00:00:00+00:00",
            "projectRevision": revision, "citations": None, "scientificStatus": "unreviewed",
            "rightsStatus": "not-redistribution-approved"}


class FakeResearch:
    """Just enough of Research's editorial contract; it trusts nothing it cannot verify."""

    def __init__(self):
        self.articles, self.calls, self.subjects = {}, [], []
        self.refuse_publish = None

    def verify(self, header):
        scheme, _, value = (header or "").partition(" ")
        assert scheme == "SC-Workspace"
        doc = json.loads(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)))
        body = {k: v for k, v in doc.items() if k != "signature"}
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
        pub.verify(rx._b64d(doc["signature"]["value"]), research_access.SESSION_SCHEMA.encode() + b"\n" + canonical_bytes(body))
        lifetime = datetime.fromisoformat(body["expiresAt"]) - datetime.fromisoformat(body["issuedAt"])
        assert lifetime.total_seconds() <= 300 and body["authentication"] == "erw-account-session"
        return body["subject"]

    def view(self, slug):
        a = self.articles[slug]
        revs = [{"revision": n, "documentSha256": f"{n:064x}", "subjectRef": f"research-object:obj-{slug}-{n}#{n:064x}",
                 "signedApprovals": {d: d in a["approved"].get(n, set()) for d in ro.DIMENSIONS}}
                for n in range(1, len(a["revisions"]) + 1)]
        return {"slug": slug, "area": {"slug": a["area"], "visibility": "approved"}, "headRevision": len(a["revisions"]),
                "submittedRevision": a["submitted"], "publishedRevision": a["published"], "reviewStatus": a["review"],
                "publicationStatus": a["status"], "entryState": a["status"], "revisions": revs,
                "head": a["revisions"][-1] if a["revisions"] else None, "headReferences": []}

    def __call__(self, request: httpx.Request):
        subject = self.verify(request.headers.get("authorization"))
        self.subjects.append(subject)
        path = request.url.path.removeprefix("/api/research/v1")
        body = json.loads(request.content) if request.content else {}
        self.calls.append((request.method, path))
        parts = path.strip("/").split("/")

        def ok(data):
            return httpx.Response(200, json=data)

        if path == "/editorial/articles" and request.method == "POST":
            a = self.articles.get(body["slug"])
            if a and a["owner"] != subject:
                return httpx.Response(409, json={"detail": "This article slug is not available in that Research area"})
            if not a:
                self.articles[body["slug"]] = {"owner": subject, "area": body["areaSlug"], "revisions": [],
                                               "submitted": None, "published": None, "review": "draft",
                                               "status": "draft", "approved": {}, "ws": body["workspaceProjectId"]}
            return ok({"slug": body["slug"], "area": body["areaSlug"], "created": a is None})
        if path.startswith("/console/objects/"):
            oid = parts[2]
            if len(parts) == 3:
                return ok({"id": oid, "pin": "f" * 64, "title": "Synthetic dataset", "kind": "dataset",
                           "visibility": "private", "subjectRef": f"research-object:{oid}#{'c' * 64}"})
            if parts[3] == "approvals":
                assert body["record"]["subjectRef"] == f"research-object:{oid}#{'c' * 64}"
                return ok({"dimension": parts[4], "signed": True})
            if parts[3] == "public-projection":
                return httpx.Response(403, json={"detail": "Missing signed Workspace approvals: rights"})
        if path.startswith("/editorial/areas/"):
            if request.method == "GET":
                return ok({"slug": parts[2], "title": "Metrics", "visibility": "private",
                           "subjectRef": f"research-area:area-1#{'d' * 64}"})
            return ok({"slug": parts[2], "visibility": "approved"})
        slug = parts[2] if len(parts) > 2 else ""
        a = self.articles.get(slug)
        if a is None or a["owner"] != subject:
            return httpx.Response(404, json={"detail": "Research article not found"})
        if request.method == "GET" and len(parts) == 3:
            return ok(self.view(slug))
        if parts[3:] == ["revisions"]:
            if body["baseRevision"] != len(a["revisions"]):
                return httpx.Response(409, json={"detail": "reload before revising"})
            a["revisions"].append({"title": body["title"], "references": body["references"],
                                   "publication": body["publication"], "sections": body["sections"]})
            a["submitted"], a["review"] = None, "draft"
            n = len(a["revisions"])
            return ok({"revision": n, "documentSha256": f"{n:064x}", "subjectRef": f"research-object:obj-{slug}-{n}#{n:064x}"})
        if parts[3] == "revisions" and parts[5] == "submit":
            a["submitted"], a["review"] = int(parts[4]), "in-review"
            return ok({"revision": int(parts[4])})
        if parts[3] == "revisions" and parts[5] == "approvals":
            a["approved"].setdefault(int(parts[4]), set()).add(parts[6])
            return ok({"revision": int(parts[4]), "dimension": parts[6], "recordSha256": "a" * 64})
        if parts[3] == "revisions" and parts[5] == "publish":
            if self.refuse_publish:
                return httpx.Response(403, json={"detail": self.refuse_publish})
            n = int(parts[4])
            a["published"], a["status"], a["submitted"], a["review"] = n, "published", None, "published"
            return ok({"slug": slug, "publishedRevision": n, "publicationStatus": "published",
                       "receipt": {"schema": "sc-research-release-receipt/1.0", "action": "article-published",
                                   "article": slug, "seq": 7, "eventSha256": "e" * 64}})
        if parts[3] in ("unlist", "relist", "withdraw"):
            a["status"] = {"unlist": "unlisted", "relist": "published", "withdraw": "withdrawn"}[parts[3]]
            return ok({"slug": slug, "publicationStatus": a["status"],
                       "receipt": {"schema": "sc-research-release-receipt/1.0", "action": "article-" + parts[3]}})
        if parts[3] == "receipts":
            return ok({"items": [{"action": "article-published"}]})
        return httpx.Response(404, json={"detail": "not found"})


@pytest.fixture
def env(monkeypatch):
    get_settings.cache_clear()
    rx._key.cache_clear()
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_API_ORIGIN", RESEARCH)
    get_settings.cache_clear()
    research = FakeResearch()
    monkeypatch.setattr(ro, "TRANSPORT", httpx.MockTransport(research))
    store = {("owner-a", "metrics"): {"revision": 3, "project": {"objects": [
        {"id": "p1", "type": "scientific-publication", "publication": _doc("publication-overview", 1, "# Overview\n\nOne.")},
        {"id": "p2", "type": "scientific-publication", "publication": _doc("publication-report", 1, "# Report\n\nPrivate.")},
    ]}, "history": {}}}
    store[("owner-a", "metrics")]["history"] = {("publication-overview", 1): _doc("publication-overview", 1, "# Overview\n\nOne."),
                                               ("publication-report", 1): _doc("publication-report", 1, "# Report\n\nPrivate.")}

    def subject(request: Request):
        owner = request.headers.get("x-test-owner", "")
        if owner not in ("owner-a", "owner-b"):
            raise HTTPException(401, "A valid Workspace browser session is required.")
        return owner

    monkeypatch.setattr(security, "_session_identity", lambda request: security.ServiceIdentity(
        request.headers.get("x-test-owner"), "workspace-user:" + request.headers.get("x-test-owner", ""),
        "workspace-user", "session", request.headers.get("x-test-auth", "erw-account-session")))

    def write(request: Request):
        if request.headers.get("origin") != ORIGIN:
            raise HTTPException(403, "Research write origin is not authorized.")

    def project(db, owner, project_id):
        value = store.get((owner, project_id))
        if value is None:
            raise HTTPException(404, "Private project was not found.")
        return SimpleNamespace(revision=value["revision"], project_id=project_id, title="Metrics",
                               package={"project": deepcopy(value["project"])})

    def save(db, owner, row, updated, operation):
        value = store[(owner, row.project_id)]
        if row.revision != value["revision"]:
            raise HTTPException(409, "Workspace project changed.")
        value["revision"] += 1
        value["project"] = deepcopy(updated)
        return project(db, owner, row.project_id)

    def saved(db, owner, project_id, document_id, rev=None):
        row = project(db, owner, project_id)
        doc = store[(owner, project_id)]["history"].get((document_id, rev))
        if doc is None:
            raise HTTPException(404, "Publication not found in this project.")
        return row, doc

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def documents(package):
        return [{"documentId": o["publication"]["documentId"], "title": o["publication"]["title"],
                 "revision": o["publication"]["revision"], "publicationType": o["publication"]["publicationType"]}
                for o in package["project"]["objects"] if o.get("type") == "scientific-publication"]

    app = FastAPI()
    app.include_router(ro.build_router({"subject": subject, "write": write, "project": project, "locked_project": project,
                                        "session": Session, "headers": {"Cache-Control": "private, no-store"},
                                        "saved": saved, "store": save, "research_revision": research_revision,
                                        "documents": documents}))
    yield SimpleNamespace(client=TestClient(app), research=research, store=store)
    get_settings.cache_clear()


def h(owner="owner-a", write=True):
    return {"x-test-owner": owner, **({"origin": ORIGIN} if write else {})}


BASE = "/projects/metrics/outputs"


def bind(env, doc="publication-overview", slug="metrics-public-overview"):
    return env.client.post(f"{BASE}/{doc}/bind", headers=h(),
                           json={"areaSlug": "metrics-of-sustainable-development", "articleSlug": slug})


def test_not_configured_disables_every_control(env, monkeypatch):
    monkeypatch.delenv("SC_WORKSPACE_RESEARCH_API_ORIGIN")
    get_settings.cache_clear()
    out = env.client.get(BASE, headers=h(write=False)).json()
    assert out["researchConfigured"] is False
    assert all(not v for o in out["outputs"] for v in o["controls"].values())
    assert env.research.calls == []


def test_http_research_origin_refused_without_explicit_staging_flag(env, monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_API_ORIGIN", "http://research-api:8000")
    get_settings.cache_clear()
    assert bind(env).status_code == 503
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_API_ALLOW_HTTP", "true")
    get_settings.cache_clear()
    assert ro.research_origin() == "http://research-api:8000"


def test_bind_is_idempotent_signed_and_owner_scoped(env):
    first = bind(env)
    assert first.status_code == 201 and first.json()["created"] is True
    assert env.research.subjects == ["workspace-user:owner-a"]
    again = bind(env)
    assert again.status_code == 200 and again.json()["created"] is False
    assert bind(env, slug="another-slug").status_code == 409  # one output, one article
    assert bind(env, doc="publication-report").status_code == 409  # siblings never share an article
    # Another owner cannot see or bind this project, and Research is never called for them.
    calls = len(env.research.calls)
    assert env.client.get(BASE, headers=h("owner-b", False)).status_code == 404
    assert bind_as(env, "owner-b").status_code == 404
    assert len(env.research.calls) == calls


def bind_as(env, owner):
    return env.client.post(f"{BASE}/publication-overview/bind", headers=h(owner),
                           json={"areaSlug": "metrics-of-sustainable-development", "articleSlug": "x"})


def test_writes_need_the_workspace_origin_and_a_session(env):
    assert env.client.post(f"{BASE}/publication-overview/bind", headers=h(write=False),
                           json={"areaSlug": "a", "articleSlug": "b"}).status_code == 403
    assert env.client.get(BASE).status_code == 401
    assert env.research.calls == []


def test_password_only_sign_in_refused_unless_admitted(env, monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_SESSION_METHODS", "")
    get_settings.cache_clear()
    assert bind(env).status_code == 403
    assert env.research.calls == []


def test_exact_revision_push_is_idempotent_and_keeps_sibling_private(env):
    bind(env)
    push = lambda: env.client.post(f"{BASE}/publication-overview/research-revisions", headers=h(), json={
        "studioRevision": 1, "publicationType": "report", "references": [{"objectId": "obj-1", "role": "dataset"}]})
    first = push()
    assert first.status_code == 201 and first.json()["researchRevision"] == 1
    sent = env.research.articles["metrics-public-overview"]["revisions"][0]
    origin = sent["publication"]["derivedFrom"][0]
    assert origin["documentId"] == "publication-overview" and origin["revision"] == 1
    assert origin["documentSha256"] == _doc("publication-overview", 1, "# Overview\n\nOne.")["markdownSHA256"]
    assert sent["references"] == [{"objectId": "obj-1", "role": "dataset", "pin": "f" * 64}]
    again = push()
    assert again.status_code == 200 and again.json()["created"] is False
    assert len(env.research.articles["metrics-public-overview"]["revisions"]) == 1
    listing = env.client.get(BASE, headers=h(write=False)).json()["outputs"]
    sibling = next(o for o in listing if o["documentId"] == "publication-report")
    assert sibling["binding"] is None and sibling["research"] is None
    assert list(env.research.articles) == ["metrics-public-overview"]


def _to_review(env, monkeypatch, approvals=ro.DIMENSIONS):
    from app import research_approvals as ra
    bind(env)
    env.client.post(f"{BASE}/publication-overview/research-revisions", headers=h(), json={
        "studioRevision": 1, "publicationType": "report", "references": [{"objectId": "obj-1", "role": "dataset"}]})
    assert env.client.post(f"{BASE}/publication-overview/submit", headers=h(), json={"researchRevision": 1}).status_code == 200
    subject = env.research.view("metrics-public-overview")["revisions"][0]["subjectRef"]
    records = {f"apr-{d}": {"subjectRef": subject, "projectId": "metrics", "dimension": d} for d in approvals}
    monkeypatch.setattr(ra, "record_route", lambda approval_id, identity: records[approval_id])
    for d in approvals:
        r = env.client.post(f"{BASE}/publication-overview/approvals/attach", headers=h(),
                            json={"researchRevision": 1, "approvalId": f"apr-{d}"})
        assert r.status_code == 200, r.text
    return records


def test_stale_or_foreign_approval_is_refused(env, monkeypatch):
    from app import research_approvals as ra
    _to_review(env, monkeypatch, approvals=())
    monkeypatch.setattr(ra, "record_route", lambda approval_id, identity: {
        "subjectRef": "research-object:other#" + "0" * 64, "projectId": "metrics", "dimension": "rights"})
    r = env.client.post(f"{BASE}/publication-overview/approvals/attach", headers=h(),
                        json={"researchRevision": 1, "approvalId": "apr-x"})
    assert r.status_code == 409
    assert not any(p.endswith("/approvals/rights") for _, p in env.research.calls)


def test_publish_needs_confirmation_and_records_researchs_receipt(env, monkeypatch):
    _to_review(env, monkeypatch)
    out = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]
    assert out["controls"]["publish"] is True and out["research"]["publicUrl"] is None
    bad = env.client.post(f"{BASE}/publication-overview/publish", headers=h(),
                          json={"researchRevision": 1, "confirmArticleSlug": "wrong"})
    assert bad.status_code == 422
    r = env.client.post(f"{BASE}/publication-overview/publish", headers=h(),
                        json={"researchRevision": 1, "confirmArticleSlug": "metrics-public-overview"})
    assert r.status_code == 200 and r.json()["receipt"]["eventSha256"] == "e" * 64
    out = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]
    assert out["research"]["publicationStatus"] == "published"
    assert out["research"]["publicUrl"].endswith("?article=metrics-public-overview")
    assert out["controls"]["unlist"] and out["controls"]["withdraw"] and not out["controls"]["relist"]
    receipts = out["binding"]["receipts"]
    assert receipts[-1]["action"] == "published" and receipts[-1]["receipt"]["eventSha256"] == "e" * 64


def test_research_refusal_is_reported_and_nothing_recorded(env, monkeypatch):
    _to_review(env, monkeypatch, approvals=("scientific",))
    env.research.refuse_publish = "Missing signed Workspace approvals for this revision: rights"
    before = deepcopy(env.store[("owner-a", "metrics")]["project"])
    r = env.client.post(f"{BASE}/publication-overview/publish", headers=h(),
                        json={"researchRevision": 1, "confirmArticleSlug": "metrics-public-overview"})
    assert r.status_code == 403 and "rights" in r.json()["detail"]
    assert env.store[("owner-a", "metrics")]["project"] == before


def test_unlist_relist_and_final_withdrawal(env, monkeypatch):
    _to_review(env, monkeypatch)
    env.client.post(f"{BASE}/publication-overview/publish", headers=h(),
                    json={"researchRevision": 1, "confirmArticleSlug": "metrics-public-overview"})
    assert env.client.post(f"{BASE}/publication-overview/unlist", headers=h(), json={"reason": "test"}).json()["publicationStatus"] == "unlisted"
    out = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]
    assert out["controls"]["relist"] and not out["controls"]["unlist"]
    assert env.client.post(f"{BASE}/publication-overview/relist", headers=h(), json={"reason": "t"}).status_code == 200
    assert env.client.post(f"{BASE}/publication-overview/withdraw", headers=h(), json={
        "reason": "t", "publicNotice": "Withdrawn.", "confirmArticleSlug": "nope"}).status_code == 422
    r = env.client.post(f"{BASE}/publication-overview/withdraw", headers=h(), json={
        "reason": "t", "publicNotice": "Withdrawn.", "confirmArticleSlug": "metrics-public-overview"})
    assert r.json()["publicationStatus"] == "withdrawn"
    out = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]
    assert not any(out["controls"][k] for k in ("publish", "unlist", "relist", "withdraw", "pushRevision"))
    assert [x["action"] for x in out["binding"]["receipts"]][-4:] == ["published", "unlisted", "relisted", "withdrawn"]


def test_concurrent_research_revision_is_a_conflict_and_nothing_recorded(env):
    bind(env)
    view = env.research.view

    def racing(slug):
        out = view(slug)
        env.research.articles[slug]["revisions"].append({"title": "other", "references": [], "publication": {}})
        env.research.view = view
        return out

    env.research.view = racing
    before = deepcopy(env.store[("owner-a", "metrics")]["project"])
    r = env.client.post(f"{BASE}/publication-overview/research-revisions", headers=h(), json={
        "studioRevision": 1, "publicationType": "report", "references": []})
    assert r.status_code == 409
    assert env.store[("owner-a", "metrics")]["project"] == before


def test_studio_page_carries_the_panel_and_its_script_under_the_csp_hash(monkeypatch):
    import base64 as b64
    import hashlib
    import re
    from starlette.requests import Request as R
    from app import reporting_publication as rp
    monkeypatch.setattr(rp, "_subject", lambda request: "owner-a")
    page = rp.publication_ui(R({"type": "http", "headers": []}))
    html = page.body.decode()
    assert 'id="outputsPanel"' in html and 'id="outputsOpen"' in html
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    assert "/outputs" in script and "research-approvals/inbox" in script
    digest = b64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    assert f"'sha256-{digest}'" in page.headers["content-security-policy"]
    assert "innerHTML" not in script.split("SC-PUB-ENDTOEND-01")[1]


def test_cited_evidence_and_area_use_the_same_exact_subject_rules(env, monkeypatch):
    from app import research_approvals as ra
    bind(env)
    subject = f"research-object:obj-1#{'c' * 64}"
    seen = {}
    monkeypatch.setattr(ra, "create_request_route", lambda payload, identity: seen.setdefault("req", payload) and {"item": {}})
    r = env.client.post("/projects/metrics/research-objects/obj-1/approval-requests", headers=h(), json={"dimension": "rights"})
    assert r.status_code == 201 and seen["req"].subjectRef == subject and seen["req"].projectId == "metrics"
    monkeypatch.setattr(ra, "record_route", lambda approval_id, identity: {
        "subjectRef": f"research-object:obj-1#{'0' * 64}", "projectId": "metrics", "dimension": "rights"})
    stale = env.client.post("/projects/metrics/research-objects/obj-1/approvals/attach", headers=h(), json={"approvalId": "a"})
    assert stale.status_code == 409
    monkeypatch.setattr(ra, "record_route", lambda approval_id, identity: {
        "subjectRef": subject, "projectId": "metrics", "dimension": "rights"})
    assert env.client.post("/projects/metrics/research-objects/obj-1/approvals/attach", headers=h(),
                           json={"approvalId": "a"}).status_code == 200
    refused = env.client.post("/projects/metrics/research-objects/obj-1/release", headers=h())
    assert refused.status_code == 403 and "rights" in refused.json()["detail"]  # Research's rule, reported as is
    # Another owner's project: nothing reaches Research.
    calls = len(env.research.calls)
    assert env.client.post("/projects/metrics/research-objects/obj-1/release", headers=h("owner-b")).status_code == 404
    assert len(env.research.calls) == calls
    monkeypatch.setattr(ra, "record_route", lambda approval_id, identity: {"dimension": "area-publication"})
    bad = env.client.post(f"{BASE}/publication-overview/area/publish", headers=h(),
                          json={"approvalId": "x", "confirmAreaSlug": "wrong"})
    assert bad.status_code == 422
    ok = env.client.post(f"{BASE}/publication-overview/area/publish", headers=h(),
                         json={"approvalId": "x", "confirmAreaSlug": "metrics-of-sustainable-development"})
    assert ok.status_code == 200 and ok.json()["visibility"] == "approved"


BACKEND = "http://sc-workspace-backend:8089"
ISSUER = BACKEND + "/v1/research-access/session"


def _issuer_env(env, monkeypatch, answer):
    """The Studio without the signing key: sessions come from the backend issuer (here a MockTransport)."""
    pinned = rx.public_key_info()  # Research keeps the public key it pins; only the private key leaves this process
    monkeypatch.setattr(rx, "public_key_info", lambda: pinned)
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_SIGNING_BACKEND_URL", BACKEND)
    monkeypatch.setenv("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", "/nonexistent/no-key-in-the-studio")
    get_settings.cache_clear()
    seen = []

    def issuer(request: httpx.Request):
        seen.append(request)
        return answer(request)
    monkeypatch.setattr(ro, "ISSUER_TRANSPORT", httpx.MockTransport(issuer))
    return seen


def _backend_signed(subject="workspace-user:owner-a", method="erw-account-session"):
    # Signed with the test key, as the backend would; the Studio process itself is not given the key file.
    from datetime import timedelta, timezone
    now = datetime.now(timezone.utc)
    return rx.sign_document(research_access.SESSION_SCHEMA, {
        "schema": research_access.SESSION_SCHEMA, "issuer": rx.ISSUER, "audience": rx.AUDIENCE, "sessionId": "rss_t",
        "subject": subject, "authentication": method, "issuedAt": now.isoformat(),
        "expiresAt": (now + timedelta(seconds=300)).isoformat()})


def test_studio_obtains_the_session_from_the_backend_with_the_persons_cookie(env, monkeypatch):
    doc = _backend_signed()  # signed before the Studio loses the key
    seen = _issuer_env(env, monkeypatch, lambda r: httpx.Response(200, json=doc))
    with pytest.raises((HTTPException, OSError)):  # this process cannot sign a session itself
        research_access.issue_session(security.ServiceIdentity("owner-a", "workspace-user:owner-a", "workspace-user",
                                                               "session", "erw-account-session"))
    env.client.cookies.set("sc_workspace_session", "cookie-of-owner-a")
    first = bind(env)
    assert first.status_code == 201, first.text
    assert env.research.subjects == ["workspace-user:owner-a"]  # Research verified the backend's signature
    assert seen and all(r.method == "POST" and str(r.url) == ISSUER for r in seen)
    assert all(r.headers["cookie"] == "sc_workspace_session=cookie-of-owner-a" and r.headers["origin"] == ORIGIN
               for r in seen)


def test_backend_issued_session_must_name_exactly_this_person(env, monkeypatch):
    other = _backend_signed(subject="workspace-user:owner-b")
    _issuer_env(env, monkeypatch, lambda r: httpx.Response(200, json=other))
    env.client.cookies.set("sc_workspace_session", "cookie-of-owner-a")
    assert bind(env).status_code == 502
    assert env.research.calls == []


def test_backend_refusal_passes_through_and_no_cookie_is_refused(env, monkeypatch):
    _issuer_env(env, monkeypatch, lambda r: httpx.Response(403, json={"detail": {"code": "sc-identity-required",
                                                                                   "message": "Sign in."}}))
    assert bind(env).status_code == 401  # no session cookie to forward: nothing is asked of the backend
    env.client.cookies.set("sc_workspace_session", "cookie-of-owner-a")
    assert bind(env).status_code == 403
    assert env.research.calls == []


def test_approval_decisions_are_signed_by_the_backend_not_the_studio(env, monkeypatch):
    def backend(request: httpx.Request):
        if request.url.path.endswith("/decide"):
            body = json.loads(request.content)
            if body["expectedSubjectRef"] != "object:o1#sha256:" + "a" * 64:
                return httpx.Response(409, json={"ok": False, "message": "The subject changed; review it again."})
            return httpx.Response(200, json={"record": {"schema": "sc-workspace-research-approval/1.0",
                                                        "approvalId": "approval_x", "decision": body["decision"]}})
        return httpx.Response(404, json={"detail": "not found"})
    seen = _issuer_env(env, monkeypatch, backend)
    env.client.cookies.set("sc_workspace_session", "cookie-of-owner-a")
    good = {"decision": "approve", "note": "ok", "expectedSubjectRef": "object:o1#sha256:" + "a" * 64}
    out = env.client.post("/research-approvals/approval_x/decide", headers=h(), json=good)
    assert out.status_code == 200 and out.json()["record"]["decision"] == "approve"
    assert str(seen[-1].url) == BACKEND + "/v1/research-approvals/requests/approval_x/decide"
    assert seen[-1].headers["cookie"] == "sc_workspace_session=cookie-of-owner-a"
    stale = env.client.post("/research-approvals/approval_x/decide", headers=h(),
                            json={**good, "expectedSubjectRef": "object:o1#sha256:" + "b" * 64})
    assert stale.status_code == 409 and "review it again" in stale.text
    assert env.client.post("/research-approvals/approval_x/decide", headers=h(write=False), json=good).status_code == 403
