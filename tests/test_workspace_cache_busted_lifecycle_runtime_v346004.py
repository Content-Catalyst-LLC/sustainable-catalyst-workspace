from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOYMENT = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
SHELL = P / "assets/js/workspace-v3.46.0.4.js"
LIFECYCLE = P / "assets/js/sc-workspace-local-project-compat-v346004.js"
CSS = P / "assets/css/workspace-v3.46.0.4.css"

def test_release_identity():
    assert "Version: 3.46.0.4" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.0.4');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.0.4"' in CONFIG.read_text()

def test_release_specific_lifecycle_runtime():
    text = LIFECYCLE.read_text()
    assert "const INTERACTION_RUNTIME_VERSION = '3.46.0.4';" in text
    assert "function deleteActiveProjectFromDevice()" in text
    assert "target.matches('[data-scw-delete]')" in text
    assert LIFECYCLE.stat().st_size >= 10000

def test_host_config_cache_busts_lifecycle_runtime():
    text = WORKSPACE.read_text()
    exact = "add_query_arg('ver', SC_WORKSPACE_VERSION, SC_WORKSPACE_URL . 'assets/js/sc-workspace-local-project-compat-v346004.js')"
    assert text.count(exact) == 2

def test_shell_forces_release_query_and_replaces_stale_script():
    text = SHELL.read_text()
    assert "sc-workspace-local-project-compat-v346004.js" in text
    assert "parsed.searchParams.set('ver', WORKSPACE_RELEASE)" in text
    assert "scwCompatibilityRelease" in text
    assert "compatibility-cache-replacement" in text
    assert "existing.remove()" in text

def test_server_package_guard_includes_lifecycle_runtime():
    text = DEPLOYMENT.read_text()
    assert "'local_compatibility' => 'assets/js/sc-workspace-local-project-compat-v346004.js'" in text
    assert "const MIN_LIFECYCLE_RUNTIME_BYTES = 10000;" in text
    assert "$lifecycle_runtime_ok" in text
    assert "'project_lifecycle_runtime_cache_busted' => true" in text

def test_current_and_previous_release_continuity():
    text = DEPLOYMENT.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.0.3';" in text
    assert "const ROLLBACK_RELEASE = '3.46.0.3';" in text
    assert CSS.stat().st_size >= 100000
    assert SHELL.stat().st_size >= 5000

def test_core_shell_remains_wordpress_dependency_free():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.0\.4\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
