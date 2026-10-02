from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA="sc-workspace-dataset-feature-engineering-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-dataset-feature-engineering-request/1.0"
RESULT_SCHEMA="sc-workspace-dataset-feature-engineering-result/1.0"
DATASET_SCHEMA="sc-workspace-feature-dataset/1.0"
FEATURE_SCHEMA="sc-workspace-feature-definition/1.0"
TRANSFORM_SCHEMA="sc-workspace-feature-transformation/1.0"
LINEAGE_SCHEMA="sc-workspace-feature-lineage/1.0"
PACKAGE_SCHEMA="sc-workspace-feature-engineering-package/1.0"

OPERATIONS=(
    "workspace.features.validate",
    "workspace.features.dataset-profile",
    "workspace.features.feature-catalog",
    "workspace.features.transformation-plan",
    "workspace.features.lineage-graph",
    "workspace.features.readiness-check",
    "workspace.features.reproducibility-package",
)

class FeatureDefinition(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    feature_id:str=Field(alias="featureId",min_length=1,max_length=200)
    source_fields:list[str]=Field(default_factory=list,alias="sourceFields",max_length=1000)
    data_type:str=Field(alias="dataType",min_length=1,max_length=100)
    semantic_role:str|None=Field(default=None,alias="semanticRole",max_length=100)
    description:str|None=Field(default=None,max_length=2000)
    leakage_risk:bool=Field(default=False,alias="leakageRisk")
    target_related:bool=Field(default=False,alias="targetRelated")

class FeatureTransformation(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    transformation_id:str=Field(alias="transformationId",min_length=1,max_length=200)
    operation:str=Field(min_length=1,max_length=300)
    input_features:list[str]=Field(default_factory=list,alias="inputFeatures",max_length=1000)
    output_features:list[str]=Field(default_factory=list,alias="outputFeatures",max_length=1000)
    parameters:dict[str,Any]=Field(default_factory=dict)
    deterministic:bool=True
    human_review_required:bool=Field(default=False,alias="humanReviewRequired")
    provenance_refs:list[str]=Field(default_factory=list,alias="provenanceRefs",max_length=5000)

class DatasetFeatureEngineeringRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    dataset_id:str=Field(default="dataset",alias="datasetId",min_length=1,max_length=200)
    dataset_version:str|None=Field(default=None,alias="datasetVersion",max_length=100)
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=10000)
    row_count:int|None=Field(default=None,alias="rowCount",ge=0)
    column_count:int|None=Field(default=None,alias="columnCount",ge=0)
    target_feature_id:str|None=Field(default=None,alias="targetFeatureId",max_length=200)
    features:list[FeatureDefinition]=Field(default_factory=list,max_length=5000)
    transformations:list[FeatureTransformation]=Field(default_factory=list,max_length=5000)
    split_strategy:str|None=Field(default=None,alias="splitStrategy",max_length=200)
    random_seed:int|None=Field(default=None,alias="randomSeed")
    package_ref:str|None=Field(default=None,alias="packageRef",max_length=500)

def _canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(value:Any)->str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validation(req:DatasetFeatureEngineeringRequest)->dict[str,Any]:
    issues=[]
    feature_ids=[x.feature_id for x in req.features]
    feature_set=set(feature_ids)
    if len(feature_ids)!=len(feature_set):
        issues.append({"code":"duplicate-feature-id"})
    transform_ids=set()
    for tr in req.transformations:
        if tr.transformation_id in transform_ids:
            issues.append({"code":"duplicate-transformation-id","transformationId":tr.transformation_id})
        transform_ids.add(tr.transformation_id)
        for fid in tr.input_features:
            if fid not in feature_set:
                issues.append({"code":"unknown-input-feature","transformationId":tr.transformation_id,"featureId":fid})
        if not tr.provenance_refs:
            issues.append({"code":"transformation-provenance-missing","transformationId":tr.transformation_id})
    if req.target_feature_id and req.target_feature_id not in feature_set:
        issues.append({"code":"target-feature-missing","featureId":req.target_feature_id})
    return {
        "schema":"sc-workspace-dataset-feature-engineering-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "featureCount":len(req.features),
        "transformationCount":len(req.transformations),
    }

def _require(req):
    result=_validation(req)
    if not result["valid"]:
        raise ValueError(f"dataset feature engineering validation failed with {result['issueCount']} issue(s)")

def _dataset_profile(req):
    _require(req)
    payload={
        "schema":DATASET_SCHEMA,
        "datasetId":req.dataset_id,
        "datasetVersion":req.dataset_version,
        "rowCount":req.row_count,
        "columnCount":req.column_count,
        "sourceRefs":req.source_refs,
        "splitStrategy":req.split_strategy,
        "randomSeed":req.random_seed,
        "targetFeatureId":req.target_feature_id,
    }
    return {**payload,"datasetFingerprint":_sha(payload),"sourceProvenancePreserved":True}

def _feature_catalog(req):
    _require(req)
    return {
        "schema":"sc-workspace-feature-catalog/1.0",
        "datasetId":req.dataset_id,
        "items":[x.model_dump(by_alias=True) for x in req.features],
        "featureCount":len(req.features),
        "targetFeatureId":req.target_feature_id,
        "leakageRiskFeatureIds":[x.feature_id for x in req.features if x.leakage_risk],
        "targetRelatedFeatureIds":[x.feature_id for x in req.features if x.target_related],
        "automaticFeatureSelectionEnabled":False,
    }

def _transformation_plan(req):
    _require(req)
    return {
        "schema":"sc-workspace-feature-transformation-plan/1.0",
        "datasetId":req.dataset_id,
        "items":[x.model_dump(by_alias=True) for x in req.transformations],
        "transformationCount":len(req.transformations),
        "allDeterministic":all(x.deterministic for x in req.transformations),
        "humanReviewRequiredCount":sum(1 for x in req.transformations if x.human_review_required),
        "automaticExecutionEnabled":False,
    }

def _lineage(req):
    _require(req)
    nodes=[{"id":x.feature_id,"kind":"feature","dataType":x.data_type} for x in req.features]
    edges=[]
    for tr in req.transformations:
        nodes.append({"id":tr.transformation_id,"kind":"transformation","operation":tr.operation})
        for fid in tr.input_features:
            edges.append({"source":fid,"target":tr.transformation_id,"relation":"input-to-transformation"})
        for fid in tr.output_features:
            edges.append({"source":tr.transformation_id,"target":fid,"relation":"transformation-to-output"})
    return {
        "schema":LINEAGE_SCHEMA,
        "datasetId":req.dataset_id,
        "nodes":nodes,
        "edges":edges,
        "sourceRefs":req.source_refs,
        "provenancePreserved":True,
        "transformationLineagePreserved":True,
    }

def _readiness(req):
    _require(req)
    risky=[x.feature_id for x in req.features if x.leakage_risk]
    missing_source=not req.source_refs
    nondeterministic=[x.transformation_id for x in req.transformations if not x.deterministic]
    missing_seed=req.split_strategy not in {None,"none"} and req.random_seed is None
    return {
        "schema":"sc-workspace-feature-engineering-readiness/1.0",
        "datasetId":req.dataset_id,
        "ready":not missing_source and not risky and not nondeterministic and not missing_seed,
        "sourceReferencesPresent":not missing_source,
        "leakageRiskFeatureIds":risky,
        "nondeterministicTransformationIds":nondeterministic,
        "splitSeedMissing":missing_seed,
        "automaticLeakageOverrideEnabled":False,
        "automaticFeatureSelectionEnabled":False,
        "arbitraryCodeExecution":False,
    }

def _package(req):
    _require(req)
    dataset=_dataset_profile(req)
    catalog=_feature_catalog(req)
    plan=_transformation_plan(req)
    lineage=_lineage(req)
    readiness=_readiness(req)
    payload={
        "datasetId":req.dataset_id,
        "datasetFingerprint":dataset["datasetFingerprint"],
        "featureIds":[x["featureId"] for x in catalog["items"]],
        "transformationIds":[x["transformationId"] for x in plan["items"]],
        "lineageSha256":_sha(lineage),
        "sourceRefs":sorted(set(req.source_refs)),
        "ready":readiness["ready"],
        "packageRef":req.package_ref,
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **payload,
        "packageSha256":_sha(payload),
        "provenancePreserved":True,
        "deterministicTransformationsPreferred":True,
        "automaticExecutionEnabled":False,
        "arbitraryCodeExecution":False,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.57.0",
        "title":"Dataset & Feature Engineering Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "datasetProfiling":True,
        "featureCatalog":True,
        "transformationPlanning":True,
        "featureLineage":True,
        "leakageRiskInspection":True,
        "reproducibilityPackaging":True,
        "automaticFeatureSelectionEnabled":False,
        "automaticTransformationExecutionEnabled":False,
        "automaticLeakageOverrideEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req:DatasetFeatureEngineeringRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported dataset feature engineering operation")
    result={
        OPERATIONS[0]:lambda:_validation(req),
        OPERATIONS[1]:lambda:_dataset_profile(req),
        OPERATIONS[2]:lambda:_feature_catalog(req),
        OPERATIONS[3]:lambda:_transformation_plan(req),
        OPERATIONS[4]:lambda:_lineage(req),
        OPERATIONS[5]:lambda:_readiness(req),
        OPERATIONS[6]:lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.57.0","operation":req.operation,"ok":True,"result":result}
