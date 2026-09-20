from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuthorizationDecisionReceipt
from .utils import iso, sha256_hex

AUTHORIZATION_SCHEMA = "sc-workspace-backend-authorization/1.0"
PRINCIPAL_SCHEMA = "sc-workspace-principal-identity/1.0"
DECISION_SCHEMA = "sc-workspace-authorization-decision/1.0"
POLICY_ID = "workspace-authenticated-user-v1"
POLICY_REVISION = 1
SERVICE_PRINCIPAL = "wordpress-proxy"

ACTIONS = (
    "workspace.read",
    "workspace.write",
    "workspace.execute",
    "workspace.sync",
    "workspace.handoff.prepare",
    "workspace.handoff.accept",
    "workspace.authorization.inspect",
    "workspace.authorization.evaluate",
)

RESOURCE_KINDS = (
    "workspace", "project", "notebook", "artifact", "dataset", "model",
    "execution", "visualization", "study-package", "handoff", "authorization",
)

GRANTS = frozenset(ACTIONS)


class AuthorizationEvaluateRequest(BaseModel):
    schema: Literal["sc-workspace-authorization-evaluate-request/1.0"]
    action: str = Field(min_length=1, max_length=96)
    resourceKind: str = Field(default="workspace", min_length=1, max_length=64)
    resourceId: str = Field(default="", max_length=160)
    projectId: str = Field(default="", max_length=160)
    context: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_known_values(self):
        if self.action not in ACTIONS:
            raise ValueError("unsupported authorization action")
        if self.resourceKind not in RESOURCE_KINDS:
            raise ValueError("unsupported authorization resource kind")
        return self


def profile() -> dict[str, Any]:
    return {
        "schema": AUTHORIZATION_SCHEMA,
        "backendAuthoritative": True,
        "browserAuthoritativeAuthorization": False,
        "identityResolution": "service-credential-plus-wordpress-user-context",
        "servicePrincipal": SERVICE_PRINCIPAL,
        "humanPrincipalType": "wordpress-user",
        "userIsolationKey": "user_key",
        "policyId": POLICY_ID,
        "policyRevision": POLICY_REVISION,
        "defaultEffect": "deny",
        "supportedActions": list(ACTIONS),
        "resourceKinds": list(RESOURCE_KINDS),
        "routePolicyEnforcement": True,
        "projectScopeExplicit": True,
        "durableDecisionReceipts": True,
        "clientSuppliedRolesTrusted": False,
        "clientSuppliedScopesTrusted": False,
        "serviceCredentialsBrowserVisible": False,
        "arbitraryCodeExecution": False,
    }


def principal_payload(identity: Any) -> dict[str, Any]:
    return {
        "schema": PRINCIPAL_SCHEMA,
        "principalId": identity.principal_id,
        "principalType": identity.principal_type,
        "servicePrincipal": identity.service_principal,
        "userKey": identity.user_key,
        "authenticationMethod": identity.authentication_method,
        "policyId": POLICY_ID,
        "policyRevision": POLICY_REVISION,
        "effectiveScopes": sorted(GRANTS),
        "serverResolved": True,
        "browserAuthoritative": False,
    }


def action_for_request(method: str, path: str) -> str:
    method = method.upper()
    if path.startswith("/v1/authorization"):
        return "workspace.authorization.evaluate" if method == "POST" else "workspace.authorization.inspect"
    if path == "/v1/queries/execute":
        return "workspace.read"
    if path == "/v1/commands/execute":
        return "workspace.execute"
    if path.startswith("/v1/sync"):
        return "workspace.sync" if method == "POST" else "workspace.read"
    if path == "/v1/handoffs" and method == "POST":
        return "workspace.handoff.prepare"
    if path.startswith("/v1/handoffs/") and path.endswith("/accept") and method == "POST":
        return "workspace.handoff.accept"
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "workspace.write"
    return "workspace.read"


def evaluate(identity: Any, action: str, resource_kind: str = "workspace", resource_id: str = "", project_id: str = "", context: dict[str, Any] | None = None) -> dict[str, Any]:
    known_action = action in ACTIONS
    known_resource = resource_kind in RESOURCE_KINDS
    authenticated = bool(getattr(identity, "user_key", "")) and getattr(identity, "service_principal", "") == SERVICE_PRINCIPAL
    allowed = authenticated and known_action and known_resource and action in GRANTS
    reason = "authenticated-user-scoped-policy" if allowed else (
        "unknown-action" if not known_action else "unknown-resource-kind" if not known_resource else "principal-not-authorized"
    )
    basis = {
        "principalId": getattr(identity, "principal_id", ""),
        "servicePrincipal": getattr(identity, "service_principal", ""),
        "userKey": getattr(identity, "user_key", ""),
        "action": action,
        "resourceKind": resource_kind,
        "resourceId": resource_id,
        "projectId": project_id,
        "effect": "allow" if allowed else "deny",
        "reason": reason,
        "policyId": POLICY_ID,
        "policyRevision": POLICY_REVISION,
        "context": context or {},
    }
    return {
        "schema": DECISION_SCHEMA,
        **basis,
        "decisionFingerprint": sha256_hex(basis),
        "serverAuthoritative": True,
    }


def authorize_request(identity: Any, method: str, path: str) -> dict[str, Any]:
    action = action_for_request(method, path)
    return evaluate(identity, action, "authorization" if path.startswith("/v1/authorization") else "workspace", path)


def evaluate_and_record(db: Session, identity: Any, payload: AuthorizationEvaluateRequest) -> dict[str, Any]:
    decision = evaluate(identity, payload.action, payload.resourceKind, payload.resourceId, payload.projectId, payload.context)
    receipt = AuthorizationDecisionReceipt(
        user_key=identity.user_key,
        receipt_id="authz-" + uuid4().hex[:24],
        principal_id=identity.principal_id,
        principal_type=identity.principal_type,
        service_principal=identity.service_principal,
        action=payload.action,
        resource_kind=payload.resourceKind,
        resource_id=payload.resourceId,
        project_id=payload.projectId,
        effect=decision["effect"],
        reason=decision["reason"],
        policy_id=POLICY_ID,
        policy_revision=POLICY_REVISION,
        decision_fingerprint=decision["decisionFingerprint"],
        context_json=payload.context,
    )
    db.add(receipt)
    db.commit()
    return {"ok": decision["effect"] == "allow", "item": decision, "receipt": receipt_payload(receipt)}


def receipt_payload(row: AuthorizationDecisionReceipt) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-authorization-decision-receipt/1.0",
        "receiptId": row.receipt_id,
        "principalId": row.principal_id,
        "principalType": row.principal_type,
        "servicePrincipal": row.service_principal,
        "action": row.action,
        "resourceKind": row.resource_kind,
        "resourceId": row.resource_id,
        "projectId": row.project_id,
        "effect": row.effect,
        "reason": row.reason,
        "policyId": row.policy_id,
        "policyRevision": row.policy_revision,
        "decisionFingerprint": row.decision_fingerprint,
        "context": row.context_json,
        "createdAt": iso(row.created_at),
    }


def list_decisions(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(AuthorizationDecisionReceipt)
        .where(AuthorizationDecisionReceipt.user_key == user_key)
        .order_by(AuthorizationDecisionReceipt.created_at.desc())
        .limit(limit)
    ).all()
    return [receipt_payload(row) for row in rows]
