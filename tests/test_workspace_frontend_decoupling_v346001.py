from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php"
WORKSPACE = ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php"
RUNTIME = ROOT / "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v3.46.0.1.js"
CONFIG = ROOT / "backend/app/config.py"

def test_release_identity():
    assert "Version: 3.46.0.1" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.0.1');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.0.1"' in CONFIG.read_text()

def test_main_runtime_has_zero_wordpress_script_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.0\.1\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m, "main Workspace enqueue block missing"
    assert re.sub(r"\s+", "", m.group(1)) == "array()"

def test_host_neutral_boot_contract():
    text = RUNTIME.read_text()
    assert "const WORKSPACE_RELEASE = '3.46.0.1';" in text
    assert "wordpressRequiredForApplicationBoot: false" in text
    assert "wordpressRequiredForProjectInteraction: false" in text
    assert "standalone-core-with-host-adapters" in text
    assert "SCWorkspaceConfig" in text
    assert "assetUrl('sc-workspace-local-project-compat-v3000.js')" in text
    assert "loadCompat('v3.46.0.1-core-interaction-continuity')" in text

def test_wordpress_is_adapter_configuration_not_application_dependency():
    text = WORKSPACE.read_text()
    assert "'SCWorkspaceConfig'" in text
    assert "'host' => 'wordpress'" in text
    assert "'wordpressRequired' => false" in text
    assert "'frontendMode' => 'standalone-core-with-wordpress-adapter'" in text
