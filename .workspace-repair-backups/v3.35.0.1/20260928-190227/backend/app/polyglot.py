from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import PolyglotExecutionReceipt, StatisticalModelReceipt, NumericalSimulationReceipt, PredictiveModelReceipt, ModelEvaluationReceipt, ForecastReceipt, ForecastEvaluationReceipt, ProbabilisticInferenceReceipt, UncertaintyAnalysisReceipt, OptimizationReceipt, DecisionOptimizationReceipt, ReliabilityAnalysisReceipt
from .object_store import get_artifact, store_artifact
from .registry import store_run_output
from .schemas import ArtifactStoreRequest, ExecutionRunOutputRequest
from .utils import sha256_hex

ProgressCallback = Callable[[int, dict[str, Any]], bool]


@dataclass(frozen=True)
class RuntimeSpec:
    language: str
    runtime: str
    transport: str
    operations: tuple[str, ...]
    description: str


RUNTIMES: tuple[RuntimeSpec, ...] = (
    RuntimeSpec("python", "cpython-scientific", "in-process", (
        "workspace.compute.describe", "workspace.compute.transform", "workspace.compute.linear-algebra",
        "workspace.compute.symbolic", "workspace.compute.integrate-series", "workspace.compute.optimize-quadratic",
        "workspace.compute.roots-polynomial",
    ), "Primary scientific runtime backed by NumPy, Pandas, SciPy, and SymPy."),
    RuntimeSpec("sql", "sqlite-analytical", "in-process", (
        "workspace.polyglot.sql.aggregate", "workspace.polyglot.sql.group-summary",
    ), "Bounded relational analytics over ephemeral tabular inputs; arbitrary SQL text is not accepted."),
    RuntimeSpec("r", "r-statistical-econometric", "server-configured-http", (
        "workspace.polyglot.r.describe", "workspace.polyglot.r.t-test", "workspace.polyglot.r.correlation",
        "workspace.polyglot.r.linear-model", "workspace.polyglot.r.logistic-model", "workspace.polyglot.r.anova",
        "workspace.polyglot.r.arima", "workspace.polyglot.r.econometric-ols",
    ), "Hardened R runtime for bounded statistical, inferential, time-series, and econometric workflows."),
    RuntimeSpec("julia", "julia-simulation-numerical", "server-configured-http", (
        "workspace.polyglot.julia.ode-linear-rk4", "workspace.polyglot.julia.lotka-volterra",
        "workspace.polyglot.julia.monte-carlo-normal", "workspace.polyglot.julia.quadratic-optimize",
        "workspace.polyglot.julia.eigen-analysis", "workspace.polyglot.julia.integrate-series",
        "workspace.polyglot.julia.polynomial-roots", "workspace.polyglot.julia.parameter-sweep",
    ), "Hardened Julia runtime for bounded simulation, numerical modeling, optimization, and sensitivity workflows."),
    RuntimeSpec("ml", "python-sklearn-predictive", "server-configured-http", (
        "workspace.ml.linear-regression", "workspace.ml.logistic-classification",
        "workspace.ml.random-forest-regression", "workspace.ml.random-forest-classification",
        "workspace.ml.gradient-boosting-regression", "workspace.ml.gradient-boosting-classification",
        "workspace.ml.cross-validate", "workspace.ml.predict",
    ), "Hardened Python/scikit-learn runtime for bounded predictive modeling, evaluation, cross-validation, and scoring."),
    RuntimeSpec("neural", "python-pytorch-neural", "server-configured-http", (
        "workspace.neural.tensor-summary", "workspace.neural.model-summary",
        "workspace.neural.linear-forward", "workspace.neural.mlp-forward",
        "workspace.neural.tensor-contract", "workspace.neural.dataset-manifest",
        "workspace.neural.batch-plan", "workspace.neural.transformation-apply",
        "workspace.neural.training-plan", "workspace.neural.train-linear", "workspace.neural.train-mlp",
        "workspace.neural.checkpoint-inspect", "workspace.neural.resume-linear", "workspace.neural.resume-mlp",
        "workspace.neural.evaluate-regression", "workspace.neural.evaluate-binary", "workspace.neural.evaluate-multiclass",
        "workspace.neural.calibration-report", "workspace.neural.uncertainty-summary",
        "workspace.neural.explain-gradient", "workspace.neural.explain-integrated-gradients",
        "workspace.neural.explain-occlusion", "workspace.neural.explain-global-sensitivity",
        "workspace.neural.embedding-generate", "workspace.neural.representation-summary",
        "workspace.neural.embedding-similarity", "workspace.neural.embedding-neighbors",
        "workspace.neural.infer-regression", "workspace.neural.infer-binary",
        "workspace.neural.infer-multiclass", "workspace.neural.prediction-inspect",
        "workspace.neural.package-create", "workspace.neural.package-verify",
        "workspace.neural.package-inspect", "workspace.neural.package-infer",
        "workspace.neural.device-inventory", "workspace.neural.device-plan",
        "workspace.neural.device-verify", "workspace.neural.accelerator-smoke",
        "workspace.neural.trial-plan", "workspace.neural.trial-execute",
        "workspace.neural.batch-execute", "workspace.neural.hyperparameter-grid",
        "workspace.neural.hyperparameter-random",
        "workspace.neural.remote-worker-inventory", "workspace.neural.remote-dispatch-plan",
        "workspace.neural.remote-execute", "workspace.neural.remote-receipt-verify",
        "workspace.neural.certification-plan", "workspace.neural.certification-execute",
        "workspace.neural.certification-verify", "workspace.neural.certification-report",
        "workspace.neural.graph-tensor-contract",
        "workspace.neural.graph-dataset-project",
        "workspace.neural.gnn-model-summary",
        "workspace.neural.gnn-forward",
        "workspace.neural.gnn-infer",
        "workspace.neural.gnn-split-plan",
        "workspace.neural.gnn-training-plan",
        "workspace.neural.gnn-train",
        "workspace.neural.gnn-checkpoint-create",
        "workspace.neural.gnn-checkpoint-resume",
    ), "Production-certified hardened PyTorch neural runtime for bounded declarative training, governed model packages, inference provenance, device orchestration, reproducible trial execution, operator-governed remote GPU dispatch, and machine-verifiable runtime assurance."),
    RuntimeSpec("forecast", "python-statsmodels-forecasting", "server-configured-http", (
        "workspace.forecast.naive", "workspace.forecast.seasonal-naive", "workspace.forecast.linear-trend", "workspace.forecast.exponential-smoothing",
        "workspace.forecast.holt-winters", "workspace.forecast.arima", "workspace.forecast.backtest", "workspace.forecast.evaluate",
    ), "Hardened forecasting runtime for bounded time-series models, intervals, rolling-origin backtesting, and evaluation."),
    RuntimeSpec("probability", "python-probabilistic-bayesian", "server-configured-http", (
        "workspace.probability.normal-summary", "workspace.probability.beta-binomial-update", "workspace.probability.normal-normal-update",
        "workspace.probability.gamma-poisson-update", "workspace.probability.posterior-predictive-binomial", "workspace.probability.uncertainty-propagate",
    ), "Hardened probabilistic and Bayesian runtime for bounded conjugate inference, credible intervals, posterior prediction, and uncertainty propagation."),
    RuntimeSpec("uncertainty", "python-monte-carlo-uq", "server-configured-http", (
        "workspace.uncertainty.monte-carlo-weighted-sum", "workspace.uncertainty.bootstrap-interval",
        "workspace.uncertainty.latin-hypercube", "workspace.uncertainty.correlated-normal",
        "workspace.uncertainty.empirical-summary", "workspace.uncertainty.rank-correlation-sensitivity",
        "workspace.uncertainty.variance-contribution-linear", "workspace.uncertainty.scenario-envelope",
    ), "Hardened uncertainty-quantification runtime for seeded Monte Carlo simulation, resampling, experimental design, correlation, sensitivity, and scenario envelopes."),
    RuntimeSpec("optimization", "python-optimization-parameter-search", "server-configured-http", (
        "workspace.optimize.quadratic-box", "workspace.optimize.linear-box", "workspace.optimize.grid-search", "workspace.optimize.random-search",
        "workspace.optimize.coordinate-descent", "workspace.optimize.pareto-weighted-sum", "workspace.optimize.robust-scenario-rank", "workspace.optimize.parameter-sweep-rank",
    ), "Hardened optimization runtime for bounded numerical optimization, parameter search, multi-objective weighting, and robust scenario ranking."),
    RuntimeSpec("decision", "python-robust-decision-pareto", "server-configured-http", (
        "workspace.decision.pareto-front", "workspace.decision.expected-utility-rank",
        "workspace.decision.minimax-regret", "workspace.decision.constraint-robustness",
        "workspace.decision.stochastic-dominance", "workspace.decision.robustness-envelope",
        "workspace.decision.scenario-stress-rank", "workspace.decision.value-of-perfect-information",
    ), "Hardened decision runtime for Pareto analysis, utility ranking, regret, scenario robustness, dominance, stress testing, and value-of-information analysis."),
    RuntimeSpec("reliability", "python-reliability-survival", "server-configured-http", (
        "workspace.reliability.kaplan-meier", "workspace.reliability.exponential-fit",
        "workspace.reliability.weibull-fit", "workspace.reliability.reliability-at-time",
        "workspace.reliability.series-parallel-system", "workspace.reliability.repairable-availability",
        "workspace.reliability.binomial-reliability", "workspace.reliability.inverse-power-life",
    ), "Hardened reliability runtime for survival estimation, failure-time models, system reliability, availability, reliability intervals, and accelerated-life analysis."),
    RuntimeSpec("wasm", "wasm-sandbox-adapter", "server-configured-http", (
        "workspace.polyglot.wasm.invoke",),
        "Server-configured WebAssembly adapter for portable, capability-bounded compute modules."),
)

RUNTIME_BY_LANGUAGE = {r.language: r for r in RUNTIMES}
OPERATION_LANGUAGE = {op: r.language for r in RUNTIMES for op in r.operations}


def _runtime_route(language: str) -> tuple[str, str]:
    s = get_settings()
    return {
        "r": (s.runtime_r_url, s.runtime_r_token),
        "julia": (s.runtime_julia_url, s.runtime_julia_token),
        "ml": (s.runtime_ml_url, s.runtime_ml_token),
        "neural": (s.runtime_neural_url, s.runtime_neural_token),
        "forecast": (s.runtime_forecast_url, s.runtime_forecast_token),
        "probability": (s.runtime_probability_url, s.runtime_probability_token),
        "uncertainty": (s.runtime_uncertainty_url, s.runtime_uncertainty_token),
        "optimization": (s.runtime_optimization_url, s.runtime_optimization_token),
        "decision": (s.runtime_decision_url, s.runtime_decision_token),
        "reliability": (s.runtime_reliability_url, s.runtime_reliability_token),
        "wasm": (s.runtime_wasm_url, s.runtime_wasm_token),
    }.get(language, ("", ""))


def runtime_catalog() -> list[dict[str, Any]]:
    items=[]
    for spec in RUNTIMES:
        url, token = _runtime_route(spec.language)
        configured = spec.transport == "in-process" or bool(url.strip())
        items.append({
            "language": spec.language,
            "runtime": spec.runtime,
            "transport": spec.transport,
            "configured": configured,
            "serviceCredentialConfigured": True if spec.transport == "in-process" else bool(token.strip()),
            "serverConfiguredOnly": True,
            "clientSuppliedRuntimeUrlAllowed": False,
            "clientSuppliedCredentialsAllowed": False,
            "arbitraryCodeExecution": False,
            "operations": list(spec.operations),
            "description": spec.description,
            "interchange": {"schema": "sc-workspace-native-arrow-table/1.0", "formats": ["records-json", "arrow-ipc-stream", "parquet"]},
        })
    return items


