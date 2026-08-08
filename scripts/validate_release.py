from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(ok,msg):
    if not ok: raise SystemExit('FAIL - '+msg)
main=(P/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.9.0' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.9.0')" in main,'runtime version')
php=(P/'includes/class-sc-workspace.php').read_text(); js=(P/'assets/js/workspace-v0.9.0.js').read_text(); reg=(P/'includes/class-sc-workspace-registry.php').read_text()
for token in ('data-scw-project-mode="traceability"','/traceability-contract','sc-workspace-traceability/1.0',"home_url('/knowledge-libraries/')"): check(token in php,'PHP contract '+token)
for token in ('const STORAGE_VERSION = 10',"const PROJECT_SCHEMA = 'sc-workspace-project/8.0'",'traceabilityTemplate','sha256Object','cleanTraceabilityReferences','REPRO_EXPORT_SCHEMA'): check(token in js,'JS contract '+token)
check("const BACKUP_KEY = 'sc_workspace_registry_backup_v090'" in reg,'registry backup'); check("'previous_version' => '0.8.3.1'" in reg,'registry previous')
m=json.loads((ROOT/'release-manifest-v0.9.0.json').read_text()); check(m['version']=='0.9.0','manifest version'); check(m['storage_schema_version']==10,'storage'); check(m['project_schema']=='sc-workspace-project/8.0','project'); check(m['canonical_library_path']=='/knowledge-libraries/','library route')
r=json.loads((ROOT/'registry/workspace-product-record-v0.9.0.json').read_text()); check(r['public_version']=='0.9.0','registry version'); check(r['previous_version']=='0.8.3.1','registry prev'); check(r['product_url']=='/platform/','platform route')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.9.0 — Evidence, Provenance & Reproducibility')
