from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.5.0');OLD=load_manifest(R,'1.4.0');REG=load_registry(R,'1.5.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();MAIN=(P/'sustainable-catalyst-workspace.php').read_text();LPHP=(P/'includes/class-sc-workspace-lab-integration.php').read_text();LJS=(P/'assets/js/sc-workspace-lab-integration-v1.js').read_text();APP=CUR.script_path.read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.5.0 Lab integration gate: '+l)
lineage=validate_current_release_lineage(R,'1.5.0','1.4.0');check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.5.0','1.4.0','Lab & Scientific Workspace Integration'),'release identity')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('1.5.0','1.4.0','Lab & Scientific Workspace Integration'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/lab-integration-contract'},'only Lab integration REST route added')
g=MAN['lab_integration']
check(g['schema']=='sc-workspace-lab-integration/1.0','contract schema')
check(g['context_package_schema']=='sc-workspace-lab-scientific-context/1.0' and g['return_package_schema']=='sc-workspace-lab-scientific-return/1.0' and g['scientific_artifact_schema']=='sc-workspace-scientific-artifact/1.0','portable schemas')
check(g['canonical_lab_route']=='/lab/' and len(g['supported_workflows'])==8,'Lab route/workflows')
check(set(g['context_object_types'])=={'source','evidence','dataset','analysis','document','export'},'context object types')
check(set(g['return_artifact_families'])=={'dataset','derived-variable','model','graph','posterior-summary','diagnostic','experiment-result','scientific-report'},'return families')
check(g['canonical_materialization']=={'dataset':'dataset','derived-variable':'dataset','model':'analysis','graph':'export','posterior-summary':'analysis','diagnostic':'analysis','experiment-result':'analysis','scientific-report':'document'},'canonical materialization')
for k in ['explicit_context_selection','portable_context_package','round_trip_handoff_identity_required','project_and_handoff_match_required','source_object_ids_preserved','provenance_preserved','methodology_metadata_preserved','uncertainty_metadata_preserved','units_metadata_preserved','explicit_return_import_required','explicit_workspace_materialization_required','traceability_edges_from_selected_context']:check(g.get(k) is True,k)
for k in ['outbound_url_carries_content','lab_execution_automatic','automatic_context_upload','automatic_return_commit','automatic_ai','behavioral_telemetry','query_telemetry','canonical_lab_records_mutated','schema_migration_required']:check(g.get(k) is False,k)
check('Version: 1.5.0' in MAIN and "SC_WORKSPACE_VERSION', '1.5.0'" in MAIN and 'class-sc-workspace-lab-integration.php' in MAIN,'WordPress identity/bootstrap')
check("'/lab-integration-contract'" in PHP and 'lab_integration_contract' in PHP and 'sc-workspace-lab-integration-v1' in PHP,'REST/enqueue')
check('data-release-stage="lab-scientific-integration"' in PHP and CUR.script_name in PHP and CUR.style_name in PHP,'current stage/assets')
for t in ['sc-workspace-lab-integration/1.0','sc-workspace-lab-scientific-context/1.0','sc-workspace-lab-scientific-return/1.0','sc-workspace-scientific-artifact/1.0','posterior-predictive-modeling','traceabilityEdgesFromSelectedContext']:check(t in LPHP,'PHP contract '+t)
for t in ['buildContextPackage','normalizeReturn','toWorkspaceReturnPacket','returnTemplate','FNV-1a-32','scientific-return','automaticContextUpload:false','automaticReturnCommit:false']:check(t in LJS,'JS bridge '+t)
for t in ['SCIENTIFIC WORKSPACE / LAB ROUND TRIP','Open Lab with IDs','Export scientific context','Export return template','Import Lab return','Explicit Lab round trip']:check(t in (PHP+APP),'visible/runtime '+t)
check("PREVIOUS_RELEASE = '1.4.0'" in DEP and "ROLLBACK_RELEASE = '1.4.0'" in DEP and CUR.script_name in DEP and 'class-sc-workspace-lab-integration.php' in DEP,'deployment predecessor/preflight')
check("PREVIOUS_RELEASE = '1.4.0'" in PROD and "ROLLBACK_RELEASE = '1.4.0'" in PROD and CUR.script_name in PROD,'production predecessor')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v150'" in REGPHP and 'LEGACY_PENDING_KEY_V140' in REGPHP,'registry retry lineage')
for f in ['docs/LAB_SCIENTIFIC_WORKSPACE_INTEGRATION_V150.md','RELEASE_NOTES_1.5.0.md','schemas/sc-workspace-lab-scientific-context-v1.schema.json','schemas/sc-workspace-lab-scientific-return-v1.schema.json','schemas/sc-workspace-scientific-artifact-v1.schema.json','tests/test_lab_scientific_workspace_integration_contract.py','tests/test_lab_scientific_workspace_integration_runtime.js','tests/test_lab_scientific_workspace_integration_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_knowledge_graph_relationship_explorer.py')],check=True,cwd=R)
print('PASS - v1.5.0 Lab & Scientific Workspace Integration source gate')
