from pathlib import Path
import subprocess,sys
from release_lineage import current_release,load_manifest,load_registry,validate_current_release_lineage
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.0.1');OLD=load_manifest(R,'1.0.0');REG=load_registry(R,'1.0.1');PHP=(P/'includes/class-sc-workspace.php').read_text();STAB=(P/'includes/class-sc-workspace-ga-stabilization.php').read_text();RUN=(P/'assets/js/sc-workspace-ga-stabilization-v1.js').read_text();APP=CUR.script_path.read_text();CSS=CUR.style_path.read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v1.0.1 GA Field Stabilization gate: '+l)
lineage=validate_current_release_lineage(R,'1.0.1','1.0.0');check(lineage['ok'],'current lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.0.1','1.0.0','GA Field Stabilization & Production Evidence Closure'),'release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'],REG['lifecycle_state'],REG['release_channel'])==('1.0.1','1.0.0','GA Field Stabilization & Production Evidence Closure','production','stable'),'registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types');check(MAN['schema_migration_required'] is False,'no schema migration')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/ga-stabilization-contract'},'only stabilization REST route added')
g=MAN['ga_field_stabilization']
for k in ['released_ga_certificate_required','field_evidence_required','production_browser_smoke_required','cache_coherence_required','installer_reinstall_required','accessibility_regression_required','cross_browser_device_smoke_required','recovery_rollback_review_required','no_known_blocking_defects_attestation_required','human_field_attestation_required','exportable_stabilization_report','local_evidence_record','rollback_schema_compatible']:check(g.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_release_certification','automatic_cache_purge','automatic_rollback','automatic_project_migration','project_content_in_report','project_data_inspected','project_data_mutated','behavioral_telemetry']:check(g.get(k) is False,k)
check(g['general_availability_release']=='1.0.0' and g['rollback_release']=='1.0.0','v1.0.0 predecessor/rollback')
check("GA_RELEASE = '1.0.0'" in STAB and "ROLLBACK_RELEASE = '1.0.0'" in STAB,'stabilization class predecessor')
check("const RELEASE_VERSION='1.0.1'" in RUN and "GA_RELEASE='1.0.0'" in RUN,'stabilization runtime identity')
check('projectContentIncluded:false' in RUN and 'rawUserAgentIncluded:false' in RUN and 'behavioralTelemetry:false' in RUN,'privacy boundary')
for rid in ['ga-certificate','production-browser-smoke','cache-coherence','installer-reinstall','accessibility-regression','cross-browser-device-smoke','recovery-rollback','no-known-blocking-defects']:check(rid in RUN,'required check '+rid)
check("'/ga-stabilization-contract'" in PHP and 'ga_stabilization_contract' in PHP,'REST integration')
check('data-scw-ga-stabilization' in PHP and 'Close field stabilization' in PHP and 'Export stabilization report' in PHP,'stabilization UI shell')
check('sc-workspace-ga-stabilization-v1' in PHP and 'sc-workspace-ga-stabilization-ui-v1' in PHP,'stabilization assets')
check("'ga-stabilization'" in APP,'stabilization navigation route');check('/* v1.0.1 — GA Field Stabilization & Production Evidence Closure */' in CSS,'stabilization CSS marker')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v101'" in REGPHP and "LEGACY_PENDING_KEY_V100" in REGPHP,'registry retry lineage')
for f in ['schemas/sc-workspace-ga-stabilization-v1.schema.json','schemas/sc-workspace-ga-stabilization-report-v1.schema.json','docs/GA_FIELD_STABILIZATION_PRODUCTION_EVIDENCE_CLOSURE_V101.md','RELEASE_NOTES_1.0.1.md']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_general_availability.py')],check=True,cwd=R)
print('PASS - v1.0.1 GA Field Stabilization & Production Evidence Closure source gate')
