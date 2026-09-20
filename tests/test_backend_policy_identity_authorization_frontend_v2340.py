from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text()
MAIN=(WP/'assets/js/workspace-v2.35.0.js').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v2350.js').read_text()
TS=(ROOT/'frontend/typed-client/src/60-backend-policy-identity-authorization.ts').read_text()

def test_release_identity_and_working_interaction_lineage_preserved():
    assert 'Version: 2.35.0' in PLUGIN
    assert "const WORKSPACE_RELEASE = '2.35.0';" in MAIN
    assert 'SCWorkspaceInteractionRuntime' in MAIN and 'SCWorkspaceInteractionRepair' in MAIN

def test_wordpress_proxy_exposes_authorization_endpoints_without_service_token():
    for text in ['/backend/authorization', '/backend/authorization/identity', '/backend/authorization/evaluate', '/backend/authorization/decisions']:
        assert text in PHP
    assert 'service_token' not in TYPED.lower()

def test_typed_client_exposes_authorization_profile_identity_evaluation_and_receipts():
    for text in ['authorizationProfile()', 'authorizationIdentity()', 'evaluateAuthorization(request', 'authorizationDecisions()']:
        assert text in TYPED
    generated=(ROOT/'frontend/typed-client/src/00-generated-contracts.ts').read_text()
    assert 'WorkspaceAuthorizationEvaluateRequest' in generated

def test_browser_boundary_never_becomes_authorization_authority():
    assert 'SCWorkspaceAuthorizationBoundary' in MAIN
    assert 'browserAuthoritativeAuthorization:false' in MAIN
    assert 'clientSuppliedRolesTrusted:false' in MAIN
    assert 'clientSuppliedScopesTrusted:false' in MAIN
    assert 'backendAuthoritative:true' in TS
    assert "defaultEffect:'deny'" in TS

def test_generated_typed_client_is_v2340_and_has_35_endpoints():
    generated=(ROOT/'frontend/typed-client/src/00-generated-contracts.ts').read_text()
    assert "SCW_TYPED_CONTRACT_VERSION = '2.35.0'" in generated
    assert generated.count("path: '/v1/") == 35
