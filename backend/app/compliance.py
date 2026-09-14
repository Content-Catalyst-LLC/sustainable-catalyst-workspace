from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    AttestationVerificationReceipt,
    ComplianceWaiver,
    RuntimeExecutionAttestation,
    RuntimeTrustPolicyHead,
    RuntimeTrustPolicyRevision,
)
from .schemas import AttestationVerificationCreateRequest, ComplianceWaiverCreateRequest, RuntimeTrustPolicyStoreRequest
from .utils import iso, sha256_hex

NON_WAIVABLE_ATTESTATION_CHECKS = {"job-terminal-state", "job-succeeded"}


def _now():
    return datetime.now(timezone.utc)


def _clean(values, limit=100):
    out=[]; seen=set()
    for raw in values or []:
        value=str(raw).strip()[:160]
        if not value: continue
        key=value.casefold()
        if key in seen: continue
        seen.add(key); out.append(value)
    return out[:limit]


def _parse_time(value: str | None):
    if not value: return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=422, detail="expiresAt must be an ISO-8601 timestamp.")


def trust_policy_metadata(row):
    return {
        "trustPolicyId": row.trust_policy_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "revision": int(row.revision),
        "fingerprint": row.fingerprint,
        "allowedSources": row.allowed_sources_json,
        "allowedAttestors": row.allowed_attestors_json,
        "acceptedClassifications": row.accepted_classifications_json,
        "requireBudgetCompliant": bool(row.require_budget_compliant),
        "requireSandboxCompliant": bool(row.require_sandbox_compliant),
        "requireEvidenceDigest": bool(row.require_evidence_digest),
        "allowedSandboxModes": row.allowed_sandbox_modes_json,
        "downstreamScopes": row.downstream_scopes_json,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def waiver_metadata(row):
    return {
        "waiverId": row.waiver_id,
        "attestationId": row.attestation_id,
        "downstreamScopes": row.downstream_scopes_json,
        "waivedChecks": row.waived_checks_json,
        "reason": row.reason,
        "humanAuthorized": bool(row.human_authorized),
        "expiresAt": iso(row.expires_at),
        "notes": row.notes,
        "fingerprint": row.fingerprint,
        "createdAt": iso(row.created_at),
        "executionPolicyRelaxed": False,
        "attestationRewritten": False,
    }


def verification_metadata(row):
    return {
        "verificationId": row.verification_id,
        "attestationId": row.attestation_id,
        "attestationFingerprint": row.attestation_fingerprint,
        "trustPolicyRef": {"trustPolicyId": row.trust_policy_id, "revision": int(row.trust_policy_revision), "fingerprint": row.trust_policy_fingerprint},
        "downstreamScope": row.downstream_scope,
        "waiverId": row.waiver_id or None,
        "eligible": bool(row.eligible),
        "classification": row.classification,
        "checks": row.checks_json,
        "notes": row.notes,
        "fingerprint": row.fingerprint,
        "createdAt": iso(row.created_at),
        "executionAuthorizationGranted": False,
    }


def store_trust_policy(db: Session, user_key: str, payload: RuntimeTrustPolicyStoreRequest):
    settings=get_settings(); pid=payload.trustPolicyId.strip(); op=(payload.operationId or "").strip()
    existing=db.get(RuntimeTrustPolicyHead,{"user_key":user_key,"trust_policy_id":pid})
    doc={
        "allowedSources": _clean(payload.allowedSources, 10),
        "allowedAttestors": _clean(payload.allowedAttestors, 100),
        "acceptedClassifications": _clean(payload.acceptedClassifications, 10),
        "requireBudgetCompliant": bool(payload.requireBudgetCompliant),
        "requireSandboxCompliant": bool(payload.requireSandboxCompliant),
        "requireEvidenceDigest": bool(payload.requireEvidenceDigest),
        "allowedSandboxModes": _clean(payload.allowedSandboxModes, 10),
        "downstreamScopes": _clean(payload.downstreamScopes, 10),
    }
    fp=sha256_hex(doc)
    if existing is not None and op and existing.last_operation_id==op:
        if existing.fingerprint!=fp: raise HTTPException(status_code=409,detail="Runtime-trust operationId was reused for a different policy.")
        return existing, True
    current=int(existing.revision) if existing else 0
    if existing is None:
        if payload.expectedRevision not in (None,0): raise HTTPException(status_code=409,detail={"message":"Runtime-trust policy revision conflict.","currentRevision":0})
        count=int(db.scalar(select(func.count()).select_from(RuntimeTrustPolicyHead).where(RuntimeTrustPolicyHead.user_key==user_key)) or 0)
        if count>=settings.max_runtime_trust_policies_per_account: raise HTTPException(status_code=409,detail="Runtime-trust policy limit reached.")
    elif payload.expectedRevision is None or int(payload.expectedRevision)!=current:
        raise HTTPException(status_code=409,detail={"message":"Runtime-trust policy revision conflict.","currentRevision":current,"current":trust_policy_metadata(existing)})
    rev=current+1; now=_now()
    values=dict(project_id=(payload.projectId or "").strip(),name=payload.name.strip(),description=payload.description.strip(),revision=rev,fingerprint=fp,
        allowed_sources_json=doc["allowedSources"],allowed_attestors_json=doc["allowedAttestors"],accepted_classifications_json=doc["acceptedClassifications"],
        require_budget_compliant=doc["requireBudgetCompliant"],require_sandbox_compliant=doc["requireSandboxCompliant"],require_evidence_digest=doc["requireEvidenceDigest"],
        allowed_sandbox_modes_json=doc["allowedSandboxModes"],downstream_scopes_json=doc["downstreamScopes"],metadata_json=payload.metadata)
    if existing is None:
        existing=RuntimeTrustPolicyHead(user_key=user_key,trust_policy_id=pid,last_operation_id=op,created_at=now,updated_at=now,**values); db.add(existing)
    else:
        for k,v in values.items(): setattr(existing,k,v)
        existing.last_operation_id=op; existing.updated_at=now
    db.add(RuntimeTrustPolicyRevision(user_key=user_key,trust_policy_id=pid,operation_id=op,created_at=now,**values))
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409,detail="Concurrent runtime-trust policy revision detected.")
    db.refresh(existing); return existing, False


