import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class GeneralAvailabilityContractTests(unittest.TestCase):
 def test_release_identity(self):
  m=json.loads((R/'history/release-manifest-v1.0.0.json').read_text());self.assertEqual((m['version'],m['previous_version'],m['release_name']),('1.0.0','0.84.0','General Availability'));self.assertEqual(m['storage_schema_version'],35);self.assertFalse(m['schema_migration_required'])
 def test_ga_boundary(self):
  g=json.loads((R/'history/release-manifest-v1.0.0.json').read_text())['general_availability'];self.assertTrue(g['general_availability']);self.assertTrue(g['stable_release']);self.assertEqual(g['readiness_release'],'0.84.0');self.assertEqual(g['rollback_release'],'0.84.0');self.assertFalse(g['automatic_release_certification']);self.assertFalse(g['project_content_in_certificate'])
 def test_only_new_route(self):
  cur=json.loads((R/'history/release-manifest-v1.0.0.json').read_text());old=json.loads((R/'history/release-manifest-v0.84.0.json').read_text());self.assertEqual(set(cur['rest_routes'])-set(old['rest_routes']),{'/wp-json/sc-workspace/v1/general-availability-contract'});self.assertEqual(cur['object_types'],old['object_types'])
if __name__=='__main__':unittest.main()
