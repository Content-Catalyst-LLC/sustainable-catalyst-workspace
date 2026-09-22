from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v3100.js').read_text()
BOUNDARY=(WP/'assets/js/sc-workspace-platform-core-runtime-v3100.js').read_text()
MAIN=(WP/'assets/js/workspace-v3.1.0.js').read_text()


def test_wordpress_exposes_platform_core_server_proxy_without_core_secret():
    for route in ('/backend/platform-core-runtime', '/backend/platform-core-runtime/readiness', '/backend/platform-core-runtime/sessions', '/backend/platform-core-runtime/object-bindings', '/backend/platform-core-runtime/execution-bindings', '/backend/platform-core-runtime/visual-bindings', '/backend/platform-core-runtime/package-bindings', '/backend/platform-core-runtime/handoff-bindings'):
        assert route in PHP
    assert 'SC_WORKSPACE_PLATFORM_CORE_WRITE_API_KEY' not in PHP
    assert 'SC_CORE_WRITE_API_KEY' not in PHP


def test_typed_client_contains_all_core_v3_integration_methods():
    for token in ('platformCoreRuntime', 'platformCoreReadiness', 'createPlatformCoreSession', 'bindPlatformCoreObject', 'bindPlatformCoreExecution', 'bindPlatformCoreVisual', 'bindPlatformCorePackage', 'bindPlatformCoreHandoff', 'platformCoreSessionLineage', 'platformCoreSessionBundle'):
        assert token in TYPED
    assert "SCW_TYPED_CONTRACT_VERSION = '3.1.0'" in TYPED


def test_browser_boundary_is_reference_first_and_non_authoritative():
    assert "workspaceVersion:'3.1.0'" in BOUNDARY
    assert 'referenceFirst:true' in BOUNDARY
    assert 'browserAuthoritative:false' in BOUNDARY
    assert 'browserDirectCoreAccess:false' in BOUNDARY
    assert 'coreCredentialBrowserVisible:false' in BOUNDARY


def test_v3100_thin_shell_exists():
    assert MAIN
    assert '3.1.0' in MAIN
