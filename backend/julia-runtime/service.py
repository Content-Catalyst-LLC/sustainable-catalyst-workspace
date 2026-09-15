from __future__ import annotations

import hmac
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException

SERVICE = "Sustainable Catalyst Workspace Julia Numerical Runtime"
SERVICE_VERSION = "2.14.0"
RUNTIME = "julia-simulation-numerical"
RUNNER = Path("/app/runner.jl")
IMMUTABLE_DEPOT = Path("/opt/julia-depot")
WRITABLE_DEPOT = Path("/tmp/sc-julia-depot")
JULIA_PROJECT = Path("/opt/julia-depot/environments/v1.11")
JULIA_BIN = os.getenv("SC_WORKSPACE_JULIA_BIN", "/usr/local/julia/bin/julia").strip() or "/usr/local/julia/bin/julia"
TOKEN = os.getenv("SC_WORKSPACE_JULIA_RUNTIME_TOKEN", "").strip()
TIMEOUT = max(1.0, min(float(os.getenv("SC_WORKSPACE_JULIA_TIMEOUT_SECONDS", "60")), 180.0))
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_JULIA_MAX_PAYLOAD_BYTES", str(10 * 1024 * 1024))), 25 * 1024 * 1024))

OPERATIONS = {
    "workspace.polyglot.julia.ode-linear-rk4",
    "workspace.polyglot.julia.lotka-volterra",
    "workspace.polyglot.julia.monte-carlo-normal",
    "workspace.polyglot.julia.quadratic-optimize",
    "workspace.polyglot.julia.eigen-analysis",
    "workspace.polyglot.julia.integrate-series",
    "workspace.polyglot.julia.polynomial-roots",
    "workspace.polyglot.julia.parameter-sweep",
}

app = FastAPI(title=SERVICE, version=SERVICE_VERSION, docs_url=None, redoc_url=None)

def _require_auth(authorization: str | None) -> None:
    if not TOKEN:
        raise HTTPException(status_code=503, detail="Julia runtime service credential is not configured")
    expected = f"Bearer {TOKEN}"
    if not authorization or not hmac.compare_digest(authorization.strip(), expected):
        raise HTTPException(status_code=401, detail="Julia runtime service authentication failed")

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True, "service": SERVICE, "version": SERVICE_VERSION, "runtime": RUNTIME, "engine": "Julia",
        "operations": sorted(OPERATIONS), "boundedOperationsOnly": True, "arbitraryCodeExecution": False,
        "clientSuppliedPackagesAllowed": False, "clientSuppliedRuntimeUrlsAllowed": False,
        "juliaExecutable": JULIA_BIN, "juliaExecutableAvailable": Path(JULIA_BIN).is_file(),
        "immutableDepot": str(IMMUTABLE_DEPOT), "writableCacheDepot": str(WRITABLE_DEPOT),
        "runtimeProject": str(JULIA_PROJECT), "packageImagesEnabled": False,
    }

@app.post("/v1/execute")
def execute(envelope: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    if envelope.get("schema") != "sc-workspace-polyglot-execution-envelope/1.0":
        raise HTTPException(status_code=400, detail="Unsupported polyglot execution envelope")
    if envelope.get("language") != "julia":
        raise HTTPException(status_code=400, detail="Julia runtime only accepts language=julia")
    operation = str(envelope.get("operation") or "")
    if operation not in OPERATIONS:
        raise HTTPException(status_code=400, detail="Julia operation is not registered")
    if envelope.get("arbitraryCodeExecution") is not False:
        raise HTTPException(status_code=400, detail="Arbitrary-code execution must remain disabled")
    payload = envelope.get("payload") or {}
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")
    raw = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="Julia runtime payload limit exceeded")
    if not Path(JULIA_BIN).is_file():
        raise HTTPException(status_code=503, detail=f"Julia executable is unavailable: {JULIA_BIN}")
    in_path = out_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="sc-julia-in-", suffix=".json", dir="/tmp", delete=False) as src:
            src.write(raw); in_path = src.name
        with tempfile.NamedTemporaryFile(prefix="sc-julia-out-", suffix=".json", dir="/tmp", delete=False) as dst:
            out_path = dst.name
        WRITABLE_DEPOT.mkdir(parents=True, exist_ok=True)
        env = {
            "PATH": "/usr/local/julia/bin:/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "JULIA_NUM_THREADS": "2",
            "JULIA_DEPOT_PATH": f"{WRITABLE_DEPOT}:{IMMUTABLE_DEPOT}",
            "JULIA_PKG_PRECOMPILE_AUTO": "0",
        }
        completed = subprocess.run(
            [
                JULIA_BIN,
                "--startup-file=no",
                "--history-file=no",
                f"--project={JULIA_PROJECT}",
                "--pkgimages=no",
                str(RUNNER),
                in_path,
                out_path,
            ],
            cwd="/app", env=env, capture_output=True, text=True, timeout=TIMEOUT, check=False, shell=False,
        )
        if completed.returncode != 0:
            raise HTTPException(status_code=422, detail=f"Julia runtime operation failed: {completed.stderr[-1200:]}")
        result = json.loads(Path(out_path).read_text())
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise HTTPException(status_code=422, detail="Julia runtime returned an invalid result")
        return result
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Julia runtime operation exceeded its execution timeout") from exc
    finally:
        for path in (in_path, out_path):
            if path:
                try: Path(path).unlink(missing_ok=True)
                except OSError: pass
