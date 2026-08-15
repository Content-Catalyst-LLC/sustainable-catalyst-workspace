from pathlib import Path
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]; CUR=current_release(R)
MAN=load_manifest(R,'0.80.0'); OLD=load_manifest(R,'0.79.0'); REG=load_registry(R,'0.80.0')
P=R/'wordpress/sustainable-catalyst-workspace'; PHP=(P/'includes/class-sc-workspace.php').read_text(); CORE=(P/'assets/js/sc-workspace-release-candidate-i-v1.js').read_text(); APP=CUR.script_path.read_text(); CSS=CUR.style_path.read_text(); EXP=(P/'assets/js/sc-workspace-experience-v1.js').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v0.80 Release Candidate I gate: '+l)
check(validate_current_release_lineage(R)['ok'],'current release lineage')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.80.0','0.79.0','Workspace Release Candidate I'),'historical lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema freeze')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']: check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check('/wp-json/sc-workspace/v1/release-candidate-contract' in MAN['rest_routes'],'manifest REST')
r=MAN['release_candidate_i']
for k in ['release_candidate','feature_freeze','canonical_schema_freeze','public_beta_iii_closure_required','security_privacy_gate_required','accessibility_performance_gate_required','recovery_disaster_gate_required','wordpress_header_window_required','dependency_cycle_gate_required','package_integrity_required','rollback_artifact_required','manual_field_validation_outstanding']: check(r[k] is True,k)
check(r['known_automated_blocker_count']==0 and r['new_product_subsystem'] is False and r['automatic_promotion_to_stable'] is False,'RC governance')
check(CUR.asset_handle in PHP and CUR.script_name in PHP and CUR.style_name in PHP,'current assets')
check("'/release-candidate-contract'" in PHP and 'release_candidate_contract' in PHP,'REST contract')
check('data-scw-release-candidate' in PHP and 'Run RC gate' in PHP and 'Export field checklist' in PHP,'RC UI')
check("'release-candidate'" in APP and "id:'release-candidate'" in EXP,'RC route recognition')
check('/* v0.80.0 — Workspace Release Candidate I */' in CSS,'RC CSS layer')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.80.0','0.79.0','Workspace Release Candidate I'),'historical registry')
for f in ['schemas/sc-workspace-release-candidate-v1.schema.json','schemas/sc-workspace-release-candidate-report-v1.schema.json','schemas/sc-workspace-release-candidate-checklist-v1.schema.json','docs/WORKSPACE_RELEASE_CANDIDATE_I_V0800.md','RELEASE_NOTES_0.80.0.md']: check((R/f).exists(),f)
print(f'PASS - v0.80.0 Workspace Release Candidate I source gate under current v{CUR.version}')
