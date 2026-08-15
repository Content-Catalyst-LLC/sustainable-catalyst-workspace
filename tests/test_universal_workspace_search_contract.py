import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
class UniversalWorkspaceSearchContractTests(unittest.TestCase):
 def setUp(self):
  self.cur=json.loads((R/'history/release-manifest-v1.2.0.json').read_text())
  self.old=json.loads((R/'history/release-manifest-v1.1.0.json').read_text())
  self.reg=json.loads((R/'history/workspace-product-record-v1.2.0.json').read_text())
  self.main=(P/'sustainable-catalyst-workspace.php').read_text()
  self.workspace=(P/'includes/class-sc-workspace.php').read_text()
  self.us=(P/'includes/class-sc-workspace-universal-search.php').read_text()
  self.js=(P/'assets/js/sc-workspace-universal-search-v1.js').read_text()
  self.app=(P/'assets/js/workspace-v1.9.0.js').read_text()
  self.dep=(P/'includes/class-sc-workspace-deployment.php').read_text()
  self.prod=(P/'includes/class-sc-workspace-production-certification.php').read_text()
  self.regphp=(P/'includes/class-sc-workspace-registry.php').read_text()
 def test_release_identity_and_freeze(self):
  self.assertEqual((self.cur['version'],self.cur['previous_version'],self.cur['release_name']),('1.2.0','1.1.0','Universal Workspace Search & Knowledge Retrieval'))
  for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:
   self.assertEqual(self.cur[k],self.old[k])
  self.assertEqual(self.cur['object_types'],self.old['object_types']);self.assertFalse(self.cur['schema_migration_required'])
 def test_only_universal_search_route_added(self):
  self.assertEqual(set(self.cur['rest_routes'])-set(self.old['rest_routes']),{'/wp-json/sc-workspace/v1/universal-search-contract'})
 def test_governance_and_corpus(self):
  u=self.cur['universal_search']; expected={'project','object','notebook','notebook-block','research-question','research-claim','analysis-question','decision','briefing-draft','citation-reference','research-task'}
  self.assertEqual(set(u['corpus']),expected);self.assertTrue(u['derived_from_local_records']);self.assertTrue(u['browser_local_index']);self.assertTrue(u['cross_project']);self.assertTrue(u['deterministic_explainable_ranking']);self.assertTrue(u['ranking_reasons_visible']);self.assertTrue(u['canonical_origin_links']);self.assertTrue(u['saved_searches_reused']);self.assertTrue(u['citation_library_included']);self.assertTrue(u['research_tasks_included'])
  for k in ['server_index','semantic_embeddings','automatic_ai','automatic_semantic_inference','automatic_canonical_mutation','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(u[k])
 def test_wordpress_runtime_integration(self):
  self.assertIn('Version: 1.9.0',self.main);self.assertIn("define('SC_WORKSPACE_VERSION', '1.9.0')",self.main);self.assertIn('class-sc-workspace-universal-search.php',self.main)
  self.assertIn("'/universal-search-contract'",self.workspace);self.assertIn('universal_search_contract',self.workspace);self.assertIn('sc-workspace-universal-search-v1',self.workspace);self.assertIn("'sc-workspace-v190'",self.workspace);self.assertIn('workspace-v1.9.0.js',self.workspace);self.assertIn('workspace-v1.9.0.css',self.workspace);self.assertIn('data-release-stage="institutional-audit-studio"',self.workspace)
  self.assertIn('sc-workspace-universal-search-contract/1.0',self.us);self.assertIn('sc-workspace-universal-search/1.0',self.us)
 def test_universal_search_ui_and_routes(self):
  surface=self.workspace+self.app
  for token in ['UNIVERSAL WORKSPACE SEARCH','Find the work, not the subsystem.','Search Workspace','data-scw-cockpit-universal-search','analysis-question','briefing-draft','citation-reference','research-task','openUniversalEntry','No local Workspace records match these retrieval fields.']: self.assertIn(token,surface)
 def test_release_engineering_identity(self):
  self.assertIn("PREVIOUS_RELEASE = '1.8.0'",self.dep);self.assertIn("ROLLBACK_RELEASE = '1.8.0'",self.dep);self.assertIn('workspace-v1.9.0.js',self.dep);self.assertIn('workspace-v1.9.0.css',self.dep)
  self.assertIn("PREVIOUS_RELEASE = '1.8.0'",self.prod);self.assertIn("ROLLBACK_RELEASE = '1.8.0'",self.prod);self.assertIn('workspace-v1.9.0.js',self.prod);self.assertIn('workspace-v1.9.0.css',self.prod)
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v190'",self.regphp);self.assertIn('LEGACY_PENDING_KEY_V110',self.regphp)
  self.assertEqual((self.reg['public_version'],self.reg['previous_version'],self.reg['release_name'],self.reg['lifecycle_state'],self.reg['release_channel']),('1.2.0','1.1.0','Universal Workspace Search & Knowledge Retrieval','production','stable'))
 def test_history_preserved(self):
  self.assertTrue((R/'history/release-manifest-v1.1.0.json').exists());self.assertTrue((R/'history/workspace-product-record-v1.1.0.json').exists())
if __name__=='__main__': unittest.main()
