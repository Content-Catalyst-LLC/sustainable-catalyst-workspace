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
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import PolyglotExecutionReceipt
from .object_store import store_artifact
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
    RuntimeSpec("r", "r-scientific-adapter", "server-configured-http", (
        "workspace.polyglot.r.statistics", "workspace.polyglot.r.model", "workspace.polyglot.r.visualize",
    ), "Server-configured R runtime adapter for statistical research workflows."),
    RuntimeSpec("julia", "julia-scientific-adapter", "server-configured-http", (
        "workspace.polyglot.julia.numerical", "workspace.polyglot.julia.simulation", "workspace.polyglot.julia.optimization",
    ), "Server-configured Julia runtime adapter for numerical modeling and simulation."),
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
            "interchange": {"schema": "sc-workspace-arrow-compatible-table/1.0", "formats": ["records-json", "arrow-schema-json"]},
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
    result_doc={"schema":"sc-workspace-polyglot-result/1.0","language":language,"operation":row.operation,"result":result}
    raw=json.dumps(result_doc,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
    if len(raw)>get_settings().compute_max_result_bytes:
        raise HTTPException(status_code=413, detail="Polyglot result byte limit exceeded")
    artifact=store_artifact(db,row.user_key,ArtifactStoreRequest(
        projectId=row.project_id or "",filename=f"polyglot-{language}-{row.job_id}.json",mediaType="application/json",contentBase64=__import__('base64').b64encode(raw).decode(),metadata={"language":language,"operation":row.operation,"jobId":row.job_id}
    ))
    run_id=str(((row.payload or {}).get("executionRunId") or "")).strip()
    if run_id:
        try:
            store_run_output(db,row.user_key,run_id,ExecutionRunOutputRequest(role="polyglot-result",artifactId=artifact.artifact_id,mediaType="application/json",sha256=artifact.sha256,bytes=artifact.bytes,metadata={"language":language,"operation":row.operation}))
        except Exception: pass
    finished=datetime.now(timezone.utc)
    receipt=PolyglotExecutionReceipt(
        receipt_id=f"pgr_{uuid4().hex}", user_key=row.user_key, job_id=row.job_id, execution_run_id=run_id,
        language=language, runtime=RUNTIME_BY_LANGUAGE[language].runtime, operation=row.operation,
        request_fingerprint=row.request_fingerprint, result_artifact_id=artifact.artifact_id,
        result_sha256=artifact.sha256, result_bytes=artifact.bytes,
        transport=RUNTIME_BY_LANGUAGE[language].transport, status="succeeded",
        started_at=started, finished_at=finished, details_json={"exchangeSchema":"sc-workspace-arrow-compatible-table/1.0","serverConfiguredOnly":True,"arbitraryCodeExecution":False}
    )
    db.add(receipt); db.flush()
    if progress_callback: progress_callback(95,{"stage":"result-persisted","artifactId":artifact.artifact_id})
    return {"schema":"sc-workspace-job-result/1.0","polyglot":result_doc,"resultArtifactId":artifact.artifact_id,"receiptId":receipt.receipt_id,"resultSha256":artifact.sha256}


def receipt_metadata(r: PolyglotExecutionReceipt) -> dict[str, Any]:
    return {"receiptId":r.receipt_id,"jobId":r.job_id,"executionRunId":r.execution_run_id,"language":r.language,"runtime":r.runtime,"operation":r.operation,"requestFingerprint":r.request_fingerprint,"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"resultBytes":r.result_bytes,"transport":r.transport,"status":r.status,"startedAt":r.started_at.isoformat(),"finishedAt":r.finished_at.isoformat(),"details":r.details_json or {}}


def list_receipts(db: Session,user_key:str,limit:int=100) -> list[dict[str,Any]]:
    rows=db.execute(select(PolyglotExecutionReceipt).where(PolyglotExecutionReceipt.user_key==user_key).order_by(PolyglotExecutionReceipt.created_at.desc()).limit(limit)).scalars().all()
    return [receipt_metadata(r) for r in rows]


def get_receipt(db: Session,user_key:str,receipt_id:str):
    return db.execute(select(PolyglotExecutionReceipt).where(PolyglotExecutionReceipt.user_key==user_key,PolyglotExecutionReceipt.receipt_id==receipt_id)).scalar_one_or_none()
