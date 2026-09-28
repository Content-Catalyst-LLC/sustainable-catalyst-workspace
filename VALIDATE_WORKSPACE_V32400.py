#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()

def req(cond,msg):
    if not cond: raise SystemExit('ERROR: '+msg)

config=(root/'backend/app/config.py').read_text(); client=(root/'backend/app/client_contracts.py').read_text(); main=(root/'backend/app/main.py').read_text(); poly=(root/'backend/app/polyglot.py').read_text(); neural=(root/'backend/neural-runtime/service.py').read_text(); compose=(root/'backend/docker-compose.example.yml').read_text(); docker=(root/'backend/neural-runtime/Dockerfile').read_text(); requirements=(root/'backend/neural-runtime/requirements.txt').read_text(); plugin=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); klass=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
req('service_version: str = "3.24.0"' in config,'backend version is not 3.24.0')
req('"workspaceVersion": "3.24.0"' in client,'typed client backend contract is not 3.24.0')
req('SERVICE_VERSION = "3.24.0"' in neural,'neural runtime version is not 3.24.0')
ops=['workspace.neural.evaluate-regression','workspace.neural.evaluate-binary','workspace.neural.evaluate-multiclass','workspace.neural.calibration-report','workspace.neural.uncertainty-summary']
for op in ops: req(op in neural and op in poly,f'neural operation missing: {op}')
req('EVALUATION_ARTIFACT_SCHEMA = "sc-workspace-neural-evaluation-artifact/1.0"' in neural,'evaluation artifact schema missing')
req('CALIBRATION_ARTIFACT_SCHEMA = "sc-workspace-neural-calibration-artifact/1.0"' in neural,'calibration artifact schema missing')
req('UNCERTAINTY_ARTIFACT_SCHEMA = "sc-workspace-neural-uncertainty-artifact/1.0"' in neural,'uncertainty artifact schema missing')
req('_roc_auc_binary' in neural and 'expectedCalibrationError' in neural and 'meanPredictiveEntropy' in neural,'evaluation/calibration/uncertainty implementation incomplete')
req('empirical-residual' in neural,'regression uncertainty method must remain explicitly empirical-residual')
req('checkpoint trained model fingerprint' in neural,'checkpoint/model analysis binding missing')
req('"neuralRuntimeBoundedOperations": 19' in main,'Workspace neural operation count is not 19')
req('"neuralEvaluationCalibrationUncertaintyRuntime": True' in main,'Workspace neural evaluation capability flag missing')
for mt in ['application/vnd.sc.workspace.neural-evaluation+json','application/vnd.sc.workspace.neural-calibration+json','application/vnd.sc.workspace.neural-uncertainty+json']:
    req(mt in poly,f'Workspace neural analysis media type missing: {mt}')
req('outputId":"neural-analysis"' in poly,'execution-run neural analysis output missing')
req('workspaceAnalysisArtifactId' in poly and 'analysisArtifactFingerprint' in poly,'polyglot neural analysis receipt lineage missing')
req('SC_WORKSPACE_NEURAL_MAX_EVALUATION_ROWS' in compose and 'SC_WORKSPACE_NEURAL_MAX_CALIBRATION_BINS' in compose,'bounded neural analysis Compose limits missing')
req('USER 65532:65532' in docker,'numeric runtime UID changed unexpectedly')
req('read_only: true' in compose and 'no-new-privileges:true' in compose,'container hardening changed unexpectedly')
req('numpy==2.2.6' in requirements and 'torch==2.10.0' in requirements,'neural dependency pins changed unexpectedly')
req('torch.save(' not in neural and 'torch.load(' not in neural,'raw torch serialization unexpectedly enabled')
req(' * Version: 3.24.0' in plugin,'WordPress plugin header is not 3.24.0')
req("define('SC_WORKSPACE_VERSION', '3.24.0');" in plugin,'SC_WORKSPACE_VERSION is not 3.24.0')
for rel in ['assets/js/workspace-v3.24.0.js','assets/css/workspace-v3.24.0.css','assets/js/sc-workspace-typed-client-v32400.js']:
    req((root/'wordpress/sustainable-catalyst-workspace'/rel).is_file(),f'missing stable package asset {rel}')
req('assets/js/workspace-v3.24.0.js' in klass,'WordPress enqueue does not use v3.24.0 JS shell')
req('assets/css/workspace-v3.24.0.css' in klass,'WordPress enqueue does not use v3.24.0 CSS shell')
req('sc-workspace-typed-client-v32400.js' in klass,'WordPress enqueue does not use v3.24.0 typed client')
manifest=root/'release-manifest-v3.24.0.json'; req(manifest.is_file(),'release manifest missing'); d=json.loads(manifest.read_text())
req(d.get('version')=='3.24.0' and d.get('backendVersion')=='3.24.0','manifest version mismatch')
req(d.get('databaseMigrationRequired') is False,'unexpected DB migration')
req(d.get('rollbackBaseline')=='3.23.0','rollback baseline mismatch')
n=d.get('neuralRuntime') or {}; req(n.get('operations')==19,'manifest neural operation count mismatch'); req(n.get('evaluationCalibrationUncertaintyEnabled') is True,'manifest neural analysis capability missing'); req(n.get('classificationUncertainty')=='predictive-entropy','manifest classification uncertainty mismatch'); req(n.get('regressionUncertainty')=='empirical-residual','manifest regression uncertainty mismatch'); req(n.get('acceleratorExecutionEnabled') is False,'accelerator boundary changed unexpectedly')
req((root/'backend/tests/test_neural_evaluation_calibration_uncertainty_v32400.py').is_file(),'v3.24 regression test missing')
print('PASS: Workspace v3.24.0 neural evaluation, calibration & uncertainty validation')
