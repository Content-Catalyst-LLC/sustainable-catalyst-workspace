from __future__ import annotations
from collections import Counter
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import (
    ProjectHead, UncertaintyAssessmentHead, UncertaintyAssessmentRevision, UncertaintyParameter,
    UncertaintyScenario, SensitivityAnalysisRequestRecord, ProbabilisticResultBinding,
    UncertaintyInvestigationSnapshot,
)
from .utils import iso, sha256_hex

UNCERTAINTY_WORKSPACE_SCHEMA="sc-workspace-uncertainty-sensitivity-probabilistic-investigation-workspace/1.0"
ASSESSMENT_REQUEST_SCHEMA="sc-workspace-uncertainty-assessment-request/1.0"
ASSESSMENT_SCHEMA="sc-workspace-uncertainty-assessment/1.0"
PARAMETER_REQUEST_SCHEMA="sc-workspace-uncertainty-parameter-request/1.0"
PARAMETER_SCHEMA="sc-workspace-uncertainty-parameter/1.0"
SCENARIO_REQUEST_SCHEMA="sc-workspace-uncertainty-scenario-request/1.0"
SCENARIO_SCHEMA="sc-workspace-uncertainty-scenario/1.0"
SENSITIVITY_REQUEST_SCHEMA="sc-workspace-sensitivity-analysis-request/1.0"
SENSITIVITY_SCHEMA="sc-workspace-sensitivity-analysis/1.0"
RESULT_BINDING_REQUEST_SCHEMA="sc-workspace-probabilistic-result-binding-request/1.0"
RESULT_BINDING_SCHEMA="sc-workspace-probabilistic-result-binding/1.0"
MANIFEST_SCHEMA="sc-workspace-uncertainty-investigation-manifest/1.0"
GRAPH_SCHEMA="sc-workspace-uncertainty-investigation-graph/1.0"
DIAGNOSTICS_SCHEMA="sc-workspace-uncertainty-investigation-diagnostics/1.0"
SNAPSHOT_REQUEST_SCHEMA="sc-workspace-uncertainty-investigation-snapshot-request/1.0"
SNAPSHOT_SCHEMA="sc-workspace-uncertainty-investigation-snapshot/1.0"

METHOD_FAMILIES=("monte-carlo","bootstrap","bayesian","ensemble","analytical","interval","scenario","custom")
DISTRIBUTIONS=("fixed","normal","lognormal","uniform","triangular","beta","gamma","poisson","empirical","discrete","interval","custom")
PARAMETER_ROLES=("input","assumption","boundary","measurement","latent","calibration","scenario","other")
SENSITIVITY_METHODS=("sobol","morris","local","one-at-a-time","variance-decomposition","regression","correlation","custom")
DESTINATIONS=("workbench","research-lab","catalyst-analytics-r","platform-core")
RESULT_KINDS=("distribution","probability","credible-interval","confidence-interval","prediction-interval","sensitivity-index","scenario-ensemble","calibration-diagnostic","posterior","forecast","other")

class UncertaintyAssessmentRequest(BaseModel):
    schema:Literal["sc-workspace-uncertainty-assessment-request/1.0"]
    assessmentId:str=Field(default="",max_length=160)
    projectId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    objective:str=Field(default="",max_length=8000)
    methodFamily:str=Field(default="monte-carlo")
    assumptions:list[dict[str,Any]]=Field(default_factory=list,max_length=1000)
    configuration:dict[str,Any]=Field(default_factory=dict)
    expectedRevision:int|None=Field(default=None,ge=0)
    metadata:dict[str,Any]=Field(default_factory=dict)

class UncertaintyParameterRequest(BaseModel):
    schema:Literal["sc-workspace-uncertainty-parameter-request/1.0"]
    assessmentId:str=Field(min_length=1,max_length=160)
    name:str=Field(min_length=1,max_length=240)
    role:str=Field(default="input")
    distribution:str=Field(default="fixed")
    distributionParameters:dict[str,Any]=Field(default_factory=dict)
    units:str=Field(default="",max_length=120)
    evidenceRef:str=Field(default="",max_length=2000)
    evidenceFingerprint:str=Field(default="",max_length=128)
    metadata:dict[str,Any]=Field(default_factory=dict)

