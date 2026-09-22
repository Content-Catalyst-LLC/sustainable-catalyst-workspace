#!/usr/bin/env python3
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
manifest=json.loads((ROOT/'release-manifest-v3.1.0.json').read_text())
main=(ROOT/'backend/app/main.py').read_text()
module=(ROOT/'backend/app/platform_core_runtime.py').read_text()
migration=(ROOT/'backend/migrations/032_platform_core_v3_unified_research_runtime_integration.sql').read_text()
php=(WP/'includes/class-sc-workspace.php').read_text()
plugin=(WP/'sustainable-catalyst-workspace.php').read_text()
typed=(WP/'assets/js/sc-workspace-typed-client-v3100.js').read_text()
boundary=(WP/'assets/js/sc-workspace-platform-core-runtime-v3100.js').read_text()
compose=(ROOT/'backend/docker-compose.example.yml').read_text()
deploy=(ROOT/'backend/deploy_workspace_backend_v3_1_0_vps.sh').read_text()
assert manifest['version']=='3.1.0' and manifest['backendFirst'] is True
assert manifest['migration']=='032_platform_core_v3_unified_research_runtime_integration.sql'
assert manifest['rollbackBaseline']=='3.0.0'
assert manifest['platformCore']['contract']=='sc.research.unified-research-scientific-investigation-runtime.v1'
assert manifest['security']['coreCredentialBrowserVisible'] is False
assert 'workspace_platform_core_research_sessions' in migration and 'workspace_platform_core_runtime_receipts' in migration
assert 'GRANT SELECT,INSERT,UPDATE,DELETE' in migration
for route in ('/v1/platform-core-runtime/readiness','/v1/platform-core-runtime/sessions','/v1/platform-core-runtime/object-bindings','/v1/platform-core-runtime/execution-bindings','/v1/platform-core-runtime/visual-bindings','/v1/platform-core-runtime/package-bindings','/v1/platform-core-runtime/handoff-bindings'):
    assert route in main, route
assert 'referenceFirst' in module and 'objectContentReplicatedToCore' in module
assert 'coreExecutesWorkspaceScientificWork' in module and 'coreAuthorizesWorkspaceUsers' in module
assert 'X-SC-API-Key' in module and 'platform_core_write_api_key' in module
assert 'SC_WORKSPACE_PLATFORM_CORE_WRITE_API_KEY' not in php
assert 'SC_CORE_WRITE_API_KEY' not in php
assert 'Version: 3.1.0' in plugin
assert 'sc-workspace-typed-client-v3100.js' in php
assert 'sc-workspace-platform-core-runtime-v3100.js' in php
assert "SCW_TYPED_CONTRACT_VERSION = '3.1.0'" in typed
assert 'platformCoreSessionCreate' in typed and 'platformCoreExecutionBind' in typed
assert 'browserDirectCoreAccess:false' in boundary and 'coreCredentialBrowserVisible:false' in boundary
assert 'SC_WORKSPACE_PLATFORM_CORE_URL' in compose and 'SC_WORKSPACE_PLATFORM_CORE_WRITE_API_KEY' in compose
assert 'sc-core' in deploy and '032_platform_core_v3_unified_research_runtime_integration.sql' in deploy
assert 'v1/platform-core-runtime/readiness' in deploy
print('PASS: Workspace v3.1.0 Platform Core v3 Unified Research Runtime Integration release contract')
