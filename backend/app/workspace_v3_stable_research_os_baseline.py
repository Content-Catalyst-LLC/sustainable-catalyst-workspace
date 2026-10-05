from __future__ import annotations
from datetime import datetime, timezone
import hashlib, json
from typing import Any, Dict, Mapping

from .production_certification_agentic_runtime import runtime_profile as production_certification_profile
from .unified_research_session_runtime import runtime_profile as session_profile
from .research_os_runtime_registry import runtime_profile as registry_profile
from .cross_product_research_handoff_consolidation import runtime_profile as handoff_profile
from .portable_research_workspace_recovery import runtime_profile as recovery_profile, compatibility as recovery_compatibility

VERSION = "3.70.0"
RUNTIME_SCHEMA = "sc-workspace-v3-production-consolidation-stable-research-os-baseline/1.0"
CERTIFICATION_SCHEMA = "sc-workspace-v3-stable-research-os-certification/1.0"
COMPATIBILITY_SCHEMA = "sc-workspace-v3-stable-baseline-compatibility/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-v3-stable-baseline-snapshot/1.0"

OPERATIONS = (
    "workspace.stable-baseline.validate",
    "workspace.stable-baseline.runtime-chain",
    "workspace.stable-baseline.capability-summary",
    "workspace.stable-baseline.authority-summary",
    "workspace.stable-baseline.portability-readiness",
    "workspace.stable-baseline.compatibility",
    "workspace.stable-baseline.certify",
    "workspace.stable-baseline.snapshot",
)

CHAIN = (
    ("3.60.0", "agentic-research-workflow"),
    ("3.61.0", "human-governance-approval-intervention"),
    ("3.62.0", "multi-agent-orchestration-specialist-coordination"),
    ("3.63.0", "reproducible-agentic-research-package"),
    ("3.64.0", "integrated-research-os"),
    ("3.65.0", "production-certification-agentic-runtime-consolidation"),
    ("3.66.0", "unified-research-session-lifecycle-persistence"),
    ("3.67.0", "research-os-runtime-registry-capability-discovery"),
    ("3.68.0", "cross-product-research-handoff-consolidation"),
    ("3.69.0", "portable-research-workspace-recovery-packages"),
)

BOUNDARIES = {
    "boundedOperationsOnly": True,
    "baselineIsCertificationOnly": True,
    "newCapabilityFamilyIntroduced": False,
    "runtimeMutationEnabled": False,
    "sourceObjectMutationEnabled": False,
    "automaticExecutionEnabled": False,
    "automaticModelExecutionEnabled": False,
    "automaticAgentExecutionEnabled": False,
    "automaticApprovalEnabled": False,
    "automaticGovernanceBypassEnabled": False,
    "automaticPublicationEnabled": False,
    "automaticRestoreEnabled": False,
    "automaticImportEnabled": False,
    "automaticExternalSideEffectsEnabled": False,
    "automaticTruthDeterminationEnabled": False,
    "automaticEvidenceRankingEnabled": False,
    "automaticNarrativeSelectionEnabled": False,
    "automaticDecisionAuthorityEnabled": False,
    "humanGovernancePreserved": True,
    "provenancePreserved": True,
    "dissentPreserved": True,
    "upstreamRuntimeAuthorityPreserved": True,
    "crossProductAuthorityPreserved": True,
    "recoveryAuthorityPreserved": True,
}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

def runtime_chain(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"schema":"sc-workspace-v3-stable-runtime-chain/1.0","version":VERSION,"from":"3.60.0","through":"3.69.0","stableBaseline":VERSION,"runtimeCount":len(CHAIN),"items":[{"version":v,"role":role} for v,role in CHAIN],"frozenForCertification":True,"mutationPerformed":False}

def capability_summary(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"schema":"sc-workspace-v3-stable-capability-summary/1.0","version":VERSION,"researchOS":True,"agenticWorkflow":True,"humanGovernance":True,"multiAgentCoordination":True,"reproducibleResearchPackages":True,"unifiedResearchSessions":True,"runtimeRegistry":True,"crossProductHandoffs":True,"portableRecoveryPackages":True,"standaloneMigrationReadiness":True,"wordpressHostCompatibility":True,"databaseMigrationRequired":False,"projectSchemaMigrationRequired":False}

def authority_summary(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"schema":"sc-workspace-v3-stable-authority-summary/1.0","version":VERSION,**BOUNDARIES}

