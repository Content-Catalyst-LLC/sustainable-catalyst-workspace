"""SC-AUTH-01 F1/F2/F3/G1 and WordPress bridge assertions — isolated, synthetic only."""
import hashlib
import time
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.requests import Request as StarletteRequest

from sc_auth01_sqlite_schema import create_auth_hardening_tables
from app import security, session_auth, session_revocation, wp_bridge

ORIGIN = "https://workspace.sustainablecatalyst.com"
BRIDGE_KEY = "b" * 48


def make_settings(**over):
    base = dict(
        session_signing_secret="synthetic-signing-secret-at-least-32-bytes",
        session_signing_secret_file="",
        service_token="synthetic-service-token-at-least-32-bytes!",
        research_introspection_token="",
        research_introspection_token_file="",
        session_cookie_name="sc_workspace_session",
        session_issuer="sustainable-catalyst-workspace",
        session_audience="workspace.sustainablecatalyst.com",
        session_ttl_seconds=28800,
        session_revocation_enforced=True,
        cors_allowed_origins=ORIGIN,
        bridge_assertion_key=BRIDGE_KEY,
        bridge_assertion_key_file="",
        bridge_audience="sc-workspace-api",
        bridge_assertion_required=False,
        token_configured=True,
    )
    base.update(over)
    return SimpleNamespace(**base)


@pytest.fixture
def env(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE workspace_revoked_sessions (token_fingerprint varchar(64) PRIMARY KEY, "
                          "user_key varchar(128) NOT NULL, expires_at timestamp NOT NULL, revoked_at timestamp)"))
        create_auth_hardening_tables(conn)
    settings = make_settings()
    for mod in (session_auth, security, wp_bridge):
        monkeypatch.setattr(mod, "get_settings", lambda: settings)
    monkeypatch.setattr(session_auth, "session_scope", lambda: Session(engine))
    import app.db as appdb
    monkeypatch.setattr(appdb, "session_scope", lambda: Session(engine))
    monkeypatch.setattr(security, "authorize_request", lambda *a, **k: {"effect": "allow"})
    yield settings, engine
    engine.dispose()


def req(method, headers=()):
    raw = [(k.lower().encode(), v.encode()) for k, v in headers]
    return StarletteRequest({"type": "http", "method": method, "path": "/v1/projects", "headers": raw})


# F1 ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("method,headers,ok", [
    ("GET", [], True),
    ("POST", [], False),
    ("POST", [("origin", "https://attacker.example")], False),
    ("POST", [("origin", "https://lab.sustainablecatalyst.com")], False),
    ("DELETE", [("origin", ORIGIN), ("sec-fetch-site", "cross-site")], False),
    ("POST", [("origin", ORIGIN), ("sec-fetch-site", "same-site")], True),
])
def test_cookie_csrf_requires_exact_allowed_origin(env, method, headers, ok):
    if ok:
        session_auth.enforce_cookie_csrf(req(method, headers))
    else:
        with pytest.raises(HTTPException) as exc:
            session_auth.enforce_cookie_csrf(req(method, headers))
        assert exc.value.status_code == 403


def test_cookie_identity_path_applies_csrf(env):
    token = session_auth.issue_session_token("owner-a")
    cookie = ("cookie", f"sc_workspace_session={token}")
    assert security.require_service_identity(req("POST", [cookie, ("origin", ORIGIN)])).user_key == "owner-a"
    with pytest.raises(HTTPException) as exc:
        security.require_service_identity(req("POST", [cookie]))
    assert exc.value.status_code == 403


# F2 ---------------------------------------------------------------------------------------------

def test_nonce_is_single_use(env):
    _, engine = env
    with Session(engine) as db:
        n = "a" * 64
        assert session_revocation.consume_nonce(db, "introspection", n, int(time.time()) + 60) is True
        assert session_revocation.consume_nonce(db, "introspection", n, int(time.time()) + 60) is False
        assert session_revocation.consume_nonce(db, "wp-bridge", n, int(time.time()) + 60) is True
        with pytest.raises(ValueError):
            session_revocation.consume_nonce(db, "other", n, 1)


# G1 ---------------------------------------------------------------------------------------------

