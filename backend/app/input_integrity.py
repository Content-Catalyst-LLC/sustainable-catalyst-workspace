"""SC-NB-01 input integrity: bind polyglot job inputs to exact, immutable dataset bytes.

A job may name a dataset revision (``payload.datasetInput``) instead of sending rows inline. The
worker then loads the artifact snapshot that the dataset revision pinned when it was registered,
re-hashes the stored bytes, checks that the execution run declared that dataset revision, and only
then builds the runtime rows (optionally through a declared deterministic transform). Receipts record
the binding; inline rows are labelled ``inline-unverified`` and never count as verified lineage.

SC-SIM-01: a job may also name the ParameterSet revision its execution run declared
(``payload.parameterInput``). The worker re-hashes the stored revision, checks it is the one the run
pinned, and builds the runtime parameters from it alone; no other inline key is accepted beside it.
The lineage token ``artifact-bound-verified`` therefore means "bound server-side to an immutable
registry revision": dataset bytes or a parameter-set revision.
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
from .registry import get_dataset_revision, get_execution_run, get_parameter_set_revision
from .utils import sha256_hex

BINDING_SCHEMA = "sc-workspace-dataset-input-binding/1.0"
VERIFIED = "artifact-bound-verified"
INLINE = "inline-unverified"
NONE = "none"
FORMATS = {"json-records", "csv"}
TRANSFORMS = {"least-squares-normal-equations", "numeric-series"}
SERIES_TARGETS = {"values", "observations"}
PARAMETER_BINDING_SCHEMA = "sc-workspace-parameter-input-binding/1.0"
PARAMETER_KIND = "parameter-set"
MAX_SERIES_POINTS = 100_000


class InputIntegrityRefused(HTTPException):
    """A deterministic refusal: the job's declared inputs cannot be bound to pinned bytes."""

    @property
    def code(self) -> str:
        return self.detail["code"]


def _refuse(code: str, **detail) -> InputIntegrityRefused:
    return InputIntegrityRefused(status_code=409, detail={"code": code, **detail})


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


def _numeric_series(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    """One numeric column as an ordered series. Row order is the pinned file order unless ``orderBy`` names a
    column with unique, uniformly typed keys. Missing or non-finite values are refused, never dropped."""
    column, order_by = str(spec.get("column") or ""), spec.get("orderBy")
    target = str(spec.get("target") or "values")
    if not column:
        raise _refuse("transform-needs-column")
    if target not in SERIES_TARGETS:
        raise _refuse("transform-target-unsupported", supported=sorted(SERIES_TARGETS))
    if not rows or len(rows) > MAX_SERIES_POINTS:
        raise _refuse("transform-series-size", rows=len(rows), maximum=MAX_SERIES_POINTS)
    if order_by is not None:
        keys = [r.get(str(order_by)) for r in rows]
        numeric = all(isinstance(k, (int, float)) and not isinstance(k, bool) and math.isfinite(k) for k in keys)
        if not (numeric or all(isinstance(k, str) and k for k in keys)) or len(set(keys)) != len(keys):
            raise _refuse("transform-order-key-invalid", column=str(order_by),
                          detail="orderBy values must be unique and all numeric or all non-empty strings")
        rows = [r for _, r in sorted(zip(keys, rows), key=lambda kr: kr[0])]
    values = []
    for i, r in enumerate(rows):
        v = r.get(column)
        if not (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)):
            raise _refuse("transform-non-numeric-value", columns=[column], row=i)
        values.append(float(v))
    return {"target": target, "values": values}


