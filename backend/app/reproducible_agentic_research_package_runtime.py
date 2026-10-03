from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import hashlib, json
from typing import Any, Dict, Mapping
from uuid import uuid4

VERSION="3.63.0"
RUNTIME_SCHEMA="sc-workspace-reproducible-agentic-research-package-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-reproducible-agentic-research-package-request/1.0"
RESULT_SCHEMA="sc-workspace-reproducible-agentic-research-package-result/1.0"
PACKAGE_SCHEMA="sc-workspace-reproducible-agentic-research-package/1.0"
OBJECT_SCHEMA="sc-workspace-research-package-object/1.0"
RECEIPT_SCHEMA="sc-workspace-research-package-receipt-record/1.0"
GOVERNANCE_RECORD_SCHEMA="sc-workspace-research-package-governance-record/1.0"
MANIFEST_SCHEMA="sc-workspace-research-package-manifest/1.0"
VERIFICATION_SCHEMA="sc-workspace-research-package-verification/1.0"
SNAPSHOT_SCHEMA="sc-workspace-research-package-snapshot/1.0"

UPSTREAM={
 "agenticWorkflow":"sc-workspace-agentic-research-workflow-runtime/1.0",
 "humanGovernance":"sc-workspace-human-governance-approval-intervention-runtime/1.0",
 "multiAgentCoordination":"sc-workspace-multi-agent-orchestration-specialist-coordination-runtime/1.0",
}

OPERATIONS=(
 "workspace.research-package.validate",
 "workspace.research-package.create",
 "workspace.research-package.add-object",
 "workspace.research-package.add-receipt",
 "workspace.research-package.add-governance",
 "workspace.research-package.finalize",
 "workspace.research-package.verify",
 "workspace.research-package.snapshot",
)

ALLOWED_OBJECT_KINDS=(
 "workflow","workflow_snapshot","specialist_team","specialist_assignment",
 "specialist_synthesis","evidence","claim","dataset","model","notebook",
 "visualization","artifact","publication","runtime_metadata",
 "environment_metadata","final_output",
)

BOUNDARIES={
 "boundedOperationsOnly":True,
 "arbitraryCodeExecution":False,
 "automaticReplayEnabled":False,
 "automaticApprovalEnabled":False,
 "automaticGovernanceBypassEnabled":False,
 "automaticExternalSideEffectsEnabled":False,
 "automaticClaimPromotionEnabled":False,
 "automaticEvidenceMutationEnabled":False,
 "automaticTruthDeterminationEnabled":False,
 "automaticEvidenceRankingEnabled":False,
 "packageMayGrantAuthority":False,
 "packageMayModifySourceObjects":False,
 "verificationIsDescriptiveOnly":True,
 "provenancePreserved":True,
 "governanceHistoryPreserved":True,
 "dissentPreserved":True,
 "contentAddressedObjects":True,
 "manifestIntegrityRequired":True,
 "maxObjects":512,
 "maxReceipts":256,
 "maxGovernanceRecords":256,
}

def _now(): return datetime.now(timezone.utc).isoformat()
def _id(prefix): return f"{prefix}_{uuid4().hex}"
def _copy(v): return deepcopy(v)
def _digest(v):
    raw=json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(raw).hexdigest()

def _authority():
    return {"approval":False,"replay":False,"governanceBypass":False,
            "externalSideEffects":False,"sourceMutation":False}

def _package(payload:Mapping[str,Any], require_open=False)->Dict[str,Any]:
    p=payload.get("package")
    if not isinstance(p,dict) or p.get("schema")!=PACKAGE_SCHEMA:
        raise ValueError("valid research package is required")
    p=_copy(p)
    if require_open and p.get("status")!="open":
        raise ValueError("research package is not open")
    if any(bool((p.get("authority") or {}).get(k)) for k in _authority()):
        raise ValueError("research package authority boundary violated")
    return p

