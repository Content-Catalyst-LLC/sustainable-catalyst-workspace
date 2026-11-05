"""RH-PROD-05.1 isolated revocation unit tests (no deployed server)."""
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.session_revocation import (
    SessionVerificationUnavailable, is_revoked, revoke_session,
    token_fingerprint, validate_session_for_service,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE workspace_revoked_sessions ("
            "token_fingerprint varchar(64) PRIMARY KEY, "
            "user_key varchar(128) NOT NULL, "
            "expires_at timestamp NOT NULL, "
            "revoked_at timestamp DEFAULT CURRENT_TIMESTAMP)"
        ))
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_fingerprint_not_raw_token():
    assert token_fingerprint("opaque-token") != "opaque-token"
    assert token_fingerprint("opaque-token") != token_fingerprint("other-token")
    assert len(token_fingerprint("opaque-token")) == 64


def test_revocation_idempotent_and_durable(db):
    assert is_revoked(db, "session-a") is False
    exp = 2147483647
    revoke_session(db, "session-a", subject="user-1", expires_at=exp)
    revoke_session(db, "session-a", subject="user-1", expires_at=exp)
    db.commit()
    assert is_revoked(db, "session-a") is True
    assert is_revoked(db, "session-b") is False
    count = db.execute(text("SELECT count(*) FROM workspace_revoked_sessions")).scalar_one()
    assert count == 1


def test_service_validation_rejects_revoked(db):
    import time
    payload = {"sub": "user-1", "exp": int(time.time()) + 300}
    assert validate_session_for_service(db, "token", decode=lambda _: payload) == payload
    revoke_session(db, "token", subject="user-1", expires_at=payload["exp"])
    db.commit()
    with pytest.raises(ValueError, match="Revoked"):
        validate_session_for_service(db, "token", decode=lambda _: payload)


def test_service_validation_expired(db):
    with pytest.raises(ValueError, match="Expired"):
        validate_session_for_service(db, "token", decode=lambda _: {"sub": "u", "exp": 1})


def test_fail_closed_without_revocation_table():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with Session(engine) as session:
        with pytest.raises(SessionVerificationUnavailable):
            is_revoked(session, "session")
        with pytest.raises(SessionVerificationUnavailable):
            validate_session_for_service(
                session, "session", decode=lambda _: {"sub": "user", "exp": 2147483647}
            )
    engine.dispose()


def test_validation_does_not_accept_unsigned_browser_claims(db):
    with pytest.raises(ValueError):
        validate_session_for_service(db, "token", decode=lambda _: {"sub": ""})


def test_invalid_revocation_input_denied(db):
    with pytest.raises(ValueError):
        revoke_session(db, "token", subject="", expires_at=2147483647)
    with pytest.raises(ValueError):
        revoke_session(db, "token", subject="valid", expires_at=0)
