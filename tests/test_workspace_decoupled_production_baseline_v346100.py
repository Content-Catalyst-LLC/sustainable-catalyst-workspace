from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"

PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"
CONTRACT = ROOT / "production/decoupled-workspace-production-baseline-v3.46.10.0.json"
REPORT = ROOT / "production/decoupled-workspace-production-baseline-certification-v346100.json"
BASELINE_JS = ROOT / "app/core/workspace-decoupled-production-baseline-v346100.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v346100.js"
RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v346100.js"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
WP_CLASS = P / "includes/class-sc-workspace.php"

def enqueue_block():
    text = WP_CLASS.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.46.10.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.10.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.10.0"' in CONFIG.read_text()

def test_baseline_contract():
    data = json.loads(CONTRACT.read_text())
    assert data["schema"] == "sc-workspace-decoupled-production-baseline-contract/1.0"
    assert data["version"] == "3.46.10.0"
    assert data["productionBaseline"] is True
    assert data["rollbackRelease"] == "3.46.9.0"
    assert data["wordpress"]["role"] == "thin-host-adapter"
    assert data["standalone"]["productionCertified"] is True
    assert data["backend"]["canonicalAuthority"] is True

def test_baseline_certification_report():
    data = json.loads(REPORT.read_text())
    assert data["schema"] == "sc-workspace-decoupled-production-baseline-certification/1.0"
    assert data["version"] == "3.46.10.0"
    assert data["passed"] is True

def test_runtime_baseline_asset():
    text = BASELINE_JS.read_text()
    assert "sc-workspace-decoupled-production-baseline/1.0" in text
    assert "productionBaseline: true" in text
    assert "wordpressOwnsProjectLogic: false" in text
    assert "wordpressOwnsCanonicalState: false" in text
    assert "wordpressOwnsModuleBoot: false" in text
    assert "canonicalBackendAuthority: true" in text

def test_kernel_frozen_baseline_capability():
    text = KERNEL.read_text()
    assert "sc-workspace-application-kernel/1.9" in text
    assert "decoupledProductionBaseline: true" in text
    assert "wordpressRequired: false" in text

def test_standalone_runtime_frozen_baseline():
    text = RUNTIME.read_text()
    assert "decoupledProductionBaseline: '3.46.10.0'" in text
    assert "wordpressRequired: false" in text
    assert "directBackendTransport: true" in text

def test_wordpress_remains_thin():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "'sc-workspace-wordpress-thin-adapter-v346100'" in block
    assert "'assetManifestUrl'" in block
    for marker in ("'applicationKernelUrl'", "'projectRuntimeUrl'", "'entryPointUrl'", "SCWorkspaceConfig", "SCWorkspaceIdentity"):
        assert marker not in block

def test_baseline_asset_in_both_host_manifests():
    wp = json.loads((P / "assets/manifests/workspace-runtime-assets-v346100.json").read_text())
    st = json.loads((ROOT / "standalone/asset-manifest-v346100.json").read_text())
    assert "production.baseline" in wp["assets"]
    assert "production.baseline" in st["assets"]
    assert wp["assets"]["production.baseline"]["sha256"] == st["assets"]["production.baseline"]["sha256"]

def test_standalone_production_certification_still_passes():
    report = json.loads((ROOT / "standalone/production-certification-v346100.json").read_text())
    assert report["passed"] is True
    assert report["wordpressRequired"] is False

def test_deployment_rollback_and_baseline_guard():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.9.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.9.0';" in text
    assert "sc-workspace-decoupled-production-baseline-v346100.js" in text
    assert "$decoupled_production_baseline_ok" in text

def test_no_migrations():
    data = json.loads(CONTRACT.read_text())
    assert data["databaseMigration"] is False
    assert data["storageSchemaMigration"] is False
