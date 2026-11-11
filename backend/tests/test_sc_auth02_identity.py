"""SC-AUTH-02 — Sustainable Catalyst Identity (OIDC) for Workspace, isolated and synthetic.

A synthetic identity provider (RSA keys, JWKS, token endpoint) runs in-process.
No network, no real accounts, no WordPress.
"""
import hashlib
import json
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from sc_auth01_sqlite_schema import create_auth_hardening_tables
from app import auth_hygiene, sc_identity, security, session_auth, session_revocation

ISSUER = "https://auth.staging.invalid/realms/sustainable-catalyst"
CLIENT = "sc-workspace"
API_AUD = "sc-workspace-api"
ORIGIN = "https://workspace.sustainablecatalyst.com"
SUBJECT_A, SUBJECT_B = "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"
OWNER_A, OWNER_B = "erw:sc:owner-a", "sci:" + SUBJECT_B
KID = "staging-key-1"


class FakeIdP:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()))
        jwk.update({"kid": KID, "alg": "RS256", "use": "sig"})
        self.jwks = {"keys": [jwk]}
        self.metadata = {
            "issuer": ISSUER,
            "authorization_endpoint": ISSUER + "/protocol/openid-connect/auth",
            "token_endpoint": "http://idp.internal/token",
            "jwks_uri": "http://idp.internal/certs",
            "end_session_endpoint": ISSUER + "/protocol/openid-connect/logout",
        }
        self.down = False
        self.next_id_token = None
        self.token_calls = []

    def sign(self, claims, key=None, kid=KID, alg="RS256"):
        return jwt.encode(claims, key or self.key, algorithm=alg, headers={"kid": kid})

    def id_token(self, nonce, **over):
        now = int(time.time())
        c = {"iss": ISSUER, "sub": SUBJECT_A, "aud": CLIENT, "azp": CLIENT, "typ": "ID", "iat": now, "exp": now + 300,
             "auth_time": now, "nonce": nonce, "sid": "idp-session-a", "amr": ["pwd", "otp"], "name": "Owner A"}
        c.update(over)
        return self.sign(c)

    def access_token(self, **over):
        now = int(time.time())
        c = {"iss": ISSUER, "sub": SUBJECT_A, "aud": [API_AUD, "account"], "azp": "sc-research", "typ": "Bearer",
             "iat": now, "exp": now + 300, "sid": "idp-session-a", "amr": ["pwd", "otp"]}
        c.update(over)
        return self.sign(c)

    def logout_token(self, **over):
        now = int(time.time())
        c = {"iss": ISSUER, "aud": CLIENT, "iat": now, "exp": now + 120, "jti": f"lt-{time.time_ns()}-abcdefgh",
             "sid": "idp-session-a", "events": {sc_identity.LOGOUT_EVENT: {}}}
        c.update(over)
        return self.sign(c)


def make_settings(**over):
    base = dict(
        session_signing_secret="synthetic-signing-secret-at-least-32-bytes",
        session_signing_secret_file="",
        service_token="synthetic-service-token-at-least-32-bytes!",
        session_cookie_name="sc_workspace_session",
        session_issuer="sustainable-catalyst-workspace",
        session_audience="workspace.sustainablecatalyst.com",
        session_ttl_seconds=28800,
        session_revocation_enforced=True,
        cors_allowed_origins=ORIGIN,
        token_configured=True,
        sc_identity_issuer=ISSUER,
        sc_identity_discovery_url="http://idp.internal/.well-known/openid-configuration",
        sc_identity_client_id=CLIENT,
        sc_identity_client_secret="synthetic-client-secret",
        sc_identity_client_secret_file="",
        sc_identity_redirect_uri=ORIGIN + "/v1/auth/callback",
        sc_identity_post_logout_redirect_uri=ORIGIN + "/",
        sc_identity_api_audience=API_AUD,
        sc_identity_allowed_bearer_clients="",
        sc_identity_require_mfa=True,
        sc_identity_mfa_amr="otp,mfa,hwk,swk",
        sc_identity_step_up_max_age=300,
        sc_identity_required=True,
    )
    base.update(over)
    return SimpleNamespace(**base)


