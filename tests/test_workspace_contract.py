import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads((ROOT/'release-manifest-v0.4.1.json').read_text()); self.assertEqual(m['version'],'0.4.1'); self.assertEqual(m['previous_version'],'0.4.0'); self.assertFalse(m['account_required']); self.assertTrue(m['anonymous_access']); self.assertFalse(m['cloud_sync']); self.assertFalse(m['server_project_storage'])
 def test_registry(self):
  r=json.loads((ROOT/'registry/workspace-product-record-v0.4.1.json').read_text()); self.assertEqual(r['public_version'],'0.4.1'); self.assertEqual(r['previous_version'],'0.4.0'); self.assertEqual(r['console_screen'],'commercial')
 def test_php_contract(self):
  t=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();
  for x in ("'/identity-contract'","'browser-local-projects-v5'","'project_schema' => 'sc-workspace-project/3.1'","'identity_schema' => 'sc-workspace-identity/1.0'","'storage_schema_version' => 5","'account_required' => false","'server_project_storage' => false","'cloud_sync' => false"): self.assertIn(x,t)
if __name__=='__main__': unittest.main()
