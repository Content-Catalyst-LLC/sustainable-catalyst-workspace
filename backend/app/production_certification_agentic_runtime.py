from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping
from uuid import uuid4

from .agentic_research_workflow_runtime import runtime_profile as v360_profile, operation_index as v360_operations
from .human_governance_approval_intervention_runtime import runtime_profile as v361_profile, operation_index as v361_operations
from .multi_agent_orchestration_specialist_coordination_runtime import runtime_profile as v362_profile, operation_index as v362_operations
from .reproducible_agentic_research_package_runtime import runtime_profile as v363_profile, operation_index as v363_operations
from .integrated_research_os_runtime import runtime_profile as v364_profile, operation_index as v364_operations

VERSION = "3.65.0"
RUNTIME_SCHEMA = "sc-workspace-production-certification-agentic-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-production-certification-request/1.0"
RESULT_SCHEMA = "sc-workspace-production-certification-result/1.0"
REPORT_SCHEMA = "sc-workspace-production-certification-report/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-production-certification-snapshot/1.0"

CHAIN = (
    ("v3.60", "3.60.0", "sc-workspace-agentic-research-workflow-runtime/1.0", v360_profile, v360_operations),
    ("v3.61", "3.61.0", "sc-workspace-human-governance-approval-intervention-runtime/1.0", v361_profile, v361_operations),
    ("v3.62", "3.62.0", "sc-workspace-multi-agent-orchestration-specialist-coordination-runtime/1.0", v362_profile, v362_operations),
    ("v3.63", "3.63.0", "sc-workspace-reproducible-agentic-research-package-runtime/1.0", v363_profile, v363_operations),
    ("v3.64", "3.64.0", "sc-workspace-integrated-research-os-runtime/1.0", v364_profile, v364_operations),
)

EXPECTED_ROUTES = (
    "/v1/agentic-research-workflow-runtime",
    "/v1/agentic-research-workflow-runtime/operations",
    "/v1/human-governance-approval-intervention-runtime",
    "/v1/human-governance-approval-intervention-runtime/operations",
    "/v1/multi-agent-orchestration-specialist-coordination-runtime",
    "/v1/multi-agent-orchestration-specialist-coordination-runtime/operations",
    "/v1/reproducible-agentic-research-package-runtime",
    "/v1/reproducible-agentic-research-package-runtime/operations",
    "/v1/integrated-research-os-runtime",
    "/v1/integrated-research-os-runtime/operations",
    "/v1/production-certification-agentic-runtime",
    "/v1/production-certification-agentic-runtime/operations",
    "/v1/production-certification-agentic-runtime/report",
)

EXPECTED_HOST_ASSETS = (
    "sc-workspace-agentic-research-workflow-v3600.js",
    "sc-workspace-human-governance-approval-intervention-v3610.js",
    "sc-workspace-multi-agent-orchestration-specialist-coordination-v3620.js",
    "sc-workspace-reproducible-agentic-research-package-v3630.js",
    "sc-workspace-integrated-research-os-v3640.js",
    "sc-workspace-production-certification-agentic-v3650.js",
)

OPERATIONS = (
    "workspace.production-certification.validate",
    "workspace.production-certification.certify-runtime-chain",
    "workspace.production-certification.route-inventory",
    "workspace.production-certification.compatibility",
    "workspace.production-certification.host-parity",
    "workspace.production-certification.recovery-readiness",
    "workspace.production-certification.package-integrity",
    "workspace.production-certification.snapshot",
)

AUTHORITY_FALSE_KEYS = (
    "arbitraryCodeExecution",
    "automaticApprovalEnabled",
    "automaticGovernanceBypassEnabled",
    "automaticExternalSideEffectsEnabled",
    "automaticTruthDeterminationEnabled",
    "automaticEvidenceRankingEnabled",
)

BOUNDARIES = {
    "boundedOperationsOnly": True,
    "certificationIsDescriptiveOnly": True,
    "arbitraryCodeExecution": False,
    "automaticExecutionEnabled": False,
    "automaticApprovalEnabled": False,
    "automaticGovernanceBypassEnabled": False,
    "automaticPublicationEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "automaticTruthDeterminationEnabled": False,
    "automaticEvidenceRankingEnabled": False,
    "automaticDecisionAuthorityEnabled": False,
    "runtimeMutationEnabled": False,
    "sourceObjectMutationEnabled": False,
    "humanGovernancePreserved": True,
    "provenancePreserved": True,
    "dissentPreserved": True,
    "rollbackTarget": "3.64.0",
}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _profile_operation_count(profile: Mapping[str, Any], index: Mapping[str, Any]) -> int:
    explicit = profile.get("boundedOperationCount")
    if isinstance(explicit, int):
        return explicit
    for key in ("items", "operations", "boundedOperations"):
        value = index.get(key) if isinstance(index, Mapping) else None
        if isinstance(value, list):
            return len(value)
    bounded = profile.get("boundedOperations")
    return len(bounded) if isinstance(bounded, list) else 0

