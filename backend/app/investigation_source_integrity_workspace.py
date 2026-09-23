from __future__ import annotations
from collections import defaultdict
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (ProjectHead, InvestigationSourceHead, InvestigationSourceRevision, InvestigationSourceProvenanceEvent,
    InvestigationSourceCustodyEvent, InvestigationIntegrityAssertion, InvestigationSourceEvidenceBinding,
    InvestigationSourceIntegritySnapshot)
from .investigation_media_workspace import build_media_graph
from .utils import iso, sha256_hex

SOURCE_INTEGRITY_WORKSPACE_SCHEMA="sc-workspace-source-reliability-provenance-evidence-integrity-workspace/1.0"
SOURCE_REQUEST_SCHEMA="sc-workspace-investigation-source-request/1.0"
SOURCE_SCHEMA="sc-workspace-investigation-source/1.0"
PROVENANCE_EVENT_REQUEST_SCHEMA="sc-workspace-source-provenance-event-request/1.0"
CUSTODY_EVENT_REQUEST_SCHEMA="sc-workspace-source-custody-event-request/1.0"
INTEGRITY_ASSERTION_REQUEST_SCHEMA="sc-workspace-integrity-assertion-request/1.0"
EVIDENCE_BINDING_REQUEST_SCHEMA="sc-workspace-source-evidence-binding-request/1.0"
SOURCE_GRAPH_SCHEMA="sc-workspace-source-integrity-graph/1.0"
SOURCE_DIAGNOSTICS_SCHEMA="sc-workspace-source-integrity-diagnostics/1.0"
SOURCE_INTEGRITY_SCHEMA="sc-workspace-source-integrity-assessment/1.0"
SOURCE_SNAPSHOT_REQUEST_SCHEMA="sc-workspace-source-integrity-snapshot-request/1.0"
SOURCE_SNAPSHOT_SCHEMA="sc-workspace-source-integrity-snapshot/1.0"
SOURCE_TYPES=("document","web-page","database-record","public-record","testimony","media","dataset","publication","correspondence","physical-evidence-record","other")
PROVENANCE_EVENT_TYPES=("acquired","imported","copied","transformed","normalized","extracted","redacted","exported","verified","superseded","transferred","other")
CUSTODY_ACTIONS=("received","released","transferred","stored","accessed","copied","sealed","unsealed","verified","other")
ASSERTION_TYPES=("hash-match","signature-valid","metadata-consistent","provenance-complete","custody-intact","original-available","derivative-declared","source-attributed","other")
ASSERTION_STATUSES=("asserted","verified","disputed","failed","unknown")
TARGET_KINDS=("statement","claim","hypothesis","event","entity","document","excerpt","testimony","media-artifact","spatial-observation","evidence-ref","scientific-object-ref")
BINDING_RELATIONS=("source-of","supports","contradicts","contextualizes","corroborates","derived-from","mentions","depicts","records","related-to")
REVIEW_STATES=("open","under-review","documented","contested","unresolved","closed")

class InvestigationSourceRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-source-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); sourceId:str=Field(default="",max_length=160)
    sourceType:Literal["document","web-page","database-record","public-record","testimony","media","dataset","publication","correspondence","physical-evidence-record","other"]
    title:str=Field(min_length=1,max_length=1000); sourceRef:str=Field(min_length=1,max_length=2000)
    publisher:str=Field(default="",max_length=1000); publishedAt:str=Field(default="",max_length=64); retrievedAt:str=Field(default="",max_length=64)
    contentFingerprint:str=Field(min_length=8,max_length=128); reviewState:Literal["open","under-review","documented","contested","unresolved","closed"]="open"
    expectedRevision:int|None=Field(default=None,ge=0); metadata:dict[str,Any]=Field(default_factory=dict)

