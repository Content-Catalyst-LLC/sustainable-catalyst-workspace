from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .portable_research_workspace_recovery import (
    build_package, compatibility, manifest, migration_drill,
    operation_index, restore_plan, runtime_profile, snapshot, validate, verify,
)

router = APIRouter(tags=["portable-research-workspace-recovery"])

@router.get("/v1/portable-research-workspace-recovery")
def profile() -> Dict[str, Any]:
    return runtime_profile()

@router.get("/v1/portable-research-workspace-recovery/operations")
def operations() -> Dict[str, Any]:
    return operation_index()

@router.get("/v1/portable-research-workspace-recovery/compatibility")
def compatible() -> Dict[str, Any]:
    return compatibility()

@router.post("/v1/portable-research-workspace-recovery/evaluate")
def evaluate(payload: Dict[str, Any]) -> Dict[str, Any]:
    kind = str(payload.get("kind") or "").strip()
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    try:
        if kind == "validate": return validate(body)
        if kind == "manifest": return manifest(body)
        if kind == "package": return build_package(body)
        if kind == "verify": return verify(body)
        if kind == "restore-plan": return restore_plan(body)
        if kind == "migration-drill": return migration_drill(body)
        if kind == "snapshot": return snapshot(body)
        raise ValueError("unsupported evaluation kind")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
