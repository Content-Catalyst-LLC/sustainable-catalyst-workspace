from __future__ import annotations

import base64
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

import numpy as np
import pandas as pd
import scipy
from fastapi import HTTPException
from scipy import integrate as scipy_integrate
from scipy import optimize as scipy_optimize
import sympy as sp
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import ComputeExecutionReceipt
from .object_store import get_artifact, store_artifact
from .registry import store_run_output
from .schemas import ArtifactStoreRequest, ExecutionRunOutputRequest
from .utils import iso, sha256_hex


ProgressCallback = Callable[[int, dict[str, Any]], bool]


@dataclass(frozen=True)
class OperationSpec:
    operation: str
    engine: str
    category: str
    description: str
    deterministic: bool = True


OPERATIONS: tuple[OperationSpec, ...] = (
    OperationSpec("workspace.compute.describe", "pandas", "statistics", "Descriptive statistics, missingness, and column summaries for bounded tabular data."),
    OperationSpec("workspace.compute.transform", "pandas", "dataframe", "Declarative select/filter/sort/group/aggregate transforms over bounded tabular data."),
    OperationSpec("workspace.compute.linear-algebra", "numpy", "linear-algebra", "Bounded matrix solve, inverse, determinant, eigendecomposition, and matrix multiplication."),
    OperationSpec("workspace.compute.symbolic", "sympy", "symbolic", "Restricted symbolic simplify, differentiation, integration, and equation solving."),
    OperationSpec("workspace.compute.integrate-series", "scipy", "numerical", "Numerical integration over sampled x/y series using trapezoid or Simpson methods."),
    OperationSpec("workspace.compute.optimize-quadratic", "scipy", "optimization", "Bounded minimization of a quadratic objective with optional box constraints."),
    OperationSpec("workspace.compute.roots-polynomial", "numpy", "numerical", "Roots of a bounded polynomial coefficient vector."),
)

OPERATION_MAP = {item.operation: item for item in OPERATIONS}


