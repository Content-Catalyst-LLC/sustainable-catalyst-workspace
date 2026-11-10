"""SC-ED-01 — authenticated, persisted, Workspace-signed approvals for Research publication.

Research publishes nothing without one Workspace human-governance approval per dimension
(scientific, rights, ownership, publication; area publication for Research areas). Before this
module those records came from the stateless governance runtime, whose actor was whatever the
payload claimed. Here:

* the requester and the decider are the authenticated Workspace identity, never payload fields;
* the project owner grants roles: ``editor`` (may raise requests on the owner's project) and
  ``approver:<dimension>`` (may decide that one dimension); grants are explicit and revocable;
* a decider must differ from the requester, and must hold the dimension grant (the owner may
  decide only the ``ownership`` dimension, and only for requests an editor raised);
* requests and decisions are persisted; a decided request never changes again;
* the decision is returned as a record signed with the Workspace Research export key under its
  own domain, so Research verifies it with the key it already pins and cannot mint one itself.

The approval and decision bodies are produced by the existing human-governance runtime
(``request_approval`` / ``decide``) so Research's approval contract is unchanged.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select

from . import human_governance_approval_intervention_runtime as hg
from .db import session_scope
from .models import ProjectHead, ResearchApprovalGrant, ResearchApprovalRequest
from .research_exports import AUDIENCE, ISSUER, _signing_key, public_key_info, sign_document
from .security import ServiceIdentity, require_service_identity
from .utils import sha256_hex

RECORD_SCHEMA = "sc-workspace-research-approval-record/1.0"
POLICY_ID = "sc-ed-01-research-publication-approval/1"
ACTIONS = {
    "scientific": "research_scientific_review",
    "rights": "research_rights_clearance",
    "ownership": "research_ownership_confirmation",
    "publication": "research_publication",
    "area-publication": "research_area_publication",
}
ROLES = frozenset({"editor", *(f"approver:{d}" for d in ACTIONS)})
ANY_PROJECT = "*"
SUBJECT = re.compile(r"^research-(object|area):[A-Za-z0-9._:-]{1,160}#[0-9a-f]{64}$")
router = APIRouter(prefix="/v1/research-approvals", tags=["SC-ED-01 Research approvals"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _scope(user_key: str) -> str:
    return f"workspace-user:{user_key}"


def _policy() -> dict[str, Any]:
    roles = ["research_owner", *(f"research_{d.replace('-', '_')}_approver" for d in ACTIONS)]
    return hg.register_policy({"policyId": POLICY_ID, "title": "Research publication approvals",
                               "approverRoles": roles, "requiredActions": list(ACTIONS.values()),
                               "createdAt": "2026-11-10T00:00:00Z"})


def _project_ok(db, owner: str, project_id: str) -> bool:
    return project_id == ANY_PROJECT or db.get(ProjectHead, {"user_key": owner, "project_id": project_id}) is not None


def active_grant(db, owner: str, grantee: str, role: str, project_id: str) -> ResearchApprovalGrant | None:
    return db.scalars(select(ResearchApprovalGrant).where(
        ResearchApprovalGrant.owner_user_key == owner, ResearchApprovalGrant.grantee_user_key == grantee,
        ResearchApprovalGrant.role == role, ResearchApprovalGrant.revoked_at.is_(None),
        ResearchApprovalGrant.project_id.in_([project_id, ANY_PROJECT]))).first()


def check_subject(dimension: str, subject_ref: str) -> None:
    match = SUBJECT.fullmatch(subject_ref)
    if not match:
        raise ValueError("subjectRef must be research-object:<id>#<sha256> or research-area:<id>#<sha256>")
    if (match.group(1) == "area") != (dimension == "area-publication"):
        raise ValueError("area-publication approves Research areas; other dimensions approve Research objects")


def may_decide(owner: str, requester: str, decider: str, dimension: str, has_grant: bool) -> str:
    """Return the decider's role, or raise PermissionError. Pure, so the rule is unit-tested."""
    if decider == requester:
        raise PermissionError("self-approval is prohibited")
    if has_grant:
        return f"research_{dimension.replace('-', '_')}_approver"
    if decider == owner and dimension == "ownership":
        return "research_owner"
    raise PermissionError(f"no active approver:{dimension} grant from the project owner")


def grant_view(row: ResearchApprovalGrant) -> dict[str, Any]:
    return {"grantId": row.grant_id, "ownerScope": _scope(row.owner_user_key), "grantee": _scope(row.grantee_user_key),
            "role": row.role, "projectId": row.project_id, "grantedAt": row.granted_at.isoformat(),
            "revokedAt": row.revoked_at.isoformat() if row.revoked_at else None}


