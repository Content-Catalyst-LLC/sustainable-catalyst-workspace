import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-resilience-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-resilience-ui-v1.js').read_text();APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text();NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
class T(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.84.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['product_hardening_i']['schema_migration'])
 def test_03_schemas(self):
  for n in ['sc-workspace-route-state-v1.schema.json','sc-workspace-field-resilience-v1.schema.json','sc-workspace-resilience-snapshot-v1.schema.json']:json.loads((ROOT/'schemas'/n).read_text())
 def test_04_route_restore(self): self.assertIn("STORAGE_KEY='sc_workspace_route_state_v0610'",HELP);self.assertIn('sanitizeRouteState',HELP);self.assertIn("?'invalid-route'",HELP)
 def test_05_back_forward(self): self.assertIn("window.addEventListener('popstate'",UI);self.assertIn('history.pushState',UI);self.assertIn('history.replaceState',UI)
 def test_06_navigation_reset_only(self): self.assertIn('clearUiState',HELP);self.assertIn('canonicalDataTouched:false',HELP);self.assertNotIn('localStorage.clear',HELP+UI)
 def test_07_recovery_classification(self): self.assertIn('recoveryState',HELP);self.assertIn("state=current==='invalid'",HELP);self.assertIn('lastKnownGood',HELP)
 def test_08_privacy_snapshot(self): self.assertIn('projectContentIncluded:false',HELP);self.assertIn('sourceUrlsIncluded:false',HELP);self.assertIn('automaticTelemetry:false',HELP)
 def test_09_ui(self): self.assertIn('data-scw-field-resilience',PHP);self.assertIn('Reset navigation state',PHP);self.assertIn('data-scw-workspace-view="reliability"',PHP)
 def test_10_navigation(self): self.assertIn("'reliability'",NAV);self.assertIn("reliability:'Reliability'",NAV);self.assertIn("workspaceView !== 'reliability'",APP)
 def test_11_rest(self): self.assertIn("'/field-resilience-contract'",PHP);self.assertIn('/wp-json/sc-workspace/v1/field-resilience-contract',MAN['rest_routes'])
 def test_12_header_and_cleanup(self): self.assertIn('.scw-field-resilience{border-top:4px solid #000',CSS);self.assertEqual(PHP.count('A free project environment for carrying questions, evidence, data, analysis, decisions, and authored work across Sustainable Catalyst.'),1)
 def test_13_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0840'",REGPHP);self.assertTrue((ROOT/'history/release-manifest-v0.61.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.61.0.json').exists())
if __name__=='__main__':unittest.main()
