"""RH-PUB-01 — registering the original file behind a Studio output as a private Research source.

Reuses the SC-PUB-ENDTOEND-01 harness (in-memory owner-scoped store, a fake Research that verifies every signature).
Synthetic bytes only; Research's own registration is tested in the Research repository.
"""
import base64
import hashlib
import json

import httpx
import pytest
from fastapi import HTTPException

from tests.test_sc_pub_e2e01_outputs import BASE, FakeResearch, bind, env, h  # noqa: F401 (env is a fixture)
from app import reporting_publication, research_exports as rx, research_sources as rs
from app.utils import canonical_bytes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOC = "publication-overview"
RAW = b"PK\x03\x04 synthetic word original"
SHA = hashlib.sha256(RAW).hexdigest()
RIGHTS = {"rightsBasis": "author-owned", "rightsHolder": "Synthetic Author",
          "rightsStatement": "Written by the owner; no third-party material is reproduced."}


@pytest.fixture
def originals(env, monkeypatch):
    """Give the bound output an original Word file and let Research accept signed source records."""
    files = {"artifact-1": {"name": "Synthetic manuscript.docx", "raw": RAW, "sha": SHA}}
    for doc in [o["publication"] for o in env.store[("owner-a", "metrics")]["project"]["objects"]] + \
            list(env.store[("owner-a", "metrics")]["history"].values()):
        if doc["documentId"] == DOC:
            doc["source"] = {"artifactId": "artifact-1", "filename": "Synthetic manuscript.docx", "sha256": SHA}

    def original(db, owner, project_id, artifact_id):
        if (owner, project_id) != ("owner-a", "metrics") or artifact_id not in files:
            raise HTTPException(404, "Research source not found in this project.")
        f = files[artifact_id]
        return {"artifactId": artifact_id, "filename": f["name"], "sha256": f["sha"], "bytes": len(f["raw"])}, f["raw"]

    def saved(db, owner, project_id, document_id, rev=None):
        doc = env.store.get((owner, project_id), {}).get("history", {}).get((document_id, rev))
        if doc is None:
            raise HTTPException(404, "Publication not found in this project.")
        return None, doc

    monkeypatch.setattr(reporting_publication, "_original_asset", original)
    monkeypatch.setattr(reporting_publication, "_saved", saved)

    class Session:
        def __enter__(self):
            return None

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(rs, "session_scope", Session)
    received = []
    plain = FakeResearch.__call__

    def research(self, request: httpx.Request):
        if request.url.path.endswith("/sources") and request.method == "POST":
            subject = self.verify(request.headers.get("authorization"))
            doc = json.loads(request.content)["document"]
            body = {k: v for k, v in doc.items() if k != "signature"}
            pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
            pub.verify(rx._b64d(doc["signature"]["value"]), rs.SOURCE_SCHEMA.encode() + b"\n" + canonical_bytes(body))
            assert body["ownerScope"] == subject
            received.append(body)
            return httpx.Response(200, json={"objectId": "obj-source-1", "kind": "source", "role": "citation",
                                             "sourceSha256": body["original"]["sha256"], "visibility": "private",
                                             "pin": "9" * 64, "studioRevision": body["studioRevision"],
                                             "created": len(received) == 1})
        return plain(self, request)

    monkeypatch.setattr(FakeResearch, "__call__", research)
    return {"files": files, "received": received}


def register(env, doc=DOC, owner="owner-a", write=True, **kw):
    return env.client.post(f"{BASE}/{doc}/source-registration", headers=h(owner, write),
                           json={"studioRevision": 1, **RIGHTS, **kw})


def test_registers_the_exact_original_and_studio_revision_signed_by_workspace(env, originals):
    assert bind(env).status_code == 201
    out = register(env)
    assert out.status_code == 200, out.text
    assert out.json() == {"objectId": "obj-source-1", "kind": "source", "role": "citation", "sourceSha256": SHA,
                          "visibility": "private", "pin": "9" * 64, "created": True,
                          "studioRevision": {"documentId": DOC, "revision": 1,
                                             "markdownSHA256": hashlib.sha256(b"# Overview\n\nOne.").hexdigest()}}
    body = originals["received"][0]
    assert body["original"] == {"artifactId": "artifact-1", "sha256": SHA, "byteCount": len(RAW), "filename":
                                "Synthetic manuscript.docx", "mediaType": rs.MEDIA_TYPES[".docx"]}
    assert (body["projectId"], body["ownerScope"], body["rights"]["basis"]) == ("metrics", "workspace-user:owner-a", "author-owned")
    assert body["title"] == "Original manuscript: Metrics overview"
    receipts = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]["binding"]["receipts"]
    assert receipts[-1]["action"] == "source-registered" and receipts[-1]["sourceSha256"] == SHA
    # Registering again is idempotent in Research and adds no second receipt.
    assert register(env).json()["created"] is False
    receipts = env.client.get(BASE, headers=h(write=False)).json()["outputs"][0]["binding"]["receipts"]
    assert [r["action"] for r in receipts].count("source-registered") == 1


def test_nothing_is_signed_or_sent_for_an_unbound_foreign_or_cross_origin_request(env, originals):
    assert register(env).status_code == 404  # not bound yet
    bind(env)
    assert register(env, owner="owner-b").status_code == 404
    assert register(env, write=False).status_code == 403
    assert originals["received"] == []


@pytest.mark.parametrize("change,status,match", [
    (lambda f, env: f["artifact-1"].update(raw=b"changed bytes"), 409, "no longer matches"),
    (lambda f, env: f["artifact-1"].update(name="notes.txt"), 422, "Word"),
    (lambda f, env: env.store[("owner-a", "metrics")]["history"][(DOC, 1)].pop("source"), 409, "not imported"),
    (lambda f, env: env.store[("owner-a", "metrics")]["history"][(DOC, 1)].update(markdown="# Edited"), 409, "recorded hash"),
])
def test_the_original_and_revision_are_reverified_before_signing(env, originals, change, status, match):
    bind(env)
    change(originals["files"], env)
    out = register(env)
    assert out.status_code == status and match in out.text
    assert originals["received"] == []


def test_rights_must_be_declared_and_only_an_sc_identity_session_may_register(env, originals):
    bind(env)
    assert register(env, rightsStatement="mine").status_code == 422
    assert register(env, rightsBasis="assumed").status_code == 422
    assert register(env, studioRevision=2).status_code == 404
    out = env.client.post(f"{BASE}/{DOC}/source-registration", headers={**h(), "x-test-auth": "legacy-service-bearer"},
                          json={"studioRevision": 1, **RIGHTS})
    assert out.status_code == 403
    assert originals["received"] == []


def test_the_backend_exposes_the_signing_route_beside_research_sessions():
    from app.main import app
    assert any(getattr(r, "path", "") == "/v1/research-access/source-documents" and "POST" in r.methods
               for r in app.routes)