class ComputeCancelled(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _engine_version(name: str) -> str:
    if name == "numpy":
        return np.__version__
    if name == "pandas":
        return pd.__version__
    if name == "scipy":
        return scipy.__version__
    if name == "sympy":
        return sp.__version__
    return ""


def compute_catalog() -> list[dict[str, Any]]:
    s = get_settings()
    return [
        {
            "operation": item.operation,
            "engine": item.engine,
            "engineVersion": _engine_version(item.engine),
            "category": item.category,
            "description": item.description,
            "deterministic": item.deterministic,
            "arbitraryCode": False,
            "limits": {
                "rows": s.compute_max_rows,
                "columns": s.compute_max_columns,
                "matrixDimension": s.compute_max_matrix_dimension,
                "symbolicExpressionChars": s.compute_max_symbolic_chars,
                "resultBytes": s.compute_max_result_bytes,
            },
        }
        for item in OPERATIONS
    ]


def _progress(cb: ProgressCallback | None, value: int, **details: Any) -> None:
    if cb is not None and cb(value, details):
        raise ComputeCancelled("Compute job cancellation was requested.")


def _finite_number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"{name} must be numeric.")
    if not math.isfinite(number):
        raise HTTPException(status_code=400, detail=f"{name} must be finite.")
    return number


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, np.ndarray):
        return [_json_safe(x) for x in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [_json_safe(x) for x in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return str(value)


def _bounded_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="Compute payload rows must be an array.")
    s = get_settings()
    if len(rows) > s.compute_max_rows:
        raise HTTPException(status_code=413, detail="Compute row limit exceeded.")
    normalized: list[dict[str, Any]] = []
    columns: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise HTTPException(status_code=400, detail="Each compute row must be an object.")
        clean = {str(k)[:160]: v for k, v in row.items()}
        columns.update(clean.keys())
        normalized.append(clean)
    if len(columns) > s.compute_max_columns:
        raise HTTPException(status_code=413, detail="Compute column limit exceeded.")
    return normalized


def _describe(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    rows = _bounded_rows(payload)
    _progress(cb, 25, stage="dataframe-loaded")
    df = pd.DataFrame(rows)
    selected = payload.get("columns") or list(df.columns)
    if not isinstance(selected, list) or any(str(c) not in df.columns for c in selected):
        raise HTTPException(status_code=400, detail="columns contains an unknown dataframe column.")
    frame = df[[str(c) for c in selected]] if selected else df
    _progress(cb, 55, stage="statistics")
    columns: dict[str, Any] = {}
    for name in frame.columns:
        series = frame[name]
        item: dict[str, Any] = {
            "dtype": str(series.dtype),
            "count": int(series.count()),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
        }
        numeric = pd.to_numeric(series, errors="coerce")
        valid = numeric.dropna()
        if len(valid):
            item["numeric"] = {
                "count": int(valid.count()),
                "mean": _json_safe(valid.mean()),
                "std": _json_safe(valid.std(ddof=1)) if len(valid) > 1 else 0.0,
                "min": _json_safe(valid.min()),
                "q25": _json_safe(valid.quantile(0.25)),
                "median": _json_safe(valid.quantile(0.5)),
                "q75": _json_safe(valid.quantile(0.75)),
                "max": _json_safe(valid.max()),
            }
        columns[str(name)] = item
    return {"rowCount": len(df), "columnCount": len(df.columns), "columns": columns}


def _apply_filter(df: pd.DataFrame, rule: dict[str, Any]) -> pd.DataFrame:
    column = str(rule.get("column") or "")
    op = str(rule.get("op") or "eq")
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Unknown filter column: {column}")
    value = rule.get("value")
    series = df[column]
    if op == "eq": mask = series == value
    elif op == "ne": mask = series != value
    elif op in {"gt", "gte", "lt", "lte"}:
        numeric = pd.to_numeric(series, errors="coerce")
        target = _finite_number(value, f"filter {column}")
        mask = {"gt": numeric > target, "gte": numeric >= target, "lt": numeric < target, "lte": numeric <= target}[op]
    elif op == "in":
        if not isinstance(value, list) or len(value) > 500:
            raise HTTPException(status_code=400, detail="Filter 'in' requires an array of at most 500 values.")
        mask = series.isin(value)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported filter operator: {op}")
    return df[mask.fillna(False)]


def _transform(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    rows = _bounded_rows(payload)
    df = pd.DataFrame(rows)
    _progress(cb, 20, stage="dataframe-loaded")
    for rule in payload.get("filters") or []:
        if not isinstance(rule, dict):
            raise HTTPException(status_code=400, detail="Each filter must be an object.")
        df = _apply_filter(df, rule)
    selected = payload.get("select")
    if selected:
        if not isinstance(selected, list) or any(str(c) not in df.columns for c in selected):
            raise HTTPException(status_code=400, detail="select contains an unknown dataframe column.")
        df = df[[str(c) for c in selected]]
    _progress(cb, 45, stage="filtered-selected")
    group_by = payload.get("groupBy") or []
    aggregations = payload.get("aggregations") or {}
    if group_by:
        if any(str(c) not in df.columns for c in group_by):
            raise HTTPException(status_code=400, detail="groupBy contains an unknown dataframe column.")
        allowed_aggs = {"count", "sum", "mean", "min", "max", "median", "std"}
        clean_aggs: dict[str, str] = {}
        if not isinstance(aggregations, dict) or not aggregations:
            raise HTTPException(status_code=400, detail="groupBy requires aggregations.")
        for col, agg in aggregations.items():
            if str(col) not in df.columns or str(agg) not in allowed_aggs:
                raise HTTPException(status_code=400, detail="Unsupported group aggregation.")
            clean_aggs[str(col)] = str(agg)
        df = df.groupby([str(c) for c in group_by], dropna=False).agg(clean_aggs).reset_index()
    sort_spec = payload.get("sort") or []
    if sort_spec:
        by: list[str] = []; ascending: list[bool] = []
        for item in sort_spec:
            if not isinstance(item, dict): raise HTTPException(status_code=400, detail="sort entries must be objects.")
            col = str(item.get("column") or "")
            if col not in df.columns: raise HTTPException(status_code=400, detail=f"Unknown sort column: {col}")
            by.append(col); ascending.append(str(item.get("direction") or "asc").lower() != "desc")
        df = df.sort_values(by=by, ascending=ascending, kind="mergesort")
    limit = int(payload.get("limit") or min(len(df), 1000))
    limit = max(0, min(limit, get_settings().compute_max_rows))
    df = df.head(limit)
    _progress(cb, 75, stage="transform-complete")
    return {"rowCount": int(len(df)), "columns": [str(c) for c in df.columns], "rows": _json_safe(df.to_dict(orient="records"))}


def _matrix(value: Any, name: str) -> np.ndarray:
    try:
        arr = np.asarray(value, dtype=float)
    except Exception:
        raise HTTPException(status_code=400, detail=f"{name} must be a numeric array.")
    if arr.ndim != 2 or 0 in arr.shape:
        raise HTTPException(status_code=400, detail=f"{name} must be a non-empty 2D matrix.")
    if max(arr.shape) > get_settings().compute_max_matrix_dimension:
        raise HTTPException(status_code=413, detail="Matrix dimension limit exceeded.")
    if not np.isfinite(arr).all():
        raise HTTPException(status_code=400, detail=f"{name} contains non-finite values.")
    return arr


def _linear_algebra(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    action = str(payload.get("action") or "")
    a = _matrix(payload.get("a"), "a")
    _progress(cb, 30, stage="matrix-validated")
    try:
        if action == "solve":
            b = np.asarray(payload.get("b"), dtype=float)
            if a.shape[0] != a.shape[1] or b.shape[0] != a.shape[0]:
                raise HTTPException(status_code=400, detail="solve requires square a and compatible b.")
            value = np.linalg.solve(a, b)
            result = {"solution": _json_safe(value)}
        elif action == "inverse":
            if a.shape[0] != a.shape[1]: raise HTTPException(status_code=400, detail="inverse requires a square matrix.")
            result = {"inverse": _json_safe(np.linalg.inv(a))}
        elif action == "determinant":
            if a.shape[0] != a.shape[1]: raise HTTPException(status_code=400, detail="determinant requires a square matrix.")
            result = {"determinant": float(np.linalg.det(a))}
        elif action == "eigen":
            if a.shape[0] != a.shape[1]: raise HTTPException(status_code=400, detail="eigen requires a square matrix.")
            values, vectors = np.linalg.eig(a)
            if np.iscomplexobj(values) or np.iscomplexobj(vectors):
                result = {"eigenvalues": [{"real": float(v.real), "imag": float(v.imag)} for v in values],
                          "eigenvectors": [[{"real": float(v.real), "imag": float(v.imag)} for v in row] for row in vectors]}
            else:
                result = {"eigenvalues": _json_safe(values), "eigenvectors": _json_safe(vectors)}
        elif action == "matmul":
            b = _matrix(payload.get("b"), "b")
            if a.shape[1] != b.shape[0]: raise HTTPException(status_code=400, detail="matmul dimensions are incompatible.")
            result = {"product": _json_safe(a @ b)}
        else:
            raise HTTPException(status_code=400, detail="Unsupported linear-algebra action.")
    except np.linalg.LinAlgError as exc:
        raise HTTPException(status_code=422, detail=f"Linear algebra failed: {exc}")
    _progress(cb, 80, stage="linear-algebra-complete")
    return {"action": action, **result}


_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ALLOWED_FUNCS = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt, "Abs": sp.Abs, "abs": sp.Abs}
_ALLOWED_CONSTS = {"pi": sp.pi, "E": sp.E}


def _safe_symbolic_expression(expression: str, variables: list[str]) -> tuple[sp.Expr, dict[str, sp.Symbol]]:
    if len(expression) > get_settings().compute_max_symbolic_chars:
        raise HTTPException(status_code=413, detail="Symbolic expression limit exceeded.")
    if "__" in expression or any(ch in expression for ch in "[]{};:'\"\\"):
        raise HTTPException(status_code=400, detail="Symbolic expression contains disallowed syntax.")
    if not re.fullmatch(r"[A-Za-z0-9_+\-*/^()., \t]+", expression):
        raise HTTPException(status_code=400, detail="Symbolic expression contains disallowed characters.")
    if len(variables) > 32 or any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", v) for v in variables):
        raise HTTPException(status_code=400, detail="Invalid symbolic variable list.")
    names = set(_IDENTIFIER_RE.findall(expression))
    allowed_names = set(variables) | set(_ALLOWED_FUNCS) | set(_ALLOWED_CONSTS)
    unknown = sorted(names - allowed_names)
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown symbolic identifier(s): {', '.join(unknown[:8])}")
    symbols = {name: sp.Symbol(name, real=True) for name in variables}
    locals_map: dict[str, Any] = {**symbols, **_ALLOWED_FUNCS, **_ALLOWED_CONSTS}
    try:
        expr = sp.sympify(expression.replace("^", "**"), locals=locals_map, evaluate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Symbolic expression could not be parsed: {exc.__class__.__name__}")
    if int(sp.count_ops(expr)) > get_settings().compute_max_symbolic_operations:
        raise HTTPException(status_code=413, detail="Symbolic operation complexity limit exceeded.")
    return expr, symbols


def _symbolic(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    expression = str(payload.get("expression") or "")
    variables = [str(v) for v in (payload.get("variables") or [])]
    action = str(payload.get("action") or "simplify")
    expr, symbols = _safe_symbolic_expression(expression, variables)
    _progress(cb, 30, stage="symbolic-parsed")
    variable_name = str(payload.get("variable") or (variables[0] if variables else ""))
    variable = symbols.get(variable_name)
    if action in {"differentiate", "integrate", "solve"} and variable is None:
        raise HTTPException(status_code=400, detail="A declared symbolic variable is required.")
    if action == "simplify": result = sp.simplify(expr)
    elif action == "differentiate": result = sp.diff(expr, variable, int(payload.get("order") or 1))
    elif action == "integrate": result = sp.integrate(expr, variable)
    elif action == "solve": result = sp.solve(sp.Eq(expr, 0), variable, dict=False)
    else: raise HTTPException(status_code=400, detail="Unsupported symbolic action.")
    _progress(cb, 80, stage="symbolic-complete")
    if isinstance(result, list): rendered = [str(x) for x in result]
    else: rendered = str(result)
    return {"action": action, "expression": str(expr), "result": rendered}


def _integrate_series(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    x = np.asarray(payload.get("x"), dtype=float); y = np.asarray(payload.get("y"), dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or len(x) < 2:
        raise HTTPException(status_code=400, detail="x and y must be equal-length 1D arrays with at least two values.")
    if len(x) > get_settings().compute_max_rows: raise HTTPException(status_code=413, detail="Series length limit exceeded.")
    if not np.isfinite(x).all() or not np.isfinite(y).all(): raise HTTPException(status_code=400, detail="Series contains non-finite values.")
    if np.any(np.diff(x) <= 0): raise HTTPException(status_code=400, detail="x values must be strictly increasing.")
    method = str(payload.get("method") or "trapezoid")
    _progress(cb, 40, stage="series-validated")
    if method == "trapezoid": value = scipy_integrate.trapezoid(y, x=x)
    elif method == "simpson": value = scipy_integrate.simpson(y, x=x)
    else: raise HTTPException(status_code=400, detail="Unsupported integration method.")
    return {"method": method, "integral": float(value), "samples": len(x)}


def _optimize_quadratic(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    q = _matrix(payload.get("q"), "q")
    if q.shape[0] != q.shape[1]: raise HTTPException(status_code=400, detail="q must be square.")
    n = q.shape[0]
    c = np.asarray(payload.get("c"), dtype=float)
    if c.shape != (n,) or not np.isfinite(c).all(): raise HTTPException(status_code=400, detail="c must be a finite vector compatible with q.")
    x0 = np.asarray(payload.get("x0") if payload.get("x0") is not None else np.zeros(n), dtype=float)
    if x0.shape != (n,) or not np.isfinite(x0).all(): raise HTTPException(status_code=400, detail="x0 must be a finite vector compatible with q.")
    bounds_payload = payload.get("bounds")
    bounds = None
    if bounds_payload is not None:
        if not isinstance(bounds_payload, list) or len(bounds_payload) != n: raise HTTPException(status_code=400, detail="bounds must match the optimization dimension.")
        bounds = []
        for item in bounds_payload:
            if not isinstance(item, list) or len(item) != 2: raise HTTPException(status_code=400, detail="Each bound must be [low, high].")
            low = None if item[0] is None else _finite_number(item[0], "bound low")
            high = None if item[1] is None else _finite_number(item[1], "bound high")
            if low is not None and high is not None and low > high: raise HTTPException(status_code=400, detail="Bound low exceeds high.")
            bounds.append((low, high))
    maxiter = max(1, min(int(payload.get("maxIterations") or 250), get_settings().compute_max_optimizer_iterations))
    _progress(cb, 35, stage="optimization-validated")
    def objective(x: np.ndarray) -> float:
        return float(0.5 * x @ q @ x + c @ x)
    result = scipy_optimize.minimize(objective, x0, method="L-BFGS-B" if bounds else "BFGS", bounds=bounds, options={"maxiter": maxiter})
    _progress(cb, 82, stage="optimization-complete")
    return {"success": bool(result.success), "status": int(result.status), "message": str(result.message)[:1000], "solution": _json_safe(result.x), "objective": float(result.fun), "iterations": int(getattr(result, "nit", 0))}


def _roots_polynomial(payload: dict[str, Any], cb: ProgressCallback | None) -> dict[str, Any]:
    coeffs = np.asarray(payload.get("coefficients"), dtype=float)
    if coeffs.ndim != 1 or len(coeffs) < 2 or len(coeffs) > get_settings().compute_max_polynomial_degree + 1:
        raise HTTPException(status_code=400, detail="coefficients must define a bounded polynomial of degree at least one.")
    if not np.isfinite(coeffs).all() or coeffs[0] == 0: raise HTTPException(status_code=400, detail="Polynomial coefficients must be finite with nonzero leading coefficient.")
    _progress(cb, 45, stage="polynomial-validated")
    roots = np.roots(coeffs)
    rendered = [{"real": float(v.real), "imag": float(v.imag)} for v in roots]
    return {"degree": len(coeffs) - 1, "roots": rendered}


_EXECUTORS = {
    "workspace.compute.describe": _describe,
    "workspace.compute.transform": _transform,
    "workspace.compute.linear-algebra": _linear_algebra,
    "workspace.compute.symbolic": _symbolic,
    "workspace.compute.integrate-series": _integrate_series,
    "workspace.compute.optimize-quadratic": _optimize_quadratic,
    "workspace.compute.roots-polynomial": _roots_polynomial,
}


def receipt_metadata(row: ComputeExecutionReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "jobId": row.job_id,
        "executionRunId": row.execution_run_id,
        "operation": row.operation,
        "engine": row.engine,
        "engineVersion": row.engine_version,
        "requestFingerprint": row.request_fingerprint,
        "resultArtifactId": row.result_artifact_id,
        "resultSha256": row.result_sha256,
        "resultBytes": row.result_bytes,
        "wallSeconds": row.wall_seconds,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
    }


def list_compute_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(select(ComputeExecutionReceipt).where(ComputeExecutionReceipt.user_key == user_key).order_by(ComputeExecutionReceipt.created_at.desc()).limit(max(1, min(limit, 250)))).all()
    return [receipt_metadata(row) for row in rows]


def get_compute_receipt(db: Session, user_key: str, receipt_id: str) -> ComputeExecutionReceipt | None:
    return db.get(ComputeExecutionReceipt, {"user_key": user_key, "receipt_id": receipt_id})


def execute_scientific_operation(db: Session, row, progress_callback: ProgressCallback | None = None) -> dict[str, Any]:
    spec = OPERATION_MAP.get(row.operation)
    if spec is None:
        raise HTTPException(status_code=400, detail="Scientific compute operation is not registered.")
    job_payload = (row.payload or {}).get("payload") or {}
    if not isinstance(job_payload, dict):
        raise HTTPException(status_code=400, detail="Scientific compute payload must be an object.")
    request_fp = sha256_hex({"operation": row.operation, "payload": job_payload})
    _progress(progress_callback, 10, stage="compute-started", engine=spec.engine)
    started = time.perf_counter()
    result = _EXECUTORS[row.operation](job_payload, progress_callback)
    wall_seconds = round(max(0.0, time.perf_counter() - started), 6)
    _progress(progress_callback, 90, stage="persisting-result")
    envelope = {
        "schema": "sc-workspace-scientific-compute-result/1.0",
        "workspaceVersion": get_settings().service_version,
        "operation": row.operation,
        "engine": spec.engine,
        "engineVersion": _engine_version(spec.engine),
        "requestFingerprint": request_fp,
        "result": _json_safe(result),
    }
    raw = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(raw) > get_settings().compute_max_result_bytes:
        raise HTTPException(status_code=413, detail="Scientific compute result exceeds the configured result size limit.")
    artifact_id = f"compute-result-{row.job_id}"
    existing = get_artifact(db, row.user_key, artifact_id)
    artifact_payload = ArtifactStoreRequest.model_validate({
        "schema": "sc-workspace-artifact-store/1.0",
        "artifactId": artifact_id,
        "projectId": row.project_id or None,
        "filename": f"{row.operation.split('.')[-1]}-{row.job_id}.json",
        "mediaType": "application/vnd.sc.workspace.compute-result+json",
        "contentBase64": base64.b64encode(raw).decode("ascii"),
        "expectedRevision": existing.revision if existing is not None else 0,
        "metadata": {"kind": "scientific-compute-result", "jobId": row.job_id, "executionRunId": row.execution_run_id, "operation": row.operation, "engine": spec.engine, "engineVersion": _engine_version(spec.engine), "requestFingerprint": request_fp},
    })
    artifact = store_artifact(db, row.user_key, artifact_payload)
    if row.execution_run_id:
        output_payload = ExecutionRunOutputRequest.model_validate({
            "schema": "sc-workspace-execution-run-output/1.0",
            "outputId": "scientific-compute-result",
            "artifactId": artifact.artifact_id,
            "role": "result",
            "label": "Scientific compute result",
            "metadata": {"operation": row.operation, "engine": spec.engine, "engineVersion": _engine_version(spec.engine)},
        })
        store_run_output(db, row.user_key, row.execution_run_id, output_payload)
    receipt_id = f"compute-receipt-{row.job_id}"
    receipt = db.get(ComputeExecutionReceipt, {"user_key": row.user_key, "receipt_id": receipt_id})
    if receipt is None:
        receipt = ComputeExecutionReceipt(user_key=row.user_key, receipt_id=receipt_id, job_id=row.job_id, execution_run_id=row.execution_run_id or "", operation=row.operation, engine=spec.engine, engine_version=_engine_version(spec.engine), request_fingerprint=request_fp, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256, result_bytes=artifact.bytes, wall_seconds=wall_seconds, metadata_json={"deterministic": spec.deterministic, "arbitraryCode": False}, created_at=_now())
        db.add(receipt)
    else:
        receipt.result_artifact_id = artifact.artifact_id; receipt.result_sha256 = artifact.sha256; receipt.result_bytes = artifact.bytes; receipt.wall_seconds = wall_seconds
    db.commit(); db.refresh(receipt)
    return {
        "schema": "sc-workspace-job-result/1.0",
        "scientificCompute": {
            "operation": row.operation,
            "engine": spec.engine,
            "engineVersion": _engine_version(spec.engine),
            "requestFingerprint": request_fp,
            "resultArtifact": {"artifactId": artifact.artifact_id, "sha256": artifact.sha256, "bytes": artifact.bytes, "mediaType": artifact.media_type},
            "receipt": receipt_metadata(receipt),
        },
        "result": envelope["result"],
    }
