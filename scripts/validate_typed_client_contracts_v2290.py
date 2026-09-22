#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'; main=(WP/'assets/js/workspace-v2.29.0.js').read_text(); typed=(WP/'assets/js/sc-workspace-typed-client-v2290.js').read_text(); php=(WP/'includes/class-sc-workspace.php').read_text()
assert "const WORKSPACE_RELEASE = '2.29.0';" in main and 'SCWorkspaceTypedClientBoundary' in main and 'sc-workspace-typed-client-v2290.js' in php
assert 'SC_WORKSPACE_BACKEND_TOKEN' not in typed and 'serviceCredentialsBrowserVisible: false' in typed and 'browserDirectBackendAccess: false' in typed and 'executeCommand' in typed and 'executeQuery' in typed
assert 'SCWorkspaceInteractionRuntime' in main
subprocess.run([sys.executable,str(ROOT/'scripts/generate_typed_client_contracts_v2290.py'),'--check'],cwd=ROOT,check=True,env={**os.environ,'PYTHONPATH':str(ROOT/'backend')})
print('PASS: v2.29.0 typed client/OpenAPI/WordPress proxy contract')
