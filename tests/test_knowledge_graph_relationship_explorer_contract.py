import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.4.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.3.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();JS=(P/'assets/js/sc-workspace-relationship-explorer-v2.js').read_text()
class KnowledgeGraphRelationshipExplorer(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.4.0','1.3.0','Knowledge Graph & Relationship Explorer'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertIn('/wp-json/sc-workspace/v1/knowledge-graph-explorer-contract',MAN['rest_routes']);self.assertIn("'/knowledge-graph-explorer-contract'",PHP)
 def test_04_features(self):
  g=MAN['knowledge_graph_explorer'];self.assertTrue(g['explicit_path_tracing']);self.assertTrue(g['incoming_outgoing_backlink_ledger']);self.assertTrue(g['portable_graph_snapshot_export']);self.assertEqual(g['max_path_depth'],5)
 def test_05_boundaries(self):
  g=MAN['knowledge_graph_explorer'];self.assertFalse(g['server_graph_database']);self.assertFalse(g['semantic_embeddings']);self.assertFalse(g['automatic_relationship_inference']);self.assertFalse(g['automatic_ai']);self.assertFalse(g['canonical_records_mutated'])
 def test_06_library(self): self.assertIn('library-record',MAN['knowledge_graph_explorer']['node_families']);self.assertIn('originates-in-library',JS)
 def test_07_preserved_under_current(self): self.assertIn('Version: 1.10.0',MAIN);self.assertTrue((R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-relationship-explorer-v2.js').exists())
if __name__=='__main__':unittest.main()
