from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional
from uuid import uuid4

VERSION = "3.60.0"
RUNTIME_SCHEMA = "sc-workspace-agentic-research-workflow-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-agentic-research-workflow-request/1.0"
RESULT_SCHEMA = "sc-workspace-agentic-research-workflow-result/1.0"
WORKFLOW_SCHEMA = "sc-workspace-agentic-research-workflow/1.0"
STEP_SCHEMA = "sc-workspace-agentic-research-step/1.0"
RECEIPT_SCHEMA = "sc-workspace-agentic-execution-receipt/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-agentic-workflow-snapshot/1.0"

OPERATIONS = (
    "workspace.agent.validate",
    "workspace.agent.plan",
    "workspace.agent.next-step",
    "workspace.agent.record-result",
    "workspace.agent.review",
    "workspace.agent.replan",
    "workspace.agent.snapshot",
)

DEFAULT_BOUNDARIES = {
    "arbitraryCodeExecution": False,
    "automaticClaimPromotionEnabled": False,
    "automaticEvidenceMutationEnabled": False,
    "automaticModelApprovalEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "humanReviewSupported": True,
    "provenancePreserved": True,
    "maxSteps": 32,
    "maxReplans": 3,
}

_TERMINAL = {"succeeded", "failed", "cancelled", "skipped"}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _digest(value: Any) -> str:
    return sha256(repr(value).encode("utf-8")).hexdigest()


def runtime_profile() -> Dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Agentic Research Workflow Runtime",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "goalDecomposition": True,
        "dependencyAware": True,
        "capabilityBoundExecution": True,
        "boundedReplanning": True,
        "prePostExecutionReview": True,
        "executionReceipts": True,
        "workflowSnapshots": True,
        **DEFAULT_BOUNDARIES,
    }


def operation_index() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-agentic-research-workflow-operation-index/1.0",
        "version": VERSION,
        "items": [
            {
                "operation": op,
                "input": REQUEST_SCHEMA,
                "output": RESULT_SCHEMA,
                "bounded": True,
            }
            for op in OPERATIONS
        ],
        "boundedOperationsOnly": True,
        **DEFAULT_BOUNDARIES,
    }


def _normalize_step(raw: Mapping[str, Any], ordinal: int) -> Dict[str, Any]:
    binding = dict(raw.get("binding") or {})
    if not binding.get("capabilityId") or not binding.get("operation"):
        raise ValueError("each step requires binding.capabilityId and binding.operation")
    review_policy = raw.get("reviewPolicy", "never")
    if review_policy not in {"never", "before_execution", "after_execution", "before_and_after"}:
        raise ValueError("invalid reviewPolicy")
    return {
        "schema": STEP_SCHEMA,
        "stepId": raw.get("stepId") or _id("step"),
        "ordinal": ordinal,
        "title": str(raw.get("title") or f"Step {ordinal}"),
        "objective": str(raw.get("objective") or ""),
        "binding": {
            "capabilityId": str(binding["capabilityId"]),
            "operation": str(binding["operation"]),
            "runtimeId": binding.get("runtimeId"),
            "adapterId": binding.get("adapterId"),
            "inputRefs": list(binding.get("inputRefs") or []),
            "outputKinds": list(binding.get("outputKinds") or []),
        },
        "dependsOn": list(raw.get("dependsOn") or []),
        "reviewPolicy": review_policy,
        "status": "planned",
        "artifactRefs": [],
        "provenanceRefs": [],
        "receiptRef": None,
        "error": None,
    }


