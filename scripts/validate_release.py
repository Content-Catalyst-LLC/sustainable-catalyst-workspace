from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.69.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.69.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
RAW=MAINP.read_bytes(); MAIN=MAINP.read_text(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.69.0.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-recovery-disaster-simulation-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-recovery-disaster-simulation-ui-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.69.0.css').read_text()
BETA=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
def check(ok,label):
    if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.69.0' in MAIN and "SC_WORKSPACE_VERSION', '0.69.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.69.0','0.68.0','Product Recovery & Disaster Simulation'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.69.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
    m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M)
    check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0690'" in PHP and 'workspace-v0.69.0.js' in PHP and 'workspace-v0.69.0.css' in PHP,'v0.69 cumulative assets')
check("wp_localize_script('sc-workspace-v0690'" in PHP,'current asset localization handle')
check('sc-workspace-recovery-disaster-simulation-v1.js' in PHP and 'sc-workspace-recovery-disaster-simulation-ui-v1.js' in PHP and "'/recovery-disaster-simulation-contract'" in PHP,'recovery helper UI and REST contract')
check('/wp-json/sc-workspace/v1/recovery-disaster-simulation-contract' in MAN['rest_routes'],'recovery REST manifest')
rd=MAN['product_recovery_disaster_simulation']
check(rd['scenario_count']==8 and rd['sandboxed_failure_injection'] is True and rd['production_data_injection'] is False,'sandboxed scenario boundary')
for key in ['canonical_mutation','automatic_repair','automatic_restore','automatic_import_commit','automatic_sync','background_network','report_project_content','report_source_urls','report_query_text','report_device_identifier','automatic_submission']:
    check(rd[key] is False,'recovery governance '+key)
for marker in ['corrupt-state','interrupted-write','storage-exhaustion','malformed-import','stale-restore','sync-conflict','missing-reference','future-version']:
    check(marker in HELP,'scenario '+marker)
check('memoryStorage' in HELP and 'runScenario' in HELP and 'runAll' in HELP and 'productionDataInjection:false' in HELP,'recovery simulator primitives')
check('data-scw-recovery-drills' in PHP and 'Run recovery drills' in PHP and 'does not inject faults into canonical Workspace data' in PHP,'recovery review surface')
check("'recovery-drills':'Recovery Drills'" in NAV and "'recovery-drills'" in NAV,'recovery navigation')
check('/* v0.69.0 — Product Recovery & Disaster Simulation */' in CSS,'recovery CSS')
check("expectedVersion:'0.69.0'" in BETA and "root.dataset.version==='0.69.0'" in BETA,'beta current version gate')
check("workspaceVersion:'0.69.0'" in COMP,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0690'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0690'" in REGPHP and 'LEGACY_PENDING_KEY_V0680' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.69.0','0.68.0','Product Recovery & Disaster Simulation'),'registry record')
check((ROOT/'history/release-manifest-v0.68.0.json').exists() and (ROOT/'history/workspace-product-record-v0.68.0.json').exists(),'v0.68.0 history retained')
for f in ['schemas/sc-workspace-recovery-disaster-simulation-v1.schema.json','schemas/sc-workspace-recovery-disaster-scenario-v1.schema.json','schemas/sc-workspace-recovery-disaster-report-v1.schema.json','docs/PRODUCT_RECOVERY_DISASTER_SIMULATION_V0690.md']:
    check((ROOT/f).exists(),f)
print('PASS - v0.69.0 release validator')
