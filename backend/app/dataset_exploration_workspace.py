from __future__ import annotations
from collections import Counter
from typing import Any
from sqlalchemy.orm import Session
from .registry import list_datasets, get_dataset, list_dataset_revisions, dataset_metadata

SCHEMA = "sc-workspace-dataset-data-exploration/1.0"
DETAIL_SCHEMA = "sc-workspace-dataset-exploration-detail/1.0"

def profile() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "3.76.0",
        "release": "Dataset & Data Exploration Workspace",
        "backendAuthoritative": True,
        "datasetAuthority": "workspace-dataset-registry",
        "projectScopedFiltering": True,
        "textSearch": True,
        "datasetTypeFacets": True,
        "sourceKindFacets": True,
        "schemaInspection": True,
        "lineageInspection": True,
        "revisionHistory": True,
        "fingerprintInspection": True,
        "artifactBindingsVisible": True,
        "externalReferencesVisible": True,
        "visualizationHandoffReady": True,
        "canonicalMutationEndpoint": "/v1/datasets",
        "genericMutation": False,
        "automaticDataTransformation": False,
        "automaticSchemaInference": False,
        "automaticCleaning": False,
        "databaseMigrationRequired": False,
    }

def _matches(item: dict[str, Any], query: str) -> bool:
    needle = (query or "").strip().casefold()
    if not needle:
        return True
    parts = [
        item.get("datasetId"), item.get("projectId"), item.get("name"),
        item.get("description"), item.get("datasetType"), item.get("sourceKind"),
        item.get("artifactId"), item.get("externalUri"), item.get("tags"),
        item.get("metadata"),
    ]
    return needle in " ".join(str(x or "") for x in parts).casefold()

def browse(
    db: Session,
    user_key: str,
    project_id: str | None = None,
    q: str | None = None,
    dataset_type: str | None = None,
    source_kind: str | None = None,
    limit: int = 250,
) -> dict[str, Any]:
    items = list_datasets(db, user_key, project_id)
    if q:
        items = [x for x in items if _matches(x, q)]
    if dataset_type:
        items = [x for x in items if str(x.get("datasetType") or "") == dataset_type]
    if source_kind:
        items = [x for x in items if str(x.get("sourceKind") or "") == source_kind]
    type_counts = Counter(str(x.get("datasetType") or "unspecified") for x in items)
    source_counts = Counter(str(x.get("sourceKind") or "unspecified") for x in items)
    items = items[:max(1, min(limit, 500))]
    return {
        "schema": SCHEMA,
        "version": "3.76.0",
        "backendAuthoritative": True,
        "items": items,
        "count": len(items),
        "facets": {
            "datasetType": dict(sorted(type_counts.items())),
            "sourceKind": dict(sorted(source_counts.items())),
        },
        "filters": {
            "projectId": project_id or "",
            "q": q or "",
            "datasetType": dataset_type or "",
            "sourceKind": source_kind or "",
        },
    }

def detail(db: Session, user_key: str, dataset_id: str) -> dict[str, Any] | None:
    row = get_dataset(db, user_key, dataset_id)
    if row is None:
        return None
    item = dataset_metadata(row)
    revisions = list_dataset_revisions(db, user_key, dataset_id)
    return {
        "schema": DETAIL_SCHEMA,
        "version": "3.76.0",
        "item": item,
        "revisions": revisions,
        "revisionCount": len(revisions),
        "schemaDefinition": item.get("schemaDefinition") or {},
        "lineage": item.get("lineage") or {},
        "fingerprint": item.get("fingerprint"),
        "artifactBinding": item.get("artifactId") or "",
        "externalReference": item.get("externalUri") or "",
        "visualizationHandoff": {
            "sourceKind": "dataset",
            "sourceId": item.get("datasetId"),
            "projectId": item.get("projectId") or "",
            "sourceFingerprint": item.get("fingerprint"),
            "ready": True,
        },
        "automaticDataTransformation": False,
        "automaticSchemaInference": False,
    }
