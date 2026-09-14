from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_wordpress_release_and_assets_are_v220():
    plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
    shell = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    assert "Version: 2.2.0" in plugin
    assert "workspace-v2.2.0.js" in shell
    assert "workspace-v2.2.0.css" in shell


def test_migration_bridge_is_explicit_and_nondestructive():
    bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
    shell = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    assert "configured_request" in bridge
    assert "legacyStoreRetainedAfterMigration" in bridge
    assert "backend-migration/plan" in shell
    assert "backend-migration/apply" in shell


def test_backend_has_content_addressed_storage_and_recovery():
    object_store = (ROOT / "backend/app/object_store.py").read_text()
    recovery = (ROOT / "backend/app/recovery.py").read_text()
    compose = (ROOT / "backend/docker-compose.example.yml").read_text()
    assert 'hashlib.sha256(content).hexdigest()' in object_store
    assert 'os.replace(temp, path)' in object_store
    assert 'sc-workspace-recovery-manifest/1.0' in recovery
    assert 'sc-workspace-data:/data' in compose


def test_release_manifest_preserves_local_schema_and_moves_rollback_lineage():
    manifest = json.loads((ROOT / "release-manifest-v2.2.0.json").read_text())
    assert manifest["previous_version"] == "2.1.0"
    assert manifest["storage_schema_version"] == 35
    assert manifest["project_schema"] == "sc-workspace-project/20.0"
    assert manifest["export_schema"] == "sc-workspace-project-export/20.0"
    assert manifest["backend_foundation"]["object_storage"] is True
    assert manifest["backend_foundation"]["compute_orchestration"] is False
