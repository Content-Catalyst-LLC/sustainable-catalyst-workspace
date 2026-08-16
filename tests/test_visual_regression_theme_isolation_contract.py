from pathlib import Path
import json, unittest
R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
M=json.loads((R/'release-manifest-v2.0.4.json').read_text())
OLD=json.loads((R/'release-manifest-v2.0.3.json').read_text())
MAIN=(P/'sustainable-catalyst-workspace.php').read_text()
W=(P/'includes/class-sc-workspace.php').read_text()
D=(P/'includes/class-sc-workspace-deployment.php').read_text()
CSS=(P/'assets/css/workspace-v2.0.4.css').read_text()
V=(P/'includes/class-sc-workspace-visual-regression.php').read_text()
class VisualRegressionThemeIsolationContract(unittest.TestCase):
    def test_release_identity_and_schema_freeze(self):
        self.assertEqual((M['version'],M['previous_version']),('2.0.4','2.0.3'))
        self.assertEqual((M['storage_schema_version'],M['project_schema'],M['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
    def test_render_matrix_and_boundaries(self):
        x=M['visual_regression_theme_isolation']
        self.assertEqual(x['viewport_matrix_px'],[1440,1024,768,390])
        self.assertTrue(x['hostile_theme_fixture'])
        self.assertTrue(x['no_horizontal_overflow_required'])
        self.assertTrue(x['button_theme_isolation_required'])
        self.assertFalse(x['schema_migration_required'])
    def test_live_runtime_and_deployment_identity(self):
        self.assertIn('Version: 2.0.4',MAIN)
        self.assertIn("SC_WORKSPACE_VERSION', '2.0.4'",MAIN)
        self.assertIn("PREVIOUS_RELEASE = '2.0.3'",D)
        self.assertIn('workspace-v2.0.4.js',D); self.assertIn('workspace-v2.0.4.css',D)
        self.assertIn('data-release-stage="visual-regression-theme-isolation"',W)
        self.assertIn("'/visual-regression-contract'",W)
    def test_css_theme_isolation_contract(self):
        for marker in ['/* v2.0.4 — Visual Regression, Theme Isolation & Cross-Viewport Hardening */','overflow-x:clip','background:#fff!important','grid-template-columns:1fr!important','grid-template-columns:repeat(2,minmax(0,1fr))!important']:
            self.assertIn(marker,CSS)
        self.assertIn('sc-workspace-visual-regression/2.0',V)
if __name__=='__main__': unittest.main()
