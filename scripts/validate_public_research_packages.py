from pathlib import Path
import json
from release_lineage import load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=load_manifest(R,'1.14.0');OLD=load_manifest(R,'1.13.0');REG=load_registry(R,'1.14.0');MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();JS=(P/'assets/js/sc-workspace-public-research-packages-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.14.0 public research packages gate: '+l)
lineage=validate_current_release_lineage(R,'1.14.0','1.13.0');check(lineage['ok'],'lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.14.0','1.13.0','Public Research Packages & Portable Knowledge Objects'),'release identity')
check((REG['public_version'],REG['previous_version'])==('1.14.0','1.13.0'),'registry identity')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']),'schema freeze')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/public-research-packages-contract'},'only route added')
g=MAN['public_research_packages'];check(g['private_by_default'] and g['explicit_selection_required'] and g['explicit_publication_confirmation_required'] and g['license_required_for_public'],'publication boundary')
for k in ['canonical_workspace_records_mutated','automatic_publication','automatic_upload','automatic_network_request','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']:check(not g[k],k)
check(g['integrity_algorithm']=='SHA-256' and g['portable_knowledge_objects'] and g['provenance_preserved'],'integrity/provenance')
check('Version: 1.14.0' in MAIN and "SC_WORKSPACE_VERSION', '1.14.0'" in MAIN,'WordPress identity')
check("'/public-research-packages-contract'" in PHP and 'Public Research Packages &amp; Portable Knowledge Objects' in PHP and 'data-release-stage="public-research-packages"' in PHP,'surface')
check("PREVIOUS_RELEASE = '1.13.0'" in DEP and "ROLLBACK_RELEASE = '1.13.0'" in DEP and "PREVIOUS_RELEASE = '1.13.0'" in PROD,'predecessor')
for f in ['docs/PUBLIC_RESEARCH_PACKAGES_PORTABLE_KNOWLEDGE_OBJECTS_V1140.md','RELEASE_NOTES_1.14.0.md','schemas/sc-workspace-public-research-packages-v1.schema.json','schemas/sc-workspace-public-research-package-v1.schema.json','schemas/sc-workspace-portable-knowledge-object-v1.schema.json','schemas/sc-workspace-public-research-package-manifest-v1.schema.json','schemas/sc-workspace-publication-receipt-v1.schema.json','tests/test_public_research_packages_contract.py','tests/test_public_research_packages_runtime.js','tests/test_public_research_packages_runtime.php']:check((R/f).exists(),f)
for x in ['sc-workspace-public-research-packages/1.0','function buildPackage','function releasePackage','SHA-256','privateByDefault:true','automaticPublication:false']:check(x in JS,'runtime marker '+x)
print('PASS - v1.14.0 Public Research Packages & Portable Knowledge Objects source gate')