def test_operator_revoke_user_cuts_existing_sessions_only(env):
    _, engine = env
    old = session_auth.issue_session_token("owner-a")
    other = session_auth.issue_session_token("owner-b")
    with Session(engine) as db:
        session_revocation.revoke_user_sessions(db, "owner-a", actor="ops:test", reason="lost device")
        db.commit()
    with pytest.raises(ValueError):
        session_auth.decode_session_token(old)
    assert session_auth.decode_session_token(other)["sub"] == "owner-b"
    time.sleep(1.1)
    fresh = session_auth.issue_session_token("owner-a")
    assert session_auth.decode_session_token(fresh)["sub"] == "owner-a"
    with Session(engine) as db:
        row = db.execute(text("SELECT action, actor, reason FROM workspace_session_revocation_audit")).one()
    assert tuple(row) == ("revoke-user", "ops:test", "lost device")


def test_operator_revoke_single_session(env):
    _, engine = env
    a1, a2 = session_auth.issue_session_token("owner-a"), session_auth.issue_session_token("owner-a")
    sid = session_auth.decode_session_token(a1)["jti"]
    with Session(engine) as db:
        session_revocation.revoke_session_id(db, sid, user_key="owner-a", actor="ops:test", reason="x", ttl_seconds=60)
        db.commit()
    with pytest.raises(ValueError):
        session_auth.decode_session_token(a1)
    assert session_auth.decode_session_token(a2)["sub"] == "owner-a"


@pytest.mark.parametrize("kwargs", [
    dict(actor="", reason="r"), dict(actor="ops", reason=""), dict(actor="ops", reason="r" * 501)])
def test_operator_actions_require_actor_and_reason(env, kwargs):
    _, engine = env
    with Session(engine) as db, pytest.raises(ValueError):
        session_revocation.revoke_user_sessions(db, "owner-a", **kwargs)


# Bridge assertions -------------------------------------------------------------------------------

def claims(**over):
    now = int(time.time())
    c = {"v": 1, "iss": "sc-wordpress-bridge", "aud": "sc-workspace-api", "sub": "2", "sid": "c" * 64,
         "sat": now - 30, "iat": now, "exp": now + 60, "nonce": hashlib.sha256(str(time.time_ns()).encode()).hexdigest(),
         "m": "POST", "p": "/v1/projects", "bh": hashlib.sha256(b'{"a":1}').hexdigest()}
    c.update(over)
    return c


def verify(assertion, method="POST", target="/v1/projects", body=b'{"a":1}', key=BRIDGE_KEY):
    return wp_bridge.verify_assertion(key, assertion, method=method, target=target, body=body)


def test_bridge_assertion_round_trip(env):
    assert verify(wp_bridge.sign_assertion(BRIDGE_KEY, claims()))["sub"] == "2"


@pytest.mark.parametrize("mutation,kwargs", [
    ({}, {"method": "DELETE"}),
    ({}, {"target": "/v1/projects/other"}),
    ({}, {"body": b'{"a":2}'}),
    ({}, {"key": "x" * 48}),
    ({"aud": "other"}, {}),
    ({"iss": "browser"}, {}),
    ({"exp": int(time.time()) - 1}, {}),
    ({"exp": int(time.time()) + 600}, {}),
    ({"iat": int(time.time()) + 60}, {}),
    ({"sid": "short"}, {}),
    ({"sub": ""}, {}),
])
def test_bridge_assertion_bindings_refused(env, mutation, kwargs):
    with pytest.raises(wp_bridge.BridgeAssertionError):
        verify(wp_bridge.sign_assertion(BRIDGE_KEY, claims(**mutation)), **kwargs)


def test_bridge_key_must_be_distinct(env):
    settings, _ = env
    assert wp_bridge.bridge_key() == BRIDGE_KEY
    settings.bridge_assertion_key = settings.service_token
    assert wp_bridge.bridge_key() == ""
    settings.bridge_assertion_key = "short"
    assert wp_bridge.bridge_key() == ""


def test_legacy_bearer_refused_when_bridge_required(env):
    settings, _ = env
    legacy = req("GET", [("authorization", f"Bearer {settings.service_token}"), ("x-sc-user-id", "2")])
    assert security.require_service_identity(legacy, authorization=f"Bearer {settings.service_token}", x_sc_user_id="2").user_key == "2"
    settings.bridge_assertion_required = True
    with pytest.raises(HTTPException) as exc:
        security.require_service_identity(legacy, authorization=f"Bearer {settings.service_token}", x_sc_user_id="2")
    assert exc.value.status_code == 401


