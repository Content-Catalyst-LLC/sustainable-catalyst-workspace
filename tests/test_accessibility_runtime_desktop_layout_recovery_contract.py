from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class HotfixContract(unittest.TestCase):
 def test_01_lineage_and_schema_stability(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'))
  self.assertIn('Version: 0.71.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '0.71.0",MAIN)
  self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['schema_migration_required'])
 def test_02_accessibility_dependency_has_no_self_edge(self):
  block=re.search(r"wp_enqueue_script\(\s*'sc-workspace-accessibility-v1'.*?\n\s*\);",PHP,re.S).group(0)
  self.assertIn("array('sc-workspace-browser-compatibility-v1')",block)
  deps=re.search(r"array\((.*?)\)",block,re.S).group(1)
  self.assertNotIn("'sc-workspace-accessibility-v1'",deps)
 def test_03_current_assets(self):
  self.assertIn("'sc-workspace-v0710'",PHP);self.assertIn('workspace-v0.71.0.css',PHP);self.assertIn('workspace-v0.71.0.js',PHP)
  self.assertIn("array('sc-workspace-v0710')",PHP);self.assertIn("wp_localize_script('sc-workspace-v0710'",PHP)
 def test_04_hero_zero_minimum_tracks(self):
  self.assertIn('.scw-platform-hero-grid{grid-template-columns:minmax(0,1.18fr) minmax(0,.82fr)}',CSS)
  self.assertIn('.scw-platform-hero-grid>*',CSS);self.assertIn('.scw-platform-preview',CSS);self.assertIn('min-width:0;max-width:100%',CSS)
 def test_05_research_zero_minimum_tracks(self):
  self.assertIn('.scw-research-overview{grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr)}',CSS)
  self.assertIn('.scw-research-overview>*',CSS);self.assertIn('.scw-research-overview-grid>*',CSS)
 def test_06_breakpoints_preserved(self):
  self.assertIn('@media(max-width:980px){.scw-platform-hero-grid{grid-template-columns:minmax(0,1fr)}}',CSS)
  self.assertIn('@media(max-width:900px){.scw-research-overview{grid-template-columns:minmax(0,1fr)}}',CSS)
 def test_07_viewport_matrix_and_manual_boundary(self):
  r=MAN['runtime_layout_recovery'];self.assertEqual(r['viewports'],[1600,1440,1280,1024,768,390]);self.assertTrue(r['full_wordpress_footer_render_manual_qa'])
 def test_08_registry_hotfix(self):
  self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertEqual(REG['release_name'],'Import, Export & Backward-Compatibility Hardening')
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0710'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0640',REGPHP)
 def test_09_predecessor_history(self):
  self.assertTrue((ROOT/'history/release-manifest-v0.64.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.64.0.json').exists())
if __name__=='__main__': unittest.main()
