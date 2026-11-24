"""SC-AUTH-01 F1/F2/F3/G1 controls retained by SC-AUTH-02 — isolated, synthetic only.

The SC-AUTH-01 WordPress bridge assertions were removed by SC-AUTH-02.
"""
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
from app import auth_hygiene, security, session_auth, session_revocation

ORIGIN = "https://workspace.sustainablecatalyst.com"


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
        sc_identity_required=False,
        sc_identity_issuer="",
        sc_identity_client_id="",
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
    for mod in (session_auth, security):
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
        assert session_revocation.consume_nonce(db, "backchannel-logout", n, int(time.time()) + 60) is True
        with pytest.raises(ValueError):
            session_revocation.consume_nonce(db, "wp-bridge", n, 1)
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


# SC-AUTH-02 required mode -------------------------------------------------------------------------

def test_legacy_bearer_refused_when_sc_identity_required(env):
    settings, _ = env
    legacy = req("GET", [("authorization", f"Bearer {settings.service_token}"), ("x-sc-user-id", "2")])
    assert security.require_service_identity(legacy, authorization=f"Bearer {settings.service_token}", x_sc_user_id="2").user_key == "2"
    settings.sc_identity_required = True
    with pytest.raises(HTTPException) as exc:
        security.require_service_identity(legacy, authorization=f"Bearer {settings.service_token}", x_sc_user_id="2")
    assert exc.value.status_code == 401


def test_exchange_disabled_when_sc_identity_required(env):
    settings, _ = env
    settings.sc_identity_required = True
    app = FastAPI()
    app.include_router(session_auth.router)
    r = TestClient(app).post("/v1/session/exchange",
                             headers={"Authorization": f"Bearer {settings.service_token}", "X-SC-User-ID": "3"})
    assert r.status_code == 404 and "set-cookie" not in r.headers


@pytest.fixture
def client(env):
    app = FastAPI()
    app.add_middleware(auth_hygiene.AuthHygieneMiddleware)

    @app.get("/v1/projects")
    def projects():
        return {"ok": True}

    @app.get("/health")
    def health():
        return {"ok": True}

    return TestClient(app)


def test_no_store_only_on_api_paths(client):
    assert "no-store" in client.get("/v1/projects").headers["cache-control"]
    assert "cache-control" not in client.get("/health").headers
