from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Mapping

from .cross_product_research_handoff_consolidation import runtime_profile as handoff_profile
from .research_os_runtime_registry import runtime_profile as registry_profile
from .unified_research_session_runtime import runtime_profile as session_profile

VERSION = "3.69.0"
RUNTIME_SCHEMA = "sc-workspace-portable-research-workspace-recovery-package-runtime/1.0"
PACKAGE_SCHEMA = "sc-workspace-portable-research-workspace-package/1.0"
MANIFEST_SCHEMA = "sc-workspace-portable-research-workspace-manifest/1.0"
RESTORE_PLAN_SCHEMA = "sc-workspace-research-workspace-restore-plan/1.0"
MIGRATION_DRILL_SCHEMA = "sc-workspace-research-workspace-migration-drill/1.0"
VERIFICATION_SCHEMA = "sc-workspace-portable-package-verification/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-portable-recovery-snapshot/1.0"
COMPATIBILITY_SCHEMA = "sc-workspace-portable-research-workspace-compatibility/1.0"

OPERATIONS = (
    "workspace.portable-recovery.validate",
    "workspace.portable-recovery.manifest",
    "workspace.portable-recovery.package",
    "workspace.portable-recovery.verify",
    "workspace.portable-recovery.restore-plan",
    "workspace.portable-recovery.migration-drill",
    "workspace.portable-recovery.compatibility",
    "workspace.portable-recovery.snapshot",
)

