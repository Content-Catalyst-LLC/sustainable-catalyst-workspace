import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.53.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.53.0.json').read_text())
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.53.0.js').read_text()
NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()
ADAPTER=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-notebook-assistance-adapter-v1.js').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class GroundedNotebookAssistanceContract(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.53.0','0.52.0','Collaboration Architecture Foundation')); self.assertIn('Version: 0.53.0',MAIN)
 def test_02_schema_migration(self):
  self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged']); self.assertIn('function migrateV32(raw)',JS); self.assertIn('if (raw.schemaVersion === 32) return migrateV32(raw);',JS)
 def test_03_assistance_schemas(self):
  self.assertEqual(MAN['notebook_workspace_schema'],'sc-workspace-notebook-workspace/8.0'); self.assertEqual(MAN['notebook_export_schema'],'sc-workspace-notebook-export/8.0'); self.assertEqual(MAN['notebook_assistance_schema'],'sc-workspace-notebook-assistance/1.0')
  for name in ('sc-workspace-notebook-assistance-v1.schema.json','sc-workspace-notebook-assistance-request-export-v1.schema.json','sc-workspace-notebook-assistance-response-export-v1.schema.json','sc-workspace-notebook-workspace-v6.schema.json','sc-workspace-notebook-export-v6.schema.json','sc-workspace-project-v18.schema.json'): json.loads((ROOT/'schemas'/name).read_text())
 def test_04_grounding_contract(self):
  rn=MAN['research_notebook']; self.assertTrue(rn['assistance_requires_explicit_selection']); self.assertTrue(rn['assistance_question_required']); self.assertTrue(rn['assistance_response_requires_citations']); self.assertTrue(rn['assistance_citation_markers_resolve_to_selected_material']); self.assertTrue(rn['assistance_invalid_citation_markers_rejected']); self.assertTrue(rn['assistance_output_is_reviewable_draft'])
 def test_05_governance(self):
  g=MAN['governance']; self.assertTrue(g['notebook_assistance_explicit_selection_required']); self.assertFalse(g['notebook_assistance_automatic_submission']); self.assertTrue(g['notebook_assistance_citations_required']); self.assertTrue(g['notebook_assistance_invalid_citations_rejected']); self.assertTrue(g['notebook_assistance_response_is_reviewable_draft']); self.assertFalse(g['notebook_assistance_automatic_source_mutation']); self.assertFalse(g['notebook_assistance_automatic_document_materialization'])
 def test_06_helper_surface(self):
  for token in ("ASSISTANCE_SCHEMA='sc-workspace-notebook-assistance/1.0'",'prepareAssistance','assistancePrompt','validateAssistanceResponse','applyAssistanceResponse','exportAssistanceRequest','exportAssistanceResponse','assistancesForRef'): self.assertIn(token,NB)
 def test_07_ui_surface(self):
  for token in ('data-scw-notebook-assistance-form','data-scw-notebook-assistance-material','data-scw-notebook-assistance-list','data-scw-notebook-metric-assistances','Prepare grounded question'): self.assertIn(token,PHP)
  for token in ('renderNotebookAssistance(project)','helper.prepareAssistance','helper.applyAssistanceResponse','Copy grounded prompt','Create Document'): self.assertIn(token,JS)
 def test_08_adapter(self):
  for token in ('sc_workspace_notebook_assistance_request_v1','sc_workspace_notebook_assistance_response_v1','citation marker','citationsLimitedToSelectedMaterial','postMessage'): self.assertIn(token,ADAPTER)
 def test_09_rest_contract(self):
  self.assertIn("'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0'",PHP); self.assertIn("'notebook_assistance_schema' => 'sc-workspace-notebook-assistance/1.0'",PHP); self.assertIn("'grounded_assistance_citations_required' => true",PHP); self.assertIn("'grounded_assistance_automatic_submission' => false",PHP)
 def test_10_history_registry(self):
  self.assertTrue((ROOT/'history/release-manifest-v0.36.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.36.0.json').exists()); self.assertEqual((REG['public_version'],REG['previous_version']),('0.53.0','0.52.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0530'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0360',REGPHP)
if __name__=='__main__': unittest.main()
