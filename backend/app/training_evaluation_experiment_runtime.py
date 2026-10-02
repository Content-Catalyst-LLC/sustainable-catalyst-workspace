from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA="sc-workspace-training-evaluation-experiment-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-training-evaluation-experiment-request/1.0"
RESULT_SCHEMA="sc-workspace-training-evaluation-experiment-result/1.0"
EXPERIMENT_SCHEMA="sc-workspace-training-evaluation-experiment/1.0"
RUN_SCHEMA="sc-workspace-training-evaluation-run/1.0"
METRIC_SCHEMA="sc-workspace-evaluation-metric/1.0"
LINEAGE_SCHEMA="sc-workspace-training-evaluation-lineage/1.0"
PACKAGE_SCHEMA="sc-workspace-training-evaluation-package/1.0"

OPERATIONS=(
    "workspace.experiments.validate",
    "workspace.experiments.experiment-profile",
    "workspace.experiments.training-plan",
    "workspace.experiments.evaluation-plan",
    "workspace.experiments.run-lineage",
    "workspace.experiments.comparison-readiness",
    "workspace.experiments.reproducibility-package",
)

class MetricDefinition(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    metric_id:str=Field(alias="metricId",min_length=1,max_length=200)
    name:str=Field(min_length=1,max_length=300)
    direction:str=Field(default="maximize",pattern="^(maximize|minimize|neutral)$")
    split:str=Field(default="validation",pattern="^(train|validation|test|holdout)$")
    threshold:float|None=None

class ExperimentRun(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    run_id:str=Field(alias="runId",min_length=1,max_length=200)
    model_ref:str=Field(alias="modelRef",min_length=1,max_length=500)
    dataset_ref:str=Field(alias="datasetRef",min_length=1,max_length=500)
    feature_package_ref:str|None=Field(default=None,alias="featurePackageRef",max_length=500)
    environment_ref:str|None=Field(default=None,alias="environmentRef",max_length=500)
    parameters:dict[str,Any]=Field(default_factory=dict)
    random_seed:int|None=Field(default=None,alias="randomSeed")
    metric_values:dict[str,float]=Field(default_factory=dict,alias="metricValues")
    artifact_refs:list[str]=Field(default_factory=list,alias="artifactRefs",max_length=5000)
    provenance_refs:list[str]=Field(default_factory=list,alias="provenanceRefs",max_length=5000)

class TrainingEvaluationExperimentRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    experiment_id:str=Field(default="experiment",alias="experimentId",min_length=1,max_length=200)
    title:str|None=Field(default=None,max_length=500)
    objective:str|None=Field(default=None,max_length=4000)
    task_type:str=Field(default="supervised",alias="taskType",max_length=100)
    dataset_ref:str|None=Field(default=None,alias="datasetRef",max_length=500)
    feature_package_ref:str|None=Field(default=None,alias="featurePackageRef",max_length=500)
    model_refs:list[str]=Field(default_factory=list,alias="modelRefs",max_length=1000)
    split_strategy:str|None=Field(default=None,alias="splitStrategy",max_length=200)
    random_seed:int|None=Field(default=None,alias="randomSeed")
    metrics:list[MetricDefinition]=Field(default_factory=list,max_length=1000)
    runs:list[ExperimentRun]=Field(default_factory=list,max_length=5000)
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=10000)
    package_ref:str|None=Field(default=None,alias="packageRef",max_length=500)

def _canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(value:Any)->str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validation(req:TrainingEvaluationExperimentRequest)->dict[str,Any]:
    issues=[]
    metric_ids=[x.metric_id for x in req.metrics]
    if len(metric_ids)!=len(set(metric_ids)):
        issues.append({"code":"duplicate-metric-id"})
    run_ids=[x.run_id for x in req.runs]
    if len(run_ids)!=len(set(run_ids)):
        issues.append({"code":"duplicate-run-id"})
    if req.split_strategy not in {None,"none"} and req.random_seed is None:
        issues.append({"code":"split-seed-missing"})
    metric_set=set(metric_ids)
    for run in req.runs:
        if not run.provenance_refs:
            issues.append({"code":"run-provenance-missing","runId":run.run_id})
        unknown=[m for m in run.metric_values if m not in metric_set]
        for metric_id in unknown:
            issues.append({"code":"unknown-run-metric","runId":run.run_id,"metricId":metric_id})
    return {
        "schema":"sc-workspace-training-evaluation-experiment-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "metricCount":len(req.metrics),
        "runCount":len(req.runs),
    }

def _require(req):
    result=_validation(req)
    if not result["valid"]:
        raise ValueError(f"training/evaluation experiment validation failed with {result['issueCount']} issue(s)")

def _experiment_profile(req):
    _require(req)
    payload={
        "schema":EXPERIMENT_SCHEMA,
        "experimentId":req.experiment_id,
        "title":req.title,
        "objective":req.objective,
        "taskType":req.task_type,
        "datasetRef":req.dataset_ref,
        "featurePackageRef":req.feature_package_ref,
        "modelRefs":req.model_refs,
        "splitStrategy":req.split_strategy,
        "randomSeed":req.random_seed,
        "sourceRefs":req.source_refs,
    }
    return {**payload,"experimentFingerprint":_sha(payload),"provenancePreserved":True}

def _training_plan(req):
    _require(req)
    return {
        "schema":"sc-workspace-training-plan/1.0",
        "experimentId":req.experiment_id,
        "datasetRef":req.dataset_ref,
        "featurePackageRef":req.feature_package_ref,
        "modelRefs":req.model_refs,
        "splitStrategy":req.split_strategy,
        "randomSeed":req.random_seed,
        "automaticTrainingExecutionEnabled":False,
        "humanAuthorizationRequired":True,
    }

def _evaluation_plan(req):
    _require(req)
    return {
        "schema":"sc-workspace-evaluation-plan/1.0",
        "experimentId":req.experiment_id,
        "metrics":[x.model_dump(by_alias=True) for x in req.metrics],
        "metricCount":len(req.metrics),
        "testSetSelectionAutomatic":False,
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
    }

def _lineage(req):
    _require(req)
    nodes=[{"id":req.experiment_id,"kind":"experiment"}]
    edges=[]
    if req.dataset_ref:
        nodes.append({"id":req.dataset_ref,"kind":"dataset"})
        edges.append({"source":req.dataset_ref,"target":req.experiment_id,"relation":"dataset-input"})
    if req.feature_package_ref:
        nodes.append({"id":req.feature_package_ref,"kind":"feature-package"})
        edges.append({"source":req.feature_package_ref,"target":req.experiment_id,"relation":"feature-input"})
    for run in req.runs:
        nodes.append({"id":run.run_id,"kind":"experiment-run","modelRef":run.model_ref})
        edges.append({"source":req.experiment_id,"target":run.run_id,"relation":"has-run"})
    return {
        "schema":LINEAGE_SCHEMA,
        "experimentId":req.experiment_id,
        "nodes":nodes,
        "edges":edges,
        "sourceRefs":req.source_refs,
        "runProvenancePreserved":True,
        "datasetFeatureLineagePreserved":True,
    }

def _comparison_readiness(req):
    _require(req)
    missing_metrics=[x.run_id for x in req.runs if not x.metric_values]
    missing_env=[x.run_id for x in req.runs if not x.environment_ref]
    missing_seed=[x.run_id for x in req.runs if x.random_seed is None]
    return {
        "schema":"sc-workspace-experiment-comparison-readiness/1.0",
        "experimentId":req.experiment_id,
        "ready":len(req.runs)>=2 and bool(req.metrics) and not missing_metrics and not missing_env and not missing_seed,
        "runCount":len(req.runs),
        "metricCount":len(req.metrics),
        "runsMissingMetrics":missing_metrics,
        "runsMissingEnvironmentRef":missing_env,
        "runsMissingRandomSeed":missing_seed,
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
        "automaticTruthDeterminationEnabled":False,
    }

def _package(req):
    _require(req)
    profile=_experiment_profile(req)
    lineage=_lineage(req)
    readiness=_comparison_readiness(req)
    payload={
        "experimentId":req.experiment_id,
        "experimentFingerprint":profile["experimentFingerprint"],
        "runIds":[x.run_id for x in req.runs],
        "metricIds":[x.metric_id for x in req.metrics],
        "lineageSha256":_sha(lineage),
        "sourceRefs":sorted(set(req.source_refs)),
        "comparisonReady":readiness["ready"],
        "packageRef":req.package_ref,
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **payload,
        "packageSha256":_sha(payload),
        "provenancePreserved":True,
        "automaticTrainingExecutionEnabled":False,
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
        "arbitraryCodeExecution":False,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.58.0",
        "title":"Training & Evaluation Experiment Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "experimentDefinitions":True,
        "trainingPlanning":True,
        "evaluationPlanning":True,
        "metricRegistry":True,
        "runLineage":True,
        "comparisonReadiness":True,
        "reproducibilityPackaging":True,
        "automaticTrainingExecutionEnabled":False,
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req:TrainingEvaluationExperimentRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported training/evaluation experiment operation")
    result={
        OPERATIONS[0]:lambda:_validation(req),
        OPERATIONS[1]:lambda:_experiment_profile(req),
        OPERATIONS[2]:lambda:_training_plan(req),
        OPERATIONS[3]:lambda:_evaluation_plan(req),
        OPERATIONS[4]:lambda:_lineage(req),
        OPERATIONS[5]:lambda:_comparison_readiness(req),
        OPERATIONS[6]:lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.58.0","operation":req.operation,"ok":True,"result":result}
