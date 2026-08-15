import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-security-privacy-ui-v1.js').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class SecurityPrivacyPortabilityContract(unittest.TestCase):
 def test_01_release_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 1.5.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['security_privacy']['schema_migration'])
 def test_03_schemas_exist(self):
  for name in ['sc-workspace-security-privacy-audit-v1.schema.json','sc-workspace-threat-model-v1.schema.json','sc-workspace-data-portability-bundle-v1.schema.json','sc-workspace-deletion-receipt-v1.schema.json']:
   self.assertTrue((ROOT/'schemas'/name).exists()); json.loads((ROOT/'schemas'/name).read_text())
 def test_04_inventory_and_unknown_detection(self): self.assertIn('function inventory',JS); self.assertIn('startsWith(PREFIX)',JS); self.assertIn('unclassified-private',JS); self.assertTrue(MAN['security_privacy']['unknown_workspace_key_detection'])
 def test_05_threat_model_nonclaims(self): self.assertIn('localStorageEncryption:false',JS); self.assertIn('fingerprintIsAuthentication:false',JS); self.assertFalse(MAN['security_privacy']['application_level_localstorage_encryption']); self.assertFalse(MAN['security_privacy']['fingerprint_is_encryption']); self.assertFalse(MAN['security_privacy']['durable_reference_is_authorization'])
 def test_06_portability(self): self.assertIn('buildPortabilityBundle',JS); self.assertIn("PREFIX='sc_workspace'",JS); self.assertTrue(MAN['security_privacy']['complete_browser_local_portability']); self.assertIn('serverAccountDataIncluded:false',JS)
 def test_07_verified_local_deletion(self): self.assertIn("CONFIRM_PHRASE='DELETE WORKSPACE DATA'",JS); self.assertIn('function executeDeletion',JS); self.assertIn('unrelatedLocalStorageTouched:false',JS); self.assertTrue(MAN['security_privacy']['verified_browser_local_deletion']); self.assertTrue(MAN['security_privacy']['server_account_deletion_separate'])
 def test_08_no_automatic_security_mutation(self): self.assertFalse(MAN['security_privacy']['automatic_deletion']); self.assertFalse(MAN['security_privacy']['automatic_upload']); self.assertFalse(MAN['security_privacy']['automatic_disclosure']); self.assertFalse(MAN['security_privacy']['canonical_mutation'])
 def test_09_review_surface(self): self.assertIn('data-scw-workspace-view="security"',PHP); self.assertIn('data-scw-security-privacy',PHP); self.assertIn('Export complete local bundle',PHP); self.assertIn('DELETE WORKSPACE DATA',PHP); self.assertIn("'security'",NAV)
 def test_10_runtime_navigation(self): self.assertIn('securityPrivacySection',APP); self.assertIn("workspaceView !== 'security'",APP); self.assertIn('sc-workspace-security-privacy-ui-v1.js',PHP)
 def test_11_rest_contract(self): self.assertIn('/wp-json/sc-workspace/v1/security-privacy-contract',MAN['rest_routes']); self.assertIn("'/security-privacy-contract'",PHP); self.assertIn('public function security_privacy_contract()',PHP)
 def test_12_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v150'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0580',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.58.0.json').exists())
 def test_13_editorial_and_ui_boundary(self): self.assertIn('.scw-security-privacy{border-top:4px solid #000',CSS); self.assertIn('account/cloud backups',PHP.lower()); self.assertIn('Nothing was imported',UI); self.assertIn('serverBackupsKnown:true',UI)
if __name__=='__main__': unittest.main()
