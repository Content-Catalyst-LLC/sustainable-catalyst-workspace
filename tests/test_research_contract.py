import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.56.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
class ResearchContractTests(unittest.TestCase):
    def test_schema_vocabularies(self):
        s=json.loads((ROOT/'schemas/sc-workspace-research-v1.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-research/1.0')
        self.assertEqual(s['properties']['questions']['maxItems'],100); self.assertEqual(s['properties']['claims']['maxItems'],100)
        self.assertEqual(s['properties']['readingQueue']['maxItems'],250); self.assertEqual(s['properties']['evidenceLinks']['maxItems'],500)
    def test_project_embeds_research(self):
        s=json.loads((ROOT/'schemas/sc-workspace-project-v4.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-project/4.0'); self.assertIn('research',s['required'])
        self.assertEqual(s['properties']['research']['$ref'],'sc-workspace-research-v1.schema.json')
    def test_research_functions_present(self):
        js=JS.read_text()
        for token in ('function researchTemplate','function normalizeResearch','function renderResearch','data-scw-research-question-form','data-scw-research-source-form','data-scw-research-evidence-form','data-scw-research-claim-form','data-scw-research-link-evidence','evidenceObjectIds','evidenceLinks','readingQueue'):
            self.assertIn(token,js)
    def test_research_ui_present(self):
        php=PHP.read_text()
        for token in ('RESEARCH WORKSPACE','Research questions','Capture & reading queue','Extract evidence','Claims & evidence','Research Librarian','Knowledge Library'):
            self.assertIn(token,php)
    def test_privacy_minimized_handoff(self):
        js=JS.read_text()
        for forbidden in ("searchParams.set('sc_workspace_question'","searchParams.set('sc_workspace_claim'","searchParams.set('sc_workspace_evidence'","searchParams.set('sc_workspace_source_title'"):
            self.assertNotIn(forbidden,js)
        self.assertIn("target.searchParams.set('sc_workspace_project', project.id)",js)
        self.assertIn("target.searchParams.set('sc_workspace_object', object.id)",js)
if __name__=='__main__': unittest.main()
