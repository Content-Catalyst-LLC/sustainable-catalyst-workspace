import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
XPK=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-cross-project-knowledge-v1.js').read_text()
GRAPH=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-relationship-explorer-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class V048(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 2.0.2',MAIN)
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['grounded_research_assistant_only_release']); self.assertFalse(MAN['migration']['cross_project_knowledge_only_release'])
 def test_03_schemas(self): self.assertEqual(MAN['cross_project_knowledge_schema'],'sc-workspace-cross-project-knowledge/1.0'); self.assertEqual(MAN['cross_project_reference_schema'],'sc-workspace-cross-project-reference/1.0'); self.assertEqual(MAN['cross_project_knowledge_export_schema'],'sc-workspace-cross-project-knowledge-export/1.0')
 def test_04_pointer_only(self): self.assertIn('canonicalSourcePointersOnly:true',XPK); self.assertIn('copiesCanonicalContent:false',XPK); self.assertFalse(MAN['governance']['cross_project_content_copy']); self.assertFalse(MAN['governance']['cross_project_ownership_transfer'])
 def test_05_explicit_target_boundary(self): self.assertIn('explicitTargetProjectRequired:true',XPK); self.assertIn('sameProjectReferencesRejected:true',XPK); self.assertTrue(MAN['governance']['cross_project_same_project_reference_rejected'])
 def test_06_unresolved_visible(self): self.assertIn('unresolvedReferencesRemainVisible:true',XPK); self.assertTrue(MAN['governance']['cross_project_unresolved_references_visible']); self.assertIn('UNRESOLVED',JS)
 def test_07_relations(self):
  for rel in ('references','supports','contrasts','extends','related','informs'): self.assertIn(rel,XPK)
 def test_08_graph_integration(self): self.assertTrue(MAN['knowledge_graph']['includes_cross_project_references']); self.assertIn("source:'cross-project-knowledge-reference'",GRAPH); self.assertIn('crossProjectReferences:',JS)
 def test_09_ui(self): self.assertIn('CROSS-PROJECT KNOWLEDGE',PHP); self.assertIn('data-scw-cross-project-target',PHP); self.assertIn('Reference selected research',PHP); self.assertIn('data-scw-cross-project-list',PHP)
 def test_10_export_import(self): self.assertIn('EXPORT_SCHEMA',XPK); self.assertIn('exportPackage',XPK); self.assertIn('verifyPackage',XPK); self.assertIn('data-scw-cross-project-export',PHP); self.assertIn('data-scw-cross-project-import',PHP)
 def test_11_governance(self): self.assertFalse(MAN['governance']['cross_project_automatic_relationship_inference']); self.assertFalse(MAN['governance']['cross_project_automatic_canonical_mutation']); self.assertFalse(MAN['governance']['cross_project_automatic_ai']); self.assertIn('.scw-editorial-header-bar{height:4px',CSS)
 def test_12_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v202'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0470',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.47.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.47.0.json').exists())
if __name__=='__main__': unittest.main()
