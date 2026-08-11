import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.62.0.js'
MANIFEST=ROOT/'release-manifest-v0.62.0.json'
class BriefingPublicationContractTests(unittest.TestCase):
    def test_release_and_schema_boundary(self):
        m=json.loads(MANIFEST.read_text()); self.assertEqual(m['version'],'0.62.0'); self.assertEqual(m['previous_version'],'0.61.0'); self.assertEqual(m['storage_schema_version'],35); self.assertEqual(m['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(m['briefing_schema'],'sc-workspace-briefing/1.0'); self.assertFalse(m['governance']['automatic_publication']); self.assertFalse(m['governance']['cms_write'])
    def test_json_schemas(self):
        b=json.loads((ROOT/'schemas/sc-workspace-briefing-v1.schema.json').read_text()); p=json.loads((ROOT/'schemas/sc-workspace-project-v10.schema.json').read_text()); self.assertEqual(b['properties']['schema']['const'],'sc-workspace-briefing/1.0'); self.assertIn('briefing',p['required']); self.assertEqual(p['properties']['briefing']['$ref'],'sc-workspace-briefing-v1.schema.json')
    def test_rest_contract_and_project_mode(self):
        p=PHP.read_text(); self.assertIn("'/briefing-contract'",p); self.assertIn('public function briefing_contract()',p); self.assertIn('data-scw-project-mode="briefing"',p); self.assertIn('data-scw-project-panel="briefing"',p)
    def test_local_model_and_migration(self):
        j=JS.read_text(); self.assertIn("const BRIEFING_SCHEMA = 'sc-workspace-briefing/1.0'",j); self.assertIn('briefing: briefingTemplate()',j); self.assertIn('briefing: normalizeBriefing(raw.briefing, objects)',j); self.assertIn('function migrateV10(raw)',j); self.assertIn('if (raw.schemaVersion === 10) return migrateV10(raw);',j)
    def test_formats_outlines_and_sections(self):
        j=JS.read_text(); self.assertIn("'publication-draft'",j); self.assertIn("'Executive summary'",j); self.assertIn("'Abstract'",j); self.assertIn('data-scw-briefing-section-form',PHP.read_text()); self.assertNotIn('generate with AI',PHP.read_text().lower())
    def test_object_reference_cleanup_and_duplicate_mapping(self):
        j=JS.read_text(); self.assertIn('cleanBriefingReferences(project, object.id)',j); self.assertIn('copy.briefing.drafts=copy.briefing.drafts.map',j); self.assertIn('objectMap.get(draft.documentObjectId)',j)
    def test_document_materialization(self):
        j=JS.read_text(); self.assertIn("objectTemplate('document',draft.title)",j); self.assertIn("sourceTitle:'Workspace Briefing & Publication Studio'",j); self.assertIn('briefingMarkdown(project,draft)',j); self.assertIn("relation:'derived-from',note:'Briefing basis'",j)
    def test_portable_exports_no_direct_publish(self):
        j=JS.read_text(); p=PHP.read_text(); self.assertIn('PUBLICATION_EXPORT_SCHEMA',j); self.assertIn('Export Markdown',p); self.assertIn('Export HTML',p); self.assertIn('Export publication package',p); self.assertIn('automaticPublication:false',j); self.assertIn('does not automatically publish',p)
    def test_canonical_library_route_retained(self):
        self.assertIn("home_url('/knowledge-libraries/')",PHP.read_text()); self.assertEqual(json.loads(MANIFEST.read_text())['canonical_library_path'],'/knowledge-libraries/')
if __name__=='__main__': unittest.main()
