#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); requirements=(root/'backend/neural-runtime/requirements.txt').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.27.0"' in config,'backend version is not 3.27.0')
req('"workspaceVersion": "3.27.0"' in client,'typed client backend contract is not 3.27.0')
req('SERVICE_VERSION = "3.27.0"' in neural,'neural runtime version is not 3.27.0')
ops=['workspace.neural.infer-regression','workspace.neural.infer-binary','workspace.neural.infer-multiclass','workspace.neural.prediction-inspect']
for op in ops: req(op in neural and op in poly,f'inference operation missing: {op}')
req('PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-prediction-artifact/1.0"' in neural,'prediction artifact schema missing')
for sym in ['_infer_regression','_infer_binary','_infer_multiclass','_prediction_inspect','_validate_prediction_artifact','inferenceDatasetFingerprint','evidenceBoundary']:
    req(sym in neural or sym in poly,f'inference/provenance implementation incomplete: {sym}')
req('inference operations do not accept targets' in neural,'inference/evaluation boundary missing')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
req('"neuralRuntimeBoundedOperations": 31' in main,'Workspace neural operation count is not 31')
req('"neuralInferencePredictionProvenanceRuntime": True' in main,'Workspace neural inference capability missing')
req('application/vnd.sc.workspace.neural-prediction+json' in poly,'Workspace prediction media type missing')
req('neuralInferencePredictionProvenance' in poly and 'workspacePredictionArtifactId' in poly,'polyglot prediction receipt lineage missing')
for env in ['SC_WORKSPACE_NEURAL_MAX_INFERENCE_ROWS','SC_WORKSPACE_NEURAL_MAX_PREDICTION_OUTPUTS']:
    req(env in compose,f'bounded inference Compose limit missing: {env}')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('numpy==2.2.6' in requirements and 'torch==2.10.0' in requirements,'neural dependency pins changed unexpectedly')
req('Version: 3.27.0' in plugin and "SC_WORKSPACE_VERSION', '3.27.0'" in plugin,'WordPress version mismatch')
for asset in ['workspace-v3.27.0.css','workspace-v3.27.0.js','sc-workspace-typed-client-v32700.js']:
    req((root/'wordpress/sustainable-catalyst-workspace/assets'/('css' if asset.endswith('.css') else 'js')/asset).exists(),f'WordPress asset missing: {asset}')
req('workspace-v3.27.0.css' in klass and 'workspace-v3.27.0.js' in klass and 'sc-workspace-typed-client-v32700' in klass,'WordPress enqueue references stale')
print('PASS: Workspace v3.27.0 neural inference and prediction provenance validation')
