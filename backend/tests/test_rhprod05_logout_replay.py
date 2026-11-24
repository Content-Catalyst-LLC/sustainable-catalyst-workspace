"""RH-PROD-05.1 — signed cookie replay regression, isolated SQLite only.

Production uses PostgreSQL; dedicated Postgres and real-account staging
acceptance are required before enabling the feature flag.
"""
from sc_auth01_sqlite_schema import create_auth_hardening_tables
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import session_auth


@pytest.fixture
def gated_session(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE workspace_revoked_sessions ("
            "token_fingerprint varchar(64) PRIMARY KEY, "
            "user_key varchar(128) NOT NULL, "
            "expires_at timestamp NOT NULL, "
            "revoked_at timestamp DEFAULT CURRENT_TIMESTAMP)"
        ))
        create_auth_hardening_tables(conn)

    settings = SimpleNamespace(
        session_signing_secret="test-session-signing-secret-only",
        service_token="",
        session_cookie_name="sc_workspace_session",
        session_issuer="sustainable-catalyst-workspace",
        session_audience="workspace.sustainablecatalyst.com",
        session_ttl_seconds=28800,
        session_revocation_enforced=True,
        cors_allowed_origins="https://workspace.sustainablecatalyst.com",
    )
    monkeypatch.setattr(session_auth, "get_settings", lambda: settings)
    monkeypatch.setattr(session_auth, "session_scope", lambda: Session(engine))
    yield settings, engine
    engine.dispose()


def request_for(token, origin=None):
    headers = [(b"cookie", ("sc_workspace_session=" + token).encode())]
    if origin is not None:
        headers.append((b"origin", origin.encode()))
    return Request({"type": "http", "method": "DELETE", "path": "/v1/session", "headers": headers})


def test_copied_cookie_is_rejected_after_logout(gated_session):
    token = session_auth.issue_session_token("synthetic-owner")
    req = request_for(token, "https://workspace.sustainablecatalyst.com")
    assert session_auth.get_session(req)["authenticated"] is True
    response = Response()
    result = session_auth.clear_session(req, response)
    assert result["sessionCleared"] is True
    # Intentionally replay the ORIGINAL cookie rather than trusting Set-Cookie deletion.
    assert session_auth.get_session(req)["authenticated"] is False


def test_logout_rejects_cross_site_origin_without_revoking(gated_session):
    token = session_auth.issue_session_token("synthetic-owner")
    req = request_for(token, "https://attacker.example")
    with pytest.raises(HTTPException) as caught:
        session_auth.clear_session(req, Response())
    assert caught.value.status_code == 403
    assert session_auth.get_session(req)["authenticated"] is True


def test_missing_origin_denied_when_enforced(gated_session):
    token = session_auth.issue_session_token("synthetic-owner")
    with pytest.raises(HTTPException) as caught:
        session_auth.clear_session(request_for(token), Response())
    assert caught.value.status_code == 403


def test_missing_revocation_database_fails_closed(gated_session):
    _, engine = gated_session
    token = session_auth.issue_session_token("synthetic-owner")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE workspace_revoked_sessions"))
    with pytest.raises(HTTPException) as caught:
        session_auth.get_session(request_for(token))
    assert caught.value.status_code == 503
    with pytest.raises(HTTPException) as caught_logout:
        session_auth.clear_session(
            request_for(token, "https://workspace.sustainablecatalyst.com"),
            Response()
        )
    assert caught_logout.value.status_code == 503


def test_logout_without_cookie_clears_cookie_only(gated_session):
    request = Request({
        "type": "http", "method": "DELETE", "path": "/v1/session",
        "headers": [(b"origin", b"https://workspace.sustainablecatalyst.com")]
    })
    assert session_auth.clear_session(request, Response())["sessionCleared"] is True
