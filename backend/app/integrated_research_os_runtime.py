from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping
from uuid import uuid4

VERSION = "3.64.0"
RUNTIME_SCHEMA = "sc-workspace-integrated-research-os-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-integrated-research-os-request/1.0"
RESULT_SCHEMA = "sc-workspace-integrated-research-os-result/1.0"
CONTEXT_SCHEMA = "sc-workspace-integrated-research-context/1.0"
BINDING_SCHEMA = "sc-workspace-integrated-research-binding/1.0"
HANDOFF_SCHEMA = "sc-workspace-integrated-research-handoff-plan/1.0"
READINESS_SCHEMA = "sc-workspace-integrated-research-readiness/1.0"
PACKAGE_SCHEMA = "sc-workspace-integrated-research-os-package/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-integrated-research-os-snapshot/1.0"

UPSTREAM = {
    "agenticWorkflow": "sc-workspace-agentic-research-workflow-runtime/1.0",
    "humanGovernance": "sc-workspace-human-governance-approval-intervention-runtime/1.0",
    "multiAgentCoordination": "sc-workspace-multi-agent-orchestration-specialist-coordination-runtime/1.0",
    "reproducibleAgenticPackage": "sc-workspace-reproducible-agentic-research-package-runtime/1.0",
}

STAGES = (
    "projects", "sources", "analysis", "models", "agents",
    "governance", "visualizations", "decisions", "publication",
)

OPERATIONS = (
    "workspace.research-os.validate",
    "workspace.research-os.create-context",
    "workspace.research-os.bind-object",
    "workspace.research-os.link-stage",
    "workspace.research-os.readiness",
    "workspace.research-os.handoff-plan",
    "workspace.research-os.package",
    "workspace.research-os.snapshot",
)