def certify_runtime_chain() -> Dict[str, Any]:
    items = []
    errors = []
    for label, expected_version, expected_schema, profile_fn, operations_fn in CHAIN:
        try:
            profile = profile_fn()
            operation_index = operations_fn()
        except Exception as exc:
            errors.append(f"{label}: profile load failed: {exc}")
            items.append({"release": label, "certified": False, "error": str(exc)})
            continue

        checks = {
            "version": profile.get("version") == expected_version,
            "schema": profile.get("schema") == expected_schema,
            "operationIndexVersion": operation_index.get("version") == expected_version,
            "boundedOperationCountPositive": _profile_operation_count(profile, operation_index) > 0,
        }
        authority_checks = {}
        for key in AUTHORITY_FALSE_KEYS:
            if key in profile:
                authority_checks[key] = profile.get(key) is False
        certified = all(checks.values()) and all(authority_checks.values())
        if not certified:
            errors.append(f"{label}: runtime contract mismatch")
        items.append({
            "release": label,
            "version": profile.get("version"),
            "schema": profile.get("schema"),
            "boundedOperationCount": _profile_operation_count(profile, operation_index),
            "checks": checks,
            "authorityChecks": authority_checks,
            "certified": certified,
        })

    return {
        "schema": "sc-workspace-agentic-runtime-chain-certification/1.0",
        "version": VERSION,
        "certified": not errors and len(items) == len(CHAIN),
        "runtimeCount": len(items),
        "expectedRuntimeCount": len(CHAIN),
        "items": items,
        "errors": errors,
        "certifiedAt": _now(),
        "mutationPerformed": False,
        "authorityGranted": False,
    }

def route_inventory() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-production-route-inventory/1.0",
        "version": VERSION,
        "expectedRoutes": list(EXPECTED_ROUTES),
        "expectedRouteCount": len(EXPECTED_ROUTES),
        "profileRouteCount": 6,
        "operationIndexRouteCount": 6,
        "certificationReportRouteCount": 1,
        "descriptiveOnly": True,
    }

def compatibility_report() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-agentic-runtime-compatibility/1.0",
        "version": VERSION,
        "compatibleFrom": "3.60.0",
        "certifiedThrough": "3.64.0",
        "currentCertificationRelease": VERSION,
        "databaseMigrationRequired": False,
        "projectSchemaMigrationRequired": False,
        "rollbackTarget": "3.64.0",
        "runtimeChain": [x[1] for x in CHAIN],
        "humanGovernanceRequiredForSensitiveActions": True,
        "stageAuthorityPreserved": True,
        "packageVerificationDescriptiveOnly": True,
        "compatible": certify_runtime_chain()["certified"],
    }

def host_parity(payload: Mapping[str, Any]) -> Dict[str, Any]:
    wordpress_assets = set(payload.get("wordpressAssets") or [])
    standalone_assets = set(payload.get("standaloneAssets") or [])
    expected = set(EXPECTED_HOST_ASSETS)
    supplied = bool(wordpress_assets or standalone_assets)

    if supplied:
        wp_missing = sorted(expected - wordpress_assets)
        standalone_missing = sorted(expected - standalone_assets)
        parity = not wp_missing and not standalone_missing
    else:
        wp_missing = []
        standalone_missing = []
        parity = None

    return {
        "schema": "sc-workspace-host-parity-certification/1.0",
        "version": VERSION,
        "expectedAssets": sorted(expected),
        "expectedAssetCount": len(expected),
        "evidenceSupplied": supplied,
        "wordpressMissing": wp_missing,
        "standaloneMissing": standalone_missing,
        "parity": parity,
        "certificationDeferredWithoutEvidence": not supplied,
        "mutationPerformed": False,
    }

def recovery_readiness() -> Dict[str, Any]:
    chain = certify_runtime_chain()
    return {
        "schema": "sc-workspace-agentic-recovery-readiness/1.0",
        "version": VERSION,
        "ready": chain["certified"],
        "rollbackTarget": "3.64.0",
        "statelessCertificationRuntime": True,
        "restartSafe": True,
        "databaseMigrationRequired": False,
        "projectMigrationRequired": False,
        "automaticRollbackEnabled": False,
        "automaticReplayEnabled": False,
        "automaticRecoveryMutationEnabled": False,
        "runtimeChainCertified": chain["certified"],
        "evaluatedAt": _now(),
    }

