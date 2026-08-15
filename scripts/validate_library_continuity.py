from pathlib import Path
import json
from release_lineage import load_manifest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.3.0');OLD=load_manifest(R,'1.2.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();LCPHP=(P/'includes/class-sc-workspace-library-continuity.php').read_text();LCJS=(P/'assets/js/sc-workspace-library-continuity-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - historical v1.3.0 Library Continuity gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.3.0','1.2.0','Research Projects & Library Continuity'),'release identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/library-continuity-contract'},'only Library Continuity REST route added')
l=MAN['library_continuity'];check(set(l['record_families'])=={'saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation'},'five Library continuity families')
for k in ['authenticated_identity_reused','guest_workspace_preserved','personal_recommendations_private_by_default','explicit_package_or_same_origin_handoff','browser_local_staging','explicit_project_promotion_required','provenance_preserved','origin_ids_preserved','origin_urls_preserved']:check(l.get(k) is True,k)
for k in ['second_account_required','canonical_library_records_mutated','canonical_library_records_duplicated','automatic_library_pull','automatic_background_sync','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']:check(l.get(k) is False,k)
check(l['canonical_library_route']=='/knowledge-libraries/','canonical Library route')
check("'/library-continuity-contract'" in PHP and 'library_continuity_contract' in PHP and 'sc-workspace-library-continuity-v1' in PHP,'REST/enqueue preserved')
check('sc-workspace-library-continuity/1.0' in LCPHP and 'sc-library-workspace-continuity/1.0' in LCPHP,'server contract schemas preserved')
for token in ['saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation','canonicalLibraryRecordsMutated:false','automaticBackgroundSync:false','provenancePreserved:true']:check(token in LCJS,'continuity helper '+token)
for f in ['docs/RESEARCH_PROJECTS_LIBRARY_CONTINUITY_V130.md','RELEASE_NOTES_1.3.0.md','schemas/sc-workspace-library-continuity-record-v1.schema.json','schemas/sc-library-workspace-continuity-package-v1.schema.json','tests/test_library_continuity_contract.py','tests/test_library_continuity_runtime.js','tests/test_library_continuity_runtime.php','history/release-manifest-v1.3.0.json','history/workspace-product-record-v1.3.0.json']:check((R/f).exists(),f)
print('PASS - historical v1.3.0 Research Projects & Library Continuity gate preserved')
