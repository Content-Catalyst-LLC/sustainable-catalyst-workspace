from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text()
DEPLOY=(WP/'includes/class-sc-workspace-deployment.php').read_text()
CERT=(WP/'includes/class-sc-workspace-production-certification.php').read_text()
TYPED=(WP/'assets/js/sc-workspace-typed-client-v2360.js').read_text()
MAIN=(WP/'assets/js/workspace-v2.36.0.js').read_text()


def test_wordpress_exposes_production_certification_proxy():
    assert '/backend/production-certification' in PHP
    assert "'/v1/production-certification'" in PHP


def test_release_package_uses_v236_active_assets():
    assert 'sc-workspace-typed-client-v2360.js' in DEPLOY
    assert 'sc-workspace-local-project-compat-v2360.js' in DEPLOY
    assert "'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in DEPLOY
    assert "'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in DEPLOY


def test_certification_distinguishes_architecture_from_live_field_checks():
    assert "'architecture_certification' => true" in CERT
    assert "'live_production_certification' => false" in CERT
    assert "'rollback_release' => self::ROLLBACK_RELEASE" in CERT


def test_typed_runtime_contains_certification_boundary():
    assert 'productionCertification' in TYPED
    assert '/production-certification' in TYPED
    assert 'SCWorkspaceProductionArchitectureBoundary' in TYPED


def test_thin_shell_and_interaction_repair_still_hold():
    assert "mode:'thin-shell'" in MAIN
    assert "version:'2.28.1'" in MAIN