def create_package(payload):
    research_ref=str(payload.get("researchRef") or payload.get("projectRef") or "").strip()
    if not research_ref: raise ValueError("researchRef is required")
    p={"schema":PACKAGE_SCHEMA,"version":VERSION,"packageId":str(payload.get("packageId") or _id("research_package")),
       "title":str(payload.get("title") or "Reproducible Agentic Research Package"),
       "researchRef":research_ref,"status":"open","createdAt":_now(),"updatedAt":_now(),"finalizedAt":None,
       "upstreamRuntimeSchemas":_copy(UPSTREAM),"objects":[],"receipts":[],"governanceRecords":[],
       "provenanceRefs":list(payload.get("provenanceRefs") or []),
       "dissentRefs":list(payload.get("dissentRefs") or []),"manifest":None,"integrity":None,
       "authority":_authority()}
    return {"package":p,"executionAllowed":False,"authorityGranted":False}

def add_object(payload):
    p=_package(payload,True)
    if len(p["objects"])>=BOUNDARIES["maxObjects"]: raise ValueError("maxObjects exceeded")
    kind=str(payload.get("kind") or "").strip()
    if kind not in ALLOWED_OBJECT_KINDS: raise ValueError("unsupported object kind")
    source_ref=str(payload.get("sourceRef") or "").strip()
    if not source_ref: raise ValueError("sourceRef is required")
    content=_copy(payload.get("content"))
    record={"schema":OBJECT_SCHEMA,"version":VERSION,"objectId":str(payload.get("objectId") or _id("package_object")),
            "kind":kind,"sourceRef":source_ref,"content":content,"contentDigest":_digest(content),
            "provenanceRefs":list(payload.get("provenanceRefs") or []),"capturedAt":_now(),
            "immutableCapture":True,"sourceMutationPerformed":False}
    p["objects"].append(record); p["updatedAt"]=_now()
    return {"package":p,"object":record}

def add_receipt(payload):
    p=_package(payload,True)
    if len(p["receipts"])>=BOUNDARIES["maxReceipts"]: raise ValueError("maxReceipts exceeded")
    receipt=_copy(payload.get("receipt"))
    if not isinstance(receipt,dict) or not receipt.get("schema"): raise ValueError("receipt with schema is required")
    record={"schema":RECEIPT_SCHEMA,"version":VERSION,"recordId":str(payload.get("recordId") or _id("receipt_record")),
            "sourceSchema":str(receipt["schema"]),"sourceReceiptId":str(receipt.get("receiptId") or receipt.get("recordId") or ""),
            "receipt":receipt,"receiptDigest":_digest(receipt),"provenanceRefs":list(payload.get("provenanceRefs") or []),
            "capturedAt":_now(),"immutableCapture":True}
    p["receipts"].append(record); p["updatedAt"]=_now()
    return {"package":p,"receiptRecord":record}

def add_governance(payload):
    p=_package(payload,True)
    if len(p["governanceRecords"])>=BOUNDARIES["maxGovernanceRecords"]: raise ValueError("maxGovernanceRecords exceeded")
    g=_copy(payload.get("governance"))
    if not isinstance(g,dict) or not g.get("schema"): raise ValueError("governance with schema is required")
    record={"schema":GOVERNANCE_RECORD_SCHEMA,"version":VERSION,"recordId":str(payload.get("recordId") or _id("governance_record")),
            "sourceSchema":str(g["schema"]),"governance":g,"governanceDigest":_digest(g),
            "provenanceRefs":list(payload.get("provenanceRefs") or []),"capturedAt":_now(),
            "immutableCapture":True,"approvalAuthorityGranted":False}
    p["governanceRecords"].append(record); p["updatedAt"]=_now()
    return {"package":p,"governanceRecord":record}

def _manifest_body(p):
    return {"packageId":p["packageId"],"researchRef":p["researchRef"],"version":p["version"],
            "upstreamRuntimeSchemas":_copy(p.get("upstreamRuntimeSchemas") or {}),
            "objectDigests":[{"objectId":x["objectId"],"kind":x["kind"],"digest":x["contentDigest"]} for x in p.get("objects") or []],
            "receiptDigests":[{"recordId":x["recordId"],"digest":x["receiptDigest"]} for x in p.get("receipts") or []],
            "governanceDigests":[{"recordId":x["recordId"],"digest":x["governanceDigest"]} for x in p.get("governanceRecords") or []],
            "provenanceRefs":list(p.get("provenanceRefs") or []),"dissentRefs":list(p.get("dissentRefs") or []),
            "authority":_copy(p.get("authority") or {})}

