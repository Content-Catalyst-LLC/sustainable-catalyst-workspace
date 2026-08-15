from pathlib import Path
import subprocess,sys
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]; CUR=current_release(R)
P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'0.84.0'); OLD=load_manifest(R,'0.83.0'); REG=load_registry(R,'0.84.0')
PHP=(P/'includes/class-sc-workspace.php').read_text(); MAIN=CUR.plugin_main.read_text(); GA=(P/'includes/class-sc-workspace-ga-readiness.php').read_text(); RUN=(P/'assets/js/sc-workspace-ga-readiness-v1.js').read_text(); UI=(P/'assets/js/sc-workspace-ga-readiness-ui-v1.js').read_text(); SIGN=(P/'includes/class-sc-workspace-production-signoff.php').read_text(); NAV=(P/'assets/js/sc-workspace-research-navigation-v1.js').read_text(); APP=CUR.script_path.read_text(); CSS=CUR.style_path.read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v0.84.0 Production Sign-Off Closure & 1.0 Release Readiness gate: '+l)
lineage=validate_current_release_lineage(R,'0.84.0','0.83.0')
check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.84.0','0.83.0','Production Sign-Off Closure & 1.0 Release Readiness'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.84.0','0.83.0','Production Sign-Off Closure & 1.0 Release Readiness'),'registry lineage')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:
    check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check(MAN['schema_migration_required'] is False,'no schema migration')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/ga-readiness-contract'},'only GA readiness REST route added')
check('ga_release_readiness_dossier' in MAN['capabilities'],'GA readiness capability')
g=MAN['production_ga_readiness']
for k in ['release_candidate','feature_freeze','canonical_schema_freeze','signed_production_certificate_required','release_lineage_required','package_integrity_required','current_wordpress_smoke_required','rollback_artifact_required','release_notes_review_required','support_recovery_review_required','no_known_blocking_defects_attestation_required','human_readiness_attestation_required','exportable_readiness_dossier','rollback_schema_compatible']:
    check(g.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_promotion_to_1_0','automatic_production_certification','automatic_rollback','automatic_cache_purge','automatic_project_migration','project_content_in_dossier','project_data_mutated','behavioral_telemetry']:
    check(g.get(k) is False,k)
check(g['production_signoff_release']=='0.83.0','production signoff predecessor')
check(g['rollback_release']=='0.83.0','rollback release')
check("PRODUCTION_SIGNOFF_RELEASE = '0.83.0'" in GA and "ROLLBACK_RELEASE = '0.83.0'" in GA,'GA predecessor/rollback')
check("const RELEASE_VERSION='0.84.0'" in RUN and "const PRODUCTION_SIGNOFF_RELEASE='0.83.0'" in RUN,'GA runtime identity')
check('automaticPromotionToOneDotZero:false' in RUN and 'projectContentIncluded:false' in RUN and 'telemetry:false' in RUN,'GA no-auto-promotion boundary')
for rid in ['production-signoff-certificate','current-release-identity','release-lineage','package-integrity','rollback-artifact','current-wordpress-smoke','release-notes-review','support-recovery-review','no-known-blocking-defects']:
    check(rid in RUN,'required readiness check '+rid)
check("'/ga-readiness-contract'" in PHP and 'ga_readiness_contract' in PHP,'REST integration')
check('data-scw-ga-readiness' in PHP and 'Record 1.0 readiness decision' in PHP and 'Export readiness dossier' in PHP,'readiness UI shell')
check('sc-workspace-ga-readiness-v1' in PHP and 'sc-workspace-ga-readiness-ui-v1' in PHP,'readiness assets enqueued')
check("'ga-readiness'" in NAV and "'ga-readiness'" in APP,'navigation route')
check('Readiness remains on HOLD' in UI and 'does not publish or promote v1.0.0 automatically' in UI,'readiness UI behavior')
check('/* v0.84.0 — Production Sign-Off Closure & 1.0 Release Readiness */' in CSS,'readiness CSS layer')
check("const SIGNOFF_RELEASE = '0.83.0'" in SIGN and "'historical_release_evidence' => true" in SIGN,'v0.83 signoff evidence preserved')
for f in ['schemas/sc-workspace-ga-readiness-v1.schema.json','schemas/sc-workspace-ga-readiness-dossier-v1.schema.json','docs/PRODUCTION_SIGNOFF_CLOSURE_1_0_RELEASE_READINESS_V0840.md','RELEASE_NOTES_0.84.0.md']:
    check((R/f).exists(),f)
# v0.83 source gate must remain historical-safe and callable under the v0.84 current tree.
subprocess.run([sys.executable,str(R/'scripts/validate_live_production_certification_release_signoff.py')],check=True,cwd=R)
print('PASS - v0.84.0 Production Sign-Off Closure & 1.0 Release Readiness source gate')