def resolve_parameter_input(db: Session, user_key: str, payload: dict[str, Any], run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Returns (runtime payload, binding). The parameters come only from the run's pinned ParameterSet revision."""
    spec = payload.get("parameterInput")
    if not isinstance(spec, dict):
        raise _refuse("parameter-input-malformed")
    # notebookExecution is the plan dispatcher's orchestration record, not a parameter; it never reaches the runtime.
    extra = sorted(set(payload) - {"parameterInput", "datasetInput", "notebookExecution"})
    if extra:
        raise _refuse("parameter-input-inline-keys", keys=extra[:16],
                      detail="with parameterInput every runtime parameter must come from the ParameterSet revision")
    ps_id = str(spec.get("parameterSetId") or "").strip()
    try:
        revision = int(spec.get("parameterSetRevision"))
    except (TypeError, ValueError) as exc:
        raise _refuse("parameter-input-revision-required") from exc
    if not run_id:
        raise _refuse("parameter-input-needs-run", detail="a parameter binding must belong to an execution run that declares it")
    run = get_execution_run(db, user_key, run_id)
    if run is None:
        raise _refuse("parameter-input-run-not-found", runId=run_id)
    declared = run.parameter_set_ref or {}
    if (declared.get("parameterSetId"), declared.get("revision")) != (ps_id, revision):
        raise _refuse("parameter-input-not-declared-by-run", runId=run_id, parameterSetId=ps_id, parameterSetRevision=revision)
    row = get_parameter_set_revision(db, user_key, ps_id, revision)
    if row is None:
        raise _refuse("parameter-input-not-found", parameterSetId=ps_id, parameterSetRevision=revision)
    # Same descriptor as registry.store_parameter_set: the stored revision must still hash to its fingerprint.
    recomputed = sha256_hex({"schema": "sc-workspace-parameter-set/1.0", "parameterSetId": row.parameter_set_id,
                             "projectId": row.project_id, "modelId": row.model_id, "name": row.name,
                             "parameters": row.parameters_json, "metadata": row.metadata_json})
    if recomputed != row.fingerprint or declared.get("fingerprint") != row.fingerprint:
        raise _refuse("parameter-set-integrity-failed", parameterSetId=ps_id, parameterSetRevision=revision)
    expected = str(spec.get("fingerprint") or "").lower()
    if expected and expected != row.fingerprint:
        raise _refuse("parameter-input-fingerprint-mismatch", expected=expected, pinned=row.fingerprint)
    params = row.parameters_json or {}
    if "datasetInput" in params or "parameterInput" in params:
        raise _refuse("parameter-set-contains-binding-keys")
    runtime_payload = dict(params)
    if "datasetInput" in payload:
        runtime_payload["datasetInput"] = payload["datasetInput"]
    cls = str((row.metadata_json or {}).get("scientificClassification") or "")
    binding = {
        "schema": PARAMETER_BINDING_SCHEMA, "kind": PARAMETER_KIND, "lineage": VERIFIED,
        "parameterSetId": ps_id, "parameterSetRevision": revision, "parameterSetFingerprint": row.fingerprint,
        "modelId": row.model_id, "parametersSha256": sha256_hex(params),
        # Declared by the parameter-set owner; Research never lets it make an output 'observed'.
        "scientificClassification": cls if cls in {"synthetic", "modelled", "literature-derived", "illustrative"} else "",
    }
    return runtime_payload, binding


def resolve_dataset_input(db: Session, user_key: str, payload: dict[str, Any], run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Returns (runtime payload, binding). Raises 409 on any integrity or ownership failure."""
    spec = payload.get("datasetInput")
    if not isinstance(spec, dict):
        raise _refuse("dataset-input-malformed")
    if "rows" in payload:
        raise _refuse("dataset-input-and-inline-rows", detail="send either datasetInput or rows, not both")
    transform = spec.get("transform")
    target = str(transform.get("target") or "values") if isinstance(transform, dict) and transform.get("kind") == "numeric-series" else None
    if target and target in payload:
        raise _refuse("dataset-input-and-inline-series", key=target)
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
    derived = None
    if transform is not None:
        if not isinstance(transform, dict) or transform.get("kind") not in TRANSFORMS:
            raise _refuse("dataset-input-transform-unsupported", supported=sorted(TRANSFORMS))
        if transform["kind"] == "numeric-series":
            series = _numeric_series(rows, transform)
            derived = {series["target"]: series["values"]}
        else:
            eq = _normal_equations(rows, transform)
            derived = {"Q": eq["Q"], "c": eq["c"]}
        runtime_payload.update(derived)
    else:
        runtime_payload["rows"] = rows
    binding = {
        "schema": BINDING_SCHEMA, "lineage": VERIFIED,
        "datasetId": dataset_id, "datasetRevision": revision, "datasetFingerprint": ds.fingerprint,
        "artifactId": ds.artifact_id, "artifactRevision": snapshot.revision, "artifactSha256": snapshot.sha256,
        "bytes": snapshot.bytes, "format": fmt, "rowCount": len(rows), "rowsSha256": sha256_hex(rows),
        "transform": transform, "derivedPayloadSha256": sha256_hex(derived) if derived else None,
    }
    return runtime_payload, binding


def lineage_for_payload(payload: dict[str, Any]) -> str:
    """Anything a client sent without a binding (rows, matrices, parameters) is unverified input."""
    return INLINE if isinstance(payload, dict) and payload else NONE
