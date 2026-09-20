from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import inspect as sa_inspect, select
from sqlalchemy.orm import Session

from .environments import environment_metadata, get_environment, list_environment_revisions, list_environments
from .models import (
    ArtifactRevision,
    ComputeExecutionReceipt,
    CrossRuntimeVerificationReceipt,
    DecisionOptimizationReceipt,
    ForecastEvaluationReceipt,
    ForecastReceipt,
    InterchangeReceipt,
    ModelEvaluationReceipt,
    NumericalSimulationReceipt,
    OptimizationReceipt,
    PolyglotExecutionReceipt,
    PredictiveModelReceipt,
    ProbabilisticInferenceReceipt,
    ReliabilityAnalysisReceipt,
    StatisticalModelReceipt,
    UncertaintyAnalysisReceipt,
)
from .object_store import artifact_metadata, get_artifact, list_artifacts
from .registry import (
    dataset_metadata,
    get_dataset,
    get_execution_run,
    get_model,
    get_parameter_set,
    list_dataset_revisions,
    list_datasets,
    list_execution_runs,
    list_model_revisions,
    list_models,
    list_parameter_set_revisions,
    list_parameter_sets,
    list_run_events,
    list_run_outputs,
    model_metadata,
    parameter_set_metadata,
    run_metadata,
)
from .runtime_adapters import adapter_metadata, get_adapter, list_adapter_revisions, list_adapters
from .study_packages import get_package, list_packages, package_metadata
from .utils import iso, sha256_hex
from .visualization_specs import get_spec, list_revisions as list_visualization_revisions, list_specs, metadata as visualization_metadata

SCIENTIFIC_OBJECT_SCHEMA = "sc-workspace-scientific-object/1.0"
SCIENTIFIC_OBJECT_PROFILE_SCHEMA = "sc-workspace-scientific-object-api/1.0"
SCIENTIFIC_RELATION_SCHEMA = "sc-workspace-scientific-object-relations/1.0"
SCIENTIFIC_HISTORY_SCHEMA = "sc-workspace-scientific-object-history/1.0"

OBJECT_KINDS: tuple[str, ...] = (
    "artifact",
    "dataset",
    "model",
    "parameter-set",
    "execution-run",
    "execution-environment",
    "runtime-adapter",
    "study-package",
    "visualization-spec",
    "scientific-receipt",
)

REVISIONED_KINDS = {
    "artifact",
    "dataset",
    "model",
    "parameter-set",
    "execution-environment",
    "runtime-adapter",
    "visualization-spec",
}

RECEIPT_MODELS = (
    ComputeExecutionReceipt,
    PolyglotExecutionReceipt,
    StatisticalModelReceipt,
    NumericalSimulationReceipt,
    PredictiveModelReceipt,
    ModelEvaluationReceipt,
    ForecastReceipt,
    ForecastEvaluationReceipt,
    ProbabilisticInferenceReceipt,
    UncertaintyAnalysisReceipt,
    OptimizationReceipt,
    DecisionOptimizationReceipt,
    ReliabilityAnalysisReceipt,
    InterchangeReceipt,
    CrossRuntimeVerificationReceipt,
)


def profile() -> dict[str, Any]:
    return {
        "schema": SCIENTIFIC_OBJECT_PROFILE_SCHEMA,
        "mode": "backend-authoritative-unified-scientific-object-api",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "canonicalStore": "postgresql",
        "objectSchema": SCIENTIFIC_OBJECT_SCHEMA,
        "supportedKinds": list(OBJECT_KINDS),
        "revisionedKinds": sorted(REVISIONED_KINDS),
        "immutableKinds": ["study-package", "scientific-receipt"],
        "eventHistoryKinds": ["execution-run"],
        "relations": True,
        "projectScoping": True,
        "textFiltering": True,
        "deterministicObjectFingerprint": True,
        "typedDiscovery": True,
        "localFirstCanonicalCachePersistent": False,
        "mutations": "existing-bounded-domain-apis-only",
        "genericArbitraryMutationEndpoint": False,
        "arbitraryCodeExecution": False,
    }


