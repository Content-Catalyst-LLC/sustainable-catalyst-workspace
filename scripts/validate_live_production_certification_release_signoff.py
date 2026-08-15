from pathlib import Path
import subprocess,sys
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]; CUR=current_release(R)
P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'0.83.0'); OLD=load_manifest(R,'0.82.1'); REG=load_registry(R,'0.83.0')
PHP=(P/'includes/class-sc-workspace.php').read_text(); MAIN=CUR.plugin_main.read_text(); SIGN=(P/'includes/class-sc-workspace-production-signoff.php').read_text(); RUN=(P/'assets/js/sc-workspace-production-signoff-v1.js').read_text(); UI=(P/'assets/js/sc-workspace-production-signoff-ui-v1.js').read_text(); NAV=(P/'assets/js/sc-workspace-research-navigation-v1.js').read_text(); APP=CUR.script_path.read_text(); CSS=CUR.style_path.read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v0.83.0 Live Production Certification & Release Sign-Off gate: '+l)
lineage=validate_current_release_lineage(R,'0.83.0','0.82.1')
check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.83.0','0.82.1','Live Production Certification & Release Sign-Off'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.83.0','0.82.1','Live Production Certification & Release Sign-Off'),'registry lineage')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:
    check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check(MAN['schema_migration_required'] is False,'no schema migration')
check('/wp-json/sc-workspace/v1/production-signoff-contract' in MAN['rest_routes'],'signoff REST route')
check(len(MAN['rest_routes'])==len(OLD['rest_routes'])+1,'only one release-control REST route added')
check('live_production_release_signoff' in MAN['capabilities'],'signoff capability')
s=MAN['production_release_signoff']
for k in ['release_candidate','feature_freeze','canonical_schema_freeze','live_field_evidence_required','human_attestation_required','public_page_smoke_required','rest_identity_required','anonymous_use_required','authenticated_use_required','cache_coherence_required','representative_project_preservation_required','rollback_rehearsal_required','reinstall_required','assistive_technology_required','zoom_reflow_touch_required','long_session_required','two_device_continuity_required','shared_review_handoff_required','institutional_handoff_required','explicit_reviewer_label','exportable_signoff_certificate','rollback_schema_compatible']:
    check(s.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_production_certification','automatic_signoff','automatic_cache_purge','automatic_rollback','automatic_project_migration','project_content_in_certificate','project_data_mutated','behavioral_telemetry']:
    check(s.get(k) is False,k)
check(s['rollback_release']=='0.82.1','rollback release')
check("PREVIOUS_RELEASE = '0.82.1'" in SIGN and "ROLLBACK_RELEASE = '0.82.1'" in SIGN,'signoff predecessor/rollback')
check('automatic_production_certification' in SIGN and "'automatic_signoff' => false" in SIGN,'no automatic signoff')
check("'/production-signoff-contract'" in PHP and 'production_signoff_contract' in PHP,'REST integration')
check('data-scw-production-signoff' in PHP and 'Complete production sign-off' in PHP and 'Export sign-off certificate' in PHP,'signoff UI shell')
check('sc-workspace-production-signoff-v1' in PHP and 'sc-workspace-production-signoff-ui-v1' in PHP,'signoff assets enqueued')
check("'production-signoff'" in NAV and "'production-signoff'" in APP,'navigation route')
for token in ["const RELEASE_VERSION='0.83.0'","const PREVIOUS_RELEASE='0.82.1'","const ROLLBACK_RELEASE='0.82.1'",'automaticCertification:false','projectContentIncluded:false','telemetry:false']:
    check(token in RUN,'runtime '+token)
for rid in ['public-page-smoke','rest-identity','anonymous-use','authenticated-use','cache-coherence','project-preservation','rollback-rehearsal','reinstall-current-release','assistive-technology','zoom-reflow-touch','long-session-large-project','two-device-continuity','shared-review-handoff','institutional-handoff']:
    check(rid in RUN,'required runtime check '+rid)
check('data-scw-signoff-complete' in UI and 'data-scw-signoff-export' in UI and 'Sign-off blocked' in UI,'signoff UI behavior')
check('/* v0.83.0 — Live Production Certification & Release Sign-Off */' in CSS,'signoff CSS layer')
for f in ['schemas/sc-workspace-production-signoff-v1.schema.json','schemas/sc-workspace-production-signoff-certificate-v1.schema.json','docs/LIVE_PRODUCTION_CERTIFICATION_RELEASE_SIGNOFF_V0830.md','RELEASE_NOTES_0.83.0.md']:
    check((R/f).exists(),f)
# v0.82.1 is now an inherited historical gate; it must not pin the current tree to v0.82.1.
inherited=(R/'scripts/validate_production_certification_installer_validation_lineage_repair.py').read_text()
check("validate_current_release_lineage(R,'0.82.1','0.82.0')" not in inherited,'v0.82.1 validator historical-safe')
subprocess.run([sys.executable,str(R/'scripts/validate_production_certification_installer_validation_lineage_repair.py')],check=True,cwd=R)
print('PASS - v0.83.0 Live Production Certification & Release Sign-Off source gate')
