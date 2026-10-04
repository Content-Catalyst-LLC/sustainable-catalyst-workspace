from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .integrated_research_os_runtime import execute, operation_index, runtime_profile

router = APIRouter(tags=["integrated-research-os"])

@router.get("/v1/integrated-research-os-runtime")
def profile() -> Dict[str, Any]:
    return runtime_profile()

@router.get("/v1/integrated-research-os-runtime/operations")
def operations() -> Dict[str, Any]:
    return operation_index()

@router.post("/v1/integrated-research-os-runtime/execute")
def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    operation = str(payload.get("operation") or "")
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        return execute(operation, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
