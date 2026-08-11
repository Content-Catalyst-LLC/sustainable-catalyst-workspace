import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN = (ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
CSS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.59.1.css').read_text()
JS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-focused-shell-v1.js').read_text()
MAN = json.loads((ROOT / 'release-manifest-v0.59.1.json').read_text())
REG = json.loads((ROOT / 'registry/workspace-product-record-v0.59.1.json').read_text())

class FocusedApplicationShellContract(unittest.TestCase):
    def test_release_lineage(self):
        self.assertEqual((MAN['version'], MAN['previous_version'], MAN['release_name']), ('0.59.1', '0.59.0', 'Focused Application Shell & Route Isolation'))

    def test_schema_stable(self):
        self.assertEqual(MAN['storage_schema_version'], 35)
        self.assertEqual(MAN['project_schema'], 'sc-workspace-project/20.0')
        self.assertFalse(MAN['focused_application_shell']['schema_migration'])

    def test_plugin_version(self):
        self.assertIn('Version: 0.59.1', MAIN)
        self.assertIn("define('SC_WORKSPACE_VERSION', '0.59.1');", MAIN)

    def test_current_assets(self):
        self.assertIn('assets/css/workspace-v0.59.1.css', PHP)
        self.assertIn('assets/js/workspace-v0.59.1.js', PHP)
        self.assertIn('assets/js/sc-workspace-focused-shell-v1.js', PHP)

    def test_top_level_hidden_enforcement(self):
        self.assertIn('[data-scw-workspace-section][hidden]', CSS)
        self.assertIn('display:none!important', CSS)

    def test_research_tool_navigation(self):
        self.assertIn('data-scw-research-tool-nav', PHP)
        for surface in ('overview','search','collections','cross-project','tasks','assistant','citations','composition'):
            self.assertIn(f'data-scw-research-surface="{surface}"', PHP)

    def test_research_panels_are_isolated(self):
        for surface in ('search','collections','cross-project','tasks','assistant','citations','composition'):
            self.assertIn(f'data-scw-research-surface-panel="{surface}"', PHP)
        self.assertIn('one_research_surface_visible_at_a_time', json.dumps(MAN))

    def test_default_overview(self):
        self.assertEqual(MAN['focused_application_shell']['research_default_surface'], 'overview')
        self.assertIn('data-scw-research-surface-panel="overview"', PHP)

    def test_selection_context_not_migrated(self):
        self.assertTrue(MAN['focused_application_shell']['selected_research_context_preserved'])
        self.assertFalse(MAN['focused_application_shell']['canonical_mutation'])

    def test_four_px_header_retained(self):
        self.assertTrue(MAN['focused_application_shell']['four_px_editorial_header_retained'])
        self.assertIn('border-top:4px solid #000', CSS)

    def test_focused_shell_module_contract(self):
        self.assertIn("sc-workspace-focused-shell/1.0", JS)
        self.assertIn("const SURFACES=['overview','search','collections','cross-project','tasks','assistant','citations','composition']", JS)
        self.assertIn('visibilityPlan', JS)

    def test_registry_lineage(self):
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0591'", REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0590', REGPHP)
        self.assertEqual(REG['public_version'], '0.59.1')
        self.assertEqual(REG['previous_version'], '0.59.0')

    def test_v059_history_retained(self):
        self.assertTrue((ROOT/'history/release-manifest-v0.59.0.json').exists())
        self.assertTrue((ROOT/'history/workspace-product-record-v0.59.0.json').exists())

if __name__ == '__main__':
    unittest.main()
