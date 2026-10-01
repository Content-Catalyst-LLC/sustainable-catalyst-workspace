from __future__ import annotations

from collections import defaultdict
from math import sqrt
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-request/1.0"
RESULT_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-result/1.0"
UNIT_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-unit/1.0"
CANDIDATE_SCHEMA = "sc-workspace-cross-lingual-semantic-candidate/1.0"
LINK_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-link/1.0"
MAP_SCHEMA = "sc-workspace-cross-lingual-evidence-map/1.0"
LINEAGE_SCHEMA = "sc-workspace-cross-lingual-semantic-evidence-lineage/1.0"

OPERATIONS = (
    "workspace.linguistics.cross-lingual-semantic-validate",
    "workspace.linguistics.semantic-candidate-search",
    "workspace.linguistics.semantic-similarity-score",
    "workspace.linguistics.semantic-link-proposal",
    "workspace.linguistics.evidence-relation-analysis",
    "workspace.linguistics.cross-language-evidence-map",
    "workspace.linguistics.semantic-evidence-lineage",
)

class SemanticEvidenceUnit(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    unit_id: str = Field(alias="unitId", min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=20000)
    language_identity_id: str | None = Field(default=None, alias="languageIdentityId", max_length=200)
    script_identity_id: str | None = Field(default=None, alias="scriptIdentityId", max_length=200)
    unit_kind: Literal["claim","evidence","observation","definition","quotation","context","other"] = Field(default="evidence", alias="unitKind")
    concept_ids: list[str] = Field(default_factory=list, alias="conceptIds", max_length=500)
    entity_ids: list[str] = Field(default_factory=list, alias="entityIds", max_length=500)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=500)
    embedding: list[float] | None = Field(default=None, max_length=4096)
    metadata: dict[str, Any] = Field(default_factory=dict)

class SemanticCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_unit_id: str = Field(alias="sourceUnitId", min_length=1, max_length=200)
    target_unit_id: str = Field(alias="targetUnitId", min_length=1, max_length=200)
    score: float = Field(default=0.0, ge=0, le=1)
    signals: list[str] = Field(default_factory=list, max_length=100)

class SemanticEvidenceLink(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    link_id: str = Field(alias="linkId", min_length=1, max_length=200)
    source_unit_id: str = Field(alias="sourceUnitId", min_length=1, max_length=200)
    target_unit_id: str = Field(alias="targetUnitId", min_length=1, max_length=200)
    relation_type: Literal[
        "equivalent","near-equivalent","supports","contradicts","qualifies",
        "contextualizes","derived-from","translation-alignment","related"
    ] = Field(alias="relationType")
    status: Literal["proposed","reviewed","accepted","rejected"] = "proposed"
    confidence: float | None = Field(default=None, ge=0, le=1)
    rationale: str | None = Field(default=None, max_length=8000)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=500)
    human_reviewed: bool = Field(default=False, alias="humanReviewed")

class CrossLingualSemanticEvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    units: list[SemanticEvidenceUnit] = Field(default_factory=list, max_length=25000)
    candidates: list[SemanticCandidate] = Field(default_factory=list, max_length=100000)
    links: list[SemanticEvidenceLink] = Field(default_factory=list, max_length=100000)
    source_unit_ids: list[str] = Field(default_factory=list, alias="sourceUnitIds", max_length=5000)
    target_unit_ids: list[str] = Field(default_factory=list, alias="targetUnitIds", max_length=5000)
    top_k: int = Field(default=25, alias="topK", ge=1, le=100)

def _norm(value: str) -> str:
    return " ".join(value.casefold().strip().split())

def _tokens(value: str) -> set[str]:
    out=[]; cur=[]
    for ch in _norm(value):
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            out.append("".join(cur)); cur=[]
    if cur: out.append("".join(cur))
    return set(out)

def _cosine(a: list[float] | None, b: list[float] | None) -> float | None:
    if not a or not b or len(a) != len(b):
        return None
    na = sqrt(sum(x*x for x in a)); nb = sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0:
        return None
    raw = sum(x*y for x,y in zip(a,b))/(na*nb)
    return max(0.0, min(1.0, (raw + 1.0)/2.0))

def _overlap(a: list[str], b: list[str]) -> float:
    aa={_norm(x) for x in a if _norm(x)}; bb={_norm(x) for x in b if _norm(x)}
    if not aa or not bb: return 0.0
    return len(aa & bb)/len(aa | bb)

def _lexical(a: str, b: str) -> float:
    if _norm(a) == _norm(b): return 1.0
    aa=_tokens(a); bb=_tokens(b)
    if not aa or not bb: return 0.0
    return len(aa & bb)/len(aa | bb)