def finalize_package(payload):
    p=_package(payload,True)
    if not (p.get("objects") or p.get("receipts") or p.get("governanceRecords")):
        raise ValueError("research package cannot be finalized empty")
    body=_manifest_body(p)
    m={"schema":MANIFEST_SCHEMA,"version":VERSION,"packageId":p["packageId"],"createdAt":_now(),
       "body":body,"manifestDigest":_digest(body),"immutable":True}
    p["manifest"]=m; p["integrity"]={"algorithm":"sha256","manifestDigest":m["manifestDigest"],"verifiedAtFinalization":True}
    p["status"]="finalized"; p["finalizedAt"]=_now(); p["updatedAt"]=p["finalizedAt"]
    return {"package":p,"manifest":m,"executionAllowed":False,"approvalAuthorityGranted":False,"replayAuthorityGranted":False}

def verify_package(payload):
    p=_package(payload); errors=[]; m=p.get("manifest")
    if p.get("status")!="finalized": errors.append("package is not finalized")
    if not isinstance(m,dict) or m.get("schema")!=MANIFEST_SCHEMA:
        errors.append("valid manifest is required")
    else:
        body=_manifest_body(p)
        if m.get("body")!=body: errors.append("manifest body does not match package")
        if m.get("manifestDigest")!=_digest(body): errors.append("manifest digest mismatch")
        for x in p.get("objects") or []:
            if x.get("contentDigest")!=_digest(x.get("content")): errors.append(f"object digest mismatch: {x.get('objectId')}")
        for x in p.get("receipts") or []:
            if x.get("receiptDigest")!=_digest(x.get("receipt")): errors.append(f"receipt digest mismatch: {x.get('recordId')}")
        for x in p.get("governanceRecords") or []:
            if x.get("governanceDigest")!=_digest(x.get("governance")): errors.append(f"governance digest mismatch: {x.get('recordId')}")
    v={"schema":VERIFICATION_SCHEMA,"version":VERSION,"packageId":p.get("packageId"),"verified":not errors,
       "errors":errors,"verifiedAt":_now(),"descriptiveOnly":True,"executionPerformed":False,
       "approvalPerformed":False,"sourceMutationPerformed":False}
    return {"verification":v,"package":p}

def validate(payload):
    errors=[]; p=payload.get("package")
    if p is not None:
        if not isinstance(p,dict) or p.get("schema")!=PACKAGE_SCHEMA: errors.append("invalid research package schema")
        elif any(bool((p.get("authority") or {}).get(k)) for k in _authority()):
            errors.append("research package authority boundary violated")
    return {"valid":not errors,"errors":errors}

def snapshot(payload):
    p=_package(payload); captured=_now()
    body={"package":p,"runtimeVersion":VERSION,"capturedAt":captured}
    return {"schema":SNAPSHOT_SCHEMA,"version":VERSION,"packageId":p["packageId"],"capturedAt":captured,
            "package":p,"snapshotDigest":_digest(body),"executionAllowed":False,"authorityGranted":False}

def runtime_profile():
    return {"schema":RUNTIME_SCHEMA,"version":VERSION,"title":"Reproducible Agentic Research Package Runtime",
            "boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),
            "allowedObjectKinds":list(ALLOWED_OBJECT_KINDS),"upstreamRuntimeSchemas":_copy(UPSTREAM),
            "capabilities":{"portableResearchPackages":True,"contentAddressedObjectCapture":True,
             "receiptCapture":True,"governanceHistoryCapture":True,"dissentPreservation":True,
             "manifestFinalization":True,"integrityVerification":True,"portableSnapshots":True},**BOUNDARIES}

def operation_index():
    return {"schema":"sc-workspace-reproducible-agentic-research-package-operation-index/1.0","version":VERSION,
            "items":[{"operation":op,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True,
                      "executionAuthority":False,"approvalAuthority":False} for op in OPERATIONS],
            **BOUNDARIES}

def execute(operation,payload):
    handlers={"workspace.research-package.validate":validate,"workspace.research-package.create":create_package,
              "workspace.research-package.add-object":add_object,"workspace.research-package.add-receipt":add_receipt,
              "workspace.research-package.add-governance":add_governance,"workspace.research-package.finalize":finalize_package,
              "workspace.research-package.verify":verify_package,"workspace.research-package.snapshot":snapshot}
    if operation not in handlers: raise ValueError("unsupported operation")
    return {"schema":RESULT_SCHEMA,"version":VERSION,"operation":operation,"result":handlers[operation](payload or {})}
