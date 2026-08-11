from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.71.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.71.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
RAW=MAINP.read_bytes(); MAIN=MAINP.read_text(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.71.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-first-run-onboarding-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.71.0.css').read_text()
BETA2=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()

def check(ok,label):
    if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.71.0' in MAIN and "SC_WORKSPACE_VERSION', '0.71.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.71.0','0.70.0','First-Run Onboarding & Project Creation'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.71.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
    m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M)
    check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0710'" in PHP and 'workspace-v0.71.0.js' in PHP and 'workspace-v0.71.0.css' in PHP,'v0.71 cumulative assets')
check("wp_localize_script('sc-workspace-v0710'" in PHP,'current asset localization handle')
check('sc-workspace-first-run-onboarding-v1.js' in PHP and "'/first-run-onboarding-contract'" in PHP,'first-run helper and REST contract')
check('/wp-json/sc-workspace/v1/first-run-onboarding-contract' in MAN['rest_routes'],'first-run REST manifest')
o=MAN['first_run_onboarding']
check(o['first_run_detection']=='zero-local-projects' and o['starter_count']==5,'first-run detection and starters')
check(o['starters']==['blank','research-investigation','analytical-assessment','decision-case','publication-preparation'],'starter identities')
check(o['project_creation']=='explicit-submit' and o['blank_projects_supported'] is True and o['guest_use_first_class'] is True,'explicit creation model')
for key in ['account_required','separate_behavioral_profile','automatic_project_creation','automatic_starter_selection','automatic_upload','automatic_sync','automatic_lifecycle_advance','automatic_ai','schema_migration_required']:
    check(o[key] is False,'first-run governance '+key)
for marker in ['sc-workspace-first-run-onboarding/1.0','sc-workspace-first-project-draft/1.0','sc-workspace-first-run-onboarding-report/1.0','explicit-submit','zero-local-projects']:
    check(marker in HELP,'helper '+marker)
check('data-scw-first-run' in PHP and 'data-scw-first-run-form' in PHP and 'Create first project' in PHP,'first-run Start surface')
check('function createFirstRunProject(input)' in APP and "firstRunForm.addEventListener('submit'" in APP and 'onboarding.creationPlan' in APP,'explicit first-run creation wiring')
check('projectTemplate(plan.draft.title, plan.draft.description)' in APP and 'startGuidedWorkflow(project, plan.starter.workflow)' in APP,'blank and guided creation reuse canonical project functions')
check('/* v0.71.0 — First-Run Onboarding & Project Creation */' in CSS and '.scw-first-run-starters' in CSS,'first-run CSS')
check("expectedVersion:'0.71.0'" in BETA2 and "root.dataset.version==='0.71.0'" in BETA2,'Beta II current-version gate')
check("workspaceVersion:'0.71.0'" in COMP,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0710'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0710'" in REGPHP and 'LEGACY_PENDING_KEY_V0700' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.71.0','0.70.0','First-Run Onboarding & Project Creation'),'registry record')
check((ROOT/'history/release-manifest-v0.70.0.json').exists() and (ROOT/'history/workspace-product-record-v0.70.0.json').exists(),'v0.70.0 history retained')
for f in ['schemas/sc-workspace-first-run-onboarding-v1.schema.json','schemas/sc-workspace-first-project-draft-v1.schema.json','schemas/sc-workspace-first-run-onboarding-report-v1.schema.json','docs/FIRST_RUN_ONBOARDING_PROJECT_CREATION_V0710.md','RELEASE_NOTES_0.71.0.md','VALIDATION_REPORT_0.71.0.md']:
    check((ROOT/f).exists(),f)
print('PASS - v0.71.0 release validator')
