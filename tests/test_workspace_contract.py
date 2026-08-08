import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorkspaceContractTests(unittest.TestCase):
    def test_manifest(self):
        m=json.loads((ROOT/'release-manifest-v0.4.0.json').read_text())
        self.assertEqual(m['version'],'0.4.0'); self.assertEqual(m['previous_version'],'0.3.0')
        self.assertEqual(m['storage_schema_version'],4); self.assertEqual(m['project_schema'],'sc-workspace-project/3.0')
        self.assertEqual(m['research_schema'],'sc-workspace-research/1.0'); self.assertEqual(m['registry']['family'],'commercial')
        self.assertFalse(m['account_required']); self.assertFalse(m['server_project_storage']); self.assertFalse(m['cloud_sync'])
    def test_registry(self):
        r=json.loads((ROOT/'registry/workspace-product-record-v0.4.0.json').read_text())
        self.assertEqual(r['public_version'],'0.4.0'); self.assertEqual(r['previous_version'],'0.3.0'); self.assertEqual(r['console_screen'],'commercial')
    def test_rest_contracts(self):
        php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
        for token in ("'/research-contract'","'browser-local-projects-v4'","'project_schema' => 'sc-workspace-project/3.0'","'research_schema' => 'sc-workspace-research/1.0'","'storage_schema_version' => 4","'server_project_storage' => false","'collaboration' => false"):
            self.assertIn(token,php)
if __name__=='__main__': unittest.main()
