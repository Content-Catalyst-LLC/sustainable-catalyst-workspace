"""RH-PROD-05.1 — unmounted, service-only identity introspection contract.

Do NOT include this router in the production app until the dedicated
service credential, private transport, session revocation migration and
real-account security acceptance are verified.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, Field

from .db import session_scope
from .session_auth import decode_session_token
from .session_revocation import SessionVerificationUnavailable, validate_session_for_service

router = APIRouter(prefix="/internal/v1/workspace", include_in_schema=False)


class IntrospectionRequest(BaseModel):
    schema_version: str = "rh-prod-05.1/1.0"
    session_token: str = Field(min_length=10, max_length=8192)


def verify_service_credential(authorization: str | None, *, expected: str) -> None:
    if not expected or len(expected) < 32:
        raise HTTPException(status_code=503, detail="Service introspection not configured")
    if not authorization or not secrets.compare_digest(authorization, "Bearer " + expected):
        raise HTTPException(status_code=401, detail="Service authentication required")


@router.post("/session/introspect")
def introspect_workspace_session(
    payload: IntrospectionRequest,
    response: Response,
    authorization: str | None = Header(default=None),
):
    # Independent Research service credential. Never reuse browser login,
    # accept X-SC-User-ID, or fall back to Workspace's legacy service token.
    from .config import get_settings
    expected = getattr(get_settings(), "research_introspection_token", "")
    verify_service_credential(authorization, expected=expected)
    # Never report an active session while the Workspace's ordinary
    # authorization paths still accept revoked cookies.
    if not get_settings().session_revocation_enforced:
        raise HTTPException(status_code=503, detail="Session revocation enforcement unavailable")
    try:
        with session_scope() as db:
            claims = validate_session_for_service(
                db, payload.session_token, decode=decode_session_token
            )
    except ValueError:
        raise HTTPException(status_code=401, detail="Workspace session invalid") from None
    except SessionVerificationUnavailable:
        raise HTTPException(status_code=503, detail="Workspace session verification unavailable") from None

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    now = datetime.now(timezone.utc)
    settings = get_settings()
    return {
        "schema": "sc-workspace-research-session-introspection/1.0",
        "issuer": settings.session_issuer,
        "audience": "research-private",
        "subject": str(claims["sub"]),
        "session_id": str(claims["jti"]),
        "issued_at": datetime.fromtimestamp(int(claims["iat"]), timezone.utc).isoformat(),
        "expires_at": datetime.fromtimestamp(int(claims["exp"]), timezone.utc).isoformat(),
        "verified_at": now.isoformat(),
        "active": True,
        "revoked": False,
        # Owner scope is intentionally OMITTED. Research must resolve an
        # authorized server-side owner map; subject alone is not permission.
    }
