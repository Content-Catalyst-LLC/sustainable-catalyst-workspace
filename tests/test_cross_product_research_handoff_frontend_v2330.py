from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text(); PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text(); MAIN=(WP/'assets/js/workspace-v3.0.0.js').read_text(); TYPED=(WP/'assets/js/sc-workspace-typed-client-v3000.js').read_text(); TS=(ROOT/'frontend/typed-client/src/50-cross-product-handoffs.ts').read_text()
def test_release_and_interaction_lineage_preserved():
    assert 'Version: 3.0.0' in PLUGIN and "const WORKSPACE_RELEASE = '3.0.0';" in MAIN; assert 'SCWorkspaceInteractionRuntime' in MAIN and 'SCWorkspaceInteractionRepair' in MAIN
def test_handoff_proxy_and_typed_client_routes_present():
    for text in ['/backend/handoffs/profile','/backend/handoffs','/backend/handoff-receipts']: assert text in PHP
    for text in ["handoffProfile()","createHandoff(request","acceptHandoff(handoffId","handoffReceipts()"]: assert text in TYPED
def test_browser_boundary_is_non_authoritative():
    assert 'SCWorkspaceResearchHandoffBoundary' in MAIN and 'genericDestinationMutation:false' in MAIN; assert 'backendAuthoritative:true' in TS and 'genericDestinationMutation:false' in TS