def request_view(row: ResearchApprovalRequest) -> dict[str, Any]:
    return {"approvalId": row.approval_id, "ownerScope": _scope(row.owner_user_key),
            "requester": _scope(row.requester_user_key), "projectId": row.project_id, "dimension": row.dimension,
            "action": row.action, "subjectRef": row.subject_ref, "subjectTitle": row.subject_title,
            "status": row.status, "requestedAt": row.requested_at.isoformat(),
            "decidedAt": row.decided_at.isoformat() if row.decided_at else None,
            "decider": _scope(row.decider_user_key) if row.decider_user_key else None,
            "recordSha256": row.record_sha256 or None}


# ---------------------------------------------------------------------------
# HTTP


class GrantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    granteeUserKey: str = Field(min_length=1, max_length=128)
    role: str = Field(min_length=1, max_length=48)
    projectId: str = Field(min_length=1, max_length=160)


class ApprovalRequestIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ownerUserKey: str = Field(default="", max_length=128)
    projectId: str = Field(min_length=1, max_length=160)
    dimension: str = Field(min_length=1, max_length=32)
    subjectRef: str = Field(min_length=1, max_length=320)
    subjectTitle: str = Field(default="", max_length=300)
    reason: str = Field(default="", max_length=2000)


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["approve", "reject", "request_revision"]
    note: str = Field(default="", max_length=2000)


def _forbid(exc: Exception, code: int) -> HTTPException:
    return HTTPException(status_code=code, detail=str(exc))


@router.get("/profile")
def profile_route():
    return {"schema": "sc-workspace-research-approval-profile/1.0", "recordSchema": RECORD_SCHEMA,
            "policyId": POLICY_ID, "dimensions": ACTIONS, "roles": sorted(ROLES), "audience": AUDIENCE,
            "actorFrom": "authenticated-identity", "selfApproval": False, "signed": "Ed25519 (Research export key)"}


