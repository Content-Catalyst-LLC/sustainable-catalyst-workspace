"""Permanent, account-pinned authorization for Wexford ERW report routing.

This does not authorize historical recovery inventory or bypass project ownership checks.
It uses the *existing* Workspace signed session and a separately approved,
persistent allowlist. Install in the SAME Workspace backend as session_auth.
"""

import hashlib
import hmac
import json
import os
import stat
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response
from .session_auth import session_payload_from_request

router = APIRouter(prefix="/v1/private-research/erw-access", tags=["Private Wexford Access"])

POLICY_SCHEMA = "sc.wxr.permanent-report-access.v1"
PROJECT_ID = "SC-ERW-IRELAND-001"
MAX_POLICY_BYTES = 4096


def _load_policy(path: str) -> dict:
    if not path or not Path(path).is_absolute():
        raise ValueError("Access policy path is not absolute")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(fd)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_size <= 0
            or info.st_size > MAX_POLICY_BYTES
            or (info.st_mode & 0o077) != 0
            or info.st_uid not in {0, os.geteuid()}
        ):
            raise ValueError("Access policy file is not trusted")
        with os.fdopen(os.dup(fd), "rb") as f:
            raw = f.read(MAX_POLICY_BYTES + 1)
        if len(raw) > MAX_POLICY_BYTES:
            raise ValueError("Access policy too large")
        policy = json.loads(raw)
    finally:
        os.close(fd)

    required = {"schema", "enabled", "project_id", "subject_sha256", "approved_by", "approval_reference"}
    if not isinstance(policy, dict) or set(policy) != required:
        raise ValueError("Access policy schema is invalid")
    if policy["schema"] != POLICY_SCHEMA or policy["enabled"] is not True or policy["project_id"] != PROJECT_ID:
        raise ValueError("Access policy not enabled for Wexford")
    digest = policy["subject_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Access policy subject is invalid")
    if not all(isinstance(policy[k], str) and 3 <= len(policy[k].strip()) <= 200 for k in ("approved_by", "approval_reference")):
        raise ValueError("Missing approval evidence")
    return policy


def authorize_subject(subject: object, policy_file: str) -> None:
    if not isinstance(subject, str) or not subject.strip() or len(subject) > 128:
        raise HTTPException(401, "Workspace sign-in required", headers={"Cache-Control": "no-store"})
    try:
        policy = _load_policy(policy_file)
        digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(digest, policy["subject_sha256"]):
            raise ValueError("Subject not approved")
    except (OSError, ValueError, UnicodeError, TypeError):
        raise HTTPException(403, "Wexford project access denied", headers={"Cache-Control": "no-store"}) from None


@router.get("/check", include_in_schema=False)
def check(request: Request) -> Response:
    payload = session_payload_from_request(request)
    subject = payload.get("sub") if isinstance(payload, dict) else None
    authorize_subject(subject, os.getenv("WXR_PERMANENT_ACCESS_FILE", ""))
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
