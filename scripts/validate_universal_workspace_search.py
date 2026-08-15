from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.2.0');OLD=load_manifest(R,'1.1.0');REG=load_registry(R,'1.2.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();MAIN=(P/'sustainable-catalyst-workspace.php').read_text();USPHP=(P/'includes/class-sc-workspace-universal-search.php').read_text();USJS=(P/'assets/js/sc-workspace-universal-search-v1.js').read_text();APP=CUR.script_path.read_text();CSS=CUR.style_path.read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.2.0 Universal Workspace Search gate: '+l)
lineage=validate_current_release_lineage(R,'1.2.0','1.1.0');check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.2.0','1.1.0','Universal Workspace Search & Knowledge Retrieval'),'release identity')
check((REG['public_version'],REG['previous_version'],REG['release_name'],REG['lifecycle_state'],REG['release_channel'])==('1.2.0','1.1.0','Universal Workspace Search & Knowledge Retrieval','production','stable'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'] and MAN['schema_migration_required'] is False,'canonical schema freeze')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/universal-search-contract'},'only Universal Search REST route added')
u=MAN['universal_search'];expected={'project','object','notebook','notebook-block','research-question','research-claim','analysis-question','decision','briefing-draft','citation-reference','research-task'}
check(set(u['corpus'])==expected,'universal corpus')
for k in ['derived_from_local_records','cross_project','browser_local_index','deterministic_explainable_ranking','ranking_reasons_visible','canonical_origin_links','saved_searches_reused','citation_library_included','research_tasks_included']:check(u.get(k) is True,k)
for k in ['server_index','semantic_embeddings','automatic_ai','automatic_semantic_inference','automatic_canonical_mutation','behavioral_telemetry','query_telemetry','schema_migration_required']:check(u.get(k) is False,k)
check('Version: 1.2.0' in MAIN and "SC_WORKSPACE_VERSION', '1.2.0'" in MAIN and 'class-sc-workspace-universal-search.php' in MAIN,'WordPress bootstrap identity')
check("'/universal-search-contract'" in PHP and 'universal_search_contract' in PHP and 'sc-workspace-universal-search-v1' in PHP,'REST/helper enqueue integration')
check(CUR.script_name in PHP and CUR.style_name in PHP and CUR.asset_handle in PHP and 'data-release-stage="universal-search"' in PHP,'current cumulative assets/stage')
check('sc-workspace-universal-search-contract/1.0' in USPHP and 'sc-workspace-universal-search/1.0' in USPHP,'server search contract')
for token in ['citation-reference','research-task','analysis-question','briefing-draft','derivedFromLocalRecords','semanticEmbeddings:false','queryTelemetry:false','automaticCanonicalMutation:false']:check(token in USJS,'Universal Search helper '+token)
for token in ['openUniversalEntry','universalEntries','data-scw-cockpit-universal-search','No local Workspace records match these retrieval fields.','citation-reference','research-task']:check(token in APP,'cumulative runtime '+token)
check("PREVIOUS_RELEASE = '1.1.0'" in DEP and "ROLLBACK_RELEASE = '1.1.0'" in DEP and CUR.script_name in DEP and CUR.style_name in DEP,'deployment current predecessor/assets')
check("PREVIOUS_RELEASE = '1.1.0'" in PROD and "ROLLBACK_RELEASE = '1.1.0'" in PROD and CUR.script_name in PROD and CUR.style_name in PROD,'production current predecessor/assets')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v120'" in REGPHP and 'LEGACY_PENDING_KEY_V110' in REGPHP,'registry retry lineage')
check('/* v1.2.0 — Universal Workspace Search & Knowledge Retrieval */' in CSS,'v1.2 CSS marker')
for f in ['docs/UNIVERSAL_WORKSPACE_SEARCH_KNOWLEDGE_RETRIEVAL_V120.md','RELEASE_NOTES_1.2.0.md','tests/test_universal_workspace_search_contract.py','tests/test_universal_workspace_search_runtime.js','tests/test_universal_workspace_search_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_workspace_home_project_cockpit.py')],check=True,cwd=R)
print('PASS - v1.2.0 Universal Workspace Search & Knowledge Retrieval source gate')
