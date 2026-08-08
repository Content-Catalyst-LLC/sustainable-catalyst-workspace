from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; plugin=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(ok,msg):
    if not ok: raise SystemExit('FAIL - '+msg)
main=(plugin/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.8.3.1' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.8.3.1')" in main,'runtime version')
php=(plugin/'includes/class-sc-workspace.php').read_text(); css=(plugin/'assets/css/workspace-v0.8.3.1.css').read_text(); reg=(plugin/'includes/class-sc-workspace-registry.php').read_text()
for token in ('scw-editorial-header-bar','scw-platform-hero-grid','Research. Analyze. Decide.','WORKSPACE PATHWAYS','WORKSPACE APPLICATION'): check(token in php,'public UI missing: '+token)
for token in ('v0.8.3.1 — Editorial Header Bar & Page Alignment','.scw-editorial-header-bar{height:12px;background:#0b0b0b','height:9px','.scw-platform-hero-grid'): check(token in css,'CSS missing: '+token)
check("const BACKUP_KEY = 'sc_workspace_registry_backup_v0831'" in reg,'registry backup key'); check("'previous_version' => '0.8.3'" in reg,'registry previous version')
m=json.loads((ROOT/'release-manifest-v0.8.3.1.json').read_text()); check(m['version']=='0.8.3.1','manifest version'); check(m['previous_version']=='0.8.3','manifest previous'); check(m['release_name']=='Editorial Header Bar & Page Alignment','release name'); check(m['storage_schema_version']==9,'storage unchanged'); check(m['project_schema']=='sc-workspace-project/7.0','project unchanged'); check(m['public_experience'].get('editorial_header_bar') is True,'header bar manifest')
r=json.loads((ROOT/'registry/workspace-product-record-v0.8.3.1.json').read_text()); check(r['public_version']=='0.8.3.1','registry version'); check(r['previous_version']=='0.8.3','registry previous'); check(r['product_url']=='/platform/','canonical route')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.8.3.1 — Editorial Header Bar & Page Alignment')
