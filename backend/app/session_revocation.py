"""RH-PROD-05.1 — durable revocation operations for Workspace signed sessions.

Module is intentionally *not mounted or activated* before migration and
real-account staging certification. No token, service secret, or database URL
may be written into operational logs.
"""
from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class SessionVerificationUnavailable(RuntimeError):
    """Revocation cannot be checked; callers must deny access."""


def token_fingerprint(token: str) -> str:
    """Hash the full opaque session token, not its user-controlled jti alone."""
    if not isinstance(token, str) or not token or len(token) > 8192:
        raise ValueError("Invalid session token")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_revoked(db, token: str) -> bool:
    """Database availability is mandatory for trusted private verification."""
    fingerprint = token_fingerprint(token)
    try:
        return db.execute(
            text("SELECT 1 FROM workspace_revoked_sessions WHERE token_fingerprint = :fp LIMIT 1"),
            {"fp": fingerprint},
        ).first() is not None
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session verification unavailable") from None


def revoke_session(db, token: str, *, subject: str, expires_at: int) -> None:
    """Transactional durable denial, idempotent for repeated logout.

    Caller must verify the token signature and claims before invoking.
    Caller owns transaction commit/rollback.
    """
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 128:
        raise ValueError("Invalid session subject")
    if not isinstance(expires_at, int) or expires_at <= 0:
        raise ValueError("Invalid session expiry")
    fingerprint = token_fingerprint(token)
    try:
        db.execute(
            text(
                "INSERT INTO workspace_revoked_sessions "
                "(token_fingerprint, user_key, expires_at) "
                "VALUES (:fp, :sub, :exp) "
                "ON CONFLICT (token_fingerprint) DO NOTHING"
            ),
            {
                "fp": fingerprint,
                "sub": subject,
                "exp": datetime.fromtimestamp(expires_at, tz=timezone.utc),
            },
        )
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session revocation unavailable") from None


def validate_session_for_service(db, token: str, *, decode):
    """Validate signature, standard claims AND durable revocation state.

    `decode` must be the Workspace authority's signed-token decoder, not
    a browser-provided object. Missing/corrupt DB is a hard denial.
    """
    payload = decode(token)
    if not isinstance(payload, dict) or not payload.get("sub"):
        raise ValueError("Invalid Workspace session")
    if int(payload.get("exp") or 0) <= int(time.time()):
        raise ValueError("Expired Workspace session")
    if is_revoked(db, token):
        raise ValueError("Revoked Workspace session")
    return payload
