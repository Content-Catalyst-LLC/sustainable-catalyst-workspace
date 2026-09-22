from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import AnalyticalProviderReceipt
from .utils import sha256_hex

PROVIDER_KEY = "catalystanalyticsr"
PROVIDER_VERSION = "2.2.0"
CORE_CONTRACT = "sc.core.analytical-runtime-provider.v1"
DIAGNOSTICS_CONTRACT = "sc.analytics-r.statistical-diagnostics-validation.v1"
ADAPTER_VERSION = "3.9.1"
ENVELOPE_TYPE = "catalyst_workspace_core_analytical_execution"
RESULT_TYPE = "catalyst_analytics_r_core_result"


def profile() -> dict[str, Any]:
    settings = get_settings()
    return {
        "schema": "sc-workspace-analytical-provider-adapter/1.0",
        "workspaceVersion": settings.service_version,
        "adapterVersion": ADAPTER_VERSION,
        "providerKey": PROVIDER_KEY,
        "providerVersion": PROVIDER_VERSION,
        "coreContract": CORE_CONTRACT,
        "diagnosticsContract": DIAGNOSTICS_CONTRACT,
        "statisticalDiagnosticsValidation": True,
        "runtime": "r",
        "executionHost": "workspace",
        "runtimeConfigured": bool(settings.runtime_r_url.strip()),
        "runtimeTransport": "server-configured-http",
        "runtimeImageInstallation": "build-time",
        "productionFilesystem": "read-only",
        "arbitraryFunctionDispatch": False,
        "arbitraryCodeExecution": False,
        "clientSuppliedRuntimeUrlAllowed": False,
        "clientSuppliedPackagesAllowed": False,
        "workspaceControlsAuthentication": True,
        "workspaceControlsPersistence": True,
        "humanReviewRequired": True,
    }


def _runtime_provider_url(action: str) -> str:
    base = get_settings().runtime_r_url.strip()
    if not base:
        raise HTTPException(status_code=409, detail="Workspace R runtime adapter is not configured")
    if base.endswith("/v1/execute"):
        base = base[: -len("/v1/execute")]
    else:
        base = base.rstrip("/")
    suffix = {
        "manifest": "/v1/providers/catalystanalyticsr",
        "validate": "/v1/providers/catalystanalyticsr/validate",
        "execute": "/v1/providers/catalystanalyticsr/execute",
    }.get(action)
    if not suffix:
        raise HTTPException(status_code=500, detail="Unknown analytical provider action")
    return base + suffix


def _validate_envelope_shape(envelope: dict[str, Any], *, for_execution: bool) -> None:
    if not isinstance(envelope, dict):
        raise HTTPException(status_code=400, detail="Analytical provider envelope must be an object")
    if envelope.get("envelope_type") != ENVELOPE_TYPE:
        raise HTTPException(status_code=400, detail="Unsupported analytical provider envelope type")
    request = envelope.get("request")
    plan = envelope.get("plan")
    boundary = envelope.get("boundary")
    if not isinstance(request, dict) or not isinstance(plan, dict) or not isinstance(boundary, dict):
        raise HTTPException(status_code=400, detail="Analytical provider envelope requires request, plan, and boundary objects")
    if request.get("provider_ref") != PROVIDER_KEY or plan.get("provider_ref") != PROVIDER_KEY:
        raise HTTPException(status_code=400, detail="Analytical provider envelope targets an unsupported provider")
    if request.get("runtime") != "r" or request.get("execution_host") != "workspace":
        raise HTTPException(status_code=400, detail="Catalyst Analytics R must execute through Workspace/R")
    if plan.get("core_contract") != CORE_CONTRACT:
        raise HTTPException(status_code=400, detail="Analytical provider Core contract mismatch")
    if plan.get("runtime") != "r" or plan.get("execution_host") != "workspace":
        raise HTTPException(status_code=400, detail="Analytical provider execution-plan boundary mismatch")
    if boundary.get("workspace_controls_execution") is not True:
        raise HTTPException(status_code=400, detail="Workspace execution authority is required")
    if request.get("boundary", {}).get("core_executes_provider") is not False:
        raise HTTPException(status_code=400, detail="Core may not execute the analytical provider")
    selected = str(plan.get("selected_method_ref") or "")
    allowed = plan.get("allowed_method_refs") or []
    if not selected or not isinstance(allowed, list) or selected not in allowed:
        raise HTTPException(status_code=400, detail="Provider plan method is not governed by its allowed-method registry")
    if for_execution:
        args = envelope.get("resolved_method_args")
        if not isinstance(args, dict):
            raise HTTPException(status_code=400, detail="resolved_method_args must be a Workspace-resolved object")
        if len(args) > 64:
            raise HTTPException(status_code=413, detail="resolved_method_args exceeds the Workspace bound")
    raw = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    if len(raw) > get_settings().polyglot_max_payload_bytes:
        raise HTTPException(status_code=413, detail="Analytical provider envelope payload limit exceeded")


