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


def _utc(epoch: int) -> datetime:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc)


def _aware(value) -> datetime:
    # SQLite test engines return naive timestamps; PostgreSQL returns aware ones.
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def is_revoked(db, token: str, claims: dict | None = None) -> bool:
    """Database availability is mandatory for trusted private verification.

    A token is revoked by its own fingerprint (logout), by its server-issued
    session id, or by a per-user cutoff at or after its issue time (operator).
    """
    fingerprint = token_fingerprint(token)
    try:
        if db.execute(
            text("SELECT 1 FROM workspace_revoked_sessions WHERE token_fingerprint = :fp LIMIT 1"),
            {"fp": fingerprint},
        ).first() is not None:
            return True
        if claims is None:
            return False
        session_id = str(claims.get("jti") or "")
        if session_id and db.execute(
            text("SELECT 1 FROM workspace_revoked_session_ids WHERE session_id = :sid LIMIT 1"),
            {"sid": session_id},
        ).first() is not None:
            return True
        cutoff = db.execute(
            text("SELECT not_before FROM workspace_session_user_cutoffs WHERE user_key = :sub"),
            {"sub": str(claims.get("sub") or "")},
        ).scalar()
        return cutoff is not None and _utc(int(claims.get("iat") or 0)) <= _aware(cutoff)
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session verification unavailable") from None


def consume_nonce(db, scope: str, nonce: str, expires_at: int) -> bool:
    """Record a single-use nonce. False means it was already used (replay).

    Rows must outlive the credential they protect, so callers pass the
    expiry of the bound session or assertion. Caller owns commit.
    """
    if scope not in {"introspection", "wp-bridge"} or not isinstance(nonce, str) or not 16 <= len(nonce) <= 64:
        raise ValueError("Invalid nonce")
    try:
        row = db.execute(
            text(
                "INSERT INTO workspace_used_nonces (scope, nonce, expires_at) "
                "VALUES (:scope, :nonce, :exp) ON CONFLICT (scope, nonce) DO NOTHING RETURNING nonce"
            ),
            {"scope": scope, "nonce": nonce, "exp": _utc(expires_at)},
        ).first()
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Replay protection unavailable") from None
    return row is not None


def _audit(db, action: str, user_key: str, session_id: str | None, actor: str, reason: str) -> None:
    db.execute(
        text(
            "INSERT INTO workspace_session_revocation_audit (action, user_key, session_id, actor, reason) "
            "VALUES (:action, :sub, :sid, :actor, :reason)"
        ),
        {"action": action, "sub": user_key, "sid": session_id, "actor": actor, "reason": reason},
    )


def _operator_args(user_key: str, actor: str, reason: str) -> None:
    if not isinstance(user_key, str) or not user_key.strip() or len(user_key) > 128:
        raise ValueError("Invalid user key")
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 128:
        raise ValueError("An operator identity is required")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
        raise ValueError("A revocation reason is required")


def revoke_session_id(db, session_id: str, *, user_key: str, actor: str, reason: str,
                      ttl_seconds: int) -> None:
    """Operator revocation of one session by server-issued id. Caller owns commit."""
    _operator_args(user_key, actor, reason)
    if not isinstance(session_id, str) or len(session_id) != 32 or any(c not in "0123456789abcdef" for c in session_id):
        raise ValueError("Invalid session id")
    try:
        db.execute(
            text(
                "INSERT INTO workspace_revoked_session_ids (session_id, user_key, expires_at) "
                "VALUES (:sid, :sub, :exp) ON CONFLICT (session_id) DO NOTHING"
            ),
            {"sid": session_id, "sub": user_key, "exp": _utc(int(time.time()) + int(ttl_seconds))},
        )
        _audit(db, "revoke-session", user_key, session_id, actor, reason)
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session revocation unavailable") from None


def revoke_user_sessions(db, user_key: str, *, actor: str, reason: str) -> None:
    """Operator revocation of every session issued to a user up to now. Caller owns commit."""
    _operator_args(user_key, actor, reason)
    now = datetime.now(timezone.utc)
    try:
        updated = db.execute(
            text("UPDATE workspace_session_user_cutoffs SET not_before = :now, updated_at = :now WHERE user_key = :sub"),
            {"sub": user_key, "now": now},
        ).rowcount
        if not updated:
            db.execute(
                text("INSERT INTO workspace_session_user_cutoffs (user_key, not_before) VALUES (:sub, :now)"),
                {"sub": user_key, "now": now},
            )
        _audit(db, "revoke-user", user_key, None, actor, reason)
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session revocation unavailable") from None


def purge_expired(db) -> dict:
    """Delete replay and revocation rows whose credentials can no longer be valid."""
    now = datetime.now(timezone.utc)
    counts = {}
    for table in ("workspace_used_nonces", "workspace_revoked_sessions", "workspace_revoked_session_ids"):
        counts[table] = db.execute(text(f"DELETE FROM {table} WHERE expires_at < :now"), {"now": now}).rowcount
    return counts


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
    if is_revoked(db, token, payload):
        raise ValueError("Revoked Workspace session")
    return payload
