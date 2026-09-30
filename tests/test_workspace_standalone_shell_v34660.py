from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"

STANDALONE = ROOT / "standalone"
INDEX = STANDALONE / "index.html"
BOOTSTRAP = STANDALONE / "bootstrap.js"
STANDALONE_CONFIG = STANDALONE / "config.js"
MANIFEST = STANDALONE / "asset-manifest-v34660.json"
RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v34660.js"
HOST = ROOT / "adapters/standalone/workspace-standalone-host-adapter-v34660.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34660.js"

def test_release_identity():
    assert "Version: 3.46.6.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.6.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.6.0"' in CONFIG.read_text()

def test_standalone_distribution_exists():
    for path in (
        INDEX,
        BOOTSTRAP,
        STANDALONE_CONFIG,
        MANIFEST,
        STANDALONE / "workspace-standalone-shell-v34660.css",
        STANDALONE / "assets/workspace-standalone-shell-v34660.js",
        STANDALONE / "serve.py",
    ):
        assert path.is_file(), path

def test_standalone_index_has_no_wordpress_dependency():
    text = INDEX.read_text().lower()
    for marker in ("wp-content", "wp-json", "wp-admin", "sc-workspace-wordpress-host-adapter", "sc-workspace-wordpress-transport-adapter", "sc-workspace-wordpress-auth-adapter"):
        assert marker not in text
    assert "does not require a wordpress rest proxy" in text
    assert "data-sc-workspace-standalone" in text
    assert "./config.js" in text
    assert "./bootstrap.js" in text

def test_standalone_config_is_direct_host():
    text = STANDALONE_CONFIG.read_text()
    assert "host: 'standalone'" in text
    assert "https://workspace-api.sustainablecatalyst.com" in text
    assert "wordpressRequired: false" in text
    assert "automaticBackendHealthCheck: false" in text

def test_bootstrap_loads_only_host_neutral_plus_standalone_assets():
    text = BOOTSTRAP.read_text()
    assert "sc-workspace-standalone-host-adapter-v34660.js" in text
    assert "sc-workspace-standalone-runtime-v34660.js" in text
    assert "sc-workspace-application-kernel-v34660.js" in text
    assert "workspace-standalone-shell-v34660.js" in text
    assert "wordpress-host-adapter" not in text
    assert "wordpress-transport-adapter" not in text
    assert "wordpress-auth-adapter" not in text

def test_standalone_runtime_composes_canonical_services():
    text = RUNTIME.read_text()
    for marker in (
        "createDirect",
        "createAnonymous",
        "persistenceFactory.create",
        "stateStoreFactory.create",
        "projectFactory.create",
        "moduleRegistryFactory.create",
        "kernelFactory.createKernel",
        "kernel.registerProjectLifecycle",
        "kernel.registerModuleRegistry",
    ):
        assert marker in text
    assert "wordpressRequired: false" in text

def test_standalone_host_adapter_is_host_neutral():
    text = HOST.read_text().lower()
    assert "sc-workspace-standalone-host-adapter/1.0" in text
    assert "directbackendtransport" in text
    for marker in ("wp_enqueue_", "wp_localize_", "wp-json", "wp-content", "wp-admin"):
        assert marker not in text

def test_asset_manifest_declares_wordpress_absent():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["version"] == "3.46.6.0"
    assert manifest["wordpressRequired"] is False
    assert manifest["directBackendTransport"] is True
    assert "assets/sc-workspace-application-kernel-v34660.js" in manifest["assets"]

def test_kernel_certifies_standalone_shell():
    text = KERNEL.read_text()
    assert "3.46.6.0" in text
    assert "sc-workspace-application-kernel/1.5" in text
    assert "standaloneShellCapable: true" in text
    assert "wordpressRequired: false" in text

def test_wordpress_adapter_continuity():
    text = WORKSPACE.read_text()
    assert "assets/js/workspace-v3.46.6.0.js" in text
    assert "sc-workspace-local-project-compat-v34660.js" in text
    assert "sc-workspace-application-kernel-v34660.js" in text

def test_deployment_baseline_advanced():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.5.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.5.0';" in text
    assert "sc-workspace-local-project-compat-v34660.js" in text
    assert "sc-workspace-application-kernel-v34660.js" in text

def test_main_shell_zero_wordpress_script_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.6\.0\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