class UncertaintyScenarioRequest(BaseModel):
    schema:Literal["sc-workspace-uncertainty-scenario-request/1.0"]
    assessmentId:str=Field(min_length=1,max_length=160)
    title:str=Field(min_length=1,max_length=500)
    weight:str=Field(default="",max_length=80)
    parameterOverrides:dict[str,Any]=Field(default_factory=dict)
    evidenceRefs:list[dict[str,Any]]=Field(default_factory=list,max_length=500)
    metadata:dict[str,Any]=Field(default_factory=dict)

class SensitivityAnalysisRequest(BaseModel):
    schema:Literal["sc-workspace-sensitivity-analysis-request/1.0"]
    assessmentId:str=Field(min_length=1,max_length=160)
    method:str=Field(default="sobol")
    destinationProduct:str=Field(default="catalyst-analytics-r")
    outputMetrics:list[str]=Field(default_factory=list,max_length=500)
    configuration:dict[str,Any]=Field(default_factory=dict)
    externalHandoffRef:str=Field(default="",max_length=2000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class ProbabilisticResultBindingRequest(BaseModel):
    schema:Literal["sc-workspace-probabilistic-result-binding-request/1.0"]
    assessmentId:str=Field(min_length=1,max_length=160)
    resultKind:str=Field(min_length=1,max_length=80)
    resultRef:str=Field(min_length=1,max_length=2000)
    resultFingerprint:str=Field(default="",max_length=128)
    interpretationStatus:str=Field(default="reported",max_length=40)
    note:str=Field(default="",max_length=8000)
    metadata:dict[str,Any]=Field(default_factory=dict)

class UncertaintyInvestigationSnapshotRequest(BaseModel):
    schema:Literal["sc-workspace-uncertainty-investigation-snapshot-request/1.0"]
    includeGraph:bool=True


def profile()->dict[str,Any]:
    return {
      "schema":UNCERTAINTY_WORKSPACE_SCHEMA,"workspaceVersion":"3.17.0",
      "release":"Uncertainty, Sensitivity & Probabilistic Investigation Workspace",
      "backendAuthoritative":True,"referenceFirst":True,"canonicalEvidenceAuthorityPreserved":True,
      "explicitDistributionAssumptions":True,"evidencePinnedUncertaintyParameters":True,
      "scenarioEnsembles":True,"sensitivityAnalysisHandoffs":True,"probabilisticResultBindings":True,
      "supportedSensitivityMethods":list(SENSITIVITY_METHODS),"supportedDestinations":list(DESTINATIONS),
      "immutableUncertaintySnapshots":True,"humanReviewRequired":True,
      "automaticProbabilityAsTruth":False,"automaticEvidenceRanking":False,"automaticTruthDetermination":False,
      "automaticCausalityInference":False,"automaticCulpabilityInference":False,"automaticNarrativeSelection":False,
      "automaticSensitivityExecution":False,"automaticDistributionInference":False,
    }

def _project(db,user_key,project_id): return db.get(ProjectHead,{"user_key":user_key,"project_id":project_id})
def _assessment(db,user_key,assessment_id): return db.get(UncertaintyAssessmentHead,{"user_key":user_key,"assessment_id":assessment_id})

def assessment_metadata(r):
    return {"schema":ASSESSMENT_SCHEMA,"assessmentId":r.assessment_id,"projectId":r.project_id,"title":r.title,"objective":r.objective,"methodFamily":r.method_family,"assumptions":r.assumptions_json or [],"configuration":r.configuration_json or {},"revision":r.revision,"assessmentFingerprint":r.assessment_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at),"updatedAt":iso(r.updated_at)}

def store_assessment(db:Session,user_key:str,p:UncertaintyAssessmentRequest):
    if not _project(db,user_key,p.projectId): raise KeyError(p.projectId)
    if p.methodFamily not in METHOD_FAMILIES: raise ValueError("unsupported uncertainty method family")
    row=_assessment(db,user_key,p.assessmentId) if p.assessmentId else None
    if row and row.project_id!=p.projectId: raise ValueError("assessment project mismatch")
    if row and p.expectedRevision is not None and row.revision!=p.expectedRevision: raise ValueError("assessment revision conflict")
    aid=p.assessmentId or "uncertainty-assessment-"+uuid4().hex[:24]; rev=(row.revision+1) if row else 1
    fp=sha256_hex({"assessmentId":aid,"projectId":p.projectId,"revision":rev,"title":p.title,"objective":p.objective,"methodFamily":p.methodFamily,"assumptions":p.assumptions,"configuration":p.configuration,"metadata":p.metadata})
    vals=dict(project_id=p.projectId,title=p.title,objective=p.objective,method_family=p.methodFamily,assumptions_json=p.assumptions,configuration_json=p.configuration,revision=rev,assessment_fingerprint=fp,metadata_json=p.metadata)
    if row:
        for k,v in vals.items(): setattr(row,k,v)
    else:
        row=UncertaintyAssessmentHead(user_key=user_key,assessment_id=aid,**vals); db.add(row)
    revision_vals=dict(vals); revision_vals.pop("revision",None)
    db.add(UncertaintyAssessmentRevision(user_key=user_key,assessment_id=aid,revision=rev,**revision_vals)); db.flush(); return assessment_metadata(row)

