from __future__ import annotations
from collections import Counter
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (
    ProjectHead, PredictiveScenarioHead, PredictiveScenarioRevision, PredictiveModelBinding,
    PredictiveForecastRequest, PredictiveForecastResultBinding, PredictiveScenarioComparison,
    PredictiveInvestigationSnapshot,
)
from .utils import iso, sha256_hex

PREDICTIVE_WORKSPACE_SCHEMA="sc-workspace-predictive-investigation-scenario-modeling-workspace/1.0"
SCENARIO_REQUEST_SCHEMA="sc-workspace-predictive-scenario-request/1.0"
SCENARIO_SCHEMA="sc-workspace-predictive-scenario/1.0"
MODEL_BINDING_REQUEST_SCHEMA="sc-workspace-predictive-model-binding-request/1.0"
MODEL_BINDING_SCHEMA="sc-workspace-predictive-model-binding/1.0"
FORECAST_REQUEST_SCHEMA="sc-workspace-predictive-forecast-request/1.0"
FORECAST_SCHEMA="sc-workspace-predictive-forecast/1.0"
RESULT_REQUEST_SCHEMA="sc-workspace-predictive-forecast-result-binding-request/1.0"
RESULT_SCHEMA="sc-workspace-predictive-forecast-result-binding/1.0"
COMPARISON_REQUEST_SCHEMA="sc-workspace-predictive-scenario-comparison-request/1.0"
COMPARISON_SCHEMA="sc-workspace-predictive-scenario-comparison/1.0"
MANIFEST_SCHEMA="sc-workspace-predictive-investigation-manifest/1.0"
GRAPH_SCHEMA="sc-workspace-predictive-investigation-graph/1.0"
DIAGNOSTICS_SCHEMA="sc-workspace-predictive-investigation-diagnostics/1.0"
SNAPSHOT_REQUEST_SCHEMA="sc-workspace-predictive-investigation-snapshot-request/1.0"
SNAPSHOT_SCHEMA="sc-workspace-predictive-investigation-snapshot/1.0"

REVIEW_STATES=("open","under-review","documented","contested","unresolved","closed")
SCENARIO_KINDS=("baseline","counterfactual","stress","policy","intervention","alternative","exploratory","custom")
MODEL_FAMILIES=("time-series","regression","bayesian","state-space","survival","machine-learning","simulation","ensemble","causal-forecast","custom")
DESTINATIONS=("workbench","research-lab","catalyst-analytics-r","platform-core")
FORECAST_KINDS=("point","interval","distribution","event-probability","trajectory","classification","ranking","scenario-path","custom")
RESULT_KINDS=("forecast","prediction-interval","credible-interval","probability","trajectory","calibration","backtest","error-metric","scenario-comparison","diagnostic","other")
COMPARISON_RELATIONS=("compare","stress-test","counterfactual-contrast","scenario-delta","sensitivity-contrast","custom")

class PredictiveScenarioRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-scenario-request/1.0"]
    scenarioId:str=Field(default="",max_length=160)
    projectId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    description:str=Field(default="",max_length=12000)
    scenarioKind:str=Field(default="exploratory",max_length=80)
    horizon:str=Field(default="",max_length=500)
    assumptions:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    inputRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=2000)
    causalQuestionRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=500)
    uncertaintyAssessmentRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=500)
    reviewState:str=Field(default="open",max_length=40)
    expectedRevision:int|None=Field(default=None,ge=0)
    metadata:dict[str,Any]=Field(default_factory=dict)

class PredictiveModelBindingRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-model-binding-request/1.0"]
    scenarioId:str=Field(min_length=1,max_length=160)
    modelFamily:str=Field(min_length=1,max_length=120)
    modelRef:str=Field(min_length=1,max_length=2000)
    modelFingerprint:str=Field(min_length=8,max_length=128)
    trainingDataRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=2000)
    featureRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=2000)
    environmentRef:str=Field(default="",max_length=2000)
    environmentFingerprint:str=Field(default="",max_length=128)
    metadata:dict[str,Any]=Field(default_factory=dict)

class PredictiveForecastRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-forecast-request/1.0"]
    scenarioId:str=Field(min_length=1,max_length=160)
    modelBindingId:str=Field(default="",max_length=96)
    forecastKind:str=Field(default="distribution",max_length=120)
    destinationProduct:str=Field(default="catalyst-analytics-r",max_length=80)
    targetRef:str=Field(default="",max_length=2000)
    horizon:str=Field(default="",max_length=500)
    configuration:dict[str,Any]=Field(default_factory=dict)
    calibrationPlan:dict[str,Any]=Field(default_factory=dict)
    backtestPlan:dict[str,Any]=Field(default_factory=dict)
    externalHandoffRef:str=Field(default="",max_length=2000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class PredictiveForecastResultBindingRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-forecast-result-binding-request/1.0"]
    scenarioId:str=Field(min_length=1,max_length=160)
    forecastRequestId:str=Field(default="",max_length=96)
    resultKind:str=Field(min_length=1,max_length=100)
    resultRef:str=Field(min_length=1,max_length=2000)
    resultFingerprint:str=Field(min_length=8,max_length=128)
    modelConditional:bool=True
    calibrationRef:str=Field(default="",max_length=2000)
    calibrationFingerprint:str=Field(default="",max_length=128)
    backtestRef:str=Field(default="",max_length=2000)
    backtestFingerprint:str=Field(default="",max_length=128)
    note:str=Field(default="",max_length=12000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class PredictiveScenarioComparisonRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-scenario-comparison-request/1.0"]
    projectId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    relation:str=Field(default="compare",max_length=80)
    scenarioIds:list[str]=Field(min_length=2,max_length=100)
    resultRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    note:str=Field(default="",max_length=12000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class PredictiveInvestigationSnapshotRequestModel(BaseModel):
    schema:Literal["sc-workspace-predictive-investigation-snapshot-request/1.0"]
    includeGraph:bool=True


def profile()->dict[str,Any]:
    return {
      "schema":PREDICTIVE_WORKSPACE_SCHEMA,"workspaceVersion":"3.19.0",
      "release":"Predictive Investigation & Scenario Modeling Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"canonicalEvidenceAuthorityPreserved":True,
      "explicitScenarioAssumptions":True,"modelFingerprintPinning":True,"causalContextReferences":True,
      "uncertaintyContextReferences":True,"predictiveHandoffs":True,"forecastResultBindings":True,
      "calibrationAndBacktestReferences":True,"modelConditionalForecasts":True,"immutablePredictiveSnapshots":True,
      "supportedModelFamilies":list(MODEL_FAMILIES),"supportedDestinations":list(DESTINATIONS),
      "automaticForecastExecution":False,"automaticScenarioSelection":False,"automaticModelSelection":False,
      "automaticModelRetraining":False,"automaticProbabilityAsTruth":False,"automaticForecastAsTruth":False,
      "automaticEvidenceRanking":False,"automaticCausalityInference":False,"automaticTruthDetermination":False,
      "automaticCulpabilityInference":False,"automaticNarrativeSelection":False,"humanReviewRequired":True,
    }


def _project(db,user_key,project_id): return db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
def _scenario(db,user_key,scenario_id): return db.get(PredictiveScenarioHead,{"user_key":user_key,"scenario_id":scenario_id})

def _refs_pinned(items:list[dict[str,Any]],label:str):
    for item in items:
        ref=str(item.get("ref") or item.get("objectRef") or item.get("evidenceRef") or item.get("questionRef") or item.get("assessmentRef") or "")
        fp=str(item.get("fingerprint") or item.get("objectFingerprint") or item.get("evidenceFingerprint") or item.get("questionFingerprint") or item.get("assessmentFingerprint") or "")
        if ref and len(fp)<8: raise ValueError(f"{label} reference fingerprint required")

def scenario_metadata(r):
    return {"schema":SCENARIO_SCHEMA,"scenarioId":r.scenario_id,"projectId":r.project_id,"title":r.title,"description":r.description,"scenarioKind":r.scenario_kind,"horizon":r.horizon,"assumptions":r.assumptions_json or [],"inputRefs":r.input_refs_json or [],"causalQuestionRefs":r.causal_question_refs_json or [],"uncertaintyAssessmentRefs":r.uncertainty_assessment_refs_json or [],"reviewState":r.review_state,"revision":r.revision,"scenarioFingerprint":r.scenario_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def store_scenario(db:Session,user_key:str,p:PredictiveScenarioRequestModel):
    if not _project(db,user_key,p.projectId): raise KeyError(p.projectId)
    if p.scenarioKind not in SCENARIO_KINDS: raise ValueError("unsupported predictive scenario kind")
    if p.reviewState not in REVIEW_STATES: raise ValueError("unsupported predictive scenario review state")
    _refs_pinned(p.inputRefs,"input"); _refs_pinned(p.causalQuestionRefs,"causal question"); _refs_pinned(p.uncertaintyAssessmentRefs,"uncertainty assessment")
    row=_scenario(db,user_key,p.scenarioId) if p.scenarioId else None
    if row and row.project_id!=p.projectId: raise ValueError("predictive scenario project mismatch")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("predictive scenario revision conflict")
    sid=p.scenarioId or "predictive-scenario-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"scenarioId":sid,"projectId":p.projectId,"revision":rev,"title":p.title,"description":p.description,"scenarioKind":p.scenarioKind,"horizon":p.horizon,"assumptions":p.assumptions,"inputRefs":p.inputRefs,"causalQuestionRefs":p.causalQuestionRefs,"uncertaintyAssessmentRefs":p.uncertaintyAssessmentRefs,"reviewState":p.reviewState,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,title=p.title,description=p.description,scenario_kind=p.scenarioKind,horizon=p.horizon,assumptions_json=p.assumptions,input_refs_json=p.inputRefs,causal_question_refs_json=p.causalQuestionRefs,uncertainty_assessment_refs_json=p.uncertaintyAssessmentRefs,review_state=p.reviewState,revision=rev,scenario_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=PredictiveScenarioHead(user_key=user_key,scenario_id=sid,**vals); db.add(row)
    rvals=dict(vals); rvals.pop("revision",None)
    db.add(PredictiveScenarioRevision(user_key=user_key,scenario_id=sid,revision=rev,**rvals)); db.flush(); return scenario_metadata(row)

def list_scenarios(db,user_key,project_id=None,scenario_kind=None,limit=1000):
    q=select(PredictiveScenarioHead).where(PredictiveScenarioHead.user_key==user_key)
    if project_id:q=q.where(PredictiveScenarioHead.project_id==project_id)
    if scenario_kind:q=q.where(PredictiveScenarioHead.scenario_kind==scenario_kind)
    return [scenario_metadata(x) for x in db.scalars(q.order_by(PredictiveScenarioHead.updated_at.desc()).limit(limit)).all()]

def get_scenario(db,user_key,scenario_id):
    r=_scenario(db,user_key,scenario_id); return scenario_metadata(r) if r else None

def scenario_revisions(db,user_key,scenario_id,limit=100):
    q=select(PredictiveScenarioRevision).where(PredictiveScenarioRevision.user_key==user_key,PredictiveScenarioRevision.scenario_id==scenario_id).order_by(PredictiveScenarioRevision.revision.desc()).limit(limit)
    return [{"schema":SCENARIO_SCHEMA,"scenarioId":r.scenario_id,"projectId":r.project_id,"title":r.title,"description":r.description,"scenarioKind":r.scenario_kind,"horizon":r.horizon,"assumptions":r.assumptions_json or [],"inputRefs":r.input_refs_json or [],"causalQuestionRefs":r.causal_question_refs_json or [],"uncertaintyAssessmentRefs":r.uncertainty_assessment_refs_json or [],"reviewState":r.review_state,"revision":r.revision,"scenarioFingerprint":r.scenario_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)} for r in db.scalars(q).all()]

def create_model_binding(db,user_key,p:PredictiveModelBindingRequestModel):
    sc=_scenario(db,user_key,p.scenarioId)
    if sc is None: raise KeyError(p.scenarioId)
    if p.modelFamily not in MODEL_FAMILIES: raise ValueError("unsupported predictive model family")
    _refs_pinned(p.trainingDataRefs,"training data"); _refs_pinned(p.featureRefs,"feature")
    if p.environmentRef and len(p.environmentFingerprint)<8: raise ValueError("environment fingerprint required")
    fp=sha256_hex({"projectId":sc.project_id,"scenarioId":p.scenarioId,"modelFamily":p.modelFamily,"modelRef":p.modelRef,"modelFingerprint":p.modelFingerprint,"trainingDataRefs":p.trainingDataRefs,"featureRefs":p.featureRefs,"environmentRef":p.environmentRef,"environmentFingerprint":p.environmentFingerprint,"metadata":p.metadata})
    row=PredictiveModelBinding(user_key=user_key,binding_id="predictive-model-binding-"+uuid4().hex[:24],project_id=sc.project_id,scenario_id=p.scenarioId,model_family=p.modelFamily,model_ref=p.modelRef,model_fingerprint=p.modelFingerprint,training_data_refs_json=p.trainingDataRefs,feature_refs_json=p.featureRefs,environment_ref=p.environmentRef,environment_fingerprint=p.environmentFingerprint,binding_fingerprint=fp,metadata_json=p.metadata); db.add(row); db.flush(); return model_binding_metadata(row)

def model_binding_metadata(r): return {"schema":MODEL_BINDING_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"scenarioId":r.scenario_id,"modelFamily":r.model_family,"modelRef":r.model_ref,"modelFingerprint":r.model_fingerprint,"trainingDataRefs":r.training_data_refs_json or [],"featureRefs":r.feature_refs_json or [],"environmentRef":r.environment_ref,"environmentFingerprint":r.environment_fingerprint,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_model_bindings(db,user_key,project_id=None,scenario_id=None,limit=5000):
    q=select(PredictiveModelBinding).where(PredictiveModelBinding.user_key==user_key)
    if project_id:q=q.where(PredictiveModelBinding.project_id==project_id)
    if scenario_id:q=q.where(PredictiveModelBinding.scenario_id==scenario_id)
    return [model_binding_metadata(x) for x in db.scalars(q.order_by(PredictiveModelBinding.created_at.asc()).limit(limit)).all()]

def create_forecast_request(db,user_key,p:PredictiveForecastRequestModel):
    sc=_scenario(db,user_key,p.scenarioId)
    if sc is None: raise KeyError(p.scenarioId)
    if p.forecastKind not in FORECAST_KINDS: raise ValueError("unsupported forecast kind")
    if p.destinationProduct not in DESTINATIONS: raise ValueError("unsupported forecast destination")
    if p.modelBindingId:
        mb=db.get(PredictiveModelBinding,{"user_key":user_key,"binding_id":p.modelBindingId})
        if mb is None: raise KeyError(p.modelBindingId)
        if mb.scenario_id!=p.scenarioId: raise ValueError("forecast model binding scenario mismatch")
    fp=sha256_hex({"projectId":sc.project_id,"scenarioId":p.scenarioId,"modelBindingId":p.modelBindingId,"forecastKind":p.forecastKind,"destinationProduct":p.destinationProduct,"targetRef":p.targetRef,"horizon":p.horizon,"configuration":p.configuration,"calibrationPlan":p.calibrationPlan,"backtestPlan":p.backtestPlan,"externalHandoffRef":p.externalHandoffRef,"metadata":p.metadata})
    row=PredictiveForecastRequest(user_key=user_key,forecast_request_id="predictive-forecast-"+uuid4().hex[:24],project_id=sc.project_id,scenario_id=p.scenarioId,model_binding_id=p.modelBindingId,forecast_kind=p.forecastKind,destination_product=p.destinationProduct,target_ref=p.targetRef,horizon=p.horizon,configuration_json=p.configuration,calibration_plan_json=p.calibrationPlan,backtest_plan_json=p.backtestPlan,status="ready",forecast_request_fingerprint=fp,external_handoff_ref=p.externalHandoffRef,metadata_json=p.metadata); db.add(row); db.flush(); return forecast_request_metadata(row)

def forecast_request_metadata(r): return {"schema":FORECAST_SCHEMA,"forecastRequestId":r.forecast_request_id,"projectId":r.project_id,"scenarioId":r.scenario_id,"modelBindingId":r.model_binding_id,"forecastKind":r.forecast_kind,"destinationProduct":r.destination_product,"targetRef":r.target_ref,"horizon":r.horizon,"configuration":r.configuration_json or {},"calibrationPlan":r.calibration_plan_json or {},"backtestPlan":r.backtest_plan_json or {},"status":r.status,"forecastRequestFingerprint":r.forecast_request_fingerprint,"externalHandoffRef":r.external_handoff_ref,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_forecast_requests(db,user_key,project_id=None,scenario_id=None,limit=5000):
    q=select(PredictiveForecastRequest).where(PredictiveForecastRequest.user_key==user_key)
    if project_id:q=q.where(PredictiveForecastRequest.project_id==project_id)
    if scenario_id:q=q.where(PredictiveForecastRequest.scenario_id==scenario_id)
    return [forecast_request_metadata(x) for x in db.scalars(q.order_by(PredictiveForecastRequest.created_at.asc()).limit(limit)).all()]

def create_result_binding(db,user_key,p:PredictiveForecastResultBindingRequestModel):
    sc=_scenario(db,user_key,p.scenarioId)
    if sc is None: raise KeyError(p.scenarioId)
    if p.resultKind not in RESULT_KINDS: raise ValueError("unsupported predictive result kind")
    if p.forecastRequestId:
        fr=db.get(PredictiveForecastRequest,{"user_key":user_key,"forecast_request_id":p.forecastRequestId})
        if fr is None: raise KeyError(p.forecastRequestId)
        if fr.scenario_id!=p.scenarioId: raise ValueError("forecast result scenario mismatch")
    if p.calibrationRef and len(p.calibrationFingerprint)<8: raise ValueError("calibration fingerprint required")
    if p.backtestRef and len(p.backtestFingerprint)<8: raise ValueError("backtest fingerprint required")
    fp=sha256_hex({"projectId":sc.project_id,"scenarioId":p.scenarioId,"forecastRequestId":p.forecastRequestId,"resultKind":p.resultKind,"resultRef":p.resultRef,"resultFingerprint":p.resultFingerprint,"modelConditional":p.modelConditional,"calibrationRef":p.calibrationRef,"calibrationFingerprint":p.calibrationFingerprint,"backtestRef":p.backtestRef,"backtestFingerprint":p.backtestFingerprint,"note":p.note,"metadata":p.metadata})
    row=PredictiveForecastResultBinding(user_key=user_key,binding_id="predictive-result-"+uuid4().hex[:24],project_id=sc.project_id,scenario_id=p.scenarioId,forecast_request_id=p.forecastRequestId,result_kind=p.resultKind,result_ref=p.resultRef,result_fingerprint=p.resultFingerprint,model_conditional=p.modelConditional,calibration_ref=p.calibrationRef,calibration_fingerprint=p.calibrationFingerprint,backtest_ref=p.backtestRef,backtest_fingerprint=p.backtestFingerprint,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata); db.add(row); db.flush(); return result_binding_metadata(row)

def result_binding_metadata(r): return {"schema":RESULT_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"scenarioId":r.scenario_id,"forecastRequestId":r.forecast_request_id,"resultKind":r.result_kind,"resultRef":r.result_ref,"resultFingerprint":r.result_fingerprint,"modelConditional":bool(r.model_conditional),"calibrationRef":r.calibration_ref,"calibrationFingerprint":r.calibration_fingerprint,"backtestRef":r.backtest_ref,"backtestFingerprint":r.backtest_fingerprint,"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_result_bindings(db,user_key,project_id=None,scenario_id=None,limit=5000):
    q=select(PredictiveForecastResultBinding).where(PredictiveForecastResultBinding.user_key==user_key)
    if project_id:q=q.where(PredictiveForecastResultBinding.project_id==project_id)
    if scenario_id:q=q.where(PredictiveForecastResultBinding.scenario_id==scenario_id)
    return [result_binding_metadata(x) for x in db.scalars(q.order_by(PredictiveForecastResultBinding.created_at.asc()).limit(limit)).all()]

def create_comparison(db,user_key,p:PredictiveScenarioComparisonRequestModel):
    if not _project(db,user_key,p.projectId): raise KeyError(p.projectId)
    if p.relation not in COMPARISON_RELATIONS: raise ValueError("unsupported predictive scenario comparison relation")
    if len(set(p.scenarioIds))<2: raise ValueError("scenario comparison requires at least two distinct scenarios")
    for sid in p.scenarioIds:
        sc=_scenario(db,user_key,sid)
        if sc is None: raise KeyError(sid)
        if sc.project_id!=p.projectId: raise ValueError("scenario comparison project mismatch")
    _refs_pinned(p.resultRefs,"result")
    fp=sha256_hex({"projectId":p.projectId,"title":p.title,"relation":p.relation,"scenarioIds":p.scenarioIds,"resultRefs":p.resultRefs,"note":p.note,"metadata":p.metadata})
    row=PredictiveScenarioComparison(user_key=user_key,comparison_id="predictive-comparison-"+uuid4().hex[:24],project_id=p.projectId,title=p.title,relation=p.relation,scenario_ids_json=p.scenarioIds,result_refs_json=p.resultRefs,note=p.note,comparison_fingerprint=fp,metadata_json=p.metadata); db.add(row); db.flush(); return comparison_metadata(row)

def comparison_metadata(r): return {"schema":COMPARISON_SCHEMA,"comparisonId":r.comparison_id,"projectId":r.project_id,"title":r.title,"relation":r.relation,"scenarioIds":r.scenario_ids_json or [],"resultRefs":r.result_refs_json or [],"note":r.note,"comparisonFingerprint":r.comparison_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}

def list_comparisons(db,user_key,project_id=None,limit=5000):
    q=select(PredictiveScenarioComparison).where(PredictiveScenarioComparison.user_key==user_key)
    if project_id:q=q.where(PredictiveScenarioComparison.project_id==project_id)
    return [comparison_metadata(x) for x in db.scalars(q.order_by(PredictiveScenarioComparison.created_at.asc()).limit(limit)).all()]

def manifest(db,user_key,project_id):
    if not _project(db,user_key,project_id): raise KeyError(project_id)
    scenarios=list_scenarios(db,user_key,project_id,limit=10000); models=list_model_bindings(db,user_key,project_id,limit=10000); forecasts=list_forecast_requests(db,user_key,project_id,limit=10000); results=list_result_bindings(db,user_key,project_id,limit=10000); comparisons=list_comparisons(db,user_key,project_id,limit=10000)
    counts={"scenarios":len(scenarios),"modelBindings":len(models),"forecastRequests":len(forecasts),"resultBindings":len(results),"comparisons":len(comparisons)}
    item={"schema":MANIFEST_SCHEMA,"projectId":project_id,"counts":counts,"scenarioKinds":dict(Counter(x["scenarioKind"] for x in scenarios)),"modelFamilies":dict(Counter(x["modelFamily"] for x in models)),"forecastKinds":dict(Counter(x["forecastKind"] for x in forecasts)),"referenceFirst":True,"canonicalEvidenceAuthorityPreserved":True}; item["manifestFingerprint"]=sha256_hex(item); return item

def graph(db,user_key,project_id):
    m=manifest(db,user_key,project_id); scenarios=list_scenarios(db,user_key,project_id,limit=10000); models=list_model_bindings(db,user_key,project_id,limit=10000); forecasts=list_forecast_requests(db,user_key,project_id,limit=10000); results=list_result_bindings(db,user_key,project_id,limit=10000); comparisons=list_comparisons(db,user_key,project_id,limit=10000)
    nodes=[]; edges=[]
    for x in scenarios:nodes.append({"id":x["scenarioId"],"kind":"scenario","label":x["title"],"fingerprint":x["scenarioFingerprint"]})
    for x in models:
        nodes.append({"id":x["bindingId"],"kind":"model-binding","label":x["modelFamily"],"fingerprint":x["bindingFingerprint"]}); edges.append({"from":x["scenarioId"],"to":x["bindingId"],"relation":"uses-model"})
    for x in forecasts:
        nodes.append({"id":x["forecastRequestId"],"kind":"forecast-request","label":x["forecastKind"],"fingerprint":x["forecastRequestFingerprint"]}); edges.append({"from":x["scenarioId"],"to":x["forecastRequestId"],"relation":"requests-forecast"})
        if x["modelBindingId"]: edges.append({"from":x["modelBindingId"],"to":x["forecastRequestId"],"relation":"executes-with"})
    for x in results:
        nodes.append({"id":x["bindingId"],"kind":"forecast-result","label":x["resultKind"],"fingerprint":x["bindingFingerprint"]}); edges.append({"from":x["scenarioId"],"to":x["bindingId"],"relation":"has-result"})
        if x["forecastRequestId"]: edges.append({"from":x["forecastRequestId"],"to":x["bindingId"],"relation":"returns"})
    for x in comparisons:
        nodes.append({"id":x["comparisonId"],"kind":"scenario-comparison","label":x["title"],"fingerprint":x["comparisonFingerprint"]})
        for sid in x["scenarioIds"]: edges.append({"from":sid,"to":x["comparisonId"],"relation":x["relation"]})
    item={"schema":GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"nodeCount":len(nodes),"edgeCount":len(edges),"manifestFingerprint":m["manifestFingerprint"]}; item["graphFingerprint"]=sha256_hex(item); return item

def diagnostics(db,user_key,project_id):
    scenarios=list_scenarios(db,user_key,project_id,limit=10000); models=list_model_bindings(db,user_key,project_id,limit=10000); forecasts=list_forecast_requests(db,user_key,project_id,limit=10000); results=list_result_bindings(db,user_key,project_id,limit=10000)
    model_scenarios={x["scenarioId"] for x in models}; forecast_scenarios={x["scenarioId"] for x in forecasts}; result_scenarios={x["scenarioId"] for x in results}; issues=[]
    for s in scenarios:
        if not s["assumptions"]: issues.append({"code":"scenario-without-explicit-assumptions","scenarioId":s["scenarioId"],"severity":"warning"})
        if s["scenarioId"] not in model_scenarios: issues.append({"code":"scenario-without-model-binding","scenarioId":s["scenarioId"],"severity":"info"})
        if s["scenarioId"] not in forecast_scenarios: issues.append({"code":"scenario-without-forecast-request","scenarioId":s["scenarioId"],"severity":"info"})
        if s["scenarioId"] in forecast_scenarios and s["scenarioId"] not in result_scenarios: issues.append({"code":"forecast-without-returned-result","scenarioId":s["scenarioId"],"severity":"info"})
    item={"schema":DIAGNOSTICS_SCHEMA,"projectId":project_id,"issueCount":len(issues),"issues":issues,"automaticScenarioSelection":False,"automaticModelSelection":False,"automaticForecastAsTruth":False,"automaticTruthDetermination":False}; item["diagnosticsFingerprint"]=sha256_hex(item); return item

def create_snapshot(db,user_key,project_id,p:PredictiveInvestigationSnapshotRequestModel):
    m=manifest(db,user_key,project_id); g=graph(db,user_key,project_id) if p.includeGraph else {"graphFingerprint":""}; d=diagnostics(db,user_key,project_id)
    fp=sha256_hex({"projectId":project_id,"manifestFingerprint":m["manifestFingerprint"],"graphFingerprint":g.get("graphFingerprint") or "","diagnosticsFingerprint":d["diagnosticsFingerprint"],"counts":m["counts"]})
    c=m["counts"]; row=PredictiveInvestigationSnapshot(user_key=user_key,snapshot_id="predictive-snapshot-"+uuid4().hex[:24],project_id=project_id,manifest_fingerprint=m["manifestFingerprint"],graph_fingerprint=g.get("graphFingerprint") or "",diagnostics_fingerprint=d["diagnosticsFingerprint"],snapshot_fingerprint=fp,scenario_count=c["scenarios"],model_binding_count=c["modelBindings"],forecast_request_count=c["forecastRequests"],result_binding_count=c["resultBindings"],comparison_count=c["comparisons"],issue_count=d["issueCount"],context_json={"manifest":m,"graph":g if p.includeGraph else {},"diagnostics":d}); db.add(row); db.flush(); return snapshot_metadata(row)

def snapshot_metadata(r): return {"schema":SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"manifestFingerprint":r.manifest_fingerprint,"graphFingerprint":r.graph_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"counts":{"scenarios":r.scenario_count,"modelBindings":r.model_binding_count,"forecastRequests":r.forecast_request_count,"resultBindings":r.result_binding_count,"comparisons":r.comparison_count,"issues":r.issue_count},"createdAt":iso(r.created_at)}

def list_snapshots(db,user_key,project_id,limit=100):
    q=select(PredictiveInvestigationSnapshot).where(PredictiveInvestigationSnapshot.user_key==user_key,PredictiveInvestigationSnapshot.project_id==project_id).order_by(PredictiveInvestigationSnapshot.created_at.desc()).limit(limit)
    return [snapshot_metadata(x) for x in db.scalars(q).all()]
