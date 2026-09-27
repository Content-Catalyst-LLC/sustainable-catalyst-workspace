#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()

def req(cond,msg):
    if not cond: raise SystemExit('ERROR: '+msg)

config=(root/'backend/app/config.py').read_text()
client=(root/'backend/app/client_contracts.py').read_text()
poly=(root/'backend/app/polyglot.py').read_text()
neural=(root/'backend/neural-runtime/service.py').read_text()
requirements=(root/'backend/neural-runtime/requirements.txt').read_text()
plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.22.0.1"' in config,'backend version is not 3.22.0.1')
req('"workspaceVersion": "3.22.0.1"' in client,'typed client backend contract is not 3.22.0.1')
req('SERVICE_VERSION = "3.22.0.1"' in neural,'neural runtime version is not 3.22.0.1')
req('import torch._dynamo as _torch_dynamo' in neural,'torch._dynamo preload missing')
req('OPTIMIZER_RUNTIME_WARM = _warm_optimizer_runtime()' in neural,'optimizer warmup missing')
req('_OPTIMIZER_INIT_LOCK = threading.Lock()' in neural,'optimizer initialization lock missing')
req('"torchDynamoPreloaded": True' in neural,'health preload marker missing')
req('"optimizerRuntimeWarm": OPTIMIZER_RUNTIME_WARM' in neural,'health warmup marker missing')
req('numpy==2.2.6' in requirements,'NumPy production dependency is not pinned')
req('torch==2.10.0' in requirements,'PyTorch pin changed unexpectedly')
req('workspace.neural.train-linear' in poly and 'workspace.neural.train-mlp' in poly,'neural training operations missing')
req(' * Version: 3.22.0.1' in plugin,'WordPress plugin header is not 3.22.0.1')
req("define('SC_WORKSPACE_VERSION', '3.22.0.1');" in plugin,'SC_WORKSPACE_VERSION is not 3.22.0.1')
for rel in ['assets/js/workspace-v3.22.0.1.js','assets/css/workspace-v3.22.0.1.css','assets/js/sc-workspace-typed-client-v322001.js']:
    req((root/'wordpress/sustainable-catalyst-workspace'/rel).is_file(),f'missing stable package asset {rel}')
req('assets/js/workspace-v3.22.0.1.js' in klass,'WordPress enqueue does not use v3.22.0.1 JS shell')
req('assets/css/workspace-v3.22.0.1.css' in klass,'WordPress enqueue does not use v3.22.0.1 CSS shell')
req('sc-workspace-typed-client-v322001.js' in klass,'WordPress enqueue does not use v3.22.0.1 typed client')
manifest=root/'release-manifest-v3.22.0.1.json'; req(manifest.is_file(),'release manifest missing')
d=json.loads(manifest.read_text())
req(d.get('version')=='3.22.0.1','manifest version mismatch')
req(d.get('backendVersion')=='3.22.0.1','manifest backend mismatch')
req(d.get('databaseMigrationRequired') is False,'unexpected DB migration')
n=d.get('neuralRuntime') or {}
req(n.get('operations')==11,'manifest neural operation count mismatch')
req(n.get('trainingEnabled') is True,'manifest training flag mismatch')
req(n.get('torchDynamoPreloaded') is True,'manifest Dynamo repair missing')
req(n.get('optimizerRuntimeWarm') is True,'manifest optimizer warmup missing')
req(n.get('numpyDependencyPinned')=='2.2.6','manifest NumPy pin mismatch')
req(n.get('checkpointPersistenceEnabled') is False,'checkpoint persistence unexpectedly enabled')
req(n.get('resumeTrainingEnabled') is False,'resume unexpectedly enabled')
req(n.get('acceleratorExecutionEnabled') is False,'accelerator unexpectedly enabled')
print('PASS: Workspace v3.22.0.1 neural training runtime production repair validation')
