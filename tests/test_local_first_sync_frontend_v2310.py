from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text(); PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text(); MAIN=(WP/'assets/js/workspace-v2.35.0.js').read_text(); TYPED=(WP/'assets/js/sc-workspace-typed-client-v2350.js').read_text(); TS=(ROOT/'frontend/typed-client/src/30-local-first-sync.ts').read_text()
def test_release_identity_and_interaction_runtime_preserved():
 assert 'Version: 2.35.0' in PLUGIN and "const WORKSPACE_RELEASE = '2.35.0';" in MAIN; assert 'SCWorkspaceInteractionRuntime' in MAIN and 'SCWorkspaceInteractionRepair' in MAIN
def test_local_first_outbox_is_explicitly_non_authoritative():
 assert 'sc_workspace_sync_outbox_v2310' in TS; assert 'offlineOutboxAuthoritative:false' in TS; assert 'pendingMutationsAreDrafts:true' in TS; assert 'automaticSemanticMerge:false' in TS
def test_typed_client_exposes_sync_contract():
 for token in ['syncProfile','syncBootstrap','syncEnvelope','syncReconcile','syncReceipts','SCWorkspaceLocalFirstSync'] : assert token in TYPED
def test_wordpress_proxy_allowlists_sync_routes():
 for token in ["'/backend/sync'","'/backend/sync/bootstrap'","'/backend/sync/envelopes'","'/backend/sync/reconcile'","'/backend/sync/receipts'"]: assert token in PHP
def test_main_ui_declares_local_first_boundary_without_canonical_browser_authority():
 assert 'SCWorkspaceLocalFirstSyncBoundary' in MAIN; assert 'offlineOutboxAuthoritative:false' in MAIN; assert 'browserAuthoritativeState:false' in MAIN