def plan_workflow(request: Mapping[str, Any]) -> Dict[str, Any]:
    goal = dict(request.get("goal") or {})
    if not goal.get("question"):
        raise ValueError("goal.question is required")
    raw_steps = list(request.get("steps") or [])
    if not raw_steps:
        raise ValueError("at least one step is required")

    boundaries = {**DEFAULT_BOUNDARIES, **dict(request.get("boundaries") or {})}
    if len(raw_steps) > int(boundaries["maxSteps"]):
        raise ValueError("workflow exceeds maxSteps")

    steps = [_normalize_step(s, i + 1) for i, s in enumerate(raw_steps)]
    ids = {s["stepId"] for s in steps}
    if len(ids) != len(steps):
        raise ValueError("stepId values must be unique")
    for s in steps:
        if s["stepId"] in s["dependsOn"]:
            raise ValueError("step cannot depend on itself")
        unknown = [d for d in s["dependsOn"] if d not in ids]
        if unknown:
            raise ValueError(f"unknown dependencies for {s['stepId']}: {unknown}")
        if not s["dependsOn"]:
            s["status"] = "ready"

    return {
        "schema": WORKFLOW_SCHEMA,
        "version": VERSION,
        "workflowId": request.get("workflowId") or _id("workflow"),
        "createdAt": _utcnow(),
        "updatedAt": _utcnow(),
        "status": "ready",
        "goal": {
            "title": str(goal.get("title") or "Research workflow"),
            "question": str(goal["question"]),
            "contextRefs": list(goal.get("contextRefs") or []),
            "constraints": list(goal.get("constraints") or []),
            "desiredOutputs": list(goal.get("desiredOutputs") or []),
        },
        "boundaries": boundaries,
        "replanCount": 0,
        "steps": steps,
        "receipts": [],
        "reviews": [],
        "provenanceRefs": list(request.get("provenanceRefs") or []),
    }


def _step(workflow: MutableMapping[str, Any], step_id: str) -> MutableMapping[str, Any]:
    for s in workflow.get("steps", []):
        if s.get("stepId") == step_id:
            return s
    raise ValueError("step not found")


def _refresh(workflow: MutableMapping[str, Any]) -> None:
    succeeded = {s["stepId"] for s in workflow["steps"] if s["status"] == "succeeded"}
    for s in workflow["steps"]:
        if s["status"] == "planned" and all(d in succeeded for d in s["dependsOn"]):
            s["status"] = "ready"

    statuses = {s["status"] for s in workflow["steps"]}
    if all(s in {"succeeded", "skipped"} for s in statuses):
        workflow["status"] = "completed"
    elif "waiting_review" in statuses:
        workflow["status"] = "waiting_review"
    elif "running" in statuses:
        workflow["status"] = "running"
    elif "failed" in statuses:
        workflow["status"] = "failed"
    elif "ready" in statuses:
        workflow["status"] = "ready"
    workflow["updatedAt"] = _utcnow()


def next_step(workflow: Mapping[str, Any]) -> Dict[str, Any]:
    wf = deepcopy(workflow)
    _refresh(wf)
    for s in sorted(wf["steps"], key=lambda x: x["ordinal"]):
        if s["status"] == "ready":
            before = s["reviewPolicy"] in {"before_execution", "before_and_after"}
            approved = any(
                r.get("stepId") == s["stepId"] and r.get("decision") == "approve" and r.get("phase") == "before"
                for r in wf.get("reviews", [])
            )
            if before and not approved:
                s["status"] = "waiting_review"
                s["reviewPhase"] = "before"
                _refresh(wf)
                return {"workflow": wf, "step": deepcopy(s), "action": "review"}
            s["status"] = "running"
            _refresh(wf)
            return {"workflow": wf, "step": deepcopy(s), "action": "execute"}
    return {"workflow": wf, "step": None, "action": "none"}


