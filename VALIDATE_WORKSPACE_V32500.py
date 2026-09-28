#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(cond,msg):
    if not cond: raise SystemExit('ERROR: '+msg)
config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); requirements=(root/'backend/neural-runtime/requirements.txt').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.25.0"' in config,'backend version is not 3.25.0')
req('"workspaceVersion": "3.25.0"' in client,'typed client backend contract is not 3.25.0')
req('SERVICE_VERSION = "3.25.0"' in neural,'neural runtime version is not 3.25.0')
ops=['workspace.neural.explain-gradient','workspace.neural.explain-integrated-gradients','workspace.neural.explain-occlusion','workspace.neural.explain-global-sensitivity']
for op in ops: req(op in neural and op in poly,f'neural explainability operation missing: {op}')
req('EXPLAINABILITY_ARTIFACT_SCHEMA = "sc-workspace-neural-explainability-artifact/1.0"' in neural,'explainability artifact schema missing')
for symbol in ['_explain_gradient','_explain_integrated_gradients','_explain_occlusion','_explain_global_sensitivity','completenessDelta','meanAbsoluteGradient']:
    req(symbol in neural,f'explainability implementation incomplete: {symbol}')
req('register_forward_hook' not in neural and 'register_backward_hook' not in neural and '.register_hook(' not in neural,'dynamic neural hooks unexpectedly enabled')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
req('"neuralRuntimeBoundedOperations": 23' in main,'Workspace neural operation count is not 23')
req('"neuralExplainabilityRuntime": True' in main,'Workspace neural explainability capability flag missing')
req('application/vnd.sc.workspace.neural-explainability+json' in poly,'Workspace explainability media type missing')
req('neuralExplainability' in poly and 'explainabilityMethod' in poly and 'explanationDatasetFingerprint' in poly,'polyglot explainability receipt lineage missing')
for env in ['SC_WORKSPACE_NEURAL_MAX_EXPLAINABILITY_ROWS','SC_WORKSPACE_NEURAL_MAX_EXPLAINABILITY_FEATURES','SC_WORKSPACE_NEURAL_MAX_IG_STEPS']:
    req(env in compose,f'bounded explainability Compose limit missing: {env}')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('numpy==2.2.6' in requirements and 'torch==2.10.0' in requirements,'neural dependency pins changed unexpectedly')
req(' * Version: 3.25.0' in plugin,'WordPress plugin header is not 3.25.0')
req("define('SC_WORKSPACE_VERSION', '3.25.0');" in plugin,'SC_WORKSPACE_VERSION is not 3.25.0')
for rel in ['assets/js/workspace-v3.25.0.js','assets/css/workspace-v3.25.0.css','assets/js/sc-workspace-typed-client-v32500.js']:
    req((root/'wordpress/sustainable-catalyst-workspace'/rel).is_file(),f'missing stable package asset {rel}')
req('assets/js/workspace-v3.25.0.js' in klass,'WordPress enqueue does not use v3.25.0 JS shell')
req('assets/css/workspace-v3.25.0.css' in klass,'WordPress enqueue does not use v3.25.0 CSS shell')
req('sc-workspace-typed-client-v32500.js' in klass,'WordPress enqueue does not use v3.25.0 typed client')
manifest=root/'release-manifest-v3.25.0.json'; req(manifest.is_file(),'release manifest missing'); d=json.loads(manifest.read_text())
req(d.get('version')=='3.25.0' and d.get('backendVersion')=='3.25.0','manifest version mismatch')
req(d.get('databaseMigrationRequired') is False,'unexpected DB migration')
req(d.get('rollbackBaseline')=='3.24.0','rollback baseline mismatch')
n=d.get('neuralRuntime') or {}; req(n.get('operations')==23,'manifest neural operation count mismatch'); req(n.get('explainabilityRuntimeEnabled') is True,'manifest explainability capability missing'); req(n.get('dynamicHooksAllowed') is False,'dynamic hook boundary changed'); req(n.get('acceleratorExecutionEnabled') is False,'accelerator boundary changed unexpectedly')
req((root/'backend/tests/test_neural_explainability_v32500.py').is_file(),'v3.25 explainability regression test missing')
print('PASS: Workspace v3.25.0 neural explainability compute runtime validation')
