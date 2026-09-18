#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]; WP=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(WP/'assets/js/workspace-v2.31.0.js').read_text(); typed=(WP/'assets/js/sc-workspace-typed-client-v2310.js').read_text(); php=(WP/'includes/class-sc-workspace.php').read_text(); ts=(ROOT/'frontend/typed-client/src/30-local-first-sync.ts').read_text(); plugin=(WP/'sustainable-catalyst-workspace.php').read_text()
assert 'Version: 2.31.0' in plugin and "const WORKSPACE_RELEASE = '2.31.0';" in main
assert 'SCWorkspaceInteractionRuntime' in main and 'SCWorkspaceInteractionRepair' in main
assert 'SCWorkspaceLocalFirstSyncBoundary' in main and 'offlineOutboxAuthoritative:false' in main
assert 'sc-workspace-typed-client-v2310.js' in php and 'workspace-v2.31.0.js' in php and 'workspace-v2.31.0.css' in php
assert 'syncEnvelope' in typed and 'syncReconcile' in typed and 'SCWorkspaceLocalFirstSync' in typed
assert 'sc_workspace_sync_outbox_v2310' in ts and 'pendingMutationsAreDrafts:true' in ts and 'automaticSemanticMerge:false' in ts
assert 'SC_WORKSPACE_BACKEND_TOKEN' not in typed
subprocess.run([sys.executable,str(ROOT/'scripts/generate_typed_client_contracts_v2310.py'),'--check'],cwd=ROOT,check=True,env={**os.environ,'PYTHONPATH':str(ROOT/'backend')})
print('PASS: v2.31.0 local-first synchronization protocol contract')
