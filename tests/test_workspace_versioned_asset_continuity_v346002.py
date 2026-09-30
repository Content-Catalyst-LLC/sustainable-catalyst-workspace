from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOYMENT = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
CSS_PREV = P / "assets/css/workspace-v3.46.0.1.css"
CSS_CUR = P / "assets/css/workspace-v3.46.0.2.css"
JS_PREV = P / "assets/js/workspace-v3.46.0.1.js"
JS_CUR = P / "assets/js/workspace-v3.46.0.2.js"

def test_release_identity():
    assert "Version: 3.46.0.2" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.0.2');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.0.2"' in CONFIG.read_text()

def test_current_versioned_assets():
    assert CSS_CUR.stat().st_size >= 100000
    assert JS_CUR.stat().st_size >= 5000

def test_predecessor_assets_retained():
    assert CSS_PREV.stat().st_size >= 100000
    assert JS_PREV.stat().st_size >= 5000

def test_enqueue_exact_release_assets():
    text = WORKSPACE.read_text()
    assert "assets/css/workspace-v3.46.0.2.css" in text
    assert "assets/js/workspace-v3.46.0.2.js" in text

def test_deployment_guard_hardened():
    text = DEPLOYMENT.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.0.1';" in text
    assert "const ROLLBACK_RELEASE = '3.46.0';" in text
    assert "clearstatcache();" in text
    assert "$previous_asset_continuity_ok" in text
    assert "'previous_release_asset_continuity_required' => true" in text

def test_main_runtime_has_zero_wordpress_feature_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.0\.2\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m, "main Workspace enqueue block missing"
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
