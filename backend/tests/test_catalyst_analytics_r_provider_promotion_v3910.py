from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.analytics_r_provider import profile
from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
WP = ROOT / "wordpress" / "sustainable-catalyst-workspace"


def test_workspace_391_health_promotes_analytics_r_220():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "3.9.1"
    assert body["catalystAnalyticsRRuntimeAdapter"] is True
    assert body["catalystAnalyticsRProviderInstalled"] is True
    assert body["catalystAnalyticsRProviderVersion"] == "2.2.0"
    assert body["catalystAnalyticsRCoreContract"] == "sc.core.analytical-runtime-provider.v1"
    assert body["catalystAnalyticsRDiagnosticsContract"] == "sc.analytics-r.statistical-diagnostics-validation.v1"
    assert body["catalystAnalyticsRStatisticalDiagnosticsValidation"] is True
    assert body["catalystAnalyticsRAdapterVersion"] == "3.9.1"
    assert body["releaseMigrationLineage"] == "040_timeline_event_reconstruction_investigative_sequence_workspace.sql"


def test_provider_profile_preserves_workspace_authority_and_diagnostics_boundary():
    item = profile()
    assert item["workspaceVersion"] == "3.9.1"
    assert item["providerKey"] == "catalystanalyticsr"
    assert item["providerVersion"] == "2.2.0"
    assert item["coreContract"] == "sc.core.analytical-runtime-provider.v1"
    assert item["diagnosticsContract"] == "sc.analytics-r.statistical-diagnostics-validation.v1"
    assert item["statisticalDiagnosticsValidation"] is True
    assert item["runtimeImageInstallation"] == "build-time"
    assert item["productionFilesystem"] == "read-only"
    assert item["arbitraryFunctionDispatch"] is False
    assert item["arbitraryCodeExecution"] is False
    assert item["clientSuppliedRuntimeUrlAllowed"] is False
    assert item["clientSuppliedPackagesAllowed"] is False
    assert item["workspaceControlsAuthentication"] is True
    assert item["workspaceControlsPersistence"] is True
    assert item["humanReviewRequired"] is True


def test_vendored_provider_is_220_and_declares_diagnostics_contract():
    vendor = BACKEND / "r-runtime" / "vendor" / "catalystanalyticsr"
    description = (vendor / "DESCRIPTION").read_text()
    provider = (vendor / "R" / "core_computational_provider.R").read_text()
    diagnostics = (vendor / "R" / "statistical_diagnostics_validation.R").read_text()
    assert "Package: catalystanalyticsr" in description
    assert "Version: 2.2.0" in description
    assert 'diagnostics_contract = "sc.analytics-r.statistical-diagnostics-validation.v1"' in provider
    assert "statistical_validation_bundle" in diagnostics
    assert "human_review_required" in diagnostics


def test_r_image_installs_220_at_build_time_and_stays_hardened():
    dockerfile = (BACKEND / "r-runtime" / "Dockerfile").read_text()
    compose = (BACKEND / "docker-compose.example.yml").read_text()
    assert "R CMD INSTALL --preclean /opt/catalystanalyticsr" in dockerfile
    assert 'packageVersion("catalystanalyticsr")) == "2.2.0"' in dockerfile
    assert 'p$diagnostics_contract == "sc.analytics-r.statistical-diagnostics-validation.v1"' in dockerfile
    r_section = compose.split("\n  sc-workspace-r-runtime:\n", 1)[1].split("\n  sc-workspace-julia-runtime:\n", 1)[0]
    assert "read_only: true" in r_section
    assert "cap_drop:" in r_section and "- ALL" in r_section
    assert "no-new-privileges:true" in r_section
    assert "/tmp:rw,noexec,nosuid" in r_section


def test_provider_runner_remains_bounded_and_reports_391():
    source = (BACKEND / "r-runtime" / "provider_runner.R").read_text()
    assert 'workspace_version = "3.9.1"' in source
    assert 'workspace_adapter_version = "3.9.1"' in source
    assert 'adapter_version = "3.9.1"' in source
    assert "EXECUTABLE_METHODS <- c(" in source
    assert "getExportedValue" in source
    assert "do.call(fun, method_args)" in source
    assert "eval(parse(" not in source
    assert "system(" not in source
    assert 'Catalyst Analytics R v2.2.0' in source


def test_no_new_database_migration_and_v390_lineage_is_preserved():
    migrations = sorted((BACKEND / "migrations").glob("*.sql"))
    assert migrations[-1].name == "040_timeline_event_reconstruction_investigative_sequence_workspace.sql"
    assert not any(p.name.startswith("041_") for p in migrations)
    assert (BACKEND / "app" / "investigation_timeline_workspace.py").exists()
    assert (BACKEND / "app" / "investigation_graph_workspace.py").exists()


def test_typed_client_surface_is_complete_and_promoted():
    item = client_profile(app.openapi())
    assert item["workspaceVersion"] == "3.9.1"
    assert item["typedEndpointCount"] == 111
    assert item["missingOpenApiOperations"] == []
    assert TYPED_ENDPOINTS["analyticsRProvider"] == {"method":"GET", "path":"/v1/analytics/providers/catalystanalyticsr"}
    js = (WP / "assets" / "js" / "sc-workspace-typed-client-v3910.js").read_text()
    assert "SCW_TYPED_CONTRACT_VERSION = '3.9.1'" in js
    assert item["openApiProjectionSha256"] in js


def test_wordpress_plugin_promotes_provider_without_exposing_credentials():
    plugin = (WP / "sustainable-catalyst-workspace.php").read_text()
    adapter = (WP / "assets" / "js" / "sc-workspace-catalyst-analytics-r-v3910.js").read_text()
    shell = (WP / "includes" / "class-sc-workspace.php").read_text()
    assert "Version: 3.9.1" in plugin
    assert "SC_WORKSPACE_VERSION', '3.9.1'" in plugin
    assert "providerVersion: '2.2.0'" in adapter
    assert "sc.analytics-r.statistical-diagnostics-validation.v1" in adapter
    assert "sc-workspace-catalyst-analytics-r-v3910" in shell
    assert "sc-workspace-typed-client-v3910" in shell
    assert "SC_WORKSPACE_RUNTIME_R_TOKEN" not in adapter
