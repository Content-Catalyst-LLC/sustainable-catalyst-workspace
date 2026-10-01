from __future__ import annotations

import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-integrated-global-language-research-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-integrated-global-language-research-request/1.0"
RESULT_SCHEMA = "sc-workspace-integrated-global-language-research-result/1.0"
PROJECT_SCHEMA = "sc-workspace-global-language-research-project/1.0"
LAYER_SCHEMA = "sc-workspace-global-language-research-layer/1.0"
EVIDENCE_VIEW_SCHEMA = "sc-workspace-cross-civilizational-evidence-view/1.0"
TRUST_VIEW_SCHEMA = "sc-workspace-source-quality-user-trust-view/1.0"
LINEAGE_SCHEMA = "sc-workspace-global-language-research-lineage/1.0"
PACKAGE_SCHEMA = "sc-workspace-global-language-research-package/1.0"

OPERATIONS = (
    "workspace.linguistics.global-language-project-validate",
    "workspace.linguistics.research-layer-index",
    "workspace.linguistics.cross-civilizational-evidence-view",
    "workspace.linguistics.source-quality-user-trust-view",
    "workspace.linguistics.integrated-lineage-graph",
    "workspace.linguistics.global-language-readiness",
    "workspace.linguistics.global-language-research-package",
)

REQUIRED_LAYERS = (
    "original-language-corpus",
    "linguistic-annotation",
    "translation-alignment",
    "historical-language-identity",
    "entity-toponym-resolution",
    "cross-lingual-semantic-evidence",
    "reproducible-computational-linguistics",
)

class ResearchLayer(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    layer_id: str = Field(alias="layerId", min_length=1, max_length=200)
    layer_kind: str = Field(alias="layerKind", min_length=1, max_length=200)
    object_refs: list[str] = Field(default_factory=list, alias="objectRefs", max_length=5000)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=5000)
    lineage_refs: list[str] = Field(default_factory=list, alias="lineageRefs", max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)

class EvidenceRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    relation_id: str = Field(alias="relationId", min_length=1, max_length=200)
    source_ref: str = Field(alias="sourceRef", min_length=1, max_length=500)
    target_ref: str = Field(alias="targetRef", min_length=1, max_length=500)
    relation_type: str = Field(alias="relationType", min_length=1, max_length=100)
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs", max_length=500)
    human_reviewed: bool = Field(default=False, alias="humanReviewed")

class SourceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_ref: str = Field(alias="sourceRef", min_length=1, max_length=500)
    quality_signals: dict[str, Any] = Field(default_factory=dict, alias="qualitySignals")
    user_trust_state: str | None = Field(default=None, alias="userTrustState", max_length=100)
    user_trust_reason: str | None = Field(default=None, alias="userTrustReason", max_length=2000)

class IntegratedGlobalLanguageResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    project_id: str = Field(default="global-language-project", alias="projectId", min_length=1, max_length=200)
    title: str | None = Field(default=None, max_length=500)
    layers: list[ResearchLayer] = Field(default_factory=list, max_length=1000)
    evidence_relations: list[EvidenceRelation] = Field(default_factory=list, alias="evidenceRelations", max_length=50000)
    source_assessments: list[SourceAssessment] = Field(default_factory=list, alias="sourceAssessments", max_length=10000)
    package_ref: str | None = Field(default=None, alias="packageRef", max_length=500)

def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()

def _validate(req: IntegratedGlobalLanguageResearchRequest) -> dict[str, Any]:
    issues=[]
    layer_ids=set()
    for layer in req.layers:
        if layer.layer_id in layer_ids:
            issues.append({"code":"duplicate-layer-id","layerId":layer.layer_id})
        layer_ids.add(layer.layer_id)
        if not layer.source_refs and layer.layer_kind != "reproducible-computational-linguistics":
            issues.append({"code":"layer-source-provenance-missing","layerId":layer.layer_id})
    relation_ids=set()
    for relation in req.evidence_relations:
        if relation.relation_id in relation_ids:
            issues.append({"code":"duplicate-evidence-relation-id","relationId":relation.relation_id})
        relation_ids.add(relation.relation_id)
        if relation.relation_type in {"equivalent","near-equivalent"} and not relation.human_reviewed:
            issues.append({"code":"cross-language-equivalence-requires-human-review","relationId":relation.relation_id})
    return {
        "schema":"sc-workspace-integrated-global-language-research-validation/1.0",
        "valid":not issues,
        "issueCount":len(issues),
        "issues":issues,
        "layerCount":len(req.layers),
        "evidenceRelationCount":len(req.evidence_relations),
        "sourceAssessmentCount":len(req.source_assessments),
    }

def _require(req):
    result=_validate(req)
    if not result["valid"]:
        raise ValueError(f"integrated global language research validation failed with {result['issueCount']} issue(s)")

