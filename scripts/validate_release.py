#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'; js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.6.0.js'; css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.6.0.css'
required=(main,php,js,css,ROOT/'schemas/sc-workspace-project-v5.schema.json',ROOT/'schemas/sc-workspace-decision-v1.schema.json',ROOT/'schemas/sc-workspace-analysis-v1.schema.json',ROOT/'schemas/sc-workspace-identity-v1.schema.json',ROOT/'schemas/sc-workspace-research-v1.schema.json',ROOT/'schemas/sc-workspace-object-v1.schema.json',ROOT/'release-manifest-v0.6.0.json',ROOT/'registry/workspace-product-record-v0.6.0.json')
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists(): check('Version: 0.6.0' in main.read_text(),'plugin header version mismatch')
if js.exists():
 t=js.read_text()
 for token in ("const STORAGE_VERSION = 7","const PROJECT_SCHEMA = 'sc-workspace-project/5.0'","const DECISION_SCHEMA = 'sc-workspace-decision/1.0'",'function migrateV6(raw)','function decisionTemplate()','function normalizeDecision','function renderDecision','function cleanDecisionReferences','cloudSync: false','serverProjectStorage: false'): check(token in t,f'JS contract missing: {token}')
if php.exists():
 t=php.read_text()
 for token in ("'/identity-contract'","'/analysis-contract'","'/decision-contract'",'DECISION WORKSPACE','Options &amp; criteria','Option assessments','Risks &amp; decision record',"'decision_schema' => 'sc-workspace-decision/1.0'","'server_project_storage' => false","'cloud_sync' => false"): check(token in t,f'PHP/UI contract missing: {token}')
try:
 m=json.loads((ROOT/'release-manifest-v0.6.0.json').read_text()); check(m['version']=='0.6.0','manifest version'); check(m['previous_version']=='0.5.0','previous version'); check(m['storage_schema_version']==7,'storage schema'); check(m['project_schema']=='sc-workspace-project/5.0','project schema'); check(m['decision_schema']=='sc-workspace-decision/1.0','decision schema'); check(m['account_required'] is False,'account required'); check(m['anonymous_access'] is True,'anonymous access'); check(m['server_project_storage'] is False,'server storage'); check(m['cloud_sync'] is False,'cloud sync')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
 s=json.loads((ROOT/'schemas/sc-workspace-project-v5.schema.json').read_text()); check(s['properties']['schema']['const']=='sc-workspace-project/5.0','project schema const'); check('decision' in s['required'],'decision required'); d=json.loads((ROOT/'schemas/sc-workspace-decision-v1.schema.json').read_text()); check(d['properties']['schema']['const']=='sc-workspace-decision/1.0','decision schema const'); check(d['properties']['assessments']['maxItems']==1000,'assessment cap')
except Exception as e: errors.append(f'schema parse failed: {e}')
try:
 r=json.loads((ROOT/'registry/workspace-product-record-v0.6.0.json').read_text()); check(r['public_version']=='0.6.0','registry version'); check(r['previous_version']=='0.5.0','registry previous'); check(r['family']=='commercial','registry family')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
 print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.6.0 — Decision Workspace')
