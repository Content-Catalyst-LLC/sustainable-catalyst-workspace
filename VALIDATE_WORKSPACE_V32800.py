#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); requirements=(root/'backend/neural-runtime/requirements.txt').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.28.0"' in config,'backend version is not 3.28.0')
req('"workspaceVersion": "3.28.0"' in client,'typed client backend contract is not 3.28.0')
req('SERVICE_VERSION = "3.28.0"' in neural,'neural runtime version is not 3.28.0')
ops=['workspace.neural.package-create','workspace.neural.package-verify','workspace.neural.package-inspect','workspace.neural.package-infer']
for op in ops: req(op in neural and op in poly,f'model package operation missing: {op}')
req('MODEL_PACKAGE_SCHEMA = "sc-workspace-neural-model-package/1.0"' in neural,'model package schema missing')
req('MODEL_PACKAGE_MANIFEST_SCHEMA = "sc-workspace-neural-model-package-manifest/1.0"' in neural,'model package manifest schema missing')
req('MODEL_PACKAGE_FORMAT = "sc-workspace-neural-reproducible-model-package/1.0"' in neural,'model package format missing')
for sym in ['_model_package_create','_model_package_verify','_model_package_inspect','_model_package_infer','_validate_model_package','requiredDependencyPins','sourceModelPackageFingerprint']:
    req(sym in neural or sym in poly,f'model package implementation incomplete: {sym}')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
req('"neuralRuntimeBoundedOperations": 35' in main,'Workspace neural operation count is not 35')
req('"neuralReproducibleModelPackagesRuntime": True' in main,'Workspace model package capability missing')
req('application/vnd.sc.workspace.neural-model-package+json' in poly,'Workspace model package media type missing')
req('neuralReproducibleModelPackage' in poly and 'workspaceModelPackageArtifactId' in poly,'polyglot model package receipt lineage missing')
req('workspace.neural.package-infer' in poly and 'sourceModelPackageFingerprint' in poly,'packaged inference provenance missing')
req('SC_WORKSPACE_NEURAL_MAX_PACKAGE_FEATURE_NAMES' in compose,'bounded package feature-name limit missing')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('numpy==2.2.6' in requirements and 'torch==2.10.0' in requirements,'neural dependency pins changed unexpectedly')
req('Version: 3.28.0' in plugin and "SC_WORKSPACE_VERSION', '3.28.0'" in plugin,'WordPress version mismatch')
for asset in ['workspace-v3.28.0.css','workspace-v3.28.0.js','sc-workspace-typed-client-v32800.js']:
    req((root/'wordpress/sustainable-catalyst-workspace/assets'/('css' if asset.endswith('.css') else 'js')/asset).exists(),f'WordPress asset missing: {asset}')
req('workspace-v3.28.0.css' in klass and 'workspace-v3.28.0.js' in klass and 'sc-workspace-typed-client-v32800' in klass,'WordPress enqueue references stale')
print('PASS: Workspace v3.28.0 reproducible neural model package validation')
