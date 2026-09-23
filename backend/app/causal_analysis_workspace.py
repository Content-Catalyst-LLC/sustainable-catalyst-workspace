from __future__ import annotations
from collections import Counter
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (
    ProjectHead, CausalQuestionHead, CausalQuestionRevision, CausalStructureRecord,
    AlternativeExplanationRecord, CausalIdentificationAssumption, CausalAnalysisHandoff,
    CausalResultBinding, CausalInvestigationSnapshot,
)
from .utils import iso, sha256_hex

CAUSAL_WORKSPACE_SCHEMA="sc-workspace-causal-analysis-alternative-explanation-workspace/1.0"
QUESTION_REQUEST_SCHEMA="sc-workspace-causal-question-request/1.0"
QUESTION_SCHEMA="sc-workspace-causal-question/1.0"
STRUCTURE_REQUEST_SCHEMA="sc-workspace-causal-structure-request/1.0"
STRUCTURE_SCHEMA="sc-workspace-causal-structure/1.0"
EXPLANATION_REQUEST_SCHEMA="sc-workspace-alternative-explanation-request/1.0"
EXPLANATION_SCHEMA="sc-workspace-alternative-explanation/1.0"
ASSUMPTION_REQUEST_SCHEMA="sc-workspace-causal-identification-assumption-request/1.0"
ASSUMPTION_SCHEMA="sc-workspace-causal-identification-assumption/1.0"
HANDOFF_REQUEST_SCHEMA="sc-workspace-causal-analysis-handoff-request/1.0"
HANDOFF_SCHEMA="sc-workspace-causal-analysis-handoff/1.0"
RESULT_REQUEST_SCHEMA="sc-workspace-causal-result-binding-request/1.0"
RESULT_SCHEMA="sc-workspace-causal-result-binding/1.0"
ANALYSIS_SCHEMA="sc-workspace-causal-investigation-analysis/1.0"
MANIFEST_SCHEMA="sc-workspace-causal-investigation-manifest/1.0"
GRAPH_SCHEMA="sc-workspace-causal-investigation-graph/1.0"
DIAGNOSTICS_SCHEMA="sc-workspace-causal-investigation-diagnostics/1.0"
SNAPSHOT_REQUEST_SCHEMA="sc-workspace-causal-investigation-snapshot-request/1.0"
SNAPSHOT_SCHEMA="sc-workspace-causal-investigation-snapshot/1.0"

REVIEW_STATES=("open","under-review","documented","contested","unresolved","closed")
STRUCTURE_KINDS=("dag","partial-dag","causal-graph","structural-model","path-model","custom")
VARIABLE_ROLES=("exposure","outcome","confounder","mediator","collider","instrument","effect-modifier","selection","context","latent","other")
EDGE_RELATIONS=("causes","possible-cause","mediates","confounds","instruments","selection-path","structural-link","other")
EXPLANATION_STATUSES=("open","considered","challenged","retained","rejected","unresolved")
ASSUMPTION_TYPES=("temporal-order","exchangeability","positivity","consistency","no-interference","no-unmeasured-confounding","exclusion-restriction","relevance","monotonicity","parallel-trends","continuity","stable-unit-treatment-value","measurement-validity","model-specification","transportability","custom")
ASSUMPTION_STATUSES=("asserted","supported","challenged","violated","unknown")
CAUSAL_METHODS=("difference-in-differences","instrumental-variable","matching","weighting","regression-discontinuity","interrupted-time-series","g-formula","targeted-learning","bayesian-causal","structural-equation","causal-discovery","negative-control","custom")
DESTINATIONS=("workbench","research-lab","catalyst-analytics-r","platform-core")
RESULT_KINDS=("effect-estimate","confidence-interval","credible-interval","falsification-test","balance-diagnostic","sensitivity-diagnostic","placebo-test","robustness-check","causal-graph","identification-diagnostic","other")

class CausalQuestionRequest(BaseModel):
    schema:Literal["sc-workspace-causal-question-request/1.0"]
    questionId:str=Field(default="",max_length=160)
    projectId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    questionText:str=Field(min_length=1,max_length=12000)
    estimand:str=Field(default="",max_length=500)
    exposureRef:str=Field(default="",max_length=1000)
    outcomeRef:str=Field(default="",max_length=1000)
    reviewState:str=Field(default="open",max_length=40)
    expectedRevision:int|None=Field(default=None,ge=0)
    metadata:dict[str,Any]=Field(default_factory=dict)

