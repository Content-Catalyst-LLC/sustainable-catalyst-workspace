#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'; JS=WP/'assets/js'; CSS=WP/'assets/css'
main=(JS/'workspace-v2.35.0.js').read_text(); compat=(JS/'sc-workspace-local-project-compat-v2350.js').read_text(); php=(WP/'includes/class-sc-workspace.php').read_text(); deployment=(WP/'includes/class-sc-workspace-deployment.php').read_text()
assert len(main.splitlines()) < 120
assert 'thin-shell' in main and 'SCWorkspaceFrontendRuntime' in main
assert 'loadLocalCompatibility' in main and 'legacyCompatUrl' in php
assert 'SCWorkspaceInteractionRepair' in main and '2.28.1' in main
assert 'browserAuthoritativeState:false' in main and "canonicalMutations:'command-api-only'" in main
assert "SC_WORKSPACE_VERSION . '.js'" in deployment and "SC_WORKSPACE_VERSION . '.css'" in deployment
assert len(list(JS.glob('workspace-v*.js')))==1
assert len(list(CSS.glob('workspace-v*.css')))==1
assert "const WORKSPACE_RELEASE = '2.35.0';" in compat
assert 'sc-workspace-local-project-compat-v2350.js' in deployment
print('PASS: v2.35.0 thin shell, lazy browser-local compatibility, dynamic package checks and historical asset retirement')