def _layer_index(req):
    _require(req)
    rows=[{
        "schema":LAYER_SCHEMA,
        "layerId":x.layer_id,
        "layerKind":x.layer_kind,
        "objectRefs":x.object_refs,
        "sourceRefs":x.source_refs,
        "lineageRefs":x.lineage_refs,
        "objectCount":len(x.object_refs),
    } for x in req.layers]
    kinds={x.layer_kind for x in req.layers}
    return {
        "schema":"sc-workspace-global-language-research-layer-index/1.0",
        "projectId":req.project_id,
        "items":rows,
        "layerCount":len(rows),
        "requiredLayerKinds":list(REQUIRED_LAYERS),
        "presentRequiredLayerKinds":sorted(kinds & set(REQUIRED_LAYERS)),
        "missingRequiredLayerKinds":[x for x in REQUIRED_LAYERS if x not in kinds],
    }

def _evidence_view(req):
    _require(req)
    return {
        "schema":EVIDENCE_VIEW_SCHEMA,
        "projectId":req.project_id,
        "items":[x.model_dump(by_alias=True) for x in req.evidence_relations],
        "relationCount":len(req.evidence_relations),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "crossCivilizationalEvidenceLinking":True,
        "automaticSemanticEquivalenceEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "humanReviewRequiredForEquivalence":True,
    }

def _trust_view(req):
    _require(req)
    return {
        "schema":TRUST_VIEW_SCHEMA,
        "projectId":req.project_id,
        "items":[x.model_dump(by_alias=True) for x in req.source_assessments],
        "sourceCount":len(req.source_assessments),
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "automaticTrustDecisionEnabled":False,
        "userTrustChoicePreserved":True,
    }

def _lineage(req):
    _require(req)
    nodes=[]
    edges=[]
    for layer in req.layers:
        nodes.append({"id":layer.layer_id,"kind":layer.layer_kind,"objectRefs":layer.object_refs,"sourceRefs":layer.source_refs})
        for ref in layer.lineage_refs:
            edges.append({"source":ref,"target":layer.layer_id,"relation":"derived-layer"})
    for relation in req.evidence_relations:
        edges.append({"source":relation.source_ref,"target":relation.target_ref,"relation":relation.relation_type,"relationId":relation.relation_id})
    return {
        "schema":LINEAGE_SCHEMA,
        "projectId":req.project_id,
        "nodes":nodes,
        "edges":edges,
        "provenancePreserved":True,
        "transformationLineagePreserved":True,
        "historicalLanguageIdentityPreserved":True,
    }

def _readiness(req):
    _require(req)
    kinds={x.layer_kind for x in req.layers}
    missing=[x for x in REQUIRED_LAYERS if x not in kinds]
    source_refs={ref for layer in req.layers for ref in layer.source_refs}
    return {
        "schema":"sc-workspace-global-language-research-readiness/1.0",
        "projectId":req.project_id,
        "ready":not missing and bool(source_refs),
        "missingRequiredLayerKinds":missing,
        "sourceReferenceCount":len(source_refs),
        "requiredLayerCount":len(REQUIRED_LAYERS),
        "presentRequiredLayerCount":len(REQUIRED_LAYERS)-len(missing),
        "automaticPublicationEnabled":False,
        "humanReviewRequired":True,
    }

def _package(req):
    _require(req)
    index=_layer_index(req)
    lineage=_lineage(req)
    payload={
        "projectId":req.project_id,
        "title":req.title,
        "packageRef":req.package_ref,
        "layerKinds":[x["layerKind"] for x in index["items"]],
        "lineageSha256":_sha(lineage),
        "evidenceRelationIds":[x.relation_id for x in req.evidence_relations],
        "sourceRefs":sorted({ref for layer in req.layers for ref in layer.source_refs}),
    }
    return {
        "schema":PACKAGE_SCHEMA,
        **payload,
        "packageSha256":_sha(payload),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "provenancePreserved":True,
        "arbitraryCodeExecution":False,
    }

def profile():
    return {
        "schema":RUNTIME_SCHEMA,
        "version":"3.54.0",
        "title":"Integrated Global Language Research Runtime",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "integratesWorkspaceVersions":["3.47.0","3.48.0","3.49.0","3.50.0","3.51.0","3.52.0","3.53.0"],
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "historicalLanguageIdentityPreserved":True,
        "crossCivilizationalEvidenceLinking":True,
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "automaticTranslationEnabled":False,
        "automaticEntityMergeEnabled":False,
        "automaticSemanticEquivalenceEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticPublicationEnabled":False,
        "humanReviewRequired":True,
        "provenancePreserved":True,
        "arbitraryCodeExecution":False,
    }

def operation_catalog():
    return [{"operation":x,"input":REQUEST_SCHEMA,"output":RESULT_SCHEMA,"bounded":True} for x in OPERATIONS]

def execute(req: IntegratedGlobalLanguageResearchRequest):
    if req.operation not in OPERATIONS:
        raise ValueError("unsupported integrated global language research operation")
    payload={
        OPERATIONS[0]: lambda:_validate(req),
        OPERATIONS[1]: lambda:_layer_index(req),
        OPERATIONS[2]: lambda:_evidence_view(req),
        OPERATIONS[3]: lambda:_trust_view(req),
        OPERATIONS[4]: lambda:_lineage(req),
        OPERATIONS[5]: lambda:_readiness(req),
        OPERATIONS[6]: lambda:_package(req),
    }[req.operation]()
    return {"schema":RESULT_SCHEMA,"version":"3.54.0","operation":req.operation,"ok":True,"result":payload}
