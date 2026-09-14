from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_v230_identity_and_lineage():
    plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
    assert "Version: 2.3.0" in plugin
    manifest = json.loads((ROOT / "release-manifest-v2.3.0.json").read_text())
    assert manifest["version"] == "2.3.0"
    assert manifest["previous_version"] == "2.2.0"


def test_worker_is_separate_service():
    compose = (ROOT / "backend/docker-compose.example.yml").read_text()
    assert "sc-workspace-worker:" in compose
    assert 'command: ["python", "-m", "app.worker"]' in compose
    assert "sc-workspace-data:/data" in compose


def test_job_and_handoff_contracts_are_present():
    main = (ROOT / "backend/app/main.py").read_text()
    assert '/v1/jobs' in main
    assert '/v1/worker/status' in main
    assert '/v1/orchestration/routes' in main
    routing = (ROOT / "backend/app/routing.py").read_text()
    assert 'sc-workspace-compute-handoff/1.0' in routing
    assert 'No server-side orchestration route is configured' in routing


def test_browser_cannot_choose_route_urls():
    schema = (ROOT / "backend/app/schemas.py").read_text()
    assert "targetProduct" in schema
    assert "targetUrl" not in schema
    contract = json.loads((ROOT / "schemas/sc-workspace-background-jobs-v1.schema.json").read_text())
    assert contract["properties"]["browserSuppliedRouteUrlsAllowed"]["const"] is False


def test_wordpress_job_proxy_routes_exist():
    workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    for route in ["backend-jobs", "backend-worker-status", "backend-orchestration-routes"]:
        assert route in workspace