def record_result(workflow: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
    wf = deepcopy(workflow)
    s = _step(wf, str(payload.get("stepId") or ""))
    if s["status"] != "running":
        raise ValueError("step must be running")

    error = payload.get("error")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "receiptId": _id("receipt"),
        "workflowId": wf["workflowId"],
        "stepId": s["stepId"],
        "capabilityId": s["binding"]["capabilityId"],
        "operation": s["binding"]["operation"],
        "runtimeId": s["binding"].get("runtimeId"),
        "adapterId": s["binding"].get("adapterId"),
        "recordedAt": _utcnow(),
        "status": "failed" if error else "succeeded",
        "inputRefs": list(s["binding"].get("inputRefs") or []),
        "artifactRefs": list(payload.get("artifactRefs") or []),
        "provenanceRefs": list(payload.get("provenanceRefs") or []),
        "outputDigest": _digest(payload.get("output")),
        "error": error,
    }
    wf.setdefault("receipts", []).append(receipt)
    s["receiptRef"] = receipt["receiptId"]
    s["artifactRefs"] = receipt["artifactRefs"]
    s["provenanceRefs"] = receipt["provenanceRefs"]

    if error:
        s["status"] = "failed"
        s["error"] = str(error)
    elif s["reviewPolicy"] in {"after_execution", "before_and_after"}:
        s["status"] = "waiting_review"
        s["reviewPhase"] = "after"
    else:
        s["status"] = "succeeded"
    _refresh(wf)
    return {"workflow": wf, "receipt": receipt}


def review(workflow: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
    wf = deepcopy(workflow)
    s = _step(wf, str(payload.get("stepId") or ""))
    decision = str(payload.get("decision") or "")
    if decision not in {"approve", "reject", "request_revision"}:
        raise ValueError("invalid review decision")
    if s["status"] != "waiting_review":
        raise ValueError("step is not waiting for review")
    phase = s.get("reviewPhase") or "after"
    item = {
        "reviewId": _id("review"),
        "stepId": s["stepId"],
        "phase": phase,
        "decision": decision,
        "reviewerId": str(payload.get("reviewerId") or "human-reviewer"),
        "note": payload.get("note"),
        "decidedAt": _utcnow(),
    }
    wf.setdefault("reviews", []).append(item)
    if decision == "approve":
        s["status"] = "ready" if phase == "before" else "succeeded"
    elif decision == "request_revision":
        s["status"] = "ready"
        s["receiptRef"] = None
    else:
        s["status"] = "cancelled"
        wf["status"] = "paused"
    _refresh(wf)
    return {"workflow": wf, "review": item}


def replan(workflow: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
    wf = deepcopy(workflow)
    maximum = int(wf.get("boundaries", {}).get("maxReplans", DEFAULT_BOUNDARIES["maxReplans"]))
    if int(wf.get("replanCount", 0)) >= maximum:
        raise ValueError("maxReplans exceeded")
    if wf.get("status") == "completed":
        raise ValueError("completed workflows cannot be replanned")
    planned = plan_workflow({
        "workflowId": wf["workflowId"],
        "goal": wf["goal"],
        "steps": payload.get("steps") or [],
        "boundaries": wf["boundaries"],
        "provenanceRefs": wf.get("provenanceRefs") or [],
    })
    planned["createdAt"] = wf["createdAt"]
    planned["receipts"] = list(wf.get("receipts") or [])
    planned["reviews"] = list(wf.get("reviews") or [])
    planned["replanCount"] = int(wf.get("replanCount", 0)) + 1
    return {"workflow": planned}


def snapshot(workflow: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "capturedAt": _utcnow(),
        "workflow": deepcopy(workflow),
        "workflowDigest": _digest(workflow),
    }


def execute(operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise ValueError("unsupported operation")
    if operation == "workspace.agent.validate":
        planned = plan_workflow(payload)
        return {"schema": RESULT_SCHEMA, "version": VERSION, "operation": operation, "ok": True, "workflow": planned}
    if operation == "workspace.agent.plan":
        planned = plan_workflow(payload)
        return {"schema": RESULT_SCHEMA, "version": VERSION, "operation": operation, "ok": True, "workflow": planned}
    workflow = payload.get("workflow")
    if not isinstance(workflow, Mapping):
        raise ValueError("workflow is required")
    if operation == "workspace.agent.next-step":
        result = next_step(workflow)
    elif operation == "workspace.agent.record-result":
        result = record_result(workflow, payload)
    elif operation == "workspace.agent.review":
        result = review(workflow, payload)
    elif operation == "workspace.agent.replan":
        result = replan(workflow, payload)
    else:
        result = {"snapshot": snapshot(workflow)}
    return {"schema": RESULT_SCHEMA, "version": VERSION, "operation": operation, "ok": True, **result}
