from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
DEPLOY=(WP/'includes/class-sc-workspace-deployment.php').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v3000.js').read_text()
MAIN=(WP/'assets/js/workspace-v3.0.0.js').read_text()

def test_wordpress_exposes_backend_native_proxy_and_bootstrap():
    assert '/backend/backend-native-workspace' in PHP
    assert "'/v1/backend-native-workspace'" in PHP
    assert '/backend/backend-native-workspace/bootstrap' in PHP
    assert "'/v1/backend-native-workspace/bootstrap'" in PHP

def test_release_package_uses_v3000_active_assets():
    assert 'sc-workspace-typed-client-v3000.js' in DEPLOY
    assert 'sc-workspace-local-project-compat-v3000.js' in DEPLOY
    assert "'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in DEPLOY
    assert "'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in DEPLOY

def test_typed_runtime_contains_backend_native_boundary():
    assert 'backendNativeWorkspace' in TYPED
    assert 'backendNativeBootstrap' in TYPED
    assert 'SCWorkspaceBackendNativeScientificWorkspace' in TYPED
    assert "version: '3.0.0'" in TYPED

def test_thin_shell_forbids_signed_in_local_canonical_fallback():
    assert "SCWorkspaceBackendNativeBoundary" in MAIN
    assert "signedInLocalCanonicalFallback:false" in MAIN
    assert "version:'2.28.1'" in MAIN
