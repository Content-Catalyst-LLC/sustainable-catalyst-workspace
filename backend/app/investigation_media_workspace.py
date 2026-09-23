from __future__ import annotations
from collections import defaultdict
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (ProjectHead, InvestigationMediaArtifactHead, InvestigationMediaArtifactRevision,
    InvestigationMediaLocator, InvestigationMediaDerivative, InvestigationMediaContextLink,
    InvestigationMediaRelation, InvestigationMediaSnapshot)
from .investigation_spatial_workspace import build_spatial_graph
from .utils import iso, sha256_hex

MEDIA_WORKSPACE_SCHEMA="sc-workspace-media-artifact-derivative-provenance-workspace/1.0"
MEDIA_ARTIFACT_SCHEMA="sc-workspace-investigation-media-artifact/1.0"
MEDIA_ARTIFACT_REQUEST_SCHEMA="sc-workspace-investigation-media-artifact-request/1.0"
MEDIA_LOCATOR_REQUEST_SCHEMA="sc-workspace-investigation-media-locator-request/1.0"
MEDIA_DERIVATIVE_REQUEST_SCHEMA="sc-workspace-investigation-media-derivative-request/1.0"
MEDIA_CONTEXT_LINK_REQUEST_SCHEMA="sc-workspace-investigation-media-context-link-request/1.0"
MEDIA_RELATION_REQUEST_SCHEMA="sc-workspace-investigation-media-relation-request/1.0"
MEDIA_GRAPH_SCHEMA="sc-workspace-investigation-media-provenance-graph/1.0"
MEDIA_DIAGNOSTICS_SCHEMA="sc-workspace-investigation-media-diagnostics/1.0"
MEDIA_INTEGRITY_SCHEMA="sc-workspace-investigation-media-integrity/1.0"
MEDIA_SNAPSHOT_REQUEST_SCHEMA="sc-workspace-investigation-media-snapshot-request/1.0"
MEDIA_SNAPSHOT_SCHEMA="sc-workspace-investigation-media-snapshot/1.0"
MEDIA_TYPES=("image","video","audio","animation","document-scan","screen-capture","sensor-media","other")
HASH_ALGORITHMS=("sha256","sha512","blake3","other")
LOCATOR_TYPES=("frame","timecode","time-range","region","pixel-region","track-segment","whole-artifact","other")
TRANSFORMATION_TYPES=("transcode","resize","crop","clip","extract-frame","annotate","stabilize","color-adjust","denoise","redact","composite","metadata-only","other")
TARGET_KINDS=("entity","event","document","excerpt","testimony","statement","evidence-ref","spatial-observation","scientific-object-ref")
CONTEXT_RELATIONS=("depicts","records","mentions","captured-at","associated-with","supports","contradicts","contextualizes","source-of","related-to")
MEDIA_RELATIONS=("same-content-hash","alternate-encoding","near-duplicate-asserted","sequence-related","same-source-asserted","contradicts","corroborates","related-to")
REVIEW_STATES=("open","under-review","documented","contested","unresolved","closed")

class InvestigationMediaArtifactRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-media-artifact-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); artifactId:str=Field(default="",max_length=160)
    mediaType:Literal["image","video","audio","animation","document-scan","screen-capture","sensor-media","other"]
    title:str=Field(min_length=1,max_length=1000); sourceRef:str=Field(min_length=1,max_length=2000); sourceFingerprint:str=Field(min_length=8,max_length=128)
    contentHashAlgorithm:Literal["sha256","sha512","blake3","other"]="sha256"; contentHash:str=Field(min_length=8,max_length=256)
    mimeType:str=Field(default="",max_length=160); originalFilename:str=Field(default="",max_length=1000); capturedAt:str=Field(default="",max_length=64)
    durationSeconds:str=Field(default="",max_length=64); reviewState:Literal["open","under-review","documented","contested","unresolved","closed"]="open"
    expectedRevision:int|None=Field(default=None,ge=0); metadata:dict[str,Any]=Field(default_factory=dict)

class InvestigationMediaLocatorRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-media-locator-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); artifactId:str=Field(min_length=1,max_length=160)
    locatorType:Literal["frame","timecode","time-range","region","pixel-region","track-segment","whole-artifact","other"]
    locator:dict[str,Any]=Field(default_factory=dict); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def locator_required(self):
        if self.locatorType!="whole-artifact" and not self.locator: raise ValueError("media locator payload required")
        return self

class InvestigationMediaDerivativeRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-media-derivative-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); parentArtifactId:str=Field(min_length=1,max_length=160); childArtifactId:str=Field(min_length=1,max_length=160)
    transformationType:Literal["transcode","resize","crop","clip","extract-frame","annotate","stabilize","color-adjust","denoise","redact","composite","metadata-only","other"]
    parameters:dict[str,Any]=Field(default_factory=dict); toolRef:str=Field(default="",max_length=1000); operationRef:str=Field(default="",max_length=1000)
    sourceFingerprint:str=Field(default="",max_length=128); metadata:dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.parentArtifactId==self.childArtifactId: raise ValueError("media derivative endpoints must differ")
        return self

class InvestigationMediaContextLinkRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-media-context-link-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); artifactId:str=Field(min_length=1,max_length=160)
    targetKind:Literal["entity","event","document","excerpt","testimony","statement","evidence-ref","spatial-observation","scientific-object-ref"]
    targetRef:str=Field(min_length=1,max_length=2000); relation:Literal["depicts","records","mentions","captured-at","associated-with","supports","contradicts","contextualizes","source-of","related-to"]
    locatorId:str=Field(default="",max_length=96); sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)

class InvestigationMediaRelationRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-media-relation-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); fromArtifactId:str=Field(min_length=1,max_length=160); toArtifactId:str=Field(min_length=1,max_length=160)
    relation:Literal["same-content-hash","alternate-encoding","near-duplicate-asserted","sequence-related","same-source-asserted","contradicts","corroborates","related-to"]
    sourceRef:str=Field(default="",max_length=2000); sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.fromArtifactId==self.toArtifactId: raise ValueError("media relation endpoints must differ")
        return self

class InvestigationMediaSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-media-snapshot-request/1.0"]
    includeSpatialGraph:bool=True

def profile()->dict[str,Any]:
    return {"schema":MEDIA_WORKSPACE_SCHEMA,"workspaceVersion":"3.13.0","release":"Media Artifact, Image, Video & Derivative Provenance Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"binaryMediaStorage":False,"versionedMediaArtifacts":True,"contentHashRequired":True,
      "locatorPreservingReferences":True,"explicitDerivativeLineage":True,"humanAssertedContextLinks":True,"humanAssertedMediaRelations":True,
      "spatialGraphOverlay":True,"immutableMediaSnapshots":True,"automaticMediaSimilarityMatching":False,"automaticDerivativeInference":False,
      "automaticAuthenticityDetermination":False,"automaticIdentityInference":False,"automaticCausalityInference":False,"automaticTruthDetermination":False,
      "automaticEvidenceRanking":False,"automaticCulpabilityInference":False,"automaticNarrativeSelection":False,
      "supportedMediaTypes":list(MEDIA_TYPES),"supportedLocatorTypes":list(LOCATOR_TYPES),"supportedTransformations":list(TRANSFORMATION_TYPES)}

def _project(db,user_key,project_id):
    r=db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
    if r is None: raise KeyError(project_id)
    return r