def operation_catalog() -> list[dict[str, Any]]:
    result=[]
    for spec in RUNTIMES:
        for op in spec.operations:
            result.append({
                "operation": op,
                "language": spec.language,
                "runtime": spec.runtime,
                "transport": spec.transport,
                "arbitraryCode": False,
                "serverConfiguredOnly": True,
            })
    return result


def runtime_health(language: str) -> dict[str, Any]:
    if language not in {"r", "julia", "ml", "neural", "forecast", "probability", "uncertainty", "optimization", "decision", "reliability", "wasm"}:
        raise HTTPException(status_code=400, detail="Runtime health is only available for external runtimes")
    url, _token = _runtime_route(language)
    if not url.strip():
        return {"language": language, "configured": False, "available": False}
    health_url = url.strip()
    if health_url.endswith("/v1/execute"):
        health_url = health_url[:-len("/v1/execute")] + "/health"
    else:
        health_url = health_url.rstrip("/") + "/health"
    try:
        response = httpx.get(health_url, timeout=min(get_settings().polyglot_timeout_seconds, 5.0))
    except httpx.HTTPError as exc:
        return {"language": language, "configured": True, "available": False, "error": exc.__class__.__name__}
    body: dict[str, Any]
    try:
        parsed = response.json()
        body = parsed if isinstance(parsed, dict) else {}
    except ValueError:
        body = {}
    return {
        "language": language,
        "configured": True,
        "available": 200 <= response.status_code < 300 and body.get("ok") is True,
        "httpStatus": response.status_code,
        "service": body.get("service", ""),
        "version": body.get("version", ""),
        "runtime": body.get("runtime", ""),
        "operations": body.get("operations", []),
        "boundedOperationsOnly": body.get("boundedOperationsOnly", True),
        "arbitraryCodeExecution": body.get("arbitraryCodeExecution", False),
    }


def _bounded_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows=payload.get("rows")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="rows must be an array")
    s=get_settings()
    if len(rows)>s.polyglot_max_exchange_rows:
        raise HTTPException(status_code=413, detail="Polyglot exchange row limit exceeded")
    cols=set()
    out=[]
    for row in rows:
        if not isinstance(row, dict):
            raise HTTPException(status_code=400, detail="Each row must be an object")
        clean={str(k)[:160]: v for k,v in row.items()}
        cols.update(clean)
        out.append(clean)
    if len(cols)>s.polyglot_max_exchange_columns:
        raise HTTPException(status_code=413, detail="Polyglot exchange column limit exceeded")
    encoded=json.dumps(out, separators=(",",":"), ensure_ascii=False, default=str).encode()
    if len(encoded)>s.polyglot_max_payload_bytes:
        raise HTTPException(status_code=413, detail="Polyglot exchange payload limit exceeded")
    return out


def arrow_compatible_descriptor(rows: list[dict[str, Any]]) -> dict[str, Any]:
    columns=[]
    names=[]
    for row in rows:
        for name in row:
            if name not in names: names.append(name)
    for name in names:
        vals=[r.get(name) for r in rows if r.get(name) is not None]
        kind="null"
        if vals:
            if all(isinstance(v,bool) for v in vals): kind="bool"
            elif all(isinstance(v,int) and not isinstance(v,bool) for v in vals): kind="int64"
            elif all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v)) for v in vals): kind="float64"
            else: kind="utf8"
        columns.append({"name":name,"logicalType":kind,"nullable":any(r.get(name) is None for r in rows)})
    return {"schema":"sc-workspace-arrow-compatible-table/1.0","rowCount":len(rows),"columns":columns,"format":"records-json"}


def _sql_execute(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    rows=_bounded_rows(payload)
    if not rows:
        return {"rows":[],"rowCount":0,"exchange":arrow_compatible_descriptor(rows)}
    columns=list(dict.fromkeys(k for r in rows for k in r.keys()))
    conn=sqlite3.connect(":memory:")
    try:
        qident=lambda x: '"'+str(x).replace('"','""')+'"'
        conn.execute("CREATE TABLE data ("+", ".join(f"{qident(c)}" for c in columns)+")")
        conn.executemany("INSERT INTO data VALUES ("+",".join("?" for _ in columns)+")", [[r.get(c) for c in columns] for r in rows])
        if operation == "workspace.polyglot.sql.aggregate":
            column=str(payload.get("column") or "")
            aggregate=str(payload.get("aggregate") or "count").lower()
            allowed={"count":"COUNT","sum":"SUM","avg":"AVG","min":"MIN","max":"MAX"}
            if column not in columns or aggregate not in allowed:
                raise HTTPException(status_code=400, detail="Unsupported SQL aggregate request")
            value=conn.execute(f"SELECT {allowed[aggregate]}({qident(column)}) FROM data").fetchone()[0]
            result={"aggregate":aggregate,"column":column,"value":value}
        elif operation == "workspace.polyglot.sql.group-summary":
            group=str(payload.get("groupBy") or "")
            value=str(payload.get("valueColumn") or "")
            aggregate=str(payload.get("aggregate") or "avg").lower()
            allowed={"count":"COUNT","sum":"SUM","avg":"AVG","min":"MIN","max":"MAX"}
            if group not in columns or value not in columns or aggregate not in allowed:
                raise HTTPException(status_code=400, detail="Unsupported SQL group summary request")
            cur=conn.execute(f"SELECT {qident(group)}, {allowed[aggregate]}({qident(value)}) FROM data GROUP BY {qident(group)} ORDER BY {qident(group)}")
            result={"rows":[{"group":r[0],"value":r[1]} for r in cur.fetchall()],"groupBy":group,"valueColumn":value,"aggregate":aggregate}
        else:
            raise HTTPException(status_code=400, detail="SQL operation is not registered")
        result["exchange"]=arrow_compatible_descriptor(rows)
        return result
    finally:
        conn.close()


def execute_external(language: str, row, payload: dict[str, Any]) -> dict[str, Any]:
    url, token=_runtime_route(language)
    if not url.strip():
        raise HTTPException(status_code=409, detail=f"{language} runtime adapter is not configured")
    exchange_rows=_bounded_rows(payload) if "rows" in payload else []
    envelope={
        "schema":"sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion":get_settings().service_version,
        "jobId":row.job_id,
        "language":language,
        "operation":row.operation,
        "payload":payload,
        "exchange":arrow_compatible_descriptor(exchange_rows) if exchange_rows else None,
        "requestFingerprint":row.request_fingerprint,
        "executionPolicy":(row.payload or {}).get("executionPolicy") or {},
        "resourceBudget":(row.payload or {}).get("resourceBudget") or {},
        "sandbox":(row.payload or {}).get("sandbox") or {},
        "serverConfiguredOnly":True,
        "clientSuppliedRuntimeUrlAllowed":False,
        "arbitraryCodeExecution":False,
    }
    headers={"Content-Type":"application/json","Accept":"application/json"}
    if token.strip(): headers["Authorization"]=f"Bearer {token.strip()}"
    try:
        resp=httpx.post(url.strip(), json=envelope, headers=headers, timeout=get_settings().polyglot_timeout_seconds)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"{language} runtime transport failed: {exc.__class__.__name__}") from exc
    if not (200 <= resp.status_code < 300):
        raise HTTPException(status_code=502, detail=f"{language} runtime returned HTTP {resp.status_code}")
    try: body=resp.json()
    except ValueError: body={"text":resp.text[:4000]}
    return {"remote":body,"envelopeFingerprint":sha256_hex(json.dumps(envelope, sort_keys=True, separators=(",",":"), default=str))}


