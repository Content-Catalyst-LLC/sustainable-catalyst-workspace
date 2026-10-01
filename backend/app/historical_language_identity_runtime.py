from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RUNTIME_SCHEMA = "sc-workspace-historical-language-identity-runtime/1.0"
REQUEST_SCHEMA = "sc-workspace-historical-language-identity-runtime-request/1.0"
RESULT_SCHEMA = "sc-workspace-historical-language-identity-runtime-result/1.0"
LANGUAGE_IDENTITY_SCHEMA = "sc-workspace-historical-language-identity/1.0"
SCRIPT_IDENTITY_SCHEMA = "sc-workspace-script-identity/1.0"
VARIANT_SCHEMA = "sc-workspace-language-variant-identity/1.0"
RELATION_SCHEMA = "sc-workspace-historical-language-identity-relation/1.0"
LINEAGE_SCHEMA = "sc-workspace-historical-language-identity-lineage/1.0"

MAX_LANGUAGE_IDENTITIES = 10_000
MAX_SCRIPT_IDENTITIES = 5_000
MAX_VARIANTS = 25_000
MAX_RELATIONS = 50_000

OPERATIONS = (
    "workspace.linguistics.historical-identity-validate",
    "workspace.linguistics.historical-variant-index",
    "workspace.linguistics.historical-temporal-profile",
    "workspace.linguistics.script-orthography-profile",
    "workspace.linguistics.historical-relationship-graph",
    "workspace.linguistics.historical-identity-lineage",
)

RELATION_TYPES = {
    "predecessor-of", "successor-of", "historical-stage-of", "dialect-of", "variety-of",
    "script-variant-of", "orthographic-variant-of", "normalized-form-of",
    "modernized-form-of", "related-to",
}


