import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.11.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'

class MigrationTests(unittest.TestCase):
    def test_storage_v11_to_v12_migration(self):
        js=JS.read_text()
        for token in ("const STORAGE_VERSION = 12",'function migrateV11',"if (raw.schemaVersion === 11) return migrateV11(raw)","const PROJECT_SCHEMA = 'sc-workspace-project/10.0'","const LEGACY_PROJECT_SCHEMA_V9 = 'sc-workspace-project/9.0'","guidedWorkflows: normalizeGuidedWorkflows(raw.guidedWorkflows, objects)"):
            self.assertIn(token,js)
    def test_older_migrations_retained(self):
        js=JS.read_text()
        for token in ('function migrateV9','function migrateV8','function migrateV7','function migrateV6','function migrateV5','function migrateV4','function migrateV3','function migrateV2','function migrateLegacyV1'):
            self.assertIn(token,js)
    def test_clone_remaps_canvas_object_briefing_and_workflow_refs(self):
        js=JS.read_text()
        for token in ('const objectMap = new Map()','const boardMap = new Map()','const nodeMap = new Map()','objectMap.get(node.objectId)','nodeMap.get(edge.fromNodeId)','nodeMap.get(edge.toNodeId)','copy.briefing.drafts=copy.briefing.drafts.map','objectMap.get(draft.documentObjectId)','copy.guidedWorkflows.runs = copy.guidedWorkflows.runs.map','step.objectIds.map(v=>objectMap.get(v))'):
            self.assertIn(token,js)
if __name__=='__main__': unittest.main()
