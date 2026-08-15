from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace';MAN=load_manifest(R,'1.5.0');OLD=load_manifest(R,'1.4.0');REG=load_registry(R,'1.5.0');PHP=(P/'includes/class-sc-workspace.php').read_text();MAIN=(P/'sustainable-catalyst-workspace.php').read_text();LPHP=(P/'includes/class-sc-workspace-lab-integration.php').read_text();LJS=(P/'assets/js/sc-workspace-lab-integration-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - inherited v1.5.0 Lab integration gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.5.0','1.4.0','Lab & Scientific Workspace Integration'),'historical release identity')
check((REG['public_version'],REG['previous_version'])==('1.5.0','1.4.0'),'historical registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check('/wp-json/sc-workspace/v1/lab-integration-contract' in MAN['rest_routes'],'historical route')
g=MAN['lab_integration'];check(len(g['supported_workflows'])==8 and g['canonical_lab_route']=='/lab/','workflow/route');check(g['explicit_context_selection'] and g['traceability_edges_from_selected_context'],'explicit/traceability');check(not g['automatic_context_upload'] and not g['automatic_return_commit'] and not g['automatic_ai'],'boundaries')
check('Version: 1.7.0' in MAIN and "SC_WORKSPACE_VERSION', '1.7.0'" in MAIN,'current runtime advanced')
for t in ['sc-workspace-lab-integration/1.0','posterior-predictive-modeling','traceabilityEdgesFromSelectedContext']:check(t in LPHP,'PHP contract '+t)
for t in ['buildContextPackage','toWorkspaceReturnPacket','scientific-return','automaticReturnCommit:false']:check(t in LJS,'JS bridge '+t)
subprocess.run([sys.executable,str(R/'scripts/validate_knowledge_graph_relationship_explorer.py')],check=True,cwd=R)
print('PASS - inherited v1.5.0 Lab & Scientific Workspace Integration source gate under current v'+CUR.version)
