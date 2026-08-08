#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
platform=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php'
js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.8.0.js'
css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.8.0.css'
required=(main,php,platform,js,css,ROOT/'schemas/sc-workspace-project-v7.schema.json',ROOT/'schemas/sc-workspace-handoff-ledger-v1.schema.json',ROOT/'schemas/sc-workspace-handoff-return-v1.schema.json',ROOT/'schemas/sc-workspace-canvas-v1.schema.json',ROOT/'release-manifest-v0.8.0.json',ROOT/'registry/workspace-product-record-v0.8.0.json',ROOT/'docs/CROSS_PRODUCT_HANDOFFS_V080.md')
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists():
    t=main.read_text(); check('Version: 0.8.0' in t,'plugin header version mismatch'); check("define('SC_WORKSPACE_VERSION', '0.8.0')" in t,'runtime version mismatch')
if js.exists():
    t=js.read_text()
    for token in ("const STORAGE_VERSION = 9","const PROJECT_SCHEMA = 'sc-workspace-project/7.0'","const HANDOFF_SCHEMA = 'sc-workspace-handoff/2.0'","const HANDOFF_LEDGER_SCHEMA = 'sc-workspace-handoff-ledger/1.0'","const HANDOFF_RETURN_SCHEMA = 'sc-workspace-handoff-return/1.0'",'function migrateV8(raw)','function createHandoff','function ingestReturnPacket','function renderHandoffs',"target.searchParams.set('sc_workspace_handoff', handoff.id)",'cloudSync: false','serverProjectStorage: false'):
        check(token in t,f'JS contract missing: {token}')
if php.exists():
    t=php.read_text()
    for token in ("'/handoff-contract'",'CROSS-PRODUCT HANDOFFS','Check return inbox','Import return JSON','Export return template',"'handoff_schema' => 'sc-workspace-handoff/2.0'","'storage_schema_version' => 9","'project_schema' => 'sc-workspace-project/7.0'"):
        check(token in t,f'PHP/UI contract missing: {token}')
if platform.exists():
    t=platform.read_text();
    for token in ('perform_conversion','perform_restore','sc_workspace_platform_backup_v061_',"get_page_by_path('platform'",'[sc_workspace_platform]','maybe_redirect_legacy_workspace_route'): check(token in t,f'Platform conversion regression: {token}')
    check("'post_name' =>" not in t,'conversion must not rewrite page slug'); check("'post_parent' =>" not in t,'conversion must not rewrite page parent')
try:
    h=json.loads((ROOT/'schemas/sc-workspace-handoff-ledger-v1.schema.json').read_text()); check(h['properties']['schema']['const']=='sc-workspace-handoff-ledger/1.0','handoff ledger schema id'); check(h['properties']['entries']['maxItems']==150,'handoff limit')
    r=json.loads((ROOT/'schemas/sc-workspace-handoff-return-v1.schema.json').read_text()); check(r['properties']['schema']['const']=='sc-workspace-handoff-return/1.0','return schema id'); check(r['properties']['artifacts']['maxItems']==20,'return artifact limit')
    p=json.loads((ROOT/'schemas/sc-workspace-project-v7.schema.json').read_text()); check(p['properties']['schema']['const']=='sc-workspace-project/7.0','project schema'); check(p['properties']['handoffs']['$ref']=='sc-workspace-handoff-ledger-v1.schema.json','project handoff ref')
except Exception as e: errors.append(f'schema parse failed: {e}')
try:
    m=json.loads((ROOT/'release-manifest-v0.8.0.json').read_text()); check(m['version']=='0.8.0','manifest version'); check(m['previous_version']=='0.7.0','previous version'); check(m['release_name']=='Cross-Product Handoffs','release name'); check(m['storage_schema_version']==9,'storage schema'); check(m['project_schema']=='sc-workspace-project/7.0','project schema'); check(m['handoff_schema']=='sc-workspace-handoff/2.0','handoff schema'); check(m['handoff']['content_in_query_string'] is False,'handoff content boundary'); check(m['cloud_sync'] is False,'cloud sync'); check(m['platform_conversion']['automatic'] is False,'automatic conversion must remain false')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.8.0.json').read_text()); check(r['public_version']=='0.8.0','registry version'); check(r['previous_version']=='0.7.0','registry previous'); check(r['family']=='commercial','registry family'); check(r['product_url']=='/platform/','registry product URL')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.8.0 — Cross-Product Handoffs')
