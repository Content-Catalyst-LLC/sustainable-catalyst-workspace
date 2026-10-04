from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .unified_research_session_runtime import execute, operation_index, runtime_profile
router=APIRouter(tags=['unified-research-session'])
@router.get('/v1/unified-research-session-runtime')
def profile()->Dict[str,Any]: return runtime_profile()
@router.get('/v1/unified-research-session-runtime/operations')
def operations()->Dict[str,Any]: return operation_index()
@router.post('/v1/unified-research-session-runtime/execute')
def run(payload:Dict[str,Any])->Dict[str,Any]:
    operation=str(payload.get('operation') or '')
    body=payload.get('payload') if isinstance(payload.get('payload'),dict) else payload
    try: return execute(operation,body)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
