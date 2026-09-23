from __future__ import annotations
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (ProjectHead, InvestigationSpatialObservationHead, InvestigationSpatialObservationRevision,
    InvestigationSpatialContextLink, InvestigationSpatialRelation, InvestigationSpatialSnapshot)
from .investigation_documentary_workspace import build_documentary_graph
from .utils import iso, sha256_hex

SPATIAL_WORKSPACE_SCHEMA="sc-workspace-spatial-evidence-geospatial-investigation-workspace/1.0"
SPATIAL_OBSERVATION_SCHEMA="sc-workspace-investigation-spatial-observation/1.0"
SPATIAL_OBSERVATION_REQUEST_SCHEMA="sc-workspace-investigation-spatial-observation-request/1.0"
SPATIAL_CONTEXT_LINK_REQUEST_SCHEMA="sc-workspace-investigation-spatial-context-link-request/1.0"
SPATIAL_RELATION_REQUEST_SCHEMA="sc-workspace-investigation-spatial-relation-request/1.0"
SPATIAL_GRAPH_SCHEMA="sc-workspace-investigation-spatial-graph/1.0"
SPATIAL_DIAGNOSTICS_SCHEMA="sc-workspace-investigation-spatial-diagnostics/1.0"
SPATIAL_SNAPSHOT_REQUEST_SCHEMA="sc-workspace-investigation-spatial-snapshot-request/1.0"
SPATIAL_SNAPSHOT_SCHEMA="sc-workspace-investigation-spatial-snapshot/1.0"
OBSERVATION_TYPES=("point","bounding-box","polygon","line","route","track","named-place","external-geospatial-object","other")
TARGET_KINDS=("entity","event","document","excerpt","testimony","statement","evidence-ref","scientific-object-ref")
CONTEXT_RELATIONS=("located-at","occurred-at","observed-at","originated-at","destined-for","mentions-place","contains-location","spatial-context","related-to")
SPATIAL_RELATIONS=("same-place","near","inside","contains","overlaps","intersects","disjoint","north-of","south-of","east-of","west-of","connected-by","related-to")
REVIEW_STATES=("open","under-review","documented","contested","unresolved","closed")

class InvestigationSpatialObservationRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-spatial-observation-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); observationId:str=Field(default="",max_length=160)
    observationType: Literal["point","bounding-box","polygon","line","route","track","named-place","external-geospatial-object","other"]
    label:str=Field(min_length=1,max_length=1000); geometry:dict[str,Any]=Field(default_factory=dict)
    placeRef:str=Field(default="",max_length=2000); coordinateSystem:str=Field(default="EPSG:4326",max_length=64)
    sourceRef:str=Field(min_length=1,max_length=2000); sourceFingerprint:str=Field(min_length=8,max_length=128)
    observedAt:str=Field(default="",max_length=64)
    reviewState:Literal["open","under-review","documented","contested","unresolved","closed"]="open"
    expectedRevision:int|None=Field(default=None,ge=0); metadata:dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def geometry_or_place(self):
        if not self.geometry and not self.placeRef: raise ValueError("spatial observation requires geometry or placeRef")
        return self

class InvestigationSpatialContextLinkRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-spatial-context-link-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); observationId:str=Field(min_length=1,max_length=160)
    targetKind:Literal["entity","event","document","excerpt","testimony","statement","evidence-ref","scientific-object-ref"]
    targetRef:str=Field(min_length=1,max_length=2000)
    relation:Literal["located-at","occurred-at","observed-at","originated-at","destined-for","mentions-place","contains-location","spatial-context","related-to"]
    sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)

class InvestigationSpatialRelationRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-spatial-relation-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160); fromObservationId:str=Field(min_length=1,max_length=160); toObservationId:str=Field(min_length=1,max_length=160)
    relation:Literal["same-place","near","inside","contains","overlaps","intersects","disjoint","north-of","south-of","east-of","west-of","connected-by","related-to"]
    sourceRef:str=Field(default="",max_length=2000); sourceFingerprint:str=Field(default="",max_length=128); note:str=Field(default="",max_length=4000); metadata:dict[str,Any]=Field(default_factory=dict)
    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.fromObservationId==self.toObservationId: raise ValueError("spatial relation endpoints must differ")
        return self

class InvestigationSpatialSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-investigation-spatial-snapshot-request/1.0"]
    includeDocumentaryGraph:bool=True