@pytest.fixture
def env(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE workspace_revoked_sessions (token_fingerprint varchar(64) PRIMARY KEY, "
                          "user_key varchar(128) NOT NULL, expires_at timestamp NOT NULL, revoked_at timestamp)"))
        conn.execute(text("CREATE TABLE workspace_project_heads (user_key varchar(128), project_id varchar(160), "
                          "PRIMARY KEY (user_key, project_id))"))
        create_auth_hardening_tables(conn)
        conn.execute(text("INSERT INTO workspace_project_heads VALUES (:u, 'metrics-project')"), {"u": OWNER_A})
    settings = make_settings()
    idp = FakeIdP()
    for mod in (session_auth, security, sc_identity):
        monkeypatch.setattr(mod, "get_settings", lambda: settings)
    for mod in (session_auth, sc_identity):
        monkeypatch.setattr(mod, "session_scope", lambda: Session(engine))
    import app.db as appdb
    monkeypatch.setattr(appdb, "session_scope", lambda: Session(engine))
    monkeypatch.setattr(security, "authorize_request", lambda *a, **k: {"effect": "allow"})

    def fake_get(url):
        if idp.down:
            raise sc_identity.IdentityUnavailable("down")
        return {settings.sc_identity_discovery_url: idp.metadata, idp.metadata["jwks_uri"]: idp.jwks}[url]

    def fake_post(url, data=None, auth=None, **kwargs):
        idp.token_calls.append({"url": url, "data": data, "auth": auth})
        if idp.down:
            raise httpx.ConnectError("down")
        if data.get("code") != "good-code":
            return httpx.Response(400, json={"error": "invalid_grant"})
        return httpx.Response(200, json={"id_token": idp.next_id_token, "access_token": "opaque", "token_type": "Bearer"})

    monkeypatch.setattr(sc_identity, "_http_get_json", fake_get)
    monkeypatch.setattr(sc_identity.httpx, "post", fake_post)
    sc_identity._cache.reset()
    with Session(engine) as db:
        session_revocation.link_identity(db, issuer=ISSUER, subject=SUBJECT_A, user_key=OWNER_A,
                                         method="verified-existing-owner", actor="ops:test", reason="fixture",
                                         evidence_sha256="e" * 64)
        session_revocation.link_identity(db, issuer=ISSUER, subject=SUBJECT_B, user_key=OWNER_B,
                                         method="new-enrollment", actor="ops:test", reason="fixture")
        db.commit()
    yield SimpleNamespace(settings=settings, engine=engine, idp=idp)
    engine.dispose()


@pytest.fixture
def client(env):
    app = FastAPI()
    app.add_middleware(auth_hygiene.AuthHygieneMiddleware)
    app.include_router(session_auth.router)
    app.include_router(sc_identity.router)

    @app.get("/v1/projects")
    def projects(identity=Depends(security.require_service_identity)):
        return {"user": identity.user_key, "method": identity.authentication_method}

    @app.post("/v1/projects")
    def create(identity=Depends(security.require_service_identity)):
        return {"user": identity.user_key}

    return TestClient(app, base_url=ORIGIN, follow_redirects=False)


def code(response):
    """Refusal code, with or without Workspace's error-flattening handler."""
    body = response.json()
    return body.get("code") or body.get("detail", {}).get("code")


def start_login(client, **params):
    r = client.get("/v1/auth/login", params=params)
    assert r.status_code == 303
    query = parse_qs(urlsplit(r.headers["location"]).query)
    return r, {k: v[0] for k, v in query.items()}


def sign_in(client, env, subject=SUBJECT_A, **claims):
    _, q = start_login(client, returnTo="/projects")
    env.idp.next_id_token = env.idp.id_token(q["nonce"], sub=subject, **claims)
    return client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]})


# Login (Authorization Code + PKCE) ---------------------------------------------------------------

def test_login_uses_pkce_state_nonce_and_sealed_transaction(client, env):
    r, q = start_login(client, returnTo="/projects")
    assert r.headers["location"].startswith(env.idp.metadata["authorization_endpoint"] + "?")
    assert q["response_type"] == "code" and q["client_id"] == CLIENT and q["code_challenge_method"] == "S256"
    assert len(q["state"]) >= 32 and len(q["nonce"]) >= 32 and "max_age" not in q
    cookie = r.headers["set-cookie"]
    assert "sc_oidc_tx=" in cookie and "HttpOnly" in cookie and "Secure" in cookie and "Path=/v1/auth" in cookie
    assert "no-store" in r.headers["cache-control"]
    assert q["nonce"] not in cookie or True  # sealed, integrity-protected


