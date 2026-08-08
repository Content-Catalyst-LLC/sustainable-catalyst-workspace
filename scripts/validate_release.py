#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
plugin=ROOT/'wordpress/sustainable-catalyst-workspace'
required=[plugin/'sustainable-catalyst-workspace.php',plugin/'includes/class-sc-workspace.php',plugin/'includes/class-sc-workspace-registry.php',plugin/'includes/class-sc-workspace-platform.php',plugin/'assets/js/workspace-v0.8.1.js',plugin/'assets/js/sc-workspace-return-adapter-v1.js',plugin/'assets/css/workspace-v0.8.1.css',ROOT/'release-manifest-v0.8.1.json',ROOT/'registry/workspace-product-record-v0.8.1.json',ROOT/'docs/CROSS_PRODUCT_RETURN_ADAPTERS_V081.md']
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
main=(plugin/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.8.1' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.8.1')" in main,'runtime version'); check('sc_workspace_return_adapter_script_url' in main,'producer helper URL function')
js=(plugin/'assets/js/workspace-v0.8.1.js').read_text()
for token in ("const STORAGE_VERSION = 9","const PROJECT_SCHEMA = 'sc-workspace-project/7.0'","const RETURN_ADAPTER_SCHEMA = 'sc-workspace-return-adapter/1.0'",'function adaptReturnPacket','window.SCWorkspaceReturnAdapter',"event.origin !== window.location.origin",'automatic && !entry','entry.destination !== packet.destination'):
    check(token in js,f'JS contract missing: {token}')
helper=(plugin/'assets/js/sc-workspace-return-adapter-v1.js').read_text();
for token in ("sc-workspace-return-adapter/1.0",'SCWorkspaceToolReturnAdapter','postMessage','sc_workspace_handoff_return_v1'): check(token in helper,f'producer helper missing: {token}')
php=(plugin/'includes/class-sc-workspace.php').read_text()
for token in ("'/adapter-contract'","'schema' => 'sc-workspace-return-adapter-contract/1.0'","'schema' => 'sc-workspace-handoff-contract/2.1'",'data-scw-return-adapters'): check(token in php,f'PHP/UI missing: {token}')
try:
    m=json.loads((ROOT/'release-manifest-v0.8.1.json').read_text()); check(m['version']=='0.8.1','manifest version'); check(m['previous_version']=='0.8.0','manifest previous'); check(m['release_name']=='Cross-Product Return Adapters','release name'); check(m['storage_schema_version']==9,'storage unchanged'); check(m['project_schema']=='sc-workspace-project/7.0','project unchanged'); check(m['handoff_adapter_schema']=='sc-workspace-return-adapter/1.0','adapter schema'); check(m['cloud_sync'] is False,'cloud sync')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.8.1.json').read_text()); check(r['public_version']=='0.8.1','registry version'); check(r['previous_version']=='0.8.0','registry previous'); check(r['family']=='commercial','registry family')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.8.1 — Cross-Product Return Adapters')
