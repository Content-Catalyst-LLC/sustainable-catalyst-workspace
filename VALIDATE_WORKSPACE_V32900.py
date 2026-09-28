#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); gpu=(root/'backend/docker-compose.neural-gpu.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.29.0"' in config,'backend version is not 3.29.0')
req('"workspaceVersion": "3.29.0"' in client,'typed client backend contract is not 3.29.0')
req('SERVICE_VERSION = "3.29.0"' in neural,'neural runtime version is not 3.29.0')
ops=['workspace.neural.device-inventory','workspace.neural.device-plan','workspace.neural.device-verify','workspace.neural.accelerator-smoke']
for op in ops: req(op in neural and op in poly,f'device orchestration operation missing: {op}')
for sym in ['DEVICE_PLAN_SCHEMA = "sc-workspace-neural-device-plan/1.0"','DEVICE_INVENTORY_SCHEMA = "sc-workspace-neural-device-inventory/1.0"','_resolve_device_plan','_validate_device_plan','_accelerator_smoke','ContextVar']:
    req(sym in neural,f'device orchestration implementation missing: {sym}')
req('"neuralRuntimeBoundedOperations": 39' in main,'Workspace neural operation count is not 39')
req('"neuralAcceleratorDeviceOrchestrationRuntime": True' in main,'Workspace accelerator/device capability missing')
req('"neuralRuntimeDevicePolicy": "governed-explicit-device-orchestration"' in main,'Workspace device policy mismatch')
req('neuralDeviceOrchestration' in poly and 'devicePlanFingerprint' in poly and 'selectedDevice' in poly,'polyglot device receipt lineage missing')
for key in ['SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED','SC_WORKSPACE_NEURAL_ALLOWED_DEVICES','SC_WORKSPACE_NEURAL_MAX_ACCELERATOR_DEVICES']:
    req(key in compose,f'compose device policy missing: {key}')
req('gpus: all' in gpu and 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED: "true"' in gpu,'optional GPU compose override incomplete')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('Version: 3.29.0' in plugin and "SC_WORKSPACE_VERSION', '3.29.0'" in plugin,'WordPress version mismatch')
for asset in ['workspace-v3.29.0.css','workspace-v3.29.0.js','sc-workspace-typed-client-v32900.js']:
    req((root/'wordpress/sustainable-catalyst-workspace/assets'/('css' if asset.endswith('.css') else 'js')/asset).exists(),f'WordPress asset missing: {asset}')
req('workspace-v3.29.0.css' in klass and 'workspace-v3.29.0.js' in klass and 'sc-workspace-typed-client-v32900' in klass,'WordPress enqueue references stale')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
print('PASS: Workspace v3.29.0 accelerator and device orchestration validation')