def execute_polyglot_operation(db: Session, row, progress_callback: ProgressCallback | None=None) -> dict[str, Any]:
    language=OPERATION_LANGUAGE.get(row.operation)
    if not language or language == "python":
        raise HTTPException(status_code=400, detail="Operation is not a polyglot-fabric operation")
    payload=((row.payload or {}).get("payload") or {})
    if progress_callback: progress_callback(15,{"stage":"runtime-selected","language":language})
    started=datetime.now(timezone.utc)
    if language == "sql": result=_sql_execute(row.operation,payload)
    else: result=execute_external(language,row,payload)
    if progress_callback: progress_callback(75,{"stage":"runtime-complete","language":language})
    model_artifact_id = ""
    model_artifact_sha256 = ""
    if language == "ml" and isinstance(result, dict):
        remote_body = result.get("remote") if isinstance(result.get("remote"), dict) else {}
        ml_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        model_blob = ml_result.get("modelArtifact") if isinstance(ml_result.get("modelArtifact"), dict) else None
        if model_blob and model_blob.get("contentBase64"):
            model_artifact_id = f"predictive-model-{row.job_id}"
            existing_model = get_artifact(db,row.user_key,model_artifact_id)
            model_payload = ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0", "artifactId":model_artifact_id, "projectId":row.project_id or None,
                "filename":f"predictive-model-{row.job_id}.joblib", "mediaType":"application/vnd.sc.workspace.ml-model+joblib",
                "contentBase64":model_blob.get("contentBase64"), "expectedRevision":existing_model.revision if existing_model is not None else 0,
                "metadata":{"kind":"predictive-model","language":"ml","operation":row.operation,"jobId":row.job_id,"runtime":RUNTIME_BY_LANGUAGE[language].runtime},
            })
            model_artifact=store_artifact(db,row.user_key,model_payload)
            model_artifact_sha256=model_artifact.sha256
            ml_result["modelArtifact"]={"artifactId":model_artifact.artifact_id,"format":"joblib","mediaType":model_artifact.media_type,"sha256":model_artifact.sha256,"bytes":model_artifact.bytes}
    neural_checkpoint_artifact = None
    neural_training_ops = {"workspace.neural.train-linear", "workspace.neural.train-mlp", "workspace.neural.resume-linear", "workspace.neural.resume-mlp"}
    if language == "neural" and row.operation in neural_training_ops and isinstance(result, dict):
        remote_body = result.get("remote") if isinstance(result.get("remote"), dict) else {}
        neural_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        checkpoint_blob = neural_result.get("checkpointArtifact") if isinstance(neural_result.get("checkpointArtifact"), dict) else None
        if checkpoint_blob:
            checkpoint_raw = json.dumps(checkpoint_blob, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
            checkpoint_artifact_id = f"neural-checkpoint-{row.job_id}"
            existing_checkpoint = get_artifact(db, row.user_key, checkpoint_artifact_id)
            checkpoint_payload = ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0",
                "artifactId":checkpoint_artifact_id,
                "projectId":row.project_id or None,
                "filename":f"neural-checkpoint-{row.job_id}.json",
                "mediaType":"application/vnd.sc.workspace.neural-checkpoint+json",
                "contentBase64":__import__('base64').b64encode(checkpoint_raw).decode("ascii"),
                "expectedRevision":existing_checkpoint.revision if existing_checkpoint is not None else 0,
                "metadata":{
                    "kind":"neural-checkpoint", "language":"neural", "operation":row.operation, "jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,
                    "checkpointId":checkpoint_blob.get("checkpointId"),
                    "checkpointFingerprint":checkpoint_blob.get("artifactFingerprint"),
                    "parentCheckpointFingerprint":checkpoint_blob.get("parentCheckpointFingerprint"),
                    "lineageDepth":checkpoint_blob.get("lineageDepth"),
                    "modelType":checkpoint_blob.get("modelType"), "task":checkpoint_blob.get("task"),
                },
            })
            neural_checkpoint_artifact = store_artifact(db, row.user_key, checkpoint_payload)
            neural_result["workspaceCheckpointArtifact"] = {
                "artifactId":neural_checkpoint_artifact.artifact_id,
                "mediaType":neural_checkpoint_artifact.media_type,
                "sha256":neural_checkpoint_artifact.sha256,
                "bytes":neural_checkpoint_artifact.bytes,
                "checkpointFingerprint":checkpoint_blob.get("artifactFingerprint"),
            }
    neural_analysis_artifact = None
    neural_analysis_ops = {
        "workspace.neural.evaluate-regression", "workspace.neural.evaluate-binary", "workspace.neural.evaluate-multiclass",
        "workspace.neural.calibration-report", "workspace.neural.uncertainty-summary",
        "workspace.neural.explain-gradient", "workspace.neural.explain-integrated-gradients",
        "workspace.neural.explain-occlusion", "workspace.neural.explain-global-sensitivity",
    }
    if language == "neural" and row.operation in neural_analysis_ops and isinstance(result, dict):
        remote_body = result.get("remote") if isinstance(result.get("remote"), dict) else {}
        neural_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        analysis_blob = neural_result.get("analysisArtifact") if isinstance(neural_result.get("analysisArtifact"), dict) else None
        if analysis_blob is None and isinstance(neural_result.get("explainabilityArtifact"), dict):
            analysis_blob = neural_result.get("explainabilityArtifact")
        if analysis_blob:
            analysis_raw = json.dumps(analysis_blob, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
            analysis_artifact_id = f"neural-analysis-{row.job_id}"
            existing_analysis = get_artifact(db, row.user_key, analysis_artifact_id)
            kind = str(analysis_blob.get("kind") or "neural-analysis")
            media_type = {
                "neural-evaluation":"application/vnd.sc.workspace.neural-evaluation+json",
                "neural-calibration":"application/vnd.sc.workspace.neural-calibration+json",
                "neural-uncertainty":"application/vnd.sc.workspace.neural-uncertainty+json",
                "neural-explainability":"application/vnd.sc.workspace.neural-explainability+json",
            }.get(kind, "application/vnd.sc.workspace.neural-analysis+json")
            analysis_payload = ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0", "artifactId":analysis_artifact_id, "projectId":row.project_id or None,
                "filename":f"neural-analysis-{row.job_id}.json", "mediaType":media_type,
                "contentBase64":__import__('base64').b64encode(analysis_raw).decode("ascii"),
                "expectedRevision":existing_analysis.revision if existing_analysis is not None else 0,
                "metadata":{
                    "kind":kind, "language":"neural", "operation":row.operation, "jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime, "task":analysis_blob.get("task"),
                    "analysisArtifactFingerprint":analysis_blob.get("artifactFingerprint"),
                    "modelSpecFingerprint":analysis_blob.get("modelSpecFingerprint"),
                    "checkpointFingerprint":analysis_blob.get("checkpointFingerprint"),
                    "evaluationDatasetFingerprint":analysis_blob.get("evaluationDatasetFingerprint"),
                    "explanationDatasetFingerprint":analysis_blob.get("explanationDatasetFingerprint"),
                    "explainabilityMethod":analysis_blob.get("method"),
                },
            })
            neural_analysis_artifact = store_artifact(db, row.user_key, analysis_payload)
            neural_result["workspaceAnalysisArtifact"] = {
                "artifactId":neural_analysis_artifact.artifact_id, "mediaType":neural_analysis_artifact.media_type,
                "sha256":neural_analysis_artifact.sha256, "bytes":neural_analysis_artifact.bytes,
                "analysisArtifactFingerprint":analysis_blob.get("artifactFingerprint"),
            }

    neural_representation_artifact = None
    neural_representation_ops = {
        "workspace.neural.embedding-generate", "workspace.neural.representation-summary",
        "workspace.neural.embedding-similarity", "workspace.neural.embedding-neighbors",
    }
    if language == "neural" and row.operation in neural_representation_ops and isinstance(result, dict):
        remote_body = result.get("remote") if isinstance(result.get("remote"), dict) else {}
        neural_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        representation_blob = neural_result.get("embeddingArtifact") if isinstance(neural_result.get("embeddingArtifact"), dict) else None
        if representation_blob is None and isinstance(neural_result.get("representationArtifact"), dict):
            representation_blob = neural_result.get("representationArtifact")
        if representation_blob:
            representation_raw=json.dumps(representation_blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            is_embedding=representation_blob.get("schema")=="sc-workspace-neural-embedding-artifact/1.0"
            representation_artifact_id=("neural-embedding-" if is_embedding else "neural-representation-")+row.job_id
            existing_representation=get_artifact(db,row.user_key,representation_artifact_id)
            media_type="application/vnd.sc.workspace.neural-embedding+json" if is_embedding else "application/vnd.sc.workspace.neural-representation+json"
            representation_payload=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":representation_artifact_id,"projectId":row.project_id or None,
                "filename":f"{'neural-embedding' if is_embedding else 'neural-representation'}-{row.job_id}.json","mediaType":media_type,
                "contentBase64":__import__('base64').b64encode(representation_raw).decode("ascii"),
                "expectedRevision":existing_representation.revision if existing_representation is not None else 0,
                "metadata":{
                    "kind":representation_blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"artifactFingerprint":representation_blob.get("artifactFingerprint"),
                    "sourceEmbeddingArtifactFingerprint":representation_blob.get("sourceEmbeddingArtifactFingerprint"),
                    "modelSpecFingerprint":representation_blob.get("modelSpecFingerprint"),
                    "checkpointFingerprint":representation_blob.get("checkpointFingerprint"),
                    "representationDatasetFingerprint":representation_blob.get("representationDatasetFingerprint"),
                    "analysisType":representation_blob.get("analysisType"),"normalization":representation_blob.get("normalization"),
                    "rows":representation_blob.get("rows"),"dimensions":representation_blob.get("dimensions"),
                },
            })
            neural_representation_artifact=store_artifact(db,row.user_key,representation_payload)
            neural_result["workspaceRepresentationArtifact"]={
                "artifactId":neural_representation_artifact.artifact_id,"mediaType":neural_representation_artifact.media_type,
                "sha256":neural_representation_artifact.sha256,"bytes":neural_representation_artifact.bytes,
                "artifactFingerprint":representation_blob.get("artifactFingerprint"),
            }

    neural_model_package_artifact = None
    if language == "neural" and row.operation == "workspace.neural.package-create" and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        package_blob=neural_result.get("modelPackage") if isinstance(neural_result.get("modelPackage"),dict) else None
        if package_blob:
            package_raw=json.dumps(package_blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            package_artifact_id="neural-model-package-"+row.job_id
            existing_package=get_artifact(db,row.user_key,package_artifact_id)
            package_payload=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":package_artifact_id,"projectId":row.project_id or None,
                "filename":f"neural-model-package-{row.job_id}.json","mediaType":"application/vnd.sc.workspace.neural-model-package+json",
                "contentBase64":__import__('base64').b64encode(package_raw).decode("ascii"),
                "expectedRevision":existing_package.revision if existing_package is not None else 0,
                "metadata":{
                    "kind":"neural-model-package","language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"task":package_blob.get("task"),
                    "modelPackageFingerprint":package_blob.get("artifactFingerprint"),"packageId":package_blob.get("packageId"),
                    "modelSpecFingerprint":package_blob.get("modelSpecFingerprint"),"checkpointFingerprint":package_blob.get("checkpointFingerprint"),
                    "runtimeContractFingerprint":((package_blob.get("manifest") or {}).get("runtimeContractFingerprint")),
                    "inferenceContractFingerprint":((package_blob.get("manifest") or {}).get("inferenceContractFingerprint")),
                },
            })
            neural_model_package_artifact=store_artifact(db,row.user_key,package_payload)
            neural_result["workspaceModelPackageArtifact"]={
                "artifactId":neural_model_package_artifact.artifact_id,"mediaType":neural_model_package_artifact.media_type,
                "sha256":neural_model_package_artifact.sha256,"bytes":neural_model_package_artifact.bytes,
                "modelPackageFingerprint":package_blob.get("artifactFingerprint"),"packageId":package_blob.get("packageId"),
            }

    neural_prediction_artifact = None
    neural_prediction_ops = {
        "workspace.neural.infer-regression", "workspace.neural.infer-binary", "workspace.neural.infer-multiclass",
        "workspace.neural.package-infer",
    }
    if language == "neural" and row.operation in neural_prediction_ops and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        prediction_blob=neural_result.get("predictionArtifact") if isinstance(neural_result.get("predictionArtifact"),dict) else None
        if prediction_blob:
            prediction_raw=json.dumps(prediction_blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            prediction_artifact_id="neural-prediction-"+row.job_id
            existing_prediction=get_artifact(db,row.user_key,prediction_artifact_id)
            prediction_payload=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":prediction_artifact_id,"projectId":row.project_id or None,
                "filename":f"neural-prediction-{row.job_id}.json","mediaType":"application/vnd.sc.workspace.neural-prediction+json",
                "contentBase64":__import__('base64').b64encode(prediction_raw).decode("ascii"),
                "expectedRevision":existing_prediction.revision if existing_prediction is not None else 0,
                "metadata":{
                    "kind":prediction_blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"task":prediction_blob.get("task"),
                    "predictionArtifactFingerprint":prediction_blob.get("artifactFingerprint"),
                    "modelSpecFingerprint":prediction_blob.get("modelSpecFingerprint"),
                    "checkpointFingerprint":prediction_blob.get("checkpointFingerprint"),
                    "inferenceDatasetFingerprint":prediction_blob.get("inferenceDatasetFingerprint"),
                    "rows":prediction_blob.get("rows"),"outputDimensions":prediction_blob.get("outputDimensions"),
                    "sourceModelPackageFingerprint":prediction_blob.get("sourceModelPackageFingerprint"),
                    "sourceModelPackageId":prediction_blob.get("sourceModelPackageId"),
                    "isObservedEvidence":False,"isEvaluation":False,
                },
            })
            neural_prediction_artifact=store_artifact(db,row.user_key,prediction_payload)
            neural_result["workspacePredictionArtifact"]={
                "artifactId":neural_prediction_artifact.artifact_id,"mediaType":neural_prediction_artifact.media_type,
                "sha256":neural_prediction_artifact.sha256,"bytes":neural_prediction_artifact.bytes,
                "predictionArtifactFingerprint":prediction_blob.get("artifactFingerprint"),
            }


    neural_gnn_artifact = None
    neural_gnn_ops = {
        "workspace.neural.graph-dataset-project", "workspace.neural.gnn-forward", "workspace.neural.gnn-infer",
        "workspace.neural.gnn-split-plan",
        "workspace.neural.gnn-training-plan",
        "workspace.neural.gnn-train",
        "workspace.neural.gnn-checkpoint-create",
        "workspace.neural.gnn-checkpoint-resume",
    }
    if language == "neural" and row.operation in neural_gnn_ops and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=nr.get("graphProjectionArtifact") if isinstance(nr.get("graphProjectionArtifact"),dict) else None
        if blob is None and isinstance(nr.get("gnnExecutionArtifact"),dict): blob=nr.get("gnnExecutionArtifact")
        if blob is None and isinstance(nr.get("gnnPredictionArtifact"),dict): blob=nr.get("gnnPredictionArtifact")
        if blob is None and isinstance(nr.get("gnnSplitPlanArtifact"),dict): blob=nr.get("gnnSplitPlanArtifact")
        if blob is None and isinstance(nr.get("gnnTrainingPlanArtifact"),dict): blob=nr.get("gnnTrainingPlanArtifact")
        if blob is None and isinstance(nr.get("gnnTrainingArtifact"),dict): blob=nr.get("gnnTrainingArtifact")
        if blob is None and isinstance(nr.get("gnnCheckpointArtifact"),dict): blob=nr.get("gnnCheckpointArtifact")
        if blob:
            raw_blob=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            schema=blob.get("schema")
            if schema=="sc-workspace-neural-graph-dataset-projection/1.0": media="application/vnd.sc.workspace.neural-graph-projection+json"; prefix="neural-graph-projection"; role="dataset-projection"
            elif schema=="sc-workspace-neural-gnn-split-plan/1.0": media="application/vnd.sc.workspace.neural-gnn-split-plan+json"; prefix="neural-gnn-split-plan"; role="split-plan"
            elif schema=="sc-workspace-neural-gnn-training-plan/1.0": media="application/vnd.sc.workspace.neural-gnn-training-plan+json"; prefix="neural-gnn-training-plan"; role="training-plan"
            elif schema=="sc-workspace-neural-gnn-training-artifact/1.0": media="application/vnd.sc.workspace.neural-gnn-training+json"; prefix="neural-gnn-training"; role="training"
            elif schema=="sc-workspace-neural-gnn-checkpoint-artifact/1.0": media="application/vnd.sc.workspace.neural-gnn-checkpoint+json"; prefix="neural-gnn-checkpoint"; role="checkpoint"
            elif schema=="sc-workspace-neural-gnn-prediction-artifact/1.0": media="application/vnd.sc.workspace.neural-gnn-prediction+json"; prefix="neural-gnn-prediction"; role="prediction"
            else: media="application/vnd.sc.workspace.neural-gnn-execution+json"; prefix="neural-gnn-execution"; role="execution"
            aid=f"{prefix}-{row.job_id}"
            existing_gnn=get_artifact(db,row.user_key,aid)
            req=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"projectId":row.project_id or None,
                "filename":f"{prefix}-{row.job_id}.json","mediaType":media,
                "contentBase64":__import__('base64').b64encode(raw_blob).decode("ascii"),
                "expectedRevision":existing_gnn.revision if existing_gnn is not None else 0,
                "metadata":{"kind":blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                            "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"artifactFingerprint":blob.get("artifactFingerprint"),
                            "graphFingerprint":blob.get("graphFingerprint"),"modelSpecFingerprint":blob.get("modelSpecFingerprint"),
                            "role":role,"isObservedEvidence":False},
            })
            neural_gnn_artifact=store_artifact(db,row.user_key,req)
            nr["workspaceGnnArtifact"]={"artifactId":neural_gnn_artifact.artifact_id,"mediaType":neural_gnn_artifact.media_type,
                                       "sha256":neural_gnn_artifact.sha256,"bytes":neural_gnn_artifact.bytes,
                                       "artifactFingerprint":blob.get("artifactFingerprint")}

    neural_trial_search_artifact = None
    neural_trial_search_ops = {
        "workspace.neural.trial-execute", "workspace.neural.batch-execute",
        "workspace.neural.hyperparameter-grid", "workspace.neural.hyperparameter-random",
    }
    if language == "neural" and row.operation in neural_trial_search_ops and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob = neural_result.get("trialArtifact") if isinstance(neural_result.get("trialArtifact"),dict) else None
        if blob is None and isinstance(neural_result.get("batchArtifact"),dict): blob=neural_result.get("batchArtifact")
        if blob is None and isinstance(neural_result.get("searchArtifact"),dict): blob=neural_result.get("searchArtifact")
        if blob:
            raw_blob=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            if blob.get("schema")=="sc-workspace-neural-trial-artifact/1.0":
                media="application/vnd.sc.workspace.neural-trial+json"; prefix="neural-trial"; role="trial"
            elif blob.get("schema")=="sc-workspace-neural-batch-artifact/1.0":
                media="application/vnd.sc.workspace.neural-batch+json"; prefix="neural-batch"; role="batch"
            else:
                media="application/vnd.sc.workspace.neural-hyperparameter-search+json"; prefix="neural-search"; role="search"
            aid=f"{prefix}-{row.job_id}"
            existing_exp=get_artifact(db,row.user_key,aid)
            req=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"projectId":row.project_id or None,
                "filename":f"{prefix}-{row.job_id}.json","mediaType":media,
                "contentBase64":__import__('base64').b64encode(raw_blob).decode("ascii"),
                "expectedRevision":existing_exp.revision if existing_exp is not None else 0,
                "metadata":{
                    "kind":blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"artifactFingerprint":blob.get("artifactFingerprint"),
                    "trialId":blob.get("trialId"),"trialCount":blob.get("trialCount"),
                    "bestTrialId":blob.get("bestTrialId"),"bestTrialArtifactFingerprint":blob.get("bestTrialArtifactFingerprint"),
                    "searchKind":blob.get("searchKind"),"role":role,
                },
            })
            neural_trial_search_artifact=store_artifact(db,row.user_key,req)
            neural_result["workspaceTrialSearchArtifact"]={
                "artifactId":neural_trial_search_artifact.artifact_id,"mediaType":neural_trial_search_artifact.media_type,
                "sha256":neural_trial_search_artifact.sha256,"bytes":neural_trial_search_artifact.bytes,
                "artifactFingerprint":blob.get("artifactFingerprint"),
            }

    neural_remote_execution_artifact = None
    if language == "neural" and row.operation == "workspace.neural.remote-execute" and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=neural_result.get("remoteExecutionArtifact") if isinstance(neural_result.get("remoteExecutionArtifact"),dict) else None
        if blob and blob.get("schema")=="sc-workspace-neural-remote-execution-artifact/1.0":
            raw_blob=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            aid=f"neural-remote-execution-{row.job_id}"
            existing_remote=get_artifact(db,row.user_key,aid)
            req=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"projectId":row.project_id or None,
                "filename":f"neural-remote-execution-{row.job_id}.json",
                "mediaType":"application/vnd.sc.workspace.neural-remote-execution+json",
                "contentBase64":__import__('base64').b64encode(raw_blob).decode("ascii"),
                "expectedRevision":existing_remote.revision if existing_remote is not None else 0,
                "metadata":{
                    "kind":blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"artifactFingerprint":blob.get("artifactFingerprint"),
                    "dispatchId":blob.get("dispatchId"),"workerId":blob.get("workerId"),
                    "remoteOperation":blob.get("operation"),"resultFingerprint":blob.get("resultFingerprint"),
                    "receiptFingerprint":blob.get("receiptFingerprint"),"role":"remote-execution",
                },
            })
            neural_remote_execution_artifact=store_artifact(db,row.user_key,req)
            neural_result["workspaceRemoteExecutionArtifact"]={
                "artifactId":neural_remote_execution_artifact.artifact_id,"mediaType":neural_remote_execution_artifact.media_type,
                "sha256":neural_remote_execution_artifact.sha256,"bytes":neural_remote_execution_artifact.bytes,
                "artifactFingerprint":blob.get("artifactFingerprint"),
            }

    neural_certification_artifact = None
    if language == "neural" and row.operation == "workspace.neural.certification-execute" and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=neural_result.get("certificationArtifact") if isinstance(neural_result.get("certificationArtifact"),dict) else None
        if blob and blob.get("schema")=="sc-workspace-neural-production-certification-artifact/1.0":
            raw_blob=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            aid=f"neural-production-certification-{row.job_id}"
            existing_cert=get_artifact(db,row.user_key,aid)
            req=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"projectId":row.project_id or None,
                "filename":f"neural-production-certification-{row.job_id}.json",
                "mediaType":"application/vnd.sc.workspace.neural-production-certification+json",
                "contentBase64":__import__('base64').b64encode(raw_blob).decode("ascii"),
                "expectedRevision":existing_cert.revision if existing_cert is not None else 0,
                "metadata":{
                    "kind":blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                    "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"certificationId":blob.get("certificationId"),
                    "artifactFingerprint":blob.get("artifactFingerprint"),"profile":blob.get("profile"),
                    "productionStatus":blob.get("productionStatus"),"requiredCheckCount":blob.get("requiredCheckCount"),
                    "passedRequiredCheckCount":blob.get("passedRequiredCheckCount"),
                    "remoteGpuTransportStatus":blob.get("remoteGpuTransportStatus"),"role":"runtime-certification",
                },
            })
            neural_certification_artifact=store_artifact(db,row.user_key,req)
            neural_result["workspaceProductionCertificationArtifact"]={
                "artifactId":neural_certification_artifact.artifact_id,"mediaType":neural_certification_artifact.media_type,
                "sha256":neural_certification_artifact.sha256,"bytes":neural_certification_artifact.bytes,
                "certificationArtifactFingerprint":blob.get("artifactFingerprint"),"certificationId":blob.get("certificationId"),
            }

    result_doc={"schema":"sc-workspace-polyglot-result/1.0","language":language,"operation":row.operation,"result":result}
    raw=json.dumps(result_doc,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
    if len(raw)>get_settings().compute_max_result_bytes:
        raise HTTPException(status_code=413, detail="Polyglot result byte limit exceeded")
    artifact_id=f"polyglot-result-{row.job_id}"
    existing=get_artifact(db,row.user_key,artifact_id)
    artifact_payload=ArtifactStoreRequest.model_validate({
        "schema":"sc-workspace-artifact-store/1.0",
        "artifactId":artifact_id,
        "projectId":row.project_id or None,
        "filename":f"polyglot-{language}-{row.job_id}.json",
        "mediaType":"application/vnd.sc.workspace.polyglot-result+json",
        "contentBase64":__import__('base64').b64encode(raw).decode("ascii"),
        "expectedRevision":existing.revision if existing is not None else 0,
        "metadata":{"kind":"polyglot-result","language":language,"operation":row.operation,"jobId":row.job_id},
    })
    artifact=store_artifact(db,row.user_key,artifact_payload)
    run_id=str(((row.payload or {}).get("executionRunId") or "")).strip()
    if run_id:
        output_payload=ExecutionRunOutputRequest.model_validate({
            "schema":"sc-workspace-execution-run-output/1.0",
            "outputId":"polyglot-result",
            "artifactId":artifact.artifact_id,
            "role":"result",
            "label":"Polyglot runtime result",
            "mediaType":"application/vnd.sc.workspace.polyglot-result+json",
            "sha256":artifact.sha256,
            "bytes":artifact.bytes,
            "metadata":{"language":language,"operation":row.operation},
        })
        store_run_output(db,row.user_key,run_id,output_payload)
        if neural_checkpoint_artifact is not None:
            checkpoint_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0",
                "outputId":"neural-checkpoint",
                "artifactId":neural_checkpoint_artifact.artifact_id,
                "role":"checkpoint",
                "label":"Neural training checkpoint",
                "mediaType":neural_checkpoint_artifact.media_type,
                "sha256":neural_checkpoint_artifact.sha256,
                "bytes":neural_checkpoint_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"checkpointPersistence":True},
            })
            store_run_output(db,row.user_key,run_id,checkpoint_output)
        if neural_analysis_artifact is not None:
            analysis_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0", "outputId":"neural-analysis",
                "artifactId":neural_analysis_artifact.artifact_id, "role":"analysis", "label":"Neural evaluation/calibration/uncertainty/explainability analysis",
                "mediaType":neural_analysis_artifact.media_type, "sha256":neural_analysis_artifact.sha256, "bytes":neural_analysis_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedNeuralAnalysis":True},
            })
            store_run_output(db,row.user_key,run_id,analysis_output)
        if neural_representation_artifact is not None:
            representation_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0", "outputId":"neural-representation",
                "artifactId":neural_representation_artifact.artifact_id, "role":"representation", "label":"Neural embedding / representation artifact",
                "mediaType":neural_representation_artifact.media_type, "sha256":neural_representation_artifact.sha256, "bytes":neural_representation_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedNeuralRepresentation":True},
            })
            store_run_output(db,row.user_key,run_id,representation_output)
        if neural_prediction_artifact is not None:
            prediction_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0", "outputId":"neural-prediction",
                "artifactId":neural_prediction_artifact.artifact_id, "role":"prediction", "label":"Governed neural prediction artifact",
                "mediaType":neural_prediction_artifact.media_type, "sha256":neural_prediction_artifact.sha256, "bytes":neural_prediction_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedNeuralPrediction":True,"isObservedEvidence":False},
            })
            store_run_output(db,row.user_key,run_id,prediction_output)
        if neural_trial_search_artifact is not None:
            trial_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0", "outputId":"neural-trial-search",
                "artifactId":neural_trial_search_artifact.artifact_id, "role":"analysis", "label":"Governed neural trial / batch / hyperparameter artifact",
                "mediaType":neural_trial_search_artifact.media_type, "sha256":neural_trial_search_artifact.sha256, "bytes":neural_trial_search_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedNeuralTrialSearch":True},
            })
            store_run_output(db,row.user_key,run_id,trial_output)

        if neural_gnn_artifact is not None:
            gnn_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0","outputId":"neural-gnn-artifact",
                "artifactId":neural_gnn_artifact.artifact_id,"role":"analysis","label":"Governed graph neural network artifact",
                "mediaType":neural_gnn_artifact.media_type,"sha256":neural_gnn_artifact.sha256,"bytes":neural_gnn_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedGnnArtifact":True,"isObservedEvidence":False},
            })
            store_run_output(db,row.user_key,run_id,gnn_output)

    finished=datetime.now(timezone.utc)
    receipt_details={"exchangeSchema":"sc-workspace-native-arrow-table/1.0","serverConfiguredOnly":True,"arbitraryCodeExecution":False}
    if language == "neural" and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        device_plan=remote_body.get("devicePlan") if isinstance(remote_body.get("devicePlan"),dict) else {}
        receipt_details.update({
            "neuralDeviceOrchestration":True,
            "selectedDevice":remote_body.get("device"),
            "devicePlanSchema":device_plan.get("schema"),
            "devicePlanFingerprint":device_plan.get("planFingerprint"),
            "deviceRequestedPreference":device_plan.get("requestedPreference"),
            "deviceAcceleratorSelected":device_plan.get("acceleratorSelected"),
            "deviceFallbackReason":device_plan.get("fallbackReason"),
        })
    if language == "neural" and row.operation in {"workspace.neural.train-linear","workspace.neural.train-mlp","workspace.neural.resume-linear","workspace.neural.resume-mlp"}:
        remote_body = result.get("remote") if isinstance(result, dict) and isinstance(result.get("remote"), dict) else {}
        neural_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        training_run = neural_result.get("trainingRun") if isinstance(neural_result.get("trainingRun"), dict) else {}
        receipt_details.update({
            "neuralTraining":True,
            "trainingRunSchema":training_run.get("schema"),
            "modelType":training_run.get("modelType"),
            "task":training_run.get("task"),
            "seed":training_run.get("seed"),
            "requestedEpochs":training_run.get("requestedEpochs"),
            "completedEpochs":training_run.get("completedEpochs"),
            "stoppedReason":training_run.get("stoppedReason"),
            "trainingSpecFingerprint":neural_result.get("trainingSpecFingerprint"),
            "trainingDatasetFingerprint":neural_result.get("trainingDatasetFingerprint"),
            "trainedModelSpecFingerprint":neural_result.get("trainedModelSpecFingerprint"),
            "checkpointPersistenceEnabled":True,
            "resumeTrainingEnabled":True,
            "checkpointArtifactSchema":"sc-workspace-neural-checkpoint-artifact/1.0",
            "checkpointArtifactFingerprint":neural_result.get("checkpointArtifactFingerprint"),
            "parentCheckpointFingerprint":neural_result.get("parentCheckpointFingerprint"),
            "checkpointLineageDepth":neural_result.get("checkpointLineageDepth"),
            "workspaceCheckpointArtifactId":neural_checkpoint_artifact.artifact_id if neural_checkpoint_artifact is not None else None,
            "workspaceCheckpointArtifactSha256":neural_checkpoint_artifact.sha256 if neural_checkpoint_artifact is not None else None,
            "resumed":training_run.get("resumed"),
            "resumedFromCheckpointFingerprint":training_run.get("resumedFromCheckpointFingerprint"),
            "startingEpoch":training_run.get("startingEpoch"),
            "cumulativeEpochs":training_run.get("cumulativeEpochs"),
        })
    if language == "neural" and row.operation in {
        "workspace.neural.evaluate-regression","workspace.neural.evaluate-binary","workspace.neural.evaluate-multiclass",
        "workspace.neural.calibration-report","workspace.neural.uncertainty-summary",
        "workspace.neural.explain-gradient","workspace.neural.explain-integrated-gradients",
        "workspace.neural.explain-occlusion","workspace.neural.explain-global-sensitivity"
    }:
        remote_body = result.get("remote") if isinstance(result, dict) and isinstance(result.get("remote"), dict) else {}
        neural_result = remote_body.get("result") if isinstance(remote_body.get("result"), dict) else {}
        analysis_blob = neural_result.get("analysisArtifact") if isinstance(neural_result.get("analysisArtifact"), dict) else {}
        if not analysis_blob and isinstance(neural_result.get("explainabilityArtifact"), dict):
            analysis_blob = neural_result.get("explainabilityArtifact")
        is_explainability = analysis_blob.get("schema") == "sc-workspace-neural-explainability-artifact/1.0"
        receipt_details.update({
            "neuralEvaluationCalibrationUncertainty":not is_explainability, "task":neural_result.get("task"),
            "analysisKind":neural_result.get("kind"), "analysisArtifactSchema":analysis_blob.get("schema"),
            "analysisArtifactFingerprint":analysis_blob.get("artifactFingerprint"),
            "modelSpecFingerprint":neural_result.get("modelSpecFingerprint"),
            "checkpointFingerprint":neural_result.get("checkpointFingerprint"),
            "evaluationDatasetFingerprint":neural_result.get("evaluationDatasetFingerprint"),
            "workspaceAnalysisArtifactId":neural_analysis_artifact.artifact_id if neural_analysis_artifact is not None else None,
            "workspaceAnalysisArtifactSha256":neural_analysis_artifact.sha256 if neural_analysis_artifact is not None else None,
            "neuralExplainability":is_explainability,
            "explainabilityMethod":analysis_blob.get("method") if is_explainability else None,
            "explanationDatasetFingerprint":neural_result.get("explanationDatasetFingerprint") if is_explainability else None,
        })
    if language == "neural" and row.operation in {
        "workspace.neural.embedding-generate", "workspace.neural.representation-summary",
        "workspace.neural.embedding-similarity", "workspace.neural.embedding-neighbors",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        representation_blob=neural_result.get("embeddingArtifact") if isinstance(neural_result.get("embeddingArtifact"),dict) else {}
        if not representation_blob and isinstance(neural_result.get("representationArtifact"),dict):
            representation_blob=neural_result.get("representationArtifact")
        receipt_details.update({
            "neuralEmbeddingRepresentation":True,
            "representationArtifactSchema":representation_blob.get("schema"),
            "representationArtifactFingerprint":representation_blob.get("artifactFingerprint"),
            "sourceEmbeddingArtifactFingerprint":representation_blob.get("sourceEmbeddingArtifactFingerprint"),
            "modelSpecFingerprint":representation_blob.get("modelSpecFingerprint"),
            "checkpointFingerprint":representation_blob.get("checkpointFingerprint"),
            "representationDatasetFingerprint":representation_blob.get("representationDatasetFingerprint"),
            "representationSelector":representation_blob.get("representation"),
            "normalization":representation_blob.get("normalization"),
            "representationAnalysisType":representation_blob.get("analysisType"),
            "rows":representation_blob.get("rows"),"dimensions":representation_blob.get("dimensions"),
            "workspaceRepresentationArtifactId":neural_representation_artifact.artifact_id if neural_representation_artifact is not None else None,
            "workspaceRepresentationArtifactSha256":neural_representation_artifact.sha256 if neural_representation_artifact is not None else None,
        })
    if language == "neural" and row.operation == "workspace.neural.package-create":
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        package_blob=neural_result.get("modelPackage") if isinstance(neural_result.get("modelPackage"),dict) else {}
        receipt_details.update({
            "neuralReproducibleModelPackage":True,"modelPackageSchema":package_blob.get("schema"),
            "modelPackageFingerprint":package_blob.get("artifactFingerprint"),"packageId":package_blob.get("packageId"),
            "task":package_blob.get("task"),"modelSpecFingerprint":package_blob.get("modelSpecFingerprint"),
            "checkpointFingerprint":package_blob.get("checkpointFingerprint"),
            "runtimeContractFingerprint":((package_blob.get("manifest") or {}).get("runtimeContractFingerprint")),
            "inferenceContractFingerprint":((package_blob.get("manifest") or {}).get("inferenceContractFingerprint")),
            "workspaceModelPackageArtifactId":neural_model_package_artifact.artifact_id if neural_model_package_artifact is not None else None,
            "workspaceModelPackageArtifactSha256":neural_model_package_artifact.sha256 if neural_model_package_artifact is not None else None,
            "portable":package_blob.get("portable"),"selfContainedInference":package_blob.get("selfContainedInference"),
            "containsArbitraryCode":((package_blob.get("manifest") or {}).get("containsArbitraryCode")),
        })
    if language == "neural" and row.operation in {
        "workspace.neural.infer-regression", "workspace.neural.infer-binary", "workspace.neural.infer-multiclass",
        "workspace.neural.package-infer",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        neural_result=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        prediction_blob=neural_result.get("predictionArtifact") if isinstance(neural_result.get("predictionArtifact"),dict) else {}
        receipt_details.update({
            "neuralInferencePredictionProvenance":True,
            "predictionArtifactSchema":prediction_blob.get("schema"),
            "predictionArtifactFingerprint":prediction_blob.get("artifactFingerprint"),
            "task":prediction_blob.get("task"),
            "modelSpecFingerprint":prediction_blob.get("modelSpecFingerprint"),
            "checkpointFingerprint":prediction_blob.get("checkpointFingerprint"),
            "inferenceDatasetFingerprint":prediction_blob.get("inferenceDatasetFingerprint"),
            "predictionPolicy":prediction_blob.get("predictionPolicy"),
            "uncertaintySemantics":prediction_blob.get("uncertaintySemantics"),
            "evidenceBoundary":prediction_blob.get("evidenceBoundary"),
            "isObservedEvidence":False,"isEvaluation":False,"targetsAccepted":False,
            "rows":prediction_blob.get("rows"),"outputDimensions":prediction_blob.get("outputDimensions"),
            "workspacePredictionArtifactId":neural_prediction_artifact.artifact_id if neural_prediction_artifact is not None else None,
            "workspacePredictionArtifactSha256":neural_prediction_artifact.sha256 if neural_prediction_artifact is not None else None,
            "sourceModelPackageFingerprint":prediction_blob.get("sourceModelPackageFingerprint"),
            "sourceModelPackageId":prediction_blob.get("sourceModelPackageId"),
            "packagedInference":row.operation=="workspace.neural.package-infer",
        })
    if language == "neural" and row.operation in {
        "workspace.neural.trial-plan", "workspace.neural.trial-execute", "workspace.neural.batch-execute",
        "workspace.neural.hyperparameter-grid", "workspace.neural.hyperparameter-random",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=nr.get("trialArtifact") if isinstance(nr.get("trialArtifact"),dict) else {}
        if not blob and isinstance(nr.get("batchArtifact"),dict): blob=nr.get("batchArtifact")
        if not blob and isinstance(nr.get("searchArtifact"),dict): blob=nr.get("searchArtifact")
        plan=nr.get("trialPlan") if isinstance(nr.get("trialPlan"),dict) else {}
        receipt_details.update({
            "neuralBatchTrialHyperparameterExecution":True,
            "trialPlanSchema":plan.get("schema"),"trialPlanFingerprint":plan.get("planFingerprint"),
            "trialArtifactSchema":blob.get("schema"),"trialArtifactFingerprint":blob.get("artifactFingerprint"),
            "trialId":blob.get("trialId"),"trialCount":blob.get("trialCount"),
            "bestTrialId":blob.get("bestTrialId"),"bestTrialArtifactFingerprint":blob.get("bestTrialArtifactFingerprint"),
            "bestObjectiveValue":blob.get("bestObjectiveValue"),"objective":blob.get("objective") or plan.get("objective"),
            "searchKind":blob.get("searchKind"),"searchSpaceFingerprint":blob.get("searchSpaceFingerprint"),
            "workspaceTrialSearchArtifactId":neural_trial_search_artifact.artifact_id if neural_trial_search_artifact is not None else None,
            "workspaceTrialSearchArtifactSha256":neural_trial_search_artifact.sha256 if neural_trial_search_artifact is not None else None,
        })
    if language == "neural" and row.operation in {
        "workspace.neural.remote-worker-inventory","workspace.neural.remote-dispatch-plan",
        "workspace.neural.remote-execute","workspace.neural.remote-receipt-verify",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        plan=nr.get("dispatchPlan") if isinstance(nr.get("dispatchPlan"),dict) else {}
        receipt_blob=nr.get("remoteReceipt") if isinstance(nr.get("remoteReceipt"),dict) else {}
        art=nr.get("remoteExecutionArtifact") if isinstance(nr.get("remoteExecutionArtifact"),dict) else {}
        receipt_details.update({
            "neuralRemoteGpuExecutionBroker":True,
            "remoteWorkerInventorySchema":"sc-workspace-neural-remote-worker-inventory/1.0",
            "remoteDispatchPlanSchema":"sc-workspace-neural-remote-dispatch-plan/1.0",
            "remoteExecutionReceiptSchema":"sc-workspace-neural-remote-execution-receipt/1.0",
            "remoteExecutionArtifactSchema":art.get("schema"),
            "remoteExecutionArtifactFingerprint":art.get("artifactFingerprint"),
            "remoteDispatchId":art.get("dispatchId") or receipt_blob.get("dispatchId"),
            "remoteWorkerId":art.get("workerId") or receipt_blob.get("workerId") or plan.get("workerId"),
            "remoteOperation":art.get("operation") or receipt_blob.get("operation") or plan.get("operation"),
            "remoteResultFingerprint":art.get("resultFingerprint") or receipt_blob.get("resultFingerprint"),
            "remoteReceiptFingerprint":art.get("receiptFingerprint") or receipt_blob.get("receiptFingerprint"),
            "remoteDispatchPlanFingerprint":art.get("dispatchPlanFingerprint") or plan.get("planFingerprint"),
            "workspaceRemoteExecutionArtifactId":neural_remote_execution_artifact.artifact_id if neural_remote_execution_artifact is not None else None,
            "workspaceRemoteExecutionArtifactSha256":neural_remote_execution_artifact.sha256 if neural_remote_execution_artifact is not None else None,
            "clientSuppliedRemoteWorkerUrlsAllowed":False,
        })
    if language == "neural" and row.operation in {
        "workspace.neural.certification-plan","workspace.neural.certification-execute",
        "workspace.neural.certification-verify","workspace.neural.certification-report",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        plan=nr.get("certificationPlan") if isinstance(nr.get("certificationPlan"),dict) else {}
        art=nr.get("certificationArtifact") if isinstance(nr.get("certificationArtifact"),dict) else {}
        report=nr.get("certificationReport") if isinstance(nr.get("certificationReport"),dict) else {}
        receipt_details.update({
            "neuralRuntimeProductionCertification":True,
            "productionCertificationProfile":art.get("profile") or plan.get("profile") or report.get("profile") or "workspace-neural-production/1.0",
            "productionCertificationPlanFingerprint":plan.get("planFingerprint") or art.get("planFingerprint"),
            "productionCertificationArtifactSchema":art.get("schema"),
            "productionCertificationArtifactFingerprint":art.get("artifactFingerprint") or nr.get("certificationArtifactFingerprint"),
            "productionCertificationId":art.get("certificationId") or nr.get("certificationId") or report.get("certificationId"),
            "productionCertificationStatus":art.get("productionStatus") or report.get("productionStatus"),
            "productionCertificationRequiredChecksPassed":art.get("passedRequiredCheckCount") or report.get("requiredChecksPassed"),
            "productionCertificationRequiredChecksTotal":art.get("requiredCheckCount") or report.get("requiredChecksTotal"),
            "remoteGpuTransportStatus":art.get("remoteGpuTransportStatus") or report.get("remoteGpuTransportStatus"),
            "workspaceProductionCertificationArtifactId":neural_certification_artifact.artifact_id if neural_certification_artifact is not None else None,
            "workspaceProductionCertificationArtifactSha256":neural_certification_artifact.sha256 if neural_certification_artifact is not None else None,
        })

    if language == "neural" and row.operation in {
        "workspace.neural.graph-tensor-contract","workspace.neural.graph-dataset-project","workspace.neural.gnn-model-summary",
        "workspace.neural.gnn-forward","workspace.neural.gnn-infer",
        "workspace.neural.gnn-split-plan",
        "workspace.neural.gnn-training-plan",
        "workspace.neural.gnn-train",
        "workspace.neural.gnn-checkpoint-create",
        "workspace.neural.gnn-checkpoint-resume",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=nr.get("graphTensorContract") if isinstance(nr.get("graphTensorContract"),dict) else {}
        if not blob and isinstance(nr.get("graphProjectionArtifact"),dict): blob=nr.get("graphProjectionArtifact")
        if not blob and isinstance(nr.get("gnnExecutionArtifact"),dict): blob=nr.get("gnnExecutionArtifact")
        if not blob and isinstance(nr.get("gnnPredictionArtifact"),dict): blob=nr.get("gnnPredictionArtifact")
        if not blob and isinstance(nr.get("gnnSplitPlanArtifact"),dict): blob=nr.get("gnnSplitPlanArtifact")
        if not blob and isinstance(nr.get("gnnTrainingPlanArtifact"),dict): blob=nr.get("gnnTrainingPlanArtifact")
        if not blob and isinstance(nr.get("gnnTrainingArtifact"),dict): blob=nr.get("gnnTrainingArtifact")
        if not blob and isinstance(nr.get("gnnCheckpointArtifact"),dict): blob=nr.get("gnnCheckpointArtifact")
        receipt_details.update({
            "graphNeuralNetworkRuntimeFoundation":True,"gnnArtifactSchema":blob.get("schema"),
            "gnnTrainingRuntime":True,"gnnCheckpointResumeEnabled":True,
            "gnnArtifactFingerprint":blob.get("artifactFingerprint"),"graphFingerprint":blob.get("graphFingerprint"),
            "modelSpecFingerprint":blob.get("modelSpecFingerprint"),"task":blob.get("task"),"adapter":blob.get("adapter"),
            "isObservedEvidence":False,"clientSuppliedGraphRuntimeUrlAllowed":False,
            "workspaceGnnArtifactId":neural_gnn_artifact.artifact_id if neural_gnn_artifact is not None else None,
            "workspaceGnnArtifactSha256":neural_gnn_artifact.sha256 if neural_gnn_artifact is not None else None,
        })

    receipt=PolyglotExecutionReceipt(
        receipt_id=f"pgr_{uuid4().hex}", user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id,
        language=language, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation,
        request_fingerprint=row.request_fingerprint, result_artifact_id=artifact.artifact_id,
        result_sha256=artifact.sha256, result_bytes=artifact.bytes,
        transport=RUNTIME_BY_LANGUAGE[language].transport, status="succeeded",
        started_at=started, finished_at=finished, details_json=receipt_details
    )
    db.add(receipt); db.flush()
    # Commit the language-neutral execution receipt before specialist receipt enrichment.
    db.commit(); db.refresh(receipt)
    statistical_receipt_id = ""
    if language == "r" and row.operation in R_MODEL_OPERATIONS:
        count = int(db.scalar(select(func.count()).select_from(StatisticalModelReceipt).where(StatisticalModelReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_statistical_model_receipts_per_account:
            raise HTTPException(status_code=409, detail="Statistical model receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        r_result = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(r_result, dict):
            r_result = {}
        payload_predictors = payload.get("predictors") or []
        if not isinstance(payload_predictors, list):
            payload_predictors = []
        stat = StatisticalModelReceipt(
            receipt_id=f"smr_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key,
            job_id=row.job_id, execution_run_id=run_id, language="r", runtime=RUNTIME_BY_LANGUAGE[language].runtime,
            operation=row.operation, model_kind=str(r_result.get("kind") or "")[:96],
            outcome=str(payload.get("outcome") or payload.get("column") or "")[:160],
            predictors_json=[str(x)[:160] for x in payload_predictors[:64]],
            metrics_json=r_result.get("metrics") if isinstance(r_result.get("metrics"), dict) else {},
            request_fingerprint=row.request_fingerprint, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256,
        )
        db.add(stat); db.flush(); statistical_receipt_id = stat.receipt_id
    # Artifact storage commits independently; explicitly commit runtime receipts so they survive
    # the worker's execute session and are visible to later API sessions.
    numerical_receipt_id = ""
    if language == "julia" and row.operation in JULIA_MODEL_OPERATIONS:
        count = int(db.scalar(select(func.count()).select_from(NumericalSimulationReceipt).where(NumericalSimulationReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_numerical_simulation_receipts_per_account:
            raise HTTPException(status_code=409, detail="Numerical simulation receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        j_result = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(j_result, dict):
            j_result = {}
        numerical = NumericalSimulationReceipt(
            receipt_id=f"nsr_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key,
            job_id=row.job_id, execution_run_id=run_id, language="julia", runtime=RUNTIME_BY_LANGUAGE[language].runtime,
            operation=row.operation, model_kind=str(j_result.get("kind") or "")[:96],
            solver=str(j_result.get("solver") or "")[:96], steps=int(j_result.get("steps") or payload.get("steps") or 0),
            random_seed=int(j_result.get("seed") or payload.get("seed") or 0),
            metrics_json=j_result.get("metrics") if isinstance(j_result.get("metrics"), dict) else {},
            request_fingerprint=row.request_fingerprint, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256,
        )
        db.add(numerical); db.flush(); numerical_receipt_id = numerical.receipt_id
    predictive_model_receipt_id = ""
    model_evaluation_receipt_id = ""
    if language == "ml" and row.operation in ML_EVALUATION_OPERATIONS:
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        ml_result = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(ml_result, dict): ml_result = {}
        metrics = ml_result.get("metrics") if isinstance(ml_result.get("metrics"), dict) else {}
        if row.operation in ML_TRAIN_OPERATIONS:
            count = int(db.scalar(select(func.count()).select_from(PredictiveModelReceipt).where(PredictiveModelReceipt.user_key == row.user_key)) or 0)
            if count >= get_settings().max_predictive_model_receipts_per_account:
                raise HTTPException(status_code=409, detail="Predictive model receipt limit reached")
            pm = PredictiveModelReceipt(
                receipt_id=f"pmr_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id,
                runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, model_kind=str(ml_result.get("modelKind") or "")[:96],
                task=str(ml_result.get("task") or "")[:32], target=str(ml_result.get("target") or payload.get("target") or "")[:160],
                features_json=[str(x)[:160] for x in (ml_result.get("features") or [])[:128]],
                preprocessing_json=ml_result.get("preprocessing") if isinstance(ml_result.get("preprocessing"),dict) else {},
                hyperparameters_json=ml_result.get("hyperparameters") if isinstance(ml_result.get("hyperparameters"),dict) else {},
                dataset_fingerprint=str(ml_result.get("datasetFingerprint") or "")[:64], random_seed=int(ml_result.get("seed") or 0),
                train_rows=int(ml_result.get("trainRows") or 0), test_rows=int(ml_result.get("testRows") or 0), metrics_json=metrics,
                model_artifact_id=model_artifact_id, model_sha256=model_artifact_sha256, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256,
            )
            db.add(pm); db.flush(); predictive_model_receipt_id=pm.receipt_id
        count_eval = int(db.scalar(select(func.count()).select_from(ModelEvaluationReceipt).where(ModelEvaluationReceipt.user_key == row.user_key)) or 0)
        if count_eval >= get_settings().max_model_evaluation_receipts_per_account:
            raise HTTPException(status_code=409, detail="Model evaluation receipt limit reached")
        ev = ModelEvaluationReceipt(
            receipt_id=f"mer_{uuid4().hex}", predictive_model_receipt_id=predictive_model_receipt_id, polyglot_receipt_id=receipt.receipt_id,
            user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, operation=row.operation,
            evaluation_kind="cross-validation" if row.operation == "workspace.ml.cross-validate" else "holdout",
            fold_count=int(ml_result.get("folds") or 0), dataset_fingerprint=str(ml_result.get("datasetFingerprint") or "")[:64],
            metrics_json=metrics, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256,
        )
        db.add(ev); db.flush(); model_evaluation_receipt_id=ev.receipt_id
    forecast_receipt_id = ""
    forecast_evaluation_receipt_id = ""
    if language == "forecast":
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        fr = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(fr, dict): fr = {}
        if row.operation != "workspace.forecast.evaluate":
            count = int(db.scalar(select(func.count()).select_from(ForecastReceipt).where(ForecastReceipt.user_key == row.user_key)) or 0)
            if count >= get_settings().max_forecast_receipts_per_account: raise HTTPException(status_code=409, detail="Forecast receipt limit reached")
            rec = ForecastReceipt(receipt_id=f"fcr_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, model_kind=str(fr.get("modelKind") or "")[:96], value_column=str(fr.get("valueColumn") or payload.get("valueColumn") or "value")[:160], time_column=str(fr.get("timeColumn") or payload.get("timeColumn") or "")[:160], frequency=str(fr.get("frequency") or payload.get("frequency") or "unspecified")[:64], horizon=int(fr.get("horizon") or 0), seasonal_period=int((fr.get("parameters") or {}).get("seasonalPeriod") or payload.get("seasonalPeriod") or 0), dataset_fingerprint=str(fr.get("datasetFingerprint") or "")[:64], parameters_json=fr.get("parameters") if isinstance(fr.get("parameters"),dict) else {}, metrics_json=fr.get("fitMetrics") if isinstance(fr.get("fitMetrics"),dict) else (fr.get("metrics") if isinstance(fr.get("metrics"),dict) else {}), intervals_json=fr.get("intervals") if isinstance(fr.get("intervals"),list) else [], result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
            db.add(rec); db.flush(); forecast_receipt_id=rec.receipt_id
        if row.operation in {"workspace.forecast.backtest","workspace.forecast.evaluate"}:
            count = int(db.scalar(select(func.count()).select_from(ForecastEvaluationReceipt).where(ForecastEvaluationReceipt.user_key == row.user_key)) or 0)
            if count >= get_settings().max_forecast_evaluation_receipts_per_account: raise HTTPException(status_code=409, detail="Forecast evaluation receipt limit reached")
            ev = ForecastEvaluationReceipt(receipt_id=f"fer_{uuid4().hex}", forecast_receipt_id=forecast_receipt_id, polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, operation=row.operation, evaluation_kind=str(fr.get("evaluationKind") or "direct")[:64], train_points=int(fr.get("trainPoints") or 0), test_points=int(fr.get("testPoints") or 0), dataset_fingerprint=str(fr.get("datasetFingerprint") or "")[:64], metrics_json=fr.get("metrics") if isinstance(fr.get("metrics"),dict) else {}, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
            db.add(ev); db.flush(); forecast_evaluation_receipt_id=ev.receipt_id
    probabilistic_inference_receipt_id = ""
    if language == "probability":
        count = int(db.scalar(select(func.count()).select_from(ProbabilisticInferenceReceipt).where(ProbabilisticInferenceReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_probabilistic_inference_receipts_per_account: raise HTTPException(status_code=409, detail="Probabilistic inference receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        pr = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(pr, dict): pr = {}
        posterior = pr.get("posterior") if isinstance(pr.get("posterior"), dict) else {}
        interval = posterior.get("credibleInterval") if isinstance(posterior.get("credibleInterval"), dict) else (pr.get("credibleInterval") if isinstance(pr.get("credibleInterval"),dict) else (pr.get("predictiveInterval") if isinstance(pr.get("predictiveInterval"),dict) else {}))
        prec = ProbabilisticInferenceReceipt(receipt_id=f"pir_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, inference_kind=str(pr.get("kind") or "")[:96], request_fingerprint=row.request_fingerprint, posterior_json=posterior, interval_json=interval, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
        db.add(prec); db.flush(); probabilistic_inference_receipt_id=prec.receipt_id
    uncertainty_analysis_receipt_id = ""
    if language == "uncertainty":
        count = int(db.scalar(select(func.count()).select_from(UncertaintyAnalysisReceipt).where(UncertaintyAnalysisReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_uncertainty_analysis_receipts_per_account: raise HTTPException(status_code=409, detail="Uncertainty analysis receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        ur = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(ur, dict): ur = {}
        sample_count = int(ur.get("draws") or ur.get("samples") or ur.get("sampleCount") or ur.get("scenarioCount") or ur.get("n") or 0)
        random_seed = int(ur.get("seed") or 0)
        interval_json = ur.get("interval") if isinstance(ur.get("interval"),dict) else {}
        summary_json = ur.get("summary") if isinstance(ur.get("summary"),dict) else {}
        sensitivity_json = ur.get("sensitivity") if isinstance(ur.get("sensitivity"),dict) else {}
        urec = UncertaintyAnalysisReceipt(receipt_id=f"uar_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, analysis_kind=str(ur.get("kind") or "")[:96], request_fingerprint=row.request_fingerprint, sample_count=sample_count, random_seed=random_seed, interval_json=interval_json, summary_json=summary_json, sensitivity_json=sensitivity_json, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
        db.add(urec); db.flush(); uncertainty_analysis_receipt_id=urec.receipt_id
    optimization_receipt_id = ""
    if language == "optimization":
        count = int(db.scalar(select(func.count()).select_from(OptimizationReceipt).where(OptimizationReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_optimization_receipts_per_account: raise HTTPException(status_code=409, detail="Optimization receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        rr = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(rr, dict): rr = {}
        objective_spec = payload.get("objective") if isinstance(payload.get("objective"),dict) else {}
        orec = OptimizationReceipt(receipt_id=f"opr_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, optimization_kind=str(rr.get("kind") or "")[:96], objective_kind=str(objective_spec.get("kind") or "")[:64], direction=str(rr.get("direction") or payload.get("direction") or "minimize")[:16], best_value=float(rr.get("bestValue") or 0.0), best_parameters_json=rr.get("bestParameters") if isinstance(rr.get("bestParameters"),dict) else {}, evaluation_count=int(rr.get("evaluationCount") or 0), iteration_count=int(rr.get("iterations") or 0), random_seed=int(rr.get("seed") or 0), converged=bool(rr.get("converged",True)), request_fingerprint=row.request_fingerprint, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
        db.add(orec); db.flush(); optimization_receipt_id=orec.receipt_id
    decision_optimization_receipt_id = ""
    if language == "decision":
        count = int(db.scalar(select(func.count()).select_from(DecisionOptimizationReceipt).where(DecisionOptimizationReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_decision_optimization_receipts_per_account: raise HTTPException(status_code=409, detail="Decision optimization receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        dr = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(dr, dict): dr = {}
        drec = DecisionOptimizationReceipt(receipt_id=f"dor_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, analysis_kind=str(dr.get("kind") or "")[:96], selected_alternative=str(dr.get("selectedAlternative") or "")[:160], candidate_count=int(dr.get("candidateCount") or 0), scenario_count=int(dr.get("scenarioCount") or 0), criterion=str(dr.get("criterion") or "")[:96], request_fingerprint=row.request_fingerprint, summary_json=dr.get("summary") if isinstance(dr.get("summary"),dict) else {}, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
        db.add(drec); db.flush(); decision_optimization_receipt_id=drec.receipt_id
    reliability_analysis_receipt_id = ""
    if language == "reliability":
        count = int(db.scalar(select(func.count()).select_from(ReliabilityAnalysisReceipt).where(ReliabilityAnalysisReceipt.user_key == row.user_key)) or 0)
        if count >= get_settings().max_reliability_analysis_receipts_per_account: raise HTTPException(status_code=409, detail="Reliability analysis receipt limit reached")
        remote_body = result.get("remote") if isinstance(result, dict) else {}
        rr = (remote_body or {}).get("result") if isinstance(remote_body, dict) else {}
        if not isinstance(rr, dict): rr = {}
        rrec = ReliabilityAnalysisReceipt(receipt_id=f"rar_{uuid4().hex}", polyglot_receipt_id=receipt.receipt_id, user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation, analysis_kind=str(rr.get("kind") or "")[:96], model_kind=str(rr.get("modelKind") or "")[:96], sample_count=int(rr.get("sampleCount") or 0), event_count=int(rr.get("eventCount") or 0), horizon=float(rr.get("horizon") or 0.0), request_fingerprint=row.request_fingerprint, metrics_json=rr.get("metrics") if isinstance(rr.get("metrics"),dict) else {}, result_artifact_id=artifact.artifact_id, result_sha256=artifact.sha256)
        db.add(rrec); db.flush(); reliability_analysis_receipt_id=rrec.receipt_id
    db.commit()
    db.refresh(receipt)
    if progress_callback: progress_callback(95,{"stage":"result-persisted","artifactId":artifact.artifact_id})
    return {"schema":"sc-workspace-job-result/1.0","polyglot":result_doc,"resultArtifactId":artifact.artifact_id,"receiptId":receipt.receipt_id,"statisticalModelReceiptId":statistical_receipt_id,"numericalSimulationReceiptId":numerical_receipt_id,"predictiveModelReceiptId":predictive_model_receipt_id,"modelEvaluationReceiptId":model_evaluation_receipt_id,"forecastReceiptId":forecast_receipt_id,"forecastEvaluationReceiptId":forecast_evaluation_receipt_id,"probabilisticInferenceReceiptId":probabilistic_inference_receipt_id,"uncertaintyAnalysisReceiptId":uncertainty_analysis_receipt_id,"optimizationReceiptId":optimization_receipt_id,"decisionOptimizationReceiptId":decision_optimization_receipt_id,"reliabilityAnalysisReceiptId":reliability_analysis_receipt_id,"modelArtifactId":model_artifact_id,"modelArtifactSha256":model_artifact_sha256,"resultSha256":artifact.sha256}


R_MODEL_OPERATIONS = {
    "workspace.polyglot.r.linear-model",
    "workspace.polyglot.r.logistic-model",
    "workspace.polyglot.r.anova",
    "workspace.polyglot.r.arima",
    "workspace.polyglot.r.econometric-ols",
}


def statistical_receipt_metadata(r: StatisticalModelReceipt) -> dict[str, Any]:
    return {
        "receiptId": r.receipt_id, "polyglotReceiptId": r.polyglot_receipt_id, "jobId": r.job_id,
        "executionRunId": r.execution_run_id, "language": r.language, "runtime": r.runtime,
        "operation": r.operation, "modelKind": r.model_kind, "outcome": r.outcome,
        "predictors": r.predictors_json or [], "metrics": r.metrics_json or {},
        "requestFingerprint": r.request_fingerprint, "resultArtifactId": r.result_artifact_id,
        "resultSha256": r.result_sha256, "createdAt": r.created_at.isoformat(),
    }


def list_statistical_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.execute(select(StatisticalModelReceipt).where(StatisticalModelReceipt.user_key == user_key).order_by(StatisticalModelReceipt.created_at.desc()).limit(limit)).scalars().all()
    return [statistical_receipt_metadata(r) for r in rows]


def get_statistical_receipt(db: Session, user_key: str, receipt_id: str):
    return db.execute(select(StatisticalModelReceipt).where(StatisticalModelReceipt.user_key == user_key, StatisticalModelReceipt.receipt_id == receipt_id)).scalar_one_or_none()


JULIA_MODEL_OPERATIONS = {
    "workspace.polyglot.julia.ode-linear-rk4",
    "workspace.polyglot.julia.lotka-volterra",
    "workspace.polyglot.julia.monte-carlo-normal",
    "workspace.polyglot.julia.quadratic-optimize",
    "workspace.polyglot.julia.eigen-analysis",
    "workspace.polyglot.julia.integrate-series",
    "workspace.polyglot.julia.polynomial-roots",
    "workspace.polyglot.julia.parameter-sweep",
}


def numerical_receipt_metadata(r: NumericalSimulationReceipt) -> dict[str, Any]:
    return {
        "receiptId": r.receipt_id, "polyglotReceiptId": r.polyglot_receipt_id, "jobId": r.job_id,
        "executionRunId": r.execution_run_id, "language": r.language, "runtime": r.runtime,
        "operation": r.operation, "modelKind": r.model_kind, "solver": r.solver, "steps": r.steps,
        "seed": r.random_seed, "metrics": r.metrics_json or {}, "requestFingerprint": r.request_fingerprint,
        "resultArtifactId": r.result_artifact_id, "resultSha256": r.result_sha256, "createdAt": r.created_at.isoformat(),
    }


def list_numerical_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.execute(select(NumericalSimulationReceipt).where(NumericalSimulationReceipt.user_key == user_key).order_by(NumericalSimulationReceipt.created_at.desc()).limit(limit)).scalars().all()
    return [numerical_receipt_metadata(r) for r in rows]


def get_numerical_receipt(db: Session, user_key: str, receipt_id: str):
    return db.execute(select(NumericalSimulationReceipt).where(NumericalSimulationReceipt.user_key == user_key, NumericalSimulationReceipt.receipt_id == receipt_id)).scalar_one_or_none()



ML_TRAIN_OPERATIONS = {
    "workspace.ml.linear-regression", "workspace.ml.logistic-classification",
    "workspace.ml.random-forest-regression", "workspace.ml.random-forest-classification",
    "workspace.ml.gradient-boosting-regression", "workspace.ml.gradient-boosting-classification",
}
ML_EVALUATION_OPERATIONS = ML_TRAIN_OPERATIONS | {"workspace.ml.cross-validate"}

def predictive_model_receipt_metadata(r: PredictiveModelReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"modelKind":r.model_kind,"task":r.task,"target":r.target,"features":r.features_json or [],"preprocessing":r.preprocessing_json or {},"hyperparameters":r.hyperparameters_json or {},"datasetFingerprint":r.dataset_fingerprint,"randomSeed":r.random_seed,"trainRows":r.train_rows,"testRows":r.test_rows,"metrics":r.metrics_json or {},"modelArtifactId":r.model_artifact_id,"modelSha256":r.model_sha256,"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_predictive_model_receipts(db: Session,user_key:str,limit:int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(PredictiveModelReceipt).where(PredictiveModelReceipt.user_key==user_key).order_by(PredictiveModelReceipt.created_at.desc()).limit(limit)).all()
    return [predictive_model_receipt_metadata(r) for r in rows]

def get_predictive_model_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(PredictiveModelReceipt).where(PredictiveModelReceipt.user_key==user_key,PredictiveModelReceipt.receipt_id==receipt_id)).scalar_one_or_none()

def model_evaluation_receipt_metadata(r: ModelEvaluationReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"predictiveModelReceiptId":r.predictive_model_receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"operation":r.operation,"evaluationKind":r.evaluation_kind,"foldCount":r.fold_count,"datasetFingerprint":r.dataset_fingerprint,"metrics":r.metrics_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_model_evaluation_receipts(db: Session,user_key:str,limit:int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(ModelEvaluationReceipt).where(ModelEvaluationReceipt.user_key==user_key).order_by(ModelEvaluationReceipt.created_at.desc()).limit(limit)).all()
    return [model_evaluation_receipt_metadata(r) for r in rows]

def get_model_evaluation_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(ModelEvaluationReceipt).where(ModelEvaluationReceipt.user_key==user_key,ModelEvaluationReceipt.receipt_id==receipt_id)).scalar_one_or_none()

def forecast_receipt_metadata(r: ForecastReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"modelKind":r.model_kind,"valueColumn":r.value_column,"timeColumn":r.time_column,"frequency":r.frequency,"horizon":r.horizon,"seasonalPeriod":r.seasonal_period,"datasetFingerprint":r.dataset_fingerprint,"parameters":r.parameters_json or {},"metrics":r.metrics_json or {},"intervals":r.intervals_json or [],"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_forecast_receipts(db: Session,user_key:str,limit:int=100):
    return [forecast_receipt_metadata(r) for r in db.scalars(select(ForecastReceipt).where(ForecastReceipt.user_key==user_key).order_by(ForecastReceipt.created_at.desc()).limit(limit)).all()]

def get_forecast_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(ForecastReceipt).where(ForecastReceipt.user_key==user_key,ForecastReceipt.receipt_id==receipt_id)).scalar_one_or_none()

def forecast_evaluation_receipt_metadata(r: ForecastEvaluationReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"forecastReceiptId":r.forecast_receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"operation":r.operation,"evaluationKind":r.evaluation_kind,"trainPoints":r.train_points,"testPoints":r.test_points,"datasetFingerprint":r.dataset_fingerprint,"metrics":r.metrics_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_forecast_evaluation_receipts(db: Session,user_key:str,limit:int=100):
    return [forecast_evaluation_receipt_metadata(r) for r in db.scalars(select(ForecastEvaluationReceipt).where(ForecastEvaluationReceipt.user_key==user_key).order_by(ForecastEvaluationReceipt.created_at.desc()).limit(limit)).all()]

def get_forecast_evaluation_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(ForecastEvaluationReceipt).where(ForecastEvaluationReceipt.user_key==user_key,ForecastEvaluationReceipt.receipt_id==receipt_id)).scalar_one_or_none()

def receipt_metadata(r: PolyglotExecutionReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"language":r.language,"runtime":r.runtime,"operation":r.operation,"requestFingerprint":r.request_fingerprint,"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"resultBytes":r.result_bytes,"transport":r.transport,"status":r.status,"startedAt":r.started_at.isoformat(),"finishedAt":r.finished_at.isoformat(),"details":r.details_json or {}}


def list_receipts(db: Session,user_key:str,limit:int=100) -> list[dict[str,Any]]:
    rows=db.execute(select(PolyglotExecutionReceipt).where(PolyglotExecutionReceipt.user_key==user_key).order_by(PolyglotExecutionReceipt.created_at.desc()).limit(limit)).scalars().all()
    return [receipt_metadata(r) for r in rows]


def get_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(PolyglotExecutionReceipt).where(PolyglotExecutionReceipt.user_key==user_key,PolyglotExecutionReceipt.receipt_id==receipt_id)).scalar_one_or_none()


def probabilistic_inference_receipt_metadata(r: ProbabilisticInferenceReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"inferenceKind":r.inference_kind,"requestFingerprint":r.request_fingerprint,"posterior":r.posterior_json or {},"interval":r.interval_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_probabilistic_inference_receipts(db: Session,user_key:str,limit:int=100):
    return [probabilistic_inference_receipt_metadata(r) for r in db.scalars(select(ProbabilisticInferenceReceipt).where(ProbabilisticInferenceReceipt.user_key==user_key).order_by(ProbabilisticInferenceReceipt.created_at.desc()).limit(limit)).all()]

def get_probabilistic_inference_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(ProbabilisticInferenceReceipt).where(ProbabilisticInferenceReceipt.user_key==user_key,ProbabilisticInferenceReceipt.receipt_id==receipt_id)).scalar_one_or_none()


def uncertainty_analysis_receipt_metadata(r: UncertaintyAnalysisReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"analysisKind":r.analysis_kind,"requestFingerprint":r.request_fingerprint,"sampleCount":r.sample_count,"seed":r.random_seed,"interval":r.interval_json or {},"summary":r.summary_json or {},"sensitivity":r.sensitivity_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_uncertainty_analysis_receipts(db: Session,user_key:str,limit:int=100):
    return [uncertainty_analysis_receipt_metadata(r) for r in db.scalars(select(UncertaintyAnalysisReceipt).where(UncertaintyAnalysisReceipt.user_key==user_key).order_by(UncertaintyAnalysisReceipt.created_at.desc()).limit(limit)).all()]

def get_uncertainty_analysis_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(UncertaintyAnalysisReceipt).where(UncertaintyAnalysisReceipt.user_key==user_key,UncertaintyAnalysisReceipt.receipt_id==receipt_id)).scalar_one_or_none()

def optimization_receipt_metadata(r: OptimizationReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"optimizationKind":r.optimization_kind,"objectiveKind":r.objective_kind,"direction":r.direction,"bestValue":r.best_value,"bestParameters":r.best_parameters_json or {},"evaluationCount":r.evaluation_count,"iterations":r.iteration_count,"seed":r.random_seed,"converged":r.converged,"requestFingerprint":r.request_fingerprint,"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_optimization_receipts(db: Session,user_key:str,limit:int=100):
    return [optimization_receipt_metadata(r) for r in db.scalars(select(OptimizationReceipt).where(OptimizationReceipt.user_key==user_key).order_by(OptimizationReceipt.created_at.desc()).limit(limit)).all()]

def get_optimization_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(OptimizationReceipt).where(OptimizationReceipt.user_key==user_key,OptimizationReceipt.receipt_id==receipt_id)).scalar_one_or_none()


def decision_optimization_receipt_metadata(r: DecisionOptimizationReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"analysisKind":r.analysis_kind,"selectedAlternative":r.selected_alternative,"candidateCount":r.candidate_count,"scenarioCount":r.scenario_count,"criterion":r.criterion,"requestFingerprint":r.request_fingerprint,"summary":r.summary_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_decision_optimization_receipts(db: Session,user_key:str,limit:int=100):
    return [decision_optimization_receipt_metadata(r) for r in db.scalars(select(DecisionOptimizationReceipt).where(DecisionOptimizationReceipt.user_key==user_key).order_by(DecisionOptimizationReceipt.created_at.desc()).limit(limit)).all()]

def get_decision_optimization_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(DecisionOptimizationReceipt).where(DecisionOptimizationReceipt.user_key==user_key,DecisionOptimizationReceipt.receipt_id==receipt_id)).scalar_one_or_none()


def reliability_analysis_receipt_metadata(r: ReliabilityAnalysisReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"polyglotReceiptId":r.polyglot_receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"runtime":r.runtime,"operation":r.operation,"analysisKind":r.analysis_kind,"modelKind":r.model_kind,"sampleCount":r.sample_count,"eventCount":r.event_count,"horizon":r.horizon,"requestFingerprint":r.request_fingerprint,"metrics":r.metrics_json or {},"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"createdAt":r.created_at.isoformat()}

def list_reliability_analysis_receipts(db: Session,user_key:str,limit:int=100):
    return [reliability_analysis_receipt_metadata(r) for r in db.scalars(select(ReliabilityAnalysisReceipt).where(ReliabilityAnalysisReceipt.user_key==user_key).order_by(ReliabilityAnalysisReceipt.created_at.desc()).limit(limit)).all()]

def get_reliability_analysis_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(ReliabilityAnalysisReceipt).where(ReliabilityAnalysisReceipt.user_key==user_key,ReliabilityAnalysisReceipt.receipt_id==receipt_id)).scalar_one_or_none()
