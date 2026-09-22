from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text()
MAIN=(WP/'assets/js/workspace-v3.1.0.js').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v3100.js').read_text()
TS=(ROOT/'frontend/typed-client/src/40-scientific-objects.ts').read_text()


def test_release_identity_and_interaction_repair_are_preserved():
    assert 'Version: 3.1.0' in PLUGIN and "const WORKSPACE_RELEASE = '3.1.0';" in MAIN
    assert 'SCWorkspaceInteractionRuntime' in MAIN and 'SCWorkspaceInteractionRepair' in MAIN


def test_typed_client_exposes_unified_scientific_object_methods():
    for token in ['scientificObjectProfile','scientificObjects','scientificObject','scientificObjectHistory','scientificObjectRelations']:
        assert token in TYPED
    assert 'SCWorkspaceScientificObjects' in TYPED


def test_wordpress_proxy_allowlists_unified_object_routes():
    for token in ["'/backend/scientific-objects/profile'", "'/backend/scientific-objects'", "scientific-objects/(?P<kind>", "backend_typed_scientific_object_relations"]:
        assert token in PHP


def test_frontend_object_runtime_is_read_only_projection_layer():
    assert 'backendAuthoritative:true' in TS
    assert 'browserAuthoritativeState:false' in TS
    assert 'genericMutation:false' in TS
    assert 'canonicalCachePersistent:false' in TS


def test_main_ui_declares_unified_scientific_object_boundary():
    assert 'SCWorkspaceScientificObjectBoundary' in MAIN
    assert 'genericMutation:false' in MAIN
    assert 'browserAuthoritativeState:false' in MAIN
