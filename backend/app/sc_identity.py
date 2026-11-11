"""SC-AUTH-02 — Sustainable Catalyst Identity for Workspace.

Platform Core runs a standards-based OpenID Connect provider. Workspace is a
confidential client (backend-for-frontend):

    GET  /v1/auth/login                Authorization Code + PKCE (S256), state, nonce
    GET  /v1/auth/callback             code exchange, ID-token verification, identity link,
                                       revocable Workspace session
    POST /v1/auth/logout               CSRF-checked; revokes the session, returns the IdP
                                       end-session URL
    POST /v1/auth/backchannel-logout   OIDC Back-Channel Logout 1.0 (single-use logout tokens)

Other Sustainable Catalyst services call Workspace with an IdP access token
whose audience is this API (`bearer_identity`).

Workspace never handles passwords or MFA secrets. A verified (issuer, subject)
is mapped to an existing Workspace `user_key` only through an explicit,
audited identity link (`workspace_identity_links`); unlinked or suspended
identities are refused, and nothing is linked by email. Every failure to reach
or verify the identity provider is a denial, never a fallback.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode

import httpx
import jwt
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from .authorization import SC_IDENTITY_BEARER_PRINCIPAL
from .config import get_settings
from .db import session_scope
from .session_auth import (
    _secret,
    enforce_cookie_csrf,
    issue_session_token,
    revoke_request_session,
    session_cookie_name,
)
from .session_revocation import (
    SessionVerificationUnavailable,
    consume_nonce,
    revoke_idp_session,
    revoke_user_sessions,
)

router = APIRouter(prefix="/v1/auth", tags=["sc-identity"])

AUTH_METHOD = "sc-identity-oidc"
TX_COOKIE = "sc_oidc_tx"
TX_TTL_SECONDS = 600
TX_DOMAIN = b"sc-auth-02-oidc-tx-v1"
LOGOUT_EVENT = "http://schemas.openid.net/event/backchannel-logout"
ALLOWED_ALGORITHMS = ("RS256", "PS256", "ES256")
LEEWAY_SECONDS = 30
METADATA_TTL_SECONDS = 3600
JWKS_TTL_SECONDS = 300
JWKS_MIN_REFRESH_SECONDS = 30
HTTP_TIMEOUT_SECONDS = 10


class IdentityUnavailable(RuntimeError):
    """The identity provider cannot be reached or verified; callers deny."""


def _deny(code: str, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _unavailable() -> HTTPException:
    return _deny("identity-provider-unavailable", "Sustainable Catalyst Identity is unavailable.",
                 status.HTTP_503_SERVICE_UNAVAILABLE)


def enabled() -> bool:
    settings = get_settings()
    return bool(settings.sc_identity_issuer and settings.sc_identity_client_id)


def _client_secret() -> str:
    settings = get_settings()
    if settings.sc_identity_client_secret_file:
        try:
            return Path(settings.sc_identity_client_secret_file).read_text(encoding="utf-8").strip()
        except OSError:
            return ""  # A configured but unreadable secret never falls back.
    return settings.sc_identity_client_secret.strip()


# --- provider metadata and keys -------------------------------------------

class _ProviderCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        self.metadata: dict[str, Any] | None = None
        self.metadata_at = 0.0
        self.keys: dict[str, jwt.PyJWK] = {}
        self.keys_at = 0.0


_cache = _ProviderCache()


def _http_get_json(url: str) -> dict[str, Any]:
    try:
        response = httpx.get(url, timeout=HTTP_TIMEOUT_SECONDS, follow_redirects=False)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        raise IdentityUnavailable("identity provider request failed") from None
    if not isinstance(data, dict):
        raise IdentityUnavailable("identity provider returned an invalid document")
    return data


def metadata() -> dict[str, Any]:
    settings = get_settings()
    with _cache.lock:
        if _cache.metadata and time.time() - _cache.metadata_at < METADATA_TTL_SECONDS:
            return _cache.metadata
        url = settings.sc_identity_discovery_url or (
            settings.sc_identity_issuer.rstrip("/") + "/.well-known/openid-configuration")
        data = _http_get_json(url)
        # The discovered issuer must be exactly the configured one (OIDC Discovery §4.3).
        if data.get("issuer") != settings.sc_identity_issuer:
            raise IdentityUnavailable("identity provider issuer mismatch")
        for field in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
            if not isinstance(data.get(field), str) or not data[field]:
                raise IdentityUnavailable("identity provider metadata incomplete")
        _cache.metadata, _cache.metadata_at = data, time.time()
        return data


def _signing_key(kid: str) -> jwt.PyJWK:
    meta = metadata()
    with _cache.lock:
        fresh = time.time() - _cache.keys_at < JWKS_TTL_SECONDS
        if kid in _cache.keys and fresh:
            return _cache.keys[kid]
        if kid not in _cache.keys and time.time() - _cache.keys_at < JWKS_MIN_REFRESH_SECONDS:
            raise jwt.InvalidTokenError("unknown signing key")
        keys: dict[str, jwt.PyJWK] = {}
        for jwk in _http_get_json(meta["jwks_uri"]).get("keys", []):
            if jwk.get("use", "sig") != "sig" or jwk.get("alg") not in ALLOWED_ALGORITHMS or not jwk.get("kid"):
                continue
            try:
                keys[jwk["kid"]] = jwt.PyJWK(jwk)
            except jwt.PyJWTError:
                continue
        _cache.keys, _cache.keys_at = keys, time.time()
        if kid not in keys:
            raise jwt.InvalidTokenError("unknown signing key")
        return keys[kid]


def verify_jwt(token: str, *, audience: str, required: tuple[str, ...]) -> dict[str, Any]:
    """Verify signature, issuer, audience and time claims. Raises InvalidTokenError or IdentityUnavailable."""
    if not isinstance(token, str) or not 20 <= len(token) <= 16384:
        raise jwt.InvalidTokenError("invalid token size")
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")
    if algorithm not in ALLOWED_ALGORITHMS or not header.get("kid"):
        raise jwt.InvalidTokenError("unsupported token header")
    key = _signing_key(str(header["kid"]))
    return jwt.decode(
        token,
        key=key.key,
        algorithms=[algorithm],
        audience=audience,
        issuer=get_settings().sc_identity_issuer,
        leeway=LEEWAY_SECONDS,
        options={"require": list(required)},
    )


def step_up_evidence(request: Request) -> dict[str, Any] | None:
    """Evidence of a fresh SC Identity sign-in (password + second factor) behind this request's
    session, or None. Consequential decisions (SC-PUB-M1 publication approvals) require it."""
    from .session_auth import session_payload_from_request
    payload = session_payload_from_request(request) or {}
    if payload.get("auth") != AUTH_METHOD:
        return None
    try:
        auth_time = int(payload.get("auth_time") or 0)
    except (TypeError, ValueError):
        return None
    if not auth_time or not 0 <= time.time() - auth_time <= get_settings().sc_identity_step_up_max_age:
        return None
    amr = [v for v in payload.get("amr") or [] if isinstance(v, str)]
    if not mfa_satisfied({"amr": amr}):
        return None
    return {"stepUp": True, "deciderAuthTime": auth_time, "deciderAmr": amr[:8]}


def mfa_satisfied(claims: dict[str, Any]) -> bool:
    if not get_settings().sc_identity_require_mfa:
        return True
    accepted = {v.strip() for v in get_settings().sc_identity_mfa_amr.split(",") if v.strip()}
    amr = claims.get("amr")
    return isinstance(amr, list) and any(isinstance(v, str) and v in accepted for v in amr)


# --- identity links -------------------------------------------------------

def resolve_user_key(db, issuer: str, subject: str) -> str | None:
    row = db.execute(
        text("SELECT user_key, status FROM workspace_identity_links WHERE issuer = :iss AND subject = :sub"),
        {"iss": issuer, "sub": subject},
    ).first()
    if row is None or row.status != "active":
        return None
    return row.user_key


def _linked_user_key(issuer: str, subject: str) -> str:
    try:
        with session_scope() as db:
            user_key = resolve_user_key(db, issuer, subject)
    except Exception:
        raise _unavailable() from None
    if not user_key:
        raise _deny("identity-not-linked",
                    "This Sustainable Catalyst account is not linked to a Workspace account.",
                    status.HTTP_403_FORBIDDEN)
    return user_key


# --- signed login transaction cookie --------------------------------------

def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))


def _tx_key() -> bytes:
    secret = _secret()
    if not secret:
        raise HTTPException(status_code=503, detail="Workspace session signing secret is not configured.")
    return hmac.new(secret.encode("utf-8"), TX_DOMAIN, hashlib.sha256).digest()


def _seal_tx(tx: dict[str, Any]) -> str:
    encoded = _b64e(json.dumps(tx, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return encoded + "." + _b64e(hmac.new(_tx_key(), encoded.encode("ascii"), hashlib.sha256).digest())


def _open_tx(request: Request) -> dict[str, Any] | None:
    raw = request.cookies.get(TX_COOKIE, "")
    if not raw or len(raw) > 4096 or raw.count(".") != 1:
        return None
    encoded, signature = raw.split(".")
    expected = _b64e(hmac.new(_tx_key(), encoded.encode("ascii"), hashlib.sha256).digest())
    if not secrets.compare_digest(signature, expected):
        return None
    try:
        tx = json.loads(_b64d(encoded))
    except ValueError:
        return None
    if not isinstance(tx, dict) or int(tx.get("exp") or 0) <= int(time.time()):
        return None
    return tx


def _safe_return_to(value: str | None) -> str:
    value = (value or "/").strip()
    if (not value.startswith("/") or value.startswith("//") or "\\" in value or len(value) > 512
            or re.search(r"[\x00-\x1f\x7f]", value)):
        return "/"
    return value


def _clear_tx(response) -> None:
    response.delete_cookie(TX_COOKIE, path="/v1/auth", secure=True, httponly=True, samesite="lax")


# --- browser routes -------------------------------------------------------

def _authorize_redirect(return_to: str, step_up: bool, mfa_retry: bool = False) -> RedirectResponse:
    try:
        meta = metadata()
    except IdentityUnavailable:
        raise _unavailable() from None
    settings = get_settings()
    verifier = _b64e(secrets.token_bytes(32))
    tx = {
        "state": secrets.token_urlsafe(32),
        "nonce": secrets.token_urlsafe(32),
        "verifier": verifier,
        "returnTo": _safe_return_to(return_to),
        "stepUp": bool(step_up),
        "mfaRetry": bool(mfa_retry),
        "exp": int(time.time()) + TX_TTL_SECONDS,
    }
    params = {
        "response_type": "code",
        "client_id": settings.sc_identity_client_id,
        "redirect_uri": settings.sc_identity_redirect_uri,
        "scope": "openid profile email",
        "state": tx["state"],
        "nonce": tx["nonce"],
        "code_challenge": _b64e(hashlib.sha256(verifier.encode("ascii")).digest()),
        "code_challenge_method": "S256",
    }
    if step_up or mfa_retry:
        # Fresh authentication (password + second factor) for consequential actions,
        # or once after a sign-in that carried no second-factor evidence.
        params["max_age"] = "0"
        params["prompt"] = "login"
    response = RedirectResponse(meta["authorization_endpoint"] + "?" + urlencode(params), status_code=303)
    response.set_cookie(TX_COOKIE, _seal_tx(tx), max_age=TX_TTL_SECONDS, secure=True, httponly=True,
                        samesite="lax", path="/v1/auth")
    return response


@router.get("/login")
def login(returnTo: str = "/", stepUp: bool = False):
    if not enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    return _authorize_redirect(returnTo, stepUp)


def _exchange_code(code: str, verifier: str) -> dict[str, Any]:
    settings = get_settings()
    secret = _client_secret()
    if not secret:
        raise _unavailable()
    try:
        response = httpx.post(
            metadata()["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.sc_identity_redirect_uri,
                "code_verifier": verifier,
            },
            auth=(settings.sc_identity_client_id, secret),
            headers={"Accept": "application/json"},
            timeout=HTTP_TIMEOUT_SECONDS,
            follow_redirects=False,
        )
    except (httpx.HTTPError, IdentityUnavailable):
        raise _unavailable() from None
    if response.status_code != 200:
        # Invalid, expired or replayed code; the provider's details are not echoed.
        raise _deny("oidc-code-refused", "Sign-in could not be completed. Start again.")
    try:
        body = response.json()
    except ValueError:
        raise _unavailable() from None
    if not isinstance(body, dict) or not isinstance(body.get("id_token"), str):
        raise _unavailable()
    return body


def _verify_id_token(id_token: str, nonce: str, step_up: bool) -> dict[str, Any]:
    settings = get_settings()
    try:
        claims = verify_jwt(id_token, audience=settings.sc_identity_client_id,
                            required=("iss", "sub", "aud", "exp", "iat", "nonce"))
    except IdentityUnavailable:
        raise _unavailable() from None
    except jwt.PyJWTError:
        raise _deny("oidc-id-token-invalid", "Sign-in could not be verified.") from None
    if claims.get("typ", "ID") != "ID":
        raise _deny("oidc-id-token-invalid", "Sign-in could not be verified.")
    audiences = claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]]
    if len(audiences) > 1 and claims.get("azp") != settings.sc_identity_client_id:
        raise _deny("oidc-id-token-invalid", "Sign-in could not be verified.")
    if not secrets.compare_digest(str(claims.get("nonce")), nonce):
        raise _deny("oidc-nonce-mismatch", "Sign-in could not be verified.")
    if step_up:
        auth_time = int(claims.get("auth_time") or 0)
        if time.time() - auth_time > settings.sc_identity_step_up_max_age:
            raise _deny("step-up-required", "A fresh sign-in is required.", status.HTTP_403_FORBIDDEN)
    return claims


@router.get("/callback")
def callback(request: Request, code: str = "", state: str = "", error: str = ""):
    if not enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    tx = _open_tx(request)
    if tx is None:
        raise _deny("oidc-transaction-missing", "Sign-in session expired. Start again.", status.HTTP_400_BAD_REQUEST)
    if not state or not secrets.compare_digest(state, str(tx["state"])):
        raise _deny("oidc-state-mismatch", "Sign-in could not be verified.", status.HTTP_400_BAD_REQUEST)
    try:
        with session_scope() as db:
            fresh = consume_nonce(db, "oidc-state", hashlib.sha256(state.encode()).hexdigest(), int(tx["exp"]))
            db.commit()
    except Exception:
        raise _unavailable() from None
    if not fresh:
        raise _deny("oidc-state-replayed", "Sign-in could not be verified.", status.HTTP_400_BAD_REQUEST)
    if error or not code:
        raise _deny("oidc-sign-in-not-completed", "Sign-in was not completed.")
    tokens = _exchange_code(code, str(tx["verifier"]))
    claims = _verify_id_token(tokens["id_token"], str(tx["nonce"]), bool(tx.get("stepUp")))
    if not mfa_satisfied(claims):
        # A first sign-in that enrols the second factor through a provider required
        # action carries no second-factor evidence. Re-authenticate exactly once;
        # no session is issued from a sign-in without MFA evidence.
        if not tx.get("mfaRetry"):
            return _authorize_redirect(str(tx.get("returnTo") or "/"), bool(tx.get("stepUp")), mfa_retry=True)
        raise _deny("mfa-required", "Multi-factor authentication is required.", status.HTTP_403_FORBIDDEN)
    issuer, subject = claims["iss"], str(claims["sub"])
    user_key = _linked_user_key(issuer, subject)
    settings = get_settings()
    session_token = issue_session_token(
        user_key,
        str(claims.get("name") or claims.get("preferred_username") or "")[:160],
        extra={
            "auth": AUTH_METHOD,
            "idp_iss": issuer,
            "idp_sub": subject,
            "idp_sid": str(claims.get("sid") or ""),
            "amr": [v for v in claims.get("amr", []) if isinstance(v, str)][:8],
            "auth_time": int(claims.get("auth_time") or 0),
        },
    )
    response = RedirectResponse(str(tx.get("returnTo") or "/"), status_code=303)
    response.set_cookie(session_cookie_name(), session_token, max_age=int(settings.session_ttl_seconds),
                        secure=True, httponly=True, samesite="lax", path="/")
    _clear_tx(response)
    return response


@router.post("/logout")
def logout(request: Request):
    enforce_cookie_csrf(request)
    revoke_request_session(request)
    settings = get_settings()
    end_session = ""
    if enabled():
        try:
            endpoint = metadata().get("end_session_endpoint") or ""
        except IdentityUnavailable:
            endpoint = ""  # The Workspace session is already revoked.
        if endpoint:
            params = {"client_id": settings.sc_identity_client_id}
            if settings.sc_identity_post_logout_redirect_uri:
                params["post_logout_redirect_uri"] = settings.sc_identity_post_logout_redirect_uri
            end_session = endpoint + "?" + urlencode(params)
    response = JSONResponse({"authenticated": False, "sessionRevoked": True, "endSessionUrl": end_session})
    response.delete_cookie(session_cookie_name(), path="/", secure=True, httponly=True, samesite="lax")
    return response


def _backchannel_revoke(logout_token: str) -> None:
    settings = get_settings()
    claims = verify_jwt(logout_token, audience=settings.sc_identity_client_id, required=("iss", "aud", "iat", "jti"))
    events = claims.get("events")
    if not isinstance(events, dict) or LOGOUT_EVENT not in events or "nonce" in claims:
        raise jwt.InvalidTokenError("not a logout token")
    if abs(time.time() - int(claims["iat"])) > 300:
        raise jwt.InvalidTokenError("stale logout token")
    sid, sub = str(claims.get("sid") or ""), str(claims.get("sub") or "")
    if not sid and not sub:
        raise jwt.InvalidTokenError("logout token without sid or sub")
    with session_scope() as db:
        if not consume_nonce(db, "backchannel-logout", str(claims["jti"])[:128], int(time.time()) + 900):
            raise jwt.InvalidTokenError("replayed logout token")
        if sid:
            revoke_idp_session(db, claims["iss"], sid, ttl_seconds=settings.session_ttl_seconds)
        else:
            user_key = resolve_user_key(db, claims["iss"], sub)
            if user_key:
                revoke_user_sessions(db, user_key, actor="idp:backchannel-logout", reason="identity provider logout")
        db.commit()


@router.post("/backchannel-logout")
async def backchannel_logout(request: Request):
    if not enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    body = await request.body()
    if len(body) > 16384:
        return JSONResponse({"error": "invalid_request"}, status_code=400)
    token = (parse_qs(body.decode("utf-8", "replace")).get("logout_token") or [""])[0]
    try:
        await run_in_threadpool(_backchannel_revoke, token)
    except (IdentityUnavailable, SessionVerificationUnavailable, SQLAlchemyError):
        return JSONResponse({"error": "temporarily_unavailable"}, status_code=503)
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        return JSONResponse({"error": "invalid_request"}, status_code=400)
    return JSONResponse({}, status_code=200)


# --- service-to-service bearer tokens --------------------------------------

def is_identity_bearer(authorization: str | None) -> bool:
    if not isinstance(authorization, str) or not authorization.startswith("Bearer ") or not enabled():
        return False
    return authorization[7:].count(".") == 2


def bearer_identity(authorization: str):
    """Verify an IdP access token issued for this API and map it to a linked Workspace user."""
    from .security import ServiceIdentity
    from .session_revocation import is_revoked

    settings = get_settings()
    token = authorization[7:]
    try:
        claims = verify_jwt(token, audience=settings.sc_identity_api_audience,
                            required=("iss", "sub", "aud", "exp", "iat"))
    except IdentityUnavailable:
        raise _unavailable() from None
    except jwt.PyJWTError:
        raise _deny("invalid-access-token", "Valid Workspace identity required.") from None
    if claims.get("typ", "Bearer") != "Bearer":
        raise _deny("invalid-access-token", "Valid Workspace identity required.")
    allowed = {v.strip() for v in settings.sc_identity_allowed_bearer_clients.split(",") if v.strip()}
    if allowed and claims.get("azp") not in allowed:
        raise _deny("invalid-access-token", "Valid Workspace identity required.")
    if not mfa_satisfied(claims):
        raise _deny("mfa-required", "Multi-factor authentication is required.", status.HTTP_403_FORBIDDEN)
    user_key = _linked_user_key(claims["iss"], str(claims["sub"]))
    revocation_claims = {"sub": user_key, "iat": claims["iat"], "jti": "",
                         "idp_iss": claims["iss"], "idp_sid": str(claims.get("sid") or "")}
    try:
        with session_scope() as db:
            revoked = is_revoked(db, token, revocation_claims)
    except SessionVerificationUnavailable:
        raise HTTPException(status_code=503, detail="Workspace session verification unavailable") from None
    if revoked:
        raise _deny("revoked-access-token", "Valid Workspace identity required.")
    return ServiceIdentity(
        user_key=user_key,
        principal_id=f"sc-user:{claims['sub']}",
        principal_type="sc-identity-user",
        service_principal=SC_IDENTITY_BEARER_PRINCIPAL,
        authentication_method="sc-identity-access-token",
    )
