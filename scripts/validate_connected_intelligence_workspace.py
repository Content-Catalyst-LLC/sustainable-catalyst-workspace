from pathlib import Path
import subprocess,sys
from release_lineage import load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=load_manifest(R,'1.13.0');OLD=load_manifest(R,'1.12.0');REG=load_registry(R,'1.13.0');MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();JS=(P/'assets/js/sc-workspace-connected-intelligence-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.13.0 connected intelligence gate: '+l)
lineage=validate_current_release_lineage(R,'1.13.0','1.12.0');check(lineage['ok'],'lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.13.0','1.12.0','Connected Intelligence Workspace'),'release identity');check((REG['public_version'],REG['previous_version'])==('1.13.0','1.12.0'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/connected-intelligence-contract'},'only route added')
g=MAN['connected_intelligence'];check(len(g['products'])==5 and g['site_intelligence_context'] and g['lab_roundtrip'] and g['workbench_roundtrip'] and g['decision_studio_roundtrip'],'five-product connectivity')
for k in ['explicit_context_selection','stable_ids_only_in_urls','portable_context_export','provenance_preserved','return_to_origin','context_receipts_metadata_only']:check(g[k] is True,k)
for k in ['automatic_cross_product_execution','automatic_network_request','automatic_context_upload','automatic_return_commit','automatic_ai','background_federation','canonical_specialist_records_mutated','behavioral_telemetry','query_telemetry','schema_migration_required']:check(g[k] is False,k)
check('Version: 1.13.0' in MAIN and "SC_WORKSPACE_VERSION', '1.13.0'" in MAIN,'WordPress identity');check("'/connected-intelligence-contract'" in PHP and 'Connected Intelligence Workspace' in PHP and 'sc-workspace-connected-intelligence-v1' in PHP,'surface');check('data-release-stage="connected-intelligence"' in PHP,'stage');check("PREVIOUS_RELEASE = '1.12.0'" in DEP and "ROLLBACK_RELEASE = '1.12.0'" in DEP and "PREVIOUS_RELEASE = '1.12.0'" in PROD,'predecessor')
for f in ['docs/CONNECTED_INTELLIGENCE_WORKSPACE_V1130.md','RELEASE_NOTES_1.13.0.md','schemas/sc-workspace-connected-intelligence-v1.schema.json','schemas/sc-workspace-connected-intelligence-context-v1.schema.json','schemas/sc-workspace-connected-intelligence-route-v1.schema.json','schemas/sc-workspace-connected-intelligence-receipt-v1.schema.json','tests/test_connected_intelligence_contract.py','tests/test_connected_intelligence_runtime.js','tests/test_connected_intelligence_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_institutional_scale_hardening.py')],check=True,cwd=R)
print('PASS - v1.13.0 Connected Intelligence Workspace source gate')