def _validate(req: CrossLingualSemanticEvidenceRequest) -> dict[str, Any]:
    issues=[]; ids=set(); link_ids=set()
    for u in req.units:
        if u.unit_id in ids: issues.append({"code":"duplicate-unit-id","unitId":u.unit_id})
        ids.add(u.unit_id)
    for c in req.candidates:
        if c.source_unit_id not in ids: issues.append({"code":"candidate-source-missing","unitId":c.source_unit_id})
        if c.target_unit_id not in ids: issues.append({"code":"candidate-target-missing","unitId":c.target_unit_id})
        if c.source_unit_id == c.target_unit_id: issues.append({"code":"self-candidate","unitId":c.source_unit_id})
    for link in req.links:
        if link.link_id in link_ids: issues.append({"code":"duplicate-link-id","linkId":link.link_id})
        link_ids.add(link.link_id)
        if link.source_unit_id not in ids: issues.append({"code":"link-source-missing","unitId":link.source_unit_id})
        if link.target_unit_id not in ids: issues.append({"code":"link-target-missing","unitId":link.target_unit_id})
        if link.relation_type in {"equivalent","near-equivalent"} and link.status == "accepted" and not link.human_reviewed:
            issues.append({"code":"accepted-equivalence-requires-human-review","linkId":link.link_id})
    return {"schema":"sc-workspace-cross-lingual-semantic-evidence-validation/1.0","valid":not issues,
            "issueCount":len(issues),"issues":issues,"unitCount":len(ids),"linkCount":len(link_ids)}

def _require(req):
    result=_validate(req)
    if not result["valid"]:
        raise ValueError(f"cross-lingual semantic evidence validation failed with {result['issueCount']} issue(s)")

def _score(a: SemanticEvidenceUnit, b: SemanticEvidenceUnit):
    score=0.0; signals=[]; components={}
    cosine=_cosine(a.embedding,b.embedding)
    if cosine is not None:
        components["representationCosine"]=round(cosine,6); score += 0.55*cosine; signals.append("representation-similarity")
    concepts=_overlap(a.concept_ids,b.concept_ids)
    if concepts:
        components["conceptOverlap"]=round(concepts,6); score += 0.20*concepts; signals.append("shared-concepts")
    entities=_overlap(a.entity_ids,b.entity_ids)
    if entities:
        components["entityOverlap"]=round(entities,6); score += 0.10*entities; signals.append("shared-entities")
    lexical=_lexical(a.text,b.text)
    if lexical:
        components["lexicalOverlap"]=round(lexical,6); score += 0.15*lexical; signals.append("lexical-overlap")
    if a.language_identity_id and b.language_identity_id and a.language_identity_id != b.language_identity_id:
        signals.append("cross-language")
    if a.script_identity_id and b.script_identity_id and a.script_identity_id != b.script_identity_id:
        signals.append("cross-script")
    return min(round(score,6),1.0),signals,components

def _pairs(req):
    units={u.unit_id:u for u in req.units}
    source_ids=req.source_unit_ids or list(units)
    target_ids=req.target_unit_ids or list(units)
    seen=set()
    for sid in source_ids:
        for tid in target_ids:
            if sid==tid or sid not in units or tid not in units: continue
            if (sid,tid) in seen: continue
            seen.add((sid,tid)); yield units[sid],units[tid]

def _candidate_search(req):
    _require(req); grouped=defaultdict(list)
    for a,b in _pairs(req):
        score,signals,components=_score(a,b)
        if score<=0: continue
        grouped[a.unit_id].append({"schema":CANDIDATE_SCHEMA,"sourceUnitId":a.unit_id,"targetUnitId":b.unit_id,
            "score":score,"signals":signals,"components":components,
            "sourceLanguageIdentityId":a.language_identity_id,"targetLanguageIdentityId":b.language_identity_id})
    items=[]
    for sid,rows in grouped.items():
        rows.sort(key=lambda x:(-x["score"],x["targetUnitId"]))
        items.append({"sourceUnitId":sid,"candidates":rows[:req.top_k]})
    items.sort(key=lambda x:x["sourceUnitId"])
    return {"schema":"sc-workspace-cross-lingual-semantic-candidate-index/1.0","items":items}

def _similarity(req):
    _require(req); units={u.unit_id:u for u in req.units}; rows=[]
    pairs={(c.source_unit_id,c.target_unit_id) for c in req.candidates}
    if not pairs: pairs={(a.unit_id,b.unit_id) for a,b in _pairs(req)}
    for sid,tid in sorted(pairs):
        if sid not in units or tid not in units: continue
        score,signals,components=_score(units[sid],units[tid])
        rows.append({"schema":CANDIDATE_SCHEMA,"sourceUnitId":sid,"targetUnitId":tid,"score":score,"signals":signals,"components":components})
    return {"schema":"sc-workspace-cross-lingual-semantic-scoring/1.0","items":rows}

