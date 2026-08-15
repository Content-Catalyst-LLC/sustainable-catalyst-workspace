import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class WorkspaceHomeProjectCockpitTests(unittest.TestCase):
 def test_release_identity(self):
  m=json.loads((R/'history/release-manifest-v1.1.0.json').read_text());self.assertEqual((m['version'],m['previous_version'],m['release_name']),('1.1.0','1.0.1','Workspace Home, Project Cockpit & Navigation Refinement'));self.assertEqual(m['storage_schema_version'],35);self.assertFalse(m['schema_migration_required'])
 def test_only_new_route(self):
  cur=json.loads((R/'history/release-manifest-v1.1.0.json').read_text());old=json.loads((R/'history/release-manifest-v1.0.1.json').read_text());self.assertEqual(set(cur['rest_routes'])-set(old['rest_routes']),{'/wp-json/sc-workspace/v1/workspace-home-contract'});self.assertEqual(cur['object_types'],old['object_types'])
 def test_home_governance(self):
  h=json.loads((R/'history/release-manifest-v1.1.0.json').read_text())['workspace_home_project_cockpit'];self.assertTrue(h['project_cockpit']);self.assertTrue(h['deterministic_next_actions']);self.assertTrue(h['review_navigation_progressive_disclosure']);self.assertFalse(h['schema_migration_required']);self.assertFalse(h['automatic_project_mutation']);self.assertFalse(h['automatic_ai']);self.assertFalse(h['behavioral_telemetry'])
 def test_history_preserved(self): self.assertTrue((R/'history/release-manifest-v1.0.1.json').exists());self.assertTrue((R/'history/workspace-product-record-v1.0.1.json').exists())
if __name__=='__main__':unittest.main()
