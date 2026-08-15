import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.7.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.6.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.7.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
class CrossDeviceProduction(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.7.0','1.6.0','Cross-Device Continuity & Account Sync Productionization'))
 def test_02_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.7.0','1.6.0'));self.assertIn('LEGACY_PENDING_KEY_V170',REGPHP);self.assertIn('LEGACY_PENDING_KEY_V160',REGPHP)
 def test_03_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_04_only_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/cross-device-production-contract'});self.assertIn("'/cross-device-production-contract'",PHP)
 def test_05_actions(self): self.assertEqual(MAN['cross_device_production']['plan_actions'],['local-only','enroll','push','pull-safe','open-remote-copy','recreate-cloud','noop','conflict'])
 def test_06_boundaries(self):
  g=MAN['cross_device_production'];self.assertTrue(g['guest_workspace_first_class']);self.assertTrue(g['explicit_project_enrollment']);self.assertTrue(g['revision_precondition_required']);self.assertTrue(g['conflict_preserves_both_sides']);self.assertFalse(g['background_sync']);self.assertFalse(g['automatic_upload']);self.assertFalse(g['device_fingerprinting']);self.assertFalse(g['behavioral_telemetry'])
 def test_07_receipt_privacy(self):
  g=MAN['cross_device_production'];self.assertTrue(g['production_receipt_export']);self.assertFalse(g['receipt_contains_project_content']);self.assertFalse(g['receipt_contains_query_text']);self.assertFalse(g['receipt_contains_source_urls']);self.assertFalse(g['receipt_contains_device_identifier'])
 def test_08_ui(self): self.assertIn('Production continuity plan',PHP);self.assertIn('Export continuity receipt',PHP);self.assertIn('Local-first continuity, not cloud-first storage',PHP)
 def test_09_runtime(self): self.assertIn('data-release-stage="research-operations"',PHP);self.assertIn('workspace-v1.10.0.js',PHP);self.assertIn('sc-workspace-cross-device-production-v1',PHP)
 def test_10_deployment(self): self.assertIn("PREVIOUS_RELEASE = '1.9.0'",DEP);self.assertIn("ROLLBACK_RELEASE = '1.9.0'",DEP);self.assertIn('class-sc-workspace-cross-device-production.php',DEP)
 def test_11_identity(self): self.assertIn('Version: 1.10.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '1.10.0'",MAIN)
if __name__=='__main__':unittest.main()
