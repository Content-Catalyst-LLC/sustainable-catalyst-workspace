import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.5.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.4.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();JS=(P/'assets/js/sc-workspace-lab-integration-v1.js').read_text()
class LabScientificWorkspaceIntegration(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.5.0','1.4.0','Lab & Scientific Workspace Integration'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertIn('/wp-json/sc-workspace/v1/lab-integration-contract',MAN['rest_routes']);self.assertIn("'/lab-integration-contract'",PHP)
 def test_04_features(self): self.assertEqual(len(MAN['lab_integration']['supported_workflows']),8);self.assertTrue(MAN['lab_integration']['traceability_edges_from_selected_context'])
 def test_05_boundaries(self): self.assertFalse(MAN['lab_integration']['automatic_context_upload']);self.assertFalse(MAN['lab_integration']['automatic_return_commit']);self.assertFalse(MAN['lab_integration']['automatic_ai'])
 def test_06_preserved_under_current(self): self.assertIn('Version: 2.0.0',MAIN);self.assertIn('buildContextPackage',JS)
if __name__=='__main__':unittest.main()
