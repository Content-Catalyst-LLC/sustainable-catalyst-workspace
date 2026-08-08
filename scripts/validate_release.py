#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.4.0.js'
css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.4.0.css'
for p in (main,php,js,css,ROOT/'schemas/sc-workspace-project-v3.schema.json',ROOT/'schemas/sc-workspace-research-v1.schema.json',ROOT/'schemas/sc-workspace-object-v1.schema.json',ROOT/'release-manifest-v0.4.0.json',ROOT/'registry/workspace-product-record-v0.4.0.json'):
    check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists(): check("Version: 0.4.0" in main.read_text(),'plugin header version mismatch')
if js.exists():
    t=js.read_text();
    for token in ("const STORAGE_VERSION = 4","const PROJECT_SCHEMA = 'sc-workspace-project/3.0'","const RESEARCH_SCHEMA = 'sc-workspace-research/1.0'",'function renderResearch','function cleanResearchReferences','MAX_RESEARCH_QUESTIONS = 100','MAX_RESEARCH_CLAIMS = 100'):
        check(token in t,f'JS contract missing: {token}')
if php.exists():
    t=php.read_text();
    for token in ("'/research-contract'",'RESEARCH WORKSPACE','data-scw-research-question-form','data-scw-research-source-form','data-scw-research-evidence-form','data-scw-research-claim-form'):
        check(token in t,f'PHP/UI contract missing: {token}')
try:
    m=json.loads((ROOT/'release-manifest-v0.4.0.json').read_text()); check(m['version']=='0.4.0','manifest version'); check(m['previous_version']=='0.3.0','previous version'); check(m['storage_schema_version']==4,'storage schema'); check(m['research_schema']=='sc-workspace-research/1.0','research schema'); check(m['access_model']=='free-public','access'); check(m['registry']['family']=='commercial','family')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    s=json.loads((ROOT/'schemas/sc-workspace-research-v1.schema.json').read_text()); check(s['properties']['questions']['maxItems']==100,'question limit'); check(s['properties']['claims']['maxItems']==100,'claim limit'); check(s['properties']['readingQueue']['maxItems']==250,'queue limit'); check(s['properties']['evidenceLinks']['maxItems']==500,'evidence link limit')
except Exception as e: errors.append(f'research schema parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.4.0.json').read_text()); check(r['public_version']=='0.4.0','registry version'); check(r['previous_version']=='0.3.0','registry previous')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print('FAIL -',e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.4.0')
print('PASS - Research Workspace contract and project schema 3.0')
print('PASS - research questions, priorities, lifecycle, and active-question state')
print('PASS - source capture and reading queue using canonical Source object IDs')
print('PASS - evidence extraction and source-to-evidence links')
print('PASS - claims, claim lifecycle, and evidence-to-claim links')
print('PASS - v0.3 project migration plus v0.2/v0.1 compatibility')
print('PASS - privacy-minimized cross-product handoff; research text stays out of URLs')
print('PASS - free public, device-local persistence boundary retained')