class CausalStructureRequest(BaseModel):
    schema:Literal["sc-workspace-causal-structure-request/1.0"]
    questionId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    structureKind:str=Field(default="dag")
    variables:list[dict[str,Any]]=Field(default_factory=list,max_length=500)
    edges:list[dict[str,Any]]=Field(default_factory=list,max_length=2000)
    graphRef:str=Field(default="",max_length=2000)
    graphFingerprint:str=Field(default="",max_length=128)
    metadata:dict[str,Any]=Field(default_factory=dict)

class AlternativeExplanationRequest(BaseModel):
    schema:Literal["sc-workspace-alternative-explanation-request/1.0"]
    questionId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    explanation:str=Field(min_length=1,max_length=12000)
    mechanism:str=Field(default="",max_length=12000)
    status:str=Field(default="open",max_length=40)
    hypothesisRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=500)
    evidenceRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class IdentificationAssumptionRequest(BaseModel):
    schema:Literal["sc-workspace-causal-identification-assumption-request/1.0"]
    questionId:str=Field(min_length=1,max_length=160)
    assumptionType:str=Field(min_length=1,max_length=120)
    statement:str=Field(min_length=1,max_length=12000)
    rationale:str=Field(default="",max_length=12000)
    status:str=Field(default="asserted",max_length=40)
    evidenceRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class CausalAnalysisHandoffRequest(BaseModel):
    schema:Literal["sc-workspace-causal-analysis-handoff-request/1.0"]
    questionId:str=Field(min_length=1,max_length=160)
    method:str=Field(min_length=1,max_length=120)
    destinationProduct:str=Field(default="catalyst-analytics-r")
    estimand:str=Field(default="",max_length=500)
    treatmentRef:str=Field(default="",max_length=1000)
    outcomeRef:str=Field(default="",max_length=1000)
    adjustmentSet:list[str]=Field(default_factory=list,max_length=500)
    configuration:dict[str,Any]=Field(default_factory=dict)
    externalHandoffRef:str=Field(default="",max_length=2000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class CausalResultBindingRequest(BaseModel):
    schema:Literal["sc-workspace-causal-result-binding-request/1.0"]
    questionId:str=Field(min_length=1,max_length=160)
    handoffId:str=Field(default="",max_length=96)
    resultKind:str=Field(min_length=1,max_length=100)
    resultRef:str=Field(min_length=1,max_length=2000)
    resultFingerprint:str=Field(min_length=8,max_length=128)
    interpretationStatus:str=Field(default="reported",max_length=40)
    note:str=Field(default="",max_length=12000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class CausalInvestigationSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-causal-investigation-snapshot-request/1.0"]
    includeGraph:bool=True


def profile()->dict[str,Any]:
    return {
      "schema":CAUSAL_WORKSPACE_SCHEMA,"workspaceVersion":"3.18.0",
      "release":"Causal Analysis & Alternative Explanation Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"canonicalEvidenceAuthorityPreserved":True,
      "explicitCausalQuestions":True,"explicitCausalStructures":True,"alternativeExplanationsPreserved":True,
      "identificationAssumptionsExplicit":True,"causalAnalysisHandoffs":True,"causalResultBindings":True,
      "causalResultsModelConditional":True,"immutableCausalSnapshots":True,"humanReviewRequired":True,
      "supportedMethods":list(CAUSAL_METHODS),"supportedDestinations":list(DESTINATIONS),
      "automaticCausalityInference":False,"automaticCausalDiscovery":False,"automaticConfounderSelection":False,
      "automaticIdentificationClaim":False,"automaticAlternativeExplanationRanking":False,
      "automaticEvidenceRanking":False,"automaticTruthDetermination":False,"automaticCulpabilityInference":False,
      "automaticNarrativeSelection":False,
    }

def _project(db,user_key,project_id): return db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
def _question(db,user_key,question_id): return db.get(CausalQuestionHead,{"user_key":user_key,"question_id":question_id})

def _refs_pinned(items:list[dict[str,Any]],label:str):
    for item in items:
        ref=str(item.get("ref") or item.get("evidenceRef") or item.get("hypothesisRef") or "")
        fp=str(item.get("fingerprint") or item.get("evidenceFingerprint") or item.get("hypothesisFingerprint") or "")
        if ref and len(fp)<8: raise ValueError(f"{label} reference fingerprint required")

def question_metadata(r):
    return {"schema":QUESTION_SCHEMA,"questionId":r.question_id,"projectId":r.project_id,"title":r.title,"questionText":r.question_text,"estimand":r.estimand,"exposureRef":r.exposure_ref,"outcomeRef":r.outcome_ref,"reviewState":r.review_state,"revision":r.revision,"questionFingerprint":r.question_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def store_question(db:Session,user_key:str,p:CausalQuestionRequest):
    if not _project(db,user_key,p.projectId): raise KeyError(p.projectId)
    if p.reviewState not in REVIEW_STATES: raise ValueError("unsupported causal question review state")
    row=_question(db,user_key,p.questionId) if p.questionId else None
    if row and row.project_id!=p.projectId: raise ValueError("causal question project mismatch")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("causal question revision conflict")
    qid=p.questionId or "causal-question-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"questionId":qid,"projectId":p.projectId,"revision":rev,"title":p.title,"questionText":p.questionText,"estimand":p.estimand,"exposureRef":p.exposureRef,"outcomeRef":p.outcomeRef,"reviewState":p.reviewState,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,title=p.title,question_text=p.questionText,estimand=p.estimand,exposure_ref=p.exposureRef,outcome_ref=p.outcomeRef,review_state=p.reviewState,revision=rev,question_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=CausalQuestionHead(user_key=user_key,question_id=qid,**vals); db.add(row)
    rvals=dict(vals); rvals.pop("revision",None)
    db.add(CausalQuestionRevision(user_key=user_key,question_id=qid,revision=rev,**rvals)); db.flush(); return question_metadata(row)

def list_questions(db,user_key,project_id=None,review_state=None,limit=1000):
    q=select(CausalQuestionHead).where(CausalQuestionHead.user_key==user_key)
    if project_id:q=q.where(CausalQuestionHead.project_id==project_id)
    if review_state:q=q.where(CausalQuestionHead.review_state==review_state)
    return [question_metadata(x) for x in db.scalars(q.order_by(CausalQuestionHead.updated_at.desc()).limit(limit)).all()]

def get_question(db,user_key,question_id):
    r=_question(db,user_key,question_id); return question_metadata(r) if r else None

def question_revisions(db,user_key,question_id,limit=100):
    q=select(CausalQuestionRevision).where(CausalQuestionRevision.user_key==user_key,CausalQuestionRevision.question_id==question_id).order_by(CausalQuestionRevision.revision.desc()).limit(limit)
    return [{"schema":QUESTION_SCHEMA,"questionId":r.question_id,"projectId":r.project_id,"title":r.title,"questionText":r.question_text,"estimand":r.estimand,"exposureRef":r.exposure_ref,"outcomeRef":r.outcome_ref,"reviewState":r.review_state,"revision":r.revision,"questionFingerprint":r.question_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)} for r in db.scalars(q).all()]

def _has_cycle(variable_ids:set[str],edges:list[dict[str,Any]])->bool:
    adj={x:[] for x in variable_ids}
    for e in edges: adj[str(e.get("from") or "")].append(str(e.get("to") or ""))
    state={x:0 for x in variable_ids}
    def visit(x):
        state[x]=1
        for y in adj.get(x,[]):
            if state.get(y,0)==1:return True
            if state.get(y,0)==0 and visit(y):return True
        state[x]=2;return False
    return any(state[x]==0 and visit(x) for x in variable_ids)

def create_structure(db,user_key,p:CausalStructureRequest):
    qn=_question(db,user_key,p.questionId)
    if qn is None: raise KeyError(p.questionId)
    if p.structureKind not in STRUCTURE_KINDS: raise ValueError("unsupported causal structure kind")
    if len(p.variables)<2: raise ValueError("causal structure requires at least two explicit variables")
    ids=[]
    for v in p.variables:
        vid=str(v.get("variableId") or "").strip(); role=str(v.get("role") or "other")
        if not vid: raise ValueError("causal variableId required")
        if role not in VARIABLE_ROLES: raise ValueError("unsupported causal variable role")
        ids.append(vid)
    if len(set(ids))!=len(ids): raise ValueError("causal variableId values must be unique")
    known=set(ids)
    normalized=[]
    for e in p.edges:
        src=str(e.get("from") or "").strip(); dst=str(e.get("to") or "").strip(); rel=str(e.get("relation") or "causes")
        if src not in known or dst not in known: raise ValueError("causal edge endpoint must reference a declared variable")
        if src==dst: raise ValueError("causal edge endpoints must differ")
        if rel not in EDGE_RELATIONS: raise ValueError("unsupported causal edge relation")
        normalized.append(dict(e,**{"from":src,"to":dst,"relation":rel}))
    if p.structureKind in ("dag","partial-dag") and _has_cycle(known,normalized): raise ValueError("DAG causal structure cannot contain directed cycles")
    if p.graphRef and len(p.graphFingerprint)<8: raise ValueError("external graph fingerprint required")
    fp=sha256_hex({"projectId":qn.project_id,"questionId":p.questionId,"title":p.title,"structureKind":p.structureKind,"variables":p.variables,"edges":normalized,"graphRef":p.graphRef,"graphFingerprint":p.graphFingerprint,"metadata":p.metadata})
    row=CausalStructureRecord(user_key=user_key,structure_id="causal-structure-"+uuid4().hex[:24],project_id=qn.project_id,question_id=p.questionId,title=p.title,structure_kind=p.structureKind,variables_json=p.variables,edges_json=normalized,graph_ref=p.graphRef,graph_fingerprint=p.graphFingerprint,structure_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return structure_metadata(row)

def structure_metadata(r): return {"schema":STRUCTURE_SCHEMA,"structureId":r.structure_id,"projectId":r.project_id,"questionId":r.question_id,"title":r.title,"structureKind":r.structure_kind,"variables":r.variables_json or [],"edges":r.edges_json or [],"graphRef":r.graph_ref,"graphFingerprint":r.graph_fingerprint,"structureFingerprint":r.structure_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_structures(db,user_key,project_id=None,question_id=None,limit=5000):
    q=select(CausalStructureRecord).where(CausalStructureRecord.user_key==user_key)
    if project_id:q=q.where(CausalStructureRecord.project_id==project_id)
    if question_id:q=q.where(CausalStructureRecord.question_id==question_id)
    return [structure_metadata(x) for x in db.scalars(q.order_by(CausalStructureRecord.created_at.asc()).limit(limit)).all()]

def create_alternative_explanation(db,user_key,p:AlternativeExplanationRequest):
    qn=_question(db,user_key,p.questionId)
    if qn is None: raise KeyError(p.questionId)
    if p.status not in EXPLANATION_STATUSES: raise ValueError("unsupported alternative explanation status")
    _refs_pinned(p.hypothesisRefs,"hypothesis"); _refs_pinned(p.evidenceRefs,"evidence")
    fp=sha256_hex({"projectId":qn.project_id,"questionId":p.questionId,"title":p.title,"explanation":p.explanation,"mechanism":p.mechanism,"status":p.status,"hypothesisRefs":p.hypothesisRefs,"evidenceRefs":p.evidenceRefs,"metadata":p.metadata})
    row=AlternativeExplanationRecord(user_key=user_key,explanation_id="alternative-explanation-"+uuid4().hex[:24],project_id=qn.project_id,question_id=p.questionId,title=p.title,explanation=p.explanation,mechanism=p.mechanism,status=p.status,hypothesis_refs_json=p.hypothesisRefs,evidence_refs_json=p.evidenceRefs,explanation_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return explanation_metadata(row)
def explanation_metadata(r): return {"schema":EXPLANATION_SCHEMA,"explanationId":r.explanation_id,"projectId":r.project_id,"questionId":r.question_id,"title":r.title,"explanation":r.explanation,"mechanism":r.mechanism,"status":r.status,"hypothesisRefs":r.hypothesis_refs_json or [],"evidenceRefs":r.evidence_refs_json or [],"explanationFingerprint":r.explanation_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_alternative_explanations(db,user_key,project_id=None,question_id=None,limit=5000):
    q=select(AlternativeExplanationRecord).where(AlternativeExplanationRecord.user_key==user_key)
    if project_id:q=q.where(AlternativeExplanationRecord.project_id==project_id)
    if question_id:q=q.where(AlternativeExplanationRecord.question_id==question_id)
    return [explanation_metadata(x) for x in db.scalars(q.order_by(AlternativeExplanationRecord.created_at.asc()).limit(limit)).all()]

def create_identification_assumption(db,user_key,p:IdentificationAssumptionRequest):
    qn=_question(db,user_key,p.questionId)
    if qn is None: raise KeyError(p.questionId)
    if p.assumptionType not in ASSUMPTION_TYPES: raise ValueError("unsupported identification assumption type")
    if p.status not in ASSUMPTION_STATUSES: raise ValueError("unsupported identification assumption status")
    _refs_pinned(p.evidenceRefs,"evidence")
    fp=sha256_hex({"projectId":qn.project_id,"questionId":p.questionId,"assumptionType":p.assumptionType,"statement":p.statement,"rationale":p.rationale,"status":p.status,"evidenceRefs":p.evidenceRefs,"metadata":p.metadata})
    row=CausalIdentificationAssumption(user_key=user_key,assumption_id="causal-assumption-"+uuid4().hex[:24],project_id=qn.project_id,question_id=p.questionId,assumption_type=p.assumptionType,statement=p.statement,rationale=p.rationale,status=p.status,evidence_refs_json=p.evidenceRefs,assumption_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return assumption_metadata(row)
def assumption_metadata(r): return {"schema":ASSUMPTION_SCHEMA,"assumptionId":r.assumption_id,"projectId":r.project_id,"questionId":r.question_id,"assumptionType":r.assumption_type,"statement":r.statement,"rationale":r.rationale,"status":r.status,"evidenceRefs":r.evidence_refs_json or [],"assumptionFingerprint":r.assumption_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_identification_assumptions(db,user_key,project_id=None,question_id=None,limit=5000):
    q=select(CausalIdentificationAssumption).where(CausalIdentificationAssumption.user_key==user_key)
    if project_id:q=q.where(CausalIdentificationAssumption.project_id==project_id)
    if question_id:q=q.where(CausalIdentificationAssumption.question_id==question_id)
    return [assumption_metadata(x) for x in db.scalars(q.order_by(CausalIdentificationAssumption.created_at.asc()).limit(limit)).all()]

def create_handoff(db,user_key,p:CausalAnalysisHandoffRequest):
    qn=_question(db,user_key,p.questionId)
    if qn is None: raise KeyError(p.questionId)
    if p.method not in CAUSAL_METHODS: raise ValueError("unsupported causal analysis method")
    if p.destinationProduct not in DESTINATIONS: raise ValueError("unsupported causal analysis destination")
    estimand=p.estimand or qn.estimand; treatment=p.treatmentRef or qn.exposure_ref; outcome=p.outcomeRef or qn.outcome_ref
    fp=sha256_hex({"projectId":qn.project_id,"questionId":p.questionId,"method":p.method,"destinationProduct":p.destinationProduct,"estimand":estimand,"treatmentRef":treatment,"outcomeRef":outcome,"adjustmentSet":p.adjustmentSet,"configuration":p.configuration,"externalHandoffRef":p.externalHandoffRef,"metadata":p.metadata})
    row=CausalAnalysisHandoff(user_key=user_key,handoff_id="causal-handoff-"+uuid4().hex[:24],project_id=qn.project_id,question_id=p.questionId,method=p.method,destination_product=p.destinationProduct,estimand=estimand,treatment_ref=treatment,outcome_ref=outcome,adjustment_set_json=p.adjustmentSet,configuration_json=p.configuration,status="ready",handoff_fingerprint=fp,external_handoff_ref=p.externalHandoffRef,metadata_json=p.metadata);db.add(row);db.flush();return handoff_metadata(row)
def handoff_metadata(r): return {"schema":HANDOFF_SCHEMA,"handoffId":r.handoff_id,"projectId":r.project_id,"questionId":r.question_id,"method":r.method,"destinationProduct":r.destination_product,"estimand":r.estimand,"treatmentRef":r.treatment_ref,"outcomeRef":r.outcome_ref,"adjustmentSet":r.adjustment_set_json or [],"configuration":r.configuration_json or {},"status":r.status,"handoffFingerprint":r.handoff_fingerprint,"externalHandoffRef":r.external_handoff_ref,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_handoffs(db,user_key,project_id=None,question_id=None,limit=5000):
    q=select(CausalAnalysisHandoff).where(CausalAnalysisHandoff.user_key==user_key)
    if project_id:q=q.where(CausalAnalysisHandoff.project_id==project_id)
    if question_id:q=q.where(CausalAnalysisHandoff.question_id==question_id)
    return [handoff_metadata(x) for x in db.scalars(q.order_by(CausalAnalysisHandoff.created_at.asc()).limit(limit)).all()]

def create_result_binding(db,user_key,p:CausalResultBindingRequest):
    qn=_question(db,user_key,p.questionId)
    if qn is None: raise KeyError(p.questionId)
    if p.resultKind not in RESULT_KINDS: raise ValueError("unsupported causal result kind")
    if p.handoffId:
        h=db.get(CausalAnalysisHandoff,{"user_key":user_key,"handoff_id":p.handoffId})
        if h is None: raise KeyError(p.handoffId)
        if h.question_id!=p.questionId: raise ValueError("causal result handoff question mismatch")
    fp=sha256_hex({"projectId":qn.project_id,"questionId":p.questionId,"handoffId":p.handoffId,"resultKind":p.resultKind,"resultRef":p.resultRef,"resultFingerprint":p.resultFingerprint,"interpretationStatus":p.interpretationStatus,"note":p.note,"metadata":p.metadata})
    row=CausalResultBinding(user_key=user_key,binding_id="causal-result-"+uuid4().hex[:24],project_id=qn.project_id,question_id=p.questionId,handoff_id=p.handoffId,result_kind=p.resultKind,result_ref=p.resultRef,result_fingerprint=p.resultFingerprint,interpretation_status=p.interpretationStatus,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return result_metadata(row)
def result_metadata(r): return {"schema":RESULT_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"questionId":r.question_id,"handoffId":r.handoff_id,"resultKind":r.result_kind,"resultRef":r.result_ref,"resultFingerprint":r.result_fingerprint,"interpretationStatus":r.interpretation_status,"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_result_bindings(db,user_key,project_id=None,question_id=None,limit=5000):
    q=select(CausalResultBinding).where(CausalResultBinding.user_key==user_key)
    if project_id:q=q.where(CausalResultBinding.project_id==project_id)
    if question_id:q=q.where(CausalResultBinding.question_id==question_id)
    return [result_metadata(x) for x in db.scalars(q.order_by(CausalResultBinding.created_at.asc()).limit(limit)).all()]

def manifest(db,user_key,project_id):
    if not _project(db,user_key,project_id): raise KeyError(project_id)
    questions=list_questions(db,user_key,project_id,None,5000); structures=list_structures(db,user_key,project_id,None,10000); explanations=list_alternative_explanations(db,user_key,project_id,None,10000); assumptions=list_identification_assumptions(db,user_key,project_id,None,10000); handoffs=list_handoffs(db,user_key,project_id,None,10000); results=list_result_bindings(db,user_key,project_id,None,10000)
    counts={"questions":len(questions),"structures":len(structures),"alternativeExplanations":len(explanations),"identificationAssumptions":len(assumptions),"handoffs":len(handoffs),"resultBindings":len(results)}
    payload={"schema":MANIFEST_SCHEMA,"projectId":project_id,"counts":counts,"questions":questions,"structures":structures,"alternativeExplanations":explanations,"identificationAssumptions":assumptions,"handoffs":handoffs,"resultBindings":results,"causalResultsModelConditional":True,"alternativeExplanationsPreserved":True,"canonicalEvidenceAuthorityPreserved":True}
    payload["manifestFingerprint"]=sha256_hex(payload);return payload

def graph(db,user_key,project_id):
    m=manifest(db,user_key,project_id);nodes=[];edges=[]
    for q in m["questions"]: nodes.append({"id":"causal-question:"+q["questionId"],"kind":"causal-question","label":q["title"],"fingerprint":q["questionFingerprint"]})
    for s in m["structures"]:
        sid="causal-structure:"+s["structureId"];nodes.append({"id":sid,"kind":"causal-structure","label":s["title"],"structureKind":s["structureKind"],"fingerprint":s["structureFingerprint"]});edges.append({"id":"structure-question:"+s["structureId"],"kind":"models","from":sid,"to":"causal-question:"+s["questionId"]})
        varnodes={}
        for v in s["variables"]:
            vid=str(v.get("variableId") or ""); nid=f"causal-variable:{s['structureId']}:{vid}";varnodes[vid]=nid;nodes.append({"id":nid,"kind":"causal-variable","label":str(v.get("name") or vid),"role":str(v.get("role") or "other")});edges.append({"id":f"structure-variable:{s['structureId']}:{vid}","kind":"contains-variable","from":sid,"to":nid})
        for i,e in enumerate(s["edges"]):
            edges.append({"id":f"causal-edge:{s['structureId']}:{i}","kind":str(e.get("relation") or "causes"),"from":varnodes[str(e.get("from"))],"to":varnodes[str(e.get("to"))],"humanAsserted":True})
        if s["graphRef"]: nodes.append({"id":s["graphRef"],"kind":"external-causal-graph","externalCanonicalReference":True,"objectFingerprint":s["graphFingerprint"]});edges.append({"id":"external-graph:"+s["structureId"],"kind":"references","from":sid,"to":s["graphRef"]})
    for x in m["alternativeExplanations"]:
        eid="alternative-explanation:"+x["explanationId"];nodes.append({"id":eid,"kind":"alternative-explanation","label":x["title"],"status":x["status"],"fingerprint":x["explanationFingerprint"]});edges.append({"id":"alternative-question:"+x["explanationId"],"kind":"alternative-explanation-for","from":eid,"to":"causal-question:"+x["questionId"]})
        for i,r in enumerate(x["hypothesisRefs"]):
            ref=str(r.get("ref") or r.get("hypothesisRef") or ""); fp=str(r.get("fingerprint") or r.get("hypothesisFingerprint") or "")
            if ref:nodes.append({"id":ref,"kind":"hypothesis-ref","externalCanonicalReference":True,"objectFingerprint":fp});edges.append({"id":f"alternative-hypothesis:{x['explanationId']}:{i}","kind":"references-hypothesis","from":eid,"to":ref})
    for a in m["identificationAssumptions"]:
        aid="identification-assumption:"+a["assumptionId"];nodes.append({"id":aid,"kind":"identification-assumption","label":a["assumptionType"],"status":a["status"],"fingerprint":a["assumptionFingerprint"]});edges.append({"id":"assumption-question:"+a["assumptionId"],"kind":"assumption-for","from":aid,"to":"causal-question:"+a["questionId"]})
    for h in m["handoffs"]:
        hid="causal-handoff:"+h["handoffId"];nodes.append({"id":hid,"kind":"causal-analysis-handoff","label":h["method"],"destination":h["destinationProduct"],"fingerprint":h["handoffFingerprint"]});edges.append({"id":"handoff-question:"+h["handoffId"],"kind":"analysis-handoff-for","from":"causal-question:"+h["questionId"],"to":hid})
    for r in m["resultBindings"]:
        nodes.append({"id":r["resultRef"],"kind":r["resultKind"],"externalCanonicalReference":True,"resultFingerprint":r["resultFingerprint"]});source="causal-handoff:"+r["handoffId"] if r["handoffId"] else "causal-question:"+r["questionId"];edges.append({"id":"result-binding:"+r["bindingId"],"kind":"causal-result","from":source,"to":r["resultRef"]})
    seen=set();nodes=[n for n in nodes if not (n["id"] in seen or seen.add(n["id"]))]
    payload={"schema":GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"automaticCausalityInference":False,"automaticCausalDiscovery":False,"automaticAlternativeExplanationRanking":False};payload["graphFingerprint"]=sha256_hex(payload);return payload

def diagnostics(db,user_key,project_id):
    m=manifest(db,user_key,project_id);issues=[]
    sc=Counter(x["questionId"] for x in m["structures"]); ec=Counter(x["questionId"] for x in m["alternativeExplanations"]); ac=Counter(x["questionId"] for x in m["identificationAssumptions"]); hc=Counter(x["questionId"] for x in m["handoffs"]); rc=Counter(x["questionId"] for x in m["resultBindings"])
    for q in m["questions"]:
        qid=q["questionId"]
        if sc.get(qid,0)==0: issues.append({"code":"causal-question-no-structure","severity":"review","questionId":qid,"message":"No explicit causal structure is recorded."})
        if ec.get(qid,0)==0: issues.append({"code":"causal-question-no-alternative-explanation","severity":"review","questionId":qid,"message":"No alternative explanation is recorded."})
        if ac.get(qid,0)==0: issues.append({"code":"causal-question-no-identification-assumptions","severity":"review","questionId":qid,"message":"No explicit identification assumptions are recorded."})
        if hc.get(qid,0)==0: issues.append({"code":"causal-question-no-analysis-handoff","severity":"info","questionId":qid,"message":"No specialist causal-analysis handoff is recorded."})
        if rc.get(qid,0)==0: issues.append({"code":"causal-question-no-results","severity":"info","questionId":qid,"message":"No causal-analysis result reference is bound."})
    for s in m["structures"]:
        roles=Counter(str(v.get("role") or "other") for v in s["variables"])
        if roles.get("exposure",0)==0:issues.append({"code":"causal-structure-no-exposure","severity":"review","structureId":s["structureId"],"message":"Structure has no variable explicitly marked as exposure."})
        if roles.get("outcome",0)==0:issues.append({"code":"causal-structure-no-outcome","severity":"review","structureId":s["structureId"],"message":"Structure has no variable explicitly marked as outcome."})
    for a in m["identificationAssumptions"]:
        if a["status"] in ("challenged","violated","unknown"):issues.append({"code":"causal-identification-assumption-"+a["status"],"severity":"review","assumptionId":a["assumptionId"],"message":"Identification assumption requires explicit researcher review."})
    result_by_handoff=Counter(x["handoffId"] for x in m["resultBindings"] if x["handoffId"])
    for h in m["handoffs"]:
        if result_by_handoff.get(h["handoffId"],0)==0:issues.append({"code":"causal-handoff-no-result","severity":"info","handoffId":h["handoffId"],"message":"No returned result is bound to this causal-analysis handoff."})
    kinds=Counter(x["resultKind"] for x in m["resultBindings"])
    if m["resultBindings"] and not any(kinds.get(x,0) for x in ("falsification-test","placebo-test","robustness-check","sensitivity-diagnostic")):issues.append({"code":"causal-results-no-falsification-or-robustness-diagnostic","severity":"info","message":"Causal results are present without an explicit falsification, placebo, robustness, or sensitivity diagnostic binding."})
    payload={"schema":DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"causalResultsModelConditional":True,"automaticResolution":False,"automaticCausalityInference":False,"automaticIdentificationClaim":False,"automaticAlternativeExplanationRanking":False,"automaticEvidenceRanking":False,"automaticTruthDetermination":False};payload["diagnosticsFingerprint"]=sha256_hex(payload);return payload

def analysis(db,user_key,project_id):
    m=manifest(db,user_key,project_id); g=graph(db,user_key,project_id); d=diagnostics(db,user_key,project_id)
    payload={"schema":ANALYSIS_SCHEMA,"projectId":project_id,"manifest":m,"graph":g,"diagnostics":d,"causalResultsModelConditional":True,"alternativeExplanationsPreserved":True,"humanReviewRequired":True};payload["analysisFingerprint"]=sha256_hex(payload);return payload

def create_snapshot(db,user_key,project_id,p:CausalInvestigationSnapshotRequest):
    a=analysis(db,user_key,project_id); g=a["graph"] if p.includeGraph else None; ctx={"analysis":dict(a,graph=g)}; fp=sha256_hex(ctx);m=a["manifest"];d=a["diagnostics"];c=m["counts"]
    row=CausalInvestigationSnapshot(user_key=user_key,snapshot_id="causal-snapshot-"+uuid4().hex[:24],project_id=project_id,analysis_fingerprint=a["analysisFingerprint"],manifest_fingerprint=m["manifestFingerprint"],graph_fingerprint=(g or {}).get("graphFingerprint",""),diagnostics_fingerprint=d["diagnosticsFingerprint"],snapshot_fingerprint=fp,question_count=c["questions"],structure_count=c["structures"],explanation_count=c["alternativeExplanations"],assumption_count=c["identificationAssumptions"],handoff_count=c["handoffs"],result_binding_count=c["resultBindings"],issue_count=d["issueCount"],context_json=ctx);db.add(row);db.flush();return snapshot_metadata(row)
def snapshot_metadata(r): return {"schema":SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"analysisFingerprint":r.analysis_fingerprint,"manifestFingerprint":r.manifest_fingerprint,"graphFingerprint":r.graph_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"questionCount":r.question_count,"structureCount":r.structure_count,"alternativeExplanationCount":r.explanation_count,"identificationAssumptionCount":r.assumption_count,"handoffCount":r.handoff_count,"resultBindingCount":r.result_binding_count,"issueCount":r.issue_count,"createdAt":iso(r.created_at)}
def list_snapshots(db,user_key,project_id,limit=100):
    q=select(CausalInvestigationSnapshot).where(CausalInvestigationSnapshot.user_key==user_key,CausalInvestigationSnapshot.project_id==project_id).order_by(CausalInvestigationSnapshot.created_at.desc()).limit(limit);return [snapshot_metadata(x) for x in db.scalars(q).all()]
