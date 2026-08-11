import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorkspaceContract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads((ROOT/'release-manifest-v0.58.0.json').read_text()); self.assertEqual(m['version'],'0.58.0'); self.assertEqual(m['previous_version'],'0.57.0'); self.assertEqual(m['release_name'],'Scale, Performance & Large-Project Hardening'); self.assertFalse(m['account_required']); self.assertTrue(m['anonymous_access']); self.assertEqual(m['cloud_sync'],'explicit-project-enrollment'); self.assertEqual(m['server_project_storage'],'manual-backup-plus-explicit-sync-head'); self.assertEqual(m['canvas_schema'],'sc-workspace-canvas/1.0')
 def test_registry(self):
  r=json.loads((ROOT/'registry/workspace-product-record-v0.58.0.json').read_text()); self.assertEqual(r['public_version'],'0.58.0'); self.assertEqual(r['previous_version'],'0.57.0'); self.assertEqual(r['console_screen'],'commercial'); self.assertEqual(r['family'],'commercial'); self.assertEqual(r['product_url'],'/platform/')
 def test_runtime_contract(self):
  t=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
  for x in ("'/identity-contract'","'/analysis-contract'","'/decision-contract'","'/canvas-contract'","'/sync-contract'","browser-local-projects-v27","'project_schema' => 'sc-workspace-project/20.0'","'canvas_schema' => 'sc-workspace-canvas/1.0'","'storage_schema_version' => 35","'account_required' => false","'server_project_storage' => 'manual-backup-plus-explicit-sync-head'","'cloud_sync' => 'explicit-project-enrollment'"): self.assertIn(x,t)
if __name__=='__main__':unittest.main()
