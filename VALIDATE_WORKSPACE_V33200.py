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
req('backend/app/config.py','service_version: str = "3.32.0"')
req('backend/app/client_contracts.py','"workspaceVersion": "3.32.0"')
req('backend/app/main.py','"neuralRuntimeBoundedOperations": 52','"neuralRuntimeProductionCertification": True','sc-workspace-neural-production-certification-artifact/1.0')
req('backend/app/polyglot.py','workspace.neural.certification-plan','workspace.neural.certification-execute','workspace.neural.certification-verify','workspace.neural.certification-report','application/vnd.sc.workspace.neural-production-certification+json','workspaceProductionCertificationArtifactId')
req('backend/neural-runtime/service.py','SERVICE_VERSION = "3.32.0"','PRODUCTION_CERTIFICATION_PROFILE','PRODUCTION_CERTIFICATION_PLAN_SCHEMA','PRODUCTION_CERTIFICATION_ARTIFACT_SCHEMA','PRODUCTION_CERTIFICATION_REPORT_SCHEMA')
for op in ['certification-plan','certification-execute','certification-verify','certification-report']:
    req('backend/neural-runtime/service.py',f'workspace.neural.{op}')
req('backend/tests/test_neural_runtime_production_certification_v33200.py','test_certification_execute_passes_required_checks_and_is_honest_about_remote_gpu','test_certification_verify_detects_tampering','test_workspace_registry_persistence_and_typed_contract_expose_v332')
req('frontend/typed-client/src/00-generated-contracts.ts','3.32.0')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.32.0',"SC_WORKSPACE_VERSION', '3.32.0")
req('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php','workspace-v3.32.0.css','workspace-v3.32.0.js','sc-workspace-typed-client-v33200.js')
req('wordpress/sustainable-catalyst-workspace/assets/css/workspace-v3.32.0.css')
req('wordpress/sustainable-catalyst-workspace/assets/js/workspace-v3.32.0.js')
req('wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v33200.js')
req('scripts/generate_typed_client_contracts_v33200.py','3.32.0')
req('NEURAL_RUNTIME_PRODUCTION_CERTIFICATION_V33200.md','Neural Runtime Production Certification')
print('PASS: Workspace v3.32.0 neural runtime production certification validation')
print(f'VALIDATED_WORKSPACE_V33200_FILES={len(set(checks))}')
