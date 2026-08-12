from pathlib import Path
import json,re,subprocess,sys

R=Path(__file__).resolve().parents[1]
PLUGIN=R/'wordpress/sustainable-catalyst-workspace'
MP=PLUGIN/'sustainable-catalyst-workspace.php'
RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(PLUGIN/'includes/class-sc-workspace.php').read_text()
REGPHP=(PLUGIN/'includes/class-sc-workspace-registry.php').read_text()
DEP=(PLUGIN/'includes/class-sc-workspace-deployment.php').read_text()
NAV=(PLUGIN/'assets/js/sc-workspace-research-navigation-v1.js').read_text()
EXP=(PLUGIN/'assets/js/sc-workspace-experience-v1.js').read_text()
RUNTIME=(PLUGIN/'assets/js/sc-workspace-wordpress-deployment-hardening-v1.js').read_text()
UI=(PLUGIN/'assets/js/sc-workspace-wordpress-deployment-hardening-ui-v1.js').read_text()
APP=(PLUGIN/'assets/js/workspace-v0.81.0.js').read_text()
CSS=(PLUGIN/'assets/css/workspace-v0.81.0.css').read_text()
MAN=json.loads((R/'release-manifest-v0.81.0.json').read_text())
OLD=json.loads((R/'history/release-manifest-v0.80.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.81.0.json').read_text())


def check(x,label):
    if not x:
        raise SystemExit('FAIL - v0.81 WordPress & Deployment Hardening gate: '+label)

check('Version: 0.81.0' in MAIN and "SC_WORKSPACE_VERSION', '0.81.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.81.0','0.80.0','WordPress & Deployment Hardening'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.81.0','0.80.0','WordPress & Deployment Hardening'),'registry lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema freeze')
for key in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:
    check(MAN[key]==OLD[key],'frozen '+key)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/deployment-hardening-contract'},'only planned REST addition')
check(not (set(OLD['rest_routes'])-set(MAN['rest_routes'])),'no inherited REST removal')

for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.81.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
    m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M)
    check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact WordPress header')

check('sc_workspace_bootstrap_failure' in MAIN and 'is_readable' in MAIN and 'return;' in MAIN,'safe bootstrap guard')
check('SC_Workspace_Deployment_Hardening::activate()' in MAIN and 'activation_preflight' in DEP,'activation preflight')
check("SC_Workspace_Deployment_Hardening::observe('runtime')" in MAIN,'runtime deployment observation')
check("array('SC_Workspace_Deployment_Hardening', 'admin_notice')" in MAIN,'deployment admin notice')
check('MAX_HISTORY = 12' in DEP and 'sc_workspace_deployment_history_v1' in DEP,'bounded deployment history')
check('project data' in DEP.lower() or 'project_data' in DEP,'project-data boundary documented')
check("PREVIOUS_RELEASE = '0.80.0'" in DEP,'rollback predecessor')
check('automatic_cache_purge' in DEP and 'automatic_rollback' in DEP,'no automatic destructive deployment action')

check("'sc-workspace-v0810'" in PHP and 'workspace-v0.81.0.js' in PHP and 'workspace-v0.81.0.css' in PHP,'current versioned assets')
check("wp_localize_script('sc-workspace-v0810'" in PHP,'current localized runtime')
check('sc-workspace-v0800' not in PHP and 'workspace-v0.80.0.js' not in PHP and 'workspace-v0.80.0.css' not in PHP,'no stale current assets in enqueue')
check("'/deployment-hardening-contract'" in PHP and 'deployment_hardening_contract' in PHP,'deployment REST contract')
check('data-scw-deployment-server-state' in PHP and 'data-scw-wordpress-deployment-hardening' in PHP,'deployment surface markers')
check('Run deployment check' in PHP and 'Export production checklist' in PHP,'deployment controls')
check('Project storage is not a cache' in PHP,'cache/data boundary')
check('sc-workspace-wordpress-deployment-hardening-v1' in PHP and 'sc-workspace-wordpress-deployment-hardening-ui-v1' in PHP,'deployment assets enqueued')

