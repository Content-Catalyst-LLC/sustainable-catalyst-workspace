from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"

PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"
MAIN = ROOT / "backend/app/main.py"
BACKEND_PROFILE = ROOT / "backend/app/original_language_corpus_workspace.py"
MODULE = ROOT / "app/linguistics/workspace-original-language-corpus-v3470.js"
ENTRY = ROOT / "app/entry/workspace-application-entry-v3470.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v3470.js"
RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v3470.js"
BUILD_MANIFEST = ROOT / "build/workspace-runtime-assets-v3470.json"
WP_MANIFEST = P / "assets/manifests/workspace-runtime-assets-v3470.json"
ST_MANIFEST = ROOT / "standalone/asset-manifest-v3470.json"
WP_CLASS = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
BASELINE = ROOT / "production/decoupled-workspace-production-baseline-v3.46.10.0.json"

def enqueue_block():
    text = WP_CLASS.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.47.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.47.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.47.0"' in CONFIG.read_text()

def test_decoupled_production_baseline_preserved():
    data = json.loads(BASELINE.read_text())
    assert data["version"] == "3.46.10.0"
    assert data["productionBaseline"] is True
    assert data["wordpress"]["requiredByCore"] is False
    assert data["backend"]["canonicalAuthority"] is True

def test_original_language_module_contract():
    text = MODULE.read_text()
    assert "sc-workspace-original-language-corpus-workspace/1.0" in text
    assert "sc-workspace-original-language-text/1.0" in text
    assert "sc-workspace-derived-language-representation/1.0" in text
    assert "workspace.linguistics.text-identity" in text
    assert "workspace.linguistics.corpus-profile" in text
    assert "workspace.linguistics.corpus-lineage" in text
    assert "automaticLanguageDetectionEnabled: false" in text
    assert "automaticTranslationEnabled: false" in text
    assert "automaticTransliterationEnabled: false" in text
    assert "wordpressRequired: false" in text

def test_optional_module_loader_supports_logical_asset_id():
    text = ENTRY.read_text()
    assert "source.assetId" in text
    assert "assetUrl('', assetId)" in text

def test_wordpress_registers_linguistics_module_without_module_url():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "'assetId' => 'workspace.linguistics.original-language-corpus'" in block
    assert "'global' => 'SCWorkspaceOriginalLanguageCorpusWorkspace'" in block
    assert "sc-workspace-original-language-corpus-v3470.js" not in block

def test_standalone_registers_linguistics_module_by_asset_id():
    text = (ROOT / "standalone/config.js").read_text()
    assert "workspace.linguistics.original-language-corpus" in text
    assert "SCWorkspaceOriginalLanguageCorpusWorkspace" in text
    assert "assetId" in text

def test_module_shared_across_hosts():
    build = json.loads(BUILD_MANIFEST.read_text())
    item = next(x for x in build["assets"] if x["id"] == "workspace.linguistics.original-language-corpus")
    assert item["shared"] is True
    assert item["autoload"] is False
    assert set(item["targets"]) == {"wordpress", "standalone"}

    wp = json.loads(WP_MANIFEST.read_text())
    st = json.loads(ST_MANIFEST.read_text())
    assert wp["assets"]["workspace.linguistics.original-language-corpus"]["sha256"] == st["assets"]["workspace.linguistics.original-language-corpus"]["sha256"]

def test_backend_workspace_profile():
    text = BACKEND_PROFILE.read_text()
    assert 'WORKSPACE_SCHEMA = "sc-workspace-original-language-corpus-workspace/1.0"' in text
    assert '"originalLanguageFirst": True' in text
    assert '"automaticTranslationEnabled": False' in text
    assert '"boundedOperationCount": len(OPERATIONS)' in text

def test_backend_route_and_health_advertisement():
    text = MAIN.read_text()
    assert '@app.get("/v1/original-language-corpus-workspace")' in text
    assert '"originalLanguageCorpusWorkspace": True' in text
    assert '"originalLanguageCorpusWorkspaceSchema": ORIGINAL_LANGUAGE_CORPUS_WORKSPACE_SCHEMA' in text
    assert '"originalLanguageCorpusWorkspaceBoundedOperations": len(MULTILINGUAL_CORPUS_OPERATIONS)' in text

def test_kernel_and_runtime_preserve_decoupling():
    kernel = KERNEL.read_text()
    runtime = RUNTIME.read_text()
    assert "decoupledProductionBaseline: true" in kernel
    assert "originalLanguageCorpusWorkspaceCapable: true" in kernel
    assert "wordpressRequired: false" in kernel
    assert "decoupledProductionBaseline: '3.46.10.0'" in runtime
    assert "originalLanguageCorpusWorkspace: true" in runtime
    assert "wordpressRequired: false" in runtime

def test_deployment_previous_and_rollback_release():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.10.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.10.0';" in text
    assert "sc-workspace-original-language-corpus-v3470.js" in text

def test_no_migrations():
    manifest = json.loads((ROOT / "release-manifest-v3.47.0.json").read_text())
    assert manifest["databaseMigration"] is False
    assert manifest["storageSchemaMigration"] is False