def profile()->dict[str,Any]:
    return {"schema":SPATIAL_WORKSPACE_SCHEMA,"workspaceVersion":"3.12.0","release":"Spatial Evidence & Geospatial Investigation Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"versionedSpatialObservations":True,"sourceFingerprintRequired":True,
      "humanAssertedSpatialContextLinks":True,"humanAssertedSpatialRelations":True,"documentaryGraphOverlay":True,
      "mapReadyProjection":True,"spatialTemporalConsistencyDiagnostics":True,"immutableSpatialSnapshots":True,
      "automaticGeolocationInference":False,"automaticRelationshipInference":False,"automaticCausalityInference":False,
      "automaticTruthDetermination":False,"automaticEvidenceRanking":False,"automaticCulpabilityInference":False,"automaticNarrativeSelection":False,
      "supportedObservationTypes":list(OBSERVATION_TYPES),"supportedSpatialRelations":list(SPATIAL_RELATIONS)}

def _project(db,user_key,project_id):
    r=db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
    if r is None: raise KeyError(project_id)
    return r

def _obs(db,user_key,oid): return db.get(InvestigationSpatialObservationHead,{"user_key":user_key,"observation_id":oid})
def observation_metadata(r):
    return {"schema":SPATIAL_OBSERVATION_SCHEMA,"observationId":r.observation_id,"projectId":r.project_id,"observationType":r.observation_type,
      "label":r.label,"geometry":r.geometry_json or {},"placeRef":r.place_ref,"coordinateSystem":r.coordinate_system,"sourceRef":r.source_ref,
      "sourceFingerprint":r.source_fingerprint,"observedAt":r.observed_at,"reviewState":r.review_state,"revision":r.revision,
      "observationFingerprint":r.observation_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}
def revision_metadata(r):
    x=observation_metadata(r); x["createdAt"]=iso(r.created_at); x.pop("updatedAt",None); return x

def store_observation(db:Session,user_key:str,p:InvestigationSpatialObservationRequest):
    _project(db,user_key,p.projectId); row=_obs(db,user_key,p.observationId) if p.observationId else None
    if row and row.project_id!=p.projectId: raise ValueError("observation belongs to another project")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("observation revision conflict")
    oid=p.observationId or "spatial-observation-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"projectId":p.projectId,"observationId":oid,"revision":rev,"type":p.observationType,"label":p.label,"geometry":p.geometry,"placeRef":p.placeRef,"coordinateSystem":p.coordinateSystem,"sourceRef":p.sourceRef,"sourceFingerprint":p.sourceFingerprint,"observedAt":p.observedAt,"reviewState":p.reviewState,"metadata":p.metadata})
    if row is None:
        row=InvestigationSpatialObservationHead(user_key=user_key,observation_id=oid,project_id=p.projectId,observation_type=p.observationType,label=p.label,geometry_json=p.geometry,place_ref=p.placeRef,coordinate_system=p.coordinateSystem,source_ref=p.sourceRef,source_fingerprint=p.sourceFingerprint,observed_at=p.observedAt,review_state=p.reviewState,revision=rev,observation_fingerprint=fp,metadata_json=p.metadata); db.add(row)
    else:
        row.observation_type=p.observationType; row.label=p.label; row.geometry_json=p.geometry; row.place_ref=p.placeRef; row.coordinate_system=p.coordinateSystem; row.source_ref=p.sourceRef; row.source_fingerprint=p.sourceFingerprint; row.observed_at=p.observedAt; row.review_state=p.reviewState; row.revision=rev; row.observation_fingerprint=fp; row.metadata_json=p.metadata
    db.add(InvestigationSpatialObservationRevision(user_key=user_key,observation_id=oid,revision=rev,project_id=p.projectId,observation_type=p.observationType,label=p.label,geometry_json=p.geometry,place_ref=p.placeRef,coordinate_system=p.coordinateSystem,source_ref=p.sourceRef,source_fingerprint=p.sourceFingerprint,observed_at=p.observedAt,review_state=p.reviewState,observation_fingerprint=fp,metadata_json=p.metadata)); db.flush(); return observation_metadata(row)

def list_observations(db,user_key,project_id=None,observation_type=None,limit=1000):
    q=select(InvestigationSpatialObservationHead).where(InvestigationSpatialObservationHead.user_key==user_key)
    if project_id:q=q.where(InvestigationSpatialObservationHead.project_id==project_id)
    if observation_type:q=q.where(InvestigationSpatialObservationHead.observation_type==observation_type)
    return [observation_metadata(x) for x in db.scalars(q.order_by(InvestigationSpatialObservationHead.created_at.desc()).limit(limit)).all()]
def get_observation(db,user_key,oid):
    r=_obs(db,user_key,oid); return observation_metadata(r) if r else None
