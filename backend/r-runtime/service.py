from __future__ import annotations

import hmac
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException

SERVICE = "Sustainable Catalyst Workspace R Statistical Runtime"
SERVICE_VERSION = "2.13.0"
RUNTIME = "r-statistical-econometric"
RUNNER = Path("/app/runner.R")
PROVIDER_RUNNER = Path("/app/provider_runner.R")
ADAPTER_VERSION = "3.9.1"
PROVIDER_KEY = "catalystanalyticsr"
PROVIDER_VERSION = "2.2.0"
CORE_PROVIDER_CONTRACT = "sc.core.analytical-runtime-provider.v1"
DIAGNOSTICS_CONTRACT = "sc.analytics-r.statistical-diagnostics-validation.v1"
TOKEN = os.getenv("SC_WORKSPACE_R_RUNTIME_TOKEN", "").strip()
TIMEOUT = max(1.0, min(float(os.getenv("SC_WORKSPACE_R_TIMEOUT_SECONDS", "40")), 120.0))
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_R_MAX_PAYLOAD_BYTES", str(10 * 1024 * 1024))), 25 * 1024 * 1024))

OPERATIONS = {
    "workspace.polyglot.r.describe",
    "workspace.polyglot.r.t-test",
    "workspace.polyglot.r.correlation",
    "workspace.polyglot.r.linear-model",
    "workspace.polyglot.r.logistic-model",
    "workspace.polyglot.r.anova",
    "workspace.polyglot.r.arima",
    "workspace.polyglot.r.econometric-ols",
}

app = FastAPI(title=SERVICE, version=SERVICE_VERSION, docs_url=None, redoc_url=None)


def _require_auth(authorization: str | None) -> None:
    if not TOKEN:
        raise HTTPException(status_code=503, detail="R runtime service credential is not configured")
    expected = f"Bearer {TOKEN}"
    if not authorization or not hmac.compare_digest(authorization.strip(), expected):
        raise HTTPException(status_code=401, detail="R runtime service authentication failed")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": SERVICE,
        "version": SERVICE_VERSION,
        "runtime": RUNTIME,
        "engine": "R",
        "operations": sorted(OPERATIONS),
        "boundedOperationsOnly": True,
        "arbitraryCodeExecution": False,
        "clientSuppliedPackagesAllowed": False,
        "clientSuppliedRuntimeUrlsAllowed": False,
        "catalystAnalyticsRProviderInstalled": True,
        "catalystAnalyticsRProviderKey": PROVIDER_KEY,
        "catalystAnalyticsRProviderVersion": PROVIDER_VERSION,
        "catalystAnalyticsRCoreContract": CORE_PROVIDER_CONTRACT,
        "catalystAnalyticsRDiagnosticsContract": DIAGNOSTICS_CONTRACT,
        "catalystAnalyticsRStatisticalDiagnosticsValidation": True,
        "catalystAnalyticsRAdapterVersion": ADAPTER_VERSION,
    }


@app.post("/v1/execute")
def execute(envelope: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    if envelope.get("schema") != "sc-workspace-polyglot-execution-envelope/1.0":
        raise HTTPException(status_code=400, detail="Unsupported polyglot execution envelope")
    if envelope.get("language") != "r":
        raise HTTPException(status_code=400, detail="R runtime only accepts language=r")
    operation = str(envelope.get("operation") or "")
    if operation not in OPERATIONS:
        raise HTTPException(status_code=400, detail="R operation is not registered")
    if envelope.get("arbitraryCodeExecution") is not False:
        raise HTTPException(status_code=400, detail="Arbitrary-code execution must remain disabled")
    payload = envelope.get("payload") or {}
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")
    raw = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="R runtime payload limit exceeded")

    in_path = out_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="sc-r-in-", suffix=".json", dir="/tmp", delete=False) as src:
            src.write(raw)
            in_path = src.name
        with tempfile.NamedTemporaryFile(prefix="sc-r-out-", suffix=".json", dir="/tmp", delete=False) as dst:
            out_path = dst.name
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
        completed = subprocess.run(
            ["/usr/bin/Rscript", "--vanilla", str(RUNNER), in_path, out_path],
            cwd="/app",
            env=env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
            shell=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "R operation failed").strip().replace("\n", " ")[:1200]
            raise HTTPException(status_code=422, detail=f"R operation failed: {detail}")
        try:
            body = json.loads(Path(out_path).read_text(encoding="utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=502, detail="R runtime produced invalid JSON") from exc
        if not isinstance(body, dict) or body.get("ok") is not True:
            raise HTTPException(status_code=422, detail="R runtime operation did not complete successfully")
        return body
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="R runtime operation exceeded its bounded timeout") from exc
    finally:
        for path in (in_path, out_path):
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass



def _run_provider(envelope: dict[str, Any], action: str) -> dict[str, Any]:
    payload = dict(envelope)
    payload["action"] = action
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="Catalyst Analytics R provider payload limit exceeded")
    in_path = out_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="sc-car-in-", suffix=".json", dir="/tmp", delete=False) as src:
            src.write(raw)
            in_path = src.name
        with tempfile.NamedTemporaryFile(prefix="sc-car-out-", suffix=".json", dir="/tmp", delete=False) as dst:
            out_path = dst.name
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
        completed = subprocess.run(
            ["/usr/bin/Rscript", "--vanilla", str(PROVIDER_RUNNER), in_path, out_path],
            cwd="/app",
            env=env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
            shell=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "Catalyst Analytics R provider action failed").strip().replace("\n", " ")[:1600]
            raise HTTPException(status_code=422, detail=f"Catalyst Analytics R provider action failed: {detail}")
        try:
            body = json.loads(Path(out_path).read_text(encoding="utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Catalyst Analytics R provider produced invalid JSON") from exc
        if not isinstance(body, dict) or body.get("ok") is not True:
            raise HTTPException(status_code=422, detail="Catalyst Analytics R provider action did not complete successfully")
        return body
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Catalyst Analytics R provider action exceeded its bounded timeout") from exc
    finally:
        for path in (in_path, out_path):
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass


@app.get("/v1/providers/catalystanalyticsr")
def catalyst_analytics_r_provider(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    return _run_provider({}, "manifest")


@app.post("/v1/providers/catalystanalyticsr/validate")
def validate_catalyst_analytics_r_provider(envelope: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    return _run_provider(envelope, "validate")


@app.post("/v1/providers/catalystanalyticsr/execute")
def execute_catalyst_analytics_r_provider(envelope: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    return _run_provider(envelope, "execute")