def _isoish(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return iso(value)
    return str(value)


def _scalar_receipt(row: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for attr in sa_inspect(row).mapper.column_attrs:
        key = attr.key
        if key == "user_key" or key.endswith("_json"):
            continue
        value = getattr(row, key)
        if isinstance(value, datetime):
            value = iso(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            data[key] = value
    return data


def _receipt_metadata(row: Any) -> dict[str, Any]:
    raw = _scalar_receipt(row)
    receipt_id = str(raw.get("receipt_id") or "")
    project_id = str(raw.get("project_id") or "")
    created = raw.get("created_at")
    fingerprint = sha256_hex({"table": row.__tablename__, "receipt": raw})
    return {
        "receiptId": receipt_id,
        "receiptType": row.__tablename__,
        "projectId": project_id,
        "fingerprint": fingerprint,
        "summary": raw,
        "createdAt": created,
        "updatedAt": created,
    }


def _list_receipts(db: Session, user_key: str, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    per_model = max(1, min(limit, 25))
    for model in RECEIPT_MODELS:
        if not hasattr(model, "receipt_id"):
            continue
        order = getattr(model, "created_at", None)
        stmt = select(model).where(model.user_key == user_key)
        if order is not None:
            stmt = stmt.order_by(order.desc())
        for row in db.scalars(stmt.limit(per_model)).all():
            rows.append(_receipt_metadata(row))
    rows.sort(key=lambda item: str(item.get("updatedAt") or ""), reverse=True)
    return rows[:limit]


def _get_receipt(db: Session, user_key: str, receipt_id: str) -> dict[str, Any] | None:
    for model in RECEIPT_MODELS:
        if not hasattr(model, "receipt_id"):
            continue
        row = db.scalar(select(model).where(model.user_key == user_key, model.receipt_id == receipt_id).limit(1))
        if row is not None:
            return _receipt_metadata(row)
    return None


def _source_metadata(kind: str, db: Session, user_key: str, object_id: str) -> dict[str, Any] | None:
    if kind == "artifact":
        row = get_artifact(db, user_key, object_id)
        return artifact_metadata(row) if row else None
    if kind == "dataset":
        row = get_dataset(db, user_key, object_id)
        return dataset_metadata(row) if row else None
    if kind == "model":
        row = get_model(db, user_key, object_id)
        return model_metadata(row) if row else None
    if kind == "parameter-set":
        row = get_parameter_set(db, user_key, object_id)
        return parameter_set_metadata(row) if row else None
    if kind == "execution-run":
        row = get_execution_run(db, user_key, object_id)
        return run_metadata(row) if row else None
    if kind == "execution-environment":
        row = get_environment(db, user_key, object_id)
        return environment_metadata(row) if row else None
    if kind == "runtime-adapter":
        row = get_adapter(db, user_key, object_id)
        return adapter_metadata(row) if row else None
    if kind == "study-package":
        row = get_package(db, user_key, object_id)
        return package_metadata(row) if row else None
    if kind == "visualization-spec":
        row = get_spec(db, user_key, object_id)
        return visualization_metadata(row) if row else None
    if kind == "scientific-receipt":
        return _get_receipt(db, user_key, object_id)
    raise HTTPException(status_code=400, detail={"code": "unsupported-scientific-object-kind", "kind": kind})


def _identity_fields(kind: str, meta: dict[str, Any]) -> tuple[str, str, str, int | None, str, str | None, str | None]:
    ids = {
        "artifact": "artifactId",
        "dataset": "datasetId",
        "model": "modelId",
        "parameter-set": "parameterSetId",
        "execution-run": "runId",
        "execution-environment": "environmentId",
        "runtime-adapter": "adapterId",
        "study-package": "packageId",
        "visualization-spec": "visualizationId",
        "scientific-receipt": "receiptId",
    }
    names = {
        "artifact": "filename",
        "dataset": "name",
        "model": "name",
        "parameter-set": "name",
        "execution-run": "name",
        "execution-environment": "name",
        "runtime-adapter": "name",
        "study-package": "title",
        "visualization-spec": "title",
        "scientific-receipt": "receiptType",
    }
    fingerprints = {
        "artifact": "sha256",
        "dataset": "fingerprint",
        "model": "fingerprint",
        "parameter-set": "fingerprint",
        "execution-run": "reproducibilityFingerprint",
        "execution-environment": "fingerprint",
        "runtime-adapter": "fingerprint",
        "study-package": "manifestFingerprint",
        "visualization-spec": "specFingerprint",
        "scientific-receipt": "fingerprint",
    }
    object_id = str(meta.get(ids[kind]) or "")
    project_id = str(meta.get("projectId") or "")
    name = str(meta.get(names[kind]) or object_id)
    revision = int(meta.get("revision")) if meta.get("revision") is not None else None
    fingerprint = str(meta.get(fingerprints[kind]) or sha256_hex({"kind": kind, "id": object_id, "metadata": meta}))
    created = _isoish(meta.get("createdAt"))
    updated = _isoish(meta.get("updatedAt") or meta.get("finishedAt") or created)
    return object_id, project_id, name, revision, fingerprint, created, updated


def normalize(kind: str, meta: dict[str, Any]) -> dict[str, Any]:
    object_id, project_id, name, revision, fingerprint, created, updated = _identity_fields(kind, meta)
    status = ""
    if kind == "execution-run":
        status = str(meta.get("status") or "")
    elif kind == "study-package":
        status = "verified" if meta.get("closureVerified") else "packaged"
    elif kind == "scientific-receipt":
        status = str((meta.get("summary") or {}).get("status") or "recorded")
    summary_keys = {
        "artifact": ("filename", "mediaType", "bytes", "sha256"),
        "dataset": ("name", "datasetType", "sourceKind", "artifactId", "tags"),
        "model": ("name", "modelKind", "framework", "algorithm", "versionLabel"),
        "parameter-set": ("name", "modelId"),
        "execution-run": ("name", "status", "progress", "operation", "jobId"),
        "execution-environment": ("name", "description", "runtime"),
        "runtime-adapter": ("name", "runtimeFamily", "runtimeVersion", "adapterType", "trustLevel"),
        "study-package": ("title", "description", "componentCount", "embeddedArtifactCount", "closureVerified"),
        "visualization-spec": ("title", "sceneKind", "viewCount", "sourceCount"),
        "scientific-receipt": ("receiptType", "summary"),
    }
    summary = {key: meta.get(key) for key in summary_keys[kind] if key in meta}
    item = {
        "schema": SCIENTIFIC_OBJECT_SCHEMA,
        "kind": kind,
        "objectId": object_id,
        "projectId": project_id,
        "name": name,
        "revision": revision,
        "fingerprint": fingerprint,
        "status": status,
        "createdAt": created,
        "updatedAt": updated,
        "summary": summary,
        "capabilities": {
            "revisionHistory": kind in REVISIONED_KINDS,
            "eventHistory": kind == "execution-run",
            "relations": True,
            "genericMutation": False,
        },
    }
    item["objectFingerprint"] = sha256_hex({k: item[k] for k in ("kind", "objectId", "projectId", "revision", "fingerprint")})
    return item


def _list_kind(db: Session, user_key: str, kind: str, project_id: str | None, limit: int) -> list[dict[str, Any]]:
    if kind == "artifact":
        rows = list_artifacts(db, user_key)
    elif kind == "dataset":
        rows = list_datasets(db, user_key, project_id)
    elif kind == "model":
        rows = list_models(db, user_key, project_id)
    elif kind == "parameter-set":
        rows = list_parameter_sets(db, user_key, None)
    elif kind == "execution-run":
        rows = list_execution_runs(db, user_key, None, project_id, limit)
    elif kind == "execution-environment":
        rows = list_environments(db, user_key, project_id)
    elif kind == "runtime-adapter":
        rows = list_adapters(db, user_key, project_id)
    elif kind == "study-package":
        rows = list_packages(db, user_key, project_id, limit)
    elif kind == "visualization-spec":
        rows = list_specs(db, user_key, project_id, limit)
    elif kind == "scientific-receipt":
        rows = _list_receipts(db, user_key, limit)
    else:
        raise HTTPException(status_code=400, detail={"code": "unsupported-scientific-object-kind", "kind": kind})
    if project_id and kind in {"artifact", "parameter-set", "scientific-receipt"}:
        rows = [row for row in rows if str(row.get("projectId") or "") == project_id]
    return [normalize(kind, row) for row in rows[:limit]]


def list_objects(db: Session, user_key: str, kind: str | None = None, project_id: str | None = None, q: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    if kind is not None and kind not in OBJECT_KINDS:
        raise HTTPException(status_code=400, detail={"code": "unsupported-scientific-object-kind", "kind": kind})
    kinds = (kind,) if kind else OBJECT_KINDS
    items: list[dict[str, Any]] = []
    per_kind = limit if kind else max(10, min(limit, 50))
    for item_kind in kinds:
        items.extend(_list_kind(db, user_key, item_kind, project_id, per_kind))
    needle = (q or "").strip().casefold()
    if needle:
        items = [item for item in items if needle in (item["objectId"] + " " + item["name"] + " " + str(item.get("summary") or "")).casefold()]
    items.sort(key=lambda item: str(item.get("updatedAt") or item.get("createdAt") or ""), reverse=True)
    return items[:limit]


def get_object(db: Session, user_key: str, kind: str, object_id: str) -> dict[str, Any] | None:
    meta = _source_metadata(kind, db, user_key, object_id)
    return normalize(kind, meta) if meta is not None else None


def history(db: Session, user_key: str, kind: str, object_id: str, limit: int = 100) -> dict[str, Any]:
    if kind not in OBJECT_KINDS:
        raise HTTPException(status_code=400, detail={"code": "unsupported-scientific-object-kind", "kind": kind})
    if kind == "artifact":
        rows = db.scalars(select(ArtifactRevision).where(ArtifactRevision.user_key == user_key, ArtifactRevision.artifact_id == object_id).order_by(ArtifactRevision.revision.desc()).limit(limit)).all()
        items = [{"revision": row.revision, "projectId": row.project_id, "filename": row.filename, "mediaType": row.media_type, "bytes": row.bytes, "sha256": row.sha256, "metadata": row.metadata_json, "createdAt": iso(row.created_at)} for row in rows]
        mode = "revisions"
    elif kind == "dataset":
        items = list_dataset_revisions(db, user_key, object_id)[:limit]; mode = "revisions"
    elif kind == "model":
        items = list_model_revisions(db, user_key, object_id)[:limit]; mode = "revisions"
    elif kind == "parameter-set":
        items = list_parameter_set_revisions(db, user_key, object_id)[:limit]; mode = "revisions"
    elif kind == "execution-environment":
        items = list_environment_revisions(db, user_key, object_id)[:limit]; mode = "revisions"
    elif kind == "runtime-adapter":
        items = list_adapter_revisions(db, user_key, object_id)[:limit]; mode = "revisions"
    elif kind == "visualization-spec":
        items = list_visualization_revisions(db, user_key, object_id, limit); mode = "revisions"
    elif kind == "execution-run":
        items = list_run_events(db, user_key, object_id)[:limit]; mode = "events"
    else:
        items = []; mode = "immutable"
    return {"schema": SCIENTIFIC_HISTORY_SCHEMA, "kind": kind, "objectId": object_id, "historyMode": mode, "items": items}


def _relation(kind: str, object_id: str, relation: str, target_kind: str, target_id: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    item = {"sourceKind": kind, "sourceId": object_id, "relation": relation, "targetKind": target_kind, "targetId": target_id}
    if details:
        item["details"] = details
    return item


def relations(db: Session, user_key: str, kind: str, object_id: str) -> dict[str, Any]:
    meta = _source_metadata(kind, db, user_key, object_id)
    if meta is None:
        raise HTTPException(status_code=404, detail={"code": "scientific-object-not-found", "kind": kind, "objectId": object_id})
    out: list[dict[str, Any]] = []
    project_id = str(meta.get("projectId") or "")
    if project_id:
        out.append(_relation(kind, object_id, "belongs-to-project", "project", project_id))
    if kind == "dataset" and meta.get("artifactId"):
        out.append(_relation(kind, object_id, "materialized-by", "artifact", str(meta["artifactId"])))
    elif kind == "model" and meta.get("sourceArtifactId"):
        out.append(_relation(kind, object_id, "source-artifact", "artifact", str(meta["sourceArtifactId"])))
    elif kind == "parameter-set" and meta.get("modelId"):
        out.append(_relation(kind, object_id, "parameters-for", "model", str(meta["modelId"])))
    elif kind == "execution-run":
        for ref in meta.get("datasetRefs") or []:
            if isinstance(ref, dict) and ref.get("datasetId"):
                out.append(_relation(kind, object_id, "uses-dataset", "dataset", str(ref["datasetId"]), {"revision": ref.get("revision")}))
        ref = meta.get("modelRef") or {}
        if isinstance(ref, dict) and ref.get("modelId"):
            out.append(_relation(kind, object_id, "uses-model", "model", str(ref["modelId"]), {"revision": ref.get("revision")}))
        ref = meta.get("parameterSetRef") or {}
        if isinstance(ref, dict) and ref.get("parameterSetId"):
            out.append(_relation(kind, object_id, "uses-parameter-set", "parameter-set", str(ref["parameterSetId"]), {"revision": ref.get("revision")}))
        ref = meta.get("environmentRef") or {}
        if isinstance(ref, dict) and ref.get("environmentId"):
            out.append(_relation(kind, object_id, "uses-environment", "execution-environment", str(ref["environmentId"]), {"revision": ref.get("revision")}))
        ref = meta.get("runtimeAdapterRef") or {}
        if isinstance(ref, dict) and ref.get("adapterId"):
            out.append(_relation(kind, object_id, "uses-runtime-adapter", "runtime-adapter", str(ref["adapterId"]), {"revision": ref.get("revision")}))
        for output in list_run_outputs(db, user_key, object_id):
            if output.get("artifactId"):
                out.append(_relation(kind, object_id, "produces-artifact", "artifact", str(output["artifactId"]), {"role": output.get("role"), "outputId": output.get("outputId")}))
    elif kind == "execution-environment":
        for ref in meta.get("lockArtifacts") or []:
            if isinstance(ref, dict) and ref.get("artifactId"):
                out.append(_relation(kind, object_id, "locks-artifact", "artifact", str(ref["artifactId"]), {"revision": ref.get("revision")}))
    elif kind == "study-package" and meta.get("bundleArtifactId"):
        out.append(_relation(kind, object_id, "bundle-artifact", "artifact", str(meta["bundleArtifactId"])))
    elif kind == "visualization-spec":
        row = get_spec(db, user_key, object_id)
        if row is not None:
            for source in row.spec_json.get("sources", []) if isinstance(row.spec_json, dict) else []:
                if not isinstance(source, dict):
                    continue
                skind = str(source.get("kind") or "")
                ref = str(source.get("ref") or "")
                if ref and skind in {"artifact", "dataset", "execution-run", "receipt"}:
                    target = "scientific-receipt" if skind == "receipt" else skind
                    out.append(_relation(kind, object_id, "visualizes", target, ref, {"sourceId": source.get("id")}))
    return {"schema": SCIENTIFIC_RELATION_SCHEMA, "kind": kind, "objectId": object_id, "items": out, "relationCount": len(out)}