def _artifact(db,user_key,artifact_id): return db.get(InvestigationMediaArtifactHead,{"user_key":user_key,"artifact_id":artifact_id})
def artifact_metadata(r):
    return {"schema":MEDIA_ARTIFACT_SCHEMA,"artifactId":r.artifact_id,"projectId":r.project_id,"mediaType":r.media_type,"title":r.title,
      "sourceRef":r.source_ref,"sourceFingerprint":r.source_fingerprint,"contentHashAlgorithm":r.content_hash_algorithm,"contentHash":r.content_hash,
      "mimeType":r.mime_type,"originalFilename":r.original_filename,"capturedAt":r.captured_at,"durationSeconds":r.duration_seconds,
      "reviewState":r.review_state,"revision":r.revision,"artifactFingerprint":r.artifact_fingerprint,"metadata":r.metadata_json or {},
      "createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}
def revision_metadata(r):
    x=artifact_metadata(r); x["createdAt"]=iso(r.created_at); x.pop("updatedAt",None); return x

def store_artifact(db:Session,user_key:str,p:InvestigationMediaArtifactRequest):
    _project(db,user_key,p.projectId); row=_artifact(db,user_key,p.artifactId) if p.artifactId else None
    if row and row.project_id!=p.projectId: raise ValueError("media artifact belongs to another project")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("media artifact revision conflict")
    aid=p.artifactId or "media-artifact-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"projectId":p.projectId,"artifactId":aid,"revision":rev,"mediaType":p.mediaType,"title":p.title,"sourceRef":p.sourceRef,
      "sourceFingerprint":p.sourceFingerprint,"contentHashAlgorithm":p.contentHashAlgorithm,"contentHash":p.contentHash,"mimeType":p.mimeType,
      "originalFilename":p.originalFilename,"capturedAt":p.capturedAt,"durationSeconds":p.durationSeconds,"reviewState":p.reviewState,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,media_type=p.mediaType,title=p.title,source_ref=p.sourceRef,source_fingerprint=p.sourceFingerprint,
      content_hash_algorithm=p.contentHashAlgorithm,content_hash=p.contentHash,mime_type=p.mimeType,original_filename=p.originalFilename,
      captured_at=p.capturedAt,duration_seconds=p.durationSeconds,review_state=p.reviewState,revision=rev,artifact_fingerprint=fp,metadata_json=p.metadata)
    if row is None:
        row=InvestigationMediaArtifactHead(user_key=user_key,artifact_id=aid,**vals); db.add(row)
    else:
        for k,v in vals.items(): setattr(row,k,v)
    db.add(InvestigationMediaArtifactRevision(user_key=user_key,artifact_id=aid,**vals)); db.flush(); return artifact_metadata(row)

def list_artifacts(db,user_key,project_id=None,media_type=None,limit=1000):
    q=select(InvestigationMediaArtifactHead).where(InvestigationMediaArtifactHead.user_key==user_key)
    if project_id:q=q.where(InvestigationMediaArtifactHead.project_id==project_id)
    if media_type:q=q.where(InvestigationMediaArtifactHead.media_type==media_type)
    return [artifact_metadata(x) for x in db.scalars(q.order_by(InvestigationMediaArtifactHead.created_at.desc()).limit(limit)).all()]
def get_artifact(db,user_key,artifact_id):
    r=_artifact(db,user_key,artifact_id); return artifact_metadata(r) if r else None
def artifact_revisions(db,user_key,artifact_id,limit=100):
    q=select(InvestigationMediaArtifactRevision).where(InvestigationMediaArtifactRevision.user_key==user_key,InvestigationMediaArtifactRevision.artifact_id==artifact_id).order_by(InvestigationMediaArtifactRevision.revision.desc()).limit(limit)
    return [revision_metadata(x) for x in db.scalars(q).all()]

def _idempotent(db,model,user_key,field,fp):
    q=select(model).where(model.user_key==user_key,getattr(model,field)==fp); return db.scalars(q).first()
def create_locator(db,user_key,p:InvestigationMediaLocatorRequest):
    a=_artifact(db,user_key,p.artifactId)
    if not a or a.project_id!=p.projectId: raise ValueError("media artifact not found in project")
    fp=sha256_hex({"projectId":p.projectId,"artifactId":p.artifactId,"locatorType":p.locatorType,"locator":p.locator,"note":p.note,"metadata":p.metadata})
    old=_idempotent(db,InvestigationMediaLocator,user_key,"locator_fingerprint",fp)
    if old:return locator_metadata(old)
    row=InvestigationMediaLocator(user_key=user_key,locator_id="media-locator-"+uuid4().hex[:20],project_id=p.projectId,artifact_id=p.artifactId,locator_type=p.locatorType,locator_json=p.locator,note=p.note,locator_fingerprint=fp,metadata_json=p.metadata); db.add(row);db.flush();return locator_metadata(row)
