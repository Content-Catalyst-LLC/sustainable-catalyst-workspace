import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceContractTests(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads((ROOT / 'release-manifest-v0.3.0.json').read_text())
        self.assertEqual(manifest['version'], '0.3.0')
        self.assertEqual(manifest['previous_version'], '0.2.0')
        self.assertEqual(manifest['access_model'], 'free-public')
        self.assertFalse(manifest['account_required'])
        self.assertFalse(manifest['server_project_storage'])
        self.assertEqual(manifest['storage_schema_version'], 3)
        self.assertEqual(manifest['project_schema'], 'sc-workspace-project/2.0')
        self.assertEqual(manifest['object_schema'], 'sc-workspace-object/1.0')
        self.assertEqual(manifest['registry']['family'], 'commercial')

    def test_registry_record(self):
        record = json.loads((ROOT / 'registry/workspace-product-record-v0.3.0.json').read_text())
        self.assertEqual(record['canonical_id'], 'sustainable-catalyst-workspace')
        self.assertEqual(record['console_screen'], 'commercial')
        self.assertEqual(record['display_order'], 400)
        self.assertEqual(record['public_version'], '0.3.0')
        self.assertEqual(record['previous_version'], '0.2.0')
        self.assertEqual(record['commercial'], '1')
        self.assertEqual(record['public_interest'], '1')

    def test_health_and_rest_contract(self):
        php = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
        for token in (
            "add_shortcode('sc_workspace'",
            "add_shortcode('sc_workspace_entry'",
            "'/object-contract'",
            "'browser-local-projects-v3'",
            "'project_schema' => 'sc-workspace-project/2.0'",
            "'object_schema' => 'sc-workspace-object/1.0'",
            "'storage_schema_version' => 3",
            "'max_objects_per_project' => 250",
            "'server_project_storage' => false",
            "'cloud_sync' => false",
            "'collaboration' => false",
        ):
            self.assertIn(token, php)


if __name__ == '__main__':
    unittest.main()
