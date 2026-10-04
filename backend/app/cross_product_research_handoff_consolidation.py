from __future__ import annotations
from datetime import datetime, timezone
import hashlib, json
from typing import Any, Mapping
from .cross_product_handoffs import PRODUCTS, INTENTS, HANDOFF_SCHEMA, profile as handoff_fabric_profile
from .research_os_runtime_registry import runtime_profile as registry_profile
from .unified_research_session_runtime import runtime_profile as session_profile

VERSION="3.68.0"
RUNTIME_SCHEMA="sc-workspace-cross-product-research-handoff-consolidation-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-cross-product-research-handoff-consolidation-request/1.0"
RESULT_SCHEMA="sc-workspace-cross-product-research-handoff-consolidation-result/1.0"
OPERATIONS=(
"workspace.handoff-consolidation.validate",
"workspace.handoff-consolidation.destination-profiles",
"workspace.handoff-consolidation.intent-compatibility",
"workspace.handoff-consolidation.plan",
"workspace.handoff-consolidation.manifest",
"workspace.handoff-consolidation.acceptance-contract",
"workspace.handoff-consolidation.compatibility",
"workspace.handoff-consolidation.snapshot",
)
DESTINATIONS={
"platform-core":["validate","continue-research"],
"knowledge-library":["cite","publish","continue-research","investigate"],
"research-librarian":["cite","continue-research","investigate","compare"],
"workbench":["analyze","simulate","visualize","compare","validate"],
"research-lab":["analyze","simulate","validate","compare","investigate","visualize"],
"decision-studio":["compare","decide","visualize","validate"],
"site-intelligence":["analyze","visualize","investigate","compare"],
"catalyst-data":["analyze","compare","validate","continue-research"],
"workspace":list(INTENTS),
}
BOUNDARIES={"boundedOperationsOnly":True,"consolidationIsDescriptiveOnly":True,"existingHandoffFabricRemainsAuthoritative":True,"backendPersistenceRemainsAuthoritative":True,"genericDestinationMutationEnabled":False,"automaticHandoffDispatchEnabled":False,"automaticDestinationExecutionEnabled":False,"automaticAcceptanceEnabled":False,"automaticApprovalEnabled":False,"automaticGovernanceBypassEnabled":False,"automaticPublicationEnabled":False,"automaticExternalSideEffectsEnabled":False,"automaticTruthDeterminationEnabled":False,"automaticEvidenceRankingEnabled":False,"automaticNarrativeSelectionEnabled":False,"automaticDecisionAuthorityEnabled":False,"sourceObjectMutationEnabled":False,"humanGovernancePreserved":True,"provenancePreserved":True,"dissentPreserved":True,"revisionPinningRequired":True,"fingerprintPinningRequired":True,"destinationAcceptanceReceiptRequired":True}
def _now(): return datetime.now(timezone.utc).isoformat()
def _digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def destination_profiles(_=None):
    items=[]
    for p,intents in DESTINATIONS.items():
        body={"schema":"sc-workspace-cross-product-destination-profile/1.0","version":VERSION,"product":p,"acceptedIntents":intents,"handoffFabricProductSupported":p in PRODUCTS,"requiresPinnedObjects":True,"acceptanceMustBeExplicit":True,"executionAuthorityGranted":False,"approvalAuthorityGranted":False,"publicationAuthorityGranted":False,"decisionAuthorityGranted":False}
        body["profileDigest"]=_digest(body); items.append(body)
    return {"schema":"sc-workspace-cross-product-destination-profile-index/1.0","version":VERSION,"destinationCount":len(items),"items":items,**BOUNDARIES}
