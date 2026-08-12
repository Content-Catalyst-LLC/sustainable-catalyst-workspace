from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.72.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.72.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MAINP.read_bytes(); MAIN=MAINP.read_text(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.72.0.js').read_text(); HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-workflow-guidance-v1.js').read_text(); UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-workflow-guidance-ui-v1.js').read_text(); CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.72.0.css').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.72.0' in MAIN and "SC_WORKSPACE_VERSION', '0.72.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.72.0','0.71.0','Research Workflow Guidance & Empty-State Refinement'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.72.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0720'" in PHP and 'workspace-v0.72.0.js' in PHP and 'workspace-v0.72.0.css' in PHP,'current cumulative assets')
check("wp_localize_script('sc-workspace-v0720'" in PHP,'current localization handle')
check("'/workflow-guidance-contract'" in PHP and 'workflow_guidance_contract' in PHP,'workflow guidance REST')
check('/wp-json/sc-workspace/v1/workflow-guidance-contract' in MAN['rest_routes'],'manifest REST route')
g=MAN['research_workflow_guidance']; check(g['mode']=='derived-contextual-advisory' and g['stages']==['orient','frame','gather','extract','connect','synthesize','compose','review'],'guidance stages')
for k in ['canonical_mutation','automatic_completion','automatic_task_creation','automatic_ai','automatic_navigation','hidden_readiness_score','behavioral_tracking','telemetry','schema_migration_required']: check(g[k] is False,'guidance boundary '+k)
for marker in ['frame-question','capture-source','extract-evidence','test-claim','synthesize-notes','review-next','hiddenReadinessScore:false','automaticTaskCreation:false','automaticAi:false']: check(marker in HELP,'helper '+marker)
check('SCWorkspaceWorkflowGuidance' in UI and 'data-scw-workflow-guidance' in PHP and 'data-scw-project-research-guidance' in PHP,'guidance UI')
check('No research questions yet. Frame one explicit question' in APP and 'No sources in the reading queue. Capture a source' in APP,'actionable empty states')
check('/* v0.72.0 — Research Workflow Guidance & Empty-State Refinement */' in CSS,'v0.72 CSS')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0720'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0720'" in REGPHP and 'LEGACY_PENDING_KEY_V0710' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.72.0','0.71.0','Research Workflow Guidance & Empty-State Refinement'),'registry record')
check((ROOT/'history/release-manifest-v0.71.0.json').exists() and (ROOT/'history/workspace-product-record-v0.71.0.json').exists(),'v0.71 history retained')
for f in ['schemas/sc-workspace-workflow-guidance-v1.schema.json','schemas/sc-workspace-empty-state-guidance-v1.schema.json','schemas/sc-workspace-workflow-guidance-report-v1.schema.json','docs/RESEARCH_WORKFLOW_GUIDANCE_EMPTY_STATES_V0720.md','RELEASE_NOTES_0.72.0.md']:
 check((ROOT/f).exists(),f)
print('PASS - v0.72.0 release validator')
