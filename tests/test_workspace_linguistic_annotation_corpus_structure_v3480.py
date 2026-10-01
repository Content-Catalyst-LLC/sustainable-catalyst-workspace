from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"

PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"
MAIN = ROOT / "backend/app/main.py"
MODULE = ROOT / "app/linguistics/workspace-linguistic-annotation-corpus-structure-v3480.js"
RUNTIME = ROOT / "backend/app/linguistic_annotation_runtime.py"
PROFILE = ROOT / "backend/app/linguistic_annotation_corpus_workspace.py"
ENTRY = ROOT / "app/entry/workspace-application-entry-v3480.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v3480.js"
ST_RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v3480.js"
BUILD_MANIFEST = ROOT / "build/workspace-runtime-assets-v3480.json"
WP_MANIFEST = P / "assets/manifests/workspace-runtime-assets-v3480.json"
ST_MANIFEST = ROOT / "standalone/asset-manifest-v3480.json"
WP_CLASS = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
BASELINE = ROOT / "production/decoupled-workspace-production-baseline-v3.46.10.0.json"

def enqueue_block():
    text = WP_CLASS.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.48.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.48.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.48.0"' in CONFIG.read_text()

def test_decoupled_baseline_preserved():
    data = json.loads(BASELINE.read_text())
    assert data["version"] == "3.46.10.0"
    assert data["wordpress"]["requiredByCore"] is False
    assert data["backend"]["canonicalAuthority"] is True

def test_annotation_module_contract():
    text = MODULE.read_text()
    assert "sc-workspace-linguistic-annotation-corpus-structure-workspace/1.0" in text
    assert "sc-workspace-linguistic-annotation/1.0" in text
    assert "sc-workspace-linguistic-annotation-layer/1.0" in text
    assert "sc-workspace-corpus-structure-node/1.0" in text
    assert "unicode-code-point" in text
    for operation in (
        "workspace.linguistics.annotation-validate",
        "workspace.linguistics.annotation-span-index",
        "workspace.linguistics.annotation-layer-profile",
        "workspace.linguistics.document-structure",
        "workspace.linguistics.corpus-structure",
        "workspace.linguistics.annotation-lineage",
    ):
        assert operation in text
    assert "automaticLanguageDetectionEnabled: false" in text
    assert "automaticTranslationEnabled: false" in text
    assert "wordpressRequired: false" in text

def test_backend_runtime_contract():
    text = RUNTIME.read_text()
    assert 'RUNTIME_SCHEMA = "sc-workspace-linguistic-annotation-runtime/1.0"' in text
    assert 'OFFSET_UNIT = "unicode-code-point"' in text
    assert "MAX_ANNOTATIONS = 20_000" in text
    assert "STRUCTURE_NODE_TYPES" in text
    assert "provenancePreserved" in text

def test_backend_workspace_profile():
    text = PROFILE.read_text()
    assert 'WORKSPACE_SCHEMA = "sc-workspace-linguistic-annotation-corpus-structure-workspace/1.0"' in text
    assert '"boundedOperationCount": len(OPERATIONS)' in text
    assert '"offsetUnit": OFFSET_UNIT' in text
    assert '"originalLanguageFirst": True' in text
    assert '"provenancePreserved": True' in text

def test_backend_routes_and_health():
    text = MAIN.read_text()
    assert '@app.get("/v1/linguistic-annotation-corpus-structure-workspace")' in text
    assert '@app.get("/v1/linguistic-annotation-runtime")' in text
    assert '@app.get("/v1/linguistic-annotation-runtime/operations")' in text
    assert '@app.post("/v1/linguistic-annotation-runtime/execute")' in text
    assert '"linguisticAnnotationCorpusStructureWorkspace": True' in text
    assert '"linguisticAnnotationRuntimeBoundedOperations": len(LINGUISTIC_ANNOTATION_OPERATIONS)' in text

def test_module_registry_dependencies():
    wp = enqueue_block()
    standalone = (ROOT / "standalone/config.js").read_text()
    for text in (wp, standalone):
        assert "workspace.linguistics.annotation-corpus-structure" in text
        assert "workspace.linguistics.original-language-corpus" in text
        assert "assetId" in text

def test_wordpress_stays_single_entrypoint():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "sc-workspace-linguistic-annotation-corpus-structure-v3480.js" not in block

def test_shared_module_asset_parity():
    build = json.loads(BUILD_MANIFEST.read_text())
    item = next(x for x in build["assets"] if x["id"] == "workspace.linguistics.annotation-corpus-structure")
    assert item["shared"] is True
    assert item["autoload"] is False

    wp = json.loads(WP_MANIFEST.read_text())
    st = json.loads(ST_MANIFEST.read_text())
    assert wp["assets"]["workspace.linguistics.annotation-corpus-structure"]["sha256"] == st["assets"]["workspace.linguistics.annotation-corpus-structure"]["sha256"]

def test_original_language_module_continuity():
    build = json.loads(BUILD_MANIFEST.read_text())
    item = next(x for x in build["assets"] if x["id"] == "workspace.linguistics.original-language-corpus")
    assert item["source"] == "app/linguistics/workspace-original-language-corpus-v3470.js"

def test_kernel_and_runtime_capabilities():
    kernel = KERNEL.read_text()
    runtime = ST_RUNTIME.read_text()
    assert "decoupledProductionBaseline: true" in kernel
    assert "originalLanguageCorpusWorkspaceCapable: true" in kernel
    assert "linguisticAnnotationCorpusStructureWorkspaceCapable: true" in kernel
    assert "wordpressRequired: false" in kernel
    assert "decoupledProductionBaseline: '3.46.10.0'" in runtime
    assert "linguisticAnnotationCorpusStructureWorkspace: true" in runtime
    assert "wordpressRequired: false" in runtime

def test_deployment_previous_and_rollback():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.47.0';" in text
    assert "const ROLLBACK_RELEASE = '3.47.0';" in text
    assert "sc-workspace-linguistic-annotation-corpus-structure-v3480.js" in text
    assert "sc-workspace-original-language-corpus-v3470.js" in text

def test_no_migrations():
    manifest = json.loads((ROOT / "release-manifest-v3.48.0.json").read_text())
    assert manifest["databaseMigration"] is False
    assert manifest["storageSchemaMigration"] is False
