#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(ok,msg):
    if not ok: print('FAIL - '+msg); sys.exit(1)
    print('PASS - '+msg)
main=(P/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.11.0' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.11.0')" in main,'runtime version')
php=(P/'includes/class-sc-workspace.php').read_text(); js=(P/'assets/js/workspace-v0.11.0.js').read_text(); reg=(P/'includes/class-sc-workspace-registry.php').read_text()
check("'/guided-workflows-contract'" in php,'Guided Workflows REST contract'); check('data-scw-project-mode="guide"' in php,'Guide project mode'); check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
check("const STORAGE_VERSION = 12" in js,'storage schema 12'); check("const PROJECT_SCHEMA = 'sc-workspace-project/10.0'" in js,'project schema 10.0'); check("const GUIDED_WORKFLOWS_SCHEMA = 'sc-workspace-guided-workflows/1.0'" in js,'guided workflows schema'); check('function migrateV11(raw)' in js,'v0.10 migration'); check('function startGuidedWorkflow' in js,'workflow run creation'); check('setProjectMode(step.mode)' in js,'native mode guidance')
m=json.loads((ROOT/'release-manifest-v0.11.0.json').read_text()); check(m['version']=='0.11.0','manifest version'); check(m['previous_version']=='0.10.0','previous version'); check(m['storage_schema_version']==12,'storage schema'); check(m['project_schema']=='sc-workspace-project/10.0','project schema'); check(m['guided_workflows_schema']=='sc-workspace-guided-workflows/1.0','guided workflow manifest'); check(m['canonical_library_path']=='/knowledge-libraries/','library route'); check(m['workflow_principles']['blank_projects_supported'],'blank projects supported'); check(not m['governance']['automatic_workflow_completion'],'automatic workflow completion disabled')
r=json.loads((ROOT/'registry/workspace-product-record-v0.11.0.json').read_text()); check(r['public_version']=='0.11.0','registry version'); check(r['previous_version']=='0.10.0','registry previous version'); check(r['product_url']=='/platform/','platform route')
json.loads((ROOT/'schemas/sc-workspace-guided-workflows-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-project-v10.schema.json').read_text()); check(True,'schema JSON')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.11.0 — Templates & Guided Workflows')