def list_assessments(db,user_key,project_id=None,method_family=None,limit=1000):
    q=select(UncertaintyAssessmentHead).where(UncertaintyAssessmentHead.user_key==user_key)
    if project_id:q=q.where(UncertaintyAssessmentHead.project_id==project_id)
    if method_family:q=q.where(UncertaintyAssessmentHead.method_family==method_family)
    return [assessment_metadata(x) for x in db.scalars(q.order_by(UncertaintyAssessmentHead.updated_at.desc()).limit(limit)).all()]

def get_assessment(db,user_key,assessment_id):
    r=_assessment(db,user_key,assessment_id); return assessment_metadata(r) if r else None

def assessment_revisions(db,user_key,assessment_id,limit=100):
    q=select(UncertaintyAssessmentRevision).where(UncertaintyAssessmentRevision.user_key==user_key,UncertaintyAssessmentRevision.assessment_id==assessment_id).order_by(UncertaintyAssessmentRevision.revision.desc()).limit(limit)
    return [{"schema":ASSESSMENT_SCHEMA,"assessmentId":r.assessment_id,"projectId":r.project_id,"title":r.title,"objective":r.objective,"methodFamily":r.method_family,"assumptions":r.assumptions_json or [],"configuration":r.configuration_json or {},"revision":r.revision,"assessmentFingerprint":r.assessment_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)} for r in db.scalars(q).all()]

