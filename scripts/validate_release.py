from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(v,msg):
    if not v: print('FAIL - '+msg); sys.exit(1)
    print('PASS - '+msg)
main=(P/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.9.0.1' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.9.0.1')" in main,'runtime version')
php=(P/'includes/class-sc-workspace.php').read_text(); js=(P/'assets/js/workspace-v0.9.0.1.js').read_text(); reg=(P/'includes/class-sc-workspace-registry.php').read_text()
closing=php.split('<section class="scw-editorial-closing"',1)[1].split('</section>',1)[0]
check('data-scw-platform-new-project' in closing and '>New Project</button>' in closing,'functional New Project closing CTA')
check('>Open Workspace</a>' not in closing,'redundant closing Open Workspace removed')
check("home_url('/knowledge-libraries/')" in closing,'canonical Library closing action')
check("document.querySelectorAll('[data-scw-platform-new-project]')" in js and 'trigger.click();' in js and 'form.scrollIntoView' in js,'page-level New Project bridge')
check("const STORAGE_VERSION = 10" in js,'storage schema unchanged')
check("const PROJECT_SCHEMA = 'sc-workspace-project/8.0'" in js,'project schema unchanged')
m=json.loads((ROOT/'release-manifest-v0.9.0.1.json').read_text()); check(m['version']=='0.9.0.1','manifest version'); check(m['previous_version']=='0.9.0','previous version'); check(m['storage_schema_version']==10,'storage preserved'); check(m['project_schema']=='sc-workspace-project/8.0','project preserved'); check(m['canonical_library_path']=='/knowledge-libraries/','library route')
r=json.loads((ROOT/'registry/workspace-product-record-v0.9.0.1.json').read_text()); check(r['public_version']=='0.9.0.1','registry version'); check(r['previous_version']=='0.9.0','registry previous version'); check(r['product_url']=='/platform/','platform route')
check("const LEGACY_PENDING_KEY_V090 = 'sc_workspace_registry_pending_v090';" in reg,'v0.9.0 pending migration cleanup')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.9.0.1 — Closing CTA Cleanup & Action Alignment')
