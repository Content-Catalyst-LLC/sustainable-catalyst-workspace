import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.60.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.60.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.60.0.js').read_text()
HELPER=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.60.0.css').read_text()
SCHEMA=json.loads((ROOT/'schemas/sc-workspace-public-beta-readiness-v1.schema.json').read_text())
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class PublicBetaProductReadiness(unittest.TestCase):
 def test_release_lineage(self):
  self.assertEqual(MAN['version'],'0.60.0'); self.assertEqual(MAN['previous_version'],'0.59.1'); self.assertEqual(MAN['release_name'],'Public Product Beta II')
 def test_schema_stable(self):
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required']); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged'])
 def test_manifest_public_beta_contract(self):
  self.assertEqual(MAN['public_beta_schema'],'sc-workspace-public-beta-readiness/1.0'); self.assertEqual(MAN['public_beta_rest_endpoint'],'/wp-json/sc-workspace/v1/public-beta-contract'); self.assertEqual(MAN['public_beta']['release_stage'],'public-beta')
 def test_quick_starts(self):
  self.assertEqual(MAN['public_beta']['quick_starts'],['research-investigation','analytical-assessment','decision-case','publication-preparation']); self.assertIn("const QUICK_STARTS",HELPER)
 def test_guest_first_boundary(self):
  self.assertTrue(MAN['anonymous_access']); self.assertFalse(MAN['account_required']); self.assertTrue(MAN['public_beta']['guest_workspace_supported']); self.assertFalse(MAN['public_beta']['login_wall'])
 def test_no_automatic_boundary_expansion(self):
  self.assertFalse(MAN['public_beta']['automatic_cloud_upload']); self.assertFalse(MAN['public_beta']['background_sync']); self.assertFalse(MAN['public_beta']['automatic_telemetry']); self.assertFalse(MAN['public_beta']['hidden_readiness_score']); self.assertFalse(MAN['public_beta']['automatic_lifecycle_advance'])
 def test_start_view_is_default(self):
  self.assertIn("let workspaceView = 'start'",JS); self.assertIn('data-scw-workspace-section="start"',PHP); self.assertIn('Begin with the work, not the software.',PHP)
 def test_start_actions(self):
  self.assertIn('data-scw-beta-new',PHP); self.assertIn('data-scw-beta-continue',PHP); self.assertIn('/knowledge-libraries/',PHP); self.assertIn('startBetaGuidedProject',JS)
 def test_runtime_capability_surface(self):
  for marker in ['data-scw-beta-cap-storage','data-scw-beta-cap-crypto','data-scw-beta-cap-files','data-scw-beta-cap-return']: self.assertIn(marker,PHP)
  for key in ['localStorage','sessionStorage','webCryptoSha256','fileApi','postMessage']: self.assertIn(key,HELPER)
 def test_keyboard_workspace_navigation(self):
  self.assertIn("['ArrowLeft','ArrowRight','Home','End']",JS); self.assertIn("setAttribute('aria-current', 'page')",JS)
 def test_accessibility_styles(self):
  self.assertIn(':focus-visible',CSS); self.assertIn('prefers-reduced-motion:reduce',CSS); self.assertIn('forced-colors:active',CSS)
 def test_helper_governance_has_no_scores(self):
  self.assertIn('hiddenScore: false',HELPER); self.assertIn('automaticProjectCreation: false',HELPER); self.assertIn('automaticTelemetry: false',HELPER)
 def test_schema_contract(self):
  self.assertEqual(SCHEMA['properties']['schema']['const'],'sc-workspace-public-beta-readiness/1.0'); self.assertFalse(SCHEMA['properties']['governance']['properties']['hiddenScore']['const'])
 def test_registry_lineage(self):
  self.assertEqual(REG['public_version'],'0.60.0'); self.assertEqual(REG['previous_version'],'0.59.1'); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0600'",REGPHP); self.assertIn("LEGACY_PENDING_KEY_V0290",REGPHP)
 def test_plugin_and_rest_contract(self):
  self.assertIn('Version: 0.60.0',MAIN); self.assertIn("'/public-beta-contract'",PHP); self.assertIn('public function public_beta_contract()',PHP); self.assertIn("'release_stage' => 'public-beta'",PHP)
if __name__=='__main__': unittest.main()
