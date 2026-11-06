"""RH-PROD-05.1 isolated PostgreSQL acceptance; never connects to production.

CI supplies RH_PROD05_TEST_DATABASE_URL using its disposable PostgreSQL service.
"""
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from fastapi import Response
from starlette.requests import Request

from app import session_auth


@pytest.fixture
def database(monkeypatch):
    url = os.getenv("RH_PROD05_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Disposable acceptance PostgreSQL URL not supplied")
    engine = create_engine(url)
    migration = Path(__file__).resolve().parents[1] / "migrations" / "051_workspace_session_revocation.sql"
    with engine.begin() as conn:
        conn.execute(text(migration.read_text()))
        conn.execute(text("DELETE FROM workspace_revoked_sessions"))
    from types import SimpleNamespace
    settings = SimpleNamespace(
        session_signing_secret="synthetic-test-signature-not-production",
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
    yield engine
    engine.dispose()


def request(token):
    return Request({
        "type": "http", "method": "DELETE", "path": "/v1/session",
        "headers": [
            (b"origin", b"https://workspace.sustainablecatalyst.com"),
            (b"cookie", ("sc_workspace_session=" + token).encode()),
        ],
    })


def test_real_postgres_logout_replay_and_new_login(database):
    previous = session_auth.issue_session_token("staging-synthetic-user")
    req = request(previous)
    assert session_auth.get_session(req)["authenticated"] is True
    assert session_auth.clear_session(req, Response())["sessionCleared"] is True
    assert session_auth.get_session(req)["authenticated"] is False
    with database.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM workspace_revoked_sessions")).scalar_one() == 1
    replacement = session_auth.issue_session_token("staging-synthetic-user")
    assert session_auth.get_session(request(replacement))["authenticated"] is True
    assert session_auth.get_session(req)["authenticated"] is False


def test_real_postgres_revocation_survives_new_session(database):
    token = session_auth.issue_session_token("staging-synthetic-user-2")
    req = request(token)
    session_auth.clear_session(req, Response())
    # Fresh database connection represents an application restart's store view.
    with database.connect() as conn:
        assert conn.execute(text(
            "SELECT count(*) FROM workspace_revoked_sessions WHERE user_key=:sub"
        ), {"sub": "staging-synthetic-user-2"}).scalar_one() == 1
    assert session_auth.get_session(req)["authenticated"] is False


def test_additive_migration_runner_is_idempotent(database):
    from app.migrate_security import migrate, require_schema
    migrate(database)
    migrate(database)
    require_schema(database)
    with database.connect() as c:
        assert c.scalar(text("SELECT count(*) FROM workspace_security_migrations WHERE migration_id='051_workspace_session_revocation'")) == 1