def intent_compatibility(payload:Mapping[str,Any]):
    source=str(payload.get("sourceProduct") or "workspace"); dest=str(payload.get("destinationProduct") or ""); intent=str(payload.get("intent") or "")
    if source not in PRODUCTS: raise ValueError("unsupported source product")
    if dest not in DESTINATIONS: raise ValueError("unsupported destination product")
    if source==dest: raise ValueError("source and destination products must differ")
    if intent not in INTENTS: raise ValueError("unsupported handoff intent")
    return {"schema":"sc-workspace-cross-product-intent-compatibility/1.0","version":VERSION,"sourceProduct":source,"destinationProduct":dest,"intent":intent,"compatible":intent in DESTINATIONS[dest],"acceptedIntents":DESTINATIONS[dest],"dispatchPerformed":False,"destinationMutationPerformed":False,"authorityGranted":False}
def _refs(payload):
    refs=payload.get("objects") or []
    if not isinstance(refs,list) or not refs: raise ValueError("at least one pinned object reference is required")
    out=[]
    for ref in refs:
        if not isinstance(ref,dict): raise ValueError("object reference must be an object")
        if not ref.get("kind") or not ref.get("objectId"): raise ValueError("object kind and objectId are required")
        if ref.get("revision") is None: raise ValueError("object revision is required")
        if not ref.get("fingerprint"): raise ValueError("object fingerprint is required")
        out.append({"kind":ref["kind"],"objectId":ref["objectId"],"revision":ref["revision"],"fingerprint":ref["fingerprint"]})
    return out
def plan(payload):
    c=intent_compatibility(payload)
    if not c["compatible"]: raise ValueError("handoff intent is not compatible with destination")
    if not payload.get("projectRef"): raise ValueError("projectRef is required")
    body={"schema":"sc-workspace-cross-product-handoff-plan/1.0","version":VERSION,"sourceProduct":c["sourceProduct"],"destinationProduct":c["destinationProduct"],"intent":c["intent"],"projectRef":payload["projectRef"],"researchSessionRef":payload.get("researchSessionRef"),"objects":_refs(payload),"lineage":{"registrySchema":registry_profile().get("schema"),"registryVersion":registry_profile().get("version"),"sessionSchema":session_profile().get("schema"),"sessionVersion":session_profile().get("version"),"handoffFabricSchema":handoff_fabric_profile().get("schema"),"handoffPackageSchema":HANDOFF_SCHEMA},"requiredReceipts":["prepared-handoff","destination-acceptance"],"dispatchPerformed":False,"executionPerformed":False,"destinationMutationPerformed":False,"authorityGranted":False}
    body["objectCount"]=len(body["objects"]); body["planDigest"]=_digest(body); return body
def manifest(payload):
    p=plan(payload); body={"schema":"sc-workspace-cross-product-handoff-manifest/1.0","version":VERSION,"projectRef":p["projectRef"],"researchSessionRef":p["researchSessionRef"],"sourceProduct":p["sourceProduct"],"destinationProduct":p["destinationProduct"],"intent":p["intent"],"objects":p["objects"],"lineage":p["lineage"],"requiredReceipts":p["requiredReceipts"],"portable":True,"readOnly":True,"importExecutesAutomatically":False,"destinationMustExplicitlyAccept":True}; body["manifestDigest"]=_digest(body); return body
def acceptance_contract(payload):
    d=str(payload.get("destinationProduct") or "")
    if d not in DESTINATIONS: raise ValueError("unsupported destination product")
    return {"schema":"sc-workspace-cross-product-acceptance-contract/1.0","version":VERSION,"destinationProduct":d,"destinationMustMatchPreparedHandoff":True,"acceptanceMustBeExplicit":True,"idempotentReplayExpected":True,"durableReceiptRequired":True,"automaticAcceptanceEnabled":False,"automaticExecutionEnabled":False,"authorityGranted":False}