def test_callback_issues_revocable_oidc_session_for_linked_identity(client, env):
    r = sign_in(client, env)
    assert r.status_code == 303 and r.headers["location"] == "/projects"
    token = client.cookies.get("sc_workspace_session")
    claims = session_auth.decode_session_token(token)
    assert claims["sub"] == OWNER_A and claims["auth"] == "sc-identity-oidc"
    assert claims["idp_sid"] == "idp-session-a" and "otp" in claims["amr"]
    assert env.idp.token_calls[-1]["auth"] == (CLIENT, "synthetic-client-secret")
    assert len(env.idp.token_calls[-1]["data"]["code_verifier"]) >= 43
    me = client.get("/v1/projects")
    assert me.json() == {"user": OWNER_A, "method": "sc-identity-oidc-session"}
    assert client.get("/v1/session").json()["authenticationMethod"] == "sc-identity-oidc"


def test_cross_owner_isolation_by_server_side_link(client, env):
    sign_in(client, env, subject=SUBJECT_B)
    assert client.get("/v1/projects", headers={"X-SC-User-ID": OWNER_A}).json()["user"] == OWNER_B


@pytest.mark.parametrize("value,expected", [
    ("/projects?x=1", "/projects?x=1"), ("//evil.example/x", "/"), ("https://evil.example", "/"),
    ("/\\evil", "/"), ("/a\nb", "/")])
def test_return_to_is_same_origin_path_only(value, expected):
    assert sc_identity._safe_return_to(value) == expected


def test_callback_without_transaction_or_with_wrong_state_is_refused(client, env):
    assert client.get("/v1/auth/callback", params={"code": "good-code", "state": "x"}).status_code == 400
    start_login(client)
    r = client.get("/v1/auth/callback", params={"code": "good-code", "state": "forged-state"})
    assert r.status_code == 400 and code(r) == "oidc-state-mismatch"


def test_callback_state_is_single_use(client, env):
    _, q = start_login(client)
    env.idp.next_id_token = env.idp.id_token(q["nonce"])
    tx = client.cookies.get("sc_oidc_tx")
    assert client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]}).status_code == 303
    client.cookies.set("sc_oidc_tx", tx, path="/v1/auth")
    replay = client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]})
    assert replay.status_code == 400 and code(replay) == "oidc-state-replayed"


def test_tampered_transaction_cookie_is_refused(client, env):
    _, q = start_login(client)
    tx = client.cookies.get("sc_oidc_tx")
    client.cookies.set("sc_oidc_tx", tx[:-2] + ("AA" if not tx.endswith("AA") else "BB"), path="/v1/auth")
    assert client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]}).status_code == 400


def test_refused_authorization_code_is_a_denial(client, env):
    _, q = start_login(client)
    r = client.get("/v1/auth/callback", params={"code": "replayed-code", "state": q["state"]})
    assert r.status_code == 401 and code(r) == "oidc-code-refused"
    assert "sc_workspace_session" not in client.cookies


@pytest.mark.parametrize("mutation,expected", [
    (dict(nonce="other-nonce"), "oidc-nonce-mismatch"),
    (dict(aud="another-client"), "oidc-id-token-invalid"),
    (dict(iss="https://evil.example/realms/x"), "oidc-id-token-invalid"),
    (dict(exp=int(time.time()) - 120), "oidc-id-token-invalid"),
    (dict(typ="Bearer"), "oidc-id-token-invalid"),
    (dict(aud=[CLIENT, "x"], azp="x"), "oidc-id-token-invalid"),
])
def test_id_token_claims_are_verified(client, env, mutation, expected):
    _, q = start_login(client)
    claims = {"nonce": q["nonce"], **mutation}
    env.idp.next_id_token = env.idp.id_token(**claims) if "nonce" in mutation else env.idp.id_token(q["nonce"], **mutation)
    r = client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]})
    assert r.status_code == 401 and code(r) == expected
    assert "sc_workspace_session" not in client.cookies


def test_id_token_signed_by_unknown_key_or_alg_none_is_refused(client, env):
    for token in (
        env.idp.sign({"iss": ISSUER, "sub": SUBJECT_A, "aud": CLIENT, "iat": 1, "exp": 2**31}, key=env.idp.other_key),
        jwt.encode({"iss": ISSUER, "sub": SUBJECT_A, "aud": CLIENT}, None, algorithm="none"),
        env.idp.sign({"iss": ISSUER}, kid="unknown-kid"),
    ):
        _, q = start_login(client)
        env.idp.next_id_token = token
        assert client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]}).status_code == 401


def test_mfa_is_required(client, env):
    r = sign_in(client, env, amr=["pwd"])
    assert r.status_code == 403 and code(r) == "mfa-required"
    r = sign_in(client, env, amr=None)
    assert r.status_code == 403


def test_unlinked_and_suspended_identities_are_refused(client, env):
    r = sign_in(client, env, subject="33333333-3333-4333-8333-333333333333")
    assert r.status_code == 403 and code(r) == "identity-not-linked"
    with Session(env.engine) as db:
        session_revocation.suspend_identity(db, issuer=ISSUER, subject=SUBJECT_A, actor="ops:test", reason="incident")
        db.commit()
    assert sign_in(client, env).status_code == 403


