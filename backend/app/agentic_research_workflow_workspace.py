from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .agentic_research_workflow_runtime import (
    REQUEST_SCHEMA,
    RESULT_SCHEMA,
    VERSION,
    execute,
    operation_index,
    runtime_profile,
)

router = APIRouter(tags=["agentic-research-workflow"])


@router.get("/v1/agentic-research-workflow-runtime")
def agentic_research_workflow_profile() -> Dict[str, Any]:
    return runtime_profile()


@router.get("/v1/agentic-research-workflow-runtime/operations")
def agentic_research_workflow_operations() -> Dict[str, Any]:
    return operation_index()


@router.post("/v1/agentic-research-workflow-runtime/execute")
def agentic_research_workflow_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    operation = str(payload.get("operation") or "")
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        return execute(operation, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
