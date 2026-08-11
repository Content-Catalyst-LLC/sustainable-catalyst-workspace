import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.65.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.65.0.css'
MANIFEST=ROOT/'release-manifest-v0.65.0.json'
class KnowledgeGraphContract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.65.0');self.assertEqual(m['previous_version'],'0.64.1');self.assertEqual(m['storage_schema_version'],35);self.assertEqual(m['project_schema'],'sc-workspace-project/20.0');self.assertEqual(m['knowledge_graph_schema'],'sc-workspace-knowledge-graph/2.0')
 def test_graph_schema(self):
  s=json.loads((ROOT/'schemas/sc-workspace-knowledge-graph-v2.schema.json').read_text());self.assertEqual(s['properties']['schema']['const'],'sc-workspace-knowledge-graph/2.0')
 def test_graph_engine(self):
  j=JS.read_text();self.assertIn('function buildKnowledgeGraph()',j);self.assertIn('function graphNeighborhood',j);self.assertIn('MAX_GRAPH_NODES = 1600',j)
 def test_node_types(self):
  p=PHP.read_text();self.assertIn("'project','provenance','source','evidence','dataset','analysis','decision','document','export'",p)
 def test_relationships(self):
  j=JS.read_text();
  for x in ('contains','sourced-from','same-source','evidence-from','uses','informs','supports','contradicts','derived-from','produced-by','supersedes','cites'): self.assertIn("'"+x+"'",j)
 def test_no_embeddings(self):
  m=json.loads(MANIFEST.read_text());self.assertFalse(m['knowledge_graph']['semantic_embeddings']);self.assertFalse(m['knowledge_graph']['server_graph_database']);self.assertFalse(m['knowledge_graph']['server_search_index'])
 def test_no_hidden_inference(self):
  self.assertFalse(json.loads(MANIFEST.read_text())['knowledge_graph']['hidden_relationship_inference'])
 def test_storage_migration(self):
  j=JS.read_text();self.assertIn('const STORAGE_VERSION = 35',j);self.assertIn('function migrateV16(raw)',j);self.assertIn('if (raw.schemaVersion === 16) return migrateV16(raw)',j);self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/20.0'",j)
 def test_ui(self):
  p=PHP.read_text();self.assertIn('data-scw-workspace-view="graph"',p);self.assertIn('RESEARCH GRAPH &amp; RELATIONSHIP EXPLORER',p);self.assertIn('data-scw-graph-svg',p)
 def test_accessible_parallel_relationships(self):
  p=PHP.read_text();self.assertIn('Why this node is connected',p);self.assertIn('aria-label="Focused Workspace knowledge graph neighborhood"',p)
 def test_style(self):
  c=CSS.read_text();self.assertIn('.scw-knowledge-graph{',c);self.assertIn('.scw-graph-node.is-focus circle',c)
 def test_library_route(self):
  self.assertIn("home_url('/knowledge-libraries/')",PHP.read_text())
if __name__=='__main__': unittest.main()
