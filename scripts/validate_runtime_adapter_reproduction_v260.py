#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
if 'Version: 2.6.0' not in plugin or "SC_WORKSPACE_VERSION', '2.6.0" not in plugin: errors.append('WordPress plugin version is not v2.6.0')
for p in ['backend/app/runtime_adapters.py','backend/app/reproduction.py','backend/migrations/006_runtime_adapter_reproduction_verification.sql','tests/test_runtime_adapter_reproduction_v260.py','schemas/sc-workspace-runtime-adapter-reproduction-v1.schema.json']:
    if not (ROOT/p).is_file(): errors.append(f'missing {p}')
main=(ROOT/'backend/app/main.py').read_text(); models=(ROOT/'backend/app/models.py').read_text(); schemas=(ROOT/'backend/app/schemas.py').read_text(); migration=(ROOT/'backend/migrations/006_runtime_adapter_reproduction_verification.sql').read_text()
for token in ['runtimeAdapterRegistry','runtimeCompatibilityChecks','reproductionPlans','reproductionVerification','arbitraryCodeExecution','/v1/runtime-adapters','/v1/reproduction-verifications']:
    if token not in main: errors.append(f'main missing {token}')
for token in ['workspace_runtime_adapter_heads','workspace_runtime_adapter_revisions','workspace_reproduction_plans','workspace_reproduction_verifications','runtime_adapter_ref','runtime_adapter_fingerprint']:
    if token not in models: errors.append(f'models missing {token}')
for token in ['RuntimeAdapterStoreRequest','RuntimeCompatibilityCheckRequest','ReproductionPlanCreateRequest','ReproductionVerificationCreateRequest','runtimeAdapterRef']:
    if token not in schemas: errors.append(f'schemas missing {token}')
for token in ['GRANT SELECT, INSERT, UPDATE, DELETE','ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS runtime_adapter_ref']:
    if token not in migration: errors.append(f'migration missing {token}')
manifest=json.loads((ROOT/'release-manifest-v2.6.0.json').read_text())
if manifest.get('version')!='2.6.0' or manifest.get('previous_version')!='2.5.0': errors.append('release manifest lineage incorrect')
contract=json.loads((ROOT/'schemas/sc-workspace-runtime-adapter-reproduction-v1.schema.json').read_text())
if contract['properties']['arbitraryCodeExecution']['const'] is not False: errors.append('arbitrary execution policy incorrect')
if contract['properties']['automaticReexecution']['const'] is not False: errors.append('automatic reexecution policy incorrect')
for p in [ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.6.0.js',ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.6.0.css']:
    if not p.is_file(): errors.append(f'missing asset {p.name}')
for f in ['wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php','wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php']:
    text=(ROOT/f).read_text()
    if "PREVIOUS_RELEASE = '2.5.0'" not in text or 'workspace-v2.6.0.js' not in text: errors.append(f'release lineage/assets incorrect in {f}')
if errors:
    print('FAIL — Workspace v2.6.0 Runtime Adapter Registry & Reproduction Verification')
    for e in errors: print(' -',e)
    sys.exit(1)
print('PASS — Workspace v2.6.0 Runtime Adapter Registry & Reproduction Verification validated')
