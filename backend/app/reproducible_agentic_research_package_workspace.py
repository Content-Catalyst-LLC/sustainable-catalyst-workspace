from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .reproducible_agentic_research_package_runtime import execute, operation_index, runtime_profile
router=APIRouter(tags=["reproducible-agentic-research-package"])

@router.get("/v1/reproducible-agentic-research-package-runtime")
def profile()->Dict[str,Any]: return runtime_profile()

@router.get("/v1/reproducible-agentic-research-package-runtime/operations")
def operations()->Dict[str,Any]: return operation_index()

@router.post("/v1/reproducible-agentic-research-package-runtime/execute")
def run(payload:Dict[str,Any])->Dict[str,Any]:
    op=str(payload.get("operation") or "")
    body=payload.get("payload") if isinstance(payload.get("payload"),dict) else payload
    try: return execute(op,body)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
