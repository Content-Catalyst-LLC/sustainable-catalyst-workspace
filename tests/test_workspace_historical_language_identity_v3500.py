from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"

PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"
MAIN = ROOT / "backend/app/main.py"
MODULE = ROOT / "app/linguistics/workspace-historical-language-script-variant-identity-v3500.js"
RUNTIME = ROOT / "backend/app/historical_language_identity_runtime.py"
PROFILE = ROOT / "backend/app/historical_language_identity_workspace.py"
BUILD = ROOT / "build/workspace-runtime-assets-v3500.json"
WP_MAN = P / "assets/manifests/workspace-runtime-assets-v3500.json"
ST_MAN = ROOT / "standalone/asset-manifest-v3500.json"
WP_CLASS = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
KERNEL = ROOT / "app/core/workspace-application-kernel-v3500.js"
ST_RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v3500.js"

def enqueue_block():
    text = WP_CLASS.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.50.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.50.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.50.0"' in CONFIG.read_text()

def test_module_contract():
    text = MODULE.read_text()
    assert "sc-workspace-historical-language-script-variant-identity-workspace/1.0" in text
    assert "sc-workspace-historical-language-identity/1.0" in text
    assert "sc-workspace-script-identity/1.0" in text
    assert "sc-workspace-language-variant-identity/1.0" in text
    assert "automaticModernizationEnabled: false" in text
    assert "automaticVariantNormalizationEnabled: false" in text
    assert "wordpressRequired: false" in text

def test_backend_contract():
    text = RUNTIME.read_text()
    assert 'RUNTIME_SCHEMA = "sc-workspace-historical-language-identity-runtime/1.0"' in text
    assert "workspace.linguistics.historical-temporal-profile" in text
    assert "historicalIdentityPreserved" in text

def test_backend_routes_and_health():
    text = MAIN.read_text()
    assert '@app.get("/v1/historical-language-script-variant-identity-workspace")' in text
    assert '@app.get("/v1/historical-language-identity-runtime")' in text
    assert '@app.get("/v1/historical-language-identity-runtime/operations")' in text
    assert '@app.post("/v1/historical-language-identity-runtime/execute")' in text
    assert '"historicalLanguageIdentityWorkspace": True' in text
    assert '"historicalLanguageIdentityRuntimeBoundedOperations": len(HISTORICAL_LANGUAGE_IDENTITY_OPERATIONS)' in text

def test_registry_chain():
    for text in (enqueue_block(), (ROOT / "standalone/config.js").read_text()):
        assert "workspace.linguistics.original-language-corpus" in text
        assert "workspace.linguistics.annotation-corpus-structure" in text
        assert "workspace.linguistics.translation-parallel-alignment" in text
        assert "workspace.linguistics.historical-language-identity" in text

def test_single_wordpress_entrypoint():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "sc-workspace-historical-language-script-variant-identity-v3500.js" not in block

def test_shared_asset_and_prior_module_continuity():
    build = json.loads(BUILD.read_text())
    by_id = {item["id"]: item for item in build["assets"]}
    current = by_id["workspace.linguistics.historical-language-identity"]
    assert current["shared"] is True and current["autoload"] is False
    assert by_id["workspace.linguistics.original-language-corpus"]["source"].endswith("v3470.js")
    assert by_id["workspace.linguistics.annotation-corpus-structure"]["source"].endswith("v3480.js")
    assert by_id["workspace.linguistics.translation-parallel-alignment"]["source"].endswith("v3490.js")

    wp = json.loads(WP_MAN.read_text())
    st = json.loads(ST_MAN.read_text())
    assert wp["assets"][current["id"]]["sha256"] == st["assets"][current["id"]]["sha256"]

def test_kernel_runtime_capability():
    assert "historicalLanguageScriptVariantIdentityWorkspaceCapable: true" in KERNEL.read_text()
    runtime = ST_RUNTIME.read_text()
    assert "historicalLanguageScriptVariantIdentityWorkspace: true" in runtime
    assert "decoupledProductionBaseline: '3.46.10.0'" in runtime

def test_deployment_rollback():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.49.0';" in text
    assert "const ROLLBACK_RELEASE = '3.49.0';" in text
    assert "sc-workspace-historical-language-script-variant-identity-v3500.js" in text

def test_no_migrations():
    manifest = json.loads((ROOT / "release-manifest-v3.50.0.json").read_text())
    assert manifest["databaseMigration"] is False
    assert manifest["storageSchemaMigration"] is False
