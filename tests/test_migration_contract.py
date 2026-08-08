import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.4.0.js'
class MigrationTests(unittest.TestCase):
    def test_storage_v4_migration(self):
        js=JS.read_text()
        for token in ('const STORAGE_VERSION = 4','function migrateV3',"if (raw.schemaVersion === 3) return migrateV3(raw)","const PROJECT_SCHEMA = 'sc-workspace-project/3.0'","const LEGACY_PROJECT_SCHEMA_V2 = 'sc-workspace-project/2.0'","research: normalizeResearch(raw.research, objects)"):
            self.assertIn(token,js)
    def test_older_migrations_retained(self):
        js=JS.read_text(); self.assertIn('function migrateV2',js); self.assertIn('function migrateLegacyV1',js); self.assertIn("const LEGACY_KEY = 'sc_workspace_v0_1'",js)
    def test_clone_remaps_research_object_references(self):
        js=JS.read_text(); self.assertIn('const objectMap = new Map()',js); self.assertIn('objectMap.get(link.evidenceObjectId)',js); self.assertIn('objectMap.get(item.objectId)',js)
if __name__=='__main__': unittest.main()
