from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.79.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.79.0.json').read_text())
MP=R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-defect-closure-v1.js').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.79.0.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.79.0.css').read_text(); EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v0.79 defect closure gate: '+l)
check('Version: 0.79.0' in MAIN and "SC_WORKSPACE_VERSION', '0.79.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.79.0','0.78.0','Public Beta III Defect Closure'),'lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema stability')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.79.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M);check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact header')
check("'sc-workspace-v0790'" in PHP and 'workspace-v0.79.0.js' in PHP and 'workspace-v0.79.0.css' in PHP,'current assets')
check('sc-workspace-v0780' not in PHP and 'workspace-v0.78.0.js' not in PHP and 'workspace-v0.78.0.css' not in PHP,'no stale current asset handles')
check("wp_localize_script('sc-workspace-v0790'" in PHP,'current localization handle')
check("'/public-beta-iii-defect-closure-contract'" in PHP and 'public_beta_iii_defect_closure_contract' in PHP,'REST contract')
check('/wp-json/sc-workspace/v1/public-beta-iii-defect-closure-contract' in MAN['rest_routes'],'manifest REST')
c=MAN['public_beta_iii_defect_closure']
for k in ['automated_defect_gate','manual_field_validation_outstanding','manual_field_items_are_not_silently_closed','current_release_consistency_required','wordpress_header_window_required','dependency_cycle_gate_required','security_privacy_gate_required','accessibility_performance_gate_required','beta_iii_topology_gate_required','recovery_disaster_gate_required','no_new_product_subsystem']: check(c[k] is True,k)
check(c['known_automated_blocker_count']==0,'zero automated blockers at release')
check(len(c['closed_defect_classes'])==10,'closed defect class count')
check('data-scw-beta-closure' in PHP and 'Run closure gate' in PHP and 'Export closure report' in PHP,'closure UI')
check("'beta-closure'" in APP and "id:'beta-closure'" in EXP,'closure route recognition')
check('/* v0.79.0 — Public Beta III Defect Closure */' in CSS,'closure CSS layer')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0790'" in REGPHP and 'LEGACY_PENDING_KEY_V0780' in REGPHP,'registry keys')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.79.0','0.78.0','Public Beta III Defect Closure'),'registry record')
README=(R/'README.md').read_text(); check('# Sustainable Catalyst Workspace v0.79.0' in README and 'Public Beta III Defect Closure' in README,'current README identity')
check(REG.get('known_issue_count')==0,'registry known issue count')
for f in ['schemas/sc-workspace-public-beta-iii-defect-closure-v1.schema.json','schemas/sc-workspace-public-beta-iii-defect-closure-report-v1.schema.json','docs/PUBLIC_BETA_III_DEFECT_CLOSURE_V0790.md','RELEASE_NOTES_0.79.0.md','history/release-manifest-v0.78.0.json','history/workspace-product-record-v0.78.0.json']: check((R/f).exists(),f)
# Existing release-candidate blockers remain mandatory.
subprocess.run([sys.executable,str(R/'scripts/validate_security_privacy_audit_ii.py')],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'scripts/validate_accessibility_performance_final_audit.py')],check=True,cwd=R)
print('PASS - v0.79.0 Public Beta III Defect Closure source gate')
