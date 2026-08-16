from pathlib import Path
import json
from release_lineage import load_manifest, load_registry
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=load_manifest(R,'2.0.0');OLD=load_manifest(R,'1.15.0');REG=load_registry(R,'2.0.0');CURRENT=load_manifest(R,'2.0.1');MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();JS=(P/'assets/js/sc-workspace-connected-knowledge-v2.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - historical v2.0.0 Connected Knowledge gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('2.0.0','1.15.0','Connected Knowledge Workspace'),'historical release identity')
check((REG['public_version'],REG['previous_version'])==('2.0.0','1.15.0'),'historical registry identity')
check(CURRENT['version']=='2.0.1' and CURRENT['previous_version']=='2.0.0','current patch lineage')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']),'data contract compatibility')
g=MAN['connected_knowledge_workspace'];check(g['stable_major_release'] and g['v1_rest_namespace_preserved'] and g['v2_rest_namespace_available'],'major version API boundary');check(g['v1_project_compatibility'] and g['v1_export_compatibility'] and not g['v2_native_project_schema_introduced'],'project/export compatibility');check(not g['schema_migration_required'] and not g['automatic_migration'],'no forced migration')
check(len(g['surfaces'])==11 and len(g['context_families'])==14 and g['single_context_envelope'],'connected context')
for k in ['automatic_cross_product_execution','automatic_context_upload','automatic_return_commit','automatic_ai','canonical_workspace_records_mutated','behavioral_telemetry','query_telemetry']:check(not g[k],k)
check("register_rest_route('sc-workspace/v2', '/connected-knowledge-contract'" in PHP and 'SC_Workspace_Connected_Knowledge::contract()' in PHP,'v2 REST surface')
check('Version: 2.0.1' in MAIN and "SC_WORKSPACE_VERSION', '2.0.1'" in MAIN,'current WordPress identity')
check("PREVIOUS_RELEASE = '2.0.0'" in DEP and "ROLLBACK_RELEASE = '2.0.0'" in DEP and "PREVIOUS_RELEASE = '2.0.0'" in PROD,'current rollback lineage')
for f in ['docs/CONNECTED_KNOWLEDGE_WORKSPACE_V200.md','RELEASE_NOTES_2.0.0.md','release-manifest-v2.0.0.json','registry/workspace-product-record-v2.0.0.json','schemas/sc-workspace-connected-knowledge-workspace-v2.schema.json','schemas/sc-workspace-connected-knowledge-context-v2.schema.json','schemas/sc-workspace-knowledge-object-reference-v2.schema.json','schemas/sc-workspace-knowledge-route-v2.schema.json','schemas/sc-workspace-v1-compatibility-registry-v2.schema.json','schemas/sc-workspace-connected-knowledge-receipt-v2.schema.json','tests/test_connected_knowledge_workspace_v2_contract.py','tests/test_connected_knowledge_workspace_v2_runtime.js','tests/test_connected_knowledge_workspace_v2_runtime.php','wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.0.0.js','wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.0.css']:check((R/f).exists(),f)
for x in ['sc-workspace-connected-knowledge-workspace/2.0','v1RestNamespacePreserved:true','v2RestNamespaceAvailable:true','automaticCrossProductExecution:false']:check(x in JS,'runtime marker '+x)
print('PASS - historical v2.0.0 Connected Knowledge Workspace source gate')
from validate_product_maturity import *