BOUNDARIES = {
    "boundedOperationsOnly": True,
    "portablePackageIsDataOnly": True,
    "existingRecoverySnapshotAuthorityPreserved": True,
    "automaticRestoreEnabled": False,
    "automaticImportEnabled": False,
    "automaticProjectMutationEnabled": False,
    "automaticNotebookMutationEnabled": False,
    "automaticArtifactMutationEnabled": False,
    "automaticRuntimeExecutionEnabled": False,
    "automaticAgentExecutionEnabled": False,
    "automaticApprovalEnabled": False,
    "automaticGovernanceBypassEnabled": False,
    "automaticPublicationEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "automaticCredentialExportEnabled": False,
    "automaticSecretExportEnabled": False,
    "automaticTruthDeterminationEnabled": False,
    "automaticDecisionAuthorityEnabled": False,
    "humanReviewRequiredBeforeRestore": True,
    "provenancePreserved": True,
    "dissentPreserved": True,
    "integrityVerificationRequired": True,
    "fingerprintPinningRequired": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _list(payload: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    out = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"{key} entries must be objects")
        out.append(dict(item))
    return out


def _safe_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    metadata = dict(payload.get("metadata") or {})
    forbidden = {
        "password", "secret", "token", "apiKey", "api_key", "credential",
        "credentials", "privateKey", "private_key", "serviceToken",
    }
    for key in list(metadata):
        if key in forbidden:
            metadata.pop(key, None)
    return metadata


def validate(payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors = []
    project_ref = str(payload.get("projectRef") or "").strip()
    if payload and not project_ref:
        errors.append("projectRef is required")
    recovery = payload.get("recoverySnapshot")
    if recovery is not None and not isinstance(recovery, Mapping):
        errors.append("recoverySnapshot must be an object")
    return {
        "valid": not errors,
        "version": VERSION,
        "errors": errors,
        "evaluatedAt": _now(),
        "mutationPerformed": False,
        "restorePerformed": False,
        "authorityGranted": False,
    }


def manifest(payload: Mapping[str, Any]) -> Dict[str, Any]:
    v = validate(payload)
    if not v["valid"]:
        raise ValueError("; ".join(v["errors"]))
    projects = _list(payload, "projects")
    notebooks = _list(payload, "notebooks")
    artifacts = _list(payload, "artifacts")
    datasets = _list(payload, "datasets")
    models = _list(payload, "models")
    executions = _list(payload, "executions")
    handoffs = _list(payload, "handoffs")
    package = {
        "schema": MANIFEST_SCHEMA,
        "version": VERSION,
        "projectRef": str(payload["projectRef"]),
        "researchSessionRef": payload.get("researchSessionRef"),
        "sourceWorkspaceVersion": str(payload.get("sourceWorkspaceVersion") or VERSION),
        "projects": projects,
        "notebooks": notebooks,
        "artifacts": artifacts,
        "datasets": datasets,
        "models": models,
        "executions": executions,
        "handoffs": handoffs,
        "metadata": _safe_metadata(payload),
        "counts": {
            "projects": len(projects),
            "notebooks": len(notebooks),
            "artifacts": len(artifacts),
            "datasets": len(datasets),
            "models": len(models),
            "executions": len(executions),
            "handoffs": len(handoffs),
        },
        "lineage": {
            "runtimeRegistrySchema": registry_profile().get("schema"),
            "runtimeRegistryVersion": registry_profile().get("version"),
            "unifiedResearchSessionSchema": session_profile().get("schema"),
            "unifiedResearchSessionVersion": session_profile().get("version"),
            "handoffConsolidationSchema": handoff_profile().get("schema"),
            "handoffConsolidationVersion": handoff_profile().get("version"),
            "recoveryManifestSchema": "sc-workspace-recovery-manifest/1.0",
        },
        "excludedClasses": [
            "credentials",
            "service-tokens",
            "private-keys",
            "runtime-secrets",
            "database-passwords",
        ],
        "portable": True,
        "readOnly": True,
        "restoreRequiresExplicitPlan": True,
    }
    if isinstance(payload.get("recoverySnapshot"), Mapping):
        rs = dict(payload["recoverySnapshot"])
        package["recoverySnapshot"] = {
            "snapshotId": rs.get("snapshotId"),
            "fingerprint": rs.get("fingerprint"),
            "projectCount": rs.get("projectCount"),
            "notebookCount": rs.get("notebookCount"),
            "artifactCount": rs.get("artifactCount"),
            "createdAt": rs.get("createdAt"),
        }
    package["manifestDigest"] = _digest(package)
    return package


def build_package(payload: Mapping[str, Any]) -> Dict[str, Any]:
    m = manifest(payload)
    body = {
        "schema": PACKAGE_SCHEMA,
        "version": VERSION,
        "manifest": m,
        "packageFormat": "json",
        "contentAddressed": True,
        "portableAcrossHosts": True,
        "wordpressIndependent": True,
        "standaloneCompatible": True,
        "requiresIntegrityVerificationBeforeRestore": True,
        "requiresHumanReviewBeforeRestore": True,
        "automaticRestoreEnabled": False,
        "automaticImportEnabled": False,
    }
    body["packageDigest"] = _digest(body)
    return body


def verify(payload: Mapping[str, Any]) -> Dict[str, Any]:
    package = payload.get("package")
    if not isinstance(package, Mapping):
        raise ValueError("package is required")
    p = dict(package)
    supplied = str(p.get("packageDigest") or "")
    p_without = dict(p)
    p_without.pop("packageDigest", None)
    expected = _digest(p_without)
    manifest_obj = p.get("manifest")
    manifest_ok = False
    manifest_expected = None
    manifest_supplied = None
    if isinstance(manifest_obj, Mapping):
        m = dict(manifest_obj)
        manifest_supplied = str(m.get("manifestDigest") or "")
        m.pop("manifestDigest", None)
        manifest_expected = _digest(m)
        manifest_ok = manifest_supplied == manifest_expected
    return {
        "schema": VERIFICATION_SCHEMA,
        "version": VERSION,
        "packageDigestSupplied": supplied,
        "packageDigestExpected": expected,
        "packageDigestValid": supplied == expected,
        "manifestDigestSupplied": manifest_supplied,
        "manifestDigestExpected": manifest_expected,
        "manifestDigestValid": manifest_ok,
        "valid": supplied == expected and manifest_ok,
        "mutationPerformed": False,
        "restorePerformed": False,
    }


def restore_plan(payload: Mapping[str, Any]) -> Dict[str, Any]:
    package = payload.get("package")
    if not isinstance(package, Mapping):
        raise ValueError("package is required")
    verification = verify({"package": package})
    if not verification["valid"]:
        raise ValueError("portable package integrity verification failed")
    manifest_obj = dict(package["manifest"])
    plan = {
        "schema": RESTORE_PLAN_SCHEMA,
        "version": VERSION,
        "projectRef": manifest_obj.get("projectRef"),
        "sourceWorkspaceVersion": manifest_obj.get("sourceWorkspaceVersion"),
        "targetWorkspaceVersion": str(payload.get("targetWorkspaceVersion") or VERSION),
        "packageDigest": package.get("packageDigest"),
        "steps": [
            {"order": 1, "action": "verify-package-integrity", "automatic": False},
            {"order": 2, "action": "inspect-conflicts-and-identities", "automatic": False},
            {"order": 3, "action": "review-project-and-session-lineage", "automatic": False},
            {"order": 4, "action": "review-object-and-artifact-bindings", "automatic": False},
            {"order": 5, "action": "review-cross-product-handoffs", "automatic": False},
            {"order": 6, "action": "human-approve-restore", "automatic": False},
            {"order": 7, "action": "execute-restore-with-backend-authority", "automatic": False},
            {"order": 8, "action": "post-restore-integrity-verification", "automatic": False},
        ],
        "conflictPolicy": str(payload.get("conflictPolicy") or "preserve-existing"),
        "restorePerformed": False,
        "mutationPerformed": False,
        "humanApprovalRequired": True,
        "backendAuthorityRequired": True,
    }
    plan["planDigest"] = _digest(plan)
    return plan


def migration_drill(payload: Mapping[str, Any]) -> Dict[str, Any]:
    package = payload.get("package")
    if not isinstance(package, Mapping):
        raise ValueError("package is required")
    verification = verify({"package": package})
    source = str(package.get("manifest", {}).get("sourceWorkspaceVersion") or "")
    target = str(payload.get("targetWorkspaceVersion") or VERSION)
    checks = {
        "packageIntegrityValid": verification["valid"],
        "sourceVersionPresent": bool(source),
        "targetVersionPresent": bool(target),
        "manifestPresent": isinstance(package.get("manifest"), Mapping),
        "credentialsExcluded": "credentials" in package.get("manifest", {}).get("excludedClasses", []),
        "automaticRestoreDisabled": package.get("automaticRestoreEnabled") is False,
        "humanReviewRequired": package.get("requiresHumanReviewBeforeRestore") is True,
    }
    return {
        "schema": MIGRATION_DRILL_SCHEMA,
        "version": VERSION,
        "sourceWorkspaceVersion": source,
        "targetWorkspaceVersion": target,
        "checks": checks,
        "readyForControlledRestore": all(checks.values()),
        "drillOnly": True,
        "restorePerformed": False,
        "mutationPerformed": False,
        "externalSideEffectsPerformed": False,
        "evaluatedAt": _now(),
    }


def compatibility(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    handoff = handoff_profile()
    registry = registry_profile()
    session = session_profile()
    checks = {
        "handoffConsolidationValid": bool(handoff.get("consolidationValid")),
        "runtimeRegistryValid": bool(registry.get("registryValid")),
        "unifiedResearchSessionAvailable": session.get("version") == "3.66.0",
        "recoveryManifestSchemaKnown": True,
        "portablePackageIntegritySupported": True,
        "wordpressIndependentPackageSupported": True,
        "standaloneCompatiblePackageSupported": True,
    }
    return {
        "schema": COMPATIBILITY_SCHEMA,
        "version": VERSION,
        "compatibleFrom": "3.68.0",
        "currentRelease": VERSION,
        "previousRelease": "3.68.0",
        "rollbackTarget": "3.68.0",
        "databaseMigrationRequired": False,
        "projectSchemaMigrationRequired": False,
        "checks": checks,
        "compatible": all(checks.values()),
    }


def snapshot(payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    body = {
        "runtime": runtime_profile(),
        "compatibility": compatibility(),
        "capturedAt": _now(),
    }
    if payload:
        body["package"] = build_package(payload)
    return {
        "schema": SNAPSHOT_SCHEMA,
        "version": VERSION,
        "snapshot": body,
        "snapshotDigest": _digest(body),
        "readOnly": True,
        "portable": True,
        "automaticReplayEnabled": False,
        "automaticRestoreEnabled": False,
        "mutationPerformed": False,
    }


def runtime_profile() -> Dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": VERSION,
        "title": "Portable Research Workspace & Recovery Packages",
        "recoveryManifestSchema": "sc-workspace-recovery-manifest/1.0",
        "portablePackageSchema": PACKAGE_SCHEMA,
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "capabilities": {
            "portableWorkspaceManifests": True,
            "portableResearchPackages": True,
            "contentAddressedIntegrity": True,
            "packageVerification": True,
            "restorePlanning": True,
            "migrationDrills": True,
            "recoverySnapshotLineage": True,
            "wordpressIndependentPackages": True,
            "standaloneCompatiblePackages": True,
            "explicitSecretExclusion": True,
        },
        **BOUNDARIES,
    }


def operation_index() -> Dict[str, Any]:
    return {
        "schema": "sc-workspace-portable-research-workspace-recovery-operation-index/1.0",
        "version": VERSION,
        "items": [
            {
                "operation": op,
                "bounded": True,
                "dataOnly": True,
                "mutationAuthority": False,
                "restoreAuthority": False,
                "executionAuthority": False,
                "approvalAuthority": False,
                "publicationAuthority": False,
                "externalSideEffectAuthority": False,
            }
            for op in OPERATIONS
        ],
        **BOUNDARIES,
    }


def execute(operation: str, payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    handlers = {
        "workspace.portable-recovery.validate": validate,
        "workspace.portable-recovery.manifest": manifest,
        "workspace.portable-recovery.package": build_package,
        "workspace.portable-recovery.verify": verify,
        "workspace.portable-recovery.restore-plan": restore_plan,
        "workspace.portable-recovery.migration-drill": migration_drill,
        "workspace.portable-recovery.compatibility": compatibility,
        "workspace.portable-recovery.snapshot": snapshot,
    }
    if operation not in handlers:
        raise ValueError("unsupported operation")
    return {
        "schema": "sc-workspace-portable-research-workspace-recovery-result/1.0",
        "version": VERSION,
        "operation": operation,
        "result": handlers[operation](payload or {}),
    }
