import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.8.2.css'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.8.2.js'
PLATFORM=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php'
class PublicExperienceTests(unittest.TestCase):
    def test_public_hero_is_simplified(self):
        t=PHP.read_text()
        self.assertIn('<h1>Research. Analyze. Decide.</h1>',t)
        self.assertNotIn('<h1>Research. Analyze. Decide. Move the work.</h1>',t)
        self.assertIn('scw-platform-bridge',t)
        self.assertNotIn('scw-platform-principles',t)
    def test_project_mode_navigation(self):
        p=PHP.read_text(); j=JS.read_text()
        for mode in ('overview','research','analysis','decision','canvas','objects'):
            self.assertIn(f'data-scw-project-mode="{mode}"',p)
            self.assertIn(f'data-scw-project-panel="{mode}"',p)
        self.assertIn('function setProjectMode(mode)',j)
        self.assertIn("root.classList.add('scw-mode-enabled')",j)
    def test_technical_controls_progressively_disclosed(self):
        t=PHP.read_text()
        self.assertIn('scw-settings-drawer',t)
        self.assertIn('scw-connections-drawer',t)
        self.assertIn('Storage &amp; identity',t)
        self.assertIn('Tools, returns &amp; handoff history',t)
    def test_visual_system_is_light_institutional(self):
        t=CSS.read_text()
        self.assertIn('v0.8.2 — Workspace Interface Refinement & Public Experience',t)
        self.assertIn('background:#f4f4f1',t)
        self.assertIn('background:#fff',t)
        self.assertIn('--scw-accent:#ff0000',t)
        self.assertIn('.scw-project-mode-nav',t)
    def test_platform_contract_and_navigation_naming(self):
        t=PHP.read_text(); a=PLATFORM.read_text()
        self.assertIn("'schema' => 'sc-workspace-platform-contract/1.1'",t)
        self.assertIn("'recommended_navigation_label' => 'Workspace'",t)
        self.assertIn("const NAV_BACKUP_KEY = 'sc_workspace_navigation_backup_v082'",a)
        self.assertIn('relabel_navigation_items',a)
        self.assertIn('restore_navigation_items',a)
        self.assertIn("post_title' => 'Workspace'",a)
    def test_no_data_schema_change(self):
        m=json.loads((ROOT/'release-manifest-v0.8.2.json').read_text())
        self.assertEqual(m['storage_schema_version'],9)
        self.assertEqual(m['project_schema'],'sc-workspace-project/7.0')
        self.assertEqual(m['version'],'0.8.2')
        self.assertEqual(m['previous_version'],'0.8.1')
        self.assertFalse(m['cloud_sync'])
        self.assertFalse(m['server_project_storage'])
if __name__=='__main__': unittest.main()
