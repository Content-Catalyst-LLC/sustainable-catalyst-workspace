#!/usr/bin/env python3
from pathlib import Path
import json, sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
errors=[]
def req(c,m):
    if not c: errors.append(m)

def text(rel): return (root/rel).read_text()
config=text('backend/app/config.py'); client=text('backend/app/client_contracts.py'); poly=text('backend/app/polyglot.py'); main=text('backend/app/main.py'); neural=text('backend/neural-runtime/service.py')
wp=root/'wordpress/sustainable-catalyst-workspace'; plugin=(wp/'sustainable-catalyst-workspace.php').read_text(); klass=(wp/'includes/class-sc-workspace.php').read_text(); deployment=(wp/'includes/class-sc-workspace-deployment.php').read_text()
req('service_version: str = "3.22.0"' in config,'backend version is not 3.22.0')
req('"workspaceVersion": "3.22.0"' in client,'typed client backend contract is not 3.22.0')
req('SERVICE_VERSION = "3.22.0"' in neural,'neural runtime version is not 3.22.0')
for op in ['tensor-summary','model-summary','linear-forward','mlp-forward','tensor-contract','dataset-manifest','batch-plan','transformation-apply','training-plan','train-linear','train-mlp']:
    req(f'workspace.neural.{op}' in neural,f'neural runtime missing {op}')
    req(f'workspace.neural.{op}' in poly,f'polyglot registry missing {op}')
req('"neuralRuntimeBoundedOperations": 11' in main,'backend health does not report 11 neural operations')
req('"neuralRuntimeTrainingEnabled": True' in main,'backend health does not enable neural training')
req('"neuralTrainingJobRuntime": True' in main,'backend health missing neural training job runtime')
req('"neuralTrainingCheckpointPersistenceEnabled": False' in main,'backend must keep checkpoint persistence disabled')
req('"neuralTrainingResumeEnabled": False' in main,'backend must keep training resume disabled')
req('"checkpointPersistenceEnabled": False' in neural,'neural runtime checkpoint persistence must remain disabled')
req('"resumeTrainingEnabled": False' in neural,'neural runtime resume must remain disabled')
req('"acceleratorExecutionEnabled": False' in neural,'neural runtime accelerators must remain disabled')
req('sc-workspace-neural-training-spec/1.0' in neural,'training spec schema missing')
req('sc-workspace-neural-training-run/1.0' in neural,'training run schema missing')
req('stateDictBase64' in neural and 'torchModuleBase64' in neural,'serialized neural model rejection guard missing')
req('MAX_TRAINING_EPOCHS' in neural and 'MAX_TRAINING_PARAMETERS' in neural and 'MAX_TRAINING_SECONDS' in neural,'training resource bounds missing')
req('neuralTraining' in poly and 'trainedModelSpecFingerprint' in poly,'training receipt enrichment missing')
req(' * Version: 3.22.0' in plugin,'WordPress plugin header is not 3.22.0')
req("define('SC_WORKSPACE_VERSION', '3.22.0');" in plugin,'SC_WORKSPACE_VERSION is not 3.22.0')
for rel in ['assets/js/workspace-v3.22.0.js','assets/css/workspace-v3.22.0.css','assets/js/sc-workspace-typed-client-v32200.js']:
    f=wp/rel; req(f.is_file() and f.stat().st_size>0,f'missing/empty WordPress asset: {rel}')
req('assets/js/workspace-v3.22.0.js' in klass,'WordPress enqueue does not use v3.22.0 JS shell')
req('assets/css/workspace-v3.22.0.css' in klass,'WordPress enqueue does not use v3.22.0 CSS shell')
req('sc-workspace-typed-client-v32200' in klass,'WordPress does not enqueue v3.22 typed client')
req("'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in deployment,'stable package script contract changed')
req("'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in deployment,'stable package style contract changed')
manifest=root/'release-manifest-v3.22.0.json'; req(manifest.is_file(),'release manifest missing')
if manifest.is_file():
    d=json.loads(manifest.read_text()); req(d.get('version')=='3.22.0','manifest version mismatch'); req(d.get('backendVersion')=='3.22.0','manifest backend mismatch'); req(d.get('databaseMigrationRequired') is False,'unexpected DB migration'); n=d.get('neuralRuntime') or {}; req(n.get('operations')==11,'manifest neural operation count mismatch'); req(n.get('trainingEnabled') is True,'manifest training flag mismatch'); req(n.get('checkpointPersistenceEnabled') is False,'manifest checkpoint flag mismatch')
for f in root.rglob('.env'):
    if '.git' not in f.parts: errors.append(f'forbidden .env in release tree: {f}')
if errors:
    [print('FAIL:',e) for e in errors]; raise SystemExit(1)
print('PASS: Workspace v3.22.0 neural training job runtime validation')
