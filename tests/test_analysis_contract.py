import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.5.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
class AnalysisContractTests(unittest.TestCase):
    def test_analysis_schema(self):
        s=json.loads((ROOT/'schemas/sc-workspace-analysis-v1.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-analysis/1.0')
        self.assertEqual(s['properties']['questions']['maxItems'],100)
        self.assertEqual(s['properties']['variables']['maxItems'],120)
        self.assertEqual(s['properties']['findings']['maxItems'],150)
    def test_project_embeds_analysis(self):
        s=json.loads((ROOT/'schemas/sc-workspace-project-v4.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-project/4.0')
        self.assertIn('analysis',s['required'])
        self.assertEqual(s['properties']['analysis']['$ref'],'sc-workspace-analysis-v1.schema.json')
    def test_analysis_functions_present(self):
        js=JS.read_text()
        for token in ('function analysisTemplate','function normalizeAnalysis','function renderAnalysis','function touchAnalysis','function cleanAnalysisReferences',"objectTemplate('dataset',title)","objectTemplate('analysis',name)"):
            self.assertIn(token,js)
    def test_analysis_ui_present(self):
        php=PHP.read_text()
        for token in ('ANALYSIS WORKSPACE','Analysis questions','Datasets &amp; variables','Assumptions &amp; methods','Comparisons &amp; findings','Analytics R','Workbench','Catalyst Data','Site Intelligence'):
            self.assertIn(token,php)
    def test_analysis_endpoint(self):
        php=PHP.read_text(); self.assertIn("'/analysis-contract'",php); self.assertIn("'analysis_schema' => 'sc-workspace-analysis/1.0'",php)
    def test_privacy_minimized_analysis_handoff(self):
        js=JS.read_text()
        for forbidden in ("searchParams.set('sc_workspace_analysis_question'","searchParams.set('sc_workspace_variable'","searchParams.set('sc_workspace_assumption'","searchParams.set('sc_workspace_finding'"):
            self.assertNotIn(forbidden,js)
