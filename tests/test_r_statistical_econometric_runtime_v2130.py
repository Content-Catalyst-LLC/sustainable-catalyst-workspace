from pathlib import Path
import json

from app.polyglot import RUNTIMES, OPERATION_LANGUAGE

ROOT = Path(__file__).resolve().parents[1]

R_OPS = {
    "workspace.polyglot.r.describe",
    "workspace.polyglot.r.t-test",
    "workspace.polyglot.r.correlation",
    "workspace.polyglot.r.linear-model",
    "workspace.polyglot.r.logistic-model",
    "workspace.polyglot.r.anova",
    "workspace.polyglot.r.arima",
    "workspace.polyglot.r.econometric-ols",
}


def test_version_and_lineage():
    cfg = (ROOT / "backend/app/config.py").read_text()
    assert 'service_version: str = "2.13.0"' in cfg
    dep = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php").read_text()
    assert "const PREVIOUS_RELEASE = '2.12.0';" in dep
    assert "const ROLLBACK_RELEASE = '2.12.0';" in dep


def test_r_runtime_has_eight_bounded_operations():
    spec = next(r for r in RUNTIMES if r.language == "r")
    assert spec.runtime == "r-statistical-econometric"
    assert set(spec.operations) == R_OPS
    assert all(OPERATION_LANGUAGE[x] == "r" for x in R_OPS)


def test_r_sidecar_is_fixed_operation_only():
    service = (ROOT / "backend/r-runtime/service.py").read_text()
    runner = (ROOT / "backend/r-runtime/runner.R").read_text()
    assert 'shell=False' in service
    assert '["/usr/bin/Rscript", "--vanilla", str(RUNNER)' in service
    assert 'OPERATIONS = {' in service
    for unsafe in ("eval(", "exec(", "shell=True"):
        assert unsafe not in service
    for unsafe in ("eval(", "parse(", "system(", "system2(", "source("):
        assert unsafe not in runner
    assert "reformulate(" in runner


def test_r_container_has_independent_sandbox_and_internal_network():
    compose = (ROOT / "backend/docker-compose.example.yml").read_text()
    assert "sc-workspace-r-runtime:" in compose
    assert "build: ./r-runtime" in compose
    assert "internal: true" in compose
    assert "cpus: 1.5" in compose
    assert "mem_limit: 1g" in compose
    assert "pids_limit: 128" in compose
    assert "read_only: true" in compose
    assert "no-new-privileges:true" in compose
    assert "SC_WORKSPACE_RUNTIME_R_URL: ${SC_WORKSPACE_RUNTIME_R_URL:-http://sc-workspace-r-runtime:8090/v1/execute}" in compose


def test_migration_013_and_model_receipt_model():
    mig = (ROOT / "backend/migrations/013_r_statistical_econometric_runtime.sql").read_text()
    model = (ROOT / "backend/app/models.py").read_text()
    assert "workspace_statistical_model_receipts" in mig
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in mig
    assert "class StatisticalModelReceipt" in model
    assert '__tablename__ = "workspace_statistical_model_receipts"' in model


def test_backend_routes_and_wordpress_read_only_proxies():
    main = (ROOT / "backend/app/main.py").read_text()
    php = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    for token in ("/v1/polyglot/runtimes/r/status", "/v1/statistical-model-receipts"):
        assert token in main
    for token in ("backend-r-runtime-status", "backend-statistical-model-receipts"):
        assert token in php


def test_release_contract_is_bounded():
    manifest = json.loads((ROOT / "release-manifest-v2.13.0.json").read_text())
    r = manifest["r_runtime"]
    assert r["operation_count"] == 8
    assert r["internal_only_network"] is True
    assert r["statistical_model_receipts"] is True
    assert r["client_supplied_code_allowed"] is False
    assert r["client_supplied_packages_allowed"] is False
    assert r["client_supplied_runtime_urls_allowed"] is False
    assert r["client_supplied_credentials_allowed"] is False
    assert r["arbitrary_code_execution"] is False


def test_polyglot_receipts_are_explicitly_committed():
    src = (ROOT / "backend/app/polyglot.py").read_text()
    marker = 'db.add(receipt); db.flush()'
    assert marker in src
    assert 'db.commit()' in src[src.index(marker):src.index(marker) + 2600]


def test_deployer_runs_real_r_model_smoke():
    deploy = (ROOT / "scripts/deploy_workspace_backend_v2_13_0_vps.sh").read_text()
    assert "migrations/013_r_statistical_econometric_runtime.sql" in deploy
    assert "workspace.polyglot.r.linear-model" in deploy
    assert "statisticalModelReceiptId" in deploy
    assert "sc-workspace-r-runtime" in deploy
    assert "internal-only network" in deploy


def test_r_service_auth_and_fixed_runner_dispatch(monkeypatch):
    import importlib.util
    import os
    from types import SimpleNamespace
    from fastapi.testclient import TestClient

    monkeypatch.setenv("SC_WORKSPACE_R_RUNTIME_TOKEN", "test-secret")
    spec = importlib.util.spec_from_file_location("sc_r_runtime_service_v2130", ROOT / "backend/r-runtime/service.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    def fake_run(cmd, **kwargs):
        assert cmd[:3] == ["/usr/bin/Rscript", "--vanilla", "/app/runner.R"]
        assert kwargs["shell"] is False
        out_path = Path(cmd[4])
        out_path.write_text('{"ok":true,"schema":"sc-workspace-r-runtime-result/1.0","runtime":"r-statistical-econometric","operation":"workspace.polyglot.r.describe","boundedOperationsOnly":true,"arbitraryCodeExecution":false,"result":{"kind":"describe"}}')
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    envelope = {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "2.13.0",
        "jobId": "job-test",
        "language": "r",
        "operation": "workspace.polyglot.r.describe",
        "payload": {"rows": [{"x": 1}, {"x": 2}]},
        "arbitraryCodeExecution": False,
    }
    with TestClient(module.app) as client:
        assert client.get("/health").status_code == 200
        assert client.post("/v1/execute", json=envelope).status_code == 401
        response = client.post("/v1/execute", json=envelope, headers={"Authorization": "Bearer test-secret"})
    assert response.status_code == 200
    assert response.json()["runtime"] == "r-statistical-econometric"
