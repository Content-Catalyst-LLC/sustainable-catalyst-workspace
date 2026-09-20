from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text()
MAIN=(WP/'assets/js/workspace-v2.35.0.js').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v2350.js').read_text()
TS=(ROOT/'frontend/typed-client/src/20-thin-client-state.ts').read_text()

def test_release_identity_and_working_interaction_runtime_are_preserved():
    assert 'Version: 2.35.0' in PLUGIN and "const WORKSPACE_RELEASE = '2.35.0';" in MAIN
    assert 'SCWorkspaceInteractionRuntime' in MAIN and 'SCWorkspaceInteractionRepair' in MAIN
    assert 'workspace-v2.35.0.js' in PHP and 'workspace-v2.35.0.css' in PHP

def test_thin_state_runtime_persists_only_allowlisted_transient_keys():
    assert "sc_workspace_transient_v2310" in TS
    assert "canonicalCache:Map<string,unknown>" in TS
    assert "canonicalCachePersistent:false" in TS
    assert "persistentBrowserState:'transient-only'" in TS
    assert "Workspace thin-state rejected non-transient key" in TS

def test_canonical_cache_is_memory_only_and_rehydratable():
    assert "this.canonicalCache.clear()" in TS
    assert "thinClientBootstrap" in TS
    assert "persistCanonicalCache" not in TS
    assert "localStorage.setItem('projects'" not in TS

def test_typed_client_exposes_thin_state_profile_and_bootstrap():
    assert 'thinClientStateProfile' in TYPED and 'thinClientBootstrap' in TYPED
    assert 'SCWorkspaceThinClientState' in TYPED and 'SCWorkspaceState' in TYPED

def test_wordpress_proxy_exposes_only_server_side_thin_state_routes():
    assert "'/backend/thin-client-state'" in PHP
    assert "'/backend/thin-client-state/bootstrap'" in PHP
    assert "backend_typed_thin_client_state" in PHP and "backend_typed_thin_client_bootstrap" in PHP

def test_main_runtime_declares_thin_client_boundary():
    assert 'SCWorkspaceThinClientStateBoundary' in MAIN
    assert "canonicalMutations:'command-api-only'" in MAIN
    assert "persistentBrowserState:'transient-only'" in MAIN
