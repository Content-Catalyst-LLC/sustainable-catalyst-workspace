import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = json.loads((ROOT / 'release-manifest-v0.66.0.json').read_text())
REG = json.loads((ROOT / 'registry/workspace-product-record-v0.66.0.json').read_text())
JS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
NB = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()
PHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN = (ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()

TARGETS = ['source','evidence','dataset','analysis','decision','document','canvas']

class NotebookToWorkspaceIntelligenceContract(unittest.TestCase):
    def test_01_release_lineage(self):
        self.assertEqual((MAN['version'], MAN['previous_version'], MAN['release_name']),
                         ('0.66.0', '0.65.0', 'Import, Export & Backward-Compatibility Hardening'))
        self.assertIn('Version: 1.13.0', MAIN)

    def test_02_storage_and_project_migration(self):
        self.assertEqual((MAN['storage_schema_version'], MAN['project_schema'], MAN['export_schema']),
                         (35, 'sc-workspace-project/20.0', 'sc-workspace-project-export/20.0'))
        self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35))
        self.assertEqual((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to']),('sc-workspace-project/20.0','sc-workspace-project/20.0'))
        self.assertIn('function migrateV32(raw)', JS)
        self.assertIn('if (raw.schemaVersion === 32) return migrateV32(raw);', JS)

    def test_03_notebook_promotion_schemas(self):
        self.assertEqual(MAN['notebook_workspace_schema'], 'sc-workspace-notebook-workspace/8.0')
        self.assertEqual(MAN['notebook_schema'], 'sc-workspace-notebook/3.0')
        self.assertEqual(MAN['notebook_block_schema'], 'sc-workspace-notebook-block/3.0')
        self.assertEqual(MAN['notebook_export_schema'], 'sc-workspace-notebook-export/8.0')
        self.assertEqual(MAN['notebook_promotion_schema'], 'sc-workspace-notebook-promotion/1.0')
        for name in (
            'sc-workspace-notebook-block-v3.schema.json',
            'sc-workspace-notebook-v3.schema.json',
            'sc-workspace-notebook-promotion-v1.schema.json',
            'sc-workspace-notebook-workspace-v4.schema.json',
            'sc-workspace-notebook-export-v4.schema.json',
            'sc-workspace-project-v16.schema.json',
        ):
            json.loads((ROOT / 'schemas' / name).read_text())

    def test_04_explicit_destination_set(self):
        rn = MAN['research_notebook']
        self.assertEqual(rn['promotion_targets'], TARGETS)
        self.assertTrue(rn['promotion_requires_explicit_destination'])
        self.assertTrue(rn['multiple_derivatives_per_block'])
        self.assertTrue(rn['promotion_lineage_visible'])
        self.assertTrue(rn['promotion_ledger_project_bound'])
        self.assertTrue(rn['canvas_promotion_creates_node'])

    def test_05_no_automatic_or_hidden_promotion(self):
        self.assertFalse(MAN['research_notebook']['automatic_promotion'])
        self.assertFalse(MAN['governance']['notebook_automatic_promotion'])
        self.assertFalse(MAN['governance']['notebook_promotion_hidden_classification'])
        self.assertFalse(MAN['governance']['notebook_promotion_ai_required'])
        self.assertFalse(MAN['governance']['notebook_promotion_overwrites_source_block'])
        self.assertTrue(MAN['governance']['notebook_promotion_requires_explicit_destination'])
        self.assertTrue(MAN['governance']['notebook_promotion_preserves_original_material'])

    def test_06_helper_promotion_ledger(self):
        for token in (
            "PROMOTION_SCHEMA='sc-workspace-notebook-promotion/1.0'",
            'createPromotion', 'promotionRecord', 'promotionsForRef',
            'promotionDestinations', 'suggestedPromotionType', 'canvasNodeType',
            'promotions', 'automaticPromotion:false',
        ):
            self.assertIn(token, NB)

    def test_07_workspace_promotion_runtime(self):
        for token in (
            'function promoteNotebookBlock(project, notebook, section, block, targetType)',
            "if(targetType==='canvas')",
            "objectTemplate(targetType,block.title||`${block.type} from Notebook`)",
            'helper.createPromotion?.(sourceRef,targetType,targetKind,targetId',
            "block.promotion={status:'promoted',targetKind,targetType,targetId,promotedAt:stamp}",
            'renderNotebookPromotions(project)',
            "title:'Notebook Promotions'",
        ):
            self.assertIn(token, JS)

    def test_08_source_and_evidence_integrations(self):
        self.assertIn("targetType==='source'&&project.research.readingQueue", JS)
        self.assertIn("targetType==='evidence'&&block.sourceObjectId", JS)
        self.assertIn('sourceObjectId:block.sourceObjectId', JS)

    def test_09_visible_ui_and_rest_contract(self):
        self.assertIn('data-scw-notebook-promotion-list', PHP)
        self.assertIn("'notebook_promotion_schema' => 'sc-workspace-notebook-promotion/1.0'", PHP)
        self.assertIn("'promotion_targets' => array('source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'canvas')", PHP)
        self.assertIn("'promotion_requires_explicit_destination' => true", PHP)
        self.assertIn("'multiple_derivatives_per_block' => true", PHP)
        self.assertIn("'promotion_lineage_visible' => true", PHP)

    def test_10_project_and_account_contracts_advance(self):
        self.assertIn("'schema' => 'sc-workspace-project-contract/20.0'", PHP)
        self.assertIn("'export_schema' => 'sc-workspace-project-export/20.0'", PHP)
        self.assertIn("array('sc-workspace-project/20.0','sc-workspace-project/19.0','sc-workspace-project/18.0'", PHP)

    def test_11_v034_knowledge_links_preserved(self):
        rn = MAN['research_notebook']
        self.assertEqual(rn['link_relations'], ['references','supports','contrasts','extends','related'])
        self.assertTrue(rn['backlinks_derived_from_explicit_links'])
        self.assertTrue(MAN['migration']['preserves_notebook_collections'])
        self.assertTrue(MAN['migration']['preserves_notebook_links'])
        self.assertTrue((ROOT / 'history/release-manifest-v0.34.0.json').exists())
        self.assertTrue((ROOT / 'history/workspace-product-record-v0.34.0.json').exists())

    def test_12_registry_lineage(self):
        self.assertEqual((REG['public_version'], REG['previous_version']), ('0.66.0','0.65.0'))
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v1130'", REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0360', REGPHP)

if __name__ == '__main__':
    unittest.main()
