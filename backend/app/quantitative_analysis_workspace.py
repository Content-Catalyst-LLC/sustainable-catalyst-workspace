from __future__ import annotations
from collections import Counter
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (
    ProjectHead, QuantitativeReconstructionHead, QuantitativeReconstructionRevision,
    QuantitativeInputBinding, QuantitativeAnalysisHandoff, QuantitativeResultBinding,
    QuantitativeAnalysisSnapshot,
)
from .utils import iso, sha256_hex

QUANT_WORKSPACE_SCHEMA="sc-workspace-quantitative-reconstruction-scientific-analysis-handoffs-workspace/1.0"
RECONSTRUCTION_REQUEST_SCHEMA="sc-workspace-quantitative-reconstruction-request/1.0"
RECONSTRUCTION_SCHEMA="sc-workspace-quantitative-reconstruction/1.0"
INPUT_BINDING_REQUEST_SCHEMA="sc-workspace-quantitative-input-binding-request/1.0"
INPUT_BINDING_SCHEMA="sc-workspace-quantitative-input-binding/1.0"
HANDOFF_REQUEST_SCHEMA="sc-workspace-quantitative-analysis-handoff-request/1.0"
HANDOFF_SCHEMA="sc-workspace-quantitative-analysis-handoff/1.0"
HANDOFF_STATUS_REQUEST_SCHEMA="sc-workspace-quantitative-analysis-handoff-status-request/1.0"
RESULT_BINDING_REQUEST_SCHEMA="sc-workspace-quantitative-result-binding-request/1.0"
RESULT_BINDING_SCHEMA="sc-workspace-quantitative-result-binding/1.0"
ANALYSIS_MANIFEST_SCHEMA="sc-workspace-quantitative-analysis-manifest/1.0"
ANALYSIS_GRAPH_SCHEMA="sc-workspace-quantitative-analysis-graph/1.0"
ANALYSIS_DIAGNOSTICS_SCHEMA="sc-workspace-quantitative-analysis-diagnostics/1.0"
SNAPSHOT_REQUEST_SCHEMA="sc-workspace-quantitative-analysis-snapshot-request/1.0"
SNAPSHOT_SCHEMA="sc-workspace-quantitative-analysis-snapshot/1.0"

METHOD_CLASSES=("descriptive","statistical","simulation","optimization","causal","time-series","spatial","uncertainty","custom")
DESTINATIONS=("workbench","research-lab","catalyst-analytics-r","platform-core")
HANDOFF_STATUSES=("draft","ready","sent","accepted","completed","failed","cancelled")

class QuantitativeReconstructionRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-reconstruction-request/1.0"]
    reconstructionId:str=Field(default="",max_length=160)
    projectId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    objective:str=Field(default="",max_length=8000)
    researchQuestion:str=Field(default="",max_length=8000)
    methodClass:str=Field(default="descriptive")
    assumptions:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    parameters:dict[str,Any]=Field(default_factory=dict)
    expectedRevision:int|None=Field(default=None,ge=0)
    metadata:dict[str,Any]=Field(default_factory=dict)

class QuantitativeInputBindingRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-input-binding-request/1.0"]
    reconstructionId:str=Field(min_length=1,max_length=160)
    inputKind:str=Field(min_length=1,max_length=80)
    objectRef:str=Field(min_length=1,max_length=2000)
    objectFingerprint:str=Field(default="",max_length=128)
    role:str=Field(default="input",max_length=80)
    transformSpec:dict[str,Any]=Field(default_factory=dict)
    note:str=Field(default="",max_length=8000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class QuantitativeAnalysisHandoffRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-analysis-handoff-request/1.0"]
    reconstructionId:str=Field(min_length=1,max_length=160)
    destinationProduct:str
    analysisKind:str=Field(min_length=1,max_length=160)
    requestedOperations:list[str]=Field(default_factory=list,max_length=500)
    environmentRef:str=Field(default="",max_length=1000)
    reproducibilityRequirements:dict[str,Any]=Field(default_factory=dict)
    note:str=Field(default="",max_length=8000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class QuantitativeAnalysisHandoffStatusRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-analysis-handoff-status-request/1.0"]
    status:str
    externalHandoffRef:str=Field(default="",max_length=2000)
    receiptRef:str=Field(default="",max_length=2000)
    note:str=Field(default="",max_length=8000)

class QuantitativeResultBindingRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-result-binding-request/1.0"]
    handoffId:str=Field(min_length=1,max_length=160)
    resultKind:str=Field(min_length=1,max_length=80)
    resultRef:str=Field(min_length=1,max_length=2000)
    resultFingerprint:str=Field(default="",max_length=128)
    status:str=Field(default="reported",max_length=40)
    note:str=Field(default="",max_length=8000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class QuantitativeAnalysisSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-quantitative-analysis-snapshot-request/1.0"]
    includeGraph:bool=True


def profile()->dict[str,Any]:
    return {
      "schema":QUANT_WORKSPACE_SCHEMA,"workspaceVersion":"3.16.0",
      "release":"Quantitative Reconstruction & Scientific Analysis Handoffs",
      "backendAuthoritative":True,"referenceFirst":True,"canonicalEvidenceAuthorityPreserved":True,
      "reproducibleAnalysisHandoffs":True,"supportedDestinations":list(DESTINATIONS),
      "explicitInputFingerprintPinning":True,"humanReviewRequired":True,"immutableAnalysisSnapshots":True,
      "automaticAnalysisExecution":False,"automaticEvidenceTransformation":False,"automaticEvidenceRanking":False,
      "automaticTruthDetermination":False,"automaticCausalityInference":False,"automaticCulpabilityInference":False,
      "coreExecutesSpecialistProvider":False,"workspaceOrchestratesHandoffs":True,
    }

def _project(db,user_key,project_id): return db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
def _reconstruction(db,user_key,reconstruction_id): return db.get(QuantitativeReconstructionHead,{"user_key":user_key,"reconstruction_id":reconstruction_id})
def _handoff(db,user_key,handoff_id): return db.get(QuantitativeAnalysisHandoff,{"user_key":user_key,"handoff_id":handoff_id})

def reconstruction_metadata(r):
    return {"schema":RECONSTRUCTION_SCHEMA,"reconstructionId":r.reconstruction_id,"projectId":r.project_id,"title":r.title,"objective":r.objective,"researchQuestion":r.research_question,"methodClass":r.method_class,"assumptions":r.assumptions_json or [],"parameters":r.parameters_json or {},"revision":r.revision,"reconstructionFingerprint":r.reconstruction_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def store_reconstruction(db:Session,user_key:str,p:QuantitativeReconstructionRequest):
    if not _project(db,user_key,p.projectId): raise KeyError(p.projectId)
    if p.methodClass not in METHOD_CLASSES: raise ValueError("unsupported method class")
    row=_reconstruction(db,user_key,p.reconstructionId) if p.reconstructionId else None
    if row and row.project_id!=p.projectId: raise ValueError("reconstruction project mismatch")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("reconstruction revision conflict")
    rid=p.reconstructionId or "quant-reconstruction-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"reconstructionId":rid,"projectId":p.projectId,"revision":rev,"title":p.title,"objective":p.objective,"researchQuestion":p.researchQuestion,"methodClass":p.methodClass,"assumptions":p.assumptions,"parameters":p.parameters,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,title=p.title,objective=p.objective,research_question=p.researchQuestion,method_class=p.methodClass,assumptions_json=p.assumptions,parameters_json=p.parameters,revision=rev,reconstruction_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=QuantitativeReconstructionHead(user_key=user_key,reconstruction_id=rid,**vals); db.add(row)
    revision_vals=dict(vals); revision_vals.pop("revision",None)
    db.add(QuantitativeReconstructionRevision(user_key=user_key,reconstruction_id=rid,revision=rev,**revision_vals)); db.flush(); return reconstruction_metadata(row)

def list_reconstructions(db,user_key,project_id=None,method_class=None,limit=1000):
    q=select(QuantitativeReconstructionHead).where(QuantitativeReconstructionHead.user_key==user_key)
    if project_id:q=q.where(QuantitativeReconstructionHead.project_id==project_id)
    if method_class:q=q.where(QuantitativeReconstructionHead.method_class==method_class)
    q=q.order_by(QuantitativeReconstructionHead.updated_at.desc()).limit(limit); return [reconstruction_metadata(x) for x in db.scalars(q).all()]

def get_reconstruction(db,user_key,reconstruction_id):
    r=_reconstruction(db,user_key,reconstruction_id); return reconstruction_metadata(r) if r else None

def reconstruction_revisions(db,user_key,reconstruction_id,limit=100):
    q=select(QuantitativeReconstructionRevision).where(QuantitativeReconstructionRevision.user_key==user_key,QuantitativeReconstructionRevision.reconstruction_id==reconstruction_id).order_by(QuantitativeReconstructionRevision.revision.desc()).limit(limit)
    return [{"schema":RECONSTRUCTION_SCHEMA,"reconstructionId":r.reconstruction_id,"projectId":r.project_id,"title":r.title,"objective":r.objective,"researchQuestion":r.research_question,"methodClass":r.method_class,"assumptions":r.assumptions_json or [],"parameters":r.parameters_json or {},"revision":r.revision,"reconstructionFingerprint":r.reconstruction_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)} for r in db.scalars(q).all()]

def create_input_binding(db,user_key,p:QuantitativeInputBindingRequest):
    rec=_reconstruction(db,user_key,p.reconstructionId)
    if rec is None: raise KeyError(p.reconstructionId)
    fp=sha256_hex({"projectId":rec.project_id,"reconstructionId":p.reconstructionId,"inputKind":p.inputKind,"objectRef":p.objectRef,"objectFingerprint":p.objectFingerprint,"role":p.role,"transformSpec":p.transformSpec,"note":p.note,"metadata":p.metadata})
    q=select(QuantitativeInputBinding).where(QuantitativeInputBinding.user_key==user_key,QuantitativeInputBinding.binding_fingerprint==fp)
    existing=db.scalars(q).first()
    if existing:return input_binding_metadata(existing)
    row=QuantitativeInputBinding(user_key=user_key,binding_id="quant-input-"+uuid4().hex[:24],project_id=rec.project_id,reconstruction_id=p.reconstructionId,input_kind=p.inputKind,object_ref=p.objectRef,object_fingerprint=p.objectFingerprint,role=p.role,transform_spec_json=p.transformSpec,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata); db.add(row); db.flush(); return input_binding_metadata(row)

def input_binding_metadata(r): return {"schema":INPUT_BINDING_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"reconstructionId":r.reconstruction_id,"inputKind":r.input_kind,"objectRef":r.object_ref,"objectFingerprint":r.object_fingerprint,"role":r.role,"transformSpec":r.transform_spec_json or {},"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_input_bindings(db,user_key,project_id=None,reconstruction_id=None,limit=1000):
    q=select(QuantitativeInputBinding).where(QuantitativeInputBinding.user_key==user_key)
    if project_id:q=q.where(QuantitativeInputBinding.project_id==project_id)
    if reconstruction_id:q=q.where(QuantitativeInputBinding.reconstruction_id==reconstruction_id)
    q=q.order_by(QuantitativeInputBinding.created_at.asc()).limit(limit); return [input_binding_metadata(x) for x in db.scalars(q).all()]

def create_analysis_handoff(db,user_key,p:QuantitativeAnalysisHandoffRequest):
    rec=_reconstruction(db,user_key,p.reconstructionId)
    if rec is None: raise KeyError(p.reconstructionId)
    if p.destinationProduct not in DESTINATIONS: raise ValueError("unsupported destination product")
    inputs=list_input_bindings(db,user_key,rec.project_id,p.reconstructionId,5000)
    package={"reconstruction":reconstruction_metadata(rec),"inputs":inputs,"analysisKind":p.analysisKind,"requestedOperations":p.requestedOperations,"environmentRef":p.environmentRef,"reproducibilityRequirements":p.reproducibilityRequirements}
    fp=sha256_hex(package)
    row=QuantitativeAnalysisHandoff(user_key=user_key,handoff_id="quant-handoff-"+uuid4().hex[:24],project_id=rec.project_id,reconstruction_id=p.reconstructionId,destination_product=p.destinationProduct,analysis_kind=p.analysisKind,requested_operations_json=p.requestedOperations,environment_ref=p.environmentRef,reproducibility_requirements_json=p.reproducibilityRequirements,status="ready",package_fingerprint=fp,external_handoff_ref="",receipt_ref="",note=p.note,metadata_json=p.metadata); db.add(row); db.flush(); return handoff_metadata(row)

def handoff_metadata(r): return {"schema":HANDOFF_SCHEMA,"handoffId":r.handoff_id,"projectId":r.project_id,"reconstructionId":r.reconstruction_id,"destinationProduct":r.destination_product,"analysisKind":r.analysis_kind,"requestedOperations":r.requested_operations_json or [],"environmentRef":r.environment_ref,"reproducibilityRequirements":r.reproducibility_requirements_json or {},"status":r.status,"packageFingerprint":r.package_fingerprint,"externalHandoffRef":r.external_handoff_ref,"receiptRef":r.receipt_ref,"note":r.note,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def list_analysis_handoffs(db,user_key,project_id=None,reconstruction_id=None,destination_product=None,limit=1000):
    q=select(QuantitativeAnalysisHandoff).where(QuantitativeAnalysisHandoff.user_key==user_key)
    if project_id:q=q.where(QuantitativeAnalysisHandoff.project_id==project_id)
    if reconstruction_id:q=q.where(QuantitativeAnalysisHandoff.reconstruction_id==reconstruction_id)
    if destination_product:q=q.where(QuantitativeAnalysisHandoff.destination_product==destination_product)
    q=q.order_by(QuantitativeAnalysisHandoff.created_at.desc()).limit(limit); return [handoff_metadata(x) for x in db.scalars(q).all()]

def get_analysis_handoff(db,user_key,handoff_id):
    r=_handoff(db,user_key,handoff_id); return handoff_metadata(r) if r else None

def update_analysis_handoff_status(db,user_key,handoff_id,p:QuantitativeAnalysisHandoffStatusRequest):
    row=_handoff(db,user_key,handoff_id)
    if row is None: raise KeyError(handoff_id)
    if p.status not in HANDOFF_STATUSES: raise ValueError("unsupported handoff status")
    row.status=p.status; row.external_handoff_ref=p.externalHandoffRef; row.receipt_ref=p.receiptRef; row.note=p.note or row.note; db.flush(); return handoff_metadata(row)

def create_result_binding(db,user_key,p:QuantitativeResultBindingRequest):
    h=_handoff(db,user_key,p.handoffId)
    if h is None: raise KeyError(p.handoffId)
    fp=sha256_hex({"handoffId":p.handoffId,"resultKind":p.resultKind,"resultRef":p.resultRef,"resultFingerprint":p.resultFingerprint,"status":p.status,"note":p.note,"metadata":p.metadata})
    q=select(QuantitativeResultBinding).where(QuantitativeResultBinding.user_key==user_key,QuantitativeResultBinding.binding_fingerprint==fp)
    existing=db.scalars(q).first()
    if existing:return result_binding_metadata(existing)
    row=QuantitativeResultBinding(user_key=user_key,binding_id="quant-result-"+uuid4().hex[:24],project_id=h.project_id,handoff_id=p.handoffId,reconstruction_id=h.reconstruction_id,result_kind=p.resultKind,result_ref=p.resultRef,result_fingerprint=p.resultFingerprint,status=p.status,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata); db.add(row); db.flush(); return result_binding_metadata(row)

def result_binding_metadata(r): return {"schema":RESULT_BINDING_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"handoffId":r.handoff_id,"reconstructionId":r.reconstruction_id,"resultKind":r.result_kind,"resultRef":r.result_ref,"resultFingerprint":r.result_fingerprint,"status":r.status,"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_result_bindings(db,user_key,project_id=None,handoff_id=None,reconstruction_id=None,limit=1000):
    q=select(QuantitativeResultBinding).where(QuantitativeResultBinding.user_key==user_key)
    if project_id:q=q.where(QuantitativeResultBinding.project_id==project_id)
    if handoff_id:q=q.where(QuantitativeResultBinding.handoff_id==handoff_id)
    if reconstruction_id:q=q.where(QuantitativeResultBinding.reconstruction_id==reconstruction_id)
    q=q.order_by(QuantitativeResultBinding.created_at.asc()).limit(limit); return [result_binding_metadata(x) for x in db.scalars(q).all()]

def analysis_manifest(db,user_key,project_id):
    if not _project(db,user_key,project_id): raise KeyError(project_id)
    recs=list_reconstructions(db,user_key,project_id,None,5000); inputs=list_input_bindings(db,user_key,project_id,None,5000); handoffs=list_analysis_handoffs(db,user_key,project_id,None,None,5000); results=list_result_bindings(db,user_key,project_id,None,None,5000)
    counts={"reconstructions":len(recs),"inputBindings":len(inputs),"handoffs":len(handoffs),"resultBindings":len(results)}
    payload={"schema":ANALYSIS_MANIFEST_SCHEMA,"projectId":project_id,"counts":counts,"reconstructions":recs,"inputBindings":inputs,"handoffs":handoffs,"resultBindings":results,"canonicalEvidenceAuthorityPreserved":True,"automaticAnalysisExecution":False}
    payload["manifestFingerprint"]=sha256_hex(payload); return payload

def analysis_graph(db,user_key,project_id):
    m=analysis_manifest(db,user_key,project_id); nodes=[]; edges=[]
    for r in m["reconstructions"]: nodes.append({"id":"reconstruction:"+r["reconstructionId"],"kind":"quantitative-reconstruction","label":r["title"],"projectId":project_id,"fingerprint":r["reconstructionFingerprint"]})
    for b in m["inputBindings"]:
        rid="reconstruction:"+b["reconstructionId"]; oid=b["objectRef"]
        nodes.append({"id":oid,"kind":b["inputKind"],"label":oid,"externalCanonicalReference":True,"objectFingerprint":b["objectFingerprint"]})
        edges.append({"id":"input-edge:"+b["bindingId"],"kind":"analysis-input","from":oid,"to":rid,"bindingFingerprint":b["bindingFingerprint"]})
    for h in m["handoffs"]:
        hid="handoff:"+h["handoffId"]; nodes.append({"id":hid,"kind":"analysis-handoff","label":h["destinationProduct"]+": "+h["analysisKind"],"status":h["status"],"fingerprint":h["packageFingerprint"]}); edges.append({"id":"handoff-edge:"+h["handoffId"],"kind":"analysis-handoff","from":"reconstruction:"+h["reconstructionId"],"to":hid})
    for b in m["resultBindings"]:
        rid=b["resultRef"]; nodes.append({"id":rid,"kind":b["resultKind"],"label":rid,"externalCanonicalReference":True,"resultFingerprint":b["resultFingerprint"]}); edges.append({"id":"result-edge:"+b["bindingId"],"kind":"analysis-result","from":"handoff:"+b["handoffId"],"to":rid,"bindingFingerprint":b["bindingFingerprint"]})
    # deterministic dedupe
    seen=set(); nodes=[x for x in nodes if not (x["id"] in seen or seen.add(x["id"]))]
    payload={"schema":ANALYSIS_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"automaticRelationshipInference":False,"automaticCausalityInference":False}; payload["graphFingerprint"]=sha256_hex(payload); return payload

def diagnostics(db,user_key,project_id):
    m=analysis_manifest(db,user_key,project_id); issues=[]
    input_counts=Counter(x["reconstructionId"] for x in m["inputBindings"]); handoff_counts=Counter(x["reconstructionId"] for x in m["handoffs"]); result_counts=Counter(x["handoffId"] for x in m["resultBindings"])
    for r in m["reconstructions"]:
        rid=r["reconstructionId"]
        if input_counts.get(rid,0)==0: issues.append({"code":"quantitative-reconstruction-no-inputs","severity":"review","reconstructionId":rid,"message":"No source/evidence inputs are bound to this reconstruction."})
        if handoff_counts.get(rid,0)==0: issues.append({"code":"quantitative-reconstruction-no-handoff","severity":"info","reconstructionId":rid,"message":"No specialist analysis handoff has been created."})
    for h in m["handoffs"]:
        if h["status"]=="completed" and result_counts.get(h["handoffId"],0)==0: issues.append({"code":"completed-handoff-no-result-binding","severity":"review","handoffId":h["handoffId"],"message":"Handoff is marked completed but has no returned result reference."})
    payload={"schema":ANALYSIS_DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"automaticResolution":False,"automaticEvidenceRanking":False,"automaticTruthDetermination":False}; payload["diagnosticsFingerprint"]=sha256_hex(payload); return payload

def create_snapshot(db,user_key,project_id,p:QuantitativeAnalysisSnapshotRequest):
    m=analysis_manifest(db,user_key,project_id); d=diagnostics(db,user_key,project_id); g=analysis_graph(db,user_key,project_id) if p.includeGraph else None
    ctx={"manifest":m,"diagnostics":d,"graph":g}; fp=sha256_hex(ctx)
    row=QuantitativeAnalysisSnapshot(user_key=user_key,snapshot_id="quant-snapshot-"+uuid4().hex[:24],project_id=project_id,manifest_fingerprint=m["manifestFingerprint"],diagnostics_fingerprint=d["diagnosticsFingerprint"],graph_fingerprint=(g or {}).get("graphFingerprint",""),snapshot_fingerprint=fp,reconstruction_count=m["counts"]["reconstructions"],input_binding_count=m["counts"]["inputBindings"],handoff_count=m["counts"]["handoffs"],result_binding_count=m["counts"]["resultBindings"],issue_count=d["issueCount"],context_json=ctx); db.add(row); db.flush(); return snapshot_metadata(row)

def snapshot_metadata(r): return {"schema":SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"manifestFingerprint":r.manifest_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"graphFingerprint":r.graph_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"reconstructionCount":r.reconstruction_count,"inputBindingCount":r.input_binding_count,"handoffCount":r.handoff_count,"resultBindingCount":r.result_binding_count,"issueCount":r.issue_count,"createdAt":iso(r.created_at)}

def list_snapshots(db,user_key,project_id,limit=100):
    q=select(QuantitativeAnalysisSnapshot).where(QuantitativeAnalysisSnapshot.user_key==user_key,QuantitativeAnalysisSnapshot.project_id==project_id).order_by(QuantitativeAnalysisSnapshot.created_at.desc()).limit(limit); return [snapshot_metadata(x) for x in db.scalars(q).all()]
