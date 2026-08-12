import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
FEATURE=json.loads((ROOT/'history/release-manifest-v0.49.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
TPL=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-templates-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class V049Templates(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version']),('0.66.0','0.65.0')); self.assertIn('Version: 0.73.0',MAIN); self.assertEqual((FEATURE['version'],FEATURE['release_name']),('0.49.0','Research Templates & Reusable Workflows'))
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(FEATURE['migration']['research_templates_only_release'])
 def test_03_template_schemas(self): self.assertEqual(MAN['research_template_library_schema'],'sc-workspace-research-template-library/1.0'); self.assertEqual(MAN['research_template_schema'],'sc-workspace-research-template/1.0'); self.assertEqual(MAN['research_template_export_schema'],'sc-workspace-research-template-export/1.0')
 def test_04_eight_builtins(self):
  self.assertEqual(MAN['research_templates']['built_in_count'],8)
  for title in ('Research Protocol','Literature Review','Evidence Review Protocol','Decision Workflow','Systems Inquiry','Publication Workflow','Rapid Research Assessment','Source Validation Protocol'): self.assertIn(title,TPL)
 def test_05_structure_only_capture(self):
  self.assertIn('templateFromWorkflow',TPL); self.assertIn('copiesProjectContent:false',TPL); self.assertIn('copiesNotebookContent:false',TPL); self.assertIn('copiesFindings:false',TPL); self.assertIn('copiesCompletionStatus:false',TPL)
  for token in ('note','objectIds','status','completedAt'): self.assertNotIn(f'{token}:s.{token}',TPL)
 def test_06_explicit_instantiation(self): self.assertIn('data-scw-research-template-apply',PHP); self.assertIn('Apply structure to this project',PHP); self.assertIn('Create project starter',PHP); self.assertIn('explicitInstantiationRequired:true',TPL); self.assertFalse(MAN['research_templates']['automatic_instantiation'])
 def test_07_notebook_and_workflow_scaffolds(self): self.assertIn('helper.createNotebook',JS); self.assertIn('helper.createSection',JS); self.assertIn("id('wr')",JS); self.assertIn('Notebook scaffold',PHP); self.assertIn('Guided workflow',PHP)
 def test_08_optional_empty_objects(self): self.assertIn('Empty starter objects',PHP); self.assertIn('objectTemplate(spec.type,spec.title)',JS); self.assertTrue(MAN['research_templates']['optional_empty_starter_objects'])
 def test_09_portable_custom_templates(self): self.assertIn('exportPackage',TPL); self.assertIn('verifyPackage',TPL); self.assertIn('workspace-research-templates.json',JS); self.assertIn('fingerprint',TPL)
 def test_10_rest_contract(self): self.assertIn("'/research-templates-contract'",PHP); self.assertIn('public function research_templates_contract()',PHP); self.assertIn('/wp-json/sc-workspace/v1/research-templates-contract',MAN['rest_routes'])
 def test_11_governance_and_header(self): self.assertFalse(MAN['governance']['research_templates_store_project_content']); self.assertFalse(MAN['governance']['research_templates_store_findings']); self.assertFalse(MAN['governance']['research_templates_automatic_ai']); self.assertIn('.scw-editorial-header-bar{height:4px',CSS)
 def test_12_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0730'",REGPHP); self.assertIn("LEGACY_PENDING_KEY_V0490 = 'sc_workspace_registry_pending_v0490'",REGPHP); self.assertTrue((ROOT/'history/workspace-product-record-v0.49.0.json').exists())
if __name__=='__main__': unittest.main()
