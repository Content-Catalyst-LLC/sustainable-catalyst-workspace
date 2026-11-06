"""RH-PROD-05.1 — unmounted, service-only identity introspection contract.

Do NOT include this router in the production app until the dedicated
service credential, private transport, session revocation migration and
real-account security acceptance are verified.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from pathlib import Path
from sqlalchemy import select
from .models import ProjectHead

from .db import session_scope
from .session_auth import decode_session_token
from .session_revocation import SessionVerificationUnavailable, validate_session_for_service

router = APIRouter(prefix="/internal/v1/workspace", include_in_schema=False)


class IntrospectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["rh-prod-05.1/1.0"] = "rh-prod-05.1/1.0"
    project_id: str | None = Field(default=None, min_length=1, max_length=160)
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
    settings = get_settings()
    try:
        expected = (Path(settings.research_introspection_token_file).read_text().strip()
                    if getattr(settings,"research_introspection_token_file","") else settings.research_introspection_token)
    except OSError:
        raise HTTPException(status_code=503, detail="Service introspection unavailable") from None
    if expected and expected == getattr(settings,"service_token",""):
        raise HTTPException(status_code=503, detail="Dedicated service credential required")
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
            # Ownership proof comes from the authority's persisted composite key,
            # never caller owner_scope or subject alone. No project content emitted.
            query=select(ProjectHead.project_id).where(ProjectHead.user_key==claims["sub"])
            if payload.project_id is not None:
                query=query.where(ProjectHead.project_id==payload.project_id)
            project_ids=list(db.scalars(query.order_by(ProjectHead.project_id).limit(101)))
            if payload.project_id is not None and payload.project_id not in project_ids:
                raise HTTPException(status_code=404,detail="Workspace project not found")
            if len(project_ids)>100:
                raise HTTPException(status_code=409,detail="Select a specific Workspace project")
    except ValueError:
        raise HTTPException(status_code=401, detail="Workspace session invalid") from None
    except SessionVerificationUnavailable:
        raise HTTPException(status_code=503, detail="Workspace session verification unavailable") from None

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=503,detail="Workspace session verification unavailable") from None

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
        "authorized_projects": project_ids,
        "project_authority": "workspace_project_heads",
        "active": True,
        "revoked": False,
        # Owner scope is intentionally OMITTED. Research must resolve an
        # authorized server-side owner map; subject alone is not permission.
    }
