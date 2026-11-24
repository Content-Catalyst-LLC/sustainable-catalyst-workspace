"""RH-PROD-05.1 private Workspace/Research service proof protocol.

Identical independently vendored implementation in both services.
Never transmit the shared credential or log session tokens. The nonce binds
the reply to a particular request; Workspace revocation remains authoritative.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re

NONCE_RE = re.compile(r"^[0-9a-f]{64}$")
PROOF_RE = re.compile(r"^[0-9a-f]{64}$")
REQUEST_DOMAIN = b"sc-rhprod05-private-request-v1\x00"
RESPONSE_DOMAIN = b"sc-rhprod05-private-response-v1\x00"


def _canonical(value: dict) -> bytes:
    if not isinstance(value, dict):
        raise ValueError("A structured private request/response is required")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _mac(secret: str, nonce: str, payload: dict, domain: bytes) -> str:
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("Private service key unavailable")
    if not isinstance(nonce, str) or not NONCE_RE.fullmatch(nonce):
        raise ValueError("Invalid service request nonce")
    return hmac.new(
        secret.encode("utf-8"),
        domain + bytes.fromhex(nonce) + b"\x00" + _canonical(payload),
        hashlib.sha256,
    ).hexdigest()


def request_proof(secret: str, nonce: str, payload: dict) -> str:
    return _mac(secret, nonce, payload, REQUEST_DOMAIN)


def response_proof(secret: str, nonce: str, payload: dict) -> str:
    return _mac(secret, nonce, payload, RESPONSE_DOMAIN)


def verify_request(secret: str, nonce: str | None, payload: dict,
                   supplied: str | None) -> bool:
    if not supplied or not isinstance(supplied, str) or not PROOF_RE.fullmatch(supplied):
        return False
    try:
        return hmac.compare_digest(request_proof(secret, nonce, payload), supplied)
    except ValueError:
        return False


def verify_response(secret: str, nonce: str | None, payload: dict,
                    supplied: str | None) -> bool:
    if not supplied or not isinstance(supplied, str) or not PROOF_RE.fullmatch(supplied):
        return False
    try:
        return hmac.compare_digest(response_proof(secret, nonce, payload), supplied)
    except ValueError:
        return False