@pytest.fixture
def client(env):
    app = FastAPI()
    app.add_middleware(wp_bridge.AuthHygieneMiddleware)

    @app.post("/v1/projects")
    async def store(request: Request, identity=Depends(security.require_service_identity)):
        return {"user": identity.user_key, "method": identity.authentication_method, "body": (await request.json())}

    @app.get("/health")
    def health():
        return {"ok": True}

    return TestClient(app)


def test_middleware_accepts_bridge_and_ignores_client_user_id(client):
    body = b'{"a":1}'
    a = wp_bridge.sign_assertion(BRIDGE_KEY, claims())
    r = client.post("/v1/projects", content=body, headers={"X-SC-Bridge-Assertion": a, "X-SC-User-ID": "3",
                                                             "Content-Type": "application/json"})
    assert r.status_code == 200
    assert r.json() == {"user": "2", "method": "wordpress-bridge-assertion", "body": {"a": 1}}
    assert "no-store" in r.headers["cache-control"]
    replay = client.post("/v1/projects", content=body, headers={"X-SC-Bridge-Assertion": a, "Content-Type": "application/json"})
    assert replay.status_code == 401


def test_middleware_refuses_bad_assertion_without_fallback(client, env):
    settings, _ = env
    r = client.post("/v1/projects", content=b'{"a":1}', headers={
        "X-SC-Bridge-Assertion": wp_bridge.sign_assertion("z" * 48, claims()),
        "Authorization": f"Bearer {settings.service_token}", "X-SC-User-ID": "2"})
    assert r.status_code == 401 and r.json() == {"code": "bridge-assertion-refused"}


def test_bridge_respects_operator_revoke_user(client, env):
    _, engine = env
    with Session(engine) as db:
        session_revocation.revoke_user_sessions(db, "2", actor="ops:test", reason="compromise")
        db.commit()
    r = client.post("/v1/projects", content=b'{"a":1}', headers={
        "X-SC-Bridge-Assertion": wp_bridge.sign_assertion(BRIDGE_KEY, claims()), "Content-Type": "application/json"})
    assert r.status_code == 401
    later = int(time.time()) + 2
    r = client.post("/v1/projects", content=b'{"a":1}', headers={
        "X-SC-Bridge-Assertion": wp_bridge.sign_assertion(BRIDGE_KEY, claims(sat=later, iat=later, exp=later + 60)),
        "Content-Type": "application/json"})
    assert r.status_code == 200


def test_bridge_fails_closed_when_store_unavailable(client, env, monkeypatch):
    import app.db as appdb

    def broken():
        raise RuntimeError("db down")
    monkeypatch.setattr(appdb, "session_scope", broken)
    r = client.post("/v1/projects", content=b'{"a":1}', headers={
        "X-SC-Bridge-Assertion": wp_bridge.sign_assertion(BRIDGE_KEY, claims()), "Content-Type": "application/json"})
    assert r.status_code == 503


def test_no_store_only_on_api_paths(client):
    assert "cache-control" not in client.get("/health").headers


def test_exchange_requires_bridge_assertion_when_required(env):
    settings, _ = env
    settings.bridge_assertion_required = True
    app = FastAPI()
    app.add_middleware(wp_bridge.AuthHygieneMiddleware)
    app.include_router(session_auth.router)
    client = TestClient(app)
    legacy = client.post("/v1/session/exchange", headers={"Authorization": f"Bearer {settings.service_token}", "X-SC-User-ID": "3"})
    assert legacy.status_code == 401
    ok = client.post("/v1/session/exchange", headers={
        "X-SC-Bridge-Assertion": wp_bridge.sign_assertion(BRIDGE_KEY, claims(p="/v1/session/exchange", bh=hashlib.sha256(b"").hexdigest())),
        "X-SC-User-ID": "3"})
    assert ok.status_code == 200 and ok.json()["subject"] == "2"
    assert "sc_workspace_session=" in ok.headers["set-cookie"]
