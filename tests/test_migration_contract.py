import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.5.0.js'
class MigrationTests(unittest.TestCase):
    def test_storage_v5_to_v6_migration(self):
        js=JS.read_text()
        for token in ('const STORAGE_VERSION = 6','function migrateV5',"if (raw.schemaVersion === 5) return migrateV5(raw)","const PROJECT_SCHEMA = 'sc-workspace-project/4.0'","const LEGACY_PROJECT_SCHEMA_V31 = 'sc-workspace-project/3.1'","analysis: normalizeAnalysis(raw.analysis, objects)"):
            self.assertIn(token,js)
    def test_older_migrations_retained(self):
        js=JS.read_text()
        for token in ('function migrateV4','function migrateV3','function migrateV2','function migrateLegacyV1',"const LEGACY_KEY = 'sc_workspace_v0_1'"):
            self.assertIn(token,js)
    def test_clone_remaps_cross_object_references(self):
        js=JS.read_text(); self.assertIn('const objectMap = new Map()',js); self.assertIn('objectMap.get(link.evidenceObjectId)',js); self.assertIn('objectMap.get(method.analysisObjectId)',js); self.assertIn('objectMap.get(finding.analysisObjectId)',js)
if __name__=='__main__': unittest.main()
