from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.analytics_r_provider import profile
from app.client_contracts import TYPED_ENDPOINTS

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"


def test_workspace_version_and_health_flags():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "3.5.0"
    assert body["catalystAnalyticsRRuntimeAdapter"] is True
    assert body["catalystAnalyticsRProviderInstalled"] is True
    assert body["catalystAnalyticsRProviderVersion"] == "2.1.0"
    assert body["catalystAnalyticsRCoreContract"] == "sc.core.analytical-runtime-provider.v1"
    assert body["catalystAnalyticsRAdapterVersion"] == "3.5.0"
    assert body["analyticalProviderReceipts"] is True
    assert body["releaseMigrationLineage"] == "036_catalyst_analytics_r_runtime_adapter.sql"


def test_provider_profile_preserves_workspace_authority():
    item = profile()
    assert item["workspaceVersion"] == "3.5.0"
    assert item["providerKey"] == "catalystanalyticsr"
    assert item["providerVersion"] == "2.1.0"
    assert item["coreContract"] == "sc.core.analytical-runtime-provider.v1"
    assert item["runtime"] == "r"
    assert item["executionHost"] == "workspace"
    assert item["runtimeImageInstallation"] == "build-time"
    assert item["productionFilesystem"] == "read-only"
    assert item["arbitraryFunctionDispatch"] is False
    assert item["arbitraryCodeExecution"] is False
    assert item["clientSuppliedRuntimeUrlAllowed"] is False
    assert item["clientSuppliedPackagesAllowed"] is False


def test_r_image_installs_provider_at_build_time_and_compose_remains_read_only():
    dockerfile = (BACKEND / "r-runtime" / "Dockerfile").read_text()
    compose = (BACKEND / "docker-compose.example.yml").read_text()
    assert "r-cran-ggplot2" in dockerfile
    assert "r-cran-rlang" in dockerfile
    assert "R CMD INSTALL --preclean /opt/catalystanalyticsr" in dockerfile
    assert 'packageVersion("catalystanalyticsr")' in dockerfile
    r_section = compose.split("\n  sc-workspace-r-runtime:\n", 1)[1].split("\n  sc-workspace-julia-runtime:\n", 1)[0]
    assert "read_only: true" in r_section
    assert "cap_drop:" in r_section and "- ALL" in r_section
    assert "no-new-privileges:true" in r_section


def test_provider_runner_is_whitelist_only():
    source = (BACKEND / "r-runtime" / "provider_runner.R").read_text()
    assert "EXECUTABLE_METHODS <- c(" in source
    assert '"run_uncertainty"' in source
    assert '"difference_in_differences"' in source
    assert '"climate_accounting"' in source
    assert "scenario_projection" not in source
    assert "getExportedValue" in source
    assert "do.call(fun, method_args)" in source
    assert "eval(parse(" not in source
    assert "system(" not in source


def test_vendored_provider_identity():
    description = (BACKEND / "r-runtime" / "vendor" / "catalystanalyticsr" / "DESCRIPTION").read_text()
    assert "Package: catalystanalyticsr" in description
    assert "Version: 2.1.0" in description
    assert "ggplot2" in description and "rlang" in description


def test_provider_routes_are_typed_and_present_in_openapi():
    expected = {
        "analyticsRProvider": ("GET", "/v1/analytics/providers/catalystanalyticsr"),
        "analyticsRProviderValidate": ("POST", "/v1/analytics/providers/catalystanalyticsr/validate"),
        "analyticsRProviderExecute": ("POST", "/v1/analytics/providers/catalystanalyticsr/execute"),
        "analyticsProviderReceipts": ("GET", "/v1/analytics/provider-receipts"),
        "analyticsProviderReceipt": ("GET", "/v1/analytics/provider-receipts/{receipt_id}"),
    }
    paths = app.openapi()["paths"]
    for key, (method, path) in expected.items():
        assert TYPED_ENDPOINTS[key] == {"method": method, "path": path}
        assert method.lower() in paths[path]
    assert len(TYPED_ENDPOINTS) == 69


def test_provider_routes_require_service_identity():
    client = TestClient(app)
    for method, path in [
        ("get", "/v1/analytics/providers/catalystanalyticsr"),
        ("post", "/v1/analytics/providers/catalystanalyticsr/validate"),
        ("post", "/v1/analytics/providers/catalystanalyticsr/execute"),
        ("get", "/v1/analytics/provider-receipts"),
    ]:
        response = client.post(path, json={}) if method == "post" else client.get(path)
        assert response.status_code in {401, 503}


def test_migration_and_model_define_durable_receipts():
    migration = (BACKEND / "migrations" / "036_catalyst_analytics_r_runtime_adapter.sql").read_text()
    models = (BACKEND / "app" / "models.py").read_text()
    assert "CREATE TABLE IF NOT EXISTS workspace_analytical_provider_receipts" in migration
    assert "request_fingerprint VARCHAR(64)" in migration
    assert "result_fingerprint VARCHAR(64)" in migration
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in migration
    assert 'class AnalyticalProviderReceipt(Base):' in models
    assert '__tablename__ = "workspace_analytical_provider_receipts"' in models