def portability_readiness(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    r=recovery_profile(); c=recovery_compatibility(); caps=r.get("capabilities",{})
    checks={"portableWorkspaceManifests":bool(caps.get("portableWorkspaceManifests")),"portableResearchPackages":bool(caps.get("portableResearchPackages")),"contentAddressedIntegrity":bool(caps.get("contentAddressedIntegrity")),"restorePlanning":bool(caps.get("restorePlanning")),"migrationDrills":bool(caps.get("migrationDrills")),"wordpressIndependentPackages":bool(caps.get("wordpressIndependentPackages")),"standaloneCompatiblePackages":bool(caps.get("standaloneCompatiblePackages")),"recoveryCompatibility":bool(c.get("compatible"))}
    return {"schema":"sc-workspace-v3-portability-readiness/1.0","version":VERSION,"checks":checks,"ready":all(checks.values()),"automaticRestoreEnabled":False,"automaticImportEnabled":False}

def compatibility(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    registry=registry_profile(); session=session_profile(); handoff=handoff_profile(); recovery=recovery_compatibility(); prod=production_certification_profile()
    checks={"productionCertificationAvailable":prod.get("version")=="3.65.0","unifiedResearchSessionAvailable":session.get("version")=="3.66.0","runtimeRegistryValid":bool(registry.get("registryValid")),"crossProductHandoffConsolidationValid":bool(handoff.get("consolidationValid")),"portableRecoveryCompatible":bool(recovery.get("compatible")),"runtimeChainExpectedLength":len(CHAIN)==10,"runtimeChainExpectedStart":CHAIN[0][0]=="3.60.0","runtimeChainExpectedEnd":CHAIN[-1][0]=="3.69.0"}
    return {"schema":COMPATIBILITY_SCHEMA,"version":VERSION,"compatibleFrom":"3.60.0","certifiedThrough":"3.69.0","currentRelease":VERSION,"previousRelease":"3.69.0","rollbackTarget":"3.69.0","databaseMigrationRequired":False,"projectSchemaMigrationRequired":False,"checks":checks,"compatible":all(checks.values())}

def validate(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    c=compatibility(); p=portability_readiness(); errors=[k for k,v in c["checks"].items() if not v]
    if not p["ready"]: errors.append("portabilityReadiness")
    return {"valid":not errors,"version":VERSION,"errors":errors,"runtimeCount":len(CHAIN),"evaluatedAt":_now(),"mutationPerformed":False,"authorityGranted":False}

def certify(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    v=validate(); body={"schema":CERTIFICATION_SCHEMA,"version":VERSION,"title":"Workspace 3.x Production Consolidation & Stable Research OS Baseline","certified":bool(v["valid"]),"certifiedFrom":"3.60.0","certifiedThrough":"3.69.0","stableBaseline":VERSION,"runtimeCount":len(CHAIN),"compatibility":compatibility(),"portability":portability_readiness(),"authority":authority_summary(),"certifiedAt":_now(),"databaseMigrationRequired":False,"projectSchemaMigrationRequired":False,"rollbackTarget":"3.69.0"}; body["certificationDigest"]=_digest(body); return body

def snapshot(_: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    body={"runtime":runtime_profile(),"runtimeChain":runtime_chain(),"capabilities":capability_summary(),"authority":authority_summary(),"portability":portability_readiness(),"compatibility":compatibility(),"capturedAt":_now()}
    return {"schema":SNAPSHOT_SCHEMA,"version":VERSION,"snapshot":body,"snapshotDigest":_digest(body),"readOnly":True,"portable":True,"automaticReplayEnabled":False,"automaticMutationEnabled":False}

def runtime_profile() -> Dict[str, Any]:
    v=validate()
    return {"schema":RUNTIME_SCHEMA,"version":VERSION,"title":"Workspace 3.x Production Consolidation & Stable Research OS Baseline","releaseStage":"stable-research-os-baseline","stableMajorLine":"3.x","certifiedRuntimeFrom":"3.60.0","certifiedRuntimeThrough":"3.69.0","registeredRuntimeCount":len(CHAIN),"boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),"baselineValid":bool(v["valid"]),"capabilities":{"stableResearchOSBaseline":True,"runtimeChainCertification":True,"authorityBoundaryCertification":True,"crossProductContinuityCertification":True,"portableRecoveryCertification":True,"wordpressStandaloneParityBaseline":True,"rollbackReadiness":True,"productionPromotionReadiness":True},**BOUNDARIES}

def operation_index() -> Dict[str, Any]:
    return {"schema":"sc-workspace-v3-stable-baseline-operation-index/1.0","version":VERSION,"items":[{"operation":op,"bounded":True,"certificationOnly":True,"mutationAuthority":False,"executionAuthority":False,"approvalAuthority":False,"publicationAuthority":False,"restoreAuthority":False,"externalSideEffectAuthority":False} for op in OPERATIONS],**BOUNDARIES}

def execute(operation: str, payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    handlers={"workspace.stable-baseline.validate":validate,"workspace.stable-baseline.runtime-chain":runtime_chain,"workspace.stable-baseline.capability-summary":capability_summary,"workspace.stable-baseline.authority-summary":authority_summary,"workspace.stable-baseline.portability-readiness":portability_readiness,"workspace.stable-baseline.compatibility":compatibility,"workspace.stable-baseline.certify":certify,"workspace.stable-baseline.snapshot":snapshot}
    if operation not in handlers: raise ValueError("unsupported operation")
    return {"schema":"sc-workspace-v3-stable-baseline-result/1.0","version":VERSION,"operation":operation,"result":handlers[operation](payload or {})}
