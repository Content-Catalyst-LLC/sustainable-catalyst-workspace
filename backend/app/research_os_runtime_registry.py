from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping

from .agentic_research_workflow_runtime import runtime_profile as v360_profile, operation_index as v360_operations
from .human_governance_approval_intervention_runtime import runtime_profile as v361_profile, operation_index as v361_operations
from .multi_agent_orchestration_specialist_coordination_runtime import runtime_profile as v362_profile, operation_index as v362_operations
from .reproducible_agentic_research_package_runtime import runtime_profile as v363_profile, operation_index as v363_operations
from .integrated_research_os_runtime import runtime_profile as v364_profile, operation_index as v364_operations
from .production_certification_agentic_runtime import runtime_profile as v365_profile, operation_index as v365_operations
from .unified_research_session_runtime import runtime_profile as v366_profile, operation_index as v366_operations

VERSION = "3.67.0"
RUNTIME_SCHEMA = "sc-workspace-research-os-runtime-registry/1.0"
REQUEST_SCHEMA = "sc-workspace-research-os-runtime-registry-request/1.0"
RESULT_SCHEMA = "sc-workspace-research-os-runtime-registry-result/1.0"
DESCRIPTOR_SCHEMA = "sc-workspace-research-os-runtime-descriptor/1.0"
CAPABILITY_SCHEMA = "sc-workspace-research-os-capability-discovery/1.0"
OPERATION_SCHEMA = "sc-workspace-research-os-operation-discovery/1.0"
AUTHORITY_SCHEMA = "sc-workspace-research-os-authority-matrix/1.0"
COMPATIBILITY_SCHEMA = "sc-workspace-research-os-registry-compatibility/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-research-os-runtime-registry-snapshot/1.0"

RUNTIMES = (
    ("v3.60", "agentic-research-workflow", "3.60.0", v360_profile, v360_operations),
    ("v3.61", "human-governance-approval-intervention", "3.61.0", v361_profile, v361_operations),
    ("v3.62", "multi-agent-orchestration-specialist-coordination", "3.62.0", v362_profile, v362_operations),
    ("v3.63", "reproducible-agentic-research-package", "3.63.0", v363_profile, v363_operations),
    ("v3.64", "integrated-research-os", "3.64.0", v364_profile, v364_operations),
    ("v3.65", "production-certification-agentic", "3.65.0", v365_profile, v365_operations),
    ("v3.66", "unified-research-session", "3.66.0", v366_profile, v366_operations),
)

OPERATIONS = (
    "workspace.runtime-registry.validate",
    "workspace.runtime-registry.list",
    "workspace.runtime-registry.get-runtime",
    "workspace.runtime-registry.discover-capabilities",
    "workspace.runtime-registry.discover-operations",
    "workspace.runtime-registry.authority-matrix",
    "workspace.runtime-registry.compatibility",
    "workspace.runtime-registry.snapshot",
)

BOUNDARIES = {
    "boundedOperationsOnly": True,
    "registryIsDescriptiveOnly": True,
    "runtimeInvocationEnabled": False,
    "runtimeMutationEnabled": False,
    "sourceObjectMutationEnabled": False,
    "automaticExecutionEnabled": False,
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
    "automaticCapabilityActivationEnabled": False,
    "automaticOperationDispatchEnabled": False,
    "humanGovernancePreserved": True,
    "provenancePreserved": True,
    "dissentPreserved": True,
    "upstreamRuntimeAuthorityPreserved": True,
}

AUTHORITY_KEYS = (
    "arbitraryCodeExecution",
    "automaticExecutionEnabled",
    "automaticModelExecutionEnabled",
    "automaticAgentExecutionEnabled",
    "automaticApprovalEnabled",
    "automaticGovernanceBypassEnabled",
    "automaticPublicationEnabled",
    "automaticExternalSideEffectsEnabled",
    "automaticTruthDeterminationEnabled",
    "automaticEvidenceRankingEnabled",
    "automaticNarrativeSelectionEnabled",
    "automaticDecisionAuthorityEnabled",
    "runtimeMutationEnabled",
    "sourceObjectMutationEnabled",
)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _copy(value: Any) -> Any:
    return deepcopy(value)

def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _items(index: Mapping[str, Any]) -> list[dict[str, Any]]:
    for key in ("items", "operations", "boundedOperations"):
        value = index.get(key)
        if isinstance(value, list):
            out = []
            for item in value:
                out.append(_copy(item) if isinstance(item, dict) else {"operation": str(item)})
            return out
    return []

