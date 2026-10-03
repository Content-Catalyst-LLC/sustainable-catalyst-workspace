from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .human_governance_approval_intervention_runtime import execute, operation_index, runtime_profile

router = APIRouter(tags=["human-governance-approval-intervention"])


@router.get("/v1/human-governance-approval-intervention-runtime")
def human_governance_runtime_profile() -> Dict[str, Any]:
    return runtime_profile()


@router.get("/v1/human-governance-approval-intervention-runtime/operations")
def human_governance_runtime_operations() -> Dict[str, Any]:
    return operation_index()


@router.post("/v1/human-governance-approval-intervention-runtime/execute")
def human_governance_runtime_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    operation = str(payload.get("operation") or "")
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        return execute(operation, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
