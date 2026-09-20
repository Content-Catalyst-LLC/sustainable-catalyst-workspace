#!/usr/bin/env python3
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'; JS=WP/'assets/js'; CSS=WP/'assets/css'
main=(JS/'workspace-v2.36.0.js').read_text(); compat=(JS/'sc-workspace-local-project-compat-v2360.js').read_text(); typed=(JS/'sc-workspace-typed-client-v2360.js').read_text()
php=(WP/'includes/class-sc-workspace.php').read_text(); deployment=(WP/'includes/class-sc-workspace-deployment.php').read_text(); cert=(WP/'includes/class-sc-workspace-production-certification.php').read_text()
manifest=json.loads((ROOT/'release-manifest-v2.36.0.json').read_text())
assert len(main.splitlines()) < 120 and "mode:'thin-shell'" in main
assert 'SCWorkspaceInteractionRepair' in main and "version:'2.28.1'" in main
assert "const WORKSPACE_RELEASE = '2.36.0';" in compat
assert [x.name for x in JS.glob('workspace-v*.js')]==['workspace-v2.36.0.js']
assert [x.name for x in CSS.glob('workspace-v*.css')]==['workspace-v2.36.0.css']
assert 'sc-workspace-typed-client-v2360.js' in deployment and 'sc-workspace-local-project-compat-v2360.js' in deployment
assert "SC_WORKSPACE_VERSION . '.js'" in deployment and "SC_WORKSPACE_VERSION . '.css'" in deployment
assert '/backend/production-certification' in php and "'/v1/production-certification'" in php
assert 'SCWorkspaceProductionArchitectureBoundary' in typed and 'productionCertification' in typed
assert "'architecture_certification' => true" in cert and "'live_production_certification' => false" in cert
assert manifest['version']=='2.36.0' and manifest['migration'] is None
assert manifest['migrationLineage']=='031_backend_policy_identity_authorization_consolidation.sql'
assert manifest['backendFirst'] is True and manifest['arbitraryCodeExecution'] is False
print('PASS: v2.36.0 production architecture certification release contract')
