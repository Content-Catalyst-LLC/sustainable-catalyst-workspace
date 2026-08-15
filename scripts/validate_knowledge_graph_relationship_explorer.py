from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.4.0');OLD=load_manifest(R,'1.3.0');REG=load_registry(R,'1.4.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();MAIN=(P/'sustainable-catalyst-workspace.php').read_text();KPHP=(P/'includes/class-sc-workspace-knowledge-graph-explorer.php').read_text();KJS=(P/'assets/js/sc-workspace-relationship-explorer-v2.js').read_text();APP=CUR.script_path.read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.4.0 Knowledge Graph gate: '+l)
lineage=validate_current_release_lineage(R,'1.4.0','1.3.0');check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.4.0','1.3.0','Knowledge Graph & Relationship Explorer'),'release identity')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('1.4.0','1.3.0','Knowledge Graph & Relationship Explorer'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/knowledge-graph-explorer-contract'},'only graph explorer REST route added')
g=MAN['knowledge_graph_explorer'];
for k in ['explicit_path_tracing','incoming_outgoing_backlink_ledger','edge_explanation_visible','library_continuity_pointers_included','universal_search_origin_routing','portable_graph_snapshot_export','derived_at_runtime']:check(g.get(k) is True,k)
for k in ['snapshot_copies_canonical_bodies','server_graph_database','semantic_embeddings','automatic_relationship_inference','automatic_semantic_similarity_edges','automatic_ai','behavioral_telemetry','query_telemetry','canonical_records_mutated','schema_migration_required']:check(g.get(k) is False,k)
check(g['max_path_depth']==5 and 'library-record' in g['node_families'],'path depth/library node')
check('Version: 1.4.0' in MAIN and "SC_WORKSPACE_VERSION', '1.4.0'" in MAIN and 'class-sc-workspace-knowledge-graph-explorer.php' in MAIN,'WordPress identity/bootstrap')
check("'/knowledge-graph-explorer-contract'" in PHP and 'knowledge_graph_explorer_contract' in PHP and 'sc-workspace-relationship-explorer-v2' in PHP,'REST/enqueue')
check('data-release-stage="knowledge-graph-explorer"' in PHP and CUR.script_name in PHP and CUR.style_name in PHP,'current stage/assets')
for t in ['sc-workspace-knowledge-graph-explorer/1.0','sc-workspace-knowledge-graph-snapshot/1.0','maxPathDepth','serverGraphDatabase']:check(t in KPHP,'PHP contract '+t)
for t in ['shortestPath','backlinks','edgeExplanation','snapshot','originates-in-library','library-record','canonicalBodiesCopied:false','automaticRelationshipInference:false']:check(t in KJS,'JS explorer '+t)
for t in ['data-scw-graph-path-from','Trace explicit path','Export graph snapshot','workspace-knowledge-graph-snapshot.json']:check(t in (PHP+APP),'visible/runtime '+t)
check("PREVIOUS_RELEASE = '1.3.0'" in DEP and "ROLLBACK_RELEASE = '1.3.0'" in DEP and CUR.script_name in DEP,'deployment predecessor')
check("PREVIOUS_RELEASE = '1.3.0'" in PROD and "ROLLBACK_RELEASE = '1.3.0'" in PROD and CUR.script_name in PROD,'production predecessor')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v140'" in REGPHP and 'LEGACY_PENDING_KEY_V130' in REGPHP,'registry retry lineage')
for f in ['docs/KNOWLEDGE_GRAPH_RELATIONSHIP_EXPLORER_V140.md','RELEASE_NOTES_1.4.0.md','schemas/sc-workspace-knowledge-graph-snapshot-v1.schema.json','tests/test_knowledge_graph_relationship_explorer_contract.py','tests/test_knowledge_graph_relationship_explorer_runtime.js','tests/test_knowledge_graph_relationship_explorer_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_library_continuity.py')],check=True,cwd=R)
print('PASS - v1.4.0 Knowledge Graph & Relationship Explorer source gate')
