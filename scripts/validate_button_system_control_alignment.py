from pathlib import Path
from release_lineage import load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'2.0.1'); OLD=load_manifest(R,'2.0.0'); REG=load_registry(R,'2.0.1'); CURRENT=load_manifest(R,'2.0.3')
MAIN=(P/'sustainable-catalyst-workspace.php').read_text(); PHP=(P/'includes/class-sc-workspace.php').read_text(); CSS=(P/'assets/css/workspace-v2.0.1.css').read_text(); BTN=(P/'includes/class-sc-workspace-button-system.php').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - historical v2.0.1 Button System gate: '+l)
lineage=validate_current_release_lineage(R,'2.0.3','2.0.2'); check(lineage['ok'],'current lineage: '+str(lineage['errors']))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('2.0.1','2.0.0','Button System, Control Alignment & Interaction-State Repair'),'historical release identity')
check((REG['public_version'],REG['previous_version'])==('2.0.1','2.0.0'),'historical registry identity')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']),'historical schema freeze')
b=MAN['button_system_repair']; check(b['desktop_minimum_control_height_px']==40 and b['touch_minimum_control_height_px']==44,'target sizes'); check(b['focus_visible'] and b['forced_colors_supported'],'accessibility states'); check(b['connected_product_actions_use_intentional_grid'] and b['status_outputs_are_information_surfaces'],'alignment/status repair'); check(not b['javascript_behavior_change'] and not b['schema_migration_required'] and not b['canonical_content_mutation'],'surgical boundary')
check(CURRENT['version']=='2.0.3' and CURRENT['previous_version']=='2.0.2','current patch lineage')
check('Version: 2.0.3' in MAIN and "SC_WORKSPACE_VERSION', '2.0.3'" in MAIN,'current WordPress identity')
for marker in ['--scw-control-height:40px','min-height:var(--scw-control-height)','grid-template-columns:repeat(2,minmax(0,1fr))']:
    check(marker in CSS, 'preserved repair marker '+marker)
check("register_rest_route('sc-workspace/v2', '/button-system-contract'" in PHP and 'SC_Workspace_Button_System::contract()' in PHP,'historical REST contract preserved')
for f in ['docs/BUTTON_SYSTEM_CONTROL_ALIGNMENT_INTERACTION_STATE_REPAIR_V201.md','RELEASE_NOTES_2.0.1.md','tests/test_button_system_control_alignment_contract.py','tests/test_button_system_control_alignment_runtime.php']:
    check((R/f).exists(),f)
print('PASS - historical v2.0.1 Button System source gate preserved under v2.0.3')
from validate_connected_knowledge_workspace_v2 import *
