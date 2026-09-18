from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    ArtifactHead,
    ComputeExecutionReceipt,
    CrossRuntimeVerificationReceipt,
    DatasetHead,
    DecisionOptimizationReceipt,
    ExecutionRun,
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
    VisualizationSpecHead,
    VisualizationSpecReceipt,
    VisualizationSpecRevision,
)
from .schemas import VisualizationSpecStoreRequest
from .utils import iso, sha256_hex

SPEC_SCHEMA = "sc-workspace-visualization-spec/1.0"
PROFILE_SCHEMA = "sc-workspace-visualization-spec-profile/1.0"
RENDERER_CONTRACT = "sc-workspace-renderer-contract/1.0"

VIEW_TYPES = (
    "table",
    "line",
    "area",
    "bar",
    "scatter",
    "histogram",
    "box",
    "heatmap",
    "distribution",
    "uncertainty-band",
    "timeline",
    "network",
    "metric",
)
SCENE_LAYOUTS = ("single", "grid", "dashboard")
SOURCE_KINDS = ("artifact", "dataset", "execution-run", "receipt", "inline")
LINK_MODES = ("filter", "highlight", "select")
INTERACTION_TYPES = ("select", "filter", "highlight", "brush", "zoom")
PROHIBITED_KEYS = {
    "javascript", "script", "eval", "function", "html", "rawhtml", "code",
    "renderer", "rendererconfig", "rendereroptions", "plotly", "echarts", "highcharts", "css",
}
MAX_VIEWS = 32
MAX_SOURCES = 64
MAX_LINKS = 128
MAX_INLINE_ROWS = 5000

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
        "schema": PROFILE_SCHEMA,
        "mode": "declarative-visualization-specification-api",
        "backendAuthoritative": True,
        "rendererNeutral": True,
        "rendererContract": RENDERER_CONTRACT,
        "specSchema": SPEC_SCHEMA,
        "viewTypes": list(VIEW_TYPES),
        "sceneLayouts": list(SCENE_LAYOUTS),
        "sourceKinds": list(SOURCE_KINDS),
        "linkModes": list(LINK_MODES),
        "interactionTypes": list(INTERACTION_TYPES),
        "linkedViews": True,
        "sourceProvenancePinning": True,
        "revisionHistory": True,
        "deterministicFingerprint": True,
        "browserDefinesAnalyticalMeaning": False,
        "arbitraryCodeExecution": False,
        "limits": {
            "maxViews": MAX_VIEWS,
            "maxSources": MAX_SOURCES,
            "maxLinks": MAX_LINKS,
            "maxInlineRows": MAX_INLINE_ROWS,
        },
    }


def _assert_no_prohibited_keys(value: Any, path: str = "spec") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower().replace("-", "").replace("_", "") in PROHIBITED_KEYS:
                raise HTTPException(status_code=400, detail={"code": "renderer-specific-or-executable-field", "path": f"{path}.{key}"})
            _assert_no_prohibited_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _assert_no_prohibited_keys(child, f"{path}[{i}]")


def _receipt_pin(db: Session, user_key: str, receipt_id: str) -> dict[str, Any]:
    for model in RECEIPT_MODELS:
        if not hasattr(model, "receipt_id"):
            continue
        row = db.scalar(select(model).where(model.user_key == user_key, model.receipt_id == receipt_id))
        if row is None:
            continue
        doc: dict[str, Any] = {"kind": "receipt", "ref": receipt_id, "table": model.__tablename__}
        for attr in sa_inspect(row).mapper.column_attrs:
            key = attr.key
            if key in {"user_key", "details_json", "result_json", "metrics_json", "summary_json", "sensitivity_json"}:
                continue
            value = getattr(row, key)
            if isinstance(value, datetime):
                value = iso(value)
            if isinstance(value, (str, int, float, bool)) or value is None:
                doc[key] = value
        doc["sourceFingerprint"] = sha256_hex(doc)
        return doc
    raise HTTPException(status_code=400, detail={"code": "visualization-source-not-found", "sourceKind": "receipt", "sourceId": receipt_id})


