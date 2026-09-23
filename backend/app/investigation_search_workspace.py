from __future__ import annotations
from collections import Counter
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (
    ProjectHead, InvestigationStatementHead, InvestigationEventHead, InvestigationEntityHead,
    InvestigationDocumentHead, InvestigationTestimonyHead, InvestigationSpatialObservationHead,
    InvestigationMediaArtifactHead, InvestigationSourceHead, InvestigationSavedSearchHead,
    InvestigationSavedSearchRevision, InvestigationSearchExecution, InvestigationSearchCollection,
    InvestigationSearchSnapshot,
)
from .utils import iso, sha256_hex

SEARCH_WORKSPACE_SCHEMA="sc-workspace-investigative-search-discovery-cross-case-retrieval-workspace/1.0"
SAVED_SEARCH_REQUEST_SCHEMA="sc-workspace-investigative-saved-search-request/1.0"
SAVED_SEARCH_SCHEMA="sc-workspace-investigative-saved-search/1.0"
SEARCH_EXECUTION_REQUEST_SCHEMA="sc-workspace-investigative-search-execution-request/1.0"
SEARCH_RESULT_SCHEMA="sc-workspace-investigative-search-results/1.0"
SEARCH_COLLECTION_REQUEST_SCHEMA="sc-workspace-investigative-search-collection-request/1.0"
SEARCH_COLLECTION_SCHEMA="sc-workspace-investigative-search-collection/1.0"
SEARCH_FACETS_SCHEMA="sc-workspace-investigative-search-facets/1.0"
SEARCH_DIAGNOSTICS_SCHEMA="sc-workspace-investigative-search-diagnostics/1.0"
SEARCH_GRAPH_SCHEMA="sc-workspace-investigative-search-discovery-graph/1.0"
SEARCH_SNAPSHOT_REQUEST_SCHEMA="sc-workspace-investigative-search-snapshot-request/1.0"
SEARCH_SNAPSHOT_SCHEMA="sc-workspace-investigative-search-snapshot/1.0"
SEARCH_KINDS=("statement","event","entity","document","testimony","spatial-observation","media-artifact","source")

class SavedSearchRequest(BaseModel):
    schema:Literal["sc-workspace-investigative-saved-search-request/1.0"]
    searchId:str=Field(default="",max_length=160); projectId:str=Field(default="",max_length=160)
    name:str=Field(min_length=1,max_length=500); query:str=Field(min_length=1,max_length=4000)
    projectScope:list[str]=Field(default_factory=list); kinds:list[str]=Field(default_factory=list)
    filters:dict[str,Any]=Field(default_factory=dict); expectedRevision:int|None=Field(default=None,ge=0); metadata:dict[str,Any]=Field(default_factory=dict)

class SearchExecutionRequest(BaseModel):
    schema:Literal["sc-workspace-investigative-search-execution-request/1.0"]
    query:str=Field(min_length=1,max_length=4000); savedSearchId:str=Field(default="",max_length=160)
    projectScope:list[str]=Field(default_factory=list); kinds:list[str]=Field(default_factory=list); filters:dict[str,Any]=Field(default_factory=dict)
    limit:int=Field(default=100,ge=1,le=1000)

class SearchCollectionRequest(BaseModel):
    schema:Literal["sc-workspace-investigative-search-collection-request/1.0"]
    name:str=Field(min_length=1,max_length=500); description:str=Field(default="",max_length=4000)
    projectScope:list[str]=Field(default_factory=list); objectRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=5000); metadata:dict[str,Any]=Field(default_factory=dict)

class SearchSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-investigative-search-snapshot-request/1.0"]
    query:str=Field(min_length=1,max_length=4000); kinds:list[str]=Field(default_factory=list); filters:dict[str,Any]=Field(default_factory=dict); limit:int=Field(default=250,ge=1,le=1000)

