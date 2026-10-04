from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .research_os_runtime_registry import authority_matrix, compatibility, discover_capabilities, discover_operations, get_runtime, list_runtimes, operation_index, runtime_profile, snapshot, validate

router = APIRouter(tags=["research-os-runtime-registry"])

@router.get("/v1/research-os-runtime-registry")
def profile() -> Dict[str, Any]: return runtime_profile()

@router.get("/v1/research-os-runtime-registry/runtimes")
def runtimes() -> Dict[str, Any]: return list_runtimes()

@router.get("/v1/research-os-runtime-registry/operations")
def operations() -> Dict[str, Any]: return operation_index()

@router.get("/v1/research-os-runtime-registry/authority")
def authority() -> Dict[str, Any]: return authority_matrix()

@router.get("/v1/research-os-runtime-registry/compatibility")
def compatible() -> Dict[str, Any]: return compatibility()

@router.get("/v1/research-os-runtime-registry/validate")
def validation() -> Dict[str, Any]: return validate()

@router.post("/v1/research-os-runtime-registry/discover")
def discover(payload: Dict[str, Any]) -> Dict[str, Any]:
    kind = str(payload.get("kind") or "").strip()
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        if kind == "runtime": return get_runtime(body)
        if kind == "capability": return discover_capabilities(body)
        if kind == "operation": return discover_operations(body)
        if kind == "snapshot": return snapshot(body)
        raise ValueError("unsupported discovery kind")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
