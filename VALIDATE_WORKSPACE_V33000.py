#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.30.0"' in config,'backend version is not 3.30.0')
req('"workspaceVersion": "3.30.0"' in client,'typed client backend contract is not 3.30.0')
req('SERVICE_VERSION = "3.30.0"' in neural,'neural runtime version is not 3.30.0')
ops=['workspace.neural.trial-plan','workspace.neural.trial-execute','workspace.neural.batch-execute','workspace.neural.hyperparameter-grid','workspace.neural.hyperparameter-random']
for op in ops: req(op in neural and op in poly,f'trial/search operation missing: {op}')
for sym in ['NEURAL_TRIAL_SCHEMA = "sc-workspace-neural-trial-artifact/1.0"','NEURAL_BATCH_SCHEMA = "sc-workspace-neural-batch-artifact/1.0"','NEURAL_SEARCH_SCHEMA = "sc-workspace-neural-hyperparameter-search-artifact/1.0"','MAX_NEURAL_BATCH_TRIALS','MAX_NEURAL_SEARCH_EPOCHS','ALLOWED_HYPERPARAMETER_PATHS','_hyperparameter_grid','_hyperparameter_random']:
    req(sym in neural,f'v3.30 implementation missing: {sym}')
req('"neuralRuntimeBoundedOperations": 44' in main,'Workspace neural operation count is not 44')
req('"neuralBatchTrialHyperparameterExecutionRuntime": True' in main,'Workspace v3.30 capability missing')
for media in ['application/vnd.sc.workspace.neural-trial+json','application/vnd.sc.workspace.neural-batch+json','application/vnd.sc.workspace.neural-hyperparameter-search+json']:
    req(media in poly,f'Workspace artifact persistence missing: {media}')
req('neuralBatchTrialHyperparameterExecution' in poly and 'bestTrialArtifactFingerprint' in poly and 'workspaceTrialSearchArtifactId' in poly,'trial/search receipt lineage missing')
req('SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED' in compose,'v3.29 device policy was not preserved')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('Version: 3.30.0' in plugin and "SC_WORKSPACE_VERSION', '3.30.0'" in plugin,'WordPress version mismatch')
for asset in ['workspace-v3.30.0.css','workspace-v3.30.0.js','sc-workspace-typed-client-v33000.js']:
    req((root/'wordpress/sustainable-catalyst-workspace/assets'/('css' if asset.endswith('.css') else 'js')/asset).exists(),f'WordPress asset missing: {asset}')
req('workspace-v3.30.0.css' in klass and 'workspace-v3.30.0.js' in klass and 'sc-workspace-typed-client-v33000' in klass,'WordPress enqueue references stale')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
print('PASS: Workspace v3.30.0 neural batch, trial, and hyperparameter execution validation')
