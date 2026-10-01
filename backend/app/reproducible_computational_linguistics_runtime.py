from __future__ import annotations

import hashlib
import json
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-reproducible-computational-linguistics-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-reproducible-computational-linguistics-request/1.0"
RESULT_SCHEMA = "sc-workspace-reproducible-computational-linguistics-result/1.0"
CORPUS_SNAPSHOT_SCHEMA = "sc-workspace-linguistics-corpus-snapshot/1.0"
PIPELINE_SCHEMA = "sc-workspace-linguistics-analysis-pipeline/1.0"
RUN_SCHEMA = "sc-workspace-linguistics-analysis-run/1.0"
BINDING_SCHEMA = "sc-workspace-linguistics-result-binding/1.0"
PACKAGE_SCHEMA = "sc-workspace-linguistics-reproducibility-package/1.0"

OPERATIONS = (
    "workspace.linguistics.reproducible-study-validate",
    "workspace.linguistics.corpus-snapshot",
    "workspace.linguistics.analysis-pipeline-plan",
    "workspace.linguistics.analysis-run-record",
    "workspace.linguistics.result-binding",
    "workspace.linguistics.reproducibility-verify",
    "workspace.linguistics.reproducibility-package-lineage",
)

class CorpusItem(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    item_id: str = Field(alias="itemId", min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=50000)
    language_identity_id: str | None = Field(default=None, alias="languageIdentityId", max_length=200)
    script_identity_id: str | None = Field(default=None, alias="scriptIdentityId", max_length=200)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=500)
    transformation_lineage: list[str] = Field(default_factory=list, alias="transformationLineage", max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

class PipelineStep(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    step_id: str = Field(alias="stepId", min_length=1, max_length=200)
    operation: str = Field(min_length=1, max_length=300)
    parameters: dict[str, Any] = Field(default_factory=dict)
    input_refs: list[str] = Field(default_factory=list, alias="inputRefs", max_length=500)
    output_refs: list[str] = Field(default_factory=list, alias="outputRefs", max_length=500)
    runtime_ref: str | None = Field(default=None, alias="runtimeRef", max_length=300)

class AnalysisRun(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    run_id: str = Field(alias="runId", min_length=1, max_length=200)
    pipeline_id: str = Field(alias="pipelineId", min_length=1, max_length=200)
    corpus_snapshot_id: str = Field(alias="corpusSnapshotId", min_length=1, max_length=200)
    runtime_identity: str | None = Field(default=None, alias="runtimeIdentity", max_length=300)
    dependency_lock_ref: str | None = Field(default=None, alias="dependencyLockRef", max_length=500)
    random_seed: int | None = Field(default=None, alias="randomSeed")
    status: Literal["planned","recorded","verified","failed"] = "recorded"
    output_refs: list[str] = Field(default_factory=list, alias="outputRefs", max_length=1000)

class ResultBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    binding_id: str = Field(alias="bindingId", min_length=1, max_length=200)
    run_id: str = Field(alias="runId", min_length=1, max_length=200)
    result_ref: str = Field(alias="resultRef", min_length=1, max_length=500)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=500)
    interpretation: str | None = Field(default=None, max_length=8000)
    human_reviewed: bool = Field(default=False, alias="humanReviewed")

class ReproducibleComputationalLinguisticsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    study_id: str = Field(default="study", alias="studyId", min_length=1, max_length=200)
    corpus_items: list[CorpusItem] = Field(default_factory=list, alias="corpusItems", max_length=25000)
    pipeline_id: str = Field(default="pipeline", alias="pipelineId", min_length=1, max_length=200)
    pipeline_steps: list[PipelineStep] = Field(default_factory=list, alias="pipelineSteps", max_length=1000)
    runs: list[AnalysisRun] = Field(default_factory=list, max_length=10000)
    bindings: list[ResultBinding] = Field(default_factory=list, max_length=50000)
    package_ref: str | None = Field(default=None, alias="packageRef", max_length=500)

def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validate(req: ReproducibleComputationalLinguisticsRequest) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    item_ids=set()
    for item in req.corpus_items:
        if item.item_id in item_ids:
            issues.append({"code":"duplicate-corpus-item-id","itemId":item.item_id})
        item_ids.add(item.item_id)
        if not item.source_refs:
            issues.append({"code":"missing-source-reference","itemId":item.item_id})
    step_ids=set()
    for step in req.pipeline_steps:
        if step.step_id in step_ids:
            issues.append({"code":"duplicate-pipeline-step-id","stepId":step.step_id})
        step_ids.add(step.step_id)
    run_ids=set()
    for run in req.runs:
        if run.run_id in run_ids:
            issues.append({"code":"duplicate-run-id","runId":run.run_id})
        run_ids.add(run.run_id)
        if run.pipeline_id != req.pipeline_id:
            issues.append({"code":"run-pipeline-mismatch","runId":run.run_id})
    binding_ids=set()
    for binding in req.bindings:
        if binding.binding_id in binding_ids:
            issues.append({"code":"duplicate-binding-id","bindingId":binding.binding_id})
        binding_ids.add(binding.binding_id)
        if binding.run_id not in run_ids:
            issues.append({"code":"binding-run-missing","bindingId":binding.binding_id,"runId":binding.run_id})
    return {
        "schema":"sc-workspace-reproducible-computational-linguistics-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "corpusItemCount":len(req.corpus_items),
        "pipelineStepCount":len(req.pipeline_steps),
        "runCount":len(req.runs),
        "bindingCount":len(req.bindings),
    }

def _require(req):
    result=_validate(req)
    if not result["valid"]:
        raise ValueError(f"reproducible computational linguistics validation failed with {result['issueCount']} issue(s)")

def _corpus_snapshot(req):
    _require(req)
    items=[{
        "itemId":x.item_id,
        "textSha256":_sha(x.text),
        "languageIdentityId":x.language_identity_id,
        "scriptIdentityId":x.script_identity_id,
        "sourceRefs":x.source_refs,
        "transformationLineage":x.transformation_lineage,
    } for x in req.corpus_items]
    payload={"studyId":req.study_id,"items":items}
    return {
        "schema":CORPUS_SNAPSHOT_SCHEMA,
        "snapshotId":"corpus-"+_sha(payload)[:24],
        "studyId":req.study_id,
        "itemCount":len(items),
        "items":items,
        "sha256":_sha(payload),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
    }

def _pipeline_plan(req):
    _require(req)
    steps=[s.model_dump(by_alias=True) for s in req.pipeline_steps]
    payload={"pipelineId":req.pipeline_id,"steps":steps}
    return {
        "schema":PIPELINE_SCHEMA,
        "pipelineId":req.pipeline_id,
        "steps":steps,
        "stepCount":len(steps),
        "sha256":_sha(payload),
        "boundedExecutionOnly":True,
        "arbitraryCodeExecution":False,
        "automaticModelSelection":False,
    }

def _run_record(req):
    _require(req)
    return {
        "schema":RUN_SCHEMA,
        "items":[r.model_dump(by_alias=True) for r in req.runs],
        "runCount":len(req.runs),
        "runtimeIdentityRequiredForVerification":True,
        "dependencyLockPreserved":True,
        "randomSeedPreserved":True,
    }

def _result_binding(req):
    _require(req)
    return {
        "schema":BINDING_SCHEMA,
        "items":[b.model_dump(by_alias=True) for b in req.bindings],
        "bindingCount":len(req.bindings),
        "interpretationsAreHumanAuthored":True,
        "automaticTruthDeterminationApplied":False,
        "automaticEvidenceRankingApplied":False,
    }

def _verify(req):
    _require(req)
    checks=[]
    for run in req.runs:
        checks.append({
            "runId":run.run_id,
            "runtimeIdentityPresent":bool(run.runtime_identity),
            "dependencyLockPresent":bool(run.dependency_lock_ref),
            "corpusSnapshotPinned":bool(run.corpus_snapshot_id),
            "seedRecorded":run.random_seed is not None,
            "outputRefsPresent":bool(run.output_refs),
            "reproducible":bool(run.runtime_identity and run.dependency_lock_ref and run.corpus_snapshot_id),
        })
    return {
        "schema":"sc-workspace-linguistics-reproducibility-verification/1.0",
        "studyId":req.study_id,
        "checks":checks,
        "verifiedRunCount":sum(1 for x in checks if x["reproducible"]),
        "runCount":len(checks),
        "automaticReproductionExecution":False,
        "humanReviewRequired":True,
    }

def _package_lineage(req):
    _require(req)
    corpus=_corpus_snapshot(req)
    pipeline=_pipeline_plan(req)
    package={
        "studyId":req.study_id,
        "packageRef":req.package_ref,
        "corpusSnapshotId":corpus["snapshotId"],
        "corpusSha256":corpus["sha256"],
        "pipelineId":req.pipeline_id,
        "pipelineSha256":pipeline["sha256"],
        "runIds":[r.run_id for r in req.runs],
        "bindingIds":[b.binding_id for b in req.bindings],
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **package,
        "packageSha256":_sha(package),
        "provenancePreserved":True,
        "immutableSnapshotRecommended":True,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.53.0",
        "title":"Reproducible Computational Linguistics Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "historicalLanguageIdentityPreserved":True,
        "sourceAndTransformationLineageRequired":True,
        "runtimeIdentityCaptured":True,
        "dependencyLockCaptured":True,
        "randomSeedCaptured":True,
        "automaticTranslationEnabled":False,
        "automaticModelSelectionEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticReproductionExecution":False,
        "humanReviewRequired":True,
        "arbitraryCodeExecution":False,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req: ReproducibleComputationalLinguisticsRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported reproducible computational linguistics operation")
    payload={
        OPERATIONS[0]: lambda:_validate(req),
        OPERATIONS[1]: lambda:_corpus_snapshot(req),
        OPERATIONS[2]: lambda:_pipeline_plan(req),
        OPERATIONS[3]: lambda:_run_record(req),
        OPERATIONS[4]: lambda:_result_binding(req),
        OPERATIONS[5]: lambda:_verify(req),
        OPERATIONS[6]: lambda:_package_lineage(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.53.0","operation":req.operation,"ok":True,"result":payload}
