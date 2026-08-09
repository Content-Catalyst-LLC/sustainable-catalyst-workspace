import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.10.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'

class MigrationTests(unittest.TestCase):
    def test_storage_v10_to_v11_migration(self):
        js=JS.read_text()
        for token in ("const STORAGE_VERSION = 11",'function migrateV10',"if (raw.schemaVersion === 10) return migrateV10(raw)","const PROJECT_SCHEMA = 'sc-workspace-project/9.0'","const LEGACY_PROJECT_SCHEMA_V8 = 'sc-workspace-project/8.0'","briefing: normalizeBriefing(raw.briefing, objects)"):
            self.assertIn(token,js)
    def test_older_migrations_retained(self):
        js=JS.read_text()
        for token in ('function migrateV9','function migrateV8','function migrateV7','function migrateV6','function migrateV5','function migrateV4','function migrateV3','function migrateV2','function migrateLegacyV1'):
            self.assertIn(token,js)
    def test_clone_remaps_canvas_object_and_briefing_refs(self):
        js=JS.read_text()
        for token in ('const objectMap = new Map()','const boardMap = new Map()','const nodeMap = new Map()','objectMap.get(node.objectId)','nodeMap.get(edge.fromNodeId)','nodeMap.get(edge.toNodeId)','copy.briefing.drafts=copy.briefing.drafts.map','objectMap.get(draft.documentObjectId)'):
            self.assertIn(token,js)
if __name__=='__main__': unittest.main()
