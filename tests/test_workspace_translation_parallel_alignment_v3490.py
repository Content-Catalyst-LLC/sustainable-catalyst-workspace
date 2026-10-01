from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"wordpress/sustainable-catalyst-workspace"
PLUGIN=P/"sustainable-catalyst-workspace.php"; CONFIG=ROOT/"backend/app/config.py"; MAIN=ROOT/"backend/app/main.py"
MODULE=ROOT/"app/linguistics/workspace-translation-transliteration-parallel-alignment-v3490.js"
RUNTIME=ROOT/"backend/app/translation_alignment_runtime.py"; PROFILE=ROOT/"backend/app/translation_alignment_workspace.py"
BUILD=ROOT/"build/workspace-runtime-assets-v3490.json"; WP_MAN=P/"assets/manifests/workspace-runtime-assets-v3490.json"; ST_MAN=ROOT/"standalone/asset-manifest-v3490.json"
WP_CLASS=P/"includes/class-sc-workspace.php"; DEPLOY=P/"includes/class-sc-workspace-deployment.php"; KERNEL=ROOT/"app/core/workspace-application-kernel-v3490.js"; ST_RUNTIME=ROOT/"app/standalone/workspace-standalone-runtime-v3490.js"

def block():
    t=WP_CLASS.read_text(); return t.split("private function enqueue_assets()",1)[1].split("private function tools()",1)[0]

def test_identity():
    assert "Version: 3.49.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.49.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.49.0"' in CONFIG.read_text()

def test_contracts():
    t=MODULE.read_text()
    assert "sc-workspace-translation-transliteration-parallel-alignment-workspace/1.0" in t
    assert "automaticTranslationEnabled: false" in t and "automaticAlignmentEnabled: false" in t
    assert "wordpressRequired: false" in t
    b=RUNTIME.read_text()
    assert 'RUNTIME_SCHEMA = "sc-workspace-translation-alignment-runtime/1.0"' in b
    assert "originalLanguageRemainsCanonical" in b

def test_routes_health():
    t=MAIN.read_text()
    assert '@app.get("/v1/translation-transliteration-parallel-alignment-workspace")' in t
    assert '@app.get("/v1/translation-alignment-runtime")' in t
    assert '@app.post("/v1/translation-alignment-runtime/execute")' in t
    assert '"translationAlignmentWorkspace": True' in t
    assert '"translationAlignmentRuntimeBoundedOperations": len(TRANSLATION_ALIGNMENT_OPERATIONS)' in t

def test_registry_chain_and_single_entrypoint():
    for t in (block(),(ROOT/"standalone/config.js").read_text()):
        assert "workspace.linguistics.original-language-corpus" in t
        assert "workspace.linguistics.annotation-corpus-structure" in t
        assert "workspace.linguistics.translation-parallel-alignment" in t
    assert block().count("wp_enqueue_script(")==1
    assert "sc-workspace-translation-transliteration-parallel-alignment-v3490.js" not in block()

def test_asset_parity_continuity():
    build=json.loads(BUILD.read_text()); by={x["id"]:x for x in build["assets"]}
    item=by["workspace.linguistics.translation-parallel-alignment"]
    assert item["shared"] is True and item["autoload"] is False
    assert by["workspace.linguistics.original-language-corpus"]["source"].endswith("v3470.js")
    assert by["workspace.linguistics.annotation-corpus-structure"]["source"].endswith("v3480.js")
    wp=json.loads(WP_MAN.read_text()); st=json.loads(ST_MAN.read_text())
    assert wp["assets"][item["id"]]["sha256"]==st["assets"][item["id"]]["sha256"]

def test_kernel_runtime_deployment():
    assert "translationTransliterationParallelAlignmentWorkspaceCapable: true" in KERNEL.read_text()
    rt=ST_RUNTIME.read_text()
    assert "translationTransliterationParallelAlignmentWorkspace: true" in rt
    assert "decoupledProductionBaseline: '3.46.10.0'" in rt
    d=DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.48.0';" in d
    assert "const ROLLBACK_RELEASE = '3.48.0';" in d
    assert "sc-workspace-translation-transliteration-parallel-alignment-v3490.js" in d

def test_no_migrations():
    x=json.loads((ROOT/"release-manifest-v3.49.0.json").read_text())
    assert x["databaseMigration"] is False and x["storageSchemaMigration"] is False