def _proposals(req):
    scored=_similarity(req)["items"]; items=[]
    for row in scored:
        relation="near-equivalent" if row["score"]>=0.90 else "related"
        items.append({"schema":LINK_SCHEMA,"sourceUnitId":row["sourceUnitId"],"targetUnitId":row["targetUnitId"],
            "relationType":relation,"status":"proposed","confidence":row["score"],"signals":row["signals"],
            "automaticAcceptanceApplied":False,"humanReviewRequired":relation in {"equivalent","near-equivalent"}})
    return {"schema":"sc-workspace-cross-lingual-semantic-link-proposal-index/1.0","items":items}

def _evidence_analysis(req):
    _require(req); counts=defaultdict(int); reviewed=0
    for link in req.links:
        counts[link.relation_type]+=1
        if link.human_reviewed: reviewed+=1
    return {"schema":"sc-workspace-cross-lingual-evidence-relation-analysis/1.0",
        "relationCounts":dict(sorted(counts.items())),"linkCount":len(req.links),"humanReviewedCount":reviewed,
        "acceptedCount":sum(1 for x in req.links if x.status=="accepted"),
        "truthDeterminationApplied":False,"automaticEvidenceRankingApplied":False}

def _evidence_map(req):
    _require(req); units={u.unit_id:u for u in req.units}
    nodes=[{"unitId":u.unit_id,"unitKind":u.unit_kind,"languageIdentityId":u.language_identity_id,
        "scriptIdentityId":u.script_identity_id,"sourceRefs":u.source_refs,"conceptIds":u.concept_ids,"entityIds":u.entity_ids}
        for u in req.units]
    edges=[{"linkId":l.link_id,"sourceUnitId":l.source_unit_id,"targetUnitId":l.target_unit_id,
        "relationType":l.relation_type,"status":l.status,"confidence":l.confidence,"humanReviewed":l.human_reviewed}
        for l in req.links if l.source_unit_id in units and l.target_unit_id in units]
    return {"schema":MAP_SCHEMA,"nodes":nodes,"edges":edges,"originalLanguageFirst":True,"translationIsDerivedRepresentation":True}

def _lineage(req):
    _require(req)
    return {"schema":LINEAGE_SCHEMA,
        "units":[{"unitId":u.unit_id,"languageIdentityId":u.language_identity_id,"scriptIdentityId":u.script_identity_id,"sourceRefs":u.source_refs} for u in req.units],
        "links":[l.model_dump(by_alias=True) for l in req.links],
        "originalLanguageFirst":True,"translationIsDerivedRepresentation":True,
        "automaticSemanticEquivalenceEnabled":False,"automaticTruthDeterminationEnabled":False,"provenancePreserved":True}

def operation_catalog():
    return [{"operation":o,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for o in OPERATIONS]

def profile():
    return {"schema":RUNTIME_SCHEMA,"version":"3.52.0","title":"Cross-Lingual Semantic & Evidence Runtime",
        "boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),
        "originalLanguageFirst":True,"translationIsDerivedRepresentation":True,"historicalLanguageIdentityPreserved":True,
        "entityResolutionLineagePreserved":True,"automaticTranslationEnabled":False,
        "automaticSemanticEquivalenceEnabled":False,"automaticEvidenceRankingEnabled":False,
        "automaticTruthDeterminationEnabled":False,"humanReviewRequiredForAcceptedEquivalence":True,
        "provenancePreserved":True,"arbitraryCodeExecution":False}

_EXEC={OPERATIONS[0]:_validate,OPERATIONS[1]:_candidate_search,OPERATIONS[2]:_similarity,OPERATIONS[3]:_proposals,
       OPERATIONS[4]:_evidence_analysis,OPERATIONS[5]:_evidence_map,OPERATIONS[6]:_lineage}

def execute(request: CrossLingualSemanticEvidenceRequest) -> dict[str, Any]:
    if request.schema_ != REQUEST_SCHEMA: raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    fn=_EXEC.get(request.operation)
    if not fn: raise ValueError(f"unsupported bounded operation: {request.operation}")
    return {"schema":RESULT_SCHEMA,"version":"3.52.0","operation":request.operation,"result":fn(request),
        "policy":{"originalLanguageFirst":True,"translationIsDerivedRepresentation":True,"automaticTranslationEnabled":False,
        "automaticSemanticEquivalenceEnabled":False,"automaticEvidenceRankingEnabled":False,
        "automaticTruthDeterminationEnabled":False,"humanReviewRequiredForAcceptedEquivalence":True,
        "provenancePreserved":True,"arbitraryCodeExecution":False}}