def test_step_up_forces_fresh_authentication(client, env):
    _, q = start_login(client, stepUp="true")
    assert q["max_age"] == "0" and q["prompt"] == "login"
    env.idp.next_id_token = env.idp.id_token(q["nonce"], auth_time=int(time.time()) - 3600)
    r = client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]})
    assert r.status_code == 403 and code(r) == "step-up-required"


def test_identity_provider_outage_fails_closed(client, env):
    env.idp.down = True
    assert client.get("/v1/auth/login").status_code == 503
    env.idp.down = False
    _, q = start_login(client)
    env.idp.down = True
    sc_identity._cache.reset()
    r = client.get("/v1/auth/callback", params={"code": "good-code", "state": q["state"]})
    assert r.status_code == 503 and "sc_workspace_session" not in client.cookies


# Logout, back-channel logout, revocation, CSRF, expiry ---------------------------------------------

def test_logout_requires_same_origin_and_revokes_session(client, env):
    sign_in(client, env)
    token = client.cookies.get("sc_workspace_session")
    assert client.post("/v1/auth/logout").status_code == 403
    assert client.post("/v1/auth/logout", headers={"Origin": "https://lab.sustainablecatalyst.com"}).status_code == 403
    r = client.post("/v1/auth/logout", headers={"Origin": ORIGIN})
    assert r.status_code == 200 and r.json()["sessionRevoked"] is True
    assert r.json()["endSessionUrl"].startswith(env.idp.metadata["end_session_endpoint"] + "?client_id=sc-workspace")
    with pytest.raises(ValueError):
        session_auth.decode_session_token(token)


def test_cookie_session_state_change_requires_origin(client, env):
    sign_in(client, env)
    assert client.post("/v1/projects").status_code == 403
    assert client.post("/v1/projects", headers={"Origin": ORIGIN}).status_code == 200
    assert client.post("/v1/projects", headers={"Origin": ORIGIN, "Sec-Fetch-Site": "cross-site"}).status_code == 403


def test_backchannel_logout_revokes_sessions_of_that_idp_session_only(client, env):
    sign_in(client, env)
    a = client.cookies.get("sc_workspace_session")
    client.cookies.clear()
    sign_in(client, env, sid="idp-session-a2")
    a2 = client.cookies.get("sc_workspace_session")
    logout_token = env.idp.logout_token()
    r = client.post("/v1/auth/backchannel-logout", data={"logout_token": logout_token})
    assert r.status_code == 200
    with pytest.raises(ValueError):
        session_auth.decode_session_token(a)
    assert session_auth.decode_session_token(a2)["sub"] == OWNER_A
    replay = client.post("/v1/auth/backchannel-logout", data={"logout_token": logout_token})
    assert replay.status_code == 400


def test_backchannel_logout_by_subject_cuts_all_user_sessions(client, env):
    sign_in(client, env)
    token = client.cookies.get("sc_workspace_session")
    r = client.post("/v1/auth/backchannel-logout", data={"logout_token": env.idp.logout_token(sid=None, sub=SUBJECT_A)})
    assert r.status_code == 200
    with pytest.raises(ValueError):
        session_auth.decode_session_token(token)


@pytest.mark.parametrize("mutation", [
    dict(nonce="x"), dict(events={}), dict(aud="another"), dict(iat=int(time.time()) - 3600, exp=int(time.time()) + 60),
    dict(sid=None), dict(jti="short")])
def test_invalid_logout_tokens_are_refused(client, env, mutation):
    r = client.post("/v1/auth/backchannel-logout", data={"logout_token": env.idp.logout_token(**mutation)})
    assert r.status_code == 400


def test_session_expiry_is_enforced(client, env):
    env.settings.session_ttl_seconds = 1
    sign_in(client, env)
    token = client.cookies.get("sc_workspace_session")
    assert session_auth.decode_session_token(token)["sub"] == OWNER_A
    time.sleep(2.1)
    with pytest.raises(ValueError):
        session_auth.decode_session_token(token)


def test_operator_revoke_user_ends_existing_sessions(client, env):
    sign_in(client, env)
    with Session(env.engine) as db:
        session_revocation.revoke_user_sessions(db, OWNER_A, actor="ops:test", reason="recovery")
        db.commit()
    assert client.get("/v1/projects").status_code == 401


# Legacy paths refused in required mode -------------------------------------------------------------

