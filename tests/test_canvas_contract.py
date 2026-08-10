import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.35.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'

class CanvasContractTests(unittest.TestCase):
    def test_canvas_schema(self):
        s=json.loads((ROOT/'schemas/sc-workspace-canvas-v1.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-canvas/1.0')
        self.assertEqual(s['properties']['boards']['maxItems'],30)
        self.assertEqual(s['properties']['nodes']['maxItems'],500)
        self.assertEqual(s['properties']['edges']['maxItems'],1000)
        self.assertEqual(s['properties']['frames']['maxItems'],100)
    def test_project_embeds_canvas(self):
        s=json.loads((ROOT/'schemas/sc-workspace-project-v6.schema.json').read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-project/6.0')
        self.assertIn('canvas',s['required'])
        self.assertEqual(s['properties']['canvas']['$ref'],'sc-workspace-canvas-v1.schema.json')
    def test_canvas_functions(self):
        js=JS.read_text()
        for token in ('function canvasTemplate','function normalizeCanvas','function renderCanvas','function touchCanvas','function cleanCanvasReferences','function removeCanvasNode','const CANVAS_SCHEMA'):
            self.assertIn(token,js)
    def test_canvas_ui(self):
        php=PHP.read_text()
        for token in ('CANVAS &amp; STRUCTURED THINKING','Thinking boards','Structured canvas','Typed relationships','Group meaning','Capture synthesis'):
            self.assertIn(token,php)
    def test_canvas_endpoint_and_handoff(self):
        php=PHP.read_text(); js=JS.read_text()
        self.assertIn("'/canvas-contract'",php); self.assertIn("'canvas_schema' => 'sc-workspace-canvas/1.0'",php)
        self.assertIn("target.searchParams.set('sc_workspace_canvas', activeBoard.id)",js)
        for forbidden in ("searchParams.set('sc_workspace_canvas_node'","searchParams.set('sc_workspace_canvas_body'","searchParams.set('sc_workspace_canvas_frame'"):
            self.assertNotIn(forbidden,js)
    def test_synthesis_creates_document_object(self):
        js=JS.read_text(); self.assertIn("objectTemplate('document',`${board.title} — Canvas synthesis`)",js); self.assertIn("obj.provenance.sourceTitle='Workspace Canvas'",js)
if __name__=='__main__': unittest.main()
