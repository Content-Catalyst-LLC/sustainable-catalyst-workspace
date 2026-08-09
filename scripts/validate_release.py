from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(P/'sustainable-catalyst-workspace.php').read_text();php=(P/'includes/class-sc-workspace.php').read_text();js=(P/'assets/js/workspace-v0.18.0.js').read_text();css=(P/'assets/css/workspace-v0.18.0.css').read_text();reg=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(ok,msg):
    if not ok: raise SystemExit('FAIL - '+msg)
    print('PASS - '+msg)
check('Version: 0.18.0' in main,'plugin version')
check("define('SC_WORKSPACE_VERSION', '0.18.0')" in main,'runtime version')
check("'/collaboration-contract'" in php,'collaboration REST contract')
check('COLLABORATION FOUNDATION' in php,'collaboration UI')
check('const STORAGE_VERSION = 19' in js,'storage schema 19')
check("const PROJECT_SCHEMA = 'sc-workspace-project/11.0'" in js,'project schema unchanged')
check("const COLLABORATION_SCHEMA = 'sc-workspace-collaboration/1.0'" in js,'collaboration schema')
check('function migrateV18(raw)' in js,'v0.17 storage migration')
check('async function collaborationRequestPackage' in js,'review request export')
check('async function collaborationResponsePackage' in js,'review response export')
check("'imported_feedback_mutates_project_automatically' => false" in php,'human-controlled feedback boundary')
check('.scw-collaboration{' in css,'collaboration styling')
check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
m=json.loads((ROOT/'release-manifest-v0.18.0.json').read_text());check(m['version']=='0.18.0','manifest version');check(m['previous_version']=='0.17.0','previous version');check(m['storage_schema_version']==19,'storage schema');check(m['project_schema']=='sc-workspace-project/11.0','project schema');check(m['collaboration_schema']=='sc-workspace-collaboration/1.0','collaboration manifest');check(not m['collaboration_foundation']['live_collaboration'],'no live collaboration');check(not m['collaboration_foundation']['server_collaboration'],'no server collaboration');check(not m['collaboration_foundation']['roles_are_server_permissions'],'roles not server permissions');check(not m['collaboration_foundation']['imported_feedback_mutates_project_automatically'],'no automatic source mutation')
r=json.loads((ROOT/'registry/workspace-product-record-v0.18.0.json').read_text());check(r['public_version']=='0.18.0','registry version');check(r['previous_version']=='0.17.0','registry previous version');json.loads((ROOT/'schemas/sc-workspace-collaboration-v1.schema.json').read_text());json.loads((ROOT/'schemas/sc-workspace-review-package-v1.schema.json').read_text());check(True,'schema JSON');check('const LEGACY_PENDING_KEY_V0170' in reg,'registry retry lineage')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.18.0 — Collaboration Foundation')
