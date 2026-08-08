from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
PLATFORM=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php').read_text()
REG=json.loads((ROOT/'registry/workspace-product-record-v0.6.1.json').read_text())
MAN=json.loads((ROOT/'release-manifest-v0.6.1.json').read_text())
class PlatformConversionTests(unittest.TestCase):
 def test_dedicated_shortcode_and_contract(self):
  self.assertIn("add_shortcode('sc_workspace_platform'",PHP); self.assertIn("'/platform-contract'",PHP); self.assertIn('Research. Analyze. Decide. Carry the work forward.',PHP)
 def test_conversion_is_explicit_and_reversible(self):
  self.assertFalse(MAN['platform_conversion']['automatic']); self.assertTrue(MAN['platform_conversion']['administrator_action_required']); self.assertTrue(MAN['platform_conversion']['rollback_snapshot']); self.assertIn('perform_conversion',PLATFORM); self.assertIn('perform_restore',PLATFORM)
 def test_page_identity_preserved(self):
  self.assertTrue(MAN['platform_conversion']['page_id_preserved']); self.assertTrue(MAN['platform_conversion']['slug_preserved']); self.assertTrue(MAN['platform_conversion']['page_template_preserved']); self.assertNotIn("'post_name' =>", PLATFORM); self.assertNotIn("'post_parent' =>", PLATFORM)
 def test_data_contract_unchanged(self):
  self.assertEqual(MAN['storage_schema_version'],7); self.assertEqual(MAN['project_schema'],'sc-workspace-project/5.0'); self.assertEqual(MAN['decision_schema'],'sc-workspace-decision/1.0')
 def test_canonical_product_url(self):
  self.assertEqual(REG['product_url'],'/platform/'); self.assertEqual(REG['public_version'],'0.6.1'); self.assertEqual(REG['previous_version'],'0.6.0')
if __name__=='__main__': unittest.main()
