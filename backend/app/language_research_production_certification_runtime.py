from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA="sc-workspace-language-research-production-certification-runtime/1.0"
REQUEST_SCHEMA="sc-workspace-language-research-production-certification-request/1.0"
RESULT_SCHEMA="sc-workspace-language-research-production-certification-result/1.0"
REPORT_SCHEMA="sc-workspace-language-research-production-certification-report/1.0"
PACKAGE_SCHEMA="sc-workspace-language-research-production-certification-package/1.0"

OPERATIONS=(
    "workspace.linguistics.production-certification-validate",
    "workspace.linguistics.release-identity-check",
    "workspace.linguistics.language-layer-continuity-check",
    "workspace.linguistics.provenance-guardrail-check",
    "workspace.linguistics.runtime-safety-check",
    "workspace.linguistics.deployment-readiness-check",
    "workspace.linguistics.production-certification-package",
)

REQUIRED_LAYERS=(
    "original-language-corpus",
    "linguistic-annotation",
    "translation-alignment",
    "historical-language-identity",
    "entity-toponym-resolution",
    "cross-lingual-semantic-evidence",
    "reproducible-computational-linguistics",
    "integrated-global-language-research",
)

class CertificationTarget(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    component:str=Field(min_length=1,max_length=200)
    version:str=Field(min_length=1,max_length=100)
    schema_ref:str|None=Field(default=None,alias="schemaRef",max_length=500)
    artifact_ref:str|None=Field(default=None,alias="artifactRef",max_length=500)
    sha256:str|None=Field(default=None,max_length=128)

class LanguageLayerStatus(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    layer_kind:str=Field(alias="layerKind",min_length=1,max_length=200)
    available:bool=True
    source_refs:list[str]=Field(default_factory=list,alias="sourceRefs",max_length=1000)
    lineage_refs:list[str]=Field(default_factory=list,alias="lineageRefs",max_length=1000)

class GuardrailStatus(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    original_language_first:bool=Field(default=True,alias="originalLanguageFirst")
    translation_is_derived_representation:bool=Field(default=True,alias="translationIsDerivedRepresentation")
    provenance_preserved:bool=Field(default=True,alias="provenancePreserved")
    human_review_required:bool=Field(default=True,alias="humanReviewRequired")
    source_quality_signals_separated_from_user_trust:bool=Field(default=True,alias="sourceQualitySignalsSeparatedFromUserTrust")
    arbitrary_code_execution:bool=Field(default=False,alias="arbitraryCodeExecution")
    automatic_truth_determination_enabled:bool=Field(default=False,alias="automaticTruthDeterminationEnabled")
    automatic_evidence_ranking_enabled:bool=Field(default=False,alias="automaticEvidenceRankingEnabled")
    automatic_publication_enabled:bool=Field(default=False,alias="automaticPublicationEnabled")

class DeploymentStatus(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    backend_health_ok:bool=Field(default=False,alias="backendHealthOk")
    backend_version:str|None=Field(default=None,alias="backendVersion",max_length=100)
    persistence:str|None=Field(default=None,max_length=100)
    worker_version:str|None=Field(default=None,alias="workerVersion",max_length=100)
    wordpress_version:str|None=Field(default=None,alias="wordpressVersion",max_length=100)
    authenticated_profile_ok:bool=Field(default=False,alias="authenticatedProfileOk")
    operation_catalog_ok:bool=Field(default=False,alias="operationCatalogOk")
    package_integrity_ok:bool=Field(default=False,alias="packageIntegrityOk")

class LanguageResearchProductionCertificationRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", populate_by_name=True)
    schema_:str=Field(default=REQUEST_SCHEMA,alias="schema")
    operation:str
    release_version:str=Field(default="3.55.0",alias="releaseVersion",min_length=1,max_length=100)
    targets:list[CertificationTarget]=Field(default_factory=list,max_length=1000)
    layers:list[LanguageLayerStatus]=Field(default_factory=list,max_length=1000)
    guardrails:GuardrailStatus=Field(default_factory=GuardrailStatus)
    deployment:DeploymentStatus=Field(default_factory=DeploymentStatus)
    package_ref:str|None=Field(default=None,alias="packageRef",max_length=500)

def _canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _sha(value:Any)->str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validate(req):
    issues=[]
    if req.release_version!="3.55.0":
        issues.append({"code":"release-version-mismatch","expected":"3.55.0","actual":req.release_version})
    seen=set()
    for target in req.targets:
        key=(target.component,target.version)
        if key in seen: issues.append({"code":"duplicate-target","component":target.component,"version":target.version})
        seen.add(key)
    return {"schema":"sc-workspace-language-research-production-certification-validation/1.0","valid":not issues,"issueCount":len(issues),"issues":issues}

def _identity(req):
    _validate_or_raise(req)
    versions={x.component:x.version for x in req.targets}
    return {
        "schema":"sc-workspace-language-research-release-identity-check/1.0",
        "releaseVersion":req.release_version,
        "targets":[x.model_dump(by_alias=True) for x in req.targets],
        "targetCount":len(req.targets),
        "backendVersionMatchesRelease":versions.get("backend") in {None,req.release_version},
        "wordpressVersionMatchesRelease":versions.get("wordpress") in {None,req.release_version},
    }

def _layers(req):
    _validate_or_raise(req)
    present={x.layer_kind for x in req.layers if x.available}
    missing=[x for x in REQUIRED_LAYERS if x not in present]
    return {
        "schema":"sc-workspace-language-layer-continuity-check/1.0",
        "requiredLayers":list(REQUIRED_LAYERS),
        "presentLayers":sorted(present),
        "missingLayers":missing,
        "requiredLayerCount":len(REQUIRED_LAYERS),
        "presentRequiredLayerCount":len(REQUIRED_LAYERS)-len(missing),
        "pass":not missing,
    }

def _guardrails(req):
    _validate_or_raise(req)
    g=req.guardrails
    checks={
        "originalLanguageFirst":g.original_language_first,
        "translationIsDerivedRepresentation":g.translation_is_derived_representation,
        "provenancePreserved":g.provenance_preserved,
        "humanReviewRequired":g.human_review_required,
        "sourceQualitySignalsSeparatedFromUserTrust":g.source_quality_signals_separated_from_user_trust,
        "arbitraryCodeExecutionDisabled":not g.arbitrary_code_execution,
        "automaticTruthDeterminationDisabled":not g.automatic_truth_determination_enabled,
        "automaticEvidenceRankingDisabled":not g.automatic_evidence_ranking_enabled,
        "automaticPublicationDisabled":not g.automatic_publication_enabled,
    }
    return {"schema":"sc-workspace-language-research-provenance-guardrail-check/1.0","checks":checks,"pass":all(checks.values())}

def _safety(req):
    _validate_or_raise(req)
    return {
        "schema":"sc-workspace-language-research-runtime-safety-check/1.0",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "arbitraryCodeExecution":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticPublicationEnabled":False,
        "humanReviewRequired":True,
        "pass":True,
    }

def _deployment(req):
    _validate_or_raise(req)
    d=req.deployment
    checks={
        "backendHealthOk":d.backend_health_ok,
        "backendVersionMatchesRelease":d.backend_version in {None,req.release_version},
        "postgresqlPersistence":d.persistence in {None,"postgresql"},
        "workerVersionMatchesRelease":d.worker_version in {None,req.release_version},
        "wordpressVersionMatchesRelease":d.wordpress_version in {None,req.release_version},
        "authenticatedProfileOk":d.authenticated_profile_ok,
        "operationCatalogOk":d.operation_catalog_ok,
        "packageIntegrityOk":d.package_integrity_ok,
    }
    return {"schema":"sc-workspace-language-research-deployment-readiness-check/1.0","checks":checks,"pass":all(checks.values())}

def _package(req):
    _validate_or_raise(req)
    report={
        "releaseIdentity":_identity(req),
        "languageLayerContinuity":_layers(req),
        "provenanceGuardrails":_guardrails(req),
        "runtimeSafety":_safety(req),
        "deploymentReadiness":_deployment(req),
    }
    certified=all(x.get("pass",True) for x in report.values()) and report["releaseIdentity"]["backendVersionMatchesRelease"] and report["releaseIdentity"]["wordpressVersionMatchesRelease"]
    payload={"releaseVersion":req.release_version,"packageRef":req.package_ref,"certified":certified,"report":report}
    return {"schema":PACKAGE_SCHEMA,**payload,"packageSha256":_sha(payload),"immutableCertificationRecordRecommended":True}

def _validate_or_raise(req):
    result=_validate(req)
    if not result["valid"]:
        raise ValueError(f"language research production certification validation failed with {result['issueCount']} issue(s)")

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.55.0",
        "title":"Language Research Production Certification Runtime",
        "certifiesWorkspaceVersions":["3.47.0","3.48.0","3.49.0","3.50.0","3.51.0","3.52.0","3.53.0","3.54.0"],
        "requiredLayers":list(REQUIRED_LAYERS),
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "provenancePreserved":True,
        "humanReviewRequired":True,
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticPublicationEnabled":False,
        "arbitraryCodeExecution":False,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req:LanguageResearchProductionCertificationRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported language research production certification operation")
    result={
        OPERATIONS[0]:lambda:_validate(req),
        OPERATIONS[1]:lambda:_identity(req),
        OPERATIONS[2]:lambda:_layers(req),
        OPERATIONS[3]:lambda:_guardrails(req),
        OPERATIONS[4]:lambda:_safety(req),
        OPERATIONS[5]:lambda:_deployment(req),
        OPERATIONS[6]:lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.55.0","operation":req.operation,"ok":True,"result":result}
