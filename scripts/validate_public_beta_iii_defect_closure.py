from pathlib import Path
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]
CUR=current_release(R); MAN=load_manifest(R,'0.79.0'); REG=load_registry(R,'0.79.0')
P=R/'wordpress/sustainable-catalyst-workspace'; PHP=(P/'includes/class-sc-workspace.php').read_text(); REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text(); CORE=(P/'assets/js/sc-workspace-public-beta-iii-defect-closure-v1.js').read_text(); APP=CUR.script_path.read_text(); CSS=CUR.style_path.read_text(); EXP=(P/'assets/js/sc-workspace-experience-v1.js').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - v0.79 defect closure gate: '+l)
check(validate_current_release_lineage(R)['ok'],'current release lineage')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.79.0','0.78.0','Public Beta III Defect Closure'),'historical lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema stability')
check(CUR.asset_handle in PHP and CUR.script_name in PHP and CUR.style_name in PHP,'current assets')
check("'/public-beta-iii-defect-closure-contract'" in PHP and 'public_beta_iii_defect_closure_contract' in PHP,'REST contract')
c=MAN['public_beta_iii_defect_closure']
for k in ['automated_defect_gate','manual_field_validation_outstanding','manual_field_items_are_not_silently_closed','current_release_consistency_required','wordpress_header_window_required','dependency_cycle_gate_required','security_privacy_gate_required','accessibility_performance_gate_required','beta_iii_topology_gate_required','recovery_disaster_gate_required','no_new_product_subsystem']: check(c[k] is True,k)
check(c['known_automated_blocker_count']==0 and len(c['closed_defect_classes'])==10,'closure blocker/class count')
check('data-scw-beta-closure' in PHP and 'Run closure gate' in PHP and 'Export closure report' in PHP,'closure UI')
check("'beta-closure'" in APP and "id:'beta-closure'" in EXP,'closure route recognition')
check('/* v0.79.0 — Public Beta III Defect Closure */' in CSS,'closure CSS layer')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.79.0','0.78.0','Public Beta III Defect Closure'),'historical registry')
check(REG.get('known_issue_count')==0,'historical known issue count')
for f in ['schemas/sc-workspace-public-beta-iii-defect-closure-v1.schema.json','schemas/sc-workspace-public-beta-iii-defect-closure-report-v1.schema.json','docs/PUBLIC_BETA_III_DEFECT_CLOSURE_V0790.md','RELEASE_NOTES_0.79.0.md','history/release-manifest-v0.78.0.json','history/workspace-product-record-v0.78.0.json']: check((R/f).exists(),f)
print(f'PASS - v0.79.0 Public Beta III Defect Closure source gate under current v{CUR.version}')
