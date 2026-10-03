from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping, MutableMapping
from uuid import uuid4

VERSION = "3.62.0"
RUNTIME_SCHEMA = "sc-workspace-multi-agent-orchestration-specialist-coordination-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-multi-agent-orchestration-request/1.0"
RESULT_SCHEMA = "sc-workspace-multi-agent-orchestration-result/1.0"
SPECIALIST_SCHEMA = "sc-workspace-specialist-agent/1.0"
TEAM_SCHEMA = "sc-workspace-specialist-team/1.0"
ASSIGNMENT_SCHEMA = "sc-workspace-specialist-assignment/1.0"
RECEIPT_SCHEMA = "sc-workspace-specialist-result-receipt/1.0"
CONFLICT_SCHEMA = "sc-workspace-specialist-conflict/1.0"
SYNTHESIS_SCHEMA = "sc-workspace-specialist-synthesis/1.0"
GOVERNANCE_HANDOFF_SCHEMA = "sc-workspace-governance-handoff/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-multi-agent-coordination-snapshot/1.0"

UPSTREAM_AGENTIC_SCHEMA = "sc-workspace-agentic-research-workflow-runtime/1.0"
UPSTREAM_GOVERNANCE_SCHEMA = "sc-workspace-human-governance-approval-intervention-runtime/1.0"
UPSTREAM_GOVERNANCE_POLICY_SCHEMA = "sc-workspace-human-governance-policy/1.0"

BOUNDED_OPERATIONS = (
    "workspace.multi-agent.validate",
    "workspace.multi-agent.register-specialist",
    "workspace.multi-agent.create-team",
    "workspace.multi-agent.delegate",
    "workspace.multi-agent.record-result",
    "workspace.multi-agent.reconcile",
    "workspace.multi-agent.governance-handoff",
    "workspace.multi-agent.snapshot",
)

SPECIALIST_ROLE_FAMILIES = (
    "research_evidence",
    "data_quantitative_analysis",
    "modeling_forecasting",
    "scientific_computing",
    "linguistics_corpus",
    "investigation_provenance",
    "visualization",
    "synthesis",
)

DEFAULT_BOUNDARIES = {
    "boundedOperationsOnly": True,
    "arbitraryCodeExecution": False,
    "automaticExternalSideEffectsEnabled": False,
    "coordinatorApprovalAuthorityEnabled": False,
    "specialistApprovalAuthorityEnabled": False,
    "automaticGovernanceBypassEnabled": False,
    "automaticTruthDeterminationEnabled": False,
    "automaticEvidenceRankingEnabled": False,
    "automaticConflictResolutionEnabled": False,
    "humanGovernanceRequiredForSensitiveActions": True,
    "specialistCapabilityConstraintsRequired": True,
    "dissentPreserved": True,
    "provenancePreserved": True,
    "maxSpecialists": 16,
    "maxAssignments": 64,
    "maxCoordinationRounds": 8,
}

