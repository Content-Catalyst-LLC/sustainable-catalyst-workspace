import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.3.0.js'
PHP = ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'


class ObjectContractTests(unittest.TestCase):
    def test_object_schema(self):
        schema = json.loads((ROOT / 'schemas/sc-workspace-object-v1.schema.json').read_text())
        self.assertEqual(schema['properties']['schema']['const'], 'sc-workspace-object/1.0')
        self.assertEqual(schema['properties']['type']['enum'], ['source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export'])
        self.assertEqual(schema['properties']['status']['enum'], ['draft', 'working', 'ready'])
        self.assertEqual(schema['properties']['content']['maxLength'], 50000)
        self.assertEqual(schema['properties']['tags']['maxItems'], 20)

    def test_project_schema_embeds_objects(self):
        schema = json.loads((ROOT / 'schemas/sc-workspace-project-v2.schema.json').read_text())
        self.assertEqual(schema['properties']['schema']['const'], 'sc-workspace-project/2.0')
        self.assertEqual(schema['properties']['objects']['maxItems'], 250)
        self.assertIn('activeObjectId', schema['required'])
        self.assertEqual(schema['properties']['activity']['maxItems'], 60)

    def test_object_operations_present(self):
        js = JS.read_text()
        for token in (
            'function objectTemplate',
            'function normalizeObject',
            'data-scw-new-object',
            'data-scw-object-duplicate',
            'data-scw-object-export',
            'data-scw-object-archive',
            'data-scw-object-delete',
            'OBJECT_EXPORT_SCHEMA',
            'normalizeTags',
            'normalizeProvenance',
        ):
            self.assertIn(token, js)

    def test_object_ui_types_present(self):
        php = PHP.read_text()
        for label in ('Source', 'Evidence', 'Dataset', 'Analysis', 'Decision', 'Document', 'Export'):
            self.assertIn(f'>{label}<', php)
        for token in ('data-scw-object-summary', 'data-scw-object-content', 'data-scw-object-tags', 'data-scw-object-source-url'):
            self.assertIn(token, php)

    def test_handoff_uses_ids_only(self):
        js = JS.read_text()
        self.assertIn("target.searchParams.set('sc_workspace_project', project.id)", js)
        self.assertIn("target.searchParams.set('sc_workspace_object', object.id)", js)
        self.assertIn('objectId: object ? object.id : null', js)
        for forbidden in (
            "searchParams.set('sc_workspace_title'",
            "searchParams.set('sc_workspace_notes'",
            "searchParams.set('sc_workspace_description'",
            "searchParams.set('sc_workspace_object_title'",
            "searchParams.set('sc_workspace_object_content'",
            "searchParams.set('sc_workspace_object_summary'",
        ):
            self.assertNotIn(forbidden, js)


if __name__ == '__main__':
    unittest.main()
