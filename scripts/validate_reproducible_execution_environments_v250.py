#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
if 'Version: 2.5.0' not in plugin or "SC_WORKSPACE_VERSION', '2.5.0" not in plugin: errors.append('WordPress plugin version is not v2.5.0')
for p in ['backend/app/environments.py','backend/migrations/005_reproducible_execution_environments.sql','tests/test_reproducible_execution_environments_v250.py','schemas/sc-workspace-execution-environment-registry-v1.schema.json']:
    if not (ROOT/p).is_file(): errors.append(f'missing {p}')
main=(ROOT/'backend/app/main.py').read_text(); models=(ROOT/'backend/app/models.py').read_text(); schemas=(ROOT/'backend/app/schemas.py').read_text(); migration=(ROOT/'backend/migrations/005_reproducible_execution_environments.sql').read_text()
for token in ['executionEnvironmentRegistry','dependencyManifests','runtimeVersionCapture','randomSeedCapture','/v1/execution-environments']:
    if token not in main: errors.append(f'main missing {token}')
for token in ['workspace_execution_environment_heads','workspace_execution_environment_revisions','environment_ref','environment_fingerprint']:
    if token not in models: errors.append(f'models missing {token}')
for token in ['ExecutionEnvironmentStoreRequest','environmentRef','environmentVariableNames']:
    if token not in schemas: errors.append(f'schemas missing {token}')
for token in ['GRANT SELECT, INSERT, UPDATE, DELETE','ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS environment_ref']:
    if token not in migration: errors.append(f'migration missing {token}')
manifest=json.loads((ROOT/'release-manifest-v2.5.0.json').read_text())
if manifest.get('version')!='2.5.0' or manifest.get('previous_version')!='2.4.0': errors.append('release manifest lineage incorrect')
contract=json.loads((ROOT/'schemas/sc-workspace-execution-environment-registry-v1.schema.json').read_text())
if contract['properties']['secretEnvironmentValuesCaptured']['const'] is not False: errors.append('secret value policy incorrect')
for p in [ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.5.0.js',ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.5.0.css']:
    if not p.is_file(): errors.append(f'missing asset {p.name}')
if errors:
    print('FAIL — Workspace v2.5.0 Reproducible Execution Environments')
    for e in errors: print(' -',e)
    sys.exit(1)
print('PASS — Workspace v2.5.0 Reproducible Execution Environments & Dependency Manifests validated')