def _capabilities(profile: Mapping[str, Any]) -> dict[str, Any]:
    value = profile.get("capabilities")
    if isinstance(value, dict):
        return _copy(value)
    ignored = {
        "schema", "version", "title", "release", "boundedOperations", "boundedOperationCount",
        "upstreamSchemas", "researchStages", "researchStageCount", "sessionStatuses",
    }
    return {
        key: val for key, val in profile.items()
        if key not in ignored and key not in BOUNDARIES and key not in AUTHORITY_KEYS and isinstance(val, bool)
    }

def _authority(profile: Mapping[str, Any]) -> dict[str, bool]:
    return {key: bool(profile.get(key)) for key in AUTHORITY_KEYS if key in profile}

def _descriptor(entry) -> dict[str, Any]:
    release, runtime_id, expected_version, profile_fn, operations_fn = entry
    profile = profile_fn()
    index = operations_fn()
    items = _items(index)
    descriptor = {
        "schema": DESCRIPTOR_SCHEMA,
        "registryVersion": VERSION,
        "release": release,
        "runtimeId": runtime_id,
        "version": str(profile.get("version") or ""),
        "expectedVersion": expected_version,
        "runtimeSchema": str(profile.get("schema") or ""),
        "available": True,
        "versionMatches": str(profile.get("version") or "") == expected_version,
        "operationIndexVersion": str(index.get("version") or ""),
        "operationCount": len(items),
        "operations": [str(x.get("operation") or "") for x in items if x.get("operation")],
        "capabilities": _capabilities(profile),
        "authority": _authority(profile),
        "boundedOperationsOnly": bool(profile.get("boundedOperationsOnly", True)),
        "humanGovernancePreserved": bool(profile.get("humanGovernancePreserved", True)),
        "provenancePreserved": bool(profile.get("provenancePreserved", True)),
        "dissentPreserved": bool(profile.get("dissentPreserved", True)),
    }
    descriptor["descriptorDigest"] = _digest(descriptor)
    return descriptor

def descriptors() -> list[dict[str, Any]]:
    return [_descriptor(entry) for entry in RUNTIMES]

