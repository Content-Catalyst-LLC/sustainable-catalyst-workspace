"""SC-UP-01 — a short-lived, signed Research session for the person signed in to Sustainable Catalyst.

Research's browser pages never hold a Research service credential and never choose their own identity. After an
SC Identity sign-in (SC-AUTH-02), the Research page calls ``POST /v1/research-access/session`` with the Workspace
session cookie (an allowlisted Origin, as for every cookie write) and receives an
``sc-workspace-research-session/1.0`` document signed with the Workspace Research key, under its own domain. Research
verifies it with the key it already pins for exports and approvals, and takes the person from ``subject``.

Only an SC Identity sign-in gets one: an OIDC session or an SC access token. The legacy service bearer and the
cookie exchange do not. SC-SCI-02: where SC Identity is not deployed (production today), the operator may also admit
the ERW account sign-in (``research_session_methods = erw-account-session``); the document names the method, so
Research applies its own allowlist too. Editor access to another owner's records still needs that owner's grant and a separate
attestation (``research_approvals``).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from .config import get_settings
from .research_exports import AUDIENCE, ISSUER, _signing_key, sign_document
from .security import ServiceIdentity, require_service_identity

SESSION_SCHEMA = "sc-workspace-research-session/1.0"
SESSION_TTL_SECONDS = 300  # Research refuses anything longer (user_sessions.SESSION_MAX_LIFETIME_SECONDS)
SC_IDENTITY_METHODS = frozenset({"sc-identity-oidc-session", "sc-identity-access-token"})
CONFIGURABLE_METHODS = frozenset({"erw-account-session"})
router = APIRouter(prefix="/v1/research-access", tags=["SC-UP-01 Research access"])


def accepted_methods() -> frozenset[str]:
    extra = {m.strip() for m in getattr(get_settings(), "research_session_methods", "").split(",") if m.strip()}
    return SC_IDENTITY_METHODS | (extra & CONFIGURABLE_METHODS)


@router.post("/session")
def research_session_route(identity: ServiceIdentity = Depends(require_service_identity)):
    if identity.authentication_method not in accepted_methods():
        raise HTTPException(status_code=403, detail={
            "code": "sc-identity-required", "message": "Sign in to Sustainable Catalyst to use Research."})
    _signing_key()
    now = datetime.now(timezone.utc)
    return sign_document(SESSION_SCHEMA, {
        "schema": SESSION_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE, "sessionId": "rss_" + uuid4().hex,
        "subject": f"workspace-user:{identity.user_key}", "authentication": identity.authentication_method,
        "issuedAt": now.isoformat(), "expiresAt": (now + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat()})
