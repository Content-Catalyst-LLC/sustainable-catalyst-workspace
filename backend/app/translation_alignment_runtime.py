from __future__ import annotations

from collections import Counter
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-translation-alignment-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-translation-alignment-runtime-request/1.0"
RESULT_SCHEMA = "sc-workspace-translation-alignment-runtime-result/1.0"
TRANSFORMATION_SCHEMA = "sc-workspace-language-transformation/1.0"
SEGMENT_SCHEMA = "sc-workspace-parallel-text-segment/1.0"
ALIGNMENT_SCHEMA = "sc-workspace-parallel-alignment-group/1.0"
LINEAGE_SCHEMA = "sc-workspace-translation-alignment-lineage/1.0"

MAX_TRANSFORMATIONS = 10_000
MAX_SEGMENTS = 50_000
MAX_ALIGNMENTS = 50_000

OPERATIONS = (
    "workspace.linguistics.transformation-validate",
    "workspace.linguistics.parallel-alignment-validate",
    "workspace.linguistics.parallel-segment-index",
    "workspace.linguistics.parallel-alignment-profile",
    "workspace.linguistics.parallel-alignment-coverage",
    "workspace.linguistics.translation-alignment-lineage",
)

class LanguageTransformation(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    transformation_id: str = Field(alias="transformationId", min_length=1, max_length=200)
    transformation_type: Literal["translation", "transliteration"] = Field(alias="transformationType")
    source_text_id: str = Field(alias="sourceTextId", min_length=1, max_length=200)
    derived_text_id: str = Field(alias="derivedTextId", min_length=1, max_length=200)
    source_language_tag: str = Field(alias="sourceLanguageTag", min_length=2, max_length=64)
    target_language_tag: str = Field(alias="targetLanguageTag", min_length=2, max_length=64)
    source_script: str | None = Field(default=None, alias="sourceScript", max_length=16)
    target_script: str | None = Field(default=None, alias="targetScript", max_length=16)
    method: Literal["human", "rule", "model", "imported", "other"] = "human"
    agent: str | None = Field(default=None, max_length=300)
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    created_at: str | None = Field(default=None, alias="createdAt", max_length=100)

class ParallelTextSegment(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    segment_id: str = Field(alias="segmentId", min_length=1, max_length=200)
    text_id: str = Field(alias="textId", min_length=1, max_length=200)
    language_tag: str = Field(alias="languageTag", min_length=2, max_length=64)
    script: str | None = Field(default=None, max_length=16)
    ordinal: int = Field(default=0, ge=0)
    text: str = Field(default="", max_length=200_000)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)

class ParallelAlignmentGroup(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    alignment_id: str = Field(alias="alignmentId", min_length=1, max_length=200)
    source_segment_ids: list[str] = Field(alias="sourceSegmentIds", min_length=1, max_length=100)
    target_segment_ids: list[str] = Field(alias="targetSegmentIds", min_length=1, max_length=100)
    relation: Literal["1:1", "1:n", "n:1", "n:m"]
    method: Literal["human", "rule", "model", "imported", "other"] = "human"
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    notes: str | None = Field(default=None, max_length=2000)

class TranslationAlignmentRuntimeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    transformations: list[LanguageTransformation] = Field(default_factory=list, max_length=MAX_TRANSFORMATIONS)
    segments: list[ParallelTextSegment] = Field(default_factory=list, max_length=MAX_SEGMENTS)
    alignments: list[ParallelAlignmentGroup] = Field(default_factory=list, max_length=MAX_ALIGNMENTS)

def operation_catalog() -> list[dict[str, Any]]:
    outputs = (
        "sc-workspace-language-transformation-validation/1.0",
        "sc-workspace-parallel-alignment-validation/1.0",
        "sc-workspace-parallel-segment-index/1.0",
        "sc-workspace-parallel-alignment-profile/1.0",
        "sc-workspace-parallel-alignment-coverage/1.0",
        LINEAGE_SCHEMA,
    )
    return [{"operation": op, "input": REQUEST_SCHEMA, "output": outputs[i], "bounded": True} for i, op in enumerate(OPERATIONS)]

def profile() -> dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA, "version": "3.49.0",
        "title": "Translation, Transliteration & Parallel Alignment Runtime",
        "boundedOperations": list(OPERATIONS), "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True, "translationIsDerivedRepresentation": True,
        "transliterationIsDerivedRepresentation": True,
        "automaticLanguageDetectionEnabled": False, "automaticTranslationEnabled": False,
        "automaticTransliterationEnabled": False, "automaticAlignmentEnabled": False,
        "arbitraryCodeExecution": False,
    }

def _transformation_validation(request):
    seen, issues = set(), []
    derived = Counter()
    for item in request.transformations:
        if item.transformation_id in seen:
            issues.append({"code":"duplicate-transformation-id","transformationId":item.transformation_id})
        seen.add(item.transformation_id)
        derived[item.derived_text_id] += 1
        if item.source_text_id == item.derived_text_id:
            issues.append({"code":"self-derived-text","transformationId":item.transformation_id})
        if item.transformation_type == "transliteration" and item.source_language_tag != item.target_language_tag:
            issues.append({"code":"transliteration-language-mismatch","transformationId":item.transformation_id})
    for text_id, count in derived.items():
        if count > 1:
            issues.append({"code":"multiple-transformations-same-derived-text","derivedTextId":text_id,"count":count})
    return {"schema":"sc-workspace-language-transformation-validation/1.0","valid":not issues,"issueCount":len(issues),"issues":issues,"transformationCount":len(request.transformations)}

def _segment_map(request):
    values, issues = {}, []
    for item in request.segments:
        if item.segment_id in values:
            issues.append({"code":"duplicate-segment-id","segmentId":item.segment_id})
        values[item.segment_id] = item
    return values, issues

def _alignment_validation(request):
    segments, issues = _segment_map(request)
    seen = set()
    for item in request.alignments:
        if item.alignment_id in seen:
            issues.append({"code":"duplicate-alignment-id","alignmentId":item.alignment_id})
        seen.add(item.alignment_id)
        for sid in item.source_segment_ids + item.target_segment_ids:
            if sid not in segments:
                issues.append({"code":"alignment-segment-missing","alignmentId":item.alignment_id,"segmentId":sid})
        expected = ("1:1" if len(item.source_segment_ids)==1 and len(item.target_segment_ids)==1
                    else "1:n" if len(item.source_segment_ids)==1
                    else "n:1" if len(item.target_segment_ids)==1 else "n:m")
        if item.relation != expected:
            issues.append({"code":"alignment-relation-mismatch","alignmentId":item.alignment_id,"expectedRelation":expected,"actualRelation":item.relation})
    return {"schema":"sc-workspace-parallel-alignment-validation/1.0","valid":not issues,"issueCount":len(issues),"issues":issues,"segmentCount":len(segments),"alignmentCount":len(request.alignments)}

def _parallel_segment_index(request):
    segments, issues = _segment_map(request)
    if issues: raise ValueError(f"parallel segment validation failed with {len(issues)} issue(s)")
    items=[{"segmentId":s.segment_id,"textId":s.text_id,"languageTag":s.language_tag,"script":s.script,"ordinal":s.ordinal,"text":s.text,"sourceRef":s.source_ref}
           for s in sorted(segments.values(), key=lambda x:(x.text_id,x.ordinal,x.segment_id))]
    return {"schema":"sc-workspace-parallel-segment-index/1.0","count":len(items),"items":items}

def _alignment_profile(request):
    v=_alignment_validation(request)
    if not v["valid"]: raise ValueError(f"parallel alignment validation failed with {v['issueCount']} issue(s)")
    relations=Counter(x.relation for x in request.alignments)
    methods=Counter(x.method for x in request.alignments)
    return {"schema":"sc-workspace-parallel-alignment-profile/1.0","alignmentCount":len(request.alignments),
            "relationDistribution":dict(sorted(relations.items())),"methodDistribution":dict(sorted(methods.items()))}

def _coverage(request):
    v=_alignment_validation(request)
    if not v["valid"]: raise ValueError(f"parallel alignment validation failed with {v['issueCount']} issue(s)")
    aligned=set()
    for x in request.alignments:
        aligned.update(x.source_segment_ids); aligned.update(x.target_segment_ids)
    total=len(request.segments)
    return {"schema":"sc-workspace-parallel-alignment-coverage/1.0","segmentCount":total,
            "alignedSegmentCount":len(aligned),"unalignedSegmentCount":max(0,total-len(aligned)),
            "coverage":(len(aligned)/total) if total else 0.0,"fullyAligned":total>0 and len(aligned)==total}

def _lineage(request):
    tv=_transformation_validation(request); av=_alignment_validation(request)
    if not tv["valid"]: raise ValueError(f"transformation validation failed with {tv['issueCount']} issue(s)")
    if not av["valid"]: raise ValueError(f"alignment validation failed with {av['issueCount']} issue(s)")
    t_edges=[{"fromTextId":x.source_text_id,"toTextId":x.derived_text_id,"relation":x.transformation_type,
              "sourceLanguageTag":x.source_language_tag,"targetLanguageTag":x.target_language_tag,
              "method":x.method,"agent":x.agent,"confidence":x.confidence,"sourceRef":x.source_ref}
             for x in request.transformations]
    a_edges=[{"alignmentId":x.alignment_id,"sourceSegmentIds":x.source_segment_ids,"targetSegmentIds":x.target_segment_ids,
              "relation":x.relation,"method":x.method,"confidence":x.confidence,"sourceRef":x.source_ref}
             for x in request.alignments]
    return {"schema":LINEAGE_SCHEMA,"transformationEdgeCount":len(t_edges),"alignmentEdgeCount":len(a_edges),
            "transformationEdges":t_edges,"alignmentEdges":a_edges,
            "originalLanguageRemainsCanonical":True,"provenancePreserved":True}

_EXECUTORS={
    OPERATIONS[0]:_transformation_validation, OPERATIONS[1]:_alignment_validation,
    OPERATIONS[2]:_parallel_segment_index, OPERATIONS[3]:_alignment_profile,
    OPERATIONS[4]:_coverage, OPERATIONS[5]:_lineage,
}

def execute(request: TranslationAlignmentRuntimeRequest) -> dict[str, Any]:
    if request.schema_ != REQUEST_SCHEMA: raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    fn=_EXECUTORS.get(request.operation)
    if fn is None: raise ValueError(f"unsupported bounded operation: {request.operation}")
    return {"schema":RESULT_SCHEMA,"version":"3.49.0","operation":request.operation,"result":fn(request),
            "policy":{"originalLanguageFirst":True,"translationIsDerivedRepresentation":True,
                      "transliterationIsDerivedRepresentation":True,
                      "automaticLanguageDetectionEnabled":False,"automaticTranslationEnabled":False,
                      "automaticTransliterationEnabled":False,"automaticAlignmentEnabled":False,
                      "arbitraryCodeExecution":False}}
