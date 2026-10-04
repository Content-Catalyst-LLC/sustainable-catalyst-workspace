from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .production_certification_agentic_runtime import (
    certification_report,
    execute,
    operation_index,
    runtime_profile,
)

router = APIRouter(tags=["production-certification-agentic"])

@router.get("/v1/production-certification-agentic-runtime")
def profile() -> Dict[str, Any]:
    return runtime_profile()

@router.get("/v1/production-certification-agentic-runtime/operations")
def operations() -> Dict[str, Any]:
    return operation_index()

@router.get("/v1/production-certification-agentic-runtime/report")
def report() -> Dict[str, Any]:
    return certification_report()

@router.post("/v1/production-certification-agentic-runtime/execute")
def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    operation = str(payload.get("operation") or "")
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        return execute(operation, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
