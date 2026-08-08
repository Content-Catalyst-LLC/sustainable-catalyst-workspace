import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.9.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'

class MigrationTests(unittest.TestCase):
    def test_storage_v8_to_v9_migration(self):
        js=JS.read_text()
        for token in ('const STORAGE_VERSION = 10','function migrateV8',"if (raw.schemaVersion === 8) return migrateV8(raw)","const PROJECT_SCHEMA = 'sc-workspace-project/8.0'","const LEGACY_PROJECT_SCHEMA_V6 = 'sc-workspace-project/6.0'","handoffs: normalizeHandoffs(raw.handoffs, objects, canvas)"):
            self.assertIn(token,js)
    def test_older_migrations_retained(self):
        js=JS.read_text()
        for token in ('function migrateV7','function migrateV6','function migrateV5','function migrateV4','function migrateV3','function migrateV2','function migrateLegacyV1'):
            self.assertIn(token,js)
    def test_clone_remaps_canvas_and_object_refs(self):
        js=JS.read_text();
        for token in ('const objectMap = new Map()','const boardMap = new Map()','const nodeMap = new Map()','objectMap.get(node.objectId)','nodeMap.get(edge.fromNodeId)','nodeMap.get(edge.toNodeId)'):
            self.assertIn(token,js)
if __name__=='__main__': unittest.main()
