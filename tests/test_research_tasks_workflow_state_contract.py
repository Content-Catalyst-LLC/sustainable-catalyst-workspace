import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-tasks-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class TestResearchTasksWorkflowState(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 1.11.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['schema_migration_required'])
 def test_03_schemas(self): self.assertEqual(MAN['research_task_schema'],'sc-workspace-research-task/1.0');self.assertEqual(MAN['research_task_library_schema'],'sc-workspace-research-task-library/1.0');self.assertTrue((ROOT/'schemas/sc-workspace-research-task-v1.schema.json').exists())
 def test_04_task_types_states(self): self.assertIn("'verify-claim'",HELP);self.assertIn("'citation-incomplete'",HELP);self.assertIn("'ready-for-synthesis'",HELP);self.assertIn("'blocked'",HELP);self.assertIn("'done'",HELP)
 def test_05_pointer_not_copy(self): self.assertIn('targetFromEntry',HELP);self.assertNotIn('content:clean(e?.content',HELP);self.assertTrue(MAN['governance']['research_tasks_canonical_pointers_only'])
 def test_06_history(self): self.assertIn('historyEvent',HELP);self.assertIn('status-change',HELP);self.assertTrue(MAN['research_tasks']['explicit_history'])
 def test_07_unresolved(self): self.assertIn('unresolved',HELP);self.assertTrue(MAN['governance']['research_tasks_unresolved_references_visible']);self.assertIn('UNRESOLVED TARGET',JS)
 def test_08_ui(self): self.assertIn('data-scw-research-tasks',PHP);self.assertIn('data-scw-task-form',PHP);self.assertIn('data-scw-task-list',PHP);self.assertIn('Workflow state is not research state',PHP)
 def test_09_rest(self): self.assertIn("'/research-tasks-contract'",PHP);self.assertIn('public function research_tasks_contract()',PHP);self.assertIn('/wp-json/sc-workspace/v1/research-tasks-contract',MAN['rest_routes'])
 def test_10_governance(self): self.assertFalse(MAN['governance']['research_tasks_automatic_creation']);self.assertFalse(MAN['governance']['research_tasks_automatic_completion']);self.assertFalse(MAN['governance']['research_tasks_automatic_canonical_mutation']);self.assertFalse(MAN['governance']['research_tasks_automatic_ai'])
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v1110'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0510',REGPHP)
 def test_12_header_retained(self): self.assertEqual(MAN['governance']['editorial_header_rule_px'],4);self.assertRegex(CSS,r'\.scw-editorial-header-bar\{height:4px')
 def test_13_history_retained(self): self.assertTrue((ROOT/'history/release-manifest-v0.51.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.51.0.json').exists())
if __name__=='__main__':unittest.main()
