"""SC-PUB-M1 approval desk: the page and its server-side exact-revision confirmation.

The browser flow (sign-in, step-up return, re-confirmation) is exercised in the isolated staging
acceptance; the desk's pure helpers are unit-tested with Node (`tests/js/approval_desk.test.mjs`).
"""
import re
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from tests.test_research_approvals_sc_ed01 import ask, client, hdr, pg, world  # noqa: F401 (fixtures)
from app import research_approvals as ra
from app import sc_identity
from app import session_auth

BACKEND = Path(__file__).resolve().parents[1]


def test_desk_page_is_same_origin_only_with_a_strict_policy(client):
    r = client.get("/v1/desk/approvals")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html")
    csp = r.headers["content-security-policy"]
    assert "script-src 'self'" in csp and "connect-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert "'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp
    assert r.headers["x-frame-options"] == "DENY" and r.headers["cache-control"].startswith("no-store")
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", r.text), "no inline script"
    assert not re.search(r"\son[a-z]+=", r.text), "no inline event handlers"
    for name in ("approval-desk.js", "approval-desk.css"):
        a = client.get(f"/v1/desk/assets/{name}")
        assert a.status_code == 200 and a.headers["content-security-policy"] == csp
    for bad in ("index.html", "..%2Fapproval_desk.py", "approval-desk.js.map", "x.js"):
        assert client.get(f"/v1/desk/assets/{bad}").status_code == 404


def test_desk_script_never_builds_html_from_data():
    js = (BACKEND / "app/static/approval_desk/approval-desk.js").read_text()
    assert "innerHTML" not in js and "outerHTML" not in js and "insertAdjacentHTML" not in js
    assert "eval(" not in js and "new Function" not in js


def _request():
    return Request({"type": "http", "method": "POST", "path": "/", "headers": []})


def test_step_up_approval_without_exact_revision_confirmation_is_refused(monkeypatch):
    payload = {"sub": "sci", "auth": sc_identity.AUTH_METHOD, "auth_time": int(time.time()) - 5, "amr": ["pwd", "otp"]}
    monkeypatch.setattr(session_auth, "session_payload_from_request", lambda _r: payload)
    monkeypatch.setattr(sc_identity, "enabled", lambda: True)
    monkeypatch.setattr(ra, "_signing_key", lambda: None)
    monkeypatch.setattr(ra, "session_scope", lambda: pytest.fail("no database access before confirmation"))
    identity = ra.ServiceIdentity("sci", "sci", "user", "sc-identity-session", "sc-identity-oidc-session")
    with pytest.raises(HTTPException) as exc:
        ra.decide_route("approval_x", ra.DecisionIn(decision="approve"), _request(), identity)
    assert exc.value.status_code == 422 and exc.value.detail["code"] == "exact-revision-confirmation-required"


def test_rejection_needs_no_revision_confirmation():
    assert ra.DecisionIn(decision="reject").expectedSubjectRef is None


@pg
def test_confirmation_must_match_the_requests_exact_revision(client, world):
    users, project = world
    aid = ask(client, users["owner"], project, "scientific").json()["item"]["approvalId"]
    subject = client.get("/v1/research-approvals/requests?role=owner&status=pending",
                         headers=hdr(users["owner"])).json()["items"][-1]["subjectRef"]
    other = subject[:-1] + ("0" if subject[-1] != "0" else "1")
    url = f"/v1/research-approvals/requests/{aid}/decide"
    r = client.post(url, headers=hdr(users["sci"]), json={"decision": "approve", "expectedSubjectRef": other})
    assert r.status_code == 409 and r.json()["code"] == "subject-changed"
    pending = client.get("/v1/research-approvals/requests?role=owner&status=pending", headers=hdr(users["owner"])).json()
    assert aid in {i["approvalId"] for i in pending["items"]}  # nothing was decided or signed
    r = client.post(url, headers=hdr(users["sci"]), json={"decision": "approve", "expectedSubjectRef": subject})
    assert r.status_code == 200, r.text
    assert r.json()["record"]["authentication"]["revisionConfirmed"] is True
    assert r.json()["record"]["subjectRef"] == subject


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_desk_helpers_node_unit_tests():
    out = subprocess.run(["node", "--test", str(BACKEND / "tests/js/approval_desk.test.mjs")],
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-2000:]
