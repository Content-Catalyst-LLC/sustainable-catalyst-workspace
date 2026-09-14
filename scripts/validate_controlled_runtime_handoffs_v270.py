#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
required=[
 'backend/app/execution_control.py','backend/migrations/007_controlled_runtime_handoffs.sql',
 'schemas/sc-workspace-controlled-runtime-handoff-v1.schema.json','release-manifest-v2.7.0.json',
 'registry/workspace-product-record-v2.7.0.json','RELEASE_NOTES_2.7.0.md'
]
for rel in required:
    assert (ROOT/rel).is_file(), rel
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
assert 'Version: 2.7.0' in plugin
main=(ROOT/'backend/app/main.py').read_text(); control=(ROOT/'backend/app/execution_control.py').read_text(); wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
for token in ['/v1/reproduction-execution-plans','/v1/runtime-handoff-receipts','humanAuthorizedDispatch','clientSuppliedRuntimeUrlsAllowed']:
    assert token in main or token in control
for token in ['humanAuthorizationRequired','automaticDispatch','serverConfiguredRouteOnly','clientSuppliedRouteUrlAllowed','arbitraryCodeExecution']:
    assert token in control
assert 'url:' not in control.lower()
for token in ['backend-reproduction-execution-plans','backend-runtime-handoff-receipts']:
    assert token in wp
schema=json.loads((ROOT/'schemas/sc-workspace-controlled-runtime-handoff-v1.schema.json').read_text())
assert schema['properties']['version']['const']=='2.7.0'
assert schema['properties']['automaticReproductionExecution']['const'] is False
assert schema['properties']['clientSuppliedRuntimeUrlsAllowed']['const'] is False
assert schema['properties']['arbitraryCodeExecution']['const'] is False
print('PASS — Workspace v2.7.0 controlled runtime handoffs validated')
