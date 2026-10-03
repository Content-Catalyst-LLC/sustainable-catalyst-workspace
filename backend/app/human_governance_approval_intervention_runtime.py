from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping, MutableMapping
from uuid import uuid4

VERSION = "3.61.0"
RUNTIME_SCHEMA = "sc-workspace-human-governance-approval-intervention-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-human-governance-request/1.0"
RESULT_SCHEMA = "sc-workspace-human-governance-result/1.0"
POLICY_SCHEMA = "sc-workspace-human-governance-policy/1.0"
APPROVAL_SCHEMA = "sc-workspace-human-approval-request/1.0"
DECISION_SCHEMA = "sc-workspace-human-approval-decision/1.0"
INTERVENTION_SCHEMA = "sc-workspace-human-intervention/1.0"
STATE_SCHEMA = "sc-workspace-human-governance-state/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-human-governance-snapshot/1.0"

BOUNDED_OPERATIONS = (
    "workspace.governance.validate",
    "workspace.governance.register-policy",
    "workspace.governance.request-approval",
    "workspace.governance.decide",
    "workspace.governance.intervene",
    "workspace.governance.resume",
    "workspace.governance.snapshot",
)

DEFAULT_BOUNDARIES = {
    "automaticApprovalEnabled": False,
    "agentApprovalAuthorityEnabled": False,
    "selfApprovalEnabled": False,
    "approvalBypassEnabled": False,
    "automaticResumeEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "arbitraryCodeExecution": False,
    "humanInterventionSupported": True,
    "decisionImmutability": True,
    "provenancePreserved": True,
    "maxApprovalRequests": 64,
    "maxInterventions": 64,
}