def _pin_source(db: Session, user_key: str, source: dict[str, Any]) -> dict[str, Any]:
    source_id = str(source.get("id") or "").strip()
    kind = str(source.get("kind") or "").strip()
    ref = str(source.get("ref") or "").strip()
    if not source_id:
        raise HTTPException(status_code=400, detail={"code": "visualization-source-id-required"})
    if kind not in SOURCE_KINDS:
        raise HTTPException(status_code=400, detail={"code": "unsupported-visualization-source-kind", "kind": kind})

    if kind == "inline":
        rows = source.get("rows", [])
        if not isinstance(rows, list) or len(rows) > MAX_INLINE_ROWS:
            raise HTTPException(status_code=400, detail={"code": "inline-source-row-limit", "maxRows": MAX_INLINE_ROWS})
        if any(not isinstance(row, dict) for row in rows):
            raise HTTPException(status_code=400, detail={"code": "inline-source-rows-must-be-objects"})
        pin = {"id": source_id, "kind": kind, "rows": rows, "rowCount": len(rows)}
        pin["sourceFingerprint"] = sha256_hex(pin)
        return pin

    if not ref:
        raise HTTPException(status_code=400, detail={"code": "visualization-source-ref-required", "sourceId": source_id})

    if kind == "artifact":
        row = db.get(ArtifactHead, {"user_key": user_key, "artifact_id": ref})
        if row is None:
            raise HTTPException(status_code=400, detail={"code": "visualization-source-not-found", "sourceKind": kind, "sourceId": ref})
        return {
            "id": source_id, "kind": kind, "ref": ref, "projectId": row.project_id,
            "revision": row.revision, "sha256": row.sha256, "bytes": row.bytes,
            "mediaType": row.media_type, "sourceFingerprint": row.sha256,
        }
    if kind == "dataset":
        row = db.get(DatasetHead, {"user_key": user_key, "dataset_id": ref})
        if row is None:
            raise HTTPException(status_code=400, detail={"code": "visualization-source-not-found", "sourceKind": kind, "sourceId": ref})
        return {
            "id": source_id, "kind": kind, "ref": ref, "projectId": row.project_id,
            "revision": row.revision, "fingerprint": row.fingerprint,
            "sourceFingerprint": row.fingerprint,
        }
    if kind == "execution-run":
        row = db.get(ExecutionRun, {"user_key": user_key, "run_id": ref})
        if row is None:
            raise HTTPException(status_code=400, detail={"code": "visualization-source-not-found", "sourceKind": kind, "sourceId": ref})
        source_fp = row.reproducibility_fingerprint or row.input_fingerprint or row.run_id
        return {
            "id": source_id, "kind": kind, "ref": ref, "projectId": row.project_id,
            "status": row.status, "reproducibilityFingerprint": row.reproducibility_fingerprint,
            "sourceFingerprint": sha256_hex({"runId": row.run_id, "fingerprint": source_fp}),
        }
    pin = _receipt_pin(db, user_key, ref)
    return {"id": source_id, **pin}


