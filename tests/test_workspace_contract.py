import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads((ROOT/'release-manifest-v0.5.0.json').read_text()); self.assertEqual(m['version'],'0.5.0'); self.assertEqual(m['previous_version'],'0.4.1'); self.assertEqual(m['release_name'],'Analysis Workspace'); self.assertFalse(m['account_required']); self.assertTrue(m['anonymous_access']); self.assertFalse(m['cloud_sync']); self.assertFalse(m['server_project_storage']); self.assertEqual(m['analysis_schema'],'sc-workspace-analysis/1.0')
 def test_registry(self):
  r=json.loads((ROOT/'registry/workspace-product-record-v0.5.0.json').read_text()); self.assertEqual(r['public_version'],'0.5.0'); self.assertEqual(r['previous_version'],'0.4.1'); self.assertEqual(r['console_screen'],'commercial'); self.assertEqual(r['family'],'commercial')
 def test_php_contract(self):
  t=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();
  for x in ("'/identity-contract'","'/analysis-contract'","'browser-local-projects-v6'","'project_schema' => 'sc-workspace-project/4.0'","'analysis_schema' => 'sc-workspace-analysis/1.0'","'storage_schema_version' => 6","'account_required' => false","'server_project_storage' => false","'cloud_sync' => false"): self.assertIn(x,t)
if __name__=='__main__': unittest.main()
