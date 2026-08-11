from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.70.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.70.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
RAW=MAINP.read_bytes(); MAIN=MAINP.read_text(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.70.0.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-ui-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.70.0.css').read_text()
BETA2=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()

def check(ok,label):
    if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.70.0' in MAIN and "SC_WORKSPACE_VERSION', '0.70.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.70.0','0.69.0','Public Product Beta III'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.70.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
    m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M)
    check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0700'" in PHP and 'workspace-v0.70.0.js' in PHP and 'workspace-v0.70.0.css' in PHP,'v0.70 cumulative assets')
check("wp_localize_script('sc-workspace-v0700'" in PHP,'current asset localization handle')
check('sc-workspace-public-beta-iii-v1.js' in PHP and 'sc-workspace-public-beta-iii-ui-v1.js' in PHP and "'/public-product-beta-iii-contract'" in PHP,'Beta III helper UI and REST contract')
check('/wp-json/sc-workspace/v1/public-product-beta-iii-contract' in MAN['rest_routes'],'Beta III REST manifest')
b=MAN['public_product_beta_iii']; ids=[x['id'] for x in b['journey']]
check(ids==['discover','capture','organize','analyze','synthesize','decide','compose','review','export-handoff'] and b['step_count']==9,'nine stage product journey')
check(b['topology_check_local_only'] is True and b['manual_walkthrough_storage']=='sessionStorage' and b['manual_walkthrough_persistent'] is False and b['privacy_minimized_report'] is True,'Beta III local/manual boundary')
for key in ['hidden_readiness_score','automatic_completion','behavioral_tracking','automatic_telemetry','automatic_submission','canonical_mutation']:
    check(b[key] is False,'Beta III governance '+key)
for marker in ids: check(marker in HELP,'Beta III step '+marker)
check("SESSION_KEY='sc_workspace_public_beta_iii_journey_v0700'" in HELP and 'assessSignals' in HELP and 'setReviewed' in HELP and 'resetManual' in HELP and 'hiddenScore:false' in HELP,'Beta III helper primitives')
check('data-scw-public-beta-iii' in PHP and 'Run product-journey check' in PHP and 'Checklist, not a score.' in PHP,'Beta III surface')
check("views:['start','journey']" in NAV and "journey:'Product Journey'" in NAV,'Beta III start navigation')
check('Object.values(navApi.AREAS||{})' in APP and "'journey'" in APP,'generic current-view validation')
check('/* v0.70.0 — Public Product Beta III */' in CSS and '.scw-beta-iii-grid' in CSS,'Beta III CSS')
check("expectedVersion:'0.70.0'" in BETA2 and "root.dataset.version==='0.70.0'" in BETA2,'Beta II current-version gate')
check("workspaceVersion:'0.70.0'" in COMP,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0700'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0700'" in REGPHP and 'LEGACY_PENDING_KEY_V0690' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.70.0','0.69.0','Public Product Beta III'),'registry record')
check((ROOT/'history/release-manifest-v0.69.0.json').exists() and (ROOT/'history/workspace-product-record-v0.69.0.json').exists(),'v0.69.0 history retained')
for f in ['schemas/sc-workspace-public-beta-iii-v1.schema.json','schemas/sc-workspace-product-journey-checkpoint-v1.schema.json','schemas/sc-workspace-product-journey-report-v1.schema.json','docs/PUBLIC_PRODUCT_BETA_III_V0700.md']:
    check((ROOT/f).exists(),f)
print('PASS - v0.70.0 release validator')