def compile_spec(db: Session, user_key: str, raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail={"code": "visualization-spec-must-be-object"})
    _assert_no_prohibited_keys(raw)

    incoming_schema = raw.get("schema")
    if incoming_schema not in (None, SPEC_SCHEMA):
        raise HTTPException(status_code=400, detail={"code": "visualization-schema-mismatch", "expected": SPEC_SCHEMA})

    scene = raw.get("scene") or {}
    if not isinstance(scene, dict):
        raise HTTPException(status_code=400, detail={"code": "visualization-scene-must-be-object"})
    layout = str(scene.get("layout") or "single")
    if layout not in SCENE_LAYOUTS:
        raise HTTPException(status_code=400, detail={"code": "unsupported-scene-layout", "layout": layout})

    views = scene.get("views") or []
    if not isinstance(views, list) or not 1 <= len(views) <= MAX_VIEWS:
        raise HTTPException(status_code=400, detail={"code": "visualization-view-count", "min": 1, "max": MAX_VIEWS})
    view_ids: set[str] = set()
    normalized_views: list[dict[str, Any]] = []
    for view in views:
        if not isinstance(view, dict):
            raise HTTPException(status_code=400, detail={"code": "visualization-view-must-be-object"})
        view_id = str(view.get("id") or "").strip()
        view_type = str(view.get("type") or "").strip()
        if not view_id or view_id in view_ids:
            raise HTTPException(status_code=400, detail={"code": "visualization-view-id-invalid", "viewId": view_id})
        if view_type not in VIEW_TYPES:
            raise HTTPException(status_code=400, detail={"code": "unsupported-visualization-view-type", "viewType": view_type})
        view_ids.add(view_id)
        encoding = view.get("encoding") or {}
        if not isinstance(encoding, dict) or len(encoding) > 16:
            raise HTTPException(status_code=400, detail={"code": "visualization-encoding-invalid", "viewId": view_id})
        interactions = view.get("interactions") or []
        if not isinstance(interactions, list) or len(interactions) > 16:
            raise HTTPException(status_code=400, detail={"code": "visualization-interactions-invalid", "viewId": view_id})
        for interaction in interactions:
            if not isinstance(interaction, dict) or interaction.get("type") not in INTERACTION_TYPES:
                raise HTTPException(status_code=400, detail={"code": "unsupported-visualization-interaction", "viewId": view_id})
        normalized_views.append({
            "id": view_id,
            "type": view_type,
            "title": str(view.get("title") or ""),
            "source": str(view.get("source") or ""),
            "encoding": encoding,
            "transform": view.get("transform") or [],
            "interactions": interactions,
            "options": view.get("options") or {},
        })

    raw_sources = raw.get("sources") or []
    if not isinstance(raw_sources, list) or len(raw_sources) > MAX_SOURCES:
        raise HTTPException(status_code=400, detail={"code": "visualization-source-count", "max": MAX_SOURCES})
    sources = [_pin_source(db, user_key, source) for source in raw_sources]
    source_ids = {s["id"] for s in sources}
    if len(source_ids) != len(sources):
        raise HTTPException(status_code=400, detail={"code": "duplicate-visualization-source-id"})
    for view in normalized_views:
        if view["source"] and view["source"] not in source_ids:
            raise HTTPException(status_code=400, detail={"code": "visualization-view-source-not-found", "viewId": view["id"], "sourceId": view["source"]})

    links = raw.get("links") or []
    if not isinstance(links, list) or len(links) > MAX_LINKS:
        raise HTTPException(status_code=400, detail={"code": "visualization-link-count", "max": MAX_LINKS})
    normalized_links: list[dict[str, Any]] = []
    for link in links:
        if not isinstance(link, dict):
            raise HTTPException(status_code=400, detail={"code": "visualization-link-must-be-object"})
        source_view = str(link.get("sourceViewId") or "")
        target_view = str(link.get("targetViewId") or "")
        mode = str(link.get("mode") or "filter")
        if source_view not in view_ids or target_view not in view_ids:
            raise HTTPException(status_code=400, detail={"code": "visualization-link-view-not-found"})
        if mode not in LINK_MODES:
            raise HTTPException(status_code=400, detail={"code": "unsupported-visualization-link-mode", "mode": mode})
        normalized_links.append({"sourceViewId": source_view, "targetViewId": target_view, "mode": mode, "field": str(link.get("field") or "")})

    spec = {
        "schema": SPEC_SCHEMA,
        "rendererContract": {"schema": RENDERER_CONTRACT, "rendererNeutral": True, "analyticalMeaningAuthoritative": "backend"},
        "title": str(raw.get("title") or ""),
        "scene": {"layout": layout, "views": normalized_views},
        "sources": sources,
        "links": normalized_links,
        "annotations": raw.get("annotations") or [],
        "policy": {
            "backendAuthoritative": True,
            "browserDefinesAnalyticalMeaning": False,
            "rendererNeutral": True,
            "arbitraryCodeExecution": False,
        },
    }
    spec["specFingerprint"] = sha256_hex(spec)
    return spec