@router.post("/grants")
def create_grant_route(payload: GrantRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    if payload.role not in ROLES:
        raise HTTPException(status_code=422, detail=f"role must be one of {sorted(ROLES)}")
    if payload.granteeUserKey == identity.user_key:
        raise HTTPException(status_code=422, detail="owners cannot grant roles to themselves")
    with session_scope() as db:
        if not _project_ok(db, identity.user_key, payload.projectId):
            raise HTTPException(status_code=404, detail="Workspace project not found.")
        existing = active_grant(db, identity.user_key, payload.granteeUserKey, payload.role, payload.projectId)
        if existing is not None and existing.project_id == payload.projectId:
            return {"item": grant_view(existing), "created": False}
        row = ResearchApprovalGrant(grant_id=f"rag_{uuid4().hex}", owner_user_key=identity.user_key,
                                    grantee_user_key=payload.granteeUserKey, role=payload.role,
                                    project_id=payload.projectId, granted_at=_now())
        db.add(row)
        db.commit()
        return {"item": grant_view(row), "created": True}


@router.get("/grants")
def list_grants_route(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        rows = db.scalars(select(ResearchApprovalGrant).where(or_(
            ResearchApprovalGrant.owner_user_key == identity.user_key,
            ResearchApprovalGrant.grantee_user_key == identity.user_key)).order_by(ResearchApprovalGrant.granted_at)).all()
        return {"items": [grant_view(r) for r in rows]}


@router.post("/grants/{grant_id}/revoke")
def revoke_grant_route(grant_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = db.get(ResearchApprovalGrant, grant_id)
        if row is None or row.owner_user_key != identity.user_key:
            raise HTTPException(status_code=404, detail="Research approval grant not found.")
        row.revoked_at = row.revoked_at or _now()
        db.commit()
        return {"item": grant_view(row)}


@router.post("/requests")
def create_request_route(payload: ApprovalRequestIn, identity: ServiceIdentity = Depends(require_service_identity)):
    if payload.dimension not in ACTIONS:
        raise HTTPException(status_code=422, detail=f"dimension must be one of {sorted(ACTIONS)}")
    try:
        check_subject(payload.dimension, payload.subjectRef)
    except ValueError as exc:
        raise _forbid(exc, 422) from exc
    owner = payload.ownerUserKey or identity.user_key
    project = ANY_PROJECT if payload.dimension == "area-publication" else payload.projectId
    with session_scope() as db:
        # Same answer for absent and foreign projects; editors act only where the owner granted them.
        if not _project_ok(db, owner, project) or (
                owner != identity.user_key and active_grant(db, owner, identity.user_key, "editor", project) is None):
            raise HTTPException(status_code=404, detail="Workspace project not found.")
        pending = db.scalars(select(ResearchApprovalRequest).where(
            ResearchApprovalRequest.owner_user_key == owner, ResearchApprovalRequest.subject_ref == payload.subjectRef,
            ResearchApprovalRequest.dimension == payload.dimension, ResearchApprovalRequest.status == "pending")).first()
        if pending is not None:
            raise HTTPException(status_code=409, detail={"code": "approval-already-pending", "approvalId": pending.approval_id})
        approval = hg.request_approval({
            "policy": _policy(), "action": ACTIONS[payload.dimension], "subjectRef": payload.subjectRef,
            "reason": payload.reason or None, "provenanceRefs": [payload.subjectRef],
            "requester": {"actorId": _scope(identity.user_key), "actorType": "human"},
        })["approval"]
        row = ResearchApprovalRequest(
            approval_id=approval["approvalId"], owner_user_key=owner, requester_user_key=identity.user_key,
            requester_auth=identity.authentication_method, project_id=project, dimension=payload.dimension,
            action=approval["action"], subject_ref=payload.subjectRef, subject_title=payload.subjectTitle,
            status="pending", approval_json=approval, requested_at=_now())
        db.add(row)
        db.commit()
        return {"item": request_view(row)}


@router.get("/requests")
def list_requests_route(role: Literal["owner", "requester", "approver"] = Query(default="approver"),
                        status: str = Query(default="pending", max_length=32),
                        identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        q = select(ResearchApprovalRequest)
        if status != "any":
            q = q.where(ResearchApprovalRequest.status == status)
        if role == "owner":
            q = q.where(ResearchApprovalRequest.owner_user_key == identity.user_key)
        elif role == "requester":
            q = q.where(ResearchApprovalRequest.requester_user_key == identity.user_key)
        rows = db.scalars(q.order_by(ResearchApprovalRequest.requested_at).limit(500)).all()
        if role == "approver":
            rows = [r for r in rows if r.requester_user_key != identity.user_key and (
                active_grant(db, r.owner_user_key, identity.user_key, f"approver:{r.dimension}", r.project_id)
                or (r.dimension == "ownership" and r.owner_user_key == identity.user_key))]
        return {"items": [request_view(r) for r in rows]}


def _visible(row: ResearchApprovalRequest | None, user_key: str) -> ResearchApprovalRequest:
    if row is None or user_key not in {row.owner_user_key, row.requester_user_key, row.decider_user_key}:
        raise HTTPException(status_code=404, detail="Research approval request not found.")
    return row


@router.post("/requests/{approval_id}/decide")
def decide_route(approval_id: str, payload: DecisionIn, identity: ServiceIdentity = Depends(require_service_identity)):
    _signing_key()
    with session_scope() as db:
        row = db.get(ResearchApprovalRequest, approval_id, with_for_update=True)
        if row is None:
            raise HTTPException(status_code=404, detail="Research approval request not found.")
        grant = active_grant(db, row.owner_user_key, identity.user_key, f"approver:{row.dimension}", row.project_id)
        try:
            role = may_decide(row.owner_user_key, row.requester_user_key, identity.user_key, row.dimension, grant is not None)
        except PermissionError as exc:
            raise _forbid(exc, 403) from exc
        if row.status != "pending":
            raise HTTPException(status_code=409, detail=f"approval request is {row.status}")
        out = hg.decide({"policy": _policy(), "approval": row.approval_json, "decision": payload.decision,
                         "note": payload.note or None, "provenanceRefs": [row.subject_ref],
                         "actor": {"actorId": _scope(identity.user_key), "actorType": "human", "role": role}})
        now = _now()
        record = sign_document(RECORD_SCHEMA, {
            "schema": RECORD_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE,
            "ownerScope": _scope(row.owner_user_key), "projectId": row.project_id, "dimension": row.dimension,
            "action": row.action, "subjectRef": row.subject_ref, "grantId": grant.grant_id if grant else "owner",
            "authentication": {"requester": row.requester_auth, "decider": identity.authentication_method},
            "approval": out["approval"], "decision": out["decision"], "issuedAt": now.isoformat(),
        })
        row.status = out["approval"]["status"]
        row.approval_json = out["approval"]
        row.decision_json = out["decision"]
        row.record_json = record
        row.record_sha256 = sha256_hex(record)
        row.decider_user_key = identity.user_key
        row.decider_auth = identity.authentication_method
        row.grant_id = grant.grant_id if grant else "owner"
        row.decided_at = now
        db.commit()
        return {"item": request_view(row), "record": record}


@router.post("/requests/{approval_id}/withdraw")
def withdraw_route(approval_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = _visible(db.get(ResearchApprovalRequest, approval_id, with_for_update=True), identity.user_key)
        if identity.user_key not in {row.owner_user_key, row.requester_user_key}:
            raise HTTPException(status_code=404, detail="Research approval request not found.")
        if row.status != "pending":
            raise HTTPException(status_code=409, detail=f"approval request is {row.status}")
        row.status = "withdrawn"
        row.decided_at = _now()
        db.commit()
        return {"item": request_view(row)}


@router.get("/requests/{approval_id}/record")
def record_route(approval_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = _visible(db.get(ResearchApprovalRequest, approval_id), identity.user_key)
        if row.record_json is None:
            raise HTTPException(status_code=409, detail=f"approval request is {row.status}")
        return row.record_json


@router.get("/public-key")
def public_key_route():
    return {"schema": "sc-workspace-research-export-key/1.0", **public_key_info()}
