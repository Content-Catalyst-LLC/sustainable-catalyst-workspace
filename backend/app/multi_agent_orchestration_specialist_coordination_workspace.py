from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .multi_agent_orchestration_specialist_coordination_runtime import execute, operation_index, runtime_profile

router = APIRouter(tags=["multi-agent-orchestration-specialist-coordination"])


@router.get("/v1/multi-agent-orchestration-specialist-coordination-runtime")
def multi_agent_runtime_profile() -> Dict[str, Any]:
    return runtime_profile()


@router.get("/v1/multi-agent-orchestration-specialist-coordination-runtime/operations")
def multi_agent_runtime_operations() -> Dict[str, Any]:
    return operation_index()


@router.post("/v1/multi-agent-orchestration-specialist-coordination-runtime/execute")
def multi_agent_runtime_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    operation = str(payload.get("operation") or "")
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        return execute(operation, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
