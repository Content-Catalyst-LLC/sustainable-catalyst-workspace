import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.9.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
class DecisionContractTests(unittest.TestCase):
    def test_decision_schema(self):
        s=json.loads((ROOT/'schemas/sc-workspace-decision-v1.schema.json').read_text()); self.assertEqual(s['properties']['schema']['const'],'sc-workspace-decision/1.0'); self.assertEqual(s['properties']['decisions']['maxItems'],60); self.assertEqual(s['properties']['assessments']['maxItems'],1000)
    def test_project_embeds_decision(self):
        s=json.loads((ROOT/'schemas/sc-workspace-project-v6.schema.json').read_text()); self.assertEqual(s['properties']['schema']['const'],'sc-workspace-project/6.0'); self.assertIn('decision',s['required']); self.assertEqual(s['properties']['decision']['$ref'],'sc-workspace-decision-v1.schema.json')
    def test_decision_functions_present(self):
        js=JS.read_text();
        for token in ('function decisionTemplate','function normalizeDecision','function renderDecision','function touchDecision','function cleanDecisionReferences',"objectTemplate('decision',title)"): self.assertIn(token,js)
    def test_decision_ui_present(self):
        php=PHP.read_text();
        for token in ('DECISION WORKSPACE','Decision records','Options &amp; criteria','Option assessments','Risks &amp; decision record','Decision Studio','Catalyst Canvas'): self.assertIn(token,php)
    def test_decision_endpoint(self):
        php=PHP.read_text(); self.assertIn("'/decision-contract'",php); self.assertIn("'decision_schema' => 'sc-workspace-decision/1.0'",php)
    def test_privacy_minimized_decision_handoff(self):
        js=JS.read_text();
        for forbidden in ("searchParams.set('sc_workspace_decision'","searchParams.set('sc_workspace_option'","searchParams.set('sc_workspace_rationale'"): self.assertNotIn(forbidden,js)
if __name__=='__main__': unittest.main()