def profile()->dict[str,Any]:
    return {"schema":SEARCH_WORKSPACE_SCHEMA,"workspaceVersion":"3.15.0","release":"Investigative Search, Discovery & Cross-Case Retrieval Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"canonicalObjectBodiesPreserved":True,"crossCaseRetrieval":True,"savedQueries":True,
      "deterministicLexicalRetrieval":True,"retrievalProvenance":True,"evidenceAwareFiltering":True,"immutableSearchSnapshots":True,
      "automaticEvidenceRanking":False,"automaticSourceReliabilityScoring":False,"automaticCredibilityScoring":False,"automaticTruthDetermination":False,
      "automaticRelationshipInference":False,"automaticCulpabilityInference":False,"automaticNarrativeSelection":False,"supportedKinds":list(SEARCH_KINDS),
      "rankingSemantics":"lexical-relevance-only-not-evidence-quality"}

def _project_exists(db,user_key,project_id):
    return db.get(ProjectHead,{"user_key":user_key,"project_id":project_id}) is not None

def _saved(db,user_key,search_id): return db.get(InvestigationSavedSearchHead,{"user_key":user_key,"search_id":search_id})

def saved_metadata(r):
    return {"schema":SAVED_SEARCH_SCHEMA,"searchId":r.search_id,"projectId":r.project_id,"name":r.name,"query":r.query_text,"projectScope":r.project_scope_json or [],"kinds":r.kinds_json or [],"filters":r.filters_json or {},"revision":r.revision,"searchFingerprint":r.search_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def store_saved_search(db:Session,user_key:str,p:SavedSearchRequest):
    if p.projectId and not _project_exists(db,user_key,p.projectId): raise KeyError(p.projectId)
    row=_saved(db,user_key,p.searchId) if p.searchId else None
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("saved search revision conflict")
    sid=p.searchId or "saved-search-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    scope=list(dict.fromkeys([x for x in p.projectScope if x])); kinds=[x for x in dict.fromkeys(p.kinds) if x in SEARCH_KINDS]
    fp=sha256_hex({"searchId":sid,"revision":rev,"projectId":p.projectId,"name":p.name,"query":p.query,"projectScope":scope,"kinds":kinds,"filters":p.filters,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,name=p.name,query_text=p.query,project_scope_json=scope,kinds_json=kinds,filters_json=p.filters,revision=rev,search_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=InvestigationSavedSearchHead(user_key=user_key,search_id=sid,**vals);db.add(row)
    db.add(InvestigationSavedSearchRevision(user_key=user_key,search_id=sid,revision=rev,project_id=p.projectId,name=p.name,query_text=p.query,project_scope_json=scope,kinds_json=kinds,filters_json=p.filters,search_fingerprint=fp,metadata_json=p.metadata));db.flush();return saved_metadata(row)

def list_saved_searches(db,user_key,project_id=None,limit=1000):
    q=select(InvestigationSavedSearchHead).where(InvestigationSavedSearchHead.user_key==user_key)
    if project_id:q=q.where(InvestigationSavedSearchHead.project_id==project_id)
    q=q.order_by(InvestigationSavedSearchHead.updated_at.desc()).limit(limit);return [saved_metadata(x) for x in db.scalars(q).all()]

def get_saved_search(db,user_key,search_id):
    r=_saved(db,user_key,search_id);return saved_metadata(r) if r else None

def saved_search_revisions(db,user_key,search_id,limit=100):
    q=select(InvestigationSavedSearchRevision).where(InvestigationSavedSearchRevision.user_key==user_key,InvestigationSavedSearchRevision.search_id==search_id).order_by(InvestigationSavedSearchRevision.revision.desc()).limit(limit)
    return [{"schema":SAVED_SEARCH_SCHEMA,"searchId":r.search_id,"projectId":r.project_id,"name":r.name,"query":r.query_text,"projectScope":r.project_scope_json or [],"kinds":r.kinds_json or [],"filters":r.filters_json or {},"revision":r.revision,"searchFingerprint":r.search_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)} for r in db.scalars(q).all()]

def _norm(v): return " ".join(str(v or "").lower().split())
def _snippet(text,terms,maxlen=280):
    s=" ".join(str(text or "").split())
    low=s.lower(); positions=[low.find(t) for t in terms if t and low.find(t)>=0]; start=max(0,(min(positions) if positions else 0)-80); out=s[start:start+maxlen]
    return ("…" if start else "")+out+("…" if start+maxlen<len(s) else "")
def _score(fields,terms):
    score=0; matched=[]
    for name,value,weight in fields:
        low=_norm(value); hits=sum(low.count(t) for t in terms if t)
        if hits: score+=hits*weight; matched.append(name)
    return score,matched

def search(db:Session,user_key:str,query:str,project_scope:list[str]|None=None,kinds:list[str]|None=None,filters:dict[str,Any]|None=None,limit:int=100):
    terms=[t for t in _norm(query).split(" ") if t]; scope=[x for x in (project_scope or []) if x]; selected=set(kinds or SEARCH_KINDS); filters=filters or {}; hits=[]
    specs=[
      ("statement",InvestigationStatementHead,"statement_id",lambda r:r.title or r.statement_text,lambda r:[("title",r.title,4),("text",r.statement_text,2),("tags"," ".join(r.tags_json or []),1)],lambda r:r.statement_fingerprint,r"statement_text"),
      ("event",InvestigationEventHead,"event_id",lambda r:r.title,lambda r:[("title",r.title,4),("description",r.description,2),("locationRef",r.location_ref,1)],lambda r:r.event_fingerprint,"description"),
      ("entity",InvestigationEntityHead,"entity_id",lambda r:r.canonical_name,lambda r:[("canonicalName",r.canonical_name,5),("description",r.description,2),("entityType",r.entity_type,1)],lambda r:r.entity_fingerprint,"description"),
      ("document",InvestigationDocumentHead,"document_id",lambda r:r.title,lambda r:[("title",r.title,4),("description",r.description,2),("sourceRef",r.source_ref,1),("authority",r.authority,1)],lambda r:r.document_fingerprint,"description"),
      ("testimony",InvestigationTestimonyHead,"testimony_id",lambda r:r.title,lambda r:[("title",r.title,4),("text",r.text,2),("sourceRef",r.source_ref,1)],lambda r:r.testimony_fingerprint,"text"),
      ("spatial-observation",InvestigationSpatialObservationHead,"observation_id",lambda r:r.label,lambda r:[("label",r.label,4),("placeRef",r.place_ref,2),("sourceRef",r.source_ref,1)],lambda r:r.observation_fingerprint,"place_ref"),
      ("media-artifact",InvestigationMediaArtifactHead,"artifact_id",lambda r:r.title,lambda r:[("title",r.title,4),("sourceRef",r.source_ref,1),("filename",r.original_filename,2),("mimeType",r.mime_type,1)],lambda r:r.artifact_fingerprint,"source_ref"),
      ("source",InvestigationSourceHead,"source_id",lambda r:r.title,lambda r:[("title",r.title,4),("sourceRef",r.source_ref,2),("publisher",r.publisher,1),("sourceType",r.source_type,1)],lambda r:r.source_record_fingerprint,"source_ref"),
    ]
    for kind,Model,idfield,labeler,fielder,fper,snippet_field in specs:
        if kind not in selected: continue
        q=select(Model).where(Model.user_key==user_key)
        if scope:q=q.where(Model.project_id.in_(scope))
        rows=db.scalars(q.limit(5000)).all()
        for r in rows:
            if filters.get("reviewState") and getattr(r,"review_state",None)!=filters["reviewState"]: continue
            score,matched=_score(fielder(r),terms)
            if score<=0: continue
            text=getattr(r,snippet_field,"")
            hits.append({"kind":kind,"objectId":getattr(r,idfield),"projectId":r.project_id,"label":labeler(r),"snippet":_snippet(text,terms),"lexicalScore":score,"matchFields":matched,"objectFingerprint":fper(r),"canonicalRef":f"workspace:{kind}:{getattr(r,idfield)}"})
    hits.sort(key=lambda x:(-x["lexicalScore"],x["kind"],x["projectId"],x["objectId"]))
    hits=hits[:limit]; fp=sha256_hex({"query":query,"scope":scope,"kinds":sorted(selected),"filters":filters,"hits":hits})
    return {"schema":SEARCH_RESULT_SCHEMA,"query":query,"projectScope":scope,"kinds":sorted(selected),"filters":filters,"hits":hits,"resultCount":len(hits),"resultFingerprint":fp,"rankingBasis":"lexical-relevance-only-not-evidence-quality","automaticEvidenceRanking":False,"automaticTruthDetermination":False}

def execute_search(db,user_key,p:SearchExecutionRequest):
    result=search(db,user_key,p.query,p.projectScope,p.kinds,p.filters,p.limit)
    row=InvestigationSearchExecution(user_key=user_key,execution_id="search-run-"+uuid4().hex[:24],saved_search_id=p.savedSearchId,query_text=p.query,project_scope_json=p.projectScope,kinds_json=p.kinds,filters_json=p.filters,result_count=result["resultCount"],result_fingerprint=result["resultFingerprint"],results_json=result["hits"]);db.add(row);db.flush();return execution_metadata(row)

def execution_metadata(r): return {"executionId":r.execution_id,"savedSearchId":r.saved_search_id,"query":r.query_text,"projectScope":r.project_scope_json or [],"kinds":r.kinds_json or [],"filters":r.filters_json or {},"resultCount":r.result_count,"resultFingerprint":r.result_fingerprint,"hits":r.results_json or [],"createdAt":iso(r.created_at),"rankingBasis":"lexical-relevance-only-not-evidence-quality"}
def list_executions(db,user_key,limit=100):
    q=select(InvestigationSearchExecution).where(InvestigationSearchExecution.user_key==user_key).order_by(InvestigationSearchExecution.created_at.desc()).limit(limit);return [execution_metadata(x) for x in db.scalars(q).all()]
def get_execution(db,user_key,execution_id):
    r=db.get(InvestigationSearchExecution,{"user_key":user_key,"execution_id":execution_id});return execution_metadata(r) if r else None

def facets(db,user_key,project_id,query="",kinds=None,filters=None):
    if not _project_exists(db,user_key,project_id): raise KeyError(project_id)
    result=search(db,user_key,query or "*",[project_id],kinds,filters,1000) if query else _all_project_refs(db,user_key,project_id,kinds)
    hits=result["hits"] if isinstance(result,dict) and "hits" in result else result
    by_kind=Counter(x["kind"] for x in hits); payload={"schema":SEARCH_FACETS_SCHEMA,"projectId":project_id,"query":query,"countsByKind":dict(sorted(by_kind.items())),"resultCount":len(hits)};payload["facetsFingerprint"]=sha256_hex(payload);return payload

def _all_project_refs(db,user_key,project_id,kinds=None):
    selected=set(kinds or SEARCH_KINDS); hits=[]
    specs=[("statement",InvestigationStatementHead,"statement_id","title"),("event",InvestigationEventHead,"event_id","title"),("entity",InvestigationEntityHead,"entity_id","canonical_name"),("document",InvestigationDocumentHead,"document_id","title"),("testimony",InvestigationTestimonyHead,"testimony_id","title"),("spatial-observation",InvestigationSpatialObservationHead,"observation_id","label"),("media-artifact",InvestigationMediaArtifactHead,"artifact_id","title"),("source",InvestigationSourceHead,"source_id","title")]
    for kind,M,idf,lab in specs:
        if kind not in selected: continue
        for r in db.scalars(select(M).where(M.user_key==user_key,M.project_id==project_id).limit(5000)).all():hits.append({"kind":kind,"objectId":getattr(r,idf),"projectId":project_id,"label":getattr(r,lab),"lexicalScore":0,"canonicalRef":f"workspace:{kind}:{getattr(r,idf)}"})
    return hits

def diagnostics(db,user_key,project_id):
    if not _project_exists(db,user_key,project_id): raise KeyError(project_id)
    refs=_all_project_refs(db,user_key,project_id); issues=[]; counts=Counter(x["kind"] for x in refs)
    if not refs:issues.append({"code":"search-project-empty","severity":"review","message":"No supported investigative objects are available for retrieval."})
    for kind in SEARCH_KINDS:
        if counts.get(kind,0)==0:issues.append({"code":"search-kind-unrepresented","severity":"info","kind":kind,"message":"No canonical objects of this kind are currently present in the project."})
    payload={"schema":SEARCH_DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"automaticResolution":False,"automaticRelationshipInference":False};payload["diagnosticsFingerprint"]=sha256_hex(payload);return payload

def discovery_graph(db,user_key,project_id,query,limit=250):
    result=search(db,user_key,query,[project_id],None,None,limit); nodes=[{"id":"query:"+sha256_hex(query)[:16],"kind":"search-query","label":query}];edges=[]
    qid=nodes[0]["id"]
    for h in result["hits"]:nodes.append({"id":h["canonicalRef"],"kind":h["kind"],"label":h["label"],"projectId":h["projectId"]});edges.append({"id":"retrieved:"+sha256_hex(h["canonicalRef"]+query)[:20],"kind":"retrieval-match","from":qid,"to":h["canonicalRef"],"lexicalScore":h["lexicalScore"],"notAnInvestigativeRelationship":True})
    payload={"schema":SEARCH_GRAPH_SCHEMA,"projectId":project_id,"query":query,"nodes":nodes,"edges":edges,"automaticRelationshipInference":False,"automaticCausalityInference":False};payload["graphFingerprint"]=sha256_hex(payload);return payload

def create_collection(db,user_key,p:SearchCollectionRequest):
    refs=[dict(x) for x in p.objectRefs];fp=sha256_hex({"name":p.name,"description":p.description,"projectScope":p.projectScope,"objectRefs":refs,"metadata":p.metadata})
    r=InvestigationSearchCollection(user_key=user_key,collection_id="search-collection-"+uuid4().hex[:24],name=p.name,description=p.description,project_scope_json=p.projectScope,object_refs_json=refs,collection_fingerprint=fp,metadata_json=p.metadata);db.add(r);db.flush();return collection_metadata(r)
def collection_metadata(r): return {"schema":SEARCH_COLLECTION_SCHEMA,"collectionId":r.collection_id,"name":r.name,"description":r.description,"projectScope":r.project_scope_json or [],"objectRefs":r.object_refs_json or [],"collectionFingerprint":r.collection_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_collections(db,user_key,limit=100):
    q=select(InvestigationSearchCollection).where(InvestigationSearchCollection.user_key==user_key).order_by(InvestigationSearchCollection.created_at.desc()).limit(limit);return [collection_metadata(x) for x in db.scalars(q).all()]
def get_collection(db,user_key,collection_id):
    r=db.get(InvestigationSearchCollection,{"user_key":user_key,"collection_id":collection_id});return collection_metadata(r) if r else None

def create_snapshot(db,user_key,project_id,p:SearchSnapshotRequest):
    if not _project_exists(db,user_key,project_id): raise KeyError(project_id)
    result=search(db,user_key,p.query,[project_id],p.kinds,p.filters,p.limit); fac=facets(db,user_key,project_id,p.query,p.kinds,p.filters); diag=diagnostics(db,user_key,project_id)
    ctx={"result":result,"facets":fac,"diagnostics":diag};fp=sha256_hex(ctx)
    r=InvestigationSearchSnapshot(user_key=user_key,snapshot_id="search-snapshot-"+uuid4().hex[:24],project_id=project_id,query_text=p.query,result_count=result["resultCount"],result_fingerprint=result["resultFingerprint"],facets_fingerprint=fac["facetsFingerprint"],diagnostics_fingerprint=diag["diagnosticsFingerprint"],snapshot_fingerprint=fp,context_json=ctx);db.add(r);db.flush();return snapshot_metadata(r)
def snapshot_metadata(r):return {"schema":SEARCH_SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"query":r.query_text,"resultCount":r.result_count,"resultFingerprint":r.result_fingerprint,"facetsFingerprint":r.facets_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"createdAt":iso(r.created_at)}
def list_snapshots(db,user_key,project_id,limit=100):
    q=select(InvestigationSearchSnapshot).where(InvestigationSearchSnapshot.user_key==user_key,InvestigationSearchSnapshot.project_id==project_id).order_by(InvestigationSearchSnapshot.created_at.desc()).limit(limit);return [snapshot_metadata(x) for x in db.scalars(q).all()]
