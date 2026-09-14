from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "wordpress" / "sustainable-catalyst-workspace"


def test_release_version_and_backend_bootstrap():
    text = (PLUGIN / "sustainable-catalyst-workspace.php").read_text()
    assert "Version: 2.1.0" in text
    assert "class-sc-workspace-backend.php" in text


def test_backend_runtime_files_present():
    required = [
        ROOT / "backend" / "app" / "main.py",
        ROOT / "backend" / "app" / "repository.py",
        ROOT / "backend" / "Dockerfile",
        ROOT / "backend" / "migrations" / "001_initial.sql",
    ]
    assert all(path.is_file() for path in required)


def test_wordpress_bridge_is_fail_closed_and_opt_in():
    text = (PLUGIN / "includes" / "class-sc-workspace-backend.php").read_text()
    assert "SC_WORKSPACE_BACKEND_MODE" in text
    assert "'disabled'" in text
    assert "No fallback write was attempted" in text
    assert "Authorization" in text
    assert "X-SC-User-ID" in text


def test_existing_cloud_routes_are_preserved_and_backend_contract_added():
    text = (PLUGIN / "includes" / "class-sc-workspace.php").read_text()
    assert "'/cloud-projects'" in text
    assert "'/cloud-notebooks'" in text
    assert "'/backend-contract'" in text
    assert "'/backend-status'" in text
    assert "SC_Workspace_Backend::enabled()" in text


def test_release_manifest_declares_backend_boundary():
    manifest = json.loads((ROOT / "release-manifest-v2.1.0.json").read_text())
    assert manifest["previous_version"] == "2.0.4"
    backend = manifest["backend_foundation"]
    assert backend["runtime"] == "FastAPI"
    assert backend["database"] == "PostgreSQL"
    assert backend["browser_direct_access"] is False
    assert backend["automatic_migration"] is False
