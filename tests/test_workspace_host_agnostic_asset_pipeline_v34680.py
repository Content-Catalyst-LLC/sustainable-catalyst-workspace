from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
BUILD_MANIFEST = ROOT / "build/workspace-runtime-assets-v34680.json"
PIPELINE = ROOT / "build/build_workspace_assets_v34680.py"
WP_MANIFEST = P / "assets/manifests/workspace-runtime-assets-v34680.json"
WP_MANIFEST_JS = P / "assets/js/sc-workspace-runtime-asset-manifest-v34680.js"
STANDALONE_MANIFEST = ROOT / "standalone/asset-manifest-v34680.json"
STANDALONE_MANIFEST_JS = ROOT / "standalone/assets/sc-workspace-runtime-asset-manifest-v34680.js"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"

def enqueue_block():
    text = WORKSPACE.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.46.8.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.8.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.8.0"' in CONFIG.read_text()

def test_canonical_build_manifest_exists():
    data = json.loads(BUILD_MANIFEST.read_text())
    assert data["schema"] == "sc-workspace-build-asset-manifest/1.0"
    assert data["version"] == "3.46.8.0"
    ids = {item["id"] for item in data["assets"]}
    for required in ("host.contract", "client.transport", "client.auth", "client.api", "state.persistence", "state.store", "projects.runtime", "modules.registry", "application.kernel"):
        assert required in ids

def test_pipeline_and_generated_manifests_exist():
    assert PIPELINE.is_file()
    assert WP_MANIFEST.is_file()
    assert WP_MANIFEST_JS.is_file()
    assert STANDALONE_MANIFEST.is_file()
    assert STANDALONE_MANIFEST_JS.is_file()

def test_shared_asset_checksum_parity():
    wp = json.loads(WP_MANIFEST.read_text())
    standalone = json.loads(STANDALONE_MANIFEST.read_text())
    shared = set(wp["assets"]).intersection(standalone["assets"])
    assert shared
    checked = 0
    for asset_id in shared:
        if wp["assets"][asset_id].get("shared"):
            assert wp["assets"][asset_id]["sha256"] == standalone["assets"][asset_id]["sha256"]
            checked += 1
    assert checked >= 8

def test_wordpress_bridge_uses_manifest_not_runtime_url_graph():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "SCWorkspaceWordPressBridge" in block
    assert "'assetManifestUrl'" in block
    assert "sc-workspace-runtime-asset-manifest-v34680.js" in block
    forbidden = (
        "'applicationKernelUrl'",
        "'moduleRegistryUrl'",
        "'persistenceRuntimeUrl'",
        "'stateStoreRuntimeUrl'",
        "'projectRuntimeUrl'",
        "'transportRuntimeUrl'",
        "'authContextRuntimeUrl'",
        "'apiClientRuntimeUrl'",
        "'transportAdapterUrl'",
        "'authAdapterUrl'",
        "'hostAdapterUrl'",
        "'legacyCompatUrl'",
        "'entryPointUrl'",
    )
    for marker in forbidden:
        assert marker not in block

def test_wordpress_thin_adapter_loads_runtime_manifest():
    text = (ROOT / "adapters/wordpress/workspace-wordpress-thin-adapter-v34680.js").read_text()
    assert "sc-workspace-wordpress-thin-adapter/1.1" in text
    assert "assetManifestUrl" in text
    assert "SCWorkspaceRuntimeAssetManifest" in text
    assert "application.entry" in text
    assert "hostAgnosticAssetPipeline: true" in text

def test_standalone_boot_is_manifest_driven():
    text = (ROOT / "standalone/bootstrap.js").read_text()
    assert "sc-workspace-runtime-asset-manifest-v34680.js" in text
    assert "manifest.loadOrder" in text
    assert "manifest.assets[id]" in text
    assert "sc-workspace-host-adapter-contract-v34620.js" not in text
    assert "sc-workspace-application-kernel-v34680.js" not in text

def test_application_entry_resolves_manifest_assets():
    text = (ROOT / "app/entry/workspace-application-entry-v34680.js").read_text()
    assert "SCWorkspaceRuntimeAssetManifest" in text
    assert "assetManifest" in text
    assert "resolveManifestAsset" in text
    assert "3.46.8.0" in text

def test_deployment_requires_generated_manifest():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.7.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.7.0';" in text
    assert "'runtime_asset_manifest' => 'assets/js/sc-workspace-runtime-asset-manifest-v34680.js'" in text
    assert "$runtime_asset_manifest_ok" in text

def test_wordpress_php_stays_single_entrypoint():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "'sc-workspace-wordpress-thin-adapter-v34680'" in block

def test_pipeline_source_has_no_wordpress_runtime_dependency():
    text = PIPELINE.read_text().lower()
    assert "wp_enqueue_script" not in text
    assert "wp_localize_script" not in text
