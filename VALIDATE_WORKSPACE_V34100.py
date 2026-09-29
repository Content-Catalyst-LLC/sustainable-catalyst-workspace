#!/usr/bin/env python3
from pathlib import Path
import sys,json
root=Path(sys.argv[1] if len(sys.argv)>1 else Path.home()/"Downloads/sustainable-catalyst-workspace").expanduser().resolve()
checks=[]
def need(rel,token):
 p=root/rel
 if not p.is_file(): raise SystemExit(f'ERROR: missing {rel}')
 text=p.read_text(errors='replace')
 if token not in text: raise SystemExit(f'ERROR: {token!r} missing from {rel}')
 checks.append(rel)
need('backend/app/config.py','service_version: str = "3.41.0"')
need('backend/neural-runtime/service.py','SERVICE_VERSION = "3.41.0"')
need('backend/neural-runtime/service.py','workspace.neural.distributed-execution-receipt')
need('backend/app/polyglot.py','workspace.neural.distributed-dispatch-plan')
need('backend/app/polyglot.py','workspaceDistributedNeuralArtifact')
need('backend/app/main.py','"neuralRuntimeBoundedOperations": 117')
need('backend/tests/test_distributed_neural_execution_worker_fabric_v34100.py','test_retry_failover_and_execution_receipt')
need('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php',"SC_WORKSPACE_VERSION', '3.41.0")
need('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php','workspace-v3.41.0.js')
manifest=json.loads((root/'release-manifest-v3.41.0.json').read_text())
if manifest.get('databaseMigration') is not False or manifest.get('neuralRuntimeOperations')!=117: raise SystemExit('ERROR: release manifest contract mismatch')
print('PASS: Workspace v3.41.0 Distributed Neural Execution & Worker Fabric validation')
print('WORKSPACE_V34100_NEURAL_RUNTIME_OPERATIONS=117')
print('WORKSPACE_V34100_DATABASE_MIGRATION=false')
