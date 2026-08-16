from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.10.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.9.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.10.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
class ResearchOperations(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.10.0','1.9.0','Workspace Automation & Research Operations'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/research-operations-contract'})
 def test_04_types(self): self.assertEqual(MAN['research_operations']['operation_types'],['saved-search-refresh','source-update-check','watchlist-review','research-queue-review','citation-verification','provenance-review','evidence-refresh','project-maintenance'])
 def test_05_governance(self):
  g=MAN['research_operations']
  for k in ['legacy_research_automation_retained','legacy_routine_import_supported','deterministic_due_planning','blocked_targets_visible','explicit_run_queue','manual_execution_only','schedule_is_declaration','external_freshness_requires_user_action','review_required','receipts_metadata_only','portable_operations_export']: self.assertTrue(g[k])
  for k in ['legacy_routine_auto_migration','background_execution','automatic_network_request','automatic_canonical_mutation','automatic_task_creation','automatic_ai','receipts_contain_project_content','receipts_contain_query_text','receipts_contain_source_urls','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(g[k])
 def test_06_wordpress(self): self.assertIn('Version: 1.15.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '1.15.0'",MAIN);self.assertIn("'/research-operations-contract'",PHP);self.assertIn('Research Operations',PHP);self.assertIn('Schedules are declarations, not a daemon',PHP);self.assertIn('data-release-stage="product-maturity"',PHP)
 def test_07_deployment(self): self.assertIn("PREVIOUS_RELEASE = '1.14.0'",DEP);self.assertIn("ROLLBACK_RELEASE = '1.14.0'",DEP);self.assertIn('workspace-v1.15.0.js',DEP);self.assertIn('class-sc-workspace-research-operations.php',DEP)
 def test_08_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.10.0','1.9.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v1150'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V190',REGPHP)
if __name__=='__main__':unittest.main()