class SourceProvenanceEventRequest(BaseModel):
    schema:Literal["sc-workspace-source-provenance-event-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); sourceId:str=Field(min_length=1,max_length=160)
    eventType:Literal["acquired","imported","copied","transformed","normalized","extracted","redacted","exported","verified","superseded","transferred","other"]
    parentRef:str=Field(default="",max_length=2000); childRef:str=Field(default="",max_length=2000); occurredAt:str=Field(default="",max_length=64)
    actorRef:str=Field(default="",max_length=1000); operationRef:str=Field(default="",max_length=1000); sourceFingerprint:str=Field(default="",max_length=128); metadata:dict[str,Any]=Field(default_factory=dict)

class SourceCustodyEventRequest(BaseModel):
    schema:Literal["sc-workspace-source-custody-event-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); sourceId:str=Field(min_length=1,max_length=160)
    action:Literal["received","released","transferred","stored","accessed","copied","sealed","unsealed","verified","other"]
    custodianRef:str=Field(min_length=1,max_length=1000); occurredAt:str=Field(default="",max_length=64); locationRef:str=Field(default="",max_length=1000)
    receiptRef:str=Field(default="",max_length=2000); sourceFingerprint:str=Field(default="",max_length=128); metadata:dict[str,Any]=Field(default_factory=dict)

class IntegrityAssertionRequest(BaseModel):
    schema:Literal["sc-workspace-integrity-assertion-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); sourceId:str=Field(min_length=1,max_length=160)
    assertionType:Literal["hash-match","signature-valid","metadata-consistent","provenance-complete","custody-intact","original-available","derivative-declared","source-attributed","other"]
    status:Literal["asserted","verified","disputed","failed","unknown"]
    basisRef:str=Field(default="",max_length=2000); sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)

class SourceEvidenceBindingRequest(BaseModel):
    schema:Literal["sc-workspace-source-evidence-binding-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); sourceId:str=Field(min_length=1,max_length=160)
    targetKind:Literal["statement","claim","hypothesis","event","entity","document","excerpt","testimony","media-artifact","spatial-observation","evidence-ref","scientific-object-ref"]
    targetRef:str=Field(min_length=1,max_length=2000); relation:Literal["source-of","supports","contradicts","contextualizes","corroborates","derived-from","mentions","depicts","records","related-to"]
    locatorRef:str=Field(default="",max_length=1000); sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)

class SourceIntegritySnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-source-integrity-snapshot-request/1.0"]
    includeMediaGraph:bool=True

def profile()->dict[str,Any]:
    return {"schema":SOURCE_INTEGRITY_WORKSPACE_SCHEMA,"workspaceVersion":"3.14.0","release":"Source Reliability, Provenance & Evidence Integrity Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"versionedSourceRecords":True,"contentFingerprintRequired":True,"explicitProvenanceEvents":True,
      "explicitCustodyEvents":True,"humanAssertedIntegrityAssertions":True,"humanAssertedEvidenceBindings":True,"mediaGraphOverlay":True,"immutableIntegritySnapshots":True,
      "descriptiveDiagnostics":True,"automaticSourceReliabilityScoring":False,"automaticCredibilityScoring":False,"automaticAuthenticityDetermination":False,
      "automaticIntegrityVerification":False,"automaticEvidenceRanking":False,"automaticTruthDetermination":False,"automaticCulpabilityInference":False,
      "automaticNarrativeSelection":False,"supportedSourceTypes":list(SOURCE_TYPES),"supportedAssertionTypes":list(ASSERTION_TYPES)}

def _project(db,user_key,project_id):
    r=db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
    if r is None: raise KeyError(project_id)
    return r

def _source(db,user_key,source_id): return db.get(InvestigationSourceHead,{"user_key":user_key,"source_id":source_id})
def source_metadata(r):
    return {"schema":SOURCE_SCHEMA,"sourceId":r.source_id,"projectId":r.project_id,"sourceType":r.source_type,"title":r.title,"sourceRef":r.source_ref,
      "publisher":r.publisher,"publishedAt":r.published_at,"retrievedAt":r.retrieved_at,"contentFingerprint":r.content_fingerprint,"reviewState":r.review_state,
      "revision":r.revision,"sourceRecordFingerprint":r.source_record_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}
def revision_metadata(r):
    x=source_metadata(r); x.pop("updatedAt",None); return x

def store_source(db:Session,user_key:str,p:InvestigationSourceRequest):
    _project(db,user_key,p.projectId); row=_source(db,user_key,p.sourceId) if p.sourceId else None
    if row and row.project_id!=p.projectId: raise ValueError("source belongs to another project")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("source revision conflict")
    sid=p.sourceId or "source-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"projectId":p.projectId,"sourceId":sid,"revision":rev,"sourceType":p.sourceType,"title":p.title,"sourceRef":p.sourceRef,"publisher":p.publisher,
      "publishedAt":p.publishedAt,"retrievedAt":p.retrievedAt,"contentFingerprint":p.contentFingerprint,"reviewState":p.reviewState,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,source_type=p.sourceType,title=p.title,source_ref=p.sourceRef,publisher=p.publisher,published_at=p.publishedAt,retrieved_at=p.retrievedAt,
      content_fingerprint=p.contentFingerprint,review_state=p.reviewState,revision=rev,source_record_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=InvestigationSourceHead(user_key=user_key,source_id=sid,**vals);db.add(row)
    db.add(InvestigationSourceRevision(user_key=user_key,source_id=sid,revision=rev,project_id=p.projectId,source_type=p.sourceType,title=p.title,source_ref=p.sourceRef,
      publisher=p.publisher,published_at=p.publishedAt,retrieved_at=p.retrievedAt,content_fingerprint=p.contentFingerprint,review_state=p.reviewState,source_record_fingerprint=fp,metadata_json=p.metadata))
    db.flush(); return source_metadata(row)

def list_sources(db,user_key,project_id=None,source_type=None,limit=1000):
    q=select(InvestigationSourceHead).where(InvestigationSourceHead.user_key==user_key)
    if project_id:q=q.where(InvestigationSourceHead.project_id==project_id)
    if source_type:q=q.where(InvestigationSourceHead.source_type==source_type)
    q=q.order_by(InvestigationSourceHead.updated_at.desc()).limit(limit);return [source_metadata(x) for x in db.scalars(q).all()]
def get_source(db,user_key,source_id):
    r=_source(db,user_key,source_id); return source_metadata(r) if r else None
def source_revisions(db,user_key,source_id,limit=100):
    q=select(InvestigationSourceRevision).where(InvestigationSourceRevision.user_key==user_key,InvestigationSourceRevision.source_id==source_id).order_by(InvestigationSourceRevision.revision.desc()).limit(limit)
    return [revision_metadata(x) for x in db.scalars(q).all()]

def _assert_source_project(db,user_key,project_id,source_id):
    _project(db,user_key,project_id); r=_source(db,user_key,source_id)
    if r is None: raise LookupError(source_id)
    if r.project_id!=project_id: raise ValueError("source belongs to another project")
    return r

def create_provenance_event(db,user_key,p:SourceProvenanceEventRequest):
    _assert_source_project(db,user_key,p.projectId,p.sourceId); fp=sha256_hex(p.model_dump()); q=select(InvestigationSourceProvenanceEvent).where(InvestigationSourceProvenanceEvent.user_key==user_key,InvestigationSourceProvenanceEvent.event_fingerprint==fp)
    old=db.scalars(q).first()
    if old:return provenance_metadata(old)
    r=InvestigationSourceProvenanceEvent(user_key=user_key,event_id="source-prov-"+uuid4().hex[:24],project_id=p.projectId,source_id=p.sourceId,event_type=p.eventType,parent_ref=p.parentRef,child_ref=p.childRef,occurred_at=p.occurredAt,actor_ref=p.actorRef,operation_ref=p.operationRef,source_fingerprint=p.sourceFingerprint,event_fingerprint=fp,metadata_json=p.metadata);db.add(r);db.flush();return provenance_metadata(r)
def provenance_metadata(r): return {"eventId":r.event_id,"projectId":r.project_id,"sourceId":r.source_id,"eventType":r.event_type,"parentRef":r.parent_ref,"childRef":r.child_ref,"occurredAt":r.occurred_at,"actorRef":r.actor_ref,"operationRef":r.operation_ref,"sourceFingerprint":r.source_fingerprint,"eventFingerprint":r.event_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_provenance_events(db,user_key,project_id=None,source_id=None,limit=1000):
    q=select(InvestigationSourceProvenanceEvent).where(InvestigationSourceProvenanceEvent.user_key==user_key)
    if project_id:q=q.where(InvestigationSourceProvenanceEvent.project_id==project_id)
    if source_id:q=q.where(InvestigationSourceProvenanceEvent.source_id==source_id)
    q=q.order_by(InvestigationSourceProvenanceEvent.created_at.desc()).limit(limit);return [provenance_metadata(x) for x in db.scalars(q).all()]

def create_custody_event(db,user_key,p:SourceCustodyEventRequest):
    _assert_source_project(db,user_key,p.projectId,p.sourceId); fp=sha256_hex(p.model_dump()); q=select(InvestigationSourceCustodyEvent).where(InvestigationSourceCustodyEvent.user_key==user_key,InvestigationSourceCustodyEvent.custody_fingerprint==fp)
    old=db.scalars(q).first()
    if old:return custody_metadata(old)
    r=InvestigationSourceCustodyEvent(user_key=user_key,custody_id="custody-"+uuid4().hex[:24],project_id=p.projectId,source_id=p.sourceId,action=p.action,custodian_ref=p.custodianRef,occurred_at=p.occurredAt,location_ref=p.locationRef,receipt_ref=p.receiptRef,source_fingerprint=p.sourceFingerprint,custody_fingerprint=fp,metadata_json=p.metadata);db.add(r);db.flush();return custody_metadata(r)
def custody_metadata(r): return {"custodyId":r.custody_id,"projectId":r.project_id,"sourceId":r.source_id,"action":r.action,"custodianRef":r.custodian_ref,"occurredAt":r.occurred_at,"locationRef":r.location_ref,"receiptRef":r.receipt_ref,"sourceFingerprint":r.source_fingerprint,"custodyFingerprint":r.custody_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_custody_events(db,user_key,project_id=None,source_id=None,limit=1000):
    q=select(InvestigationSourceCustodyEvent).where(InvestigationSourceCustodyEvent.user_key==user_key)
    if project_id:q=q.where(InvestigationSourceCustodyEvent.project_id==project_id)
    if source_id:q=q.where(InvestigationSourceCustodyEvent.source_id==source_id)
    q=q.order_by(InvestigationSourceCustodyEvent.created_at.desc()).limit(limit);return [custody_metadata(x) for x in db.scalars(q).all()]

def create_integrity_assertion(db,user_key,p:IntegrityAssertionRequest):
    _assert_source_project(db,user_key,p.projectId,p.sourceId); fp=sha256_hex(p.model_dump()); q=select(InvestigationIntegrityAssertion).where(InvestigationIntegrityAssertion.user_key==user_key,InvestigationIntegrityAssertion.assertion_fingerprint==fp)
    old=db.scalars(q).first()
    if old:return assertion_metadata(old)
    r=InvestigationIntegrityAssertion(user_key=user_key,assertion_id="integrity-"+uuid4().hex[:24],project_id=p.projectId,source_id=p.sourceId,assertion_type=p.assertionType,status=p.status,basis_ref=p.basisRef,source_fingerprint=p.sourceFingerprint,note=p.note,assertion_fingerprint=fp,metadata_json=p.metadata);db.add(r);db.flush();return assertion_metadata(r)
def assertion_metadata(r): return {"assertionId":r.assertion_id,"projectId":r.project_id,"sourceId":r.source_id,"assertionType":r.assertion_type,"status":r.status,"basisRef":r.basis_ref,"sourceFingerprint":r.source_fingerprint,"note":r.note,"assertionFingerprint":r.assertion_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_integrity_assertions(db,user_key,project_id=None,source_id=None,status=None,limit=1000):
    q=select(InvestigationIntegrityAssertion).where(InvestigationIntegrityAssertion.user_key==user_key)
    if project_id:q=q.where(InvestigationIntegrityAssertion.project_id==project_id)
    if source_id:q=q.where(InvestigationIntegrityAssertion.source_id==source_id)
    if status:q=q.where(InvestigationIntegrityAssertion.status==status)
    q=q.order_by(InvestigationIntegrityAssertion.created_at.desc()).limit(limit);return [assertion_metadata(x) for x in db.scalars(q).all()]

def create_evidence_binding(db,user_key,p:SourceEvidenceBindingRequest):
    _assert_source_project(db,user_key,p.projectId,p.sourceId); fp=sha256_hex(p.model_dump()); q=select(InvestigationSourceEvidenceBinding).where(InvestigationSourceEvidenceBinding.user_key==user_key,InvestigationSourceEvidenceBinding.binding_fingerprint==fp)
    old=db.scalars(q).first()
    if old:return binding_metadata(old)
    r=InvestigationSourceEvidenceBinding(user_key=user_key,binding_id="source-bind-"+uuid4().hex[:24],project_id=p.projectId,source_id=p.sourceId,target_kind=p.targetKind,target_ref=p.targetRef,relation=p.relation,locator_ref=p.locatorRef,source_fingerprint=p.sourceFingerprint,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata);db.add(r);db.flush();return binding_metadata(r)
def binding_metadata(r): return {"bindingId":r.binding_id,"projectId":r.project_id,"sourceId":r.source_id,"targetKind":r.target_kind,"targetRef":r.target_ref,"relation":r.relation,"locatorRef":r.locator_ref,"sourceFingerprint":r.source_fingerprint,"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_evidence_bindings(db,user_key,project_id=None,source_id=None,target_ref=None,limit=1000):
    q=select(InvestigationSourceEvidenceBinding).where(InvestigationSourceEvidenceBinding.user_key==user_key)
    if project_id:q=q.where(InvestigationSourceEvidenceBinding.project_id==project_id)
    if source_id:q=q.where(InvestigationSourceEvidenceBinding.source_id==source_id)
    if target_ref:q=q.where(InvestigationSourceEvidenceBinding.target_ref==target_ref)
    q=q.order_by(InvestigationSourceEvidenceBinding.created_at.desc()).limit(limit);return [binding_metadata(x) for x in db.scalars(q).all()]

def build_integrity_graph(db,user_key,project_id,include_media_graph=True):
    _project(db,user_key,project_id); sources=list_sources(db,user_key,project_id,None,5000); prov=list_provenance_events(db,user_key,project_id,None,10000); custody=list_custody_events(db,user_key,project_id,None,10000); assertions=list_integrity_assertions(db,user_key,project_id,None,None,10000); bindings=list_evidence_bindings(db,user_key,project_id,None,None,10000)
    nodes=[];edges=[]
    base=build_media_graph(db,user_key,project_id,False) if include_media_graph else None
    if base:
        nodes.extend(base.get("nodes") or []);edges.extend(base.get("edges") or [])
    for x in sources:nodes.append({"id":x["sourceId"],"kind":"source","label":x["title"],"sourceType":x["sourceType"],"reviewState":x["reviewState"],"fingerprint":x["sourceRecordFingerprint"]})
    for x in prov:edges.append({"id":x["eventId"],"kind":"provenance-event","from":x["sourceId"],"to":x["childRef"] or x["sourceId"],"eventType":x["eventType"],"humanAsserted":True})
    for x in custody:edges.append({"id":x["custodyId"],"kind":"custody-event","from":x["sourceId"],"to":x["custodianRef"],"action":x["action"],"humanAsserted":True})
    for x in assertions:nodes.append({"id":x["assertionId"],"kind":"integrity-assertion","label":x["assertionType"],"status":x["status"]});edges.append({"id":"edge-"+x["assertionId"],"kind":"integrity-assertion","from":x["sourceId"],"to":x["assertionId"],"humanAsserted":True})
    for x in bindings:edges.append({"id":x["bindingId"],"kind":"source-evidence-binding","from":x["sourceId"],"to":x["targetRef"],"relation":x["relation"],"targetKind":x["targetKind"],"humanAsserted":True})
    fp=sha256_hex({"projectId":project_id,"sources":sources,"provenance":prov,"custody":custody,"assertions":assertions,"bindings":bindings})
    return {"schema":SOURCE_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"sourceCount":len(sources),"provenanceEventCount":len(prov),"custodyEventCount":len(custody),"assertionCount":len(assertions),"bindingCount":len(bindings),"graphFingerprint":fp,"mediaGraphOverlay":bool(base),"automaticTruthDetermination":False,"automaticEvidenceRanking":False}

def source_integrity_diagnostics(db,user_key,project_id):
    sources=list_sources(db,user_key,project_id,None,5000); prov=list_provenance_events(db,user_key,project_id,None,10000); custody=list_custody_events(db,user_key,project_id,None,10000); assertions=list_integrity_assertions(db,user_key,project_id,None,None,10000); bindings=list_evidence_bindings(db,user_key,project_id,None,None,10000)
    p=defaultdict(list);c=defaultdict(list);a=defaultdict(list);b=defaultdict(list)
    for x in prov:p[x["sourceId"]].append(x)
    for x in custody:c[x["sourceId"]].append(x)
    for x in assertions:a[x["sourceId"]].append(x)
    for x in bindings:b[x["sourceId"]].append(x)
    issues=[]
    for s in sources:
        sid=s["sourceId"]
        if not p[sid]: issues.append({"code":"source-provenance-unrecorded","severity":"review","sourceId":sid,"message":"No provenance event has been recorded for this source."})
        if not b[sid]: issues.append({"code":"source-evidence-unbound","severity":"review","sourceId":sid,"message":"Source is not yet bound to an investigative or scientific object."})
        if not a[sid]: issues.append({"code":"integrity-assertion-unrecorded","severity":"review","sourceId":sid,"message":"No integrity assertion has been recorded for this source."})
        statuses={x["status"] for x in a[sid]}
        if "failed" in statuses or "disputed" in statuses: issues.append({"code":"integrity-assertion-needs-review","severity":"review","sourceId":sid,"message":"One or more human-recorded integrity assertions are failed or disputed."})
        fps={x["sourceFingerprint"] for x in p[sid]+c[sid]+a[sid]+b[sid] if x.get("sourceFingerprint")}
        if len(fps)>1: issues.append({"code":"source-fingerprint-mismatch-recorded","severity":"review","sourceId":sid,"message":"Recorded provenance/custody/assertion/binding fingerprints are not uniform."})
    fp=sha256_hex({"projectId":project_id,"issues":issues})
    return {"schema":SOURCE_DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"diagnosticsFingerprint":fp,"automaticResolution":False,"automaticAuthenticityDetermination":False,"automaticReliabilityScoring":False}

def source_integrity_assessment(db,user_key,project_id):
    sources=list_sources(db,user_key,project_id,None,5000); assertions=list_integrity_assertions(db,user_key,project_id,None,None,10000); by=defaultdict(list)
    for x in assertions:by[x["sourceId"]].append(x)
    rows=[]
    for s in sources:
        vals=by[s["sourceId"]]; counts={k:sum(1 for x in vals if x["status"]==k) for k in ASSERTION_STATUSES}
        rows.append({"sourceId":s["sourceId"],"contentFingerprint":s["contentFingerprint"],"assertionCount":len(vals),"statusCounts":counts,"reviewRequired":bool(counts["failed"] or counts["disputed"]),"automaticScore":None})
    fp=sha256_hex({"projectId":project_id,"sources":rows})
    return {"schema":SOURCE_INTEGRITY_SCHEMA,"projectId":project_id,"sources":rows,"sourceCount":len(rows),"integrityFingerprint":fp,"descriptiveOnly":True,"automaticIntegrityVerification":False,"automaticReliabilityScoring":False,"automaticEvidenceRanking":False}

def create_integrity_snapshot(db,user_key,project_id,p:SourceIntegritySnapshotRequest):
    graph=build_integrity_graph(db,user_key,project_id,p.includeMediaGraph);diag=source_integrity_diagnostics(db,user_key,project_id);integrity=source_integrity_assessment(db,user_key,project_id)
    context={"graph":graph,"diagnostics":diag,"integrity":integrity};fp=sha256_hex(context)
    r=InvestigationSourceIntegritySnapshot(user_key=user_key,snapshot_id="source-integrity-snapshot-"+uuid4().hex[:24],project_id=project_id,graph_fingerprint=graph["graphFingerprint"],diagnostics_fingerprint=diag["diagnosticsFingerprint"],integrity_fingerprint=integrity["integrityFingerprint"],snapshot_fingerprint=fp,source_count=graph["sourceCount"],provenance_event_count=graph["provenanceEventCount"],custody_event_count=graph["custodyEventCount"],assertion_count=graph["assertionCount"],binding_count=graph["bindingCount"],issue_count=diag["issueCount"],context_json=context);db.add(r);db.flush();return snapshot_metadata(r)
def snapshot_metadata(r): return {"schema":SOURCE_SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"graphFingerprint":r.graph_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"integrityFingerprint":r.integrity_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"sourceCount":r.source_count,"provenanceEventCount":r.provenance_event_count,"custodyEventCount":r.custody_event_count,"assertionCount":r.assertion_count,"bindingCount":r.binding_count,"issueCount":r.issue_count,"createdAt":iso(r.created_at)}
def list_integrity_snapshots(db,user_key,project_id,limit=100):
    q=select(InvestigationSourceIntegritySnapshot).where(InvestigationSourceIntegritySnapshot.user_key==user_key,InvestigationSourceIntegritySnapshot.project_id==project_id).order_by(InvestigationSourceIntegritySnapshot.created_at.desc()).limit(limit)
    return [snapshot_metadata(x) for x in db.scalars(q).all()]