def compatibility(_=None):
    f=handoff_fabric_profile(); r=registry_profile(); s=session_profile()
    checks={"handoffFabricBackendAuthoritative":bool(f.get("backendAuthoritative")),"handoffFabricDurableReceipts":bool(f.get("durableReceipts")),"handoffFabricRevisionPinning":bool(f.get("revisionPinning")),"handoffFabricFingerprintPinning":bool(f.get("fingerprintPinning")),"handoffFabricDestinationAcceptanceReceipt":bool(f.get("destinationAcceptanceReceipt")),"handoffFabricGenericDestinationMutationDisabled":f.get("genericDestinationMutation") is False,"runtimeRegistryValid":bool(r.get("registryValid")),"unifiedResearchSessionAvailable":s.get("version")=="3.66.0"}
    return {"schema":"sc-workspace-cross-product-handoff-compatibility/1.0","version":VERSION,"compatibleFrom":"3.67.0","consolidatesHandoffFabricFrom":"3.2.0","currentRelease":VERSION,"previousRelease":"3.67.0","rollbackTarget":"3.67.0","databaseMigrationRequired":False,"projectSchemaMigrationRequired":False,"checks":checks,"compatible":all(checks.values()),"existingHandoffFabricRemainsAuthoritative":True}
def validate(_=None):
    c=compatibility(); errors=[k for k,v in c["checks"].items() if not v]; unsupported=[p for p in DESTINATIONS if p not in PRODUCTS]
    if unsupported: errors.append("unsupported destination profiles: "+",".join(unsupported))
    return {"valid":not errors,"version":VERSION,"destinationCount":len(DESTINATIONS),"supportedIntentCount":len(INTENTS),"errors":errors,"evaluatedAt":_now(),"mutationPerformed":False,"authorityGranted":False}
def snapshot(payload=None):
    payload=payload or {}; body={"runtime":runtime_profile(),"destinations":destination_profiles(),"compatibility":compatibility(),"capturedAt":_now()}
    if payload.get("handoff"): body["handoffManifest"]=manifest(payload["handoff"])
    return {"schema":"sc-workspace-cross-product-handoff-recovery-snapshot/1.0","version":VERSION,"snapshot":body,"snapshotDigest":_digest(body),"readOnly":True,"portable":True,"automaticReplayEnabled":False,"automaticDispatchEnabled":False,"authorityGranted":False,"mutationPerformed":False}
def runtime_profile():
    v=validate()
    return {"schema":RUNTIME_SCHEMA,"version":VERSION,"title":"Cross-Product Research Handoff Consolidation","existingHandoffFabricSchema":handoff_fabric_profile().get("schema"),"existingHandoffPackageSchema":HANDOFF_SCHEMA,"registeredDestinationCount":len(DESTINATIONS),"supportedProducts":list(PRODUCTS),"supportedIntents":list(INTENTS),"boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),"consolidationValid":bool(v["valid"]),"capabilities":{"normalizedDestinationProfiles":True,"intentCompatibilityDiscovery":True,"pinnedObjectHandoffPlanning":True,"portableHandoffManifests":True,"explicitAcceptanceContracts":True,"handoffLineagePreservation":True,"recoverySafeSnapshots":True,"existingDurableReceiptReuse":True},**BOUNDARIES}
def operation_index():
    return {"schema":"sc-workspace-cross-product-research-handoff-consolidation-operation-index/1.0","version":VERSION,"items":[{"operation":op,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True,"descriptiveOnly":True,"executionAuthority":False,"approvalAuthority":False,"publicationAuthority":False,"mutationAuthority":False,"externalSideEffectAuthority":False} for op in OPERATIONS],**BOUNDARIES}
def execute(operation,payload=None):
    h={"workspace.handoff-consolidation.validate":validate,"workspace.handoff-consolidation.destination-profiles":destination_profiles,"workspace.handoff-consolidation.intent-compatibility":intent_compatibility,"workspace.handoff-consolidation.plan":plan,"workspace.handoff-consolidation.manifest":manifest,"workspace.handoff-consolidation.acceptance-contract":acceptance_contract,"workspace.handoff-consolidation.compatibility":compatibility,"workspace.handoff-consolidation.snapshot":snapshot}
    if operation not in h: raise ValueError("unsupported operation")
    return {"schema":RESULT_SCHEMA,"version":VERSION,"operation":operation,"result":h[operation](payload or {})}
