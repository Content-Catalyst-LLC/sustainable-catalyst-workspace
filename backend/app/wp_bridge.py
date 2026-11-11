"""SC-AUTH-01 WordPress bridge assertions and authenticated-response hygiene.

WordPress remains the user-facing login. For each proxied request it signs a
short-lived assertion with a bridge-only key, bound to:
- the WordPress user and a hash of the live WordPress session token;
- the session's sign-in time (so operator revoke-user applies);
- the exact method, path and body;
- a single-use nonce.
Workspace verifies it here, before routing, and never trusts a client user id.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
from pathlib import Path
from typing import Any

from starlette.concurrency import run_in_threadpool

from .config import get_settings

ASSERTION_HEADER = b"x-sc-bridge-assertion"
DOMAIN = b"sc-auth-01-wp-bridge-v1\x00"
ISSUER = "sc-wordpress-bridge"
MAX_LIFETIME_SECONDS = 120
CLOCK_SKEW_SECONDS = 5
MAX_BODY_BYTES = 64 * 1024 * 1024
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_NONCE = re.compile(r"^[0-9a-f]{32,64}$")


class BridgeAssertionError(ValueError):
    pass


def bridge_key() -> str:
    """Bridge-only key. It must not equal any other Workspace credential."""
    settings = get_settings()
    path = getattr(settings, "bridge_assertion_key_file", "").strip()
    try:
        key = Path(path).read_text(encoding="utf-8").strip() if path else getattr(settings, "bridge_assertion_key", "").strip()
    except OSError:
        return ""
    if len(key) < 32:
        return ""
    others = {settings.service_token.strip(), (settings.session_signing_secret or "").strip(),
              getattr(settings, "research_introspection_token", "").strip()}
    for name in ("session_signing_secret_file", "research_introspection_token_file"):
        other = getattr(settings, name, "").strip()
        if other:
            try:
                others.add(Path(other).read_text(encoding="utf-8").strip())
            except OSError:
                pass
    return "" if key in others else key


def sign_assertion(key: str, claims: dict[str, Any]) -> str:
    """Reference signer (the WordPress plugin implements the same bytes)."""
    encoded = base64.urlsafe_b64encode(
        json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")).decode("ascii").rstrip("=")
    return encoded + "." + hmac.new(key.encode("utf-8"), DOMAIN + encoded.encode("ascii"), hashlib.sha256).hexdigest()


def verify_assertion(key: str, assertion: str, *, method: str, target: str, body: bytes,
                     now: int | None = None) -> dict[str, Any]:
    """Check signature and every binding. Nonce single use is the caller's job."""
    now = int(time.time()) if now is None else now
    if not key:
        raise BridgeAssertionError("bridge-key-unavailable")
    if not isinstance(assertion, str) or len(assertion) > 4096 or assertion.count(".") != 1:
        raise BridgeAssertionError("malformed")
    encoded, supplied = assertion.split(".")
    expected = hmac.new(key.encode("utf-8"), DOMAIN + encoded.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, supplied):
        raise BridgeAssertionError("signature")
    try:
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        iat, exp, sat = int(claims["iat"]), int(claims["exp"]), int(claims["sat"])
        sub, sid, nonce = str(claims["sub"]), str(claims["sid"]), str(claims["nonce"])
    except (ValueError, KeyError, TypeError):
        raise BridgeAssertionError("claims") from None
    settings = get_settings()
    if claims.get("v") != 1 or claims.get("iss") != ISSUER or claims.get("aud") != settings.bridge_audience:
        raise BridgeAssertionError("scope")
    if not sub.strip() or len(sub) > 128 or not _HEX64.match(sid) or not _NONCE.match(nonce):
        raise BridgeAssertionError("claims")
    if exp - iat > MAX_LIFETIME_SECONDS or iat > now + CLOCK_SKEW_SECONDS or exp < now or sat > iat + CLOCK_SKEW_SECONDS:
        raise BridgeAssertionError("lifetime")
    if claims.get("m") != method.upper() or claims.get("p") != target:
        raise BridgeAssertionError("request-binding")
    if not hmac.compare_digest(str(claims.get("bh") or ""), hashlib.sha256(body).hexdigest()):
        raise BridgeAssertionError("body-binding")
    return claims


def _check_and_consume(claims: dict[str, Any]) -> None:
    from .db import session_scope
    from .session_revocation import consume_nonce, is_revoked
    with session_scope() as db:
        # Operator revoke-user applies to WordPress sessions signed in at or before the cutoff.
        if is_revoked(db, "wp-bridge:" + claims["sid"], {"sub": claims["sub"], "iat": claims["sat"]}):
            raise BridgeAssertionError("revoked")
        if not consume_nonce(db, "wp-bridge", claims["nonce"], int(claims["exp"])):
            db.rollback()
            raise BridgeAssertionError("replayed")
        db.commit()


async def _send_json(send, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    await send({"type": "http.response.start", "status": status, "headers": [
        (b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()),
        (b"cache-control", b"no-store"), (b"pragma", b"no-cache")]})
    await send({"type": "http.response.body", "body": body})


class AuthHygieneMiddleware:
    """Pure ASGI: verifies bridge assertions before routing and marks API responses no-store."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path", "")
        no_store = path.startswith("/v1/") or path == "/v1" or path.startswith("/internal/")

        async def send_wrapper(message):
            # SC-AUTH-01 F3: authenticated API data must never be stored by browsers or proxies.
            if no_store and message["type"] == "http.response.start":
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() not in (b"cache-control", b"pragma")]
                headers += [(b"cache-control", b"no-store, private"), (b"pragma", b"no-cache")]
                vary = [v for k, v in headers if k.lower() == b"vary"]
                if not any(b"cookie" in v.lower() for v in vary):
                    headers.append((b"vary", b"Cookie, Authorization"))
                message = dict(message, headers=headers)
            await send(message)

        assertion = next((v for k, v in scope.get("headers", []) if k.lower() == ASSERTION_HEADER), None)
        if assertion is None:
            return await self.app(scope, receive, send_wrapper)

        chunks, size, more = [], 0, True
        while more:
            message = await receive()
            if message["type"] != "http.request":
                return
            chunk = message.get("body", b"")
            size += len(chunk)
            if size > MAX_BODY_BYTES:
                return await _send_json(send, 413, {"code": "bridge-body-too-large"})
            chunks.append(chunk)
            more = message.get("more_body", False)
        body = b"".join(chunks)
        # Bind to the path exactly as sent (WordPress signs the encoded URL).
        query = scope.get("query_string", b"").decode("latin-1")
        raw_path = (scope.get("raw_path") or path.encode("utf-8")).decode("latin-1")
        target = raw_path + ("?" + query if query else "")
        try:
            claims = verify_assertion(bridge_key(), assertion.decode("latin-1"),
                                      method=scope["method"], target=target, body=body)
            await run_in_threadpool(_check_and_consume, claims)
        except BridgeAssertionError as exc:
            status = 503 if str(exc) == "bridge-key-unavailable" else 401
            return await _send_json(send, status, {"code": "bridge-assertion-refused"})
        except Exception:
            # Replay or revocation storage unavailable: deny, never fall back.
            return await _send_json(send, 503, {"code": "bridge-verification-unavailable"})

        scope.setdefault("state", {})["sc_bridge_identity"] = {"sub": claims["sub"], "sid": claims["sid"]}
        sent = False

        async def replay():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        return await self.app(scope, replay, send_wrapper)