BOUNDARIES = {
    "boundedOperationsOnly": True,
    "arbitraryCodeExecution": False,
    "automaticModelExecutionEnabled": False,
    "automaticAgentExecutionEnabled": False,
    "automaticApprovalEnabled": False,
    "automaticGovernanceBypassEnabled": False,
    "automaticPublicationEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "automaticTruthDeterminationEnabled": False,
    "automaticEvidenceRankingEnabled": False,
    "automaticNarrativeSelectionEnabled": False,
    "automaticDecisionAuthorityEnabled": False,
    "crossStageMutationEnabled": False,
    "stageAuthorityPreserved": True,
    "humanGovernancePreserved": True,
    "provenancePreserved": True,
    "dissentPreserved": True,
    "reproduciblePackagingSupported": True,
    "maxBindings": 1024,
    "maxStageLinks": 2048,
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _id(prefix):
    return f"{prefix}_{uuid4().hex}"

def _copy(value):
    return deepcopy(value)

def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _authority():
    return {
        "executeModels": False,
        "executeAgents": False,
        "approveGovernance": False,
        "publish": False,
        "externalSideEffects": False,
        "determineTruth": False,
        "rankEvidence": False,
        "decide": False,
    }

def _context(payload, require_open=False):
    context = payload.get("context")
    if not isinstance(context, dict) or context.get("schema") != CONTEXT_SCHEMA:
        raise ValueError("valid integrated research context is required")
    context = _copy(context)
    if require_open and context.get("status") != "active":
        raise ValueError("integrated research context is not active")
    authority = context.get("authority") or {}
    if any(bool(authority.get(k)) for k in _authority()):
        raise ValueError("integrated research OS authority boundary violated")
    return context

def create_context(payload):
    project_ref = str(payload.get("projectRef") or payload.get("researchRef") or "").strip()
    if not project_ref:
        raise ValueError("projectRef is required")
    context = {
        "schema": CONTEXT_SCHEMA,
        "version": VERSION,
        "contextId": str(payload.get("contextId") or _id("research_os")),
        "projectRef": project_ref,
        "title": str(payload.get("title") or "Integrated Research OS Context"),
        "status": "active",
        "createdAt": _now(),
        "updatedAt": _now(),
        "stages": {stage: {"bindings": [], "links": []} for stage in STAGES},
        "bindings": [],
        "stageLinks": [],
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "dissentRefs": list(payload.get("dissentRefs") or []),
        "upstreamRuntimeSchemas": _copy(UPSTREAM),
        "authority": _authority(),
    }
    return {"context": context, "authorityGranted": False}

def bind_object(payload):
    context = _context(payload, True)
    if len(context["bindings"]) >= BOUNDARIES["maxBindings"]:
        raise ValueError("maxBindings exceeded")
    stage = str(payload.get("stage") or "").strip()
    if stage not in STAGES:
        raise ValueError("unsupported research stage")
    object_ref = str(payload.get("objectRef") or "").strip()
    object_schema = str(payload.get("objectSchema") or "").strip()
    if not object_ref or not object_schema:
        raise ValueError("objectRef and objectSchema are required")
    binding = {
        "schema": BINDING_SCHEMA,
        "version": VERSION,
        "bindingId": str(payload.get("bindingId") or _id("research_binding")),
        "stage": stage,
        "objectRef": object_ref,
        "objectSchema": object_schema,
        "role": str(payload.get("role") or "research-object"),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "boundAt": _now(),
        "sourceMutationPerformed": False,
        "authorityGranted": False,
    }
    context["bindings"].append(binding)
    context["stages"][stage]["bindings"].append(binding["bindingId"])
    context["updatedAt"] = _now()
    return {"context": context, "binding": binding}

def link_stage(payload):
    context = _context(payload, True)
    if len(context["stageLinks"]) >= BOUNDARIES["maxStageLinks"]:
        raise ValueError("maxStageLinks exceeded")
    source = str(payload.get("sourceStage") or "").strip()
    target = str(payload.get("targetStage") or "").strip()
    if source not in STAGES or target not in STAGES:
        raise ValueError("sourceStage and targetStage must be supported research stages")
    if source == target:
        raise ValueError("sourceStage and targetStage must differ")
    link = {
        "schema": "sc-workspace-integrated-research-stage-link/1.0",
        "version": VERSION,
        "linkId": str(payload.get("linkId") or _id("stage_link")),
        "sourceStage": source,
        "targetStage": target,
        "relation": str(payload.get("relation") or "research-flow"),
        "sourceRefs": list(payload.get("sourceRefs") or []),
        "targetRefs": list(payload.get("targetRefs") or []),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "createdAt": _now(),
        "automaticHandoff": False,
        "automaticMutation": False,
    }
    context["stageLinks"].append(link)
    context["stages"][source]["links"].append(link["linkId"])
    context["stages"][target]["links"].append(link["linkId"])
    context["updatedAt"] = _now()
    return {"context": context, "link": link}

def readiness(payload):
    context = _context(payload)
    required = list(payload.get("requiredStages") or STAGES)
    if any(stage not in STAGES for stage in required):
        raise ValueError("requiredStages contains unsupported research stage")
    status = {}
    for stage in STAGES:
        bindings = context["stages"][stage]["bindings"]
        status[stage] = {
            "bindingCount": len(bindings),
            "present": bool(bindings),
            "required": stage in required,
        }
    missing = [stage for stage in required if not status[stage]["present"]]
    report = {
        "schema": READINESS_SCHEMA,
        "version": VERSION,
        "contextId": context["contextId"],
        "ready": not missing,
        "requiredStages": required,
        "missingStages": missing,
        "stageStatus": status,
        "evaluatedAt": _now(),
        "descriptiveOnly": True,
        "approvalPerformed": False,
        "executionPerformed": False,
    }
    return {"readiness": report, "context": context}

def handoff_plan(payload):
    context = _context(payload)
    source = str(payload.get("sourceStage") or "").strip()
    target = str(payload.get("targetStage") or "").strip()
    if source not in STAGES or target not in STAGES or source == target:
        raise ValueError("valid distinct sourceStage and targetStage are required")
    source_bindings = [x for x in context.get("bindings") or [] if x.get("stage") == source]
    plan = {
        "schema": HANDOFF_SCHEMA,
        "version": VERSION,
        "planId": str(payload.get("planId") or _id("handoff_plan")),
        "contextId": context["contextId"],
        "sourceStage": source,
        "targetStage": target,
        "sourceBindingIds": [x["bindingId"] for x in source_bindings],
        "requestedTargetRole": str(payload.get("requestedTargetRole") or "research-input"),
        "governanceRequired": bool(payload.get("governanceRequired", False)),
        "humanAcceptanceRequired": True,
        "automaticExecution": False,
        "automaticAcceptance": False,
        "automaticMutation": False,
        "createdAt": _now(),
    }
    return {"handoffPlan": plan, "context": context}

def package_context(payload):
    context = _context(payload)
    body = {
        "contextId": context["contextId"],
        "projectRef": context["projectRef"],
        "stages": _copy(context["stages"]),
        "bindings": _copy(context["bindings"]),
        "stageLinks": _copy(context["stageLinks"]),
        "provenanceRefs": list(context.get("provenanceRefs") or []),
        "dissentRefs": list(context.get("dissentRefs") or []),
        "upstreamRuntimeSchemas": _copy(context.get("upstreamRuntimeSchemas") or {}),
        "authority": _copy(context.get("authority") or {}),
    }
    package = {
        "schema": PACKAGE_SCHEMA,
        "version": VERSION,
        "packageId": str(payload.get("packageId") or _id("research_os_package")),
        "contextId": context["contextId"],
        "projectRef": context["projectRef"],
        "createdAt": _now(),
        "body": body,
        "packageDigest": _digest(body),
        "reproducible": True,
        "executionAllowed": False,
        "approvalAuthorityGranted": False,
        "publicationAuthorityGranted": False,
    }
    return {"package": package, "context": context}

def snapshot(payload):
    context = _context(payload)
    captured = _now()
    body = {"context": context, "capturedAt": captured, "version": VERSION}
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "contextId": context["contextId"],
        "capturedAt": captured,
        "context": context,
        "snapshotDigest": _digest(body),
        "authorityGranted": False,
        "executionAllowed": False,
    }

