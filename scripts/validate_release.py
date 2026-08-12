from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.78.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.78.0.json').read_text())
MP=R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-v1.js').read_text(); UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-ui-v1.js').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.78.0.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.78.0.css').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - '+l)
check('Version: 0.78.0' in MAIN and "SC_WORKSPACE_VERSION', '0.78.0" in MAIN,'version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.78.0','0.77.0','Accessibility & Performance Final Audit'),'lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.78.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M);check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact header')
check("'sc-workspace-v0780'" in PHP and 'workspace-v0.78.0.js' in PHP and 'workspace-v0.78.0.css' in PHP,'assets')
check("wp_localize_script('sc-workspace-v0780'" in PHP,'localization')
check("'/accessibility-performance-final-audit-contract'" in PHP and 'accessibility_performance_final_audit_contract' in PHP,'REST')
check('/wp-json/sc-workspace/v1/accessibility-performance-final-audit-contract' in MAN['rest_routes'],'manifest REST')
a=MAN['accessibility_performance_final_audit']
for k in ['critical_automated_release_gate','manual_field_audit_required','existing_accessibility_engine_reused','existing_long_session_monitor_reused','privacy_minimized_report']: check(a[k] is True,k)
for k in ['automated_accessibility_certification','automated_performance_certification','hidden_score','automatic_repair','automatic_optimization','automatic_deletion','automatic_upload','telemetry','canonical_mutation','schema_migration_required']: check(a[k] is False,k)
check('data-scw-final-audit' in PHP and 'Run final audit' in PHP and 'Export final field-QA checklist' in PHP,'UI')
check('/* v0.78.0 — Accessibility & Performance Final Audit */' in CSS,'CSS')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0780'" in REGPHP and 'LEGACY_PENDING_KEY_V0770' in REGPHP,'registry')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.78.0','0.77.0','Accessibility & Performance Final Audit'),'registry record')
for f in ['schemas/sc-workspace-accessibility-performance-final-audit-v1.schema.json','schemas/sc-workspace-accessibility-performance-final-audit-report-v1.schema.json','schemas/sc-workspace-accessibility-performance-final-checklist-v1.schema.json','docs/ACCESSIBILITY_PERFORMANCE_FINAL_AUDIT_V0780.md','RELEASE_NOTES_0.78.0.md','history/release-manifest-v0.77.0.json','history/workspace-product-record-v0.77.0.json']: check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_security_privacy_audit_ii.py')],check=True,cwd=R)
subprocess.run([sys.executable,str(R/'scripts/validate_accessibility_performance_final_audit.py')],check=True,cwd=R)
print('PASS - v0.78.0 release validator')
