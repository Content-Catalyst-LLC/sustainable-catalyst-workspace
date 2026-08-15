import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'history/release-manifest-v0.60.0.json').read_text()); REG=json.loads((ROOT/'history/workspace-product-record-v0.60.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text();NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
class T(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.60.0','0.59.1','Public Product Beta II'));self.assertIn('Version: 1.0.1',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0')
 def test_03_schemas(self):
  for n in ['sc-workspace-public-beta-ii-v1.schema.json','sc-workspace-beta-gate-v1.schema.json','sc-workspace-beta-field-snapshot-v1.schema.json']: json.loads((ROOT/'schemas'/n).read_text())
 def test_04_gate(self): self.assertIn("GATE_SCHEMA='sc-workspace-beta-gate/1.0'",HELP);self.assertIn("check('shell'",HELP);self.assertIn("check('recovery'",HELP)
 def test_05_no_score(self): self.assertIn('hiddenScore:false',HELP);self.assertNotIn('readinessScore',HELP)
 def test_06_privacy(self): self.assertIn('automaticTelemetry:false',HELP);self.assertIn('automaticSubmission:false',HELP);self.assertIn('projectContentIncluded:false',HELP)
 def test_07_no_repair_mutation(self): self.assertIn('automaticRepair:false',HELP);self.assertIn('automaticProjectMutation:false',HELP)
 def test_08_ui(self): self.assertIn('data-scw-public-beta-ii',PHP);self.assertIn('Run beta gate',PHP);self.assertIn("expectedVersion:'0.72.0'",UI)
 def test_09_review_route(self): self.assertIn("'beta'",NAV);self.assertIn("beta:'Beta Readiness'",NAV);self.assertIn('data-scw-workspace-view="beta"',PHP)
 def test_10_rest(self): self.assertIn("'/public-product-beta-ii-contract'",PHP);self.assertIn('/wp-json/sc-workspace/v1/public-product-beta-ii-contract',MAN['rest_routes'])
 def test_11_header(self): self.assertIn('.scw-public-beta-ii{border-top:4px solid #000',CSS)
 def test_12_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.60.0','0.59.1'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v101'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0600',REGPHP)
 def test_13_history(self): self.assertTrue((ROOT/'history/release-manifest-v0.59.1.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.59.1.json').exists())
if __name__=='__main__': unittest.main()