def create_parameter(db,user_key,p:UncertaintyParameterRequest):
    a=_assessment(db,user_key,p.assessmentId)
    if a is None: raise KeyError(p.assessmentId)
    if p.role not in PARAMETER_ROLES: raise ValueError("unsupported uncertainty parameter role")
    if p.distribution not in DISTRIBUTIONS: raise ValueError("unsupported uncertainty distribution")
    if p.evidenceRef and not p.evidenceFingerprint: raise ValueError("evidence fingerprint required when evidenceRef is supplied")
    fp=sha256_hex({"projectId":a.project_id,"assessmentId":p.assessmentId,"name":p.name,"role":p.role,"distribution":p.distribution,"distributionParameters":p.distributionParameters,"units":p.units,"evidenceRef":p.evidenceRef,"evidenceFingerprint":p.evidenceFingerprint,"metadata":p.metadata})
    row=UncertaintyParameter(user_key=user_key,parameter_id="uncertainty-parameter-"+uuid4().hex[:24],project_id=a.project_id,assessment_id=p.assessmentId,name=p.name,role=p.role,distribution=p.distribution,distribution_parameters_json=p.distributionParameters,units=p.units,evidence_ref=p.evidenceRef,evidence_fingerprint=p.evidenceFingerprint,parameter_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return parameter_metadata(row)

def parameter_metadata(r): return {"schema":PARAMETER_SCHEMA,"parameterId":r.parameter_id,"projectId":r.project_id,"assessmentId":r.assessment_id,"name":r.name,"role":r.role,"distribution":r.distribution,"distributionParameters":r.distribution_parameters_json or {},"units":r.units,"evidenceRef":r.evidence_ref,"evidenceFingerprint":r.evidence_fingerprint,"parameterFingerprint":r.parameter_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_parameters(db,user_key,project_id=None,assessment_id=None,limit=5000):
    q=select(UncertaintyParameter).where(UncertaintyParameter.user_key==user_key)
    if project_id:q=q.where(UncertaintyParameter.project_id==project_id)
    if assessment_id:q=q.where(UncertaintyParameter.assessment_id==assessment_id)
    return [parameter_metadata(x) for x in db.scalars(q.order_by(UncertaintyParameter.created_at.asc()).limit(limit)).all()]

def create_scenario(db,user_key,p:UncertaintyScenarioRequest):
    a=_assessment(db,user_key,p.assessmentId)
    if a is None: raise KeyError(p.assessmentId)
    for ref in p.evidenceRefs:
        if ref.get("ref") and not ref.get("fingerprint"): raise ValueError("scenario evidence fingerprints are required")
    fp=sha256_hex({"projectId":a.project_id,"assessmentId":p.assessmentId,"title":p.title,"weight":p.weight,"parameterOverrides":p.parameterOverrides,"evidenceRefs":p.evidenceRefs,"metadata":p.metadata})
    row=UncertaintyScenario(user_key=user_key,scenario_id="uncertainty-scenario-"+uuid4().hex[:24],project_id=a.project_id,assessment_id=p.assessmentId,title=p.title,weight=p.weight,parameter_overrides_json=p.parameterOverrides,evidence_refs_json=p.evidenceRefs,scenario_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return scenario_metadata(row)
def scenario_metadata(r): return {"schema":SCENARIO_SCHEMA,"scenarioId":r.scenario_id,"projectId":r.project_id,"assessmentId":r.assessment_id,"title":r.title,"weight":r.weight,"parameterOverrides":r.parameter_overrides_json or {},"evidenceRefs":r.evidence_refs_json or [],"scenarioFingerprint":r.scenario_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_scenarios(db,user_key,project_id=None,assessment_id=None,limit=5000):
    q=select(UncertaintyScenario).where(UncertaintyScenario.user_key==user_key)
    if project_id:q=q.where(UncertaintyScenario.project_id==project_id)
    if assessment_id:q=q.where(UncertaintyScenario.assessment_id==assessment_id)
    return [scenario_metadata(x) for x in db.scalars(q.order_by(UncertaintyScenario.created_at.asc()).limit(limit)).all()]

def create_sensitivity_request(db,user_key,p:SensitivityAnalysisRequest):
    a=_assessment(db,user_key,p.assessmentId)
    if a is None: raise KeyError(p.assessmentId)
    if p.method not in SENSITIVITY_METHODS: raise ValueError("unsupported sensitivity method")
    if p.destinationProduct not in DESTINATIONS: raise ValueError("unsupported specialist destination")
    fp=sha256_hex({"projectId":a.project_id,"assessmentId":p.assessmentId,"method":p.method,"destinationProduct":p.destinationProduct,"outputMetrics":p.outputMetrics,"configuration":p.configuration,"externalHandoffRef":p.externalHandoffRef,"metadata":p.metadata})
    row=SensitivityAnalysisRequestRecord(user_key=user_key,request_id="sensitivity-request-"+uuid4().hex[:24],project_id=a.project_id,assessment_id=p.assessmentId,method=p.method,destination_product=p.destinationProduct,output_metrics_json=p.outputMetrics,configuration_json=p.configuration,status="ready",request_fingerprint=fp,external_handoff_ref=p.externalHandoffRef,metadata_json=p.metadata);db.add(row);db.flush();return sensitivity_metadata(row)
def sensitivity_metadata(r): return {"schema":SENSITIVITY_SCHEMA,"requestId":r.request_id,"projectId":r.project_id,"assessmentId":r.assessment_id,"method":r.method,"destinationProduct":r.destination_product,"outputMetrics":r.output_metrics_json or [],"configuration":r.configuration_json or {},"status":r.status,"requestFingerprint":r.request_fingerprint,"externalHandoffRef":r.external_handoff_ref,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_sensitivity_requests(db,user_key,project_id=None,assessment_id=None,limit=5000):
    q=select(SensitivityAnalysisRequestRecord).where(SensitivityAnalysisRequestRecord.user_key==user_key)
    if project_id:q=q.where(SensitivityAnalysisRequestRecord.project_id==project_id)
    if assessment_id:q=q.where(SensitivityAnalysisRequestRecord.assessment_id==assessment_id)
    return [sensitivity_metadata(x) for x in db.scalars(q.order_by(SensitivityAnalysisRequestRecord.created_at.asc()).limit(limit)).all()]

def create_result_binding(db,user_key,p:ProbabilisticResultBindingRequest):
    a=_assessment(db,user_key,p.assessmentId)
    if a is None: raise KeyError(p.assessmentId)
    if p.resultKind not in RESULT_KINDS: raise ValueError("unsupported probabilistic result kind")
    if not p.resultFingerprint: raise ValueError("result fingerprint required")
    fp=sha256_hex({"projectId":a.project_id,"assessmentId":p.assessmentId,"resultKind":p.resultKind,"resultRef":p.resultRef,"resultFingerprint":p.resultFingerprint,"interpretationStatus":p.interpretationStatus,"note":p.note,"metadata":p.metadata})
    row=ProbabilisticResultBinding(user_key=user_key,binding_id="probabilistic-result-"+uuid4().hex[:24],project_id=a.project_id,assessment_id=p.assessmentId,result_kind=p.resultKind,result_ref=p.resultRef,result_fingerprint=p.resultFingerprint,interpretation_status=p.interpretationStatus,note=p.note,binding_fingerprint=fp,metadata_json=p.metadata);db.add(row);db.flush();return result_metadata(row)
def result_metadata(r): return {"schema":RESULT_BINDING_SCHEMA,"bindingId":r.binding_id,"projectId":r.project_id,"assessmentId":r.assessment_id,"resultKind":r.result_kind,"resultRef":r.result_ref,"resultFingerprint":r.result_fingerprint,"interpretationStatus":r.interpretation_status,"note":r.note,"bindingFingerprint":r.binding_fingerprint,"metadata":r.metadata_json or {},"createdAt":iso(r.created_at)}
def list_result_bindings(db,user_key,project_id=None,assessment_id=None,limit=5000):
    q=select(ProbabilisticResultBinding).where(ProbabilisticResultBinding.user_key==user_key)
    if project_id:q=q.where(ProbabilisticResultBinding.project_id==project_id)
    if assessment_id:q=q.where(ProbabilisticResultBinding.assessment_id==assessment_id)
    return [result_metadata(x) for x in db.scalars(q.order_by(ProbabilisticResultBinding.created_at.asc()).limit(limit)).all()]

def manifest(db,user_key,project_id):
    if not _project(db,user_key,project_id): raise KeyError(project_id)
    assessments=list_assessments(db,user_key,project_id,None,5000); params=list_parameters(db,user_key,project_id,None,10000); scenarios=list_scenarios(db,user_key,project_id,None,10000); sensitivity=list_sensitivity_requests(db,user_key,project_id,None,10000); results=list_result_bindings(db,user_key,project_id,None,10000)
    counts={"assessments":len(assessments),"parameters":len(params),"scenarios":len(scenarios),"sensitivityRequests":len(sensitivity),"resultBindings":len(results)}
    payload={"schema":MANIFEST_SCHEMA,"projectId":project_id,"counts":counts,"assessments":assessments,"parameters":params,"scenarios":scenarios,"sensitivityRequests":sensitivity,"resultBindings":results,"probabilityIsNotTruth":True,"canonicalEvidenceAuthorityPreserved":True,"automaticSensitivityExecution":False}
    payload["manifestFingerprint"]=sha256_hex(payload);return payload

def graph(db,user_key,project_id):
    m=manifest(db,user_key,project_id);nodes=[];edges=[]
    for a in m["assessments"]:nodes.append({"id":"uncertainty:"+a["assessmentId"],"kind":"uncertainty-assessment","label":a["title"],"fingerprint":a["assessmentFingerprint"]})
    for p in m["parameters"]:
        pid="parameter:"+p["parameterId"];nodes.append({"id":pid,"kind":"uncertainty-parameter","label":p["name"],"distribution":p["distribution"],"fingerprint":p["parameterFingerprint"]});edges.append({"id":"parameter-edge:"+p["parameterId"],"kind":"uncertainty-parameter","from":pid,"to":"uncertainty:"+p["assessmentId"]})
        if p["evidenceRef"]: nodes.append({"id":p["evidenceRef"],"kind":"evidence-ref","externalCanonicalReference":True,"objectFingerprint":p["evidenceFingerprint"]});edges.append({"id":"evidence-edge:"+p["parameterId"],"kind":"evidence-basis","from":p["evidenceRef"],"to":pid})
    for s in m["scenarios"]: sid="scenario:"+s["scenarioId"];nodes.append({"id":sid,"kind":"uncertainty-scenario","label":s["title"],"fingerprint":s["scenarioFingerprint"]});edges.append({"id":"scenario-edge:"+s["scenarioId"],"kind":"scenario-member","from":"uncertainty:"+s["assessmentId"],"to":sid})
    for r in m["sensitivityRequests"]: rid="sensitivity:"+r["requestId"];nodes.append({"id":rid,"kind":"sensitivity-analysis-request","label":r["method"],"destination":r["destinationProduct"],"fingerprint":r["requestFingerprint"]});edges.append({"id":"sensitivity-edge:"+r["requestId"],"kind":"sensitivity-request","from":"uncertainty:"+r["assessmentId"],"to":rid})
    for r in m["resultBindings"]: nodes.append({"id":r["resultRef"],"kind":r["resultKind"],"externalCanonicalReference":True,"resultFingerprint":r["resultFingerprint"]});edges.append({"id":"result-edge:"+r["bindingId"],"kind":"probabilistic-result","from":"uncertainty:"+r["assessmentId"],"to":r["resultRef"]})
    seen=set();nodes=[n for n in nodes if not (n["id"] in seen or seen.add(n["id"]))]
    payload={"schema":GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"automaticRelationshipInference":False,"automaticCausalityInference":False};payload["graphFingerprint"]=sha256_hex(payload);return payload

def diagnostics(db,user_key,project_id):
    m=manifest(db,user_key,project_id);issues=[];pc=Counter(x["assessmentId"] for x in m["parameters"]);rc=Counter(x["assessmentId"] for x in m["resultBindings"])
    for a in m["assessments"]:
        if pc.get(a["assessmentId"],0)==0:issues.append({"code":"uncertainty-assessment-no-parameters","severity":"review","assessmentId":a["assessmentId"],"message":"No explicit uncertain parameters are recorded."})
        if rc.get(a["assessmentId"],0)==0:issues.append({"code":"uncertainty-assessment-no-results","severity":"info","assessmentId":a["assessmentId"],"message":"No probabilistic result references are bound yet."})
    for p in m["parameters"]:
        if p["distribution"]!="fixed" and not p["distributionParameters"]:issues.append({"code":"uncertainty-distribution-missing-parameters","severity":"review","parameterId":p["parameterId"],"message":"A non-fixed distribution has no explicit distribution parameters."})
        if p["evidenceRef"] and not p["evidenceFingerprint"]:issues.append({"code":"uncertainty-evidence-unpinned","severity":"review","parameterId":p["parameterId"],"message":"Evidence reference is not fingerprint-pinned."})
    payload={"schema":DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"issueCount":len(issues),"probabilityIsNotTruth":True,"automaticResolution":False,"automaticEvidenceRanking":False,"automaticTruthDetermination":False,"automaticCausalityInference":False};payload["diagnosticsFingerprint"]=sha256_hex(payload);return payload

def create_snapshot(db,user_key,project_id,p:UncertaintyInvestigationSnapshotRequest):
    m=manifest(db,user_key,project_id);d=diagnostics(db,user_key,project_id);g=graph(db,user_key,project_id) if p.includeGraph else None;ctx={"manifest":m,"diagnostics":d,"graph":g};fp=sha256_hex(ctx)
    c=m["counts"];row=UncertaintyInvestigationSnapshot(user_key=user_key,snapshot_id="uncertainty-snapshot-"+uuid4().hex[:24],project_id=project_id,manifest_fingerprint=m["manifestFingerprint"],diagnostics_fingerprint=d["diagnosticsFingerprint"],graph_fingerprint=(g or {}).get("graphFingerprint",""),snapshot_fingerprint=fp,assessment_count=c["assessments"],parameter_count=c["parameters"],scenario_count=c["scenarios"],sensitivity_request_count=c["sensitivityRequests"],result_binding_count=c["resultBindings"],issue_count=d["issueCount"],context_json=ctx);db.add(row);db.flush();return snapshot_metadata(row)
def snapshot_metadata(r): return {"schema":SNAPSHOT_SCHEMA,"snapshotId":r.snapshot_id,"projectId":r.project_id,"manifestFingerprint":r.manifest_fingerprint,"diagnosticsFingerprint":r.diagnostics_fingerprint,"graphFingerprint":r.graph_fingerprint,"snapshotFingerprint":r.snapshot_fingerprint,"assessmentCount":r.assessment_count,"parameterCount":r.parameter_count,"scenarioCount":r.scenario_count,"sensitivityRequestCount":r.sensitivity_request_count,"resultBindingCount":r.result_binding_count,"issueCount":r.issue_count,"createdAt":iso(r.created_at)}
def list_snapshots(db,user_key,project_id,limit=100):
    q=select(UncertaintyInvestigationSnapshot).where(UncertaintyInvestigationSnapshot.user_key==user_key,UncertaintyInvestigationSnapshot.project_id==project_id).order_by(UncertaintyInvestigationSnapshot.created_at.desc()).limit(limit);return [snapshot_metadata(x) for x in db.scalars(q).all()]
