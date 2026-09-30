from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
REGISTRY = ROOT / "app/core/workspace-module-registry-v34650.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34650.js"
SHELL = P / "assets/js/workspace-v3.46.5.0.js"
COMPAT = P / "assets/js/sc-workspace-local-project-compat-v34650.js"
WP_REGISTRY = P / "assets/js/sc-workspace-module-registry-v34650.js"

def test_release_identity():
    assert "Version: 3.46.5.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.5.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.5.0"' in CONFIG.read_text()

def test_registry_is_canonical_and_host_neutral():
    assert REGISTRY.is_file()
    text = REGISTRY.read_text()
    assert "sc-workspace-module-registry/1.0" in text
    assert "sc-workspace-module-manifest/1.0" in text
    assert "optionalFailureIsolation: true" in text
    assert "requiredFailureBlocksBoot: true" in text
    assert WP_REGISTRY.read_text() == text

    lower = text.lower()
    for marker in (
        "wp_enqueue_", "wp_localize_", "wp-json", "wp-content",
        "wp-admin", "window.scworkspaceidentity"
    ):
        assert marker not in lower

def test_registry_supports_dependencies_and_capabilities():
    text = REGISTRY.read_text()
    assert "dependsOn" in text
    assert "capabilities" in text
    assert "capabilityProviders" in text
    assert "dependency-cycle" in text
    assert "missing-dependency" in text
    assert "dependency-unavailable" in text

def test_optional_failure_is_isolated():
    text = REGISTRY.read_text()
    assert "if (!record.manifest.optional) throw error;" in text
    assert "unexpected-optional-load-propagation" in text
    assert "isolate-optional-module" in text

def test_kernel_registers_module_registry():
    text = KERNEL.read_text()
    assert "registerModuleRegistry" in text
    assert "moduleRegistryRegistered" in text
    assert "optionalModuleFailureIsolation" in text
    assert "moduleRegistry()" in text

def test_shell_loads_registry_before_kernel_and_compat():
    text = SHELL.read_text()
    assert "moduleRegistryUrl" in text
    assert "SCWorkspaceModuleRegistryFactory" in text
    assert "loadOptionalModules" in text
    assert "registerCoreModuleCapabilities" in text
    assert text.index("loadScriptAsset(moduleRegistryUrl") < text.index("loadScriptAsset(kernelUrl")
    assert text.index("loadCompat('v3.46.5.0-core-interaction-continuity')") < text.index("await loadOptionalModules()")

def test_shell_optional_module_loader_does_not_block_boot():
    text = SHELL.read_text()
    assert "optional-module-load" in text
    assert "await moduleRegistry.loadAll" in text
    block = text.split("async function loadOptionalModules()",1)[1].split("function recordIssue",1)[0]
    assert "throw error" not in block

def test_compat_registers_state_project_services_in_registry():
    text = COMPAT.read_text()
    assert "core.persistence" in text
    assert "core.state-store" in text
    assert "core.project-runtime" in text
    assert "moduleRegistry.registerReady" in text

def test_wordpress_config_exposes_registry_and_optional_modules():
    text = WORKSPACE.read_text()
    assert "'moduleRegistryUrl'" in text
    assert "'optionalModules' => array()" in text

def test_deployment_guard_requires_module_registry():
    text = DEPLOY.read_text()
    assert "'module_registry' => 'assets/js/sc-workspace-module-registry-v34650.js'" in text
    assert "const MIN_MODULE_REGISTRY_BYTES" in text
    assert "$module_registry_ok" in text
    assert "const PREVIOUS_RELEASE = '3.46.4.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.4.0';" in text

def test_main_shell_still_has_zero_wordpress_script_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.5\.0\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
