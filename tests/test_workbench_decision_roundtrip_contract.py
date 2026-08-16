import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.6.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.5.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.6.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();APP=(P/'assets/js/sc-workspace-workbench-decision-roundtrip-v1.js').read_text()
class WorkbenchDecisionRoundtrip(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.6.0','1.5.0','Workbench & Decision Studio Round-Trip Workflows'))
 def test_02_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.6.0','1.5.0'))
 def test_03_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_04_route(self): self.assertIn('/wp-json/sc-workspace/v1/workbench-decision-roundtrip-contract',MAN['rest_routes']);self.assertIn("'/workbench-decision-roundtrip-contract'",PHP)
 def test_05_features(self): self.assertEqual(len(MAN['tool_roundtrip_integration']['workbench_workflows']),6);self.assertEqual(len(MAN['tool_roundtrip_integration']['decision_studio_workflows']),6);self.assertTrue(MAN['tool_roundtrip_integration']['destination_match_required'])
 def test_06_boundaries(self): self.assertFalse(MAN['tool_roundtrip_integration']['automatic_context_upload']);self.assertFalse(MAN['tool_roundtrip_integration']['automatic_return_commit']);self.assertFalse(MAN['tool_roundtrip_integration']['automatic_ai'])
 def test_07_preserved_under_current(self): self.assertIn('Version: 1.14.0',MAIN);self.assertIn('buildContextPackage',APP);self.assertIn('toWorkspaceReturnPacket',APP)
if __name__=='__main__':unittest.main()
