from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_v250_identity_and_lineage():
    plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
    assert "Version: 2.5.0" in plugin
    manifest = json.loads((ROOT / "release-manifest-v2.5.0.json").read_text())
    assert manifest["version"] == "2.5.0"
    assert manifest["previous_version"] == "2.4.0"
    assert manifest["release_name"] == "Reproducible Execution Environments & Dependency Manifests"


def test_environment_database_contract_is_present():
    models = (ROOT / "backend/app/models.py").read_text()
    migration = (ROOT / "backend/migrations/005_reproducible_execution_environments.sql").read_text()
    for token in ["workspace_execution_environment_heads", "workspace_execution_environment_revisions", "environment_ref", "environment_fingerprint"]:
        assert token in models or token in migration
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in migration


def test_environment_routes_and_run_linkage_are_present():
    main = (ROOT / "backend/app/main.py").read_text()
    schemas = (ROOT / "backend/app/schemas.py").read_text()
    registry = (ROOT / "backend/app/registry.py").read_text()
    for route in ["/v1/execution-environments", "/v1/execution-environments/{environment_id}/revisions"]:
        assert route in main
    assert "environmentRef" in schemas
    assert "resolve_environment_ref" in registry


def test_environment_manifest_excludes_secret_values():
    envs = (ROOT / "backend/app/environments.py").read_text()
    assert "environmentVariableNames" in envs
    assert "secretsCaptured" in envs
    assert "environmentVariableValues" not in envs


def test_wordpress_environment_proxy_routes_exist():
    workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
    assert "backend-execution-environments" in workspace
    for flag in ["executionEnvironmentRegistry", "dependencyManifests", "runtimeVersionCapture", "randomSeedCapture"]:
        assert flag in bridge


def test_v250_contract_is_bounded():
    contract = json.loads((ROOT / "schemas/sc-workspace-execution-environment-registry-v1.schema.json").read_text())
    props = contract["properties"]
    assert props["version"]["const"] == "2.5.0"
    assert props["secretEnvironmentValuesCaptured"]["const"] is False
    assert props["automaticEnvironmentReproduction"]["const"] is False
