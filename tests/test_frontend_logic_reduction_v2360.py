from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'; JS=WP/'assets/js'; CSS=WP/'assets/css'
MAIN=(JS/'workspace-v3.0.0.js').read_text(); COMPAT=(JS/'sc-workspace-local-project-compat-v3000.js').read_text(); PHP=(WP/'includes/class-sc-workspace.php').read_text(); DEPLOY=(WP/'includes/class-sc-workspace-deployment.php').read_text(); TYPED=(JS/'sc-workspace-typed-client-v3000.js').read_text()

def test_primary_runtime_is_thin_and_backend_authoritative():
    assert len(MAIN.splitlines()) < 120
    assert "mode:'thin-shell'" in MAIN and 'browserAuthoritativeState:false' in MAIN
    assert "canonicalMutations:'command-api-only'" in MAIN

def test_local_project_runtime_is_isolated_and_lazy():
    assert 'loadLocalCompatibility' in MAIN and 'legacyCompatUrl' in PHP
    assert "const WORKSPACE_RELEASE = '3.0.0';" in COMPAT
    assert 'sc-workspace-local-project-compat-v3000.js' in DEPLOY

def test_historical_versioned_workspace_assets_are_retired():
    assert [p.name for p in JS.glob('workspace-v*.js')] == ['workspace-v3.0.0.js']
    assert [p.name for p in CSS.glob('workspace-v*.css')] == ['workspace-v3.0.0.css']

def test_package_check_is_version_derived():
    assert "'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in DEPLOY
    assert "'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in DEPLOY

def test_frontend_runtime_is_in_typed_contract():
    assert 'frontendRuntime' in TYPED and '/v1/frontend-runtime' in TYPED
    assert 'SCWorkspaceFrontendBoundary' in TYPED

def test_v2281_interaction_repair_preserved():
    assert 'SCWorkspaceInteractionRepair' in MAIN and "version:'2.28.1'" in MAIN
