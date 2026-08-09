from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(P/'sustainable-catalyst-workspace.php').read_text();php=(P/'includes/class-sc-workspace.php').read_text();js=(P/'assets/js/workspace-v0.17.0.js').read_text();css=(P/'assets/css/workspace-v0.17.0.css').read_text();reg=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(ok,msg):
    if not ok: raise SystemExit('FAIL - '+msg)
    print('PASS - '+msg)
check('Version: 0.17.0' in main,'plugin version')
check("define('SC_WORKSPACE_VERSION', '0.17.0')" in main,'runtime version')
check("'/activity-intelligence-contract'" in php,'activity intelligence REST contract')
check('WORKFLOW &amp; ACTIVITY INTELLIGENCE' in php,'activity intelligence UI')
check('const STORAGE_VERSION = 18' in js,'storage schema 18')
check("const PROJECT_SCHEMA = 'sc-workspace-project/11.0'" in js,'project schema unchanged')
check("const ACTIVITY_INTELLIGENCE_SCHEMA = 'sc-workspace-activity-intelligence/1.0'" in js,'activity schema')
check('function migrateV17(raw)' in js,'v0.16 storage migration')
check('function derivedAttentionSignals' in js,'transparent attention signal engine')
check('function workspaceActivityTimeline' in js,'cross-project activity timeline')
check('function workflowIntelligenceRows' in js,'workflow status engine')
check('No productivity score' in php,'no productivity score boundary')
check('.scw-activity-intelligence{' in css,'activity intelligence styling')
check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
m=json.loads((ROOT/'release-manifest-v0.17.0.json').read_text());check(m['version']=='0.17.0','manifest version');check(m['previous_version']=='0.16.0','previous version');check(m['storage_schema_version']==18,'storage schema');check(m['project_schema']=='sc-workspace-project/11.0','project schema');check(m['activity_intelligence_schema']=='sc-workspace-activity-intelligence/1.0','activity manifest');check(not m['workflow_activity_intelligence']['productivity_score'],'no productivity score');check(not m['workflow_activity_intelligence']['server_activity_analytics'],'no server activity analytics');check(not m['workflow_activity_intelligence']['automatic_completion'],'no automatic completion')
r=json.loads((ROOT/'registry/workspace-product-record-v0.17.0.json').read_text());check(r['public_version']=='0.17.0','registry version');check(r['previous_version']=='0.16.0','registry previous version');json.loads((ROOT/'schemas/sc-workspace-activity-intelligence-v1.schema.json').read_text());check(True,'schema JSON');check('const LEGACY_PENDING_KEY_V0160' in reg,'registry retry lineage')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.17.0 — Workflow & Activity Intelligence')
