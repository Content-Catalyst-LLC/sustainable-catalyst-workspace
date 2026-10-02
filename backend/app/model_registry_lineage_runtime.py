from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA="sc-workspace-model-registry-lineage-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-model-registry-lineage-request/1.0"
RESULT_SCHEMA="sc-workspace-model-registry-lineage-result/1.0"
MODEL_SCHEMA="sc-workspace-research-model/1.0"
VERSION_SCHEMA="sc-workspace-research-model-version/1.0"
LINEAGE_SCHEMA="sc-workspace-research-model-lineage/1.0"
EVALUATION_BINDING_SCHEMA="sc-workspace-model-evaluation-binding/1.0"
PACKAGE_SCHEMA="sc-workspace-model-registry-package/1.0"

OPERATIONS=(
    "workspace.models.validate",
    "workspace.models.register",
    "workspace.models.version-profile",
    "workspace.models.lineage-graph",
    "workspace.models.evaluation-bindings",
    "workspace.models.promotion-readiness",
    "workspace.models.reproducibility-package",
)

class ModelVersion(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    model_version_id:str=Field(alias="modelVersionId",min_length=1,max_length=200)
    model_ref:str=Field(alias="modelRef",min_length=1,max_length=500)
    parent_model_version_refs:list[str]=Field(default_factory=list,alias="parentModelVersionRefs",max_length=1000)
    dataset_ref:str|None=Field(default=None,alias="datasetRef",max_length=500)
    feature_package_ref:str|None=Field(default=None,alias="featurePackageRef",max_length=500)
    experiment_ref:str|None=Field(default=None,alias="experimentRef",max_length=500)
    run_ref:str|None=Field(default=None,alias="runRef",max_length=500)
    environment_ref:str|None=Field(default=None,alias="environmentRef",max_length=500)
    artifact_refs:list[str]=Field(default_factory=list,alias="artifactRefs",max_length=5000)
    artifact_sha256:dict[str,str]=Field(default_factory=dict,alias="artifactSha256")
    provenance_refs:list[str]=Field(default_factory=list,alias="provenanceRefs",max_length=5000)
    author_refs:list[str]=Field(default_factory=list,alias="authorRefs",max_length=1000)
    status:str=Field(default="registered",pattern="^(registered|candidate|reviewed|approved|deprecated|archived)$")

class EvaluationBinding(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    binding_id:str=Field(alias="bindingId",min_length=1,max_length=200)
    model_version_id:str=Field(alias="modelVersionId",min_length=1,max_length=200)
    experiment_ref:str|None=Field(default=None,alias="experimentRef",max_length=500)
    run_ref:str|None=Field(default=None,alias="runRef",max_length=500)
    metric_values:dict[str,float]=Field(default_factory=dict,alias="metricValues")
    evaluation_artifact_refs:list[str]=Field(default_factory=list,alias="evaluationArtifactRefs",max_length=5000)
    provenance_refs:list[str]=Field(default_factory=list,alias="provenanceRefs",max_length=5000)

class ModelRegistryLineageRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    registry_id:str=Field(default="model-registry",alias="registryId",min_length=1,max_length=200)
    model_id:str=Field(default="model",alias="modelId",min_length=1,max_length=200)
    title:str|None=Field(default=None,max_length=500)
    model_kind:str=Field(default="research-model",alias="modelKind",max_length=200)
    description:str|None=Field(default=None,max_length=4000)
    model_versions:list[ModelVersion]=Field(default_factory=list,alias="modelVersions",max_length=5000)
    evaluation_bindings:list[EvaluationBinding]=Field(default_factory=list,alias="evaluationBindings",max_length=5000)
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=10000)
    package_ref:str|None=Field(default=None,alias="packageRef",max_length=500)

def _canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(value:Any)->str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validation(req:ModelRegistryLineageRequest)->dict[str,Any]:
    issues=[]
    version_ids=[x.model_version_id for x in req.model_versions]
    version_set=set(version_ids)
    if len(version_ids)!=len(version_set):
        issues.append({"code":"duplicate-model-version-id"})
    for version in req.model_versions:
        for parent in version.parent_model_version_refs:
            if parent==version.model_version_id:
                issues.append({"code":"self-parent-reference","modelVersionId":version.model_version_id})
        if not version.provenance_refs:
            issues.append({"code":"model-version-provenance-missing","modelVersionId":version.model_version_id})
        for artifact_ref,digest in version.artifact_sha256.items():
            if artifact_ref not in version.artifact_refs:
                issues.append({"code":"artifact-hash-without-artifact-ref","modelVersionId":version.model_version_id,"artifactRef":artifact_ref})
            if len(digest)!=64:
                issues.append({"code":"invalid-artifact-sha256","modelVersionId":version.model_version_id,"artifactRef":artifact_ref})
    binding_ids=[x.binding_id for x in req.evaluation_bindings]
    if len(binding_ids)!=len(set(binding_ids)):
        issues.append({"code":"duplicate-evaluation-binding-id"})
    for binding in req.evaluation_bindings:
        if binding.model_version_id not in version_set:
            issues.append({"code":"evaluation-model-version-missing","bindingId":binding.binding_id,"modelVersionId":binding.model_version_id})
        if not binding.provenance_refs:
            issues.append({"code":"evaluation-binding-provenance-missing","bindingId":binding.binding_id})
    return {
        "schema":"sc-workspace-model-registry-lineage-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "modelVersionCount":len(req.model_versions),
        "evaluationBindingCount":len(req.evaluation_bindings),
    }

def _require(req):
    result=_validation(req)
    if not result["valid"]:
        raise ValueError(f"model registry validation failed with {result['issueCount']} issue(s)")

def _register(req):
    _require(req)
    payload={
        "schema":MODEL_SCHEMA,
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "title":req.title,
        "modelKind":req.model_kind,
        "description":req.description,
        "modelVersionIds":[x.model_version_id for x in req.model_versions],
        "sourceRefs":req.source_refs,
    }
    return {**payload,"registryFingerprint":_sha(payload),"provenancePreserved":True}

def _version_profile(req):
    _require(req)
    return {
        "schema":VERSION_SCHEMA,
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "items":[x.model_dump(by_alias=True) for x in req.model_versions],
        "modelVersionCount":len(req.model_versions),
        "automaticVersionMutationEnabled":False,
        "automaticModelPromotionEnabled":False,
    }

def _lineage(req):
    _require(req)
    nodes=[{"id":req.model_id,"kind":"model"}]
    edges=[]
    for v in req.model_versions:
        nodes.append({"id":v.model_version_id,"kind":"model-version","status":v.status})
        edges.append({"source":req.model_id,"target":v.model_version_id,"relation":"has-version"})
        for parent in v.parent_model_version_refs:
            edges.append({"source":parent,"target":v.model_version_id,"relation":"derived-from"})
        for ref,kind,rel in (
            (v.dataset_ref,"dataset","trained-on"),
            (v.feature_package_ref,"feature-package","uses-features"),
            (v.experiment_ref,"experiment","produced-by-experiment"),
            (v.run_ref,"experiment-run","produced-by-run"),
            (v.environment_ref,"environment","executed-in"),
        ):
            if ref:
                nodes.append({"id":ref,"kind":kind})
                edges.append({"source":ref,"target":v.model_version_id,"relation":rel})
    return {
        "schema":LINEAGE_SCHEMA,
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "nodes":nodes,
        "edges":edges,
        "sourceRefs":req.source_refs,
        "provenancePreserved":True,
        "datasetFeatureExperimentRunLineagePreserved":True,
    }

def _evaluation_bindings(req):
    _require(req)
    return {
        "schema":EVALUATION_BINDING_SCHEMA,
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "items":[x.model_dump(by_alias=True) for x in req.evaluation_bindings],
        "evaluationBindingCount":len(req.evaluation_bindings),
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
    }

def _promotion_readiness(req):
    _require(req)
    bindings_by_version={}
    for b in req.evaluation_bindings:
        bindings_by_version.setdefault(b.model_version_id,[]).append(b)
    rows=[]
    for v in req.model_versions:
        reasons=[]
        if not v.artifact_refs:
            reasons.append("model-artifacts-missing")
        if not v.environment_ref:
            reasons.append("environment-ref-missing")
        if not v.run_ref:
            reasons.append("run-ref-missing")
        if not bindings_by_version.get(v.model_version_id):
            reasons.append("evaluation-binding-missing")
        rows.append({
            "modelVersionId":v.model_version_id,
            "readyForHumanReview":not reasons,
            "blockingReasons":reasons,
        })
    return {
        "schema":"sc-workspace-model-promotion-readiness/1.0",
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "items":rows,
        "humanReviewRequired":True,
        "automaticModelPromotionEnabled":False,
        "automaticApprovalEnabled":False,
    }

def _package(req):
    _require(req)
    registration=_register(req)
    lineage=_lineage(req)
    evaluations=_evaluation_bindings(req)
    readiness=_promotion_readiness(req)
    payload={
        "registryId":req.registry_id,
        "modelId":req.model_id,
        "registryFingerprint":registration["registryFingerprint"],
        "modelVersionIds":[x.model_version_id for x in req.model_versions],
        "lineageSha256":_sha(lineage),
        "evaluationBindingsSha256":_sha(evaluations),
        "promotionReadinessSha256":_sha(readiness),
        "sourceRefs":sorted(set(req.source_refs)),
        "packageRef":req.package_ref,
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **payload,
        "packageSha256":_sha(payload),
        "provenancePreserved":True,
        "automaticModelPromotionEnabled":False,
        "automaticApprovalEnabled":False,
        "arbitraryCodeExecution":False,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.59.0",
        "title":"Model Registry & Research Model Lineage Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "modelRegistration":True,
        "modelVersioning":True,
        "parentDerivedLineage":True,
        "datasetFeatureExperimentRunLineage":True,
        "artifactFingerprinting":True,
        "evaluationBindings":True,
        "promotionReadiness":True,
        "reproducibilityPackaging":True,
        "humanReviewRequiredForPromotion":True,
        "automaticModelPromotionEnabled":False,
        "automaticApprovalEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req:ModelRegistryLineageRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported model registry operation")
    result={
        OPERATIONS[0]:lambda:_validation(req),
        OPERATIONS[1]:lambda:_register(req),
        OPERATIONS[2]:lambda:_version_profile(req),
        OPERATIONS[3]:lambda:_lineage(req),
        OPERATIONS[4]:lambda:_evaluation_bindings(req),
        OPERATIONS[5]:lambda:_promotion_readiness(req),
        OPERATIONS[6]:lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.59.0","operation":req.operation,"ok":True,"result":result}
