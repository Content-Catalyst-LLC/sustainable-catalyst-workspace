import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class HistoricalGAReadinessContractTests(unittest.TestCase):
 def test_historical_identity(self):
  m=json.loads((R/'history/release-manifest-v0.84.0.json').read_text());self.assertEqual((m['version'],m['previous_version'],m['release_name']),('0.84.0','0.83.0','Production Sign-Off Closure & 1.0 Release Readiness'))
  self.assertEqual(m['storage_schema_version'],35);self.assertFalse(m['schema_migration_required'])
 def test_prerequisite_preserved(self):
  g=json.loads((R/'history/release-manifest-v0.84.0.json').read_text())['production_ga_readiness'];self.assertEqual(g['production_signoff_release'],'0.83.0');self.assertFalse(g['automatic_promotion_to_1_0'])
 def test_current_advances(self):
  main=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();self.assertIn('Version: 1.15.0',main);self.assertTrue((R/'release-manifest-v1.0.1.json').exists())
if __name__=='__main__':unittest.main()
