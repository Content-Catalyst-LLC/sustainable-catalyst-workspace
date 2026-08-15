import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class GAReadinessContractTests(unittest.TestCase):
    def test_release_identity_and_freeze(self):
        m=json.loads((R/'release-manifest-v0.84.0.json').read_text())
        self.assertEqual((m['version'],m['previous_version'],m['release_name']),('0.84.0','0.83.0','Production Sign-Off Closure & 1.0 Release Readiness'))
        self.assertEqual(m['storage_schema_version'],35)
        self.assertEqual(m['project_schema'],'sc-workspace-project/20.0')
        self.assertEqual(m['export_schema'],'sc-workspace-project-export/20.0')
        self.assertFalse(m['schema_migration_required'])
    def test_prior_signoff_is_required(self):
        g=json.loads((R/'release-manifest-v0.84.0.json').read_text())['production_ga_readiness']
        self.assertEqual(g['production_signoff_release'],'0.83.0')
        self.assertEqual(g['required_production_signoff_schema'],'sc-workspace-production-signoff-certificate/1.0')
        self.assertTrue(g['signed_production_certificate_required'])
        self.assertTrue(g['human_readiness_attestation_required'])
        self.assertFalse(g['automatic_promotion_to_1_0'])
        self.assertFalse(g['project_content_in_dossier'])
    def test_history_preserved(self):
        self.assertTrue((R/'history/release-manifest-v0.83.0.json').exists())
        self.assertTrue((R/'history/workspace-product-record-v0.83.0.json').exists())
    def test_new_surface_is_narrow(self):
        cur=json.loads((R/'release-manifest-v0.84.0.json').read_text())
        old=json.loads((R/'history/release-manifest-v0.83.0.json').read_text())
        self.assertEqual(set(cur['rest_routes'])-set(old['rest_routes']),{'/wp-json/sc-workspace/v1/ga-readiness-contract'})
        self.assertEqual(cur['object_types'],old['object_types'])
if __name__=='__main__': unittest.main()
