from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.76.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.76.0.json').read_text())
MP=R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); H=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-product-help-v1.js').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.76.0.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.76.0.css').read_text(); NAV=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - '+l)
check('Version: 0.76.0' in MAIN and "SC_WORKSPACE_VERSION', '0.76.0" in MAIN,'version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.76.0','0.75.0','Documentation, Recovery Guidance & Product Help'),'lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.76.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M);check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact header')
check("'sc-workspace-v0760'" in PHP and 'workspace-v0.76.0.js' in PHP and 'workspace-v0.76.0.css' in PHP,'assets')
check("wp_localize_script('sc-workspace-v0760'" in PHP,'localization')
check("'/product-help-contract'" in PHP and 'product_help_contract' in PHP,'REST')
check('/wp-json/sc-workspace/v1/product-help-contract' in MAN['rest_routes'],'manifest REST')
h=MAN['documentation_recovery_product_help']
for k in ['local_first_boundary_explained','backup_sync_distinction_explained','restore_as_copy_preferred','privacy_minimized_report']: check(h[k] is True,k)
for k in ['automatic_repair','automatic_restore','automatic_upload','automatic_sync','behavioral_tracking','telemetry','canonical_mutation','schema_migration_required']: check(h[k] is False,k)
check(h['searchable_topic_count']==10,'topic count')
for tok in ["id:'save-failed'","id:'sync-conflict'","id:'move-device'","id:'institutional-handoff'",'projectContentIncluded:false','deviceIdentifierIncluded:false']: check(tok in H,'helper '+tok)
check("views:['start','journey','help']" in NAV and "help:'Help & Recovery'" in NAV,'navigation')
check("'start','journey','help','projects'" in APP,'main route integration')
check('data-scw-workspace-section="help"' in PHP and 'data-scw-help-search' in PHP and 'data-scw-help-export' in PHP,'UI')
check('/* v0.76.0 — Documentation, Recovery Guidance & Product Help */' in CSS,'CSS')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0760'" in REGPHP and 'LEGACY_PENDING_KEY_V0750' in REGPHP,'registry')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.76.0','0.75.0','Documentation, Recovery Guidance & Product Help'),'registry record')
for f in ['schemas/sc-workspace-product-help-v1.schema.json','schemas/sc-workspace-recovery-guidance-v1.schema.json','schemas/sc-workspace-product-help-report-v1.schema.json','docs/DOCUMENTATION_RECOVERY_GUIDANCE_PRODUCT_HELP_V0760.md','RELEASE_NOTES_0.76.0.md','history/release-manifest-v0.75.0.json','history/workspace-product-record-v0.75.0.json']: check((R/f).exists(),f)
print('PASS - v0.76.0 release validator')
