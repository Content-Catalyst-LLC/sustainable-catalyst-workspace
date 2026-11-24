"""SC-SEO-INT-04 — the signed SEO Studio session Workspace issues to an allowlisted person signed in with SC Identity.

Synthetic identity provider and accounts (the SC-AUTH-02 fixtures); no network.
"""
import base64
import os
import secrets
from datetime import datetime

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-seo-int04-seo-access-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_ENABLED", "true")
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", SEED_FILE)

from cryptography.exceptions import InvalidSignature  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import auth_hygiene, research_access, research_exports as rx, sc_identity, seo_access, session_auth  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils import canonical_bytes  # noqa: E402
from test_sc_auth02_identity import OWNER_A, ORIGIN, client as _unused, env, sign_in  # noqa: E402,F401

get_settings.cache_clear()
rx._key.cache_clear()
STUDIO = "https://seo.example.org"


def verify(doc, domain=seo_access.SESSION_SCHEMA):
    body = {k: v for k, v in doc.items() if k != "signature"}
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
    pub.verify(rx._b64d(doc["signature"]["value"]), domain.encode() + b"\n" + canonical_bytes(body))
    return body


@pytest.fixture
def app_client(env, monkeypatch):
    env.settings.cors_allowed_origins = ORIGIN + "," + STUDIO
    env.settings.seo_studio_session_enabled = True
    env.settings.seo_studio_users = OWNER_A
    monkeypatch.setattr(seo_access, "get_settings", lambda: env.settings)
    monkeypatch.setattr(research_access, "get_settings", lambda: env.settings)
    app = FastAPI()
    app.add_middleware(auth_hygiene.AuthHygieneMiddleware)
    app.include_router(session_auth.router)
    app.include_router(sc_identity.router)
    app.include_router(seo_access.router)
    return TestClient(app, base_url=ORIGIN, follow_redirects=False)


def test_an_allowlisted_sc_identity_user_gets_a_short_seo_session(app_client, env):
    sign_in(app_client, env)
    r = app_client.post("/v1/seo-access/session", headers={"Origin": STUDIO})
    assert r.status_code == 200, r.text
    assert "no-store" in r.headers["cache-control"]
    body = verify(r.json())
    assert (body["schema"], body["issuer"], body["audience"]) == (
        "sc-workspace-seo-session/1.0", "sustainable-catalyst-workspace", "sc-seo-intelligence")
    assert body["subject"] == "workspace-user:" + OWNER_A
    assert body["authentication"] == "sc-identity-oidc-session"
    lifetime = datetime.fromisoformat(body["expiresAt"]) - datetime.fromisoformat(body["issuedAt"])
    assert lifetime.total_seconds() == 300


def test_an_seo_session_never_verifies_as_a_research_session(app_client, env):
    sign_in(app_client, env)
    doc = app_client.post("/v1/seo-access/session", headers={"Origin": STUDIO}).json()
    with pytest.raises(InvalidSignature):
        verify(doc, research_access.SESSION_SCHEMA)


def test_disabled_by_default_and_only_for_listed_users(app_client, env):
    sign_in(app_client, env)
    env.settings.seo_studio_users = "someone-else"
    r = app_client.post("/v1/seo-access/session", headers={"Origin": STUDIO})
    assert r.status_code == 403 and r.json()["detail"]["code"] == "seo-studio-not-authorized"
    env.settings.seo_studio_users = OWNER_A
    env.settings.seo_studio_session_enabled = False
    assert app_client.post("/v1/seo-access/session", headers={"Origin": STUDIO}).status_code == 503


def test_no_session_without_sign_in_or_from_an_unlisted_origin(app_client, env):
    assert app_client.post("/v1/seo-access/session", headers={"Origin": STUDIO}).status_code == 401
    sign_in(app_client, env)
    for headers in ({"Origin": "https://evil.example"}, {}, {"Origin": STUDIO, "Sec-Fetch-Site": "cross-site"}):
        assert app_client.post("/v1/seo-access/session", headers=headers).status_code == 403, headers


def test_the_legacy_service_identity_gets_no_seo_session(app_client, env):
    env.settings.sc_identity_required = False
    r = app_client.post("/v1/seo-access/session", headers={
        "Authorization": "Bearer " + env.settings.service_token, "X-SC-User-ID": OWNER_A})
    assert r.status_code == 403 and "sc-identity-required" in r.text