DEFAULT_REQUIRED_ACTIONS = (
    "claim_promotion",
    "evidence_mutation",
    "model_approval",
    "external_side_effect",
    "high_impact_decision",
    "irreversible_operation",
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _human_actor(actor: Mapping[str, Any]) -> Dict[str, Any]:
    actor = dict(actor or {})
    actor_id = str(actor.get("actorId") or actor.get("id") or "").strip()
    actor_type = str(actor.get("actorType") or actor.get("type") or "").strip().lower()
    role = str(actor.get("role") or "").strip()
    if not actor_id:
        raise ValueError("actor.actorId is required")
    if actor_type != "human":
        raise ValueError("governance authority requires actorType=human")
    if not role:
        raise ValueError("actor.role is required")
    return {"actorId": actor_id, "actorType": "human", "role": role}


def register_policy(payload: Mapping[str, Any]) -> Dict[str, Any]:
    raw = dict(payload.get("policy") or payload)
    title = str(raw.get("title") or "Human governance policy")
    approver_roles = [str(x) for x in (raw.get("approverRoles") or ["research_owner"])]
    required_actions = [str(x) for x in (raw.get("requiredActions") or DEFAULT_REQUIRED_ACTIONS)]
    if not approver_roles:
        raise ValueError("approverRoles must not be empty")
    if not required_actions:
        raise ValueError("requiredActions must not be empty")
    return {
        "schema": POLICY_SCHEMA,
        "version": VERSION,
        "policyId": str(raw.get("policyId") or _id("policy")),
        "title": title,
        "createdAt": str(raw.get("createdAt") or _utcnow()),
        "approverRoles": approver_roles,
        "requiredActions": required_actions,
        "requireHumanActor": True,
        "allowSelfApproval": False,
        "allowApprovalBypass": False,
        "automaticResume": False,
        "provenanceRefs": list(raw.get("provenanceRefs") or []),
    }


def request_approval(payload: Mapping[str, Any]) -> Dict[str, Any]:
    policy = dict(payload.get("policy") or {})
    if policy.get("schema") != POLICY_SCHEMA:
        raise ValueError("valid governance policy is required")
    action = str(payload.get("action") or "").strip()
    subject_ref = str(payload.get("subjectRef") or "").strip()
    requester = dict(payload.get("requester") or {})
    requester_id = str(requester.get("actorId") or requester.get("id") or "").strip()
    if not action:
        raise ValueError("action is required")
    if not subject_ref:
        raise ValueError("subjectRef is required")
    if not requester_id:
        raise ValueError("requester.actorId is required")
    required = action in set(policy.get("requiredActions") or [])
    approval = {
        "schema": APPROVAL_SCHEMA,
        "version": VERSION,
        "approvalId": _id("approval"),
        "policyId": policy["policyId"],
        "subjectRef": subject_ref,
        "action": action,
        "reason": payload.get("reason"),
        "riskLevel": str(payload.get("riskLevel") or "normal"),
        "requester": {"actorId": requester_id, "actorType": str(requester.get("actorType") or requester.get("type") or "agent")},
        "requestedAt": _utcnow(),
        "required": required,
        "status": "pending" if required else "not_required",
        "decisionRef": None,
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
    }
    return {"approval": approval, "executionAllowed": not required}


def decide(payload: Mapping[str, Any]) -> Dict[str, Any]:
    policy = dict(payload.get("policy") or {})
    approval = deepcopy(dict(payload.get("approval") or {}))
    if policy.get("schema") != POLICY_SCHEMA:
        raise ValueError("valid governance policy is required")
    if approval.get("schema") != APPROVAL_SCHEMA:
        raise ValueError("valid approval request is required")
    if approval.get("status") != "pending":
        raise ValueError("approval request is not pending")
    actor = _human_actor(payload.get("actor") or {})
    if actor["role"] not in set(policy.get("approverRoles") or []):
        raise ValueError("actor role is not authorized to approve")
    if actor["actorId"] == str((approval.get("requester") or {}).get("actorId") or ""):
        raise ValueError("self-approval is prohibited")
    decision = str(payload.get("decision") or "").strip()
    if decision not in {"approve", "reject", "request_revision"}:
        raise ValueError("decision must be approve, reject, or request_revision")
    record = {
        "schema": DECISION_SCHEMA,
        "decisionId": _id("decision"),
        "approvalId": approval["approvalId"],
        "policyId": policy["policyId"],
        "decision": decision,
        "actor": actor,
        "note": payload.get("note"),
        "decidedAt": _utcnow(),
        "immutable": True,
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
    }
    approval["decisionRef"] = record["decisionId"]
    approval["status"] = {
        "approve": "approved",
        "reject": "rejected",
        "request_revision": "revision_requested",
    }[decision]
    return {"approval": approval, "decision": record, "executionAllowed": decision == "approve"}


def _normalize_state(payload: Mapping[str, Any]) -> Dict[str, Any]:
    existing = payload.get("state")
    if isinstance(existing, dict) and existing.get("schema") == STATE_SCHEMA:
        state = deepcopy(existing)
    else:
        subject_ref = str(payload.get("subjectRef") or "").strip()
        if not subject_ref:
            raise ValueError("subjectRef is required when state is not supplied")
        state = {
            "schema": STATE_SCHEMA,
            "version": VERSION,
            "stateId": _id("governance"),
            "subjectRef": subject_ref,
            "status": "active",
            "approvals": [],
            "decisions": [],
            "interventions": [],
            "provenanceRefs": list(payload.get("provenanceRefs") or []),
            "createdAt": _utcnow(),
            "updatedAt": _utcnow(),
        }
    return state


def intervene(payload: Mapping[str, Any]) -> Dict[str, Any]:
    state = _normalize_state(payload)
    actor = _human_actor(payload.get("actor") or {})
    action = str(payload.get("intervention") or payload.get("action") or "").strip()
    if action not in {"pause", "cancel", "request_revision", "escalate"}:
        raise ValueError("unsupported intervention")
    if len(state.get("interventions") or []) >= DEFAULT_BOUNDARIES["maxInterventions"]:
        raise ValueError("maxInterventions exceeded")
    if state.get("status") == "cancelled":
        raise ValueError("cancelled governance state cannot be changed")
    record = {
        "schema": INTERVENTION_SCHEMA,
        "interventionId": _id("intervention"),
        "subjectRef": state["subjectRef"],
        "action": action,
        "actor": actor,
        "reason": payload.get("reason"),
        "recordedAt": _utcnow(),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
    }
    state.setdefault("interventions", []).append(record)
    if action == "pause":
        state["status"] = "paused"
    elif action == "cancel":
        state["status"] = "cancelled"
    elif action == "request_revision":
        state["status"] = "revision_requested"
    elif action == "escalate":
        state["status"] = "escalated"
    state["updatedAt"] = _utcnow()
    return {"state": state, "intervention": record, "executionAllowed": state["status"] == "active"}


def resume(payload: Mapping[str, Any]) -> Dict[str, Any]:
    state = _normalize_state(payload)
    actor = _human_actor(payload.get("actor") or {})
    if state.get("status") not in {"paused", "revision_requested", "escalated"}:
        raise ValueError("only paused, revision_requested, or escalated governance state can be resumed")
    if any(a.get("status") == "rejected" for a in state.get("approvals") or []):
        raise ValueError("rejected approvals must be resolved before resume")
    record = {
        "schema": INTERVENTION_SCHEMA,
        "interventionId": _id("intervention"),
        "subjectRef": state["subjectRef"],
        "action": "resume",
        "actor": actor,
        "reason": payload.get("reason"),
        "recordedAt": _utcnow(),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
    }
    state.setdefault("interventions", []).append(record)
    state["status"] = "active"
    state["updatedAt"] = _utcnow()
    return {"state": state, "intervention": record, "executionAllowed": True}


def validate(payload: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    policy = payload.get("policy")
    if policy is not None and (not isinstance(policy, dict) or policy.get("schema") != POLICY_SCHEMA):
        errors.append("invalid policy schema")
    approval = payload.get("approval")
    if approval is not None and (not isinstance(approval, dict) or approval.get("schema") != APPROVAL_SCHEMA):
        errors.append("invalid approval schema")
    state = payload.get("state")
    if state is not None and (not isinstance(state, dict) or state.get("schema") != STATE_SCHEMA):
        errors.append("invalid governance state schema")
    return {"valid": not errors, "errors": errors}


def snapshot(payload: Mapping[str, Any]) -> Dict[str, Any]:
    body = {
        "policy": deepcopy(payload.get("policy")),
        "approval": deepcopy(payload.get("approval")),
        "state": deepcopy(payload.get("state")),
    }
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "capturedAt": _utcnow(),
        "governance": body,
        "governanceDigest": _digest(body),
    }


def runtime_profile() -> Dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Human Governance, Approval & Intervention Runtime",
        "boundedOperations": list(BOUNDED_OPERATIONS),
        "boundedOperationCount": len(BOUNDED_OPERATIONS),
        **DEFAULT_BOUNDARIES,
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "policy": POLICY_SCHEMA,
            "approval": APPROVAL_SCHEMA,
            "decision": DECISION_SCHEMA,
            "intervention": INTERVENTION_SCHEMA,
            "state": STATE_SCHEMA,
            "snapshot": SNAPSHOT_SCHEMA,
        },
    }


def operation_index() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-human-governance-operation-index/1.0",
        "version": VERSION,
        "boundedOperationsOnly": True,
        "operations": [
            {"operation": op, "arbitraryCodeExecution": False, "humanAuthorityRequired": op in {
                "workspace.governance.decide", "workspace.governance.intervene", "workspace.governance.resume"
            }}
            for op in BOUNDED_OPERATIONS
        ],
        "boundaries": dict(DEFAULT_BOUNDARIES),
    }


def execute(operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    if operation not in BOUNDED_OPERATIONS:
        raise ValueError("unsupported governance operation")
    payload = dict(payload or {})
    if operation == "workspace.governance.validate":
        result = validate(payload)
    elif operation == "workspace.governance.register-policy":
        result = {"policy": register_policy(payload)}
    elif operation == "workspace.governance.request-approval":
        result = request_approval(payload)
    elif operation == "workspace.governance.decide":
        result = decide(payload)
    elif operation == "workspace.governance.intervene":
        result = intervene(payload)
    elif operation == "workspace.governance.resume":
        result = resume(payload)
    else:
        result = {"snapshot": snapshot(payload)}
    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "operation": operation,
        **result,
    }
