"""SC-SEO-INT-04 — a short-lived, signed SEO Studio session for an allowlisted person signed in to Sustainable Catalyst.

Same design as the Research session (``research_access``): the SEO Studio page calls ``POST /v1/seo-access/session``
with the Workspace session cookie from an allowlisted Origin and receives an ``sc-workspace-seo-session/1.0`` document
signed with the Workspace key. SEO Studio verifies it with the pinned public key and takes the person from ``subject``.

Differences from Research, all narrowing:
* its own schema (the signature's domain) and audience ``sc-seo-intelligence``, so neither session verifies as the other;
* disabled unless ``seo_studio_session_enabled``; issued only to Workspace users named in ``seo_studio_users``
  (SEO Studio applies its own allowlist too);
* SC Identity sign-ins only, plus the ERW account sign-in where the operator already admits it for Research.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from .config import get_settings
from .research_access import accepted_methods
from .research_exports import ISSUER, _signing_key, sign_document
from .security import ServiceIdentity, require_service_identity

SESSION_SCHEMA = "sc-workspace-seo-session/1.0"
AUDIENCE = "sc-seo-intelligence"
SESSION_TTL_SECONDS = 300  # SEO Studio refuses anything longer
router = APIRouter(prefix="/v1/seo-access", tags=["SC-SEO-INT-04 SEO Studio access"])


def allowed_users() -> frozenset[str]:
    return frozenset(u.strip() for u in getattr(get_settings(), "seo_studio_users", "").split(",") if u.strip())


@router.post("/session")
def seo_session_route(identity: ServiceIdentity = Depends(require_service_identity)):
    if not getattr(get_settings(), "seo_studio_session_enabled", False):
        raise HTTPException(status_code=503, detail="SEO Studio sessions are not enabled.")
    if identity.authentication_method not in accepted_methods():
        raise HTTPException(status_code=403, detail={
            "code": "sc-identity-required", "message": "Sign in to Sustainable Catalyst to use SEO Studio."})
    if identity.user_key not in allowed_users():
        raise HTTPException(status_code=403, detail={
            "code": "seo-studio-not-authorized", "message": "This account is not authorized for SEO Studio."})
    _signing_key()
    now = datetime.now(timezone.utc)
    return sign_document(SESSION_SCHEMA, {
        "schema": SESSION_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE, "sessionId": "sss_" + uuid4().hex,
        "subject": f"workspace-user:{identity.user_key}", "authentication": identity.authentication_method,
        "issuedAt": now.isoformat(), "expiresAt": (now + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat()})
