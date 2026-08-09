import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.19.0.css'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.19.0.js'
PLATFORM=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php'
class PublicExperienceTests(unittest.TestCase):
    def test_advisory_aligned_editorial_hero(self):
        t=PHP.read_text()
        self.assertIn('scw-platform-hero-grid',t)
        self.assertIn('<h1>Research. Analyze. Decide.</h1>',t)
        self.assertIn('scw-platform-preview',t)
        self.assertIn('ILLUSTRATIVE WORKSPACE',t)
        self.assertIn('scw-platform-access-grid',t)
    def test_editorial_header_bar_and_alignment(self):
        t=PHP.read_text(); c=CSS.read_text()
        self.assertIn('scw-editorial-header-bar',t)
        self.assertIn('.scw-editorial-header-bar{height:12px;background:#0b0b0b',c)
        self.assertIn('scw-editorial-header-bar + .scw-platform-hero-editorial',c)
        self.assertIn('height:9px',c)
    def test_editorial_section_rhythm(self):
        t=PHP.read_text(); c=CSS.read_text()
        for token in ('ONE PERSONAL WORKSPACE','WORKSPACE PATHWAYS','PERSONAL CAPABILITY','WORKSPACE APPLICATION','scw-editorial-band','scw-editorial-closing'):
            self.assertIn(token,t)
        for token in ('background:var(--scw-warm)','background:var(--scw-dark)','border-top:4px solid var(--scw-accent)','scw-pathway-list'):
            self.assertIn(token,c)
    def test_project_mode_navigation_still_present(self):
        p=PHP.read_text(); j=JS.read_text()
        for mode in ('overview','research','analysis','decision','canvas','traceability','objects'):
            self.assertIn(f'data-scw-project-mode="{mode}"',p)
            self.assertIn(f'data-scw-project-panel="{mode}"',p)
        self.assertIn('function setProjectMode(mode)',j)
    def test_technical_controls_remain_progressively_disclosed(self):
        t=PHP.read_text()
        self.assertIn('scw-settings-drawer',t)
        self.assertIn('scw-connections-drawer',t)
        self.assertIn('Storage &amp; identity',t)
        self.assertIn('Tools, returns &amp; handoff history',t)
    def test_visual_system_uses_advisory_grammar(self):
        c=CSS.read_text()
        self.assertIn('v0.8.3.1 — Editorial Header Bar & Page Alignment',c)
        self.assertIn('--scw-warm:#f7f3ea',c)
        self.assertIn('--scw-dark:#0d0d0d',c)
        self.assertIn('--scw-accent:#ff0000',c)
        self.assertIn('.scw-platform-application-editorial',c)
        self.assertIn('.scw-capability-dark',c)
    def test_platform_contract_and_navigation_unchanged(self):
        t=PHP.read_text(); a=PLATFORM.read_text()
        self.assertIn("'schema' => 'sc-workspace-platform-contract/1.2'",t)
        self.assertIn("'recommended_navigation_label' => 'Workspace'",t)
        self.assertIn("'public_experience' => 'advisory-aligned-editorial'",t)
        self.assertIn("const NAV_BACKUP_KEY = 'sc_workspace_navigation_backup_v082'",a)
        self.assertIn('relabel_navigation_items',a)
        self.assertIn("post_title' => 'Workspace'",a)
    def test_traceability_schema_migration_preserves_platform_boundary(self):
        m=json.loads((ROOT/'release-manifest-v0.19.0.json').read_text())
        self.assertEqual(m['storage_schema_version'],20)
        self.assertEqual(m['project_schema'],'sc-workspace-project/11.0')
        self.assertEqual(m['version'],'0.19.0')
        self.assertEqual(m['previous_version'],'0.18.0')
        self.assertFalse(m['cloud_sync'])
        self.assertFalse(m['server_project_storage'])
if __name__=='__main__': unittest.main()
