#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(ok,msg):
    if not ok: print('FAIL - '+msg); sys.exit(1)
    print('PASS - '+msg)
main=(P/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.10.0' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.10.0')" in main,'runtime version')
php=(P/'includes/class-sc-workspace.php').read_text(); js=(P/'assets/js/workspace-v0.10.0.js').read_text(); reg=(P/'includes/class-sc-workspace-registry.php').read_text()
check("'/briefing-contract'" in php,'Briefing REST contract'); check('data-scw-project-mode="briefing"' in php,'Briefing project mode'); check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
check("const STORAGE_VERSION = 11" in js,'storage schema 11'); check("const PROJECT_SCHEMA = 'sc-workspace-project/9.0'" in js,'project schema 9.0'); check("const BRIEFING_SCHEMA = 'sc-workspace-briefing/1.0'" in js,'briefing schema'); check('function migrateV10(raw)' in js,'v0.9 migration'); check("objectTemplate('document',draft.title)" in js,'Document materialization'); check('automaticPublication:false' in js,'no automatic publication')
m=json.loads((ROOT/'release-manifest-v0.10.0.json').read_text()); check(m['version']=='0.10.0','manifest version'); check(m['previous_version']=='0.9.0.1','previous version'); check(m['storage_schema_version']==11,'storage schema'); check(m['project_schema']=='sc-workspace-project/9.0','project schema'); check(m['briefing_schema']=='sc-workspace-briefing/1.0','briefing manifest'); check(m['canonical_library_path']=='/knowledge-libraries/','library route'); check(not m['governance']['automatic_publication'],'automatic publication disabled')
r=json.loads((ROOT/'registry/workspace-product-record-v0.10.0.json').read_text()); check(r['public_version']=='0.10.0','registry version'); check(r['previous_version']=='0.9.0.1','registry previous version'); check(r['product_url']=='/platform/','platform route')
json.loads((ROOT/'schemas/sc-workspace-briefing-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-project-v9.schema.json').read_text()); check(True,'schema JSON')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.10.0 — Briefing & Publication Studio')
