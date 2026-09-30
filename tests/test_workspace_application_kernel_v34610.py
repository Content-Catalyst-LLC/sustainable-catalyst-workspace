from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOYMENT = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
SHELL = P / "assets/js/workspace-v3.46.1.0.js"
LIFECYCLE = P / "assets/js/sc-workspace-local-project-compat-v34610.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34610.js"
CONTRACT = ROOT / "app/core/workspace-host-adapter-contract-v1.js"
WP_ADAPTER = ROOT / "adapters/wordpress/workspace-wordpress-host-adapter-v34610.js"
WP_KERNEL = P / "assets/js/sc-workspace-application-kernel-v34610.js"
WP_CONTRACT = P / "assets/js/sc-workspace-host-adapter-contract-v34610.js"
WP_HOST = P / "assets/js/sc-workspace-wordpress-host-adapter-v34610.js"

def test_release_identity():
    assert "Version: 3.46.1.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.1.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.1.0"' in CONFIG.read_text()

def test_application_kernel_source_exists():
    assert KERNEL.is_file()
    assert CONTRACT.is_file()
    assert WP_ADAPTER.is_file()
    assert "sc-workspace-application-kernel/1.0" in KERNEL.read_text()
    assert "sc-workspace-host-adapter-contract/1.0" in CONTRACT.read_text()

def test_core_has_zero_wordpress_imports():
    forbidden = (
        "wp_enqueue_",
        "wp_localize_",
        "wp_rest",
        "wp-json",
        "wp-content",
        "wp-admin",
        "wordpress/sustainable-catalyst-workspace",
        "window.scworkspaceidentity",
        "sc_workspace_",
    )
    for path in (KERNEL, CONTRACT):
        text = path.read_text().lower()
        for marker in forbidden:
            assert marker not in text, f"{path} contains WordPress coupling marker: {marker}"

def test_packaged_kernel_assets_match_canonical_source():
    assert WP_KERNEL.read_text() == KERNEL.read_text()
    assert WP_CONTRACT.read_text() == CONTRACT.read_text()
    assert WP_HOST.read_text() == WP_ADAPTER.read_text()

def test_shell_loads_kernel_before_compatibility_runtime():
    text = SHELL.read_text()
    assert "loadApplicationKernel" in text
    assert "SCWorkspaceApplicationKernelFactory" in text
    assert "SCWorkspaceApplicationKernel" in text
    assert text.index("await loadApplicationKernel();") < text.index("loadCompat('v3.46.1.0-core-interaction-continuity')")

def test_host_configuration_exposes_adapter_assets():
    text = WORKSPACE.read_text()
    for name in (
        "hostAdapterContractUrl",
        "applicationKernelUrl",
        "hostAdapterUrl",
        "legacyCompatUrl",
    ):
        assert name in text
    assert "sc-workspace-local-project-compat-v34610.js" in text

def test_lifecycle_bridge_preserves_verified_project_runtime():
    text = LIFECYCLE.read_text()
    assert "const INTERACTION_RUNTIME_VERSION = '3.46.1.0';" in text
    assert "function deleteActiveProjectFromDevice()" in text
    assert "registerProjectLifecycle" in text
    assert "compatibility-project-lifecycle" in text
    assert "target.matches('[data-scw-delete]')" in text

def test_deployment_guard_requires_kernel_boundary():
    text = DEPLOYMENT.read_text()
    for marker in (
        "application_kernel",
        "host_adapter_contract",
        "wordpress_host_adapter",
        "application_kernel_ok",
        "host_boundary_ok",
    ):
        assert marker in text
    assert "const PREVIOUS_RELEASE = '3.46.0.4';" in text
    assert "const ROLLBACK_RELEASE = '3.46.0.4';" in text

def test_main_shell_has_zero_wordpress_script_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.1\.0\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
