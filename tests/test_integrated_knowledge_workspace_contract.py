import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.46.1.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.46.1.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.46.1.js').read_text()
IK=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-integrated-knowledge-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.46.1.css').read_text()
class IntegratedKnowledgeWorkspace(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.46.1','0.46.0','Workspace Import & Interchange')); self.assertIn('Version: 0.46.1',MAIN)
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['schema_stable']); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged'])
 def test_03_contract(self): self.assertIn('/wp-json/sc-workspace/v1/integrated-knowledge-contract',MAN['rest_routes']); self.assertIn("'/integrated-knowledge-contract'",PHP); self.assertIn('public function integrated_knowledge_contract()',PHP); self.assertIn("'derived_from_canonical_records' => true",PHP); self.assertIn("'duplicates_canonical_content' => false",PHP)
 def test_04_schemas(self): self.assertEqual(MAN['integrated_knowledge_schema'],'sc-workspace-integrated-knowledge/1.0'); self.assertEqual(MAN['integrated_knowledge_ref_schema'],'sc-workspace-integrated-knowledge-ref/1.0'); json.loads((ROOT/'schemas/sc-workspace-integrated-knowledge-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-integrated-knowledge-ref-v1.schema.json').read_text())
 def test_05_derived_index(self):
  for token in ("kind:'object'","kind:'notebook'","kind:'notebook-block'","kind:'research-question'","kind:'research-claim'",'function derive(state)','function filter(entries,prefs={})','function connections(target,state)'): self.assertIn(token,IK)
 def test_06_governance(self):
  g=MAN['governance']; self.assertTrue(g['integrated_knowledge_derived']); self.assertFalse(g['integrated_knowledge_duplicates_canonical_content']); self.assertFalse(g['integrated_knowledge_automatic_semantic_inference']); self.assertFalse(g['integrated_knowledge_automatic_ai']); self.assertFalse(g['integrated_knowledge_automatic_mutation']); self.assertTrue(g['canonical_origin_handoff'])
 def test_07_ui(self):
  for token in ('data-scw-workspace-view="research"','INTEGRATED KNOWLEDGE WORKSPACE','data-scw-integrated-search','data-scw-integrated-results','data-scw-integrated-detail','data-scw-integrated-open-notebook','data-scw-integrated-open-knowledge'): self.assertIn(token,PHP)
  self.assertIn("workspaceView === 'research'",JS); self.assertIn('renderIntegratedKnowledge()',JS); self.assertIn('openIntegratedEntry(entry)',JS); self.assertIn('.scw-integrated-knowledge{',CSS)
 def test_08_specialized_surfaces_retained(self): self.assertIn('data-scw-workspace-view="notebook"',PHP); self.assertIn('data-scw-workspace-view="knowledge"',PHP); self.assertIn('data-scw-workspace-section="notebook"',PHP); self.assertIn('data-scw-workspace-section="knowledge"',PHP)
 def test_09_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.46.1','0.46.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0461'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0400',REGPHP)
 def test_10_history(self): self.assertTrue((ROOT/'history/release-manifest-v0.40.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.40.0.json').exists())
if __name__=='__main__': unittest.main()
