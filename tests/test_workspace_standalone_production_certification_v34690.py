from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
CONFIG = ROOT / "backend/app/config.py"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
BUILD_MANIFEST = ROOT / "build/workspace-runtime-assets-v34690.json"
PIPELINE = ROOT / "build/build_workspace_assets_v34690.py"
CERT = ROOT / "build/certify_workspace_standalone_v34690.py"
CERT_JS = ROOT / "app/standalone/workspace-standalone-production-certification-v34690.js"
STANDALONE = ROOT / "standalone"
MANIFEST = STANDALONE / "asset-manifest-v34690.json"
REPORT = STANDALONE / "production-certification-v34690.json"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34690.js"
RUNTIME = ROOT / "app/standalone/workspace-standalone-runtime-v34690.js"

def test_release_identity():
    assert "Version: 3.46.9.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.9.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.9.0"' in CONFIG.read_text()

def test_certification_sources_exist():
    assert CERT.is_file()
    assert CERT_JS.is_file()
    assert REPORT.is_file()

def test_build_manifest_contains_certification_asset():
    data = json.loads(BUILD_MANIFEST.read_text())
    assert data["version"] == "3.46.9.0"
    ids = {item["id"] for item in data["assets"]}
    assert "standalone.certification" in ids

def test_generated_manifest_certification_asset():
    data = json.loads(MANIFEST.read_text())
    assert data["version"] == "3.46.9.0"
    assert data["host"] == "standalone"
    assert data["wordpressRequired"] is False
    assert "standalone.certification" in data["assets"]
    assert data["assets"]["standalone.certification"]["file"] == "sc-workspace-standalone-production-certification-v34690.js"

def test_static_report_passed():
    report = json.loads(REPORT.read_text())
    assert report["schema"] == "sc-workspace-standalone-production-certification-report/1.0"
    assert report["version"] == "3.46.9.0"
    assert report["passed"] is True
    names = {gate["name"] for gate in report["gates"] if gate["ok"]}
    assert "WORKSPACE_STANDALONE_ASSET_SHA256_INTEGRITY" in names
    assert "WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION" in names
    assert "WORKSPACE_STANDALONE_STATIC_HTTP_SERVE" in names

def test_kernel_production_certification_capability():
    text = KERNEL.read_text()
    assert "sc-workspace-application-kernel/1.8" in text
    assert "standaloneProductionCertificationCapable: true" in text
    assert "wordpressRequired: false" in text

def test_runtime_production_certification_contract():
    text = RUNTIME.read_text()
    assert "productionCertificationContract" in text
    assert "sc-workspace-standalone-production-certification/1.0" in text
    assert "directBackendTransport: true" in text
    assert "wordpressRequired: false" in text

def test_certification_hard_gates():
    text = CERT.read_text()
    for marker in (
        "WORKSPACE_STANDALONE_CERT_MANIFEST",
        "WORKSPACE_STANDALONE_ASSET_COMPLETENESS",
        "WORKSPACE_STANDALONE_ASSET_SHA256_INTEGRITY",
        "WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION",
        "WORKSPACE_STANDALONE_MANIFEST_DRIVEN_BOOT",
        "WORKSPACE_STANDALONE_STATIC_HTTP_SERVE",
        "WORKSPACE_STANDALONE_DIRECT_BACKEND_CONFIG",
    ):
        assert marker in text

def test_live_backend_probe_is_optional():
    text = CERT.read_text()
    assert "--backend-url" in text
    assert "WORKSPACE_STANDALONE_LIVE_BACKEND_HEALTH" in text
    assert "if backend_url:" in text

def test_deployment_baseline_advanced():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.8.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.8.0';" in text
    assert "sc-workspace-runtime-asset-manifest-v34690.js" in text

def test_asset_pipeline_advanced():
    text = PIPELINE.read_text()
    assert '3.46.9.0' in text
    assert 'v34690' in text
