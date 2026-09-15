from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


def _load_service(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_JULIA_RUNTIME_TOKEN", "cache-test-token")
    spec = importlib.util.spec_from_file_location(
        "sc_julia_cache_repair_service",
        Path(__file__).parents[1] / "julia-runtime" / "service.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_julia_runtime_uses_bounded_writable_cache_depot(monkeypatch, tmp_path):
    service = _load_service(monkeypatch)
    cache = tmp_path / "sc-julia-depot"
    service.WRITABLE_DEPOT = cache
    service.JULIA_BIN = "/usr/local/julia/bin/julia"
    service.JULIA_PROJECT = Path("/opt/julia-depot/environments/v1.11")
    monkeypatch.setattr(service.Path, "is_file", lambda self: True)

    captured = {}

    class Completed:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs["env"]
        Path(cmd[-1]).write_text(
            '{"ok":true,"schema":"sc-workspace-julia-runtime-result/1.0",'
            '"runtime":"julia-simulation-numerical",'
            '"operation":"workspace.polyglot.julia.ode-linear-rk4",'
            '"boundedOperationsOnly":true,"arbitraryCodeExecution":false,'
            '"result":{"kind":"linear-ode","solver":"rk4","steps":10,'
            '"finalState":[0.3678797744],"metrics":{}}}'
        )
        return Completed()

    monkeypatch.setattr(service.subprocess, "run", fake_run)
    client = TestClient(service.app)
    envelope = {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "language": "julia",
        "runtime": "julia-simulation-numerical",
        "operation": "workspace.polyglot.julia.ode-linear-rk4",
        "arbitraryCodeExecution": False,
        "payload": {
            "A": [[-1.0]],
            "initialState": [1.0],
            "forcing": [0.0],
            "dt": 0.1,
            "steps": 10,
        },
    }
    r = client.post(
        "/v1/execute",
        headers={"Authorization": "Bearer cache-test-token"},
        json=envelope,
    )
    assert r.status_code == 200, r.text
    assert cache.is_dir()
    assert captured["env"]["JULIA_DEPOT_PATH"] == f"{cache}:/opt/julia-depot"
    assert captured["env"]["JULIA_PKG_PRECOMPILE_AUTO"] == "0"
    assert "--pkgimages=no" in captured["cmd"]
    assert "--project=/opt/julia-depot/environments/v1.11" in captured["cmd"]
    assert captured["cmd"][0] == "/usr/local/julia/bin/julia"


def test_julia_health_reports_cache_security_contract(monkeypatch):
    service = _load_service(monkeypatch)
    monkeypatch.setattr(service.Path, "is_file", lambda self: True)
    client = TestClient(service.app)
    d = client.get("/health").json()
    assert d["immutableDepot"] == "/opt/julia-depot"
    assert d["writableCacheDepot"] == "/tmp/sc-julia-depot"
    assert d["runtimeProject"] == "/opt/julia-depot/environments/v1.11"
    assert d["packageImagesEnabled"] is False
