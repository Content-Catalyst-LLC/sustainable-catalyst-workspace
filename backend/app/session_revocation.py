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
    session id, by its identity-provider session (back-channel logout), or by
    a per-user cutoff at or after its issue time (operator).
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
        idp_sid = str(claims.get("idp_sid") or "")
        if idp_sid and db.execute(
            text("SELECT 1 FROM workspace_revoked_idp_sessions WHERE issuer = :iss AND idp_sid = :sid LIMIT 1"),
            {"iss": str(claims.get("idp_iss") or ""), "sid": idp_sid},
        ).first() is not None:
            return True
        cutoff = db.execute(
            text("SELECT not_before FROM workspace_session_user_cutoffs WHERE user_key = :sub"),
            {"sub": str(claims.get("sub") or "")},
        ).scalar()
        return cutoff is not None and _utc(int(claims.get("iat") or 0)) <= _aware(cutoff)
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session verification unavailable") from None


NONCE_SCOPES = frozenset({"introspection", "oidc-state", "backchannel-logout"})


def consume_nonce(db, scope: str, nonce: str, expires_at: int) -> bool:
    """Record a single-use nonce. False means it was already used (replay).

    Rows must outlive the credential they protect, so callers pass the
    expiry of the bound session or assertion. Caller owns commit.
    """
    if scope not in NONCE_SCOPES or not isinstance(nonce, str) or not 16 <= len(nonce) <= 128:
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
    for table in ("workspace_used_nonces", "workspace_revoked_sessions", "workspace_revoked_session_ids",
                  "workspace_revoked_idp_sessions"):
        counts[table] = db.execute(text(f"DELETE FROM {table} WHERE expires_at < :now"), {"now": now}).rowcount
    return counts


def revoke_idp_session(db, issuer: str, idp_sid: str, *, ttl_seconds: int) -> None:
    """Back-channel logout: deny every Workspace session bound to an IdP session. Caller owns commit."""
    if not issuer or not isinstance(idp_sid, str) or not 1 <= len(idp_sid) <= 255:
        raise ValueError("Invalid identity-provider session")
    try:
        db.execute(
            text(
                "INSERT INTO workspace_revoked_idp_sessions (issuer, idp_sid, expires_at) "
                "VALUES (:iss, :sid, :exp) ON CONFLICT (issuer, idp_sid) DO NOTHING"
            ),
            {"iss": issuer, "sid": idp_sid, "exp": _utc(int(time.time()) + int(ttl_seconds))},
        )
    except SQLAlchemyError:
        raise SessionVerificationUnavailable("Session revocation unavailable") from None


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


LINK_METHODS = frozenset({"verified-existing-owner", "new-enrollment"})


def _link_audit(db, action, issuer, subject, user_key, actor, reason, evidence_sha256=None) -> None:
    db.execute(
        text(
            "INSERT INTO workspace_identity_link_audit "
            "(action, issuer, subject, user_key, actor, reason, evidence_sha256) "
            "VALUES (:action, :iss, :sub, :uk, :actor, :reason, :ev)"
        ),
        {"action": action, "iss": issuer, "sub": subject, "uk": user_key, "actor": actor,
         "reason": reason, "ev": evidence_sha256},
    )


def link_identity(db, *, issuer: str, subject: str, user_key: str, method: str, actor: str, reason: str,
                  evidence_sha256: str | None = None) -> str:
    """Bind a Platform Core identity to a Workspace user_key (SC-AUTH-02). Caller owns commit.

    Refuses every ambiguity instead of guessing: a subject already linked to
    another account, an account already linked to another subject, an
    existing-owner link without evidence or without existing Workspace data,
    and a new enrollment that would collide with existing data.
    Returns "linked" or "unchanged".
    """
    _operator_args(user_key, actor, reason)
    if method not in LINK_METHODS:
        raise ValueError("Unsupported link method")
    if not issuer.startswith(("https://", "http://")) or len(issuer) > 255:
        raise ValueError("Invalid issuer")
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 255:
        raise ValueError("Invalid subject")
    if evidence_sha256 is not None and (len(evidence_sha256) != 64 or any(c not in "0123456789abcdef" for c in evidence_sha256)):
        raise ValueError("Evidence must be a lowercase SHA-256 hex digest")
    by_subject = db.execute(
        text("SELECT user_key FROM workspace_identity_links WHERE issuer = :iss AND subject = :sub"),
        {"iss": issuer, "sub": subject},
    ).scalar()
    if by_subject is not None:
        if by_subject == user_key:
            return "unchanged"
        raise ValueError("Subject is already linked to a different Workspace account")
    by_user = db.execute(
        text("SELECT subject FROM workspace_identity_links WHERE issuer = :iss AND user_key = :uk"),
        {"iss": issuer, "uk": user_key},
    ).scalar()
    if by_user is not None:
        raise ValueError("Workspace account is already linked to a different subject")
    owned = db.execute(
        text("SELECT count(*) FROM workspace_project_heads WHERE user_key = :uk"), {"uk": user_key}
    ).scalar() or 0
    if method == "verified-existing-owner":
        if evidence_sha256 is None:
            raise ValueError("An existing-owner link requires an evidence digest")
        if not owned:
            raise ValueError("No existing Workspace projects for this account; use new-enrollment")
    elif owned:
        raise ValueError("A new enrollment cannot take over an account that already owns projects")
    db.execute(
        text(
            "INSERT INTO workspace_identity_links "
            "(issuer, subject, user_key, status, link_method, evidence_sha256, created_by) "
            "VALUES (:iss, :sub, :uk, 'active', :method, :ev, :actor)"
        ),
        {"iss": issuer, "sub": subject, "uk": user_key, "method": method, "ev": evidence_sha256, "actor": actor},
    )
    _link_audit(db, "link", issuer, subject, user_key, actor, reason, evidence_sha256)
    return "linked"


def suspend_identity(db, *, issuer: str, subject: str, actor: str, reason: str) -> str:
    """Suspend a link and end every session of its account. Caller owns commit."""
    user_key = db.execute(
        text("SELECT user_key FROM workspace_identity_links WHERE issuer = :iss AND subject = :sub"),
        {"iss": issuer, "sub": subject},
    ).scalar()
    if user_key is None:
        raise ValueError("No such identity link")
    db.execute(
        text("UPDATE workspace_identity_links SET status = 'suspended', updated_at = CURRENT_TIMESTAMP "
             "WHERE issuer = :iss AND subject = :sub"),
        {"iss": issuer, "sub": subject},
    )
    revoke_user_sessions(db, user_key, actor=actor, reason=reason)
    _link_audit(db, "suspend", issuer, subject, user_key, actor, reason)
    return user_key