for route in ['final-audit','beta-closure','release-candidate','deployment','recovery-drills']:
    check("'"+route+"'" in NAV,'Review navigation '+route)
check("id:'deployment'" in EXP,'deployment experience command')
check("'deployment'" in APP,'deployment route recognition')
check('/* v0.81.0 — WordPress & Deployment Hardening */' in CSS,'deployment CSS layer')
check("const RELEASE_VERSION='0.81.0'" in RUNTIME,'deployment runtime release')
check('workspace-v0.81.0.js' in RUNTIME and 'workspace-v0.81.0.css' in RUNTIME,'runtime expected assets')
check('0.80.0' in RUNTIME and 'stale' in RUNTIME.lower(),'stale predecessor detection')
check('projectContentIncluded:false' in RUNTIME and 'rawUserAgentIncluded:false' in RUNTIME and 'serverFilesystemPathsIncluded:false' in RUNTIME,'privacy-minimized runtime report')
check('data-scw-wordpress-deployment-hardening' in UI,'deployment UI target')

check("BACKUP_KEY = 'sc_workspace_registry_backup_v0810'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0810'" in REGPHP,'current registry keys')
check('LEGACY_PENDING_KEY_V0800' in REGPHP,'v0.80 pending-key retry')
for legacy in ['V0790','V0780','V0770']:
    check('LEGACY_PENDING_KEY_'+legacy in REGPHP,'recent registry retry '+legacy)

hard=MAN['wordpress_deployment_hardening']
for key in ['release_candidate','feature_freeze','safe_bootstrap_guard','activation_preflight','bounded_deployment_history','server_package_integrity_check','mixed_version_browser_detection','versioned_asset_filenames','version_query_required','registry_pending_detection','recent_registry_pending_retry_repaired','review_navigation_release_surfaces_repaired','rollback_schema_compatible','rollback_artifact_required']:
    check(hard.get(key) is True,key)
for key in ['automatic_cache_purge','automatic_rollback','automatic_project_migration','project_data_inspected','project_data_mutated','new_product_subsystem','behavioral_telemetry','schema_migration_required']:
    check(hard.get(key) is False,key)
check(hard.get('deployment_history_limit')==12,'deployment history limit')
check(hard.get('rollback_release')=='0.80.0','rollback release')
check(hard.get('storage_schema_version')==35 and hard.get('project_schema')=='sc-workspace-project/20.0' and hard.get('project_export_schema')=='sc-workspace-project-export/20.0','hardening schema freeze')

for path in [
    'schemas/sc-workspace-wordpress-deployment-hardening-v1.schema.json',
    'schemas/sc-workspace-wordpress-deployment-report-v1.schema.json',
    'schemas/sc-workspace-wordpress-deployment-checklist-v1.schema.json',
    'schemas/sc-workspace-deployment-state-v1.schema.json',
    'docs/WORDPRESS_DEPLOYMENT_HARDENING_V0810.md',
    'RELEASE_NOTES_0.81.0.md',
    'history/release-manifest-v0.80.0.json',
    'history/workspace-product-record-v0.80.0.json',
]:
    check((R/path).exists(),path)
readme=(R/'README.md').read_text()
check('# Sustainable Catalyst Workspace v0.81.0' in readme and 'WordPress & Deployment Hardening' in readme,'README identity')

# RC hardening cannot pass by bypassing any inherited release-candidate gate.
for script in [
    'validate_public_beta_iii_defect_closure.py',
    'validate_security_privacy_audit_ii.py',
    'validate_accessibility_performance_final_audit.py',
    'validate_workspace_release_candidate_i.py',
]:
    subprocess.run([sys.executable,str(R/'scripts'/script)],check=True,cwd=R)

print('PASS - v0.81.0 WordPress & Deployment Hardening source gate')
