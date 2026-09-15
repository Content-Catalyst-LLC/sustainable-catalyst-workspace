from pathlib import Path
import importlib.util
from types import SimpleNamespace
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def _load(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_JULIA_RUNTIME_TOKEN", "test-secret")
    monkeypatch.setenv("SC_WORKSPACE_JULIA_BIN", "/usr/local/julia/bin/julia")
    spec = importlib.util.spec_from_file_location("sc_julia_runtime_path_repair", ROOT / "julia-runtime/service.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_official_julia_binary_path_and_runtime_path(monkeypatch):
    module = _load(monkeypatch)
    assert module.JULIA_BIN == "/usr/local/julia/bin/julia"
    dockerfile = (ROOT / "julia-runtime/Dockerfile").read_text()
    assert '/usr/local/julia/bin' in dockerfile
    service = (ROOT / "julia-runtime/service.py").read_text()
    assert '"PATH": "/usr/local/julia/bin:/usr/local/bin:/usr/bin:/bin"' in service


def test_execute_uses_fixed_julia_path(monkeypatch, tmp_path):
    module = _load(monkeypatch)
    monkeypatch.setattr(module.Path, "is_file", lambda self: str(self) == "/usr/local/julia/bin/julia")

    def fake_run(cmd, **kwargs):
        assert cmd[0] == "/usr/local/julia/bin/julia"
        assert "--startup-file=no" in cmd
        assert "--history-file=no" in cmd
        assert "--project=/opt/julia-depot/environments/v1.11" in cmd
        assert "--pkgimages=no" in cmd
        assert "/app/runner.jl" in cmd
        assert kwargs["shell"] is False
        assert kwargs["env"]["PATH"].startswith("/usr/local/julia/bin:")
        Path(cmd[-1]).write_text('{"ok":true,"schema":"sc-workspace-julia-runtime-result/1.0","runtime":"julia-simulation-numerical","operation":"workspace.polyglot.julia.ode-linear-rk4","boundedOperationsOnly":true,"arbitraryCodeExecution":false,"result":{"kind":"linear-ode","solver":"rk4","steps":10,"finalState":[0.3678797744],"metrics":{}}}')
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    envelope = {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "2.14.0",
        "jobId": "job-test",
        "language": "julia",
        "operation": "workspace.polyglot.julia.ode-linear-rk4",
        "payload": {"A": [[-1.0]], "initialState": [1.0], "forcing": [0.0], "dt": 0.1, "steps": 10},
        "arbitraryCodeExecution": False,
    }
    with TestClient(module.app) as client:
        response = client.post("/v1/execute", json=envelope, headers={"Authorization": "Bearer test-secret"})
    assert response.status_code == 200
    assert response.json()["result"]["solver"] == "rk4"


def test_missing_julia_binary_is_clear_503(monkeypatch):
    module = _load(monkeypatch)
    monkeypatch.setattr(module.Path, "is_file", lambda self: False)
    envelope = {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "2.14.0",
        "jobId": "job-test",
        "language": "julia",
        "operation": "workspace.polyglot.julia.ode-linear-rk4",
        "payload": {"A": [[-1.0]], "initialState": [1.0], "dt": 0.1, "steps": 10},
        "arbitraryCodeExecution": False,
    }
    with TestClient(module.app) as client:
        response = client.post("/v1/execute", json=envelope, headers={"Authorization": "Bearer test-secret"})
    assert response.status_code == 503
    assert "/usr/local/julia/bin/julia" in response.json()["detail"]
