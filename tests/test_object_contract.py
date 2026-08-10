import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.34.0.js'
class ObjectTests(unittest.TestCase):
    def test_object_contract_stable(self):
        s=json.loads((ROOT/'schemas/sc-workspace-object-v1.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-object/1.0')
        self.assertEqual(s['properties']['type']['enum'],['source','evidence','dataset','analysis','decision','document','export'])
    def test_research_uses_object_ids(self):
        js=JS.read_text(); self.assertIn("objectTemplate('source', title)",js); self.assertIn("objectTemplate('evidence', title)",js); self.assertIn('sourceObjectId',js); self.assertIn('evidenceObjectId',js)
    def test_delete_cleans_cross_workspace_refs(self):
        js=JS.read_text(); self.assertIn('function cleanResearchReferences',js); self.assertIn('cleanResearchReferences(project, object.id)',js); self.assertIn('function cleanAnalysisReferences',js); self.assertIn('cleanAnalysisReferences(project, object.id)',js); self.assertIn('cleanDecisionReferences(project, object.id)',js); self.assertIn('cleanCanvasReferences(project, object.id)',js)
if __name__=='__main__': unittest.main()