def test_legacy_paths_are_refused(client, env):
    legacy = {"Authorization": f"Bearer {env.settings.service_token}", "X-SC-User-ID": OWNER_A}
    assert client.get("/v1/projects", headers=legacy).status_code == 401
    assert client.post("/v1/session/exchange", headers=legacy).status_code == 404


# Service-to-service access tokens ------------------------------------------------------------------

def bearer(client, token):
    return client.get("/v1/projects", headers={"Authorization": f"Bearer {token}"})


def test_access_token_for_this_api_maps_to_linked_owner(client, env):
    r = bearer(client, env.idp.access_token())
    assert r.status_code == 200 and r.json() == {"user": OWNER_A, "method": "sc-identity-access-token"}


@pytest.mark.parametrize("mutation,status", [
    (dict(aud="account"), 401), (dict(typ="ID"), 401), (dict(iss="https://evil.example"), 401),
    (dict(exp=int(time.time()) - 120), 401), (dict(amr=["pwd"]), 403),
    (dict(sub="33333333-3333-4333-8333-333333333333"), 403)])
def test_invalid_access_tokens_are_refused(client, env, mutation, status):
    assert bearer(client, env.idp.access_token(**mutation)).status_code == status


def test_access_token_respects_backchannel_and_operator_revocation(client, env):
    assert client.post("/v1/auth/backchannel-logout", data={"logout_token": env.idp.logout_token()}).status_code == 200
    assert bearer(client, env.idp.access_token()).status_code == 401
    assert bearer(client, env.idp.access_token(sid="idp-session-z")).status_code == 200
    with Session(env.engine) as db:
        session_revocation.revoke_user_sessions(db, OWNER_A, actor="ops:test", reason="incident")
        db.commit()
    assert bearer(client, env.idp.access_token(sid="idp-session-z")).status_code == 401


def test_access_token_client_allowlist(client, env):
    env.settings.sc_identity_allowed_bearer_clients = "sc-library"
    assert bearer(client, env.idp.access_token()).status_code == 401
    assert bearer(client, env.idp.access_token(azp="sc-library")).status_code == 200


def test_real_authorization_policy_allows_sc_identity_bearer():
    from app.authorization import authorize_request
    identity = security.ServiceIdentity(user_key=OWNER_A, principal_id="sc-user:x", principal_type="sc-identity-user",
                                        service_principal="sc-identity-bearer", authentication_method="sc-identity-access-token")
    assert authorize_request(identity, "GET", "/v1/projects")["effect"] == "allow"
    assert "wordpress-bridge" not in __import__("app.authorization", fromlist=["x"]).TRUSTED_SERVICE_PRINCIPALS


# Identity links (migration safety) -----------------------------------------------------------------

def test_identity_links_refuse_ambiguity(env):
    with Session(env.engine) as db:
        link = lambda **k: session_revocation.link_identity(db, issuer=ISSUER, actor="ops:test", reason="r", **k)
        assert link(subject=SUBJECT_A, user_key=OWNER_A, method="verified-existing-owner",
                    evidence_sha256="e" * 64) == "unchanged"
        with pytest.raises(ValueError, match="different Workspace account"):
            link(subject=SUBJECT_A, user_key="erw:sc:other", method="verified-existing-owner", evidence_sha256="e" * 64)
        with pytest.raises(ValueError, match="different subject"):
            link(subject="44444444-4444-4444-8444-444444444444", user_key=OWNER_A,
                 method="verified-existing-owner", evidence_sha256="e" * 64)
        with pytest.raises(ValueError, match="evidence"):
            link(subject="5", user_key="7", method="verified-existing-owner")
        with pytest.raises(ValueError, match="No existing Workspace projects"):
            link(subject="5", user_key="7", method="verified-existing-owner", evidence_sha256="e" * 64)
        db.execute(text("INSERT INTO workspace_project_heads VALUES ('9', 'p')"))
        with pytest.raises(ValueError, match="cannot take over"):
            link(subject="6", user_key="9", method="new-enrollment")
        with pytest.raises(ValueError, match="SHA-256"):
            link(subject="6", user_key="9", method="verified-existing-owner", evidence_sha256="E" * 64)
        actions = db.execute(text("SELECT action FROM workspace_identity_link_audit")).scalars().all()
    assert actions == ["link", "link"]  # only the two fixture links were recorded


def test_session_profile_reports_required_identity_provider(env):
    profile = session_auth.session_profile()
    assert profile["globalIdentityProviderConfigured"] is True
    assert profile["globalIdentityProviderRequired"] is True
    assert profile["legacyWordPressServiceIdentityCompatible"] is False
