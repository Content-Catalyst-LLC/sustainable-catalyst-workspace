from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'
PHP=(WP/'includes/class-sc-workspace.php').read_text(); PLUGIN=(WP/'sustainable-catalyst-workspace.php').read_text(); MAIN=(WP/'assets/js/workspace-v2.35.0.js').read_text(); TYPED=(WP/'assets/js/sc-workspace-typed-client-v2350.js').read_text(); GENERATED=(ROOT/'frontend/typed-client/src/00-generated-contracts.ts').read_text()
def test_release_identity_and_assets():
    assert 'Version: 2.35.0' in PLUGIN and "const WORKSPACE_RELEASE = '2.35.0';" in MAIN
    assert 'workspace-v2.35.0.js' in PHP and 'workspace-v2.35.0.css' in PHP and 'sc-workspace-typed-client-v2350.js' in PHP
def test_typed_client_loads_before_main_runtime():
    typed=PHP.index("'sc-workspace-typed-client-v2350'"); main=PHP.index("'sc-workspace-v241'",typed); assert typed<main
    main_block=PHP[main:PHP.index('SC_WORKSPACE_VERSION',main)]; assert 'sc-workspace-typed-client-v2350' in main_block
def test_browser_never_receives_backend_service_token():
    assert 'SC_WORKSPACE_BACKEND_TOKEN' not in TYPED and 'serviceCredentialsBrowserVisible: false' in TYPED and 'browserDirectBackendAccess: false' in TYPED
    assert "transport:'wordpress-server-proxy'" in MAIN
def test_generated_contract_has_bounded_commands_queries_and_hash():
    assert 'type WorkspaceCommand =' in GENERATED and "'project.put'" in GENERATED and "'job.retry'" in GENERATED
    assert 'type WorkspaceQuery =' in GENERATED and "'workspace.overview'" in GENERATED and re.search(r"SCW_OPENAPI_PROJECTION_SHA256 = '[a-f0-9]{64}'",GENERATED)
def test_typed_client_exposes_core_backend_adapters():
    for name in ('executeCommand','executeQuery','workspaceOverview','createNotebookPlan','createStudyPackage','storeVisualization'): assert name in TYPED
    assert 'SCWorkspaceTypedClient' in TYPED and 'SCWorkspaceApi' in TYPED
def test_working_interaction_repair_is_preserved():
    assert 'SCWorkspaceInteractionRuntime' in MAIN and "root.dataset.scwRuntimeReady = '1'" in MAIN and 'SCWorkspaceInteractionRepair' in MAIN
