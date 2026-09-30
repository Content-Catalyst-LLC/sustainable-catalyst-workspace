from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"

PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOY = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
ADAPTER = ROOT / "adapters/wordpress/workspace-wordpress-thin-adapter-v34670.js"
WP_ADAPTER = P / "assets/js/sc-workspace-wordpress-thin-adapter-v34670.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34670.js"
SHELL = P / "assets/js/workspace-v3.46.7.0.js"
COMPAT = P / "assets/js/sc-workspace-local-project-compat-v34670.js"

def enqueue_block():
    text = WORKSPACE.read_text()
    return text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]

def test_release_identity():
    assert "Version: 3.46.7.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.7.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.7.0"' in CONFIG.read_text()

def test_wordpress_enqueue_graph_is_thin():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert block.count("wp_enqueue_style(") == 1
    assert block.count("wp_localize_script(") == 1
    assert "'sc-workspace-wordpress-thin-adapter-v34670'" in block
    assert "SCWorkspaceWordPressBridge" in block
    assert "workspace-v3.46.7.0.js" in block

def test_legacy_php_script_graph_retired():
    block = enqueue_block()
    forbidden = (
        "sc-workspace-platform-core-runtime-v3100",
        "sc-workspace-unified-research-context-v3200",
        "sc-workspace-typed-client-v31100",
        "sc-workspace-production-signoff-ui-v1",
        "sc-workspace-public-beta-iii-ui-v1",
        "sc-workspace-ga-readiness-ui-v1",
    )
    for marker in forbidden:
        assert marker not in block
    assert "legacyPhpScriptGraphRetired" in block
    assert "applicationModuleBoot" in block

def test_thin_bridge_preserves_host_contract_metadata():
    block = enqueue_block()
    required = (
        "'entryPointUrl'",
        "'apiBase'",
        "'assetBase'",
        "'legacyCompatUrl'",
        "'hostAdapterContractUrl'",
        "'applicationKernelUrl'",
        "'moduleRegistryUrl'",
        "'persistenceRuntimeUrl'",
        "'stateStoreRuntimeUrl'",
        "'projectRuntimeUrl'",
        "'transportRuntimeUrl'",
        "'authContextRuntimeUrl'",
        "'apiClientRuntimeUrl'",
        "'transportAdapterUrl'",
        "'authAdapterUrl'",
        "'hostAdapterUrl'",
        "'identity'",
    )
    for marker in required:
        assert marker in block

def test_thin_adapter_is_mirrored_and_contains_no_application_logic():
    assert ADAPTER.is_file()
    assert WP_ADAPTER.is_file()
    assert ADAPTER.read_text() == WP_ADAPTER.read_text()
    text = ADAPTER.read_text()
    assert "sc-workspace-wordpress-thin-adapter/1.0" in text
    assert "sc-workspace-wordpress-thin-bridge/1.0" in text
    assert "phpScriptGraphRetired: true" in text
    assert "applicationModuleBootOwnedByJavaScript: true" in text
    assert "projectLogicOwnedByWordPress: false" in text
    assert "stateOwnedByWordPress: false" in text
    for marker in ("localStorage", "createProject(", "deleteProject(", "registerProjectLifecycle("):
        assert marker not in text

def test_application_shell_remains_host_boot_owner():
    text = SHELL.read_text()
    assert "WORKSPACE_RELEASE = '3.46.7.0'" in text
    assert "SCWorkspaceModuleRegistryFactory" in text
    assert "SCWorkspaceApplicationKernelFactory" in text
    assert "loadOptionalModules" in text
    assert "wordpressRequired: false" in text

def test_kernel_certifies_thin_adapter():
    text = KERNEL.read_text()
    assert "sc-workspace-application-kernel/1.6" in text
    assert "3.46.7.0" in text
    assert "wordpressThinAdapterCapable: true" in text
    assert "standaloneShellCapable: true" in text
    assert "wordpressRequired: false" in text

def test_compatibility_runtime_advances_without_becoming_host_owner():
    text = COMPAT.read_text()
    assert "const INTERACTION_RUNTIME_VERSION = '3.46.7.0';" in text
    assert "SCWorkspaceProjectRuntimeFactory" in text
    assert "SCWorkspaceCanonicalStateStore" in text

def test_deployment_guard_requires_thin_adapter():
    text = DEPLOY.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.6.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.6.0';" in text
    assert "'wordpress_thin_adapter' => 'assets/js/sc-workspace-wordpress-thin-adapter-v34670.js'" in text
    assert "const MIN_WORDPRESS_THIN_ADAPTER_BYTES" in text
    assert "$wordpress_thin_adapter_ok" in text

def test_historical_assets_are_not_deleted_from_package_contract():
    text = DEPLOY.read_text()
    assert "production_signoff_runtime" in text
    assert "ga_readiness_runtime" in text
    assert "connected_knowledge_runtime" in text

def test_main_application_script_is_not_directly_enqueued_by_php():
    block = enqueue_block()
    direct_main_script = (
        "'sc-workspace-v241',\n"
        "            SC_WORKSPACE_URL . 'assets/js/workspace-v3.46.7.0.js'"
    )
    assert direct_main_script not in block
    assert block.count("wp_enqueue_script(") == 1
    assert "'sc-workspace-wordpress-thin-adapter-v34670'" in block
    assert "SCWorkspaceConfig" not in block
    assert "SCWorkspaceIdentity" not in block
