import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text();EXP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-relationship-explorer-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class V047(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.67.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertFalse(MAN['schema_migration_required']);self.assertFalse(MAN['migration']['relationship_explorer_only_release']);self.assertTrue(MAN['migration']['grounded_research_assistant_only_release'])
 def test_03_graph_v2(self): self.assertEqual(MAN['knowledge_graph_schema'],'sc-workspace-knowledge-graph/2.0');self.assertIn("'schema' => 'sc-workspace-knowledge-graph-contract/2.0'",PHP);self.assertIn("'relationship_explorer_schema' => 'sc-workspace-relationship-explorer/1.0'",PHP)
 def test_04_nodes(self):
  for x in ('notebook','notebook-block','research-question','research-claim','reference','synthesis'): self.assertIn(x,MAN['knowledge_graph']['node_types']);self.assertIn(x,EXP)
 def test_05_relations(self):
  for x in ('references','supports','contrasts','extends','related','promoted-to','synthesized-into','cited-as','supports-claim','captured-from'): self.assertIn(x,MAN['knowledge_graph']['relationship_types']);self.assertIn(x,EXP)
 def test_06_no_inference(self): self.assertFalse(MAN['knowledge_graph']['semantic_embeddings']);self.assertFalse(MAN['knowledge_graph']['server_graph_database']);self.assertFalse(MAN['knowledge_graph']['hidden_relationship_inference']);self.assertFalse(MAN['knowledge_graph']['automatic_semantic_similarity_edges'])
 def test_07_runtime_helper(self): self.assertIn('SCWorkspaceRelationshipExplorer',EXP);self.assertIn('function build(state,options={})',EXP);self.assertIn('relationshipExplorer.build(state',JS)
 def test_08_notebook_lineage(self): self.assertIn("source:'explicit-notebook-link'",EXP);self.assertIn("source:'notebook-promotion'",EXP);self.assertIn("source:'notebook-synthesis-selection'",EXP)
 def test_09_citation_origins(self): self.assertTrue(MAN['knowledge_graph']['includes_citation_origins']);self.assertIn("source:'citation-library-origin'",EXP)
 def test_10_ui(self): self.assertIn('RESEARCH GRAPH &amp; RELATIONSHIP EXPLORER',PHP);self.assertIn('Citation references',PHP);self.assertIn('Synthesized into',PHP)
 def test_11_visual_patch_retained(self): self.assertIn('.scw-editorial-header-bar{height:4px',CSS)
 def test_12_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0670'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0461',REGPHP)
if __name__=='__main__':unittest.main()
