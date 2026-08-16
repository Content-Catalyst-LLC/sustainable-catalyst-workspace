import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
SEARCH=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-knowledge-search-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class KnowledgeSearchAdvancedRetrieval(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 2.0.1',MAIN)
 def test_02_schema_stable(self):
  prev=json.loads((ROOT/'history/release-manifest-v0.42.0.json').read_text()); self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['schema_stable']); self.assertTrue(prev['migration']['retrieval_only_release']); self.assertFalse(MAN['migration']['canonical_data_rewrite'])
 def test_03_rest_contract(self): self.assertIn('/wp-json/sc-workspace/v1/knowledge-search-contract',MAN['rest_routes']); self.assertIn("'/knowledge-search-contract'",PHP); self.assertIn('public function knowledge_search_contract()',PHP)
 def test_04_fields(self):
  self.assertEqual(MAN['knowledge_search']['fields'],['query','kind','subtype','project','tag','origin','provenance','scope','sort'])
  for token in ('data-scw-retrieval-subtype','data-scw-retrieval-tag','data-scw-retrieval-origin','data-scw-retrieval-provenance','data-scw-retrieval-scope','data-scw-retrieval-sort'): self.assertIn(token,PHP)
 def test_05_saved_searches(self): self.assertEqual(MAN['knowledge_search']['saved_searches'],'browser-local-preferences'); self.assertEqual(MAN['knowledge_search']['max_saved_searches'],40); self.assertIn("STORAGE_KEY='sc_workspace_saved_searches_v1'",SEARCH); self.assertIn('loadSavedKnowledgeSearches',JS); self.assertIn('persistSavedKnowledgeSearches',JS)
 def test_06_ranking(self): self.assertEqual(MAN['knowledge_search']['ranking'],'deterministic-explainable-field-match-plus-recorded-provenance'); self.assertTrue(MAN['knowledge_search']['ranking_reasons_visible']); self.assertFalse(MAN['knowledge_search']['hidden_relevance_score']); self.assertIn('Deterministic retrieval score:',JS); self.assertIn('rank.reasons',JS)
 def test_07_related(self): self.assertIn('function related(target,entries,state)',SEARCH); self.assertIn('same recorded source',SEARCH); self.assertIn('data-scw-related-list',JS); self.assertIn('RELATED MATERIAL',JS)
 def test_08_governance(self):
  g=MAN['governance']; self.assertTrue(g['knowledge_search_derived_from_integrated_index']); self.assertFalse(g['knowledge_search_server_index']); self.assertFalse(g['knowledge_search_semantic_embeddings']); self.assertFalse(g['knowledge_search_automatic_ai']); self.assertFalse(g['knowledge_search_automatic_relationship_inference']); self.assertTrue(g['knowledge_search_saved_searches_local_only']); self.assertFalse(g['knowledge_search_saved_searches_mutate_projects'])
 def test_09_schema_json(self): json.loads((ROOT/'schemas/sc-workspace-knowledge-search-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-saved-search-v1.schema.json').read_text())
 def test_10_presentation(self): self.assertIn('.scw-advanced-retrieval',CSS); self.assertIn('.scw-retrieval-toolbar',CSS); self.assertIn('.scw-related-result',CSS); self.assertIn('@media(forced-colors:active)',CSS)
 def test_11_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0420',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.43.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.43.0.json').exists())
 def test_12_v041_navigation_retained(self): self.assertIn('data-scw-workspace-area="research"',PHP); self.assertIn('sc-workspace-research-navigation-v1.js',PHP); self.assertTrue(all(x in (ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text() for x in ("start:{label:'Home'","projects:{label:'Projects'","research:{label:'Research'","review:{label:'Review'","exchange:{label:'Exchange'")))
if __name__=='__main__': unittest.main()
