from pathlib import Path
import json,subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.3.0');OLD=load_manifest(R,'1.2.0');REG=load_registry(R,'1.3.0')
PHP=(P/'includes/class-sc-workspace.php').read_text();MAIN=(P/'sustainable-catalyst-workspace.php').read_text();LCPHP=(P/'includes/class-sc-workspace-library-continuity.php').read_text();LCJS=(P/'assets/js/sc-workspace-library-continuity-v1.js').read_text();APP=CUR.script_path.read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v1.3.0 Library Continuity gate: '+l)
lineage=validate_current_release_lineage(R,'1.3.0','1.2.0');check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.3.0','1.2.0','Research Projects & Library Continuity'),'release identity')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('1.3.0','1.2.0','Research Projects & Library Continuity'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/library-continuity-contract'},'only Library Continuity REST route added')
l=MAN['library_continuity'];check(set(l['record_families'])=={'saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation'},'five Library continuity families')
for k in ['authenticated_identity_reused','guest_workspace_preserved','personal_recommendations_private_by_default','explicit_package_or_same_origin_handoff','browser_local_staging','explicit_project_promotion_required','provenance_preserved','origin_ids_preserved','origin_urls_preserved']:check(l.get(k) is True,k)
for k in ['second_account_required','canonical_library_records_mutated','canonical_library_records_duplicated','automatic_library_pull','automatic_background_sync','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']:check(l.get(k) is False,k)
check(l['canonical_library_route']=='/knowledge-libraries/','canonical Library route')
check('Version: 1.3.0' in MAIN and "SC_WORKSPACE_VERSION', '1.3.0'" in MAIN and 'class-sc-workspace-library-continuity.php' in MAIN,'WordPress bootstrap identity')
check("'/library-continuity-contract'" in PHP and 'library_continuity_contract' in PHP and 'sc-workspace-library-continuity-v1' in PHP,'REST/enqueue integration')
check('data-release-stage="library-continuity"' in PHP and CUR.script_name in PHP and CUR.style_name in PHP,'current stage/assets')
check('sc-workspace-library-continuity/1.0' in LCPHP and 'sc-library-workspace-continuity/1.0' in LCPHP,'server contract schemas')
for token in ['saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation','canonicalLibraryRecordsMutated:false','automaticBackgroundSync:false','provenancePreserved:true']:check(token in LCJS,'continuity helper '+token)
for token in ['data-scw-library-continuity','Add to project','Open Knowledge Library','sc-library-workspace-continuity','library-continuity-promote']:check(token in (PHP+APP),'visible/runtime '+token)
check("PREVIOUS_RELEASE = '1.2.0'" in DEP and "ROLLBACK_RELEASE = '1.2.0'" in DEP and CUR.script_name in DEP,'deployment predecessor')
check("PREVIOUS_RELEASE = '1.2.0'" in PROD and "ROLLBACK_RELEASE = '1.2.0'" in PROD and CUR.script_name in PROD,'production predecessor')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v130'" in REGPHP and 'LEGACY_PENDING_KEY_V120' in REGPHP,'registry retry lineage')
for f in ['docs/RESEARCH_PROJECTS_LIBRARY_CONTINUITY_V130.md','RELEASE_NOTES_1.3.0.md','schemas/sc-workspace-library-continuity-record-v1.schema.json','schemas/sc-library-workspace-continuity-package-v1.schema.json','tests/test_library_continuity_contract.py','tests/test_library_continuity_runtime.js','tests/test_library_continuity_runtime.php']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_universal_workspace_search.py')],check=True,cwd=R)
print('PASS - v1.3.0 Research Projects & Library Continuity source gate')
