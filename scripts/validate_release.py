from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.77.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.77.0.json').read_text())
MP=R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MP.read_bytes(); MAIN=MP.read_text(); HEAD=RAW[:8192].decode(errors='replace')
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); A=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-audit-ii-v1.js').read_text(); UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-audit-ii-ui-v1.js').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.77.0.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.77.0.css').read_text()
def check(x,l):
 if not x: raise SystemExit('FAIL - '+l)
check('Version: 0.77.0' in MAIN and "SC_WORKSPACE_VERSION', '0.77.0" in MAIN,'version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.77.0','0.76.0','Security & Privacy Audit II'),'lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'schema')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.77.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M);check(bool(m) and m.group(1).strip()==expected,'8KB '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512,'compact header')
check("'sc-workspace-v0770'" in PHP and 'workspace-v0.77.0.js' in PHP and 'workspace-v0.77.0.css' in PHP,'assets')
check("wp_localize_script('sc-workspace-v0770'" in PHP,'localization')
check("'/security-privacy-audit-ii-contract'" in PHP and 'security_privacy_audit_ii_contract' in PHP,'REST')
check('/wp-json/sc-workspace/v1/security-privacy-audit-ii-contract' in MAN['rest_routes'],'manifest REST')
a=MAN['security_privacy_audit_ii']
for k in ['runtime_metadata_only','localstorage_metadata_only','sessionstorage_metadata_only','accessible_cookie_count_only','rest_permission_split_audited','dynamic_code_primitives_blocked','secret_literal_scan','external_network_literal_scan','wordpress_header_window_gate','enqueue_dependency_cycle_gate','public_rest_routes_metadata_only_get','authenticated_cloud_routes_require_nonce_header','authenticated_cloud_routes_same_origin_credentials']: check(a[k] is True,k)
for k in ['storage_values_exported','storage_key_names_exported','cookie_names_exported','cookie_values_exported','project_content_exported','source_urls_exported','query_text_exported','account_identity_exported','device_identity_exported','source_audit_is_penetration_test','application_level_localstorage_encryption','automatic_remediation','automatic_deletion','automatic_upload','automatic_disclosure','telemetry','canonical_mutation','schema_migration_required']: check(a[k] is False,k)
for tok in ['storageValues:true','storageKeyNames:true','cookieNames:true','cookieValues:true','projectContent:true','accountIdentity:true','deviceIdentity:true']: check(tok in A,'audit exclusion '+tok)
check('data-scw-security-audit-ii' in PHP and 'Run Audit II' in PHP and 'Export privacy-minimized report' in PHP,'UI')
check('/* v0.77.0 — Security & Privacy Audit II */' in CSS,'CSS')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0770'" in REGPHP and 'LEGACY_PENDING_KEY_V0760' in REGPHP,'registry')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.77.0','0.76.0','Security & Privacy Audit II'),'registry record')
for f in ['schemas/sc-workspace-security-privacy-audit-ii-v1.schema.json','schemas/sc-workspace-security-privacy-audit-ii-report-v1.schema.json','schemas/sc-workspace-security-privacy-audit-ii-policy-v1.schema.json','docs/SECURITY_PRIVACY_AUDIT_II_V0770.md','RELEASE_NOTES_0.77.0.md','history/release-manifest-v0.76.0.json','history/workspace-product-record-v0.76.0.json']: check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_security_privacy_audit_ii.py')],check=True,cwd=R)
print('PASS - v0.77.0 release validator')
