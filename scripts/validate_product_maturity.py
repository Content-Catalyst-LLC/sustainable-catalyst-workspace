from pathlib import Path
import json
from release_lineage import load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=load_manifest(R,'1.15.0');OLD=load_manifest(R,'1.14.0');REG=load_registry(R,'1.15.0');MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();JS=(P/'assets/js/sc-workspace-product-maturity-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.15.0 product maturity gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.15.0','1.14.0','1.x Product Maturity & 2.0 Candidate'),'release identity')
check((REG['public_version'],REG['previous_version'])==('1.15.0','1.14.0'),'registry identity')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']),'schema freeze')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/product-maturity-contract'},'only route added')
g=MAN['product_maturity'];check(len(g['dimensions'])==12 and g['states']==['ready','attention','blocked'],'maturity dimensions/states');check(g['human_candidate_designation_required'] and g['unresolved_blocker_prevents_candidate'] and not g['numeric_score'],'evidence boundary')
for k in ['automatic_2_0_promotion','v2_schema_introduced','automatic_migration','breaking_v1_contract_change','canonical_workspace_records_mutated','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']:check(not g[k],k)
check(g['v1_api_compatibility_preserved'],'v1 compatibility')
check((P/'assets/js/workspace-v1.15.0.js').exists() and (P/'assets/css/workspace-v1.15.0.css').exists(),'historical v1.15 cumulative assets preserved')
check("'/product-maturity-contract'" in PHP and 'Product Maturity &amp; 2.0 Candidate' in PHP and 'data-scw-product-maturity' in PHP,'historical surface preserved')
check(MAN['product_maturity']['rollback_release']=='1.14.0','historical v1.15 rollback metadata')
for f in ['docs/PRODUCT_MATURITY_2_0_CANDIDATE_V1150.md','RELEASE_NOTES_1.15.0.md','schemas/sc-workspace-product-maturity-v1.schema.json','schemas/sc-workspace-product-maturity-dossier-v1.schema.json','schemas/sc-workspace-product-maturity-compatibility-matrix-v1.schema.json','schemas/sc-workspace-1x-deprecation-register-v1.schema.json','schemas/sc-workspace-2-0-candidate-boundary-v1.schema.json','tests/test_product_maturity_2_0_candidate_contract.py','tests/test_product_maturity_2_0_candidate_runtime.js','tests/test_product_maturity_2_0_candidate_runtime.php']:check((R/f).exists(),f)
for x in ['sc-workspace-2-0-candidate-boundary/1.0','function buildDossier','function candidateBoundary','numericScore:false','automatic20Promotion:false','v2SchemaIntroduced:false']:check(x in JS,'runtime marker '+x)
print('PASS - v1.15.0 1.x Product Maturity & 2.0 Candidate source gate')
# Preserve entire predecessor validation chain.
from validate_public_research_packages import *
