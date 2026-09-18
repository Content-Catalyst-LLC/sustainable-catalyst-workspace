#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
WP=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(WP/'assets/js/workspace-v2.30.0.js').read_text()
typed=(WP/'assets/js/sc-workspace-typed-client-v2300.js').read_text()
php=(WP/'includes/class-sc-workspace.php').read_text()
ts=(ROOT/'frontend/typed-client/src/20-thin-client-state.ts').read_text()
assert "const WORKSPACE_RELEASE = '2.30.0';" in main
assert 'SCWorkspaceInteractionRuntime' in main and 'SCWorkspaceInteractionRepair' in main
assert 'SCWorkspaceThinClientStateBoundary' in main
assert 'sc-workspace-typed-client-v2300.js' in php and 'workspace-v2.30.0.js' in php and 'workspace-v2.30.0.css' in php
assert 'thinClientStateProfile' in typed and 'thinClientBootstrap' in typed and 'SCWorkspaceThinClientState' in typed
assert "persistentBrowserState:'transient-only'" in ts and 'canonicalCachePersistent:false' in ts
assert 'SC_WORKSPACE_BACKEND_TOKEN' not in typed
subprocess.run([sys.executable,str(ROOT/'scripts/generate_typed_client_contracts_v2300.py'),'--check'],cwd=ROOT,check=True,env={**os.environ,'PYTHONPATH':str(ROOT/'backend')})
print('PASS: v2.30.0 thin client state architecture contract')
