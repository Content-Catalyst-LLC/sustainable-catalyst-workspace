#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
checks=[]
def req(rel,*needles):
    p=root/rel
    if not p.is_file(): raise SystemExit(f'ERROR: missing {rel}')
    text=p.read_text(errors='replace')
    for n in needles:
        if n not in text: raise SystemExit(f'ERROR: {rel} missing marker: {n}')
    checks.append(rel)

req('backend/app/config.py','service_version: str = "3.31.0"')
req('backend/app/client_contracts.py','"workspaceVersion": "3.31.0"')
req('backend/app/main.py','"neuralRuntimeBoundedOperations": 48','"neuralRemoteGpuExecutionBroker": True','sc-workspace-neural-remote-execution-artifact/1.0')
req('backend/app/polyglot.py','workspace.neural.remote-worker-inventory','workspace.neural.remote-dispatch-plan','workspace.neural.remote-execute','workspace.neural.remote-receipt-verify','application/vnd.sc.workspace.neural-remote-execution+json','workspaceRemoteExecutionArtifactId')
req('backend/neural-runtime/service.py','SERVICE_VERSION = "3.31.0"','REMOTE_WORKER_INVENTORY_SCHEMA','REMOTE_DISPATCH_PLAN_SCHEMA','REMOTE_EXECUTION_RECEIPT_SCHEMA','REMOTE_EXECUTION_ARTIFACT_SCHEMA','clientSuppliedWorkerUrlsAllowed')
for op in ['remote-worker-inventory','remote-dispatch-plan','remote-execute','remote-receipt-verify']:
    req('backend/neural-runtime/service.py',f'workspace.neural.{op}')
req('backend/docker-compose.example.yml','SC_WORKSPACE_NEURAL_REMOTE_BROKER_ENABLED: ${SC_WORKSPACE_NEURAL_REMOTE_BROKER_ENABLED:-false}','SC_WORKSPACE_NEURAL_REMOTE_WORKER_MODE: ${SC_WORKSPACE_NEURAL_REMOTE_WORKER_MODE:-false}','SC_WORKSPACE_NEURAL_REMOTE_HMAC_SECRET')
req('backend/docker-compose.neural-remote-worker.example.yml','gpus: all','SC_WORKSPACE_NEURAL_REMOTE_WORKER_MODE: "true"','SC_WORKSPACE_NEURAL_REMOTE_WORKER_ID','127.0.0.1:18101:8101')
req('backend/tests/test_neural_remote_gpu_execution_broker_v33100.py','test_remote_execute_validates_signed_worker_response','test_receipt_verification_detects_tampering')
req('frontend/typed-client/src/00-generated-contracts.ts','3.31.0')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.31.0',"SC_WORKSPACE_VERSION', '3.31.0")
req('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php','workspace-v3.31.0.css','workspace-v3.31.0.js','sc-workspace-typed-client-v33100.js')
req('wordpress/sustainable-catalyst-workspace/assets/css/workspace-v3.31.0.css')
req('wordpress/sustainable-catalyst-workspace/assets/js/workspace-v3.31.0.js')
req('wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v33100.js')
req('scripts/generate_typed_client_contracts_v33100.py','3.31.0')
req('NEURAL_REMOTE_GPU_EXECUTION_BROKER_V33100.md','Remote GPU Execution Broker')
req('REMOTE_GPU_WORKER_DEPLOYMENT_V33100.md','Remote GPU Worker Deployment')
print('PASS: Workspace v3.31.0 remote GPU execution broker validation')
print(f'VALIDATED_WORKSPACE_V33100_FILES={len(set(checks))}')
