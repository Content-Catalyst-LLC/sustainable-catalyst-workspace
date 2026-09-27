#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
errors=[]
def req(c,m):
    if not c: errors.append(m)

config=(root/'backend/app/config.py').read_text()
client=(root/'backend/app/client_contracts.py').read_text()
poly=(root/'backend/app/polyglot.py').read_text()
main=(root/'backend/app/main.py').read_text()
neural=(root/'backend/neural-runtime/service.py').read_text()
wp=root/'wordpress/sustainable-catalyst-workspace'
plugin=(wp/'sustainable-catalyst-workspace.php').read_text()
klass=(wp/'includes/class-sc-workspace.php').read_text()
deployment=(wp/'includes/class-sc-workspace-deployment.php').read_text()
req('service_version: str = "3.21.0"' in config,'backend version is not 3.21.0')
req('"workspaceVersion": "3.21.0"' in client,'typed client backend contract is not 3.21.0')
req('SERVICE_VERSION = "3.21.0"' in neural,'neural runtime version is not 3.21.0')
for op in ['tensor-contract','dataset-manifest','batch-plan','transformation-apply']:
    req(f'workspace.neural.{op}' in neural,f'neural runtime missing {op}')
    req(f'workspace.neural.{op}' in poly,f'polyglot registry missing {op}')
req('"neuralRuntimeBoundedOperations": 8' in main,'backend health does not report 8 neural operations')
req('"neuralTensorDatasetTransformationInterchange": True' in main,'backend health missing interchange capability')
req('trainingEnabled": False' in neural,'neural training must remain disabled')
req('externalDatasetReadEnabled": False' in neural,'neural external dataset reads must remain disabled')
req(' * Version: 3.21.0' in plugin,'WordPress plugin header is not 3.21.0')
req("define('SC_WORKSPACE_VERSION', '3.21.0');" in plugin,'SC_WORKSPACE_VERSION is not 3.21.0')
for rel in ['assets/js/workspace-v3.21.0.js','assets/css/workspace-v3.21.0.css','assets/js/sc-workspace-typed-client-v32100.js']:
    f=wp/rel; req(f.is_file() and f.stat().st_size>0,f'missing/empty WordPress asset: {rel}')
req("assets/js/workspace-v3.21.0.js" in klass,'WordPress enqueue does not use v3.21.0 JS shell')
req("assets/css/workspace-v3.21.0.css" in klass,'WordPress enqueue does not use v3.21.0 CSS shell')
req("sc-workspace-typed-client-v32100" in klass,'WordPress does not enqueue v3.21 typed client')
req("'current_script' => 'assets/js/workspace-v' . SC_WORKSPACE_VERSION . '.js'" in deployment,'stable package script contract changed')
req("'current_style' => 'assets/css/workspace-v' . SC_WORKSPACE_VERSION . '.css'" in deployment,'stable package style contract changed')
manifest=root/'release-manifest-v3.21.0.json'; req(manifest.is_file(),'release manifest missing')
if manifest.is_file():
    d=json.loads(manifest.read_text()); req(d.get('version')=='3.21.0','manifest version mismatch'); req(d.get('backendVersion')=='3.21.0','manifest backend mismatch'); req(d.get('databaseMigrationRequired') is False,'unexpected DB migration')
# Ensure no sensitive environment payload is packaged in tree.
for f in root.rglob('.env'):
    if '.git' not in f.parts: errors.append(f'forbidden .env in release tree: {f}')
if errors:
    [print('FAIL:',e) for e in errors]; raise SystemExit(1)
print('PASS: Workspace v3.21.0 neural dataset/tensor/transformation interchange validation')