def validate(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    items = descriptors()
    errors = []
    ids, schemas = set(), set()
    for item in items:
        if item["runtimeId"] in ids: errors.append(f"duplicate runtimeId: {item['runtimeId']}")
        ids.add(item["runtimeId"])
        if item["runtimeSchema"] in schemas: errors.append(f"duplicate runtime schema: {item['runtimeSchema']}")
        schemas.add(item["runtimeSchema"])
        if not item["runtimeSchema"]: errors.append(f"missing runtime schema: {item['runtimeId']}")
        if not item["versionMatches"]: errors.append(f"version mismatch: {item['runtimeId']}")
        if item["operationCount"] <= 0: errors.append(f"no operations exposed: {item['runtimeId']}")
    return {
        "valid": not errors, "registryVersion": VERSION, "runtimeCount": len(items),
        "expectedRuntimeCount": len(RUNTIMES), "errors": errors, "evaluatedAt": _now(),
        "mutationPerformed": False, "authorityGranted": False,
    }

def list_runtimes(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    items = descriptors()
    return {"schema": RUNTIME_SCHEMA, "version": VERSION, "runtimeCount": len(items),
            "items": items, "generatedAt": _now(), **BOUNDARIES}

def get_runtime(payload: Mapping[str, Any]) -> dict[str, Any]:
    runtime_id = str(payload.get("runtimeId") or "").strip()
    version = str(payload.get("version") or "").strip()
    schema = str(payload.get("runtimeSchema") or "").strip()
    if not any((runtime_id, version, schema)):
        raise ValueError("runtimeId, version, or runtimeSchema is required")
    matches = [item for item in descriptors()
               if (not runtime_id or item["runtimeId"] == runtime_id)
               and (not version or item["version"] == version)
               and (not schema or item["runtimeSchema"] == schema)]
    if not matches: raise ValueError("runtime not found")
    if len(matches) > 1: raise ValueError("runtime query is ambiguous")
    return matches[0]

def discover_capabilities(payload: Mapping[str, Any]) -> dict[str, Any]:
    capability = str(payload.get("capability") or "").strip()
    enabled_only = bool(payload.get("enabledOnly", False))
    matches = []
    for item in descriptors():
        for name, enabled in item["capabilities"].items():
            if capability and capability.lower() not in name.lower(): continue
            if enabled_only and enabled is not True: continue
            matches.append({"runtimeId": item["runtimeId"], "version": item["version"],
                            "runtimeSchema": item["runtimeSchema"], "capability": name, "enabled": enabled})
    return {"schema": CAPABILITY_SCHEMA, "version": VERSION, "query": capability,
            "enabledOnly": enabled_only, "matchCount": len(matches), "items": matches,
            "descriptiveOnly": True, "activationPerformed": False}

def discover_operations(payload: Mapping[str, Any]) -> dict[str, Any]:
    operation = str(payload.get("operation") or "").strip()
    runtime_id = str(payload.get("runtimeId") or "").strip()
    matches = []
    for item in descriptors():
        if runtime_id and item["runtimeId"] != runtime_id: continue
        for name in item["operations"]:
            if operation and operation.lower() not in name.lower(): continue
            matches.append({"runtimeId": item["runtimeId"], "version": item["version"],
                            "runtimeSchema": item["runtimeSchema"], "operation": name,
                            "invocationAuthority": False})
    return {"schema": OPERATION_SCHEMA, "version": VERSION, "query": operation,
            "runtimeId": runtime_id, "matchCount": len(matches), "items": matches,
            "descriptiveOnly": True, "dispatchPerformed": False}

def authority_matrix(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    items = [{"runtimeId": item["runtimeId"], "version": item["version"],
              "runtimeSchema": item["runtimeSchema"], "authority": item["authority"],
              "registryMayOverride": False} for item in descriptors()]
    return {
        "schema": AUTHORITY_SCHEMA, "version": VERSION, "runtimeCount": len(items), "items": items,
        "registryAuthority": {"invokeRuntime": False, "mutateRuntime": False, "activateCapability": False,
                              "dispatchOperation": False, "approveGovernance": False, "publish": False,
                              "externalSideEffects": False, "determineTruth": False, "rankEvidence": False,
                              "decide": False},
        **BOUNDARIES,
    }

def compatibility(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    items = descriptors()
    valid = validate()
    return {
        "schema": COMPATIBILITY_SCHEMA, "version": VERSION, "compatibleFrom": "3.60.0",
        "discoveredThrough": "3.66.0", "currentRegistryRelease": VERSION,
        "runtimeChain": [item["version"] for item in items], "runtimeCount": len(items),
        "databaseMigrationRequired": False, "projectSchemaMigrationRequired": False,
        "rollbackTarget": "3.66.0", "upstreamRuntimeAuthorityPreserved": True,
        "registryCanInvokeRuntimes": False, "compatible": bool(valid["valid"]),
    }

def snapshot(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    body = {"registry": list_runtimes(), "authority": authority_matrix(),
            "compatibility": compatibility(), "capturedAt": _now()}
    return {"schema": SNAPSHOT_SCHEMA, "version": VERSION, "capturedAt": body["capturedAt"],
            "runtimeCount": body["registry"]["runtimeCount"], "snapshot": body,
            "snapshotDigest": _digest(body), "readOnly": True, "portable": True,
            "authorityGranted": False, "mutationPerformed": False}

def runtime_profile() -> Dict[str, Any]:
    valid = validate()
    return {
        "schema": RUNTIME_SCHEMA, "version": VERSION,
        "title": "Research OS Runtime Registry & Capability Discovery",
        "registeredRuntimeCount": len(RUNTIMES), "registeredFrom": "3.60.0", "registeredThrough": "3.66.0",
        "boundedOperations": list(OPERATIONS), "boundedOperationCount": len(OPERATIONS),
        "registryValid": bool(valid["valid"]),
        "capabilities": {
            "runtimeEnumeration": True, "runtimeLookup": True, "capabilityDiscovery": True,
            "operationDiscovery": True, "authorityBoundaryDiscovery": True, "compatibilityDiscovery": True,
            "portableRegistrySnapshots": True, "normalizedRuntimeDescriptors": True,
            "schemaDiscovery": True, "versionDiscovery": True,
        },
        **BOUNDARIES,
    }

def operation_index() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-research-os-runtime-registry-operation-index/1.0", "version": VERSION,
        "items": [{"operation": op, "input": REQUEST_SCHEMA, "output": RESULT_SCHEMA, "bounded": True,
                   "descriptiveOnly": True, "executionAuthority": False, "approvalAuthority": False,
                   "publicationAuthority": False, "mutationAuthority": False,
                   "externalSideEffectAuthority": False} for op in OPERATIONS],
        **BOUNDARIES,
    }

def execute(operation: str, payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    handlers = {
        "workspace.runtime-registry.validate": validate,
        "workspace.runtime-registry.list": list_runtimes,
        "workspace.runtime-registry.get-runtime": get_runtime,
        "workspace.runtime-registry.discover-capabilities": discover_capabilities,
        "workspace.runtime-registry.discover-operations": discover_operations,
        "workspace.runtime-registry.authority-matrix": authority_matrix,
        "workspace.runtime-registry.compatibility": compatibility,
        "workspace.runtime-registry.snapshot": snapshot,
    }
    if operation not in handlers: raise ValueError("unsupported operation")
    return {"schema": RESULT_SCHEMA, "version": VERSION, "operation": operation,
            "result": handlers[operation](payload or {})}