def _transport(action: str, envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = get_settings()
    token = settings.runtime_r_token.strip()
    if not token:
        raise HTTPException(status_code=409, detail="Workspace R runtime credential is not configured")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    try:
        if action == "manifest":
            response = httpx.get(_runtime_provider_url(action), headers=headers, timeout=min(settings.polyglot_timeout_seconds, 15.0))
        else:
            response = httpx.post(
                _runtime_provider_url(action),
                json=envelope or {},
                headers={**headers, "Content-Type": "application/json"},
                timeout=settings.polyglot_timeout_seconds,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Catalyst Analytics R provider transport failed: {exc.__class__.__name__}") from exc
    if not (200 <= response.status_code < 300):
        detail = response.text[:1200]
        raise HTTPException(status_code=502, detail=f"Catalyst Analytics R provider returned HTTP {response.status_code}: {detail}")
    try:
        body = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Catalyst Analytics R provider returned invalid JSON") from exc
    if not isinstance(body, dict) or body.get("ok") is not True:
        raise HTTPException(status_code=502, detail="Catalyst Analytics R provider returned an unsuccessful response")
    return body


def manifest() -> dict[str, Any]:
    body = _transport("manifest")
    provider = body.get("provider") if isinstance(body.get("provider"), dict) else {}
    if provider.get("provider_key") != PROVIDER_KEY or provider.get("provider_version") != PROVIDER_VERSION:
        raise HTTPException(status_code=502, detail="Catalyst Analytics R runtime image provider identity mismatch")
    if provider.get("core_contract") != CORE_CONTRACT:
        raise HTTPException(status_code=502, detail="Catalyst Analytics R runtime image Core contract mismatch")
    if provider.get("diagnostics_contract") != DIAGNOSTICS_CONTRACT:
        raise HTTPException(status_code=502, detail="Catalyst Analytics R runtime image diagnostics contract mismatch")
    return body


def validate(envelope: dict[str, Any]) -> dict[str, Any]:
    _validate_envelope_shape(envelope, for_execution=False)
    return _transport("validate", envelope)


def execute(db: Session, user_key: str, envelope: dict[str, Any]) -> dict[str, Any]:
    _validate_envelope_shape(envelope, for_execution=True)
    outbound = copy.deepcopy(envelope)
    request = outbound["request"]
    plan = outbound["plan"]
    request_key = str(request.get("request_key") or "")[:255]
    if not request_key:
        raise HTTPException(status_code=400, detail="Analytical provider request_key is required")
    receipt_id = f"apr_{uuid4().hex}"
    execution_ref = f"workspace-analytics-r:{receipt_id}"
    environment_ref = f"workspace-r-env:{receipt_id}"
    result_ref = f"analytics-r-result:{receipt_id}"
    outbound["external_execution_ref"] = execution_ref
    outbound["environment_ref"] = environment_ref
    outbound["result_ref"] = result_ref
    request_fingerprint = sha256_hex(json.dumps(outbound, sort_keys=True, separators=(",", ":"), default=str))
    started = datetime.now(timezone.utc)
    status = "failed"
    result: dict[str, Any] = {}
    result_fingerprint = ""
    error = ""
    try:
        result = _transport("execute", outbound)
        core_result = result.get("core_result") if isinstance(result.get("core_result"), dict) else {}
        if core_result.get("result_type") != RESULT_TYPE:
            raise HTTPException(status_code=502, detail="Catalyst Analytics R provider result contract mismatch")
        if core_result.get("core_contract") != CORE_CONTRACT or core_result.get("provider_ref") != PROVIDER_KEY:
            raise HTTPException(status_code=502, detail="Catalyst Analytics R provider result identity mismatch")
        status = "completed"
        result_fingerprint = sha256_hex(json.dumps(result, sort_keys=True, separators=(",", ":"), default=str))
    except HTTPException as exc:
        error = str(exc.detail)[:2000]
        raise
    finally:
        receipt = AnalyticalProviderReceipt(
            user_key=user_key,
            receipt_id=receipt_id,
            request_key=request_key,
            provider_key=PROVIDER_KEY,
            provider_version=PROVIDER_VERSION,
            core_contract=CORE_CONTRACT,
            analysis_type=str(request.get("analysis_type") or "")[:128],
            method_ref=str(plan.get("selected_method_ref") or "")[:160],
            status=status,
            external_execution_ref=execution_ref,
            environment_ref=environment_ref,
            request_fingerprint=request_fingerprint,
            result_fingerprint=result_fingerprint,
            request_json=outbound,
            result_json=result,
            error=error,
            started_at=started,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(receipt)
        db.commit()
    return {"ok": True, "receipt": receipt_metadata(receipt), "providerResult": result}


def receipt_metadata(row: AnalyticalProviderReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "requestKey": row.request_key,
        "providerKey": row.provider_key,
        "providerVersion": row.provider_version,
        "coreContract": row.core_contract,
        "analysisType": row.analysis_type,
        "methodRef": row.method_ref,
        "status": row.status,
        "externalExecutionRef": row.external_execution_ref,
        "environmentRef": row.environment_ref,
        "requestFingerprint": row.request_fingerprint,
        "resultFingerprint": row.result_fingerprint,
        "error": row.error,
        "startedAt": row.started_at.isoformat() if row.started_at else None,
        "completedAt": row.completed_at.isoformat() if row.completed_at else None,
    }


def list_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(AnalyticalProviderReceipt)
        .where(AnalyticalProviderReceipt.user_key == user_key)
        .order_by(AnalyticalProviderReceipt.started_at.desc())
        .limit(limit)
    ).all()
    return [receipt_metadata(row) for row in rows]


def get_receipt(db: Session, user_key: str, receipt_id: str) -> AnalyticalProviderReceipt | None:
    return db.execute(
        select(AnalyticalProviderReceipt).where(
            AnalyticalProviderReceipt.user_key == user_key,
            AnalyticalProviderReceipt.receipt_id == receipt_id,
        )
    ).scalar_one_or_none()
