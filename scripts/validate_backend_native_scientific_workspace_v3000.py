#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'; JS=WP/'assets/js'; CSS=WP/'assets/css'
main=(JS/'workspace-v3.0.0.js').read_text(); compat=(JS/'sc-workspace-local-project-compat-v3000.js').read_text(); typed=(JS/'sc-workspace-typed-client-v3000.js').read_text()
php=(WP/'includes/class-sc-workspace.php').read_text(); deployment=(WP/'includes/class-sc-workspace-deployment.php').read_text(); cert=(WP/'includes/class-sc-workspace-production-certification.php').read_text()
manifest=json.loads((ROOT/'release-manifest-v3.0.0.json').read_text())
assert len(main.splitlines()) < 140 and "mode:'thin-shell'" in main
assert 'SCWorkspaceInteractionRepair' in main and "version:'2.28.1'" in main
assert 'SCWorkspaceBackendNativeBoundary' in main
assert "const WORKSPACE_RELEASE = '3.0.0';" in compat
assert [x.name for x in JS.glob('workspace-v*.js')]==['workspace-v3.0.0.js']
assert [x.name for x in CSS.glob('workspace-v*.css')]==['workspace-v3.0.0.css']
assert 'sc-workspace-typed-client-v3000.js' in deployment and 'sc-workspace-local-project-compat-v3000.js' in deployment
assert "SC_WORKSPACE_VERSION . '.js'" in deployment and "SC_WORKSPACE_VERSION . '.css'" in deployment
assert '/backend/backend-native-workspace' in php and "'/v1/backend-native-workspace'" in php
assert '/backend/backend-native-workspace/bootstrap' in php and "'/v1/backend-native-workspace/bootstrap'" in php
assert 'SCWorkspaceBackendNativeScientificWorkspace' in typed and 'backendNativeBootstrap' in typed
assert "'rollback_release' => self::ROLLBACK_RELEASE" in cert
assert manifest['version']=='3.0.0' and manifest['migration'] is None
assert manifest['migrationLineage']=='031_backend_policy_identity_authorization_consolidation.sql'
assert manifest['rollbackBaseline']=='2.36.0'
assert manifest['backendFirst'] is True and manifest['arbitraryCodeExecution'] is False
print('PASS: v3.0.0 backend-native scientific workspace release contract')