class TemporalScope(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    start_year: int | None = Field(default=None, alias="startYear")
    end_year: int | None = Field(default=None, alias="endYear")
    chronology_label: str | None = Field(default=None, alias="chronologyLabel", max_length=300)
    approximate: bool = False
    uncertainty: str | None = Field(default=None, max_length=1000)


class HistoricalLanguageIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    identity_id: str = Field(alias="identityId", min_length=1, max_length=200)
    label: str = Field(min_length=1, max_length=300)
    kind: Literal["language", "historical-stage", "dialect", "variety", "register", "mixed", "other"] = "language"
    language_tag: str | None = Field(default=None, alias="languageTag", max_length=64)
    aliases: list[str] = Field(default_factory=list, max_length=100)
    external_identifiers: dict[str, str] = Field(default_factory=dict, alias="externalIdentifiers")
    script_ids: list[str] = Field(default_factory=list, alias="scriptIds", max_length=100)
    regions: list[str] = Field(default_factory=list, max_length=100)
    temporal_scope: TemporalScope = Field(default_factory=TemporalScope, alias="temporalScope")
    parent_identity_id: str | None = Field(default=None, alias="parentIdentityId", max_length=200)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class ScriptIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    script_id: str = Field(alias="scriptId", min_length=1, max_length=200)
    label: str = Field(min_length=1, max_length=300)
    script_code: str | None = Field(default=None, alias="scriptCode", max_length=16)
    aliases: list[str] = Field(default_factory=list, max_length=100)
    direction: Literal["ltr", "rtl", "ttb", "btt", "unknown"] = "unknown"
    parent_script_id: str | None = Field(default=None, alias="parentScriptId", max_length=200)
    regions: list[str] = Field(default_factory=list, max_length=100)
    temporal_scope: TemporalScope = Field(default_factory=TemporalScope, alias="temporalScope")
    external_identifiers: dict[str, str] = Field(default_factory=dict, alias="externalIdentifiers")
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class LanguageVariantIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    variant_id: str = Field(alias="variantId", min_length=1, max_length=200)
    label: str = Field(min_length=1, max_length=300)
    kind: Literal["orthography", "spelling", "regional", "historical", "scribal", "print", "normalized", "other"] = "other"
    language_identity_id: str = Field(alias="languageIdentityId", min_length=1, max_length=200)
    script_identity_id: str | None = Field(default=None, alias="scriptIdentityId", max_length=200)
    aliases: list[str] = Field(default_factory=list, max_length=100)
    regions: list[str] = Field(default_factory=list, max_length=100)
    temporal_scope: TemporalScope = Field(default_factory=TemporalScope, alias="temporalScope")
    external_identifiers: dict[str, str] = Field(default_factory=dict, alias="externalIdentifiers")
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class HistoricalIdentityRelation(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    relation_id: str = Field(alias="relationId", min_length=1, max_length=200)
    from_id: str = Field(alias="fromId", min_length=1, max_length=200)
    to_id: str = Field(alias="toId", min_length=1, max_length=200)
    relation_type: Literal[
        "predecessor-of", "successor-of", "historical-stage-of", "dialect-of", "variety-of",
        "script-variant-of", "orthographic-variant-of", "normalized-form-of",
        "modernized-form-of", "related-to"
    ] = Field(alias="relationType")
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_ref: str | None = Field(default=None, alias="sourceRef", max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class HistoricalLanguageIdentityRuntimeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    schema_: str = Field(default=REQUEST_SCHEMA, alias="schema")
    operation: str
    language_identities: list[HistoricalLanguageIdentity] = Field(
        default_factory=list, alias="languageIdentities", max_length=MAX_LANGUAGE_IDENTITIES
    )
    script_identities: list[ScriptIdentity] = Field(
        default_factory=list, alias="scriptIdentities", max_length=MAX_SCRIPT_IDENTITIES
    )
    variants: list[LanguageVariantIdentity] = Field(default_factory=list, max_length=MAX_VARIANTS)
    relations: list[HistoricalIdentityRelation] = Field(default_factory=list, max_length=MAX_RELATIONS)


def operation_catalog() -> list[dict[str, Any]]:
    outputs = (
        "sc-workspace-historical-language-identity-validation/1.0",
        "sc-workspace-historical-language-variant-index/1.0",
        "sc-workspace-historical-language-temporal-profile/1.0",
        "sc-workspace-script-orthography-profile/1.0",
        "sc-workspace-historical-language-relationship-graph/1.0",
        LINEAGE_SCHEMA,
    )
    return [
        {"operation": operation, "input": REQUEST_SCHEMA, "output": outputs[index], "bounded": True}
        for index, operation in enumerate(OPERATIONS)
    ]


def profile() -> dict[str, Any]:
    return {
        "schema": RUNTIME_SCHEMA,
        "version": "3.50.0",
        "title": "Historical Language, Script & Variant Identity Runtime",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True,
        "historicalIdentityPreserved": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticModernizationEnabled": False,
        "automaticVariantNormalizationEnabled": False,
        "automaticTranslationEnabled": False,
        "arbitraryCodeExecution": False,
    }


def _scope_issues(scope: TemporalScope, object_id: str) -> list[dict[str, Any]]:
    issues = []
    if scope.start_year is not None and scope.end_year is not None and scope.end_year < scope.start_year:
        issues.append({"code": "temporal-scope-order", "objectId": object_id})
    return issues


def _validate(request):
    issues = []
    languages = {}
    scripts = {}
    variants = {}
    relations = set()

    for item in request.language_identities:
        if item.identity_id in languages:
            issues.append({"code": "duplicate-language-identity", "identityId": item.identity_id})
        languages[item.identity_id] = item
        issues.extend(_scope_issues(item.temporal_scope, item.identity_id))

    for item in request.script_identities:
        if item.script_id in scripts:
            issues.append({"code": "duplicate-script-identity", "scriptId": item.script_id})
        scripts[item.script_id] = item
        issues.extend(_scope_issues(item.temporal_scope, item.script_id))

    for item in request.variants:
        if item.variant_id in variants:
            issues.append({"code": "duplicate-variant-identity", "variantId": item.variant_id})
        variants[item.variant_id] = item
        issues.extend(_scope_issues(item.temporal_scope, item.variant_id))

    all_ids = set(languages) | set(scripts) | set(variants)

    for item in languages.values():
        if item.parent_identity_id and item.parent_identity_id not in languages:
            issues.append({"code": "language-parent-missing", "identityId": item.identity_id, "parentIdentityId": item.parent_identity_id})
        for script_id in item.script_ids:
            if script_id not in scripts:
                issues.append({"code": "language-script-missing", "identityId": item.identity_id, "scriptId": script_id})

    for item in scripts.values():
        if item.parent_script_id and item.parent_script_id not in scripts:
            issues.append({"code": "script-parent-missing", "scriptId": item.script_id, "parentScriptId": item.parent_script_id})

    for item in variants.values():
        if item.language_identity_id not in languages:
            issues.append({"code": "variant-language-missing", "variantId": item.variant_id, "languageIdentityId": item.language_identity_id})
        if item.script_identity_id and item.script_identity_id not in scripts:
            issues.append({"code": "variant-script-missing", "variantId": item.variant_id, "scriptIdentityId": item.script_identity_id})

    for item in request.relations:
        if item.relation_id in relations:
            issues.append({"code": "duplicate-relation-id", "relationId": item.relation_id})
        relations.add(item.relation_id)
        if item.from_id == item.to_id:
            issues.append({"code": "self-relation", "relationId": item.relation_id})
        if item.from_id not in all_ids:
            issues.append({"code": "relation-from-missing", "relationId": item.relation_id, "fromId": item.from_id})
        if item.to_id not in all_ids:
            issues.append({"code": "relation-to-missing", "relationId": item.relation_id, "toId": item.to_id})

    parent_map = {item.identity_id: item.parent_identity_id for item in languages.values() if item.parent_identity_id}
    for start in parent_map:
        seen = {start}
        current = parent_map.get(start)
        while current:
            if current in seen:
                issues.append({"code": "language-parent-cycle", "identityId": start})
                break
            seen.add(current)
            current = parent_map.get(current)

    script_parent_map = {item.script_id: item.parent_script_id for item in scripts.values() if item.parent_script_id}
    for start in script_parent_map:
        seen = {start}
        current = script_parent_map.get(start)
        while current:
            if current in seen:
                issues.append({"code": "script-parent-cycle", "scriptId": start})
                break
            seen.add(current)
            current = script_parent_map.get(current)

    return {
        "schema": "sc-workspace-historical-language-identity-validation/1.0",
        "valid": not issues,
        "issueCount": len(issues),
        "issues": issues,
        "languageIdentityCount": len(languages),
        "scriptIdentityCount": len(scripts),
        "variantCount": len(variants),
        "relationCount": len(request.relations),
    }


def _require_valid(request):
    result = _validate(request)
    if not result["valid"]:
        raise ValueError(f"historical language identity validation failed with {result['issueCount']} issue(s)")
    return result


def _variant_index(request):
    _require_valid(request)
    languages = {x.identity_id: x for x in request.language_identities}
    scripts = {x.script_id: x for x in request.script_identities}
    items = []
    for item in sorted(request.variants, key=lambda x: (x.language_identity_id, x.kind, x.label, x.variant_id)):
        items.append({
            "variantId": item.variant_id,
            "label": item.label,
            "kind": item.kind,
            "languageIdentityId": item.language_identity_id,
            "languageLabel": languages[item.language_identity_id].label,
            "scriptIdentityId": item.script_identity_id,
            "scriptLabel": scripts[item.script_identity_id].label if item.script_identity_id else None,
            "regions": item.regions,
            "temporalScope": item.temporal_scope.model_dump(by_alias=True),
        })
    return {"schema": "sc-workspace-historical-language-variant-index/1.0", "count": len(items), "items": items}


def _temporal_profile(request):
    _require_valid(request)
    periods = []
    for item in request.language_identities:
        periods.append({
            "objectType": "language-identity",
            "objectId": item.identity_id,
            "label": item.label,
            "kind": item.kind,
            "temporalScope": item.temporal_scope.model_dump(by_alias=True),
        })
    for item in request.script_identities:
        periods.append({
            "objectType": "script-identity",
            "objectId": item.script_id,
            "label": item.label,
            "kind": "script",
            "temporalScope": item.temporal_scope.model_dump(by_alias=True),
        })
    for item in request.variants:
        periods.append({
            "objectType": "variant",
            "objectId": item.variant_id,
            "label": item.label,
            "kind": item.kind,
            "temporalScope": item.temporal_scope.model_dump(by_alias=True),
        })
    periods.sort(key=lambda x: (
        x["temporalScope"].get("startYear") is None,
        x["temporalScope"].get("startYear") if x["temporalScope"].get("startYear") is not None else 10**9,
        x["label"],
    ))
    return {
        "schema": "sc-workspace-historical-language-temporal-profile/1.0",
        "count": len(periods),
        "items": periods,
        "automaticChronologyConversion": False,
    }


def _script_orthography_profile(request):
    _require_valid(request)
    script_use = Counter()
    variant_kinds = Counter()
    direction_counts = Counter(x.direction for x in request.script_identities)

    for item in request.language_identities:
        for script_id in item.script_ids:
            script_use[script_id] += 1
    for item in request.variants:
        variant_kinds[item.kind] += 1
        if item.script_identity_id:
            script_use[item.script_identity_id] += 1

    scripts = []
    for item in sorted(request.script_identities, key=lambda x: (x.label, x.script_id)):
        scripts.append({
            "scriptId": item.script_id,
            "label": item.label,
            "scriptCode": item.script_code,
            "direction": item.direction,
            "usageReferenceCount": script_use.get(item.script_id, 0),
            "temporalScope": item.temporal_scope.model_dump(by_alias=True),
        })

    return {
        "schema": "sc-workspace-script-orthography-profile/1.0",
        "scriptCount": len(scripts),
        "variantCount": len(request.variants),
        "scripts": scripts,
        "variantKindDistribution": dict(sorted(variant_kinds.items())),
        "scriptDirectionDistribution": dict(sorted(direction_counts.items())),
    }


def _relationship_graph(request):
    _require_valid(request)
    nodes = []
    for item in request.language_identities:
        nodes.append({"id": item.identity_id, "type": "language-identity", "label": item.label, "kind": item.kind})
    for item in request.script_identities:
        nodes.append({"id": item.script_id, "type": "script-identity", "label": item.label, "kind": "script"})
    for item in request.variants:
        nodes.append({"id": item.variant_id, "type": "variant", "label": item.label, "kind": item.kind})

    edges = [
        {
            "relationId": item.relation_id,
            "fromId": item.from_id,
            "toId": item.to_id,
            "relationType": item.relation_type,
            "confidence": item.confidence,
            "sourceRef": item.source_ref,
        }
        for item in request.relations
    ]
    return {
        "schema": "sc-workspace-historical-language-relationship-graph/1.0",
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def _lineage(request):
    _require_valid(request)
    lineage_relations = {
        "predecessor-of", "successor-of", "historical-stage-of", "dialect-of", "variety-of",
        "normalized-form-of", "modernized-form-of", "script-variant-of", "orthographic-variant-of"
    }
    edges = [
        {
            "relationId": item.relation_id,
            "fromId": item.from_id,
            "toId": item.to_id,
            "relationType": item.relation_type,
            "confidence": item.confidence,
            "sourceRef": item.source_ref,
        }
        for item in request.relations
        if item.relation_type in lineage_relations
    ]
    relation_counts = Counter(edge["relationType"] for edge in edges)
    return {
        "schema": LINEAGE_SCHEMA,
        "edgeCount": len(edges),
        "edges": edges,
        "relationDistribution": dict(sorted(relation_counts.items())),
        "historicalIdentityPreserved": True,
        "automaticModernizationApplied": False,
        "automaticVariantNormalizationApplied": False,
        "provenancePreserved": True,
    }


_EXECUTORS = {
    OPERATIONS[0]: _validate,
    OPERATIONS[1]: _variant_index,
    OPERATIONS[2]: _temporal_profile,
    OPERATIONS[3]: _script_orthography_profile,
    OPERATIONS[4]: _relationship_graph,
    OPERATIONS[5]: _lineage,
}


def execute(request: HistoricalLanguageIdentityRuntimeRequest) -> dict[str, Any]:
    if request.schema_ != REQUEST_SCHEMA:
        raise ValueError(f"schema must be {REQUEST_SCHEMA}")
    executor = _EXECUTORS.get(request.operation)
    if executor is None:
        raise ValueError(f"unsupported bounded operation: {request.operation}")

    return {
        "schema": RESULT_SCHEMA,
        "version": "3.50.0",
        "operation": request.operation,
        "result": executor(request),
        "policy": {
            "originalLanguageFirst": True,
            "historicalIdentityPreserved": True,
            "automaticLanguageDetectionEnabled": False,
            "automaticModernizationEnabled": False,
            "automaticVariantNormalizationEnabled": False,
            "automaticTranslationEnabled": False,
            "arbitraryCodeExecution": False,
        },
    }