def observation_revisions(db,user_key,oid,limit=100):
    q=select(InvestigationSpatialObservationRevision).where(InvestigationSpatialObservationRevision.user_key==user_key,InvestigationSpatialObservationRevision.observation_id==oid).order_by(InvestigationSpatialObservationRevision.revision.desc()).limit(limit)
    return [revision_metadata(x) for x in db.scalars(q).all()]

def create_context_link(db,user_key,p):
    _project(db,user_key,p.projectId); o=_obs(db,user_key,p.observationId)
    if not o or o.project_id!=p.projectId: raise KeyError(p.observationId)
    lid="spatial-link-"+uuid4().hex[:24]; fp=sha256_hex(p.model_dump())
    r=InvestigationSpatialContextLink(user_key=user_key,link_id=lid,project_id=p.projectId,observation_id=p.observationId,target_kind=p.targetKind,target_ref=p.targetRef,relation=p.relation,source_fingerprint=p.sourceFingerprint,note=p.note,link_fingerprint=fp,metadata_json=p.metadata); db.add(r); db.flush(); return context_link_metadata(r)
def context_link_metadata(r): return {"linkId":r.link_id,"projectId":r.project_id,"observationId":r.observation_id,"targetKind":r.target_kind,"targetRef":r.target_ref,"relation":r.relation,"sourceFingerprint":r.source_fingerprint,"note":r.note,"linkFingerprint":r.link_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_context_links(db,user_key,project_id=None,observation_id=None,target_ref=None,limit=2000):
    q=select(InvestigationSpatialContextLink).where(InvestigationSpatialContextLink.user_key==user_key)
    if project_id:q=q.where(InvestigationSpatialContextLink.project_id==project_id)
    if observation_id:q=q.where(InvestigationSpatialContextLink.observation_id==observation_id)
    if target_ref:q=q.where(InvestigationSpatialContextLink.target_ref==target_ref)
    return [context_link_metadata(x) for x in db.scalars(q.order_by(InvestigationSpatialContextLink.created_at.desc()).limit(limit)).all()]

def create_spatial_relation(db,user_key,p):
    _project(db,user_key,p.projectId); a=_obs(db,user_key,p.fromObservationId); b=_obs(db,user_key,p.toObservationId)
    if not a or not b or a.project_id!=p.projectId or b.project_id!=p.projectId: raise KeyError("spatial observation")
    rid="spatial-relation-"+uuid4().hex[:24]; fp=sha256_hex(p.model_dump())
    r=InvestigationSpatialRelation(user_key=user_key,relation_id=rid,project_id=p.projectId,from_observation_id=p.fromObservationId,to_observation_id=p.toObservationId,relation=p.relation,source_ref=p.sourceRef,source_fingerprint=p.sourceFingerprint,note=p.note,relation_fingerprint=fp,metadata_json=p.metadata); db.add(r); db.flush(); return relation_metadata(r)
def relation_metadata(r): return {"relationId":r.relation_id,"projectId":r.project_id,"fromObservationId":r.from_observation_id,"toObservationId":r.to_observation_id,"relation":r.relation,"sourceRef":r.source_ref,"sourceFingerprint":r.source_fingerprint,"note":r.note,"relationFingerprint":r.relation_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_spatial_relations(db,user_key,project_id=None,observation_id=None,limit=2000):
    q=select(InvestigationSpatialRelation).where(InvestigationSpatialRelation.user_key==user_key)
    if project_id:q=q.where(InvestigationSpatialRelation.project_id==project_id)
    if observation_id:q=q.where((InvestigationSpatialRelation.from_observation_id==observation_id)|(InvestigationSpatialRelation.to_observation_id==observation_id))
    return [relation_metadata(x) for x in db.scalars(q.order_by(InvestigationSpatialRelation.created_at.desc()).limit(limit)).all()]

def map_projection(db,user_key,project_id):
    obs=list_observations(db,user_key,project_id,limit=5000); links=list_context_links(db,user_key,project_id,limit=10000)
    features=[]
    for o in obs:
        features.append({"type":"Feature","id":o["observationId"],"geometry":o["geometry"] or None,"properties":{"label":o["label"],"observationType":o["observationType"],"placeRef":o["placeRef"],"observedAt":o["observedAt"],"sourceFingerprint":o["sourceFingerprint"]}})
    fp=sha256_hex({"projectId":project_id,"features":features,"links":links})
    return {"schema":"sc-workspace-investigation-spatial-map-projection/1.0","projectId":project_id,"type":"FeatureCollection","features":features,"contextLinks":links,"projectionFingerprint":fp,"mapReady":True,"automaticGeocoding":False}

def build_spatial_graph(db,user_key,project_id,include_documentary_graph=True):
    _project(db,user_key,project_id); obs=list_observations(db,user_key,project_id,limit=5000); links=list_context_links(db,user_key,project_id,limit=20000); rels=list_spatial_relations(db,user_key,project_id,limit=20000)
    base=build_documentary_graph(db,user_key,project_id,True) if include_documentary_graph else {"nodes":[],"edges":[]}; nodes=list(base.get("nodes") or []); edges=list(base.get("edges") or [])
    nodes += [{"id":"spatial:"+o["observationId"],"kind":"spatial-observation","label":o["label"],"observationType":o["observationType"],"fingerprint":o["observationFingerprint"]} for o in obs]
    edges += [{"id":"spatial-link:"+x["linkId"],"from":"spatial:"+x["observationId"],"to":x["targetKind"]+":"+x["targetRef"],"relation":x["relation"],"humanAsserted":True} for x in links]
    edges += [{"id":"spatial-relation:"+x["relationId"],"from":"spatial:"+x["fromObservationId"],"to":"spatial:"+x["toObservationId"],"relation":x["relation"],"humanAsserted":True} for x in rels]
    fp=sha256_hex({"projectId":project_id,"nodes":nodes,"edges":edges})
    return {"schema":SPATIAL_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"observationCount":len(obs),"contextLinkCount":len(links),"relationCount":len(rels),"graphFingerprint":fp,"referenceFirst":True,"automaticRelationshipInference":False,"automaticTruthDetermination":False}

def spatial_diagnostics(db,user_key,project_id):
    obs=list_observations(db,user_key,project_id,limit=5000); links=list_context_links(db,user_key,project_id,limit=20000); rels=list_spatial_relations(db,user_key,project_id,limit=20000); linked={x["observationId"] for x in links}; issues=[]
    for o in obs:
        if not o["geometry"] and not o["placeRef"]: issues.append({"kind":"observation-without-location","observationId":o["observationId"]})
        if o["observationId"] not in linked: issues.append({"kind":"observation-without-context","observationId":o["observationId"]})
        if o["coordinateSystem"]!="EPSG:4326" and o["geometry"]: issues.append({"kind":"non-wgs84-geometry-review","observationId":o["observationId"],"coordinateSystem":o["coordinateSystem"]})
    relation_counts={k:0 for k in SPATIAL_RELATIONS}
    for r in rels: relation_counts[r["relation"]]=relation_counts.get(r["relation"],0)+1
    fp=sha256_hex({"projectId":project_id,"issues":issues,"relationCounts":relation_counts})
    return {"schema":SPATIAL_DIAGNOSTICS_SCHEMA,"projectId":project_id,"observationCount":len(obs),"contextLinkCount":len(links),"relationCount":len(rels),"issues":issues,"issueCount":len(issues),"relationCounts":relation_counts,"diagnosticsFingerprint":fp,"descriptiveOnly":True,"automaticGeolocationInference":False,"automaticCausalityInference":False,"automaticTruthDetermination":False,"automaticEvidenceRanking":False}

def create_spatial_snapshot(db,user_key,project_id,p):
    g=build_spatial_graph(db,user_key,project_id,p.includeDocumentaryGraph); d=spatial_diagnostics(db,user_key,project_id); sid="spatial-snapshot-"+uuid4().hex[:24]; sfp=sha256_hex({"projectId":project_id,"graph":g["graphFingerprint"],"diagnostics":d["diagnosticsFingerprint"],"includeDocumentaryGraph":p.includeDocumentaryGraph})
    r=InvestigationSpatialSnapshot(user_key=user_key,snapshot_id=sid,project_id=project_id,graph_fingerprint=g["graphFingerprint"],diagnostics_fingerprint=d["diagnosticsFingerprint"],snapshot_fingerprint=sfp,observation_count=g["observationCount"],context_link_count=g["contextLinkCount"],relation_count=g["relationCount"],issue_count=d["issueCount"],context_json={"includeDocumentaryGraph":p.includeDocumentaryGraph}); db.add(r); db.flush(); return snapshot_metadata(r)
def snapshot_metadata(r): return {"schema":SPATIAL_SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"graphFingerprint":r.graph_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"observationCount":r.observation_count,"contextLinkCount":r.context_link_count,"relationCount":r.relation_count,"issueCount":r.issue_count,"context":r.context_json or {},"createdAt":iso(r.created_at)}
def list_spatial_snapshots(db,user_key,project_id,limit=100):
    q=select(InvestigationSpatialSnapshot).where(InvestigationSpatialSnapshot.user_key==user_key,InvestigationSpatialSnapshot.project_id==project_id).order_by(InvestigationSpatialSnapshot.created_at.desc()).limit(limit)
    return [snapshot_metadata(x) for x in db.scalars(q).all()]
