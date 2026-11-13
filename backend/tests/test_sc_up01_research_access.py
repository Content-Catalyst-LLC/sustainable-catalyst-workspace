"""SC-UP-01 — the signed Research session Workspace issues to a person signed in with SC Identity.

Synthetic identity provider and accounts (the SC-AUTH-02 fixtures); no network.
"""
import base64
import os
import secrets
from datetime import datetime

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-up01-research-access-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_ENABLED", "true")
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", SEED_FILE)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import auth_hygiene, research_access, research_exports as rx, sc_identity, session_auth  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils import canonical_bytes  # noqa: E402
from test_sc_auth02_identity import OWNER_A, ORIGIN, client as _unused, env, sign_in  # noqa: E402,F401

get_settings.cache_clear()
rx._key.cache_clear()
RESEARCH = "https://research.example.org"


def verify(doc):
    body = {k: v for k, v in doc.items() if k != "signature"}
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
    pub.verify(rx._b64d(doc["signature"]["value"]),
               research_access.SESSION_SCHEMA.encode() + b"\n" + canonical_bytes(body))
    assert doc["signature"]["keyId"] == rx.public_key_info()["keyId"]
    return body


@pytest.fixture
def app_client(env):
    env.settings.cors_allowed_origins = ORIGIN + "," + RESEARCH
    app = FastAPI()
    app.add_middleware(auth_hygiene.AuthHygieneMiddleware)
    app.include_router(session_auth.router)
    app.include_router(sc_identity.router)
    app.include_router(research_access.router)
    return TestClient(app, base_url=ORIGIN, follow_redirects=False)


def test_a_person_signed_in_with_sc_identity_gets_a_short_signed_research_session(app_client, env):
    sign_in(app_client, env)
    r = app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH})
    assert r.status_code == 200, r.text
    assert "no-store" in r.headers["cache-control"]
    body = verify(r.json())
    assert body["schema"] == "sc-workspace-research-session/1.0"
    assert (body["issuer"], body["audience"]) == ("sustainable-catalyst-workspace", "sc-research")
    assert body["subject"] == "workspace-user:" + OWNER_A  # from the server-side identity link, never the request
    assert body["authentication"] == "sc-identity-oidc-session"
    lifetime = datetime.fromisoformat(body["expiresAt"]) - datetime.fromisoformat(body["issuedAt"])
    assert lifetime.total_seconds() == 300
    again = app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH}).json()
    assert again["sessionId"] != body["sessionId"]


def test_an_sc_access_token_also_gets_one(app_client, env):
    r = app_client.post("/v1/research-access/session",
                        headers={"Authorization": "Bearer " + env.idp.access_token()})
    assert r.status_code == 200, r.text
    assert verify(r.json())["authentication"] == "sc-identity-access-token"


def test_no_session_without_sign_in_and_none_for_a_cross_site_or_unlisted_origin(app_client, env):
    assert app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH}).status_code == 401
    sign_in(app_client, env)
    for headers in ({"Origin": "https://evil.example"}, {}, {"Origin": RESEARCH, "Sec-Fetch-Site": "cross-site"}):
        assert app_client.post("/v1/research-access/session", headers=headers).status_code == 403, headers


def test_the_legacy_service_identity_gets_no_research_session(app_client, env):
    env.settings.sc_identity_required = False
    r = app_client.post("/v1/research-access/session", headers={
        "Authorization": "Bearer " + env.settings.service_token, "X-SC-User-ID": OWNER_A})
    assert r.status_code == 403 and "sc-identity-required" in r.text


def test_sign_in_returns_to_an_allowlisted_research_page_and_nowhere_else(env):
    env.settings.cors_allowed_origins = ORIGIN + "," + RESEARCH
    assert sc_identity._safe_return_to(RESEARCH + "/discover?q=1") == RESEARCH + "/discover?q=1"
    for value in ("https://evil.example/discover", "https://research.example.org.evil.example/",
                  "https://user@research.example.org/", "http://research.example.org/", "javascript:alert(1)",
                  "//research.example.org/", RESEARCH + "/a\nb"):
        assert sc_identity._safe_return_to(value) == "/", value


# ---------------------------------------------------------------------------
# SC-SCI-02: production sign-in (ERW account) admitted only where configured; Research Console origin.

def erw_cookie(app_client, extra=None):
    token = session_auth.issue_session_token("erw:sc:synthetic-owner", "Synthetic", extra)
    app_client.cookies.set(session_auth.session_cookie_name(), token)


@pytest.fixture
def erw_env(env, monkeypatch):
    monkeypatch.setattr(research_access, "get_settings", lambda: env.settings)
    return env


def test_erw_account_sessions_get_a_research_session_only_where_configured(app_client, erw_env):
    erw_cookie(app_client, {"auth": "erw-account", "amr": ["pwd"]})
    r = app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH})
    assert r.status_code == 403 and r.json()["detail"]["code"] == "sc-identity-required"  # default: SC Identity only
    erw_env.settings.research_session_methods = "erw-account-session"
    r = app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH})
    assert r.status_code == 200, r.text
    body = verify(r.json())
    assert body["subject"] == "workspace-user:erw:sc:synthetic-owner" and body["authentication"] == "erw-account-session"


@pytest.mark.parametrize("configured", ["erw-account-session", "signed-http-only-session-cookie,service-bearer+wordpress-user-context"])
def test_legacy_cookie_sessions_never_get_one_whatever_is_configured(app_client, erw_env, configured):
    erw_env.settings.research_session_methods = configured
    erw_cookie(app_client)  # cookie exchange / older sign-in: no auth claim
    r = app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH})
    assert r.status_code == 403
    assert research_access.accepted_methods() <= research_access.SC_IDENTITY_METHODS | {"erw-account-session"}


def test_research_console_origin_is_added_without_restating_the_workspace_allowlist(app_client, erw_env):
    erw_env.settings.cors_allowed_origins = ORIGIN
    erw_env.settings.research_session_methods = "erw-account-session"
    erw_cookie(app_client, {"auth": "erw-account", "amr": ["pwd"]})
    assert app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH}).status_code == 403
    erw_env.settings.research_console_origins = RESEARCH + "/"
    assert app_client.post("/v1/research-access/session", headers={"Origin": RESEARCH}).status_code == 200
    assert app_client.post("/v1/research-access/session", headers={"Origin": "https://evil.example"}).status_code == 403
    from app.config import browser_origins
    assert browser_origins(erw_env.settings) == {ORIGIN, RESEARCH}
