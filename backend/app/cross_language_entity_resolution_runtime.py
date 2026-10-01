from __future__ import annotations

from collections import defaultdict
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-cross-language-entity-toponym-resolution-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-cross-language-entity-toponym-resolution-request/1.0"
RESULT_SCHEMA = "sc-workspace-cross-language-entity-toponym-resolution-result/1.0"
ENTITY_SCHEMA = "sc-workspace-cross-language-entity/1.0"
NAME_SCHEMA = "sc-workspace-cross-language-name-form/1.0"
CANDIDATE_SCHEMA = "sc-workspace-entity-resolution-candidate/1.0"
DECISION_SCHEMA = "sc-workspace-entity-resolution-decision/1.0"
LINEAGE_SCHEMA = "sc-workspace-entity-resolution-lineage/1.0"

OPERATIONS = (
    "workspace.linguistics.entity-resolution-validate",
    "workspace.linguistics.entity-candidate-search",
    "workspace.linguistics.toponym-candidate-search",
    "workspace.linguistics.entity-resolution-score",
    "workspace.linguistics.entity-resolution-decision",
    "workspace.linguistics.entity-resolution-lineage",
)

class TemporalScope(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    start_year:int|None=Field(default=None,alias="startYear")
    end_year:int|None=Field(default=None,alias="endYear")

class NameForm(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    name_id:str=Field(alias="nameId",min_length=1,max_length=200)
    text:str=Field(min_length=1,max_length=1000)
    language_identity_id:str|None=Field(default=None,alias="languageIdentityId",max_length=200)
    script_identity_id:str|None=Field(default=None,alias="scriptIdentityId",max_length=200)
    kind:Literal["preferred","alias","historical","transliteration","translation","exonym","endonym","abbreviation","other"]="alias"
    valid_scope:TemporalScope=Field(default_factory=TemporalScope,alias="validScope")
    source_ref:str|None=Field(default=None,alias="sourceRef",max_length=500)

class ResolutionEntity(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    entity_id:str=Field(alias="entityId",min_length=1,max_length=200)
    entity_type:Literal["person","organization","place","geographic-feature","work","event","concept","other"]=Field(alias="entityType")
    canonical_label:str=Field(alias="canonicalLabel",min_length=1,max_length=1000)
    name_forms:list[NameForm]=Field(default_factory=list,alias="nameForms",max_length=500)
    external_identifiers:dict[str,str]=Field(default_factory=dict,alias="externalIdentifiers")
    regions:list[str]=Field(default_factory=list,max_length=100)
    coordinates:list[float]|None=None
    temporal_scope:TemporalScope=Field(default_factory=TemporalScope,alias="temporalScope")
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=100)

class ResolutionQuery(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    query_id:str=Field(alias="queryId",min_length=1,max_length=200)
    text:str=Field(min_length=1,max_length=1000)
    entity_type:str|None=Field(default=None,alias="entityType",max_length=100)
    language_identity_id:str|None=Field(default=None,alias="languageIdentityId",max_length=200)
    script_identity_id:str|None=Field(default=None,alias="scriptIdentityId",max_length=200)
    regions:list[str]=Field(default_factory=list,max_length=100)
    temporal_scope:TemporalScope=Field(default_factory=TemporalScope,alias="temporalScope")
    external_identifiers:dict[str,str]=Field(default_factory=dict,alias="externalIdentifiers")

class ResolutionCandidate(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    query_id:str=Field(alias="queryId")
    entity_id:str=Field(alias="entityId")
    score:float=Field(ge=0,le=1)
    evidence:list[str]=Field(default_factory=list,max_length=100)

class ResolutionDecision(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    decision_id:str=Field(alias="decisionId",min_length=1,max_length=200)
    query_id:str=Field(alias="queryId",min_length=1,max_length=200)
    entity_id:str|None=Field(default=None,alias="entityId",max_length=200)
    status:Literal["resolved","ambiguous","unresolved","rejected"]="unresolved"
    confidence:float|None=Field(default=None,ge=0,le=1)
    candidate_entity_ids:list[str]=Field(default_factory=list,alias="candidateEntityIds",max_length=100)
    rationale:str|None=Field(default=None,max_length=4000)
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=100)

class CrossLanguageEntityResolutionRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    entities:list[ResolutionEntity]=Field(default_factory=list,max_length=25000)
    queries:list[ResolutionQuery]=Field(default_factory=list,max_length=5000)
    candidates:list[ResolutionCandidate]=Field(default_factory=list,max_length=50000)
    decisions:list[ResolutionDecision]=Field(default_factory=list,max_length=10000)


def _norm(s:str)->str:
    return " ".join(s.casefold().strip().split())

def _overlap(a:TemporalScope,b:TemporalScope)->bool:
    alo=-10**9 if a.start_year is None else a.start_year; ahi=10**9 if a.end_year is None else a.end_year
    blo=-10**9 if b.start_year is None else b.start_year; bhi=10**9 if b.end_year is None else b.end_year
    return max(alo,blo)<=min(ahi,bhi)

def _validate(req):
    issues=[]; eids=set(); qids=set(); nids=set()
    for e in req.entities:
        if e.entity_id in eids: issues.append({"code":"duplicate-entity-id","entityId":e.entity_id})
        eids.add(e.entity_id)
        if e.coordinates is not None and (len(e.coordinates)!=2 or not (-90<=e.coordinates[0]<=90) or not (-180<=e.coordinates[1]<=180)):
            issues.append({"code":"invalid-coordinates","entityId":e.entity_id})
        for n in e.name_forms:
            if n.name_id in nids: issues.append({"code":"duplicate-name-id","nameId":n.name_id})
            nids.add(n.name_id)
    for q in req.queries:
        if q.query_id in qids: issues.append({"code":"duplicate-query-id","queryId":q.query_id})
        qids.add(q.query_id)
    for c in req.candidates:
        if c.query_id not in qids: issues.append({"code":"candidate-query-missing","queryId":c.query_id})
        if c.entity_id not in eids: issues.append({"code":"candidate-entity-missing","entityId":c.entity_id})
    for d in req.decisions:
        if d.query_id not in qids: issues.append({"code":"decision-query-missing","queryId":d.query_id})
        if d.entity_id and d.entity_id not in eids: issues.append({"code":"decision-entity-missing","entityId":d.entity_id})
    return {"schema":"sc-workspace-cross-language-entity-resolution-validation/1.0","valid":not issues,"issueCount":len(issues),"issues":issues,"entityCount":len(eids),"queryCount":len(qids)}

def _require(req):
    v=_validate(req)
    if not v['valid']: raise ValueError(f"cross-language entity resolution validation failed with {v['issueCount']} issue(s)")

def _score(q,e):
    score=0.0; ev=[]; qt=_norm(q.text)
    labels=[("canonical",e.canonical_label,None,None)]+[(n.kind,n.text,n.language_identity_id,n.script_identity_id) for n in e.name_forms]
    exact=[x for x in labels if _norm(x[1])==qt]
    if exact:
        score+=0.58; ev.append("exact-name")
        if any(x[0] in {"historical","transliteration","exonym","endonym","translation"} for x in exact): ev.append("cross-language-name-form")
    elif any(qt in _norm(x[1]) or _norm(x[1]) in qt for x in labels): score+=0.30; ev.append("partial-name")
    if q.entity_type and q.entity_type==e.entity_type: score+=0.08; ev.append("entity-type")
    if q.external_identifiers and any(e.external_identifiers.get(k)==v for k,v in q.external_identifiers.items()): score+=0.30; ev.append("external-identifier")
    if q.regions and set(map(_norm,q.regions)) & set(map(_norm,e.regions)): score+=0.08; ev.append("region")
    if _overlap(q.temporal_scope,e.temporal_scope): score+=0.04; ev.append("temporal-overlap")
    if q.language_identity_id and any(n.language_identity_id==q.language_identity_id and _norm(n.text)==qt for n in e.name_forms): score+=0.05; ev.append("language-context")
    if q.script_identity_id and any(n.script_identity_id==q.script_identity_id and _norm(n.text)==qt for n in e.name_forms): score+=0.05; ev.append("script-context")
    return min(score,1.0),ev

def _search(req,toponym=False):
    _require(req); out=[]
    for q in req.queries:
        rows=[]
        for e in req.entities:
            if toponym and e.entity_type not in {"place","geographic-feature"}: continue
            score,ev=_score(q,e)
            if score>0: rows.append({"schema":CANDIDATE_SCHEMA,"queryId":q.query_id,"entityId":e.entity_id,"score":round(score,6),"evidence":ev})
        rows.sort(key=lambda x:(-x['score'],x['entityId']))
        out.append({"queryId":q.query_id,"candidates":rows[:25]})
    return {"schema":"sc-workspace-toponym-candidate-index/1.0" if toponym else "sc-workspace-entity-candidate-index/1.0","items":out}

def _score_candidates(req):
    _require(req); qs={q.query_id:q for q in req.queries}; es={e.entity_id:e for e in req.entities}; rows=[]
    pairs={(c.query_id,c.entity_id) for c in req.candidates} or {(q.query_id,e.entity_id) for q in req.queries for e in req.entities}
    for qid,eid in sorted(pairs):
        if qid not in qs or eid not in es: continue
        score,ev=_score(qs[qid],es[eid]); rows.append({"schema":CANDIDATE_SCHEMA,"queryId":qid,"entityId":eid,"score":round(score,6),"evidence":ev})
    return {"schema":"sc-workspace-entity-resolution-scoring/1.0","items":rows}

def _decisions(req):
    _require(req); scored=_score_candidates(req)['items']; by=defaultdict(list)
    for x in scored: by[x['queryId']].append(x)
    items=[]
    for q in req.queries:
        rows=sorted(by[q.query_id],key=lambda x:(-x['score'],x['entityId'])); top=rows[0] if rows else None; second=rows[1] if len(rows)>1 else None
        if not top or top['score']<0.45: status='unresolved'; eid=None; conf=top['score'] if top else None
        elif second and top['score']-second['score']<0.05: status='ambiguous'; eid=None; conf=top['score']
        else: status='resolved'; eid=top['entityId']; conf=top['score']
        items.append({"schema":DECISION_SCHEMA,"queryId":q.query_id,"status":status,"entityId":eid,"confidence":conf,"candidateEntityIds":[r['entityId'] for r in rows[:5]],"automaticMergeApplied":False})
    return {"schema":"sc-workspace-entity-resolution-decision-index/1.0","items":items}

def _lineage(req):
    _require(req)
    return {"schema":LINEAGE_SCHEMA,"queries":[{"queryId":q.query_id,"text":q.text,"languageIdentityId":q.language_identity_id,"scriptIdentityId":q.script_identity_id} for q in req.queries],"decisions":[d.model_dump(by_alias=True) for d in req.decisions],"originalLanguageFirst":True,"automaticEntityMergeEnabled":False,"provenancePreserved":True}

def operation_catalog():
    return [{"operation":o,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for o in OPERATIONS]

def profile():
    return {"schema":RUNTIME_SCHEMA,"version":"3.51.0","title":"Cross-Language Entity & Toponym Resolution Runtime","boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),"originalLanguageFirst":True,"historicalNamesPreserved":True,"automaticEntityMergeEnabled":False,"automaticTranslationEnabled":False,"provenancePreserved":True,"arbitraryCodeExecution":False}

_EXEC={OPERATIONS[0]:_validate,OPERATIONS[1]:lambda r:_search(r,False),OPERATIONS[2]:lambda r:_search(r,True),OPERATIONS[3]:_score_candidates,OPERATIONS[4]:_decisions,OPERATIONS[5]:_lineage}
def execute(request:CrossLanguageEntityResolutionRequest)->dict[str,Any]:
    if request.schema_!=REQUEST_SCHEMA: raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    fn=_EXEC.get(request.operation)
    if not fn: raise ValueError(f"unsupported bounded operation: {request.operation}")
    return {"schema":RESULT_SCHEMA,"version":"3.51.0","operation":request.operation,"result":fn(request),"policy":{"originalLanguageFirst":True,"historicalNamesPreserved":True,"automaticEntityMergeEnabled":False,"automaticTranslationEnabled":False,"provenancePreserved":True,"arbitraryCodeExecution":False}}
