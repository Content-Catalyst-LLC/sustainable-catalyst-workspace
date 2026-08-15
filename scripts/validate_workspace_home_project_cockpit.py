from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.1.0');OLD=load_manifest(R,'1.0.1');REG=load_registry(R,'1.1.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();HOME=(P/'includes/class-sc-workspace-home.php').read_text();HELP=(P/'assets/js/sc-workspace-home-v1.js').read_text();NAV=(P/'assets/js/sc-workspace-research-navigation-v1.js').read_text();APP=CUR.script_path.read_text();CSS=CUR.style_path.read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v1.1.0 Workspace Home / Project Cockpit gate: '+l)
lineage=validate_current_release_lineage(R);check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.1.0','1.0.1','Workspace Home, Project Cockpit & Navigation Refinement'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'],REG['lifecycle_state'],REG['release_channel'])==('1.1.0','1.0.1','Workspace Home, Project Cockpit & Navigation Refinement','production','stable'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'] and MAN['schema_migration_required'] is False,'canonical freeze')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/workspace-home-contract'},'only Home contract REST route added')
h=MAN['workspace_home_project_cockpit']
for k in ['project_cockpit','active_project_summary','recent_project_resume','deterministic_next_actions','research_shortcuts','project_mode_shortcuts','review_navigation_progressive_disclosure','command_palette_preserved','specialized_surfaces_preserved']:check(h.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_project_mutation','automatic_ai','behavioral_telemetry','hidden_productivity_score']:check(h.get(k) is False,k)
check("primary_area_label'=>'Home'" in HOME and "'project_cockpit'=>true" in HOME and "'automatic_project_mutation'=>false" in HOME and "'automatic_ai'=>false" in HOME,'server Home contract')
for token in ['function summarize','function nextAction','choose-project','frame-work','capture-evidence','analyze','compose','review']:check(token in HELP,'Home helper '+token)
check("start:{label:'Home'" in NAV and all(x in NAV for x in ["projects:{label:'Projects'","research:{label:'Research'","review:{label:'Review'","exchange:{label:'Exchange'"]),'five-area navigation labels')
check('data-scw-project-cockpit' in PHP and 'PROJECT COCKPIT' in PHP and 'More review tools' in PHP,'Home/cockpit and progressive Review UI')
check("'/workspace-home-contract'" in PHP and 'workspace_home_contract' in PHP,'Home REST integration')
check(CUR.script_name in PHP and CUR.style_name in PHP and ("'"+CUR.asset_handle+"'") in PHP,'current assets')
check(("PREVIOUS_RELEASE = '"+CUR.previous_version+"'") in DEP and ("ROLLBACK_RELEASE = '"+CUR.previous_version+"'") in DEP and CUR.script_name in DEP and CUR.style_name in DEP,'deployment current predecessor/assets')
check(("PREVIOUS_RELEASE = '"+CUR.previous_version+"'") in PROD and ("ROLLBACK_RELEASE = '"+CUR.previous_version+"'") in PROD and CUR.script_name in PROD and CUR.style_name in PROD,'production current predecessor/assets')
cur_token=''.join(CUR.version.split('.'));prev_token='V'+''.join(CUR.previous_version.split('.'));check(("BACKUP_KEY = 'sc_workspace_registry_backup_v"+cur_token+"'") in REGPHP and ('LEGACY_PENDING_KEY_'+prev_token) in REGPHP,'registry retry lineage')
check('GENERAL AVAILABILITY' in PHP and 'Local-first' in PHP,'GA product framing')
check('/* v1.1.0 — Workspace Home, Project Cockpit & Navigation Refinement */' in CSS,'current CSS marker')
for f in ['docs/WORKSPACE_HOME_PROJECT_COCKPIT_NAVIGATION_V110.md','RELEASE_NOTES_1.1.0.md','tests/test_workspace_home_project_cockpit_contract.py','tests/test_workspace_home_project_cockpit_runtime.js','tests/test_workspace_home_project_cockpit_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_ga_field_stabilization.py')],check=True,cwd=R)
print(f'PASS - v1.1.0 Workspace Home, Project Cockpit & Navigation Refinement source gate under current v{CUR.version}')
