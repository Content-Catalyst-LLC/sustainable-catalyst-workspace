from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.80.0.json').read_text()); OLD=json.loads((R/'history/release-manifest-v0.79.0.json').read_text()); REG=json.loads((R/'registry/workspace-product-record-v0.80.0.json').read_text())
MP=R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-release-candidate-i-v1.js').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.81.0.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.81.0.css').read_text(); EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - v0.80 Release Candidate I gate: '+l)
check('Version: 0.81.0' in MAIN and "SC_WORKSPACE_VERSION', '0.81.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.80.0','0.79.0','Workspace Release Candidate I'),'lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema freeze')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']: check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/release-candidate-contract'},'no unplanned new REST surface')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.81.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M);check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact WordPress header')
check("'sc-workspace-v0810'" in PHP and 'workspace-v0.81.0.js' in PHP and 'workspace-v0.81.0.css' in PHP,'current assets')
check('sc-workspace-v0790' not in PHP and 'workspace-v0.79.0.js' not in PHP and 'workspace-v0.79.0.css' not in PHP,'no stale current asset handles')
check("wp_localize_script('sc-workspace-v0810'" in PHP,'current localization handle')
check("'/release-candidate-contract'" in PHP and 'release_candidate_contract' in PHP,'REST contract')
check('/wp-json/sc-workspace/v1/release-candidate-contract' in MAN['rest_routes'],'manifest REST')
r=MAN['release_candidate_i']
for k in ['release_candidate','feature_freeze','canonical_schema_freeze','public_beta_iii_closure_required','security_privacy_gate_required','accessibility_performance_gate_required','recovery_disaster_gate_required','wordpress_header_window_required','dependency_cycle_gate_required','package_integrity_required','rollback_artifact_required','manual_field_validation_outstanding']: check(r[k] is True,k)
check(r['known_automated_blocker_count']==0,'zero automated blockers'); check(r['new_product_subsystem'] is False,'no new product subsystem'); check(r['automatic_promotion_to_stable'] is False,'no automatic stable promotion')
check('data-scw-release-candidate' in PHP and 'Run RC gate' in PHP and 'Export field checklist' in PHP,'RC UI')
check("'release-candidate'" in APP and "id:'release-candidate'" in EXP,'RC route recognition')
check('/* v0.80.0 — Workspace Release Candidate I */' in CSS,'RC CSS layer')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0810'" in REGPHP and 'LEGACY_PENDING_KEY_V0790' in REGPHP,'registry keys')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.80.0','0.79.0','Workspace Release Candidate I'),'registry record')
check(REG.get('known_issue_count')==0,'registry known issue count')
for f in ['schemas/sc-workspace-release-candidate-v1.schema.json','schemas/sc-workspace-release-candidate-report-v1.schema.json','schemas/sc-workspace-release-candidate-checklist-v1.schema.json','docs/WORKSPACE_RELEASE_CANDIDATE_I_V0800.md','RELEASE_NOTES_0.80.0.md','history/release-manifest-v0.79.0.json','history/workspace-product-record-v0.79.0.json']: check((R/f).exists(),f)
# The candidate cannot pass unless the inherited beta/security/final-audit gates still pass under the current runtime.
subprocess.run([sys.executable,str(R/'scripts/validate_public_beta_iii_defect_closure.py')],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'scripts/validate_security_privacy_audit_ii.py')],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'scripts/validate_accessibility_performance_final_audit.py')],check=True,cwd=R)
print('PASS - v0.80.0 Workspace Release Candidate I source gate')