SENSITIVE_ACTIONS = {
    "claim_promotion",
    "evidence_mutation",
    "model_approval",
    "external_side_effect",
    "high_impact_decision",
    "irreversible_operation",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _specialist(raw: Mapping[str, Any]) -> Dict[str, Any]:
    role = str(raw.get("roleFamily") or raw.get("role") or "").strip()
    if role not in SPECIALIST_ROLE_FAMILIES:
        raise ValueError("unsupported specialist roleFamily")
    capabilities = sorted({str(x).strip() for x in (raw.get("capabilityIds") or []) if str(x).strip()})
    if not capabilities:
        raise ValueError("specialist capabilityIds must not be empty")
    authority = dict(raw.get("authority") or {})
    if any(bool(authority.get(k)) for k in ("approve", "bypassGovernance", "externalSideEffects", "arbitraryCodeExecution")):
        raise ValueError("specialists may not receive approval, governance-bypass, external-side-effect, or arbitrary-code authority")
    return {
        "schema": SPECIALIST_SCHEMA,
        "version": VERSION,
        "specialistId": str(raw.get("specialistId") or _id("specialist")),
        "name": str(raw.get("name") or role.replace("_", " ").title()),
        "roleFamily": role,
        "capabilityIds": capabilities,
        "authority": {
            "approve": False,
            "bypassGovernance": False,
            "externalSideEffects": False,
            "arbitraryCodeExecution": False,
        },
        "provenanceRefs": list(raw.get("provenanceRefs") or []),
        "registeredAt": str(raw.get("registeredAt") or _utcnow()),
    }


def register_specialist(payload: Mapping[str, Any]) -> Dict[str, Any]:
    raw = payload.get("specialist") if isinstance(payload.get("specialist"), dict) else payload
    specialist = _specialist(raw)
    return {"specialist": specialist, "coordinationAllowed": True}


def _normalize_team(payload: Mapping[str, Any]) -> Dict[str, Any]:
    existing = payload.get("team")
    if isinstance(existing, dict) and existing.get("schema") == TEAM_SCHEMA:
        return deepcopy(existing)
    raw_specialists = list(payload.get("specialists") or [])
    if not raw_specialists:
        raise ValueError("at least one specialist is required")
    if len(raw_specialists) > DEFAULT_BOUNDARIES["maxSpecialists"]:
        raise ValueError("maxSpecialists exceeded")
    specialists = []
    for raw in raw_specialists:
        if isinstance(raw, dict) and raw.get("schema") == SPECIALIST_SCHEMA:
            specialist = deepcopy(raw)
            # Revalidate authority invariants on portable specialist objects.
            if specialist.get("roleFamily") not in SPECIALIST_ROLE_FAMILIES:
                raise ValueError("unsupported specialist roleFamily")
            if not specialist.get("capabilityIds"):
                raise ValueError("specialist capabilityIds must not be empty")
            authority = specialist.get("authority") or {}
            if any(bool(authority.get(k)) for k in ("approve", "bypassGovernance", "externalSideEffects", "arbitraryCodeExecution")):
                raise ValueError("specialist authority violates runtime boundaries")
        else:
            specialist = _specialist(raw)
        specialists.append(specialist)
    ids = [s["specialistId"] for s in specialists]
    if len(ids) != len(set(ids)):
        raise ValueError("specialistId values must be unique")
    coordinator = dict(payload.get("coordinator") or {})
    coordinator_id = str(coordinator.get("coordinatorId") or coordinator.get("actorId") or "coordinator").strip()
    return {
        "schema": TEAM_SCHEMA,
        "version": VERSION,
        "teamId": str(payload.get("teamId") or _id("team")),
        "title": str(payload.get("title") or "Specialist research team"),
        "coordinator": {
            "coordinatorId": coordinator_id,
            "approvalAuthority": False,
            "governanceBypassAuthority": False,
            "externalSideEffectAuthority": False,
        },
        "specialists": specialists,
        "assignments": [],
        "receipts": [],
        "conflicts": [],
        "syntheses": [],
        "coordinationRound": 0,
        "status": "ready",
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "createdAt": _utcnow(),
        "updatedAt": _utcnow(),
    }


def create_team(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = _normalize_team(payload)
    return {"team": team, "coordinationAllowed": True}


def _find_specialist(team: Mapping[str, Any], specialist_id: str) -> Dict[str, Any]:
    for specialist in team.get("specialists") or []:
        if specialist.get("specialistId") == specialist_id:
            return specialist
    raise ValueError("specialist not found")


def delegate(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = _normalize_team(payload)
    if len(team.get("assignments") or []) >= DEFAULT_BOUNDARIES["maxAssignments"]:
        raise ValueError("maxAssignments exceeded")
    specialist_id = str(payload.get("specialistId") or "").strip()
    specialist = _find_specialist(team, specialist_id)
    capability_id = str(payload.get("capabilityId") or "").strip()
    if capability_id not in set(specialist.get("capabilityIds") or []):
        raise ValueError("assignment capabilityId is not granted to specialist")
    action_type = str(payload.get("actionType") or "analysis").strip()
    requires_governance = bool(payload.get("requiresGovernance")) or action_type in SENSITIVE_ACTIONS
    assignment = {
        "schema": ASSIGNMENT_SCHEMA,
        "version": VERSION,
        "assignmentId": str(payload.get("assignmentId") or _id("assignment")),
        "teamId": team["teamId"],
        "specialistId": specialist_id,
        "roleFamily": specialist["roleFamily"],
        "capabilityId": capability_id,
        "objective": str(payload.get("objective") or ""),
        "inputRefs": list(payload.get("inputRefs") or []),
        "expectedOutputKinds": list(payload.get("expectedOutputKinds") or []),
        "actionType": action_type,
        "requiresGovernance": requires_governance,
        "governanceSatisfied": False if requires_governance else True,
        "status": "waiting_governance" if requires_governance else "ready",
        "createdAt": _utcnow(),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
    }
    team.setdefault("assignments", []).append(assignment)
    team["updatedAt"] = _utcnow()
    if requires_governance:
        team["status"] = "waiting_governance"
    return {
        "team": team,
        "assignment": assignment,
        "executionAllowed": not requires_governance,
        "governanceRequired": requires_governance,
    }


def record_result(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = _normalize_team(payload)
    assignment_id = str(payload.get("assignmentId") or "").strip()
    assignment = next((a for a in team.get("assignments") or [] if a.get("assignmentId") == assignment_id), None)
    if not assignment:
        raise ValueError("assignment not found")
    if assignment.get("requiresGovernance") and not assignment.get("governanceSatisfied"):
        raise ValueError("assignment governance requirement is not satisfied")
    if assignment.get("status") not in {"ready", "running"}:
        raise ValueError("assignment is not executable")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "receiptId": _id("receipt"),
        "assignmentId": assignment_id,
        "specialistId": assignment["specialistId"],
        "status": str(payload.get("status") or "succeeded"),
        "artifactRefs": list(payload.get("artifactRefs") or []),
        "evidenceRefs": list(payload.get("evidenceRefs") or []),
        "claims": deepcopy(payload.get("claims") or []),
        "limitations": list(payload.get("limitations") or []),
        "confidence": payload.get("confidence"),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "recordedAt": _utcnow(),
    }
    if receipt["status"] not in {"succeeded", "failed", "inconclusive"}:
        raise ValueError("result status must be succeeded, failed, or inconclusive")
    assignment["status"] = receipt["status"]
    assignment["receiptRef"] = receipt["receiptId"]
    team.setdefault("receipts", []).append(receipt)
    team["updatedAt"] = _utcnow()
    return {"team": team, "receipt": receipt}


def reconcile(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = _normalize_team(payload)
    receipts = list(payload.get("receipts") or team.get("receipts") or [])
    if len(receipts) < 2:
        raise ValueError("at least two specialist receipts are required for reconciliation")
    round_number = int(team.get("coordinationRound") or 0) + 1
    if round_number > DEFAULT_BOUNDARIES["maxCoordinationRounds"]:
        raise ValueError("maxCoordinationRounds exceeded")
    disagreements = list(payload.get("disagreements") or [])
    conflict_records = []
    for d in disagreements:
        conflict_records.append({
            "schema": CONFLICT_SCHEMA,
            "conflictId": _id("conflict"),
            "topic": str((d or {}).get("topic") or "unspecified"),
            "positions": deepcopy((d or {}).get("positions") or []),
            "status": "unresolved",
            "humanResolutionRequired": bool((d or {}).get("humanResolutionRequired", False)),
            "recordedAt": _utcnow(),
        })
    synthesis = {
        "schema": SYNTHESIS_SCHEMA,
        "version": VERSION,
        "synthesisId": _id("synthesis"),
        "teamId": team["teamId"],
        "receiptRefs": [str(r.get("receiptId") or "") for r in receipts],
        "agreementSummary": deepcopy(payload.get("agreementSummary") or []),
        "conflictRefs": [c["conflictId"] for c in conflict_records],
        "dissentPreserved": True,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "coordinatorDecisionAuthority": False,
        "recommendedNextSteps": deepcopy(payload.get("recommendedNextSteps") or []),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "createdAt": _utcnow(),
    }
    team["coordinationRound"] = round_number
    team.setdefault("conflicts", []).extend(conflict_records)
    team.setdefault("syntheses", []).append(synthesis)
    team["status"] = "needs_human_resolution" if any(c["humanResolutionRequired"] for c in conflict_records) else "coordinated"
    team["updatedAt"] = _utcnow()
    return {"team": team, "synthesis": synthesis, "conflicts": conflict_records}


def governance_handoff(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = _normalize_team(payload)
    assignment_id = str(payload.get("assignmentId") or "").strip()
    assignment = next((a for a in team.get("assignments") or [] if a.get("assignmentId") == assignment_id), None)
    if not assignment:
        raise ValueError("assignment not found")
    if not assignment.get("requiresGovernance"):
        raise ValueError("assignment does not require governance")
    policy = payload.get("policy")
    if policy is not None and (not isinstance(policy, dict) or policy.get("schema") != UPSTREAM_GOVERNANCE_POLICY_SCHEMA):
        raise ValueError("invalid v3.61 governance policy schema")
    handoff = {
        "schema": GOVERNANCE_HANDOFF_SCHEMA,
        "version": VERSION,
        "handoffId": _id("governance_handoff"),
        "teamId": team["teamId"],
        "assignmentId": assignment_id,
        "targetRuntimeSchema": UPSTREAM_GOVERNANCE_SCHEMA,
        "targetOperation": "workspace.governance.request-approval",
        "approvalRequestPayload": {
            "policy": deepcopy(policy),
            "action": assignment["actionType"],
            "subjectRef": assignment_id,
            "requester": {
                "actorId": str((team.get("coordinator") or {}).get("coordinatorId") or "coordinator"),
                "actorType": "agent",
            },
            "reason": payload.get("reason"),
            "riskLevel": str(payload.get("riskLevel") or "normal"),
            "provenanceRefs": list(payload.get("provenanceRefs") or []),
        },
        "coordinatorMayApprove": False,
        "specialistMayApprove": False,
        "approvalBypassAllowed": False,
        "createdAt": _utcnow(),
    }
    return {"team": team, "handoff": handoff, "executionAllowed": False}


def validate(payload: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    team = payload.get("team")
    if team is not None and (not isinstance(team, dict) or team.get("schema") != TEAM_SCHEMA):
        errors.append("invalid specialist team schema")
    specialist = payload.get("specialist")
    if specialist is not None and (not isinstance(specialist, dict) or specialist.get("schema") != SPECIALIST_SCHEMA):
        errors.append("invalid specialist schema")
    assignment = payload.get("assignment")
    if assignment is not None and (not isinstance(assignment, dict) or assignment.get("schema") != ASSIGNMENT_SCHEMA):
        errors.append("invalid assignment schema")
    return {"valid": not errors, "errors": errors}


def snapshot(payload: Mapping[str, Any]) -> Dict[str, Any]:
    team = deepcopy(payload.get("team"))
    body = {
        "team": team,
        "agenticRuntimeSchema": UPSTREAM_AGENTIC_SCHEMA,
        "governanceRuntimeSchema": UPSTREAM_GOVERNANCE_SCHEMA,
    }
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "capturedAt": _utcnow(),
        "coordination": body,
        "coordinationDigest": _digest(body),
        "provenancePreserved": True,
    }


def runtime_profile() -> Dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Multi-Agent Orchestration & Specialist Coordination Runtime",
        "boundedOperations": list(BOUNDED_OPERATIONS),
        "boundedOperationCount": len(BOUNDED_OPERATIONS),
        "specialistRoleFamilies": list(SPECIALIST_ROLE_FAMILIES),
        "specialistRoleFamilyCount": len(SPECIALIST_ROLE_FAMILIES),
        "upstreamRuntimeSchemas": {
            "agenticWorkflow": UPSTREAM_AGENTIC_SCHEMA,
            "humanGovernance": UPSTREAM_GOVERNANCE_SCHEMA,
        },
        "capabilities": {
            "specialistRegistration": True,
            "capabilityBoundDelegation": True,
            "multiSpecialistTeams": True,
            "specialistResultReceipts": True,
            "conflictDetectionAndPreservation": True,
            "boundedCoordinationRounds": True,
            "governanceHandoffs": True,
            "portableCoordinationSnapshots": True,
        },
        **DEFAULT_BOUNDARIES,
    }


def operation_index() -> Dict[str, Any]:
    human_authority_operations = []
    return {
        "schema": "sc-workspace-multi-agent-orchestration-operation-index/1.0",
        "version": VERSION,
        "items": [
            {
                "operation": op,
                "input": REQUEST_SCHEMA,
                "output": RESULT_SCHEMA,
                "bounded": True,
                "humanAuthorityRequired": op in human_authority_operations,
            }
            for op in BOUNDED_OPERATIONS
        ],
        "governanceDelegatedTo": UPSTREAM_GOVERNANCE_SCHEMA,
        **DEFAULT_BOUNDARIES,
    }


def execute(operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    dispatch = {
        "workspace.multi-agent.validate": validate,
        "workspace.multi-agent.register-specialist": register_specialist,
        "workspace.multi-agent.create-team": create_team,
        "workspace.multi-agent.delegate": delegate,
        "workspace.multi-agent.record-result": record_result,
        "workspace.multi-agent.reconcile": reconcile,
        "workspace.multi-agent.governance-handoff": governance_handoff,
        "workspace.multi-agent.snapshot": snapshot,
    }
    if operation not in dispatch:
        raise ValueError("unsupported multi-agent orchestration operation")
    result = dispatch[operation](payload or {})
    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "operation": operation,
        "result": result,
        "bounded": True,
        "provenancePreserved": True,
    }
