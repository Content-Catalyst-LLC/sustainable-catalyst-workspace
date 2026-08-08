#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.4.1.js'
css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.4.1.css'
required=(main,php,js,css,ROOT/'schemas/sc-workspace-project-v3-1.schema.json',ROOT/'schemas/sc-workspace-identity-v1.schema.json',ROOT/'schemas/sc-workspace-research-v1.schema.json',ROOT/'schemas/sc-workspace-object-v1.schema.json',ROOT/'release-manifest-v0.4.1.json',ROOT/'registry/workspace-product-record-v0.4.1.json')
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists(): check('Version: 0.4.1' in main.read_text(),'plugin header version mismatch')
if js.exists():
    t=js.read_text()
    for token in ("const STORAGE_VERSION = 5","const PROJECT_SCHEMA = 'sc-workspace-project/3.1'","const IDENTITY_SCHEMA = 'sc-workspace-identity/1.0'",'function deviceId()','function projectPersistenceTemplate()','function migrateV4(raw)','function renderIdentity()','cloudSync: false','serverProjectStorage: false'):
        check(token in t,f'JS contract missing: {token}')
if php.exists():
    t=php.read_text()
    for token in ("'/identity-contract'",'IDENTITY &amp; PERSISTENCE','data-scw-identity-badge','data-scw-login','data-scw-logout',"'authentication_provider' => 'wordpress'","'server_project_storage' => false","'cloud_sync' => false"):
        check(token in t,f'PHP/UI contract missing: {token}')
try:
    m=json.loads((ROOT/'release-manifest-v0.4.1.json').read_text())
    check(m['version']=='0.4.1','manifest version'); check(m['previous_version']=='0.4.0','previous version'); check(m['storage_schema_version']==5,'storage schema'); check(m['project_schema']=='sc-workspace-project/3.1','project schema'); check(m['identity_schema']=='sc-workspace-identity/1.0','identity schema'); check(m['account_required'] is False,'account required'); check(m['anonymous_access'] is True,'anonymous access'); check(m['server_project_storage'] is False,'server storage'); check(m['cloud_sync'] is False,'cloud sync')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    s=json.loads((ROOT/'schemas/sc-workspace-project-v3-1.schema.json').read_text()); check(s['properties']['schema']['const']=='sc-workspace-project/3.1','project schema const'); check('persistence' in s['required'],'project persistence required'); check(s['properties']['persistence']['properties']['scope']['const']=='device','device scope')
    i=json.loads((ROOT/'schemas/sc-workspace-identity-v1.schema.json').read_text()); check(i['properties']['cloudSync']['const'] is False,'identity cloud sync false'); check(i['properties']['serverProjectStorage']['const'] is False,'identity server storage false')
except Exception as e: errors.append(f'schema parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.4.1.json').read_text()); check(r['public_version']=='0.4.1','registry version'); check(r['previous_version']=='0.4.0','registry previous'); check(r['family']=='commercial','registry family')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.4.1')
