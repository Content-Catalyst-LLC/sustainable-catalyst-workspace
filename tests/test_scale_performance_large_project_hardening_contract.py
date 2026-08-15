import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-scale-performance-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-scale-performance-ui-v1.js').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class TestScalePerformanceLargeProjectHardening(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 1.1.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['scale_performance']['schema_migration'])
 def test_03_contract_route(self): self.assertIn('/wp-json/sc-workspace/v1/scale-performance-contract',MAN['rest_routes']); self.assertIn("'/scale-performance-contract'",PHP); self.assertIn('scale_performance_contract',PHP)
 def test_04_derived_cache(self): self.assertTrue(MAN['scale_performance']['derived_index_cache']); self.assertIn('function deriveIntegrated',HELP); self.assertIn('cache.hits++',HELP); self.assertIn('deriveIntegrated(state,api)',APP)
 def test_05_bounded_rendering(self): self.assertEqual(MAN['scale_performance']['bounded_render_window'],120); self.assertEqual(MAN['scale_performance']['max_manual_render_window'],600); self.assertIn('rows.slice(0,integratedRenderLimit)',APP); self.assertIn('data-scw-integrated-load-more',PHP)
 def test_06_storage_pressure(self): self.assertTrue(MAN['scale_performance']['storage_pressure_visibility']); self.assertIn('function pressure',HELP); self.assertIn('navigator.storage',UI); self.assertIn('data-scw-scale-quota',PHP)
 def test_07_stress_fixtures(self): self.assertTrue(MAN['scale_performance']['large_project_stress_fixtures']); self.assertIn('function stressFixture',HELP)
 def test_08_advisory_governance(self): self.assertTrue(MAN['scale_performance']['advisory_only']); self.assertFalse(MAN['scale_performance']['automatic_deletion']); self.assertFalse(MAN['scale_performance']['automatic_archival']); self.assertFalse(MAN['scale_performance']['automatic_compaction']); self.assertFalse(MAN['scale_performance']['automatic_migration']); self.assertFalse(MAN['scale_performance']['canonical_mutation'])
 def test_09_performance_surface(self): self.assertIn('data-scw-workspace-view="performance"',PHP); self.assertIn('data-scw-scale-performance',PHP); self.assertIn('Run scale profile',PHP); self.assertIn("performance:'Performance'",NAV)
 def test_10_cache_clear_is_derived_only(self): self.assertIn('Clear derived cache',PHP); self.assertIn('Canonical Workspace data was unchanged',UI); self.assertIn('function clearCache',HELP)
 def test_11_header_rule(self): self.assertIn('.scw-scale-performance{border-top:4px solid #000',CSS)
 def test_12_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v110'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0570',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.58.0.json').exists())
 def test_13_previous_institutional_release_retained(self):
  hist=json.loads((ROOT/'history/release-manifest-v0.57.0.json').read_text()); self.assertEqual(hist['release_name'],'Institutional Research Packages'); self.assertIn('sc-workspace-institutional-research-packages-v1.js',PHP)
if __name__=='__main__': unittest.main()