def get_trust_policy(db,user_key,pid): return db.get(RuntimeTrustPolicyHead,{"user_key":user_key,"trust_policy_id":pid})
def get_trust_policy_revision(db,user_key,pid,rev): return db.get(RuntimeTrustPolicyRevision,{"user_key":user_key,"trust_policy_id":pid,"revision":rev})

def list_trust_policies(db,user_key,project_id=None):
    stmt=select(RuntimeTrustPolicyHead).where(RuntimeTrustPolicyHead.user_key==user_key)
    if project_id: stmt=stmt.where(RuntimeTrustPolicyHead.project_id==project_id)
    return [trust_policy_metadata(x) for x in db.scalars(stmt.order_by(RuntimeTrustPolicyHead.updated_at.desc())).all()]

def list_trust_policy_revisions(db,user_key,pid):
    return [trust_policy_metadata(x) for x in db.scalars(select(RuntimeTrustPolicyRevision).where(RuntimeTrustPolicyRevision.user_key==user_key,RuntimeTrustPolicyRevision.trust_policy_id==pid).order_by(RuntimeTrustPolicyRevision.revision.desc())).all()]


def resolve_trust_policy(db,user_key,ref):
    row=get_trust_policy_revision(db,user_key,ref.trustPolicyId,ref.revision) if ref.revision else get_trust_policy(db,user_key,ref.trustPolicyId)
    if row is None: raise HTTPException(status_code=409,detail="Attestation verification references an unavailable runtime-trust policy.")
    if ref.fingerprint and ref.fingerprint!=row.fingerprint: raise HTTPException(status_code=409,detail="Runtime-trust policy fingerprint mismatch.")
    return row


