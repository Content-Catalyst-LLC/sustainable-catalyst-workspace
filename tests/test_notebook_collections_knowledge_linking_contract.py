import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
NOTEBOOK=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()

class NotebookCollectionsKnowledgeLinkingContract(unittest.TestCase):
    def test_01_release_lineage(self):
        self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'))
        self.assertIn('Version: 2.0.1',MAIN)
    def test_02_migration(self):
        self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'))
        self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35))
        self.assertEqual((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to']),('sc-workspace-project/20.0','sc-workspace-project/20.0'))
        self.assertIn('function migrateV32(raw)',JS)
    def test_03_notebook_linking_schemas(self):
        self.assertEqual(MAN['notebook_workspace_schema'],'sc-workspace-notebook-workspace/8.0')
        self.assertEqual(MAN['notebook_link_schema'],'sc-workspace-notebook-link/1.0')
        self.assertEqual(MAN['notebook_collection_schema'],'sc-workspace-notebook-collection/1.0')
        self.assertEqual(MAN['notebook_ref_schema'],'sc-workspace-notebook-ref/1.0')
        self.assertEqual(MAN['notebook_export_schema'],'sc-workspace-notebook-export/8.0')
    def test_04_schema_files(self):
        for name in ('sc-workspace-notebook-ref-v1.schema.json','sc-workspace-notebook-link-v1.schema.json','sc-workspace-notebook-collection-v1.schema.json','sc-workspace-notebook-workspace-v3.schema.json','sc-workspace-notebook-export-v3.schema.json','sc-workspace-project-v15.schema.json'):
            json.loads((ROOT/'schemas'/name).read_text())
    def test_05_explicit_relations(self):
        rn=MAN['research_notebook']
        self.assertEqual(rn['link_relations'],['references','supports','contrasts','extends','related'])
        self.assertEqual(rn['link_target_kinds'],['notebook','section','block','object'])
        self.assertTrue(rn['explicit_cross_notebook_links']); self.assertTrue(rn['notebook_to_object_links']); self.assertTrue(rn['backlinks_derived_from_explicit_links'])
        self.assertFalse(rn['automatic_link_inference']); self.assertFalse(rn['semantic_embeddings_required'])
    def test_06_runtime_helper(self):
        for token in ('createCollection','addCollectionItem','createLink','backlinksForRef','findBlockLocation','refExists','sc-workspace-notebook-workspace/8.0'):
            self.assertIn(token,NOTEBOOK)
    def test_07_ui_surface(self):
        for token in ('data-scw-notebook-collection-form','data-scw-notebook-collection-assign-form','data-scw-notebook-link-form','data-scw-notebook-link-list','backlinked targets'):
            self.assertIn(token,PHP)
        for token in ('renderNotebookKnowledgeLinks','notebookRefOptions','openNotebookRef','notebookMetricBacklinks'):
            self.assertIn(token,JS)
    def test_08_governance(self):
        self.assertFalse(MAN['governance']['notebook_automatic_link_inference']); self.assertTrue(MAN['governance']['notebook_backlinks_derived_only']); self.assertFalse(MAN['governance']['notebook_collections_copy_canonical_object_content'])
    def test_09_rest_contract(self):
        self.assertIn("'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0'",PHP)
        self.assertIn("'notebook_link_schema' => 'sc-workspace-notebook-link/1.0'",PHP)
        self.assertIn("'backlinks_derived_from_explicit_links' => true",PHP)
        self.assertIn("'automatic_link_inference' => false",PHP)
    def test_10_registry_lineage(self):
        self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'))
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0360',REGPHP)
        self.assertTrue((ROOT/'history/release-manifest-v0.35.0.json').exists())
        self.assertTrue((ROOT/'history/workspace-product-record-v0.35.0.json').exists())

if __name__=='__main__': unittest.main()
