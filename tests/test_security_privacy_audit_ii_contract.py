import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.77.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.77.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-audit-ii-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-audit-ii-ui-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.3.css').read_text()
class SecurityPrivacyAuditIIContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.77.0','0.76.0','Security & Privacy Audit II')); self.assertIn('Version: 2.0.3',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_03_schemas(self):
  for f in ['sc-workspace-security-privacy-audit-ii-v1.schema.json','sc-workspace-security-privacy-audit-ii-report-v1.schema.json','sc-workspace-security-privacy-audit-ii-policy-v1.schema.json']:
   self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
 def test_04_rest_contract(self): self.assertIn("'/security-privacy-audit-ii-contract'",PHP); self.assertIn('security_privacy_audit_ii_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/security-privacy-audit-ii-contract',MAN['rest_routes'])
 def test_05_runtime_privacy_minimized(self):
  for tok in ['storageValues:true','storageKeyNames:true','cookieNames:true','cookieValues:true','accountIdentity:true','deviceIdentity:true','userAgent:true','referrer:true']: self.assertIn(tok,JS)
  self.assertIn('storageKeyNames:true',JS); self.assertIn('cookieNames:true',JS); self.assertIn('projectContent:true',JS)
 def test_06_runtime_surfaces(self): self.assertIn("summarize(localStorage,'localStorage')",JS); self.assertIn("summarize(sessionStorage,'sessionStorage')",JS); self.assertIn('accessibleWorkspaceCookieCount',JS); self.assertIn('secureContext',JS); self.assertIn('embedded',JS)
 def test_07_source_gates(self):
  a=MAN['security_privacy_audit_ii']; self.assertTrue(a['rest_permission_split_audited']); self.assertTrue(a['dynamic_code_primitives_blocked']); self.assertTrue(a['secret_literal_scan']); self.assertTrue(a['external_network_literal_scan']); self.assertTrue(a['wordpress_header_window_gate']); self.assertTrue(a['enqueue_dependency_cycle_gate'])
 def test_08_nonclaims_and_governance(self):
  a=MAN['security_privacy_audit_ii']; self.assertFalse(a['source_audit_is_penetration_test']); self.assertFalse(a['application_level_localstorage_encryption']); self.assertFalse(a['automatic_remediation']); self.assertFalse(a['automatic_deletion']); self.assertFalse(a['automatic_upload']); self.assertFalse(a['automatic_disclosure']); self.assertFalse(a['telemetry']); self.assertFalse(a['canonical_mutation'])
 def test_09_ui(self): self.assertIn('data-scw-security-audit-ii',PHP); self.assertIn('Run Audit II',PHP); self.assertIn('Export privacy-minimized report',PHP); self.assertIn('Audit, not certification',PHP); self.assertIn('data-scw-sec2-gates',PHP); self.assertIn('workspace-security-privacy-audit-ii-',UI)
 def test_10_assets(self): self.assertIn("'sc-workspace-v203'",PHP); self.assertIn('workspace-v2.0.3.js',PHP); self.assertIn('workspace-v2.0.3.css',PHP); self.assertIn('sc-workspace-security-privacy-audit-ii-v1',PHP); self.assertIn('sc-workspace-security-privacy-audit-ii-ui-v1',PHP); self.assertIn('/* v0.77.0 — Security & Privacy Audit II */',CSS)
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.77.0','0.76.0','Security & Privacy Audit II')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v203'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0760',REGPHP); self.assertTrue((R/'history/release-manifest-v0.76.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.76.0.json').exists())
 def test_12_stale_security_export_version_fixed(self): self.assertIn("workspaceVersion:root.dataset.version||''",(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-ui-v1.js').read_text())
 def test_13_artifacts(self): self.assertTrue((R/'docs/SECURITY_PRIVACY_AUDIT_II_V0770.md').exists()); self.assertTrue((R/'RELEASE_NOTES_0.77.0.md').exists())
if __name__=='__main__': unittest.main()
