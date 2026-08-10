import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.52.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.52.0.json').read_text())
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.52.0.js').read_text()
NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
KINDS=['outline','citation-pack','source-matrix','evidence-summary','research-synthesis']
class NotebookSynthesisCitationWorkspaceContract(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.52.0','0.51.0','Research Tasks & Workflow State')); self.assertIn('Version: 0.52.0',MAIN)
 def test_02_schema_migration(self):
  self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertEqual((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to']),('sc-workspace-project/20.0','sc-workspace-project/20.0')); self.assertIn('function migrateV32(raw)',JS); self.assertIn('if (raw.schemaVersion === 32) return migrateV32(raw);',JS)
 def test_03_synthesis_schemas(self):
  self.assertEqual(MAN['notebook_workspace_schema'],'sc-workspace-notebook-workspace/8.0'); self.assertEqual(MAN['notebook_export_schema'],'sc-workspace-notebook-export/8.0'); self.assertEqual(MAN['notebook_synthesis_schema'],'sc-workspace-notebook-synthesis/1.0'); self.assertEqual(MAN['notebook_synthesis_export_schema'],'sc-workspace-notebook-synthesis-export/1.0')
  for name in ('sc-workspace-notebook-synthesis-v1.schema.json','sc-workspace-notebook-synthesis-export-v1.schema.json','sc-workspace-notebook-workspace-v5.schema.json','sc-workspace-notebook-export-v5.schema.json','sc-workspace-project-v17.schema.json'): json.loads((ROOT/'schemas'/name).read_text())
 def test_04_modes_and_limits(self):
  rn=MAN['research_notebook']; self.assertEqual(rn['synthesis_kinds'],KINDS); self.assertEqual(rn['syntheses_per_project'],120); self.assertEqual(rn['items_per_synthesis'],120); self.assertTrue(rn['synthesis_requires_explicit_selection'])
 def test_05_governance(self):
  g=MAN['governance']; self.assertTrue(g['notebook_synthesis_explicit_selection_required']); self.assertFalse(g['notebook_automatic_synthesis']); self.assertFalse(g['notebook_synthesis_automatic_ai']); self.assertFalse(g['notebook_synthesis_citation_guessing']); self.assertTrue(g['notebook_synthesis_missing_citation_facts_remain_missing']); self.assertFalse(g['notebook_synthesis_source_material_mutation']); self.assertFalse(g['notebook_synthesis_hidden_evidence_score'])
 def test_06_helper_surface(self):
  for token in ("SYNTHESIS_SCHEMA='sc-workspace-notebook-synthesis/1.0'","SYNTHESIS_EXPORT_SCHEMA='sc-workspace-notebook-synthesis-export/1.0'",'generateSynthesis','exportSynthesis','resolveRef','synthesesForRef','citationLine','source-matrix','evidence-summary','research-synthesis'): self.assertIn(token,NB)
 def test_07_ui_surface(self):
  for token in ('data-scw-notebook-synthesis-form','data-scw-notebook-synthesis-material','data-scw-notebook-synthesis-list','data-scw-notebook-metric-syntheses','Create synthesis'): self.assertIn(token,PHP)
  for token in ('renderNotebookSynthesis(project)','helper.generateSynthesis','helper.exportSynthesis','Create Document'): self.assertIn(token,JS)
 def test_08_rest_contract(self):
  self.assertIn("'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0'",PHP); self.assertIn("'notebook_synthesis_schema' => 'sc-workspace-notebook-synthesis/1.0'",PHP); self.assertIn("'synthesis_requires_explicit_selection' => true",PHP); self.assertIn("'citation_guessing' => false",PHP)
 def test_09_prior_research_state_preserved(self):
  mig=MAN['migration']; self.assertTrue(mig['preserves_notebook_promotions']); self.assertTrue(mig['preserves_notebook_collections']); self.assertTrue(mig['preserves_notebook_links']); self.assertTrue(mig['preserves_source_capture']); self.assertTrue((ROOT/'history/release-manifest-v0.35.0.json').exists())
 def test_10_registry(self):
  self.assertEqual((REG['public_version'],REG['previous_version']),('0.52.0','0.51.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0520'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0360',REGPHP)
if __name__=='__main__': unittest.main()