def validate(payload):
    errors = []
    context = payload.get("context")
    if context is not None:
        if not isinstance(context, dict) or context.get("schema") != CONTEXT_SCHEMA:
            errors.append("invalid integrated research context schema")
        else:
            authority = context.get("authority") or {}
            if any(bool(authority.get(k)) for k in _authority()):
                errors.append("integrated research OS authority boundary violated")
            stages = context.get("stages") or {}
            missing = [stage for stage in STAGES if stage not in stages]
            if missing:
                errors.append("missing research stages: " + ",".join(missing))
    return {"valid": not errors, "errors": errors}

def runtime_profile():
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Integrated Research OS Runtime",
        "researchLifecycle": list(STAGES),
        "researchStageCount": len(STAGES),
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "upstreamRuntimeSchemas": _copy(UPSTREAM),
        "capabilities": {
            "unifiedResearchContext": True,
            "crossStageObjectBinding": True,
            "crossStageLineage": True,
            "readinessAssessment": True,
            "boundedHandoffPlanning": True,
            "reproducibleResearchOSPackages": True,
            "portableSnapshots": True,
        },
        **BOUNDARIES,
    }

def operation_index():
    return {
        "schema": "sc-workspace-integrated-research-os-operation-index/1.0",
        "version": VERSION,
        "items": [{
            "operation": op,
            "input": REQUEST_SCHEMA,
            "output": RESULT_SCHEMA,
            "bounded": True,
            "executionAuthority": False,
            "approvalAuthority": False,
            "publicationAuthority": False,
        } for op in OPERATIONS],
        **BOUNDARIES,
    }

def execute(operation, payload):
    handlers = {
        "workspace.research-os.validate": validate,
        "workspace.research-os.create-context": create_context,
        "workspace.research-os.bind-object": bind_object,
        "workspace.research-os.link-stage": link_stage,
        "workspace.research-os.readiness": readiness,
        "workspace.research-os.handoff-plan": handoff_plan,
        "workspace.research-os.package": package_context,
        "workspace.research-os.snapshot": snapshot,
    }
    if operation not in handlers:
        raise ValueError("unsupported operation")
    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "operation": operation,
        "result": handlers[operation](payload or {}),
    }
