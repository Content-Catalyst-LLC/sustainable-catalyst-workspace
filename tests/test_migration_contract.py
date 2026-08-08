import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.3.0.js'


class MigrationContractTests(unittest.TestCase):
    def test_storage_v3_and_v2_migration(self):
        js = JS.read_text()
        for token in (
            'const STORAGE_VERSION = 3',
            'function migrateV2',
            "if (raw.schemaVersion === 2) return migrateV2(raw)",
            "const LEGACY_PROJECT_SCHEMA = 'sc-workspace-project/1.0'",
            "const PROJECT_SCHEMA = 'sc-workspace-project/2.0'",
            "const LEGACY_EXPORT_SCHEMA = 'sc-workspace-project-export/1.0'",
            'objects: [],',
            'activeObjectId: null',
        ):
            self.assertIn(token, js)

    def test_v010_migration_is_retained(self):
        js = JS.read_text()
        self.assertIn("const LEGACY_KEY = 'sc_workspace_v0_1'", js)
        self.assertIn('function migrateLegacyV1', js)
        self.assertIn('RECOVERY_KEY', js)
        self.assertIn('function quarantine', js)

    def test_project_clone_regenerates_object_ids(self):
        js = JS.read_text()
        self.assertIn("copy.id = id('scwp')", js)
        self.assertIn("id: id('scwo')", js)


if __name__ == '__main__':
    unittest.main()