def locator_metadata(r): return {"locatorId":r.locator_id,"projectId":r.project_id,"artifactId":r.artifact_id,"locatorType":r.locator_type,"locator":r.locator_json or {},"note":r.note,"locatorFingerprint":r.locator_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_locators(db,user_key,project_id=None,artifact_id=None,limit=2000):
    q=select(InvestigationMediaLocator).where(InvestigationMediaLocator.user_key==user_key)
    if project_id:q=q.where(InvestigationMediaLocator.project_id==project_id)
    if artifact_id:q=q.where(InvestigationMediaLocator.artifact_id==artifact_id)
    return [locator_metadata(x) for x in db.scalars(q.order_by(InvestigationMediaLocator.created_at.desc()).limit(limit)).all()]

def create_derivative(db,user_key,p:InvestigationMediaDerivativeRequest):
    parent=_artifact(db,user_key,p.parentArtifactId); child=_artifact(db,user_key,p.childArtifactId)
    if not parent or not child or parent.project_id!=p.projectId or child.project_id!=p.projectId: raise ValueError("media derivative artifacts must belong to project")
    fp=sha256_hex({"projectId":p.projectId,"parent":p.parentArtifactId,"child":p.childArtifactId,"transformation":p.transformationType,"parameters":p.parameters,"toolRef":p.toolRef,"operationRef":p.operationRef,"sourceFingerprint":p.sourceFingerprint,"metadata":p.metadata})
    old=_idempotent(db,InvestigationMediaDerivative,user_key,"derivative_fingerprint",fp)
    if old:return derivative_metadata(old)
    row=InvestigationMediaDerivative(user_key=user_key,derivative_id="media-derivative-"+uuid4().hex[:20],project_id=p.projectId,parent_artifact_id=p.parentArtifactId,child_artifact_id=p.childArtifactId,transformation_type=p.transformationType,parameters_json=p.parameters,tool_ref=p.toolRef,operation_ref=p.operationRef,source_fingerprint=p.sourceFingerprint,derivative_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return derivative_metadata(row)
def derivative_metadata(r): return {"derivativeId":r.derivative_id,"projectId":r.project_id,"parentArtifactId":r.parent_artifact_id,"childArtifactId":r.child_artifact_id,"transformationType":r.transformation_type,"parameters":r.parameters_json or {},"toolRef":r.tool_ref,"operationRef":r.operation_ref,"sourceFingerprint":r.source_fingerprint,"derivativeFingerprint":r.derivative_fingerprint,"humanAsserted":True,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_derivatives(db,user_key,project_id=None,artifact_id=None,limit=2000):
    q=select(InvestigationMediaDerivative).where(InvestigationMediaDerivative.user_key==user_key)
    if project_id:q=q.where(InvestigationMediaDerivative.project_id==project_id)
    if artifact_id:q=q.where((InvestigationMediaDerivative.parent_artifact_id==artifact_id)|(InvestigationMediaDerivative.child_artifact_id==artifact_id))
    return [derivative_metadata(x) for x in db.scalars(q.order_by(InvestigationMediaDerivative.created_at.desc()).limit(limit)).all()]

def create_context_link(db,user_key,p:InvestigationMediaContextLinkRequest):
    a=_artifact(db,user_key,p.artifactId)
    if not a or a.project_id!=p.projectId: raise ValueError("media artifact not found in project")
    if p.locatorId:
        loc=db.get(InvestigationMediaLocator,{"user_key":user_key,"locator_id":p.locatorId})
        if not loc or loc.project_id!=p.projectId or loc.artifact_id!=p.artifactId: raise ValueError("media locator not found for artifact")
    fp=sha256_hex({"projectId":p.projectId,"artifactId":p.artifactId,"targetKind":p.targetKind,"targetRef":p.targetRef,"relation":p.relation,"locatorId":p.locatorId,"sourceFingerprint":p.sourceFingerprint,"note":p.note,"metadata":p.metadata})
    old=_idempotent(db,InvestigationMediaContextLink,user_key,"link_fingerprint",fp)
    if old:return context_link_metadata(old)
    row=InvestigationMediaContextLink(user_key=user_key,link_id="media-link-"+uuid4().hex[:20],project_id=p.projectId,artifact_id=p.artifactId,target_kind=p.targetKind,target_ref=p.targetRef,relation=p.relation,locator_id=p.locatorId,source_fingerprint=p.sourceFingerprint,note=p.note,link_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return context_link_metadata(row)
def context_link_metadata(r): return {"linkId":r.link_id,"projectId":r.project_id,"artifactId":r.artifact_id,"targetKind":r.target_kind,"targetRef":r.target_ref,"relation":r.relation,"locatorId":r.locator_id,"sourceFingerprint":r.source_fingerprint,"note":r.note,"linkFingerprint":r.link_fingerprint,"humanAsserted":True,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_context_links(db,user_key,project_id=None,artifact_id=None,target_ref=None,limit=3000):
    q=select(InvestigationMediaContextLink).where(InvestigationMediaContextLink.user_key==user_key)
    if project_id:q=q.where(InvestigationMediaContextLink.project_id==project_id)
    if artifact_id:q=q.where(InvestigationMediaContextLink.artifact_id==artifact_id)
    if target_ref:q=q.where(InvestigationMediaContextLink.target_ref==target_ref)
    return [context_link_metadata(x) for x in db.scalars(q.order_by(InvestigationMediaContextLink.created_at.desc()).limit(limit)).all()]

def create_media_relation(db,user_key,p:InvestigationMediaRelationRequest):
    a=_artifact(db,user_key,p.fromArtifactId); b=_artifact(db,user_key,p.toArtifactId)
    if not a or not b or a.project_id!=p.projectId or b.project_id!=p.projectId: raise ValueError("media relation artifacts must belong to project")
    fp=sha256_hex({"projectId":p.projectId,"from":p.fromArtifactId,"to":p.toArtifactId,"relation":p.relation,"sourceRef":p.sourceRef,"sourceFingerprint":p.sourceFingerprint,"note":p.note,"metadata":p.metadata})
    old=_idempotent(db,InvestigationMediaRelation,user_key,"relation_fingerprint",fp)
    if old:return relation_metadata(old)
    row=InvestigationMediaRelation(user_key=user_key,relation_id="media-relation-"+uuid4().hex[:20],project_id=p.projectId,from_artifact_id=p.fromArtifactId,to_artifact_id=p.toArtifactId,relation=p.relation,source_ref=p.sourceRef,source_fingerprint=p.sourceFingerprint,note=p.note,relation_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return relation_metadata(row)
def relation_metadata(r): return {"relationId":r.relation_id,"projectId":r.project_id,"fromArtifactId":r.from_artifact_id,"toArtifactId":r.to_artifact_id,"relation":r.relation,"sourceRef":r.source_ref,"sourceFingerprint":r.source_fingerprint,"note":r.note,"relationFingerprint":r.relation_fingerprint,"humanAsserted":True,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_media_relations(db,user_key,project_id=None,artifact_id=None,limit=3000):
    q=select(InvestigationMediaRelation).where(InvestigationMediaRelation.user_key==user_key)
    if project_id:q=q.where(InvestigationMediaRelation.project_id==project_id)
    if artifact_id:q=q.where((InvestigationMediaRelation.from_artifact_id==artifact_id)|(InvestigationMediaRelation.to_artifact_id==artifact_id))
    return [relation_metadata(x) for x in db.scalars(q.order_by(InvestigationMediaRelation.created_at.desc()).limit(limit)).all()]

def build_media_graph(db,user_key,project_id,include_spatial_graph=True):
    _project(db,user_key,project_id)
    base=build_spatial_graph(db,user_key,project_id,False) if include_spatial_graph else {"nodes":[],"edges":[],"graphFingerprint":""}
    artifacts=list_artifacts(db,user_key,project_id,None,5000); locators=list_locators(db,user_key,project_id,None,10000); derivatives=list_derivatives(db,user_key,project_id,None,10000); links=list_context_links(db,user_key,project_id,None,None,10000); relations=list_media_relations(db,user_key,project_id,None,10000)
    nodes=list(base.get("nodes") or []); edges=list(base.get("edges") or [])
    seen={str(n.get("id")) for n in nodes}
    for a in artifacts:
        nid="media:"+a["artifactId"]
        if nid not in seen: nodes.append({"id":nid,"kind":"media-artifact","label":a["title"],"mediaType":a["mediaType"],"contentHashAlgorithm":a["contentHashAlgorithm"],"contentHash":a["contentHash"],"reviewState":a["reviewState"],"sourceRef":a["sourceRef"]});seen.add(nid)
    for l in locators:
        nid="media-locator:"+l["locatorId"]; nodes.append({"id":nid,"kind":"media-locator","label":l["locatorType"],"locator":l["locator"]}); edges.append({"from":"media:"+l["artifactId"],"to":nid,"relation":"has-locator","humanAsserted":True})
    for d in derivatives: edges.append({"from":"media:"+d["parentArtifactId"],"to":"media:"+d["childArtifactId"],"relation":"derived-by:"+d["transformationType"],"humanAsserted":True,"derivativeId":d["derivativeId"]})
    for l in links: edges.append({"from":"media:"+l["artifactId"],"to":l["targetKind"]+":"+l["targetRef"],"relation":l["relation"],"humanAsserted":True,"locatorId":l["locatorId"]})
    for r in relations: edges.append({"from":"media:"+r["fromArtifactId"],"to":"media:"+r["toArtifactId"],"relation":r["relation"],"humanAsserted":True})
    payload={"schema":MEDIA_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"artifactCount":len(artifacts),"locatorCount":len(locators),"derivativeCount":len(derivatives),"contextLinkCount":len(links),"relationCount":len(relations),"spatialGraphIncluded":include_spatial_graph,"automaticSimilarityMatching":False,"automaticAuthenticityDetermination":False}
    payload["graphFingerprint"]=sha256_hex(payload); return payload

def media_integrity(db,user_key,project_id):
    arts=list_artifacts(db,user_key,project_id,None,5000); derivatives=list_derivatives(db,user_key,project_id,None,10000)
    hashes=defaultdict(list)
    for a in arts: hashes[(a["contentHashAlgorithm"],a["contentHash"])].append(a["artifactId"])
    groups=[{"contentHashAlgorithm":k[0],"contentHash":k[1],"artifactIds":v,"count":len(v),"classification":"matching-content-hash-review"} for k,v in sorted(hashes.items()) if len(v)>1]
    payload={"schema":MEDIA_INTEGRITY_SCHEMA,"projectId":project_id,"artifactCount":len(arts),"derivativeCount":len(derivatives),"hashedArtifactCount":sum(1 for a in arts if a["contentHash"]),"matchingHashGroups":groups,"matchingHashGroupCount":len(groups),"automaticDuplicateDetermination":False,"automaticAuthenticityDetermination":False,"automaticTamperDetermination":False,"humanReviewRequired":True}
    payload["integrityFingerprint"]=sha256_hex(payload); return payload

def media_diagnostics(db,user_key,project_id):
    arts=list_artifacts(db,user_key,project_id,None,5000); locs=list_locators(db,user_key,project_id,None,10000); derivatives=list_derivatives(db,user_key,project_id,None,10000)
    issues=[]; by_id={a["artifactId"]:a for a in arts}
    for a in arts:
        if a["reviewState"] in ("contested","unresolved"): issues.append({"diagnosticId":"media-review-"+a["artifactId"],"severity":"review","artifactId":a["artifactId"],"basis":"artifact review state is "+a["reviewState"],"automaticResolution":False})
    for l in locs:
        a=by_id.get(l["artifactId"]); data=l.get("locator") or {}
        if a and a.get("durationSeconds"):
            try:
                dur=float(a["durationSeconds"]); candidates=[data.get("seconds"),data.get("startSeconds"),data.get("endSeconds")]
                if any(v is not None and float(v)>dur for v in candidates): issues.append({"diagnosticId":"media-locator-range-"+l["locatorId"],"severity":"review","artifactId":l["artifactId"],"locatorId":l["locatorId"],"basis":"locator exceeds recorded artifact duration","automaticResolution":False})
            except (TypeError,ValueError): pass
    graph=defaultdict(list)
    for d in derivatives: graph[d["parentArtifactId"]].append(d["childArtifactId"])
    def has_cycle(start):
        stack=[(start,{start})]
        while stack:
            node,path=stack.pop()
            for nxt in graph.get(node,[]):
                if nxt==start:return True
                if nxt not in path: stack.append((nxt,path|{nxt}))
        return False
    cyc=sorted({a for a in graph if has_cycle(a)})
    if cyc: issues.append({"diagnosticId":"media-derivative-cycle","severity":"review","artifactIds":cyc,"basis":"explicit derivative lineage contains a cycle","automaticResolution":False})
    integ=media_integrity(db,user_key,project_id)
    for g in integ["matchingHashGroups"]: issues.append({"diagnosticId":"media-matching-hash-"+sha256_hex(g)[:16],"severity":"review","artifactIds":g["artifactIds"],"basis":"multiple artifacts share a recorded content hash; identity is not inferred","automaticResolution":False})
    payload={"schema":MEDIA_DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"automaticResolution":False,"automaticAuthenticityDetermination":False,"automaticNarrativeSelection":False,"automaticTruthDetermination":False}
    payload["diagnosticsFingerprint"]=sha256_hex(payload); return payload

def create_media_snapshot(db,user_key,project_id,p:InvestigationMediaSnapshotRequest):
    graph=build_media_graph(db,user_key,project_id,p.includeSpatialGraph); diagnostics=media_diagnostics(db,user_key,project_id); integrity=media_integrity(db,user_key,project_id)
    context={"graph":graph,"diagnostics":diagnostics,"integrity":integrity}; fp=sha256_hex(context)
    row=InvestigationMediaSnapshot(user_key=user_key,snapshot_id="media-snapshot-"+uuid4().hex[:20],project_id=project_id,graph_fingerprint=graph["graphFingerprint"],diagnostics_fingerprint=diagnostics["diagnosticsFingerprint"],integrity_fingerprint=integrity["integrityFingerprint"],snapshot_fingerprint=fp,artifact_count=graph["artifactCount"],locator_count=graph["locatorCount"],derivative_count=graph["derivativeCount"],context_link_count=graph["contextLinkCount"],relation_count=graph["relationCount"],issue_count=diagnostics["issueCount"],context_json=context);db.add(row);db.flush();return snapshot_metadata(row)
def snapshot_metadata(r): return {"schema":MEDIA_SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"graphFingerprint":r.graph_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"integrityFingerprint":r.integrity_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"artifactCount":r.artifact_count,"locatorCount":r.locator_count,"derivativeCount":r.derivative_count,"contextLinkCount":r.context_link_count,"relationCount":r.relation_count,"issueCount":r.issue_count,"createdAt":iso(r.created_at)}
def list_media_snapshots(db,user_key,project_id,limit=100):
    q=select(InvestigationMediaSnapshot).where(InvestigationMediaSnapshot.user_key==user_key,InvestigationMediaSnapshot.project_id==project_id).order_by(InvestigationMediaSnapshot.created_at.desc()).limit(limit)
    return [snapshot_metadata(x) for x in db.scalars(q).all()]
