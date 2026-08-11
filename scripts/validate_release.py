from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
HARD=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
FIELD=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-use-v1.js').read_text()
A11Y=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-v1.js').read_text()
COMPAT=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-browser-compatibility-v1.js').read_text()

def check(ok,label):
    if not ok: raise SystemExit('FAIL - '+label)

check('Version: 0.66.0' in MAIN and "SC_WORKSPACE_VERSION', '0.66.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
check('workspace-v0.66.0.js' in PHP and 'workspace-v0.66.0.css' in PHP and "'sc-workspace-v0660'" in PHP and len(APP)>100000,'current cumulative assets')
check("SCHEMA='sc-workspace-import-export-compatibility/1.0'" in HARD and "CURRENT_PROJECT_SCHEMA='sc-workspace-project/20.0'" in HARD and "CURRENT_EXPORT_SCHEMA='sc-workspace-project-export/20.0'" in HARD,'compatibility helper contracts')
check("'/import-export-compatibility-contract'" in PHP and '/wp-json/sc-workspace/v1/import-export-compatibility-contract' in MAN['rest_routes'],'compatibility REST contract')
versions=['1.0','2.0','3.0','3.1','4.0','5.0','6.0','7.0','8.0','9.0','10.0','11.0','12.0','13.0','14.0','15.0','16.0','17.0','18.0','19.0','20.0']
ib=MAN['import_export_backward_compatibility']
check(ib['supported_project_versions']==versions and ib['supported_export_versions']==versions,'historical project/export matrix')
check(ib['supported_existing_storage_versions']==list(range(1,36)),'historical storage matrix')
check(ib['project_import_mode']=='stage-review-new-local-copy' and ib['automatic_import_commit'] is False and ib['automatic_overwrite'] is False,'staged no-overwrite import boundary')
check(ib['future_schema_policy']=='block-no-downgrade' and ib['external_network_lookup'] is False and ib['server_import_pipeline'] is False,'future/remote boundary')
check(ib['round_trip_export_validation'] is True and ib['round_trip_checksum_purpose']=='drift-detection-only-not-security','round-trip and checksum boundary')
check(all(x in APP for x in ['stagedProjectImport','assessProjectImport','classifyProjectPayload','data-scw-project-import-commit','data-scw-project-import-clear','currentProjectExport','data-scw-backward-compatibility-export']), 'main import/export runtime wired')
check("project.id=id('scwp')" in APP and 'Import mode is always a new local copy' in HARD,'import-as-new-copy invariant')
check('cannot be safely downgraded' in HARD and 'futureProjectSchemas' in HARD and 'blocked-no-downgrade' in HARD,'future schema rejection')
check('roundTripCheck' in HARD and 'beforeFingerprint' in HARD and 'afterFingerprint' in HARD and 'drift-detection-only-not-security' in HARD,'round-trip drift receipt')
check('data-scw-project-import-stage' in PHP and 'Import staged copy' in PHP and 'Clear staged import' in PHP,'staged import UI')
check('data-scw-backward-compatibility-matrix' in PHP and 'Export compatibility matrix' in PHP,'compatibility matrix UI')
check('SCWorkspaceFieldUse.boot(window)' in APP and "SCHEMA='sc-workspace-field-use-profile/1.0'" in FIELD,'v0.65 field-use retained')
check('Explore the Lab' in PHP and 'Open the Lab' in PHP,'v0.65 Lab handoffs retained')
block=re.search(r"wp_enqueue_script\(\s*'sc-workspace-accessibility-v1'.*?\n\s*\);",PHP,re.S)
check(bool(block),'accessibility enqueue retained')
deps=re.search(r'array\((.*?)\)',block.group(0),re.S).group(1)
check("'sc-workspace-accessibility-v1'" not in deps,'v0.64.1 self-dependency remains fixed')
check("SCHEMA='sc-workspace-accessibility/1.0'" in A11Y and "SCHEMA='sc-workspace-browser-compatibility/1.0'" in COMPAT,'accessibility/browser compatibility retained')
check(REG['public_version']=='0.66.0' and REG['previous_version']=='0.65.0' and REG['release_name']=='Import, Export & Backward-Compatibility Hardening','registry record')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0660'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0660'" in REGPHP and 'LEGACY_PENDING_KEY_V0650' in REGPHP,'registry recovery lineage')
check((ROOT/'history/release-manifest-v0.65.0.json').exists() and (ROOT/'history/workspace-product-record-v0.65.0.json').exists(),'predecessor history')
for schema in [
 'sc-workspace-import-export-compatibility-v1.schema.json',
 'sc-workspace-import-assessment-v1.schema.json',
 'sc-workspace-backward-compatibility-matrix-v1.schema.json',
 'sc-workspace-round-trip-receipt-v1.schema.json']:
    json.loads((ROOT/'schemas'/schema).read_text())
for fixture in (ROOT/'tests/fixtures/import-export-compatibility').glob('*.json'):
    json.loads(fixture.read_text())
print('PASS - v0.66.0 release validator')
