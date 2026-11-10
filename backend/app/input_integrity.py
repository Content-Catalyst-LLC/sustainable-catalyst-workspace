"""SC-NB-01 input integrity: bind polyglot job inputs to exact, immutable dataset bytes.

A job may name a dataset revision (``payload.datasetInput``) instead of sending rows inline. The
worker then loads the artifact snapshot that the dataset revision pinned when it was registered,
re-hashes the stored bytes, checks that the execution run declared that dataset revision, and only
then builds the runtime rows (optionally through a declared deterministic transform). Receipts record
the binding; inline rows are labelled ``inline-unverified`` and never count as verified lineage.
"""
from __future__ import annotations

import csv
import io
import json
import math
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ArtifactRevision
from .object_store import read_artifact_content
from .registry import get_dataset_revision, get_execution_run
from .utils import sha256_hex

BINDING_SCHEMA = "sc-workspace-dataset-input-binding/1.0"
VERIFIED = "artifact-bound-verified"
INLINE = "inline-unverified"
NONE = "none"
FORMATS = {"json-records", "csv"}
TRANSFORMS = {"least-squares-normal-equations"}


def _refuse(code: str, **detail) -> HTTPException:
    return HTTPException(status_code=409, detail={"code": code, **detail})


def _parse(raw: bytes, fmt: str) -> list[dict[str, Any]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _refuse("input-not-utf8") from exc
    if fmt == "json-records":
        try:
            doc = json.loads(text)
        except ValueError as exc:
            raise _refuse("input-not-json") from exc
        rows = doc.get("rows") if isinstance(doc, dict) else doc
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            raise _refuse("input-not-records", expected="JSON array of objects or {rows: [...]}")
        return rows
    out = []
    for rec in csv.DictReader(io.StringIO(text)):
        row = {}
        for k, v in rec.items():
            try:
                num = float(v)
                row[k] = num if math.isfinite(num) else v
            except (TypeError, ValueError):
                row[k] = None if v in ("", None) else v
        out.append(row)
    return out


def _normal_equations(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    """Q = X'X and c = -X'y (intercept first), so minimising 0.5 x'Qx + c'x gives the OLS solution."""
    outcome = str(spec.get("outcome") or "")
    predictors = [str(p) for p in (spec.get("predictors") or [])]
    if not outcome or not predictors:
        raise _refuse("transform-needs-outcome-and-predictors")
    X, y = [], []
    for r in rows:
        vals = [r.get(outcome)] + [r.get(p) for p in predictors]
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in vals):
            raise _refuse("transform-non-numeric-value", columns=[outcome, *predictors])
        y.append(float(vals[0]))
        X.append([1.0] + [float(v) for v in vals[1:]])
    k = len(X[0]) if X else 0
    Q = [[sum(row[i] * row[j] for row in X) for j in range(k)] for i in range(k)]
    c = [-sum(row[i] * yy for row, yy in zip(X, y)) for i in range(k)]
    return {"Q": Q, "c": c, "names": ["(Intercept)", *predictors]}


def resolve_dataset_input(db: Session, user_key: str, payload: dict[str, Any], run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Returns (runtime payload, binding). Raises 409 on any integrity or ownership failure."""
    spec = payload.get("datasetInput")
    if not isinstance(spec, dict):
        raise _refuse("dataset-input-malformed")
    if "rows" in payload:
        raise _refuse("dataset-input-and-inline-rows", detail="send either datasetInput or rows, not both")
    dataset_id = str(spec.get("datasetId") or "").strip()
    try:
        revision = int(spec.get("datasetRevision"))
    except (TypeError, ValueError) as exc:
        raise _refuse("dataset-input-revision-required") from exc
    fmt = str(spec.get("format") or "json-records")
    if fmt not in FORMATS:
        raise _refuse("dataset-input-format-unsupported", format=fmt)
    ds = get_dataset_revision(db, user_key, dataset_id, revision)
    if ds is None:
        raise _refuse("dataset-input-not-found", datasetId=dataset_id, datasetRevision=revision)
    if ds.source_kind != "artifact" or not ds.artifact_id or not ds.artifact_sha256:
        raise _refuse("dataset-revision-not-byte-pinned", datasetId=dataset_id, datasetRevision=revision,
                      detail="register the dataset revision against a stored artifact to pin its bytes")
    expected = str(spec.get("artifactSha256") or "").lower()
    if expected and expected != ds.artifact_sha256:
        raise _refuse("dataset-input-sha256-mismatch", expected=expected, pinned=ds.artifact_sha256)
    if run_id:
        run = get_execution_run(db, user_key, run_id)
        if run is None:
            raise _refuse("dataset-input-run-not-found", runId=run_id)
        declared = {(r.get("datasetId"), r.get("revision")) for r in (run.dataset_refs or [])}
        if (dataset_id, revision) not in declared:
            raise _refuse("dataset-input-not-declared-by-run", runId=run_id, datasetId=dataset_id, datasetRevision=revision)
    snapshot = db.scalars(select(ArtifactRevision).where(
        ArtifactRevision.user_key == user_key, ArtifactRevision.artifact_id == ds.artifact_id,
        ArtifactRevision.sha256 == ds.artifact_sha256).order_by(ArtifactRevision.revision.desc())).first()
    if snapshot is None:
        raise _refuse("dataset-input-snapshot-missing", artifactId=ds.artifact_id, sha256=ds.artifact_sha256)
    raw = read_artifact_content(snapshot)  # re-hashes the stored bytes; 503 on any mismatch
    rows = _parse(raw, fmt)
    runtime_payload = {k: v for k, v in payload.items() if k != "datasetInput"}
    transform = spec.get("transform")
    derived = None
    if transform is not None:
        if not isinstance(transform, dict) or transform.get("kind") not in TRANSFORMS:
            raise _refuse("dataset-input-transform-unsupported", supported=sorted(TRANSFORMS))
        derived = _normal_equations(rows, transform)
        runtime_payload.update({"Q": derived["Q"], "c": derived["c"]})
    else:
        runtime_payload["rows"] = rows
    binding = {
        "schema": BINDING_SCHEMA, "lineage": VERIFIED,
        "datasetId": dataset_id, "datasetRevision": revision, "datasetFingerprint": ds.fingerprint,
        "artifactId": ds.artifact_id, "artifactRevision": snapshot.revision, "artifactSha256": snapshot.sha256,
        "bytes": snapshot.bytes, "format": fmt, "rowCount": len(rows), "rowsSha256": sha256_hex(rows),
        "transform": transform, "derivedPayloadSha256": sha256_hex({"Q": derived["Q"], "c": derived["c"]}) if derived else None,
    }
    return runtime_payload, binding


def lineage_for_payload(payload: dict[str, Any]) -> str:
    """Anything a client sent without a binding (rows, matrices, parameters) is unverified input."""
    return INLINE if isinstance(payload, dict) and payload else NONE