def package_integrity(payload: Mapping[str, Any]) -> Dict[str, Any]:
    manifest = payload.get("manifest")
    if not isinstance(manifest, Mapping):
        return {
            "schema": "sc-workspace-production-package-integrity/1.0",
            "version": VERSION,
            "verified": False,
            "errors": ["manifest is required"],
            "descriptiveOnly": True,
        }

    errors = []
    if str(manifest.get("version") or "") != VERSION:
        errors.append("manifest version mismatch")
    if str(manifest.get("runtimeSchema") or "") != RUNTIME_SCHEMA:
        errors.append("manifest runtime schema mismatch")
    expected = list(manifest.get("certifiedRuntimeVersions") or [])
    if expected != [x[1] for x in CHAIN]:
        errors.append("certified runtime version chain mismatch")
    return {
        "schema": "sc-workspace-production-package-integrity/1.0",
        "version": VERSION,
        "verified": not errors,
        "errors": errors,
        "manifestDigest": _digest(manifest),
        "descriptiveOnly": True,
        "mutationPerformed": False,
    }

def certification_report() -> Dict[str, Any]:
    chain = certify_runtime_chain()
    compatibility = compatibility_report()
    recovery = recovery_readiness()
    report = {
        "schema": REPORT_SCHEMA,
        "version": VERSION,
        "title": "Workspace v3.65 Production Certification & Agentic Runtime Consolidation",
        "certified": bool(chain["certified"] and compatibility["compatible"] and recovery["ready"]),
        "runtimeChain": chain,
        "compatibility": compatibility,
        "routeInventory": route_inventory(),
        "recovery": recovery,
        "hostParityRequiresDeploymentEvidence": True,
        "wordpressStandaloneParityExpected": True,
        "databaseMigrationRequired": False,
        "projectMigrationRequired": False,
        "certificationGeneratedAt": _now(),
        **BOUNDARIES,
    }
    report["reportDigest"] = _digest(report)
    return report

def validate(payload: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    report = payload.get("report")
    if report is not None:
        if not isinstance(report, Mapping) or report.get("schema") != REPORT_SCHEMA:
            errors.append("invalid certification report schema")
        elif report.get("version") != VERSION:
            errors.append("invalid certification report version")
    return {"valid": not errors, "errors": errors}

def snapshot(payload: Mapping[str, Any]) -> Dict[str, Any]:
    report = payload.get("report") if isinstance(payload.get("report"), Mapping) else certification_report()
    captured = _now()
    body = {"report": deepcopy(report), "capturedAt": captured, "version": VERSION}
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "capturedAt": captured,
        "report": deepcopy(report),
        "snapshotDigest": _digest(body),
        "authorityGranted": False,
        "mutationPerformed": False,
    }

def runtime_profile() -> Dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Production Certification & Agentic Runtime Consolidation",
        "certifiedRuntimeVersions": [x[1] for x in CHAIN],
        "certifiedRuntimeSchemas": [x[2] for x in CHAIN],
        "certifiedRuntimeCount": len(CHAIN),
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "expectedRouteCount": len(EXPECTED_ROUTES),
        "expectedHostAssetCount": len(EXPECTED_HOST_ASSETS),
        "databaseMigrationRequired": False,
        "projectMigrationRequired": False,
        **BOUNDARIES,
    }

def operation_index() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-production-certification-agentic-operation-index/1.0",
        "version": VERSION,
        "items": [{
            "operation": op,
            "input": REQUEST_SCHEMA,
            "output": RESULT_SCHEMA,
            "bounded": True,
            "executionAuthority": False,
            "approvalAuthority": False,
            "publicationAuthority": False,
            "mutationAuthority": False,
        } for op in OPERATIONS],
        **BOUNDARIES,
    }

def execute(operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    handlers = {
        "workspace.production-certification.validate": validate,
        "workspace.production-certification.certify-runtime-chain": lambda p: certify_runtime_chain(),
        "workspace.production-certification.route-inventory": lambda p: route_inventory(),
        "workspace.production-certification.compatibility": lambda p: compatibility_report(),
        "workspace.production-certification.host-parity": host_parity,
        "workspace.production-certification.recovery-readiness": lambda p: recovery_readiness(),
        "workspace.production-certification.package-integrity": package_integrity,
        "workspace.production-certification.snapshot": snapshot,
    }
    if operation not in handlers:
        raise ValueError("unsupported operation")
    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "operation": operation,
        "result": handlers[operation](payload or {}),
    }
