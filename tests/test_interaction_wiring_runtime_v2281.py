from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
JS=(WP/'assets/js/workspace-v2.35.0.js').read_text()
COMPAT=(WP/'assets/js/sc-workspace-local-project-compat-v2350.js').read_text()
BOOTSTRAP=(WP/'assets/js/sc-workspace-interaction-bootstrap-v2281.js').read_text()
PHP=(WP/'includes/class-sc-workspace.php').read_text()
PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text()

def test_release_identity_aligned():
    assert 'Version: 2.35.0' in PLUGIN
    assert "const WORKSPACE_RELEASE = '2.35.0';" in JS
    assert 'workspace-v2.35.0.js' in PHP
    assert 'workspace-v2.35.0.css' in PHP

def test_core_click_bindings_are_null_safe():
    assert not re.search(r"root\.querySelector\('[^']+'\)\.addEventListener\('click'", COMPAT)
    for selector in ('[data-scw-new-project]','[data-scw-delete]','[data-scw-new-object]','[data-scw-object-delete]'):
        assert f"bindControl('{selector}'" in COMPAT

def test_delegated_fallback_covers_primary_routes():
    assert "document.addEventListener('click'" in BOOTSTRAP
    for selector in ('[data-scw-workspace-view]','[data-scw-project-mode]','[data-scw-new-project]','[data-scw-import-project]'):
        assert selector in BOOTSTRAP

def test_runtime_diagnostics_and_audit_present():
    assert 'SCWorkspaceInteractionRuntime' in JS
    assert 'interactionRuntime.unhandledErrors' in JS
    assert 'interactionRuntime.audit' in COMPAT
    assert "root.dataset.scwRuntimeReady = '1'" in JS

def test_backend_authority_and_visualization_contract_preserved():
    assert 'SCWorkspaceBackendAuthority' in COMPAT
    assert 'SCWorkspaceCommandQuery' in COMPAT
    assert 'SCWorkspaceNotebookOrchestration' in COMPAT
    assert 'SCWorkspaceScientificStudyPackages' in COMPAT
    assert 'SCWorkspaceVisualizationSpecifications' in COMPAT
