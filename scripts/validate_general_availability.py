from pathlib import Path
import subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.0.0');OLD=load_manifest(R,'0.84.0');REG=load_registry(R,'1.0.0');PHP=(P/'includes/class-sc-workspace.php').read_text();GA=(P/'includes/class-sc-workspace-general-availability.php').read_text();RUN=(P/'assets/js/sc-workspace-general-availability-v1.js').read_text();UI=(P/'assets/js/sc-workspace-general-availability-ui-v1.js').read_text();APP=CUR.script_path.read_text();CSS=CUR.style_path.read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v1.0.0 General Availability gate: '+l)
lineage=validate_current_release_lineage(R,'1.0.0','0.84.0');check(lineage['ok'],'current lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.0.0','0.84.0','General Availability'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'],REG['lifecycle_state'],REG['release_channel'])==('1.0.0','0.84.0','General Availability','production','stable'),'registry GA identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types');check(MAN['schema_migration_required'] is False,'no schema migration')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/general-availability-contract'},'only GA REST route added')
g=MAN['general_availability']
for k in ['general_availability','stable_release','feature_freeze','canonical_schema_freeze','valid_readiness_dossier_required','rollback_schema_compatible','package_integrity_required','live_wordpress_smoke_required','support_recovery_review_required','public_version_semantics_review_required','no_known_blocking_defects_attestation_required','human_release_attestation_required','exportable_ga_certificate']:check(g.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_release_certification','automatic_rollback','automatic_cache_purge','automatic_project_migration','project_content_in_certificate','project_data_mutated','behavioral_telemetry']:check(g.get(k) is False,k)
check(g['readiness_release']=='0.84.0' and g['rollback_release']=='0.84.0','v0.84 readiness/rollback')
check("READINESS_RELEASE = '0.84.0'" in GA and "ROLLBACK_RELEASE = '0.84.0'" in GA,'GA class predecessor')
check("const RELEASE_VERSION='1.0.0'" in RUN and "READINESS_RELEASE='0.84.0'" in RUN,'GA runtime identity')
check('automaticReleaseCertification:false' in RUN and 'projectContentIncluded:false' in RUN and 'telemetry:false' in RUN,'no-auto boundary')
for rid in ['readiness-dossier','release-identity','package-integrity','rollback-artifact','live-wordpress-smoke','support-recovery','public-version-semantics','no-known-blocking-defects']:check(rid in RUN,'required check '+rid)
check("'/general-availability-contract'" in PHP and 'general_availability_contract' in PHP,'REST integration')
check('data-scw-general-availability' in PHP and 'Record General Availability' in PHP and 'Export GA certificate' in PHP,'GA UI shell')
check('sc-workspace-general-availability-v1' in PHP and 'sc-workspace-general-availability-ui-v1' in PHP,'GA assets')
check("'general-availability'" in APP,'GA navigation route');check('/* v1.0.0 — General Availability */' in CSS,'GA CSS marker')
for f in ['schemas/sc-workspace-general-availability-v1.schema.json','schemas/sc-workspace-general-availability-certificate-v1.schema.json','docs/GENERAL_AVAILABILITY_V100.md','RELEASE_NOTES_1.0.0.md']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_production_signoff_closure_ga_readiness.py')],check=True,cwd=R)
print('PASS - v1.0.0 General Availability source gate')
