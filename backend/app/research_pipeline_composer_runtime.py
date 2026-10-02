from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA="sc-workspace-research-pipeline-composer-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-research-pipeline-composer-request/1.0"
RESULT_SCHEMA="sc-workspace-research-pipeline-composer-result/1.0"
PIPELINE_SCHEMA="sc-workspace-research-pipeline/1.0"
STEP_SCHEMA="sc-workspace-research-pipeline-step/1.0"
HANDOFF_SCHEMA="sc-workspace-research-pipeline-handoff/1.0"
PLAN_SCHEMA="sc-workspace-research-pipeline-plan/1.0"
LINEAGE_SCHEMA="sc-workspace-research-pipeline-lineage/1.0"
PACKAGE_SCHEMA="sc-workspace-research-pipeline-package/1.0"

OPERATIONS=(
    "workspace.pipeline.validate",
    "workspace.pipeline.compose",
    "workspace.pipeline.dependency-plan",
    "workspace.pipeline.handoff-plan",
    "workspace.pipeline.lineage-graph",
    "workspace.pipeline.readiness-check",
    "workspace.pipeline.reproducibility-package",
)

class PipelineStep(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    step_id:str=Field(alias="stepId",min_length=1,max_length=200)
    operation:str=Field(min_length=1,max_length=300)
    runtime_ref:str|None=Field(default=None,alias="runtimeRef",max_length=500)
    depends_on:list[str]=Field(default_factory=list,alias="dependsOn",max_length=1000)
    input_refs:list[str]=Field(default_factory=list,alias="inputRefs",max_length=5000)
    output_refs:list[str]=Field(default_factory=list,alias="outputRefs",max_length=5000)
    parameters:dict[str,Any]=Field(default_factory=dict)
    human_review_required:bool=Field(default=False,alias="humanReviewRequired")

class PipelineHandoff(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    handoff_id:str=Field(alias="handoffId",min_length=1,max_length=200)
    from_step_id:str=Field(alias="fromStepId",min_length=1,max_length=200)
    to_step_id:str=Field(alias="toStepId",min_length=1,max_length=200)
    artifact_refs:list[str]=Field(default_factory=list,alias="artifactRefs",max_length=5000)
    contract_ref:str|None=Field(default=None,alias="contractRef",max_length=500)
    provenance_refs:list[str]=Field(default_factory=list,alias="provenanceRefs",max_length=5000)

class ResearchPipelineComposerRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    pipeline_id:str=Field(default="research-pipeline",alias="pipelineId",min_length=1,max_length=200)
    title:str|None=Field(default=None,max_length=500)
    description:str|None=Field(default=None,max_length=4000)
    steps:list[PipelineStep]=Field(default_factory=list,max_length=5000)
    handoffs:list[PipelineHandoff]=Field(default_factory=list,max_length=5000)
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=10000)
    package_ref:str|None=Field(default=None,alias="packageRef",max_length=500)

def _canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(value:Any)->str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validation(req:ResearchPipelineComposerRequest)->dict[str,Any]:
    issues=[]
    ids=[x.step_id for x in req.steps]
    step_ids=set(ids)
    if len(ids)!=len(step_ids):
        issues.append({"code":"duplicate-step-id"})
    for step in req.steps:
        for dep in step.depends_on:
            if dep not in step_ids:
                issues.append({"code":"unknown-step-dependency","stepId":step.step_id,"dependency":dep})
            if dep==step.step_id:
                issues.append({"code":"self-dependency","stepId":step.step_id})
    handoff_ids=set()
    for handoff in req.handoffs:
        if handoff.handoff_id in handoff_ids:
            issues.append({"code":"duplicate-handoff-id","handoffId":handoff.handoff_id})
        handoff_ids.add(handoff.handoff_id)
        if handoff.from_step_id not in step_ids or handoff.to_step_id not in step_ids:
            issues.append({"code":"handoff-step-missing","handoffId":handoff.handoff_id})
    return {
        "schema":"sc-workspace-research-pipeline-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "stepCount":len(req.steps),
        "handoffCount":len(req.handoffs),
    }

def _require(req):
    result=_validation(req)
    if not result["valid"]:
        raise ValueError(f"research pipeline validation failed with {result['issueCount']} issue(s)")

def _compose(req):
    _require(req)
    payload={
        "schema":PIPELINE_SCHEMA,
        "pipelineId":req.pipeline_id,
        "title":req.title,
        "description":req.description,
        "steps":[x.model_dump(by_alias=True) for x in req.steps],
        "handoffs":[x.model_dump(by_alias=True) for x in req.handoffs],
        "sourceRefs":req.source_refs,
    }
    return {**payload,"pipelineSha256":_sha(payload),"immutableDefinitionRecommended":True}

def _dependency_plan(req):
    _require(req)
    graph={x.step_id:list(x.depends_on) for x in req.steps}
    indegree={sid:0 for sid in graph}
    children={sid:[] for sid in graph}
    for sid,deps in graph.items():
        indegree[sid]=len(deps)
        for dep in deps:
            children[dep].append(sid)
    queue=sorted([sid for sid,v in indegree.items() if v==0])
    ordered=[]
    while queue:
        sid=queue.pop(0)
        ordered.append(sid)
        for child in children[sid]:
            indegree[child]-=1
            if indegree[child]==0:
                queue.append(child)
                queue.sort()
    cyclic=len(ordered)!=len(graph)
    return {
        "schema":PLAN_SCHEMA,
        "pipelineId":req.pipeline_id,
        "orderedStepIds":ordered,
        "cyclic":cyclic,
        "ready":not cyclic,
        "automaticExecutionEnabled":False,
    }

def _handoff_plan(req):
    _require(req)
    return {
        "schema":"sc-workspace-research-pipeline-handoff-plan/1.0",
        "pipelineId":req.pipeline_id,
        "items":[x.model_dump(by_alias=True) for x in req.handoffs],
        "handoffCount":len(req.handoffs),
        "provenanceRequired":True,
        "automaticHandoffAcceptanceEnabled":False,
    }

def _lineage(req):
    _require(req)
    nodes=[{"id":x.step_id,"kind":"pipeline-step","operation":x.operation,"runtimeRef":x.runtime_ref} for x in req.steps]
    edges=[]
    for step in req.steps:
        for dep in step.depends_on:
            edges.append({"source":dep,"target":step.step_id,"relation":"depends-on"})
    for handoff in req.handoffs:
        edges.append({"source":handoff.from_step_id,"target":handoff.to_step_id,"relation":"handoff","handoffId":handoff.handoff_id})
    return {
        "schema":LINEAGE_SCHEMA,
        "pipelineId":req.pipeline_id,
        "nodes":nodes,
        "edges":edges,
        "sourceRefs":req.source_refs,
        "provenancePreserved":True,
        "crossRuntimeLineagePreserved":True,
    }

def _readiness(req):
    _require(req)
    dep=_dependency_plan(req)
    missing_runtime=[x.step_id for x in req.steps if not x.runtime_ref]
    handoff_missing_provenance=[x.handoff_id for x in req.handoffs if not x.provenance_refs]
    return {
        "schema":"sc-workspace-research-pipeline-readiness/1.0",
        "pipelineId":req.pipeline_id,
        "ready":dep["ready"] and not missing_runtime and not handoff_missing_provenance,
        "cyclic":dep["cyclic"],
        "stepsMissingRuntimeRef":missing_runtime,
        "handoffsMissingProvenance":handoff_missing_provenance,
        "humanReviewRequiredStepCount":sum(1 for x in req.steps if x.human_review_required),
        "automaticExecutionEnabled":False,
        "arbitraryCodeExecution":False,
    }

def _package(req):
    _require(req)
    definition=_compose(req)
    plan=_dependency_plan(req)
    lineage=_lineage(req)
    readiness=_readiness(req)
    payload={
        "pipelineId":req.pipeline_id,
        "packageRef":req.package_ref,
        "definitionSha256":definition["pipelineSha256"],
        "orderedStepIds":plan["orderedStepIds"],
        "lineageSha256":_sha(lineage),
        "sourceRefs":sorted(set(req.source_refs)),
        "ready":readiness["ready"],
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **payload,
        "packageSha256":_sha(payload),
        "provenancePreserved":True,
        "automaticExecutionEnabled":False,
        "arbitraryCodeExecution":False,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.56.0",
        "title":"Research Pipeline Composer Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "dependencyAware":True,
        "boundedHandoffs":True,
        "crossRuntimeLineagePreserved":True,
        "reproducibilityPackaging":True,
        "humanReviewSupported":True,
        "automaticExecutionEnabled":False,
        "automaticHandoffAcceptanceEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req:ResearchPipelineComposerRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported research pipeline composer operation")
    result={
        OPERATIONS[0]:lambda:_validation(req),
        OPERATIONS[1]:lambda:_compose(req),
        OPERATIONS[2]:lambda:_dependency_plan(req),
        OPERATIONS[3]:lambda:_handoff_plan(req),
        OPERATIONS[4]:lambda:_lineage(req),
        OPERATIONS[5]:lambda:_readiness(req),
        OPERATIONS[6]:lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.56.0","operation":req.operation,"ok":True,"result":result}