def create_waiver(db: Session,user_key:str,payload:ComplianceWaiverCreateRequest):
    settings=get_settings(); att=db.get(RuntimeExecutionAttestation,{"user_key":user_key,"attestation_id":payload.attestationId})
    if att is None: raise HTTPException(status_code=404,detail="Workspace runtime-execution attestation not found.")
    if att.classification in ("execution-failed","incomplete"): raise HTTPException(status_code=409,detail="Execution-failed or incomplete attestations cannot be waived for downstream compliance.")
    failed={x.get("check") for x in (att.checks_json or []) if x.get("status")=="fail"}
    requested=set(_clean(payload.waivedChecks,50))
    if not requested or not requested.issubset(failed): raise HTTPException(status_code=409,detail="Waiver may reference only failed attestation checks.")
    if requested & NON_WAIVABLE_ATTESTATION_CHECKS: raise HTTPException(status_code=409,detail="Terminal/success checks cannot be waived.")
    count=int(db.scalar(select(func.count()).select_from(ComplianceWaiver).where(ComplianceWaiver.user_key==user_key)) or 0)
    if count>=settings.max_compliance_waivers_per_account: raise HTTPException(status_code=409,detail="Compliance-waiver limit reached.")
    wid=(payload.waiverId or f"compliance-waiver-{uuid4()}").strip()
    if db.get(ComplianceWaiver,{"user_key":user_key,"waiver_id":wid}) is not None: raise HTTPException(status_code=409,detail="Compliance waiver id already exists.")
    expires=_parse_time(payload.expiresAt)
    if expires and expires<=_now(): raise HTTPException(status_code=409,detail="Compliance waiver expiry must be in the future.")
    doc={"attestationId":att.attestation_id,"attestationFingerprint":att.fingerprint,"downstreamScopes":_clean(payload.downstreamScopes,10),"waivedChecks":sorted(requested),"reason":payload.reason.strip(),"humanAuthorized":True,"expiresAt":iso(expires),"notes":payload.notes}
    row=ComplianceWaiver(user_key=user_key,waiver_id=wid,attestation_id=att.attestation_id,downstream_scopes_json=doc["downstreamScopes"],waived_checks_json=doc["waivedChecks"],reason=doc["reason"],human_authorized=True,expires_at=expires,notes=payload.notes,fingerprint=sha256_hex(doc),created_at=_now())
    db.add(row); db.commit(); db.refresh(row); return row


def get_waiver(db,user_key,wid): return db.get(ComplianceWaiver,{"user_key":user_key,"waiver_id":wid})
def list_waivers(db,user_key): return [waiver_metadata(x) for x in db.scalars(select(ComplianceWaiver).where(ComplianceWaiver.user_key==user_key).order_by(ComplianceWaiver.created_at.desc())).all()]


