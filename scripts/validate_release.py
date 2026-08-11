from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.67.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.67.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAIN=MAINP.read_text(); RAW=MAINP.read_bytes(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.67.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-cross-device-continuity-v1.js').read_text()
BETA=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.67.0' in MAIN and "SC_WORKSPACE_VERSION', '0.67.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.67.0','0.66.1','Cross-Device Continuity & Sync Hardening'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
check(MAN['migration'].get('cross_device_continuity_only_release') is True and MAN['migration'].get('cross_device_continuity_canonical_data_rewrite') is False,'continuity-only non-destructive migration boundary')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.67.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0670'" in PHP and 'workspace-v0.67.0.js' in PHP and 'workspace-v0.67.0.css' in PHP,'v0.67 cumulative assets')
check("wp_localize_script('sc-workspace-v0670'" in PHP,'current asset localization handle')
check('sc-workspace-cross-device-continuity-v1.js' in PHP and "'/continuity-contract'" in PHP,'continuity helper and REST contract')
check('/wp-json/sc-workspace/v1/continuity-contract' in MAN['rest_routes'],'continuity REST manifest')
cc=MAN['cross_device_continuity']
check(cc['idempotent_operation_id'] is True and cc['interrupted_operation_reconciliation'] is True and cc['pull_creates_sync_safety_restore_point'] is True,'sync recovery protections')
check(cc['migration_import_mode']=='new-local-copy' and cc['sync_enrollment_transferred'] is False and cc['duplicate_migration_guard'] is True,'device migration boundary')
check(cc['manual_backup_overwrites_sync_head'] is False and cc['automatic_sync'] is False and cc['background_sync'] is False,'explicit cloud boundary')
check("$payload['operationId']" in PHP and "'replayed' => true" in PHP and 'scw_manual_backup_sync_head_conflict' in PHP,'server retry/manual-backup protection')
check("array('sc-workspace-project/20.0','sc-workspace-project/19.0'" in PHP,'current Project 20 cloud acceptance')
check('recoverInterruptedSyncOperations()' in APP and 'createDeviceMigrationPackage' in APP and 'Sync remains disabled until you explicitly enroll the new copy.' in APP,'continuity application wiring')
check("MIGRATION_SCHEMA='sc-workspace-device-migration/1.0'" in HELP and "syncEnrollmentTransferred:false" in HELP and "deviceIdentityIncluded:false" in HELP,'migration helper privacy boundary')
check("expectedVersion:'0.67.0'" in BETA and "root.dataset.version==='0.67.0'" in BETA,'beta current version gate')
check("workspaceVersion:'0.67.0'" in COMP,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0670'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0670'" in REGPHP and 'LEGACY_PENDING_KEY_V0661' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.67.0','0.66.1','Cross-Device Continuity & Sync Hardening'),'registry record')
check((ROOT/'history/release-manifest-v0.66.1.json').exists() and (ROOT/'history/workspace-product-record-v0.66.1.json').exists(),'v0.66.1 history retained')
for f in ['schemas/sc-workspace-cross-device-continuity-v1.schema.json','schemas/sc-workspace-sync-operation-v1.schema.json','schemas/sc-workspace-device-migration-v1.schema.json']:
 check((ROOT/f).exists(),f)
print('PASS - v0.67.0 release validator')
