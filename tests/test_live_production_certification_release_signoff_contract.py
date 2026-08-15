import json
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class ProductionSignoffContractTests(unittest.TestCase):
    def test_historical_release_identity_and_freeze(self):
        m=json.loads((R/'history/release-manifest-v0.83.0.json').read_text())
        self.assertEqual((m['version'],m['previous_version']),('0.83.0','0.82.1'))
        self.assertEqual(m['storage_schema_version'],35)
        self.assertEqual(m['project_schema'],'sc-workspace-project/20.0')
        self.assertFalse(m['schema_migration_required'])
    def test_signoff_is_explicit(self):
        m=json.loads((R/'history/release-manifest-v0.83.0.json').read_text())['production_release_signoff']
        self.assertTrue(m['human_attestation_required'])
        self.assertTrue(m['rollback_rehearsal_required'])
        self.assertFalse(m['automatic_production_certification'])
        self.assertFalse(m['automatic_signoff'])
        self.assertFalse(m['project_content_in_certificate'])
    def test_current_release_preserves_v083_evidence_runtime(self):
        main=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
        run=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-production-signoff-v1.js').read_text()
        self.assertIn('Version: 1.0.0',main)
        self.assertIn("const RELEASE_VERSION='0.83.0'",run)
    def test_history_preserved(self):
        self.assertTrue((R/'history/release-manifest-v0.82.1.json').exists())
        self.assertTrue((R/'history/workspace-product-record-v0.82.1.json').exists())
if __name__=='__main__': unittest.main()
