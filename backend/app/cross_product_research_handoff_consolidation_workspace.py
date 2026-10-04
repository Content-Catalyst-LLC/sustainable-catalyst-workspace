from __future__ import annotations
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .cross_product_research_handoff_consolidation import acceptance_contract, compatibility, destination_profiles, intent_compatibility, manifest, operation_index, plan, runtime_profile, snapshot, validate
router=APIRouter(tags=["cross-product-research-handoff-consolidation"])
@router.get("/v1/cross-product-research-handoff-consolidation")
def profile()->Dict[str,Any]: return runtime_profile()
@router.get("/v1/cross-product-research-handoff-consolidation/destinations")
def destinations()->Dict[str,Any]: return destination_profiles()
@router.get("/v1/cross-product-research-handoff-consolidation/operations")
def operations()->Dict[str,Any]: return operation_index()
@router.get("/v1/cross-product-research-handoff-consolidation/compatibility")
def compatible()->Dict[str,Any]: return compatibility()
@router.get("/v1/cross-product-research-handoff-consolidation/validate")
def validation()->Dict[str,Any]: return validate()
@router.post("/v1/cross-product-research-handoff-consolidation/evaluate")
def evaluate(payload:Dict[str,Any])->Dict[str,Any]:
    kind=str(payload.get("kind") or ""); body=payload.get("payload") if isinstance(payload.get("payload"),dict) else payload
    try:
        if kind=="intent-compatibility": return intent_compatibility(body)
        if kind=="plan": return plan(body)
        if kind=="manifest": return manifest(body)
        if kind=="acceptance-contract": return acceptance_contract(body)
        if kind=="snapshot": return snapshot(body)
        raise ValueError("unsupported evaluation kind")
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