def evaluate_verification(att,policy,scope,waiver=None):
    checks=[]
    def add(name,ok,**details): checks.append({"check":name,"status":"pass" if ok else "fail",**details})
    sandbox=att.sandbox_attestation_json or {}; failed={x.get("check") for x in (att.checks_json or []) if x.get("status")=="fail"}; waived=set()
    waiver_valid=False
    if waiver is not None:
        waiver_valid=(waiver.attestation_id==att.attestation_id and waiver.human_authorized and scope in (waiver.downstream_scopes_json or []) and (waiver.expires_at is None or waiver.expires_at>_now()))
        if waiver_valid: waived=set(waiver.waived_checks_json or [])
    remaining=failed-waived
    add("downstream-scope-allowed",scope in (policy.downstream_scopes_json or []),scope=scope)
    add("attestation-source-trusted",att.source in (policy.allowed_sources_json or []),source=att.source)
    attestor=str(sandbox.get("attestedBy") or "")
    allowed_attestors=policy.allowed_attestors_json or []
    add("attestor-trusted",not allowed_attestors or attestor in allowed_attestors,attestedBy=attestor)
    digest=str(sandbox.get("evidenceDigest") or "")
    add("evidence-digest-present",(not policy.require_evidence_digest) or len(digest)>=32)
    add("sandbox-mode-allowed",str(sandbox.get("mode") or "") in (policy.allowed_sandbox_modes_json or []),mode=sandbox.get("mode"))
    classification_ok=att.classification in (policy.accepted_classifications_json or [])
    if not classification_ok and waiver_valid and att.classification in ("budget-exceeded","sandbox-deviation") and not remaining:
        classification_ok=True
    add("attestation-classification-accepted",classification_ok,classification=att.classification)
    budget_ok=bool(att.budget_compliant) or (waiver_valid and not any(x.startswith("budget-") for x in remaining))
    sandbox_ok=bool(att.sandbox_compliant) or (waiver_valid and not any(x.startswith("sandbox-") for x in remaining))
    add("budget-compliance",(not policy.require_budget_compliant) or budget_ok)
    add("sandbox-compliance",(not policy.require_sandbox_compliant) or sandbox_ok)
    add("execution-succeeded",bool(att.execution_succeeded))
    if waiver is not None: add("waiver-valid",waiver_valid,waiverId=waiver.waiver_id)
    eligible=all(x["status"]=="pass" for x in checks)
    if att.classification=="incomplete": classification="incomplete"; eligible=False
    elif eligible: classification="verified-with-waiver" if waiver_valid and bool(waived & failed) else "verified"
    else: classification="rejected"
    return {"eligible":eligible,"classification":classification,"checks":checks,"waiverUsed":bool(waiver_valid and waived & failed)}


def create_verification(db: Session,user_key:str,payload:AttestationVerificationCreateRequest):
    settings=get_settings(); att=db.get(RuntimeExecutionAttestation,{"user_key":user_key,"attestation_id":payload.attestationId})
    if att is None: raise HTTPException(status_code=404,detail="Workspace runtime-execution attestation not found.")
    policy=resolve_trust_policy(db,user_key,payload.trustPolicyRef)
    waiver=None
    if payload.waiverId:
        waiver=get_waiver(db,user_key,payload.waiverId)
        if waiver is None: raise HTTPException(status_code=404,detail="Workspace compliance waiver not found.")
    count=int(db.scalar(select(func.count()).select_from(AttestationVerificationReceipt).where(AttestationVerificationReceipt.user_key==user_key)) or 0)
    if count>=settings.max_attestation_verifications_per_account: raise HTTPException(status_code=409,detail="Attestation-verification limit reached.")
    result=evaluate_verification(att,policy,payload.downstreamScope,waiver)
    vid=(payload.verificationId or f"attestation-verification-{uuid4()}").strip()
    if db.get(AttestationVerificationReceipt,{"user_key":user_key,"verification_id":vid}) is not None: raise HTTPException(status_code=409,detail="Attestation verification id already exists.")
    doc={"attestationId":att.attestation_id,"attestationFingerprint":att.fingerprint,"trustPolicyId":policy.trust_policy_id,"trustPolicyRevision":int(policy.revision),"trustPolicyFingerprint":policy.fingerprint,"downstreamScope":payload.downstreamScope,"waiverId":waiver.waiver_id if waiver else "",**result,"notes":payload.notes}
    row=AttestationVerificationReceipt(user_key=user_key,verification_id=vid,attestation_id=att.attestation_id,attestation_fingerprint=att.fingerprint,trust_policy_id=policy.trust_policy_id,trust_policy_revision=int(policy.revision),trust_policy_fingerprint=policy.fingerprint,downstream_scope=payload.downstreamScope,waiver_id=waiver.waiver_id if waiver else "",eligible=result["eligible"],classification=result["classification"],checks_json=result["checks"],notes=payload.notes,fingerprint=sha256_hex(doc),created_at=_now())
    db.add(row); db.commit(); db.refresh(row); return row


def get_verification(db,user_key,vid): return db.get(AttestationVerificationReceipt,{"user_key":user_key,"verification_id":vid})
def list_verifications(db,user_key): return [verification_metadata(x) for x in db.scalars(select(AttestationVerificationReceipt).where(AttestationVerificationReceipt.user_key==user_key).order_by(AttestationVerificationReceipt.created_at.desc())).all()]
