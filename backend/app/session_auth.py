from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from .config import get_settings

SESSION_SCHEMA = "sc-workspace-standalone-session/1.0"
SESSION_PROFILE_SCHEMA = "sc-workspace-standalone-session-profile/1.0"
SESSION_COOKIE_DEFAULT = "sc_workspace_session"
SESSION_SERVICE_PRINCIPAL = "workspace-session"

router = APIRouter(prefix="/v1/session", tags=["session"])

def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))

def _secret() -> str:
    settings = get_settings()
    explicit = (settings.session_signing_secret or "").strip()
    return explicit or settings.service_token.strip()

def session_cookie_name() -> str:
    settings = get_settings()
    return (settings.session_cookie_name or SESSION_COOKIE_DEFAULT).strip() or SESSION_COOKIE_DEFAULT

def session_profile() -> dict[str, Any]:
    settings = get_settings()
    explicit_secret = bool((settings.session_signing_secret or "").strip())
    return {
        "schema": SESSION_PROFILE_SCHEMA,
        "version": "3.71.0",
        "mode": "signed-http-only-cookie",
        "issuer": settings.session_issuer,
        "audience": settings.session_audience,
        "cookieName": session_cookie_name(),
        "ttlSeconds": settings.session_ttl_seconds,
        "secureCookie": True,
        "httpOnly": True,
        "sameSite": "lax",
        "browserServiceCredentialRequired": False,
        "serviceCredentialsBrowserVisible": False,
        "legacyWordPressServiceIdentityCompatible": True,
        "standaloneSessionIdentity": True,
        "explicitSessionSigningSecretConfigured": explicit_secret,
        "serviceTokenFallbackActive": bool(not explicit_secret and settings.service_token.strip()),
        "globalIdentityProviderConfigured": False,
        "automaticAccountCreation": False,
        "arbitraryCodeExecution": False,
    }

def issue_session_token(user_key: str, display_name: str = "") -> str:
    settings = get_settings()
    secret = _secret()
    if not secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workspace session signing secret is not configured.")
    now = int(time.time())
    payload = {
        "schema": SESSION_SCHEMA,
        "version": "3.71.0",
        "iss": settings.session_issuer,
        "aud": settings.session_audience,
        "sub": str(user_key),
        "displayName": str(display_name or ""),
        "iat": now,
        "exp": now + int(settings.session_ttl_seconds),
        "jti": uuid4().hex,
    }
    encoded = _b64e(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    signature = _b64e(hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest())
    return encoded + "." + signature

def decode_session_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    secret = _secret()
    if not secret:
        raise ValueError("session-secret-unavailable")
    parts = str(token or "").split(".")
    if len(parts) != 2:
        raise ValueError("malformed-session")
    encoded, supplied = parts
    expected = _b64e(hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest())
    if not secrets.compare_digest(supplied, expected):
        raise ValueError("invalid-session-signature")
    payload = json.loads(_b64d(encoded).decode("utf-8"))
    if payload.get("schema") != SESSION_SCHEMA:
        raise ValueError("invalid-session-schema")
    if payload.get("iss") != settings.session_issuer or payload.get("aud") != settings.session_audience:
        raise ValueError("invalid-session-scope")
    if int(payload.get("exp") or 0) <= int(time.time()):
        raise ValueError("expired-session")
    user_key = str(payload.get("sub") or "").strip()
    if not user_key or len(user_key) > 128:
        raise ValueError("invalid-session-subject")
    return payload

def session_payload_from_request(request: Request) -> dict[str, Any] | None:
    token = request.cookies.get(session_cookie_name(), "")
    if not token:
        return None
    try:
        return decode_session_token(token)
    except Exception:
        return None

def _legacy_exchange_identity(authorization: str | None, user_id: str | None) -> str:
    settings = get_settings()
    if not settings.token_configured:
        raise HTTPException(status_code=503, detail="Workspace backend service token is not configured.")
    expected = f"Bearer {settings.service_token}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Invalid service credential.")
    key = str(user_id or "").strip()
    if not key or len(key) > 128:
        raise HTTPException(status_code=400, detail="A valid user id is required.")
    return key

@router.get("/profile")
def get_session_profile():
    return session_profile()

@router.get("")
def get_session(request: Request):
    payload = session_payload_from_request(request)
    if not payload:
        return {
            "schema": SESSION_SCHEMA,
            "version": "3.71.0",
            "authenticated": False,
            "subject": "",
            "displayName": "",
            "authenticationMethod": "anonymous",
        }
    return {
        "schema": SESSION_SCHEMA,
        "version": "3.71.0",
        "authenticated": True,
        "subject": str(payload.get("sub") or ""),
        "displayName": str(payload.get("displayName") or ""),
        "authenticationMethod": "signed-http-only-session-cookie",
        "expiresAt": int(payload.get("exp") or 0),
    }

@router.post("/exchange")
def exchange_session(
    response: Response,
    authorization: str | None = Header(default=None),
    x_sc_user_id: str | None = Header(default=None, alias="X-SC-User-ID"),
    x_sc_display_name: str | None = Header(default=None, alias="X-SC-Display-Name"),
):
    user_key = _legacy_exchange_identity(authorization, x_sc_user_id)
    settings = get_settings()
    token = issue_session_token(user_key, x_sc_display_name or "")
    response.set_cookie(
        key=session_cookie_name(),
        value=token,
        max_age=int(settings.session_ttl_seconds),
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return {
        "schema": SESSION_SCHEMA,
        "version": "3.71.0",
        "authenticated": True,
        "subject": user_key,
        "displayName": str(x_sc_display_name or ""),
        "authenticationMethod": "trusted-service-session-exchange",
        "sessionIssued": True,
    }

@router.delete("")
def clear_session(response: Response):
    response.delete_cookie(key=session_cookie_name(), path="/", secure=True, httponly=True, samesite="lax")
    return {"schema": SESSION_SCHEMA, "version": "3.71.0", "authenticated": False, "sessionCleared": True}