def _metadata(row: VisualizationSpecHead) -> dict[str, Any]:
    return {
        "visualizationId": row.visualization_id,
        "projectId": row.project_id,
        "title": row.title,
        "revision": row.revision,
        "specFingerprint": row.spec_fingerprint,
        "sceneKind": row.scene_kind,
        "viewCount": row.view_count,
        "sourceCount": row.source_count,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _receipt_metadata(row: VisualizationSpecReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "visualizationId": row.visualization_id,
        "action": row.action,
        "status": row.status,
        "revision": row.revision,
        "specFingerprint": row.spec_fingerprint,
        "details": row.details_json,
        "createdAt": iso(row.created_at),
    }


def store_spec(db: Session, user_key: str, request: VisualizationSpecStoreRequest) -> tuple[VisualizationSpecHead, bool]:
    settings = get_settings()
    visualization_id = request.visualizationId or f"viz-{uuid4().hex[:24]}"
    current = db.get(VisualizationSpecHead, {"user_key": user_key, "visualization_id": visualization_id})
    if current is None:
        count = db.scalar(select(func.count()).select_from(VisualizationSpecHead).where(VisualizationSpecHead.user_key == user_key)) or 0
        if count >= settings.max_visualization_specs_per_account:
            raise HTTPException(status_code=409, detail="Workspace visualization specification limit reached.")
        if request.expectedRevision not in (None, 0):
            raise HTTPException(status_code=409, detail={"code": "visualization-revision-conflict", "currentRevision": 0})
        revision = 1
    else:
        if request.expectedRevision is not None and request.expectedRevision != current.revision:
            raise HTTPException(status_code=409, detail={"code": "visualization-revision-conflict", "currentRevision": current.revision})
        revision = current.revision + 1

    compiled = compile_spec(db, user_key, request.spec)
    fingerprint = compiled["specFingerprint"]
    if current is not None and current.spec_fingerprint == fingerprint:
        return current, True

    title = request.title or compiled.get("title") or (current.title if current else "Visualization")
    values = {
        "project_id": request.projectId,
        "title": title,
        "revision": revision,
        "spec_fingerprint": fingerprint,
        "scene_kind": compiled["scene"]["layout"],
        "view_count": len(compiled["scene"]["views"]),
        "source_count": len(compiled["sources"]),
        "spec_json": compiled,
    }
    if current is None:
        current = VisualizationSpecHead(user_key=user_key, visualization_id=visualization_id, **values)
        db.add(current)
    else:
        for key, value in values.items():
            setattr(current, key, value)

    db.add(VisualizationSpecRevision(
        user_key=user_key,
        visualization_id=visualization_id,
        revision=revision,
        project_id=request.projectId,
        title=title,
        spec_fingerprint=fingerprint,
        scene_kind=compiled["scene"]["layout"],
        view_count=len(compiled["scene"]["views"]),
        source_count=len(compiled["sources"]),
        operation_id=request.operationId or "",
        spec_json=compiled,
    ))
    db.add(VisualizationSpecReceipt(
        user_key=user_key,
        receipt_id=f"vizr-{uuid4().hex}",
        visualization_id=visualization_id,
        action="create" if revision == 1 else "update",
        status="applied",
        revision=revision,
        spec_fingerprint=fingerprint,
        details_json={"projectId": request.projectId, "viewCount": len(compiled["scene"]["views"]), "sourceCount": len(compiled["sources"])},
    ))
    db.commit()
    db.refresh(current)
    return current, False


def get_spec(db: Session, user_key: str, visualization_id: str) -> VisualizationSpecHead | None:
    return db.get(VisualizationSpecHead, {"user_key": user_key, "visualization_id": visualization_id})


def list_specs(db: Session, user_key: str, project_id: str | None, limit: int) -> list[dict[str, Any]]:
    q = select(VisualizationSpecHead).where(VisualizationSpecHead.user_key == user_key)
    if project_id:
        q = q.where(VisualizationSpecHead.project_id == project_id)
    rows = db.scalars(q.order_by(VisualizationSpecHead.updated_at.desc()).limit(limit)).all()
    return [_metadata(row) for row in rows]


def list_revisions(db: Session, user_key: str, visualization_id: str, limit: int) -> list[dict[str, Any]]:
    rows = db.scalars(select(VisualizationSpecRevision).where(
        VisualizationSpecRevision.user_key == user_key,
        VisualizationSpecRevision.visualization_id == visualization_id,
    ).order_by(VisualizationSpecRevision.revision.desc()).limit(limit)).all()
    return [{
        "visualizationId": row.visualization_id,
        "revision": row.revision,
        "projectId": row.project_id,
        "title": row.title,
        "specFingerprint": row.spec_fingerprint,
        "sceneKind": row.scene_kind,
        "viewCount": row.view_count,
        "sourceCount": row.source_count,
        "operationId": row.operation_id,
        "createdAt": iso(row.created_at),
    } for row in rows]


def list_receipts(db: Session, user_key: str, visualization_id: str | None, limit: int) -> list[dict[str, Any]]:
    q = select(VisualizationSpecReceipt).where(VisualizationSpecReceipt.user_key == user_key)
    if visualization_id:
        q = q.where(VisualizationSpecReceipt.visualization_id == visualization_id)
    rows = db.scalars(q.order_by(VisualizationSpecReceipt.created_at.desc()).limit(limit)).all()
    return [_receipt_metadata(row) for row in rows]


def delete_spec(db: Session, user_key: str, visualization_id: str) -> bool:
    row = get_spec(db, user_key, visualization_id)
    if row is None:
        return False
    db.add(VisualizationSpecReceipt(
        user_key=user_key,
        receipt_id=f"vizr-{uuid4().hex}",
        visualization_id=visualization_id,
        action="delete",
        status="applied",
        revision=row.revision,
        spec_fingerprint=row.spec_fingerprint,
        details_json={"projectId": row.project_id},
    ))
    db.delete(row)
    db.commit()
    return True


metadata = _metadata
