import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.81.0.json').read_text()) if (R/'release-manifest-v0.81.0.json').exists() else {}
OLD=json.loads((R/'history/release-manifest-v0.80.0.json').read_text()) if (R/'history/release-manifest-v0.80.0.json').exists() else {}
REG=json.loads((R/'registry/workspace-product-record-v0.81.0.json').read_text()) if (R/'registry/workspace-product-record-v0.81.0.json').exists() else {}
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
DEP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text()
NAV=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.81.0.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.81.0.css').read_text()
class DeploymentHardeningContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN.get('version'),MAN.get('previous_version'),MAN.get('release_name')),('0.81.0','0.80.0','WordPress & Deployment Hardening')); self.assertIn('Version: 0.81.0',MAIN)
 def test_02_schema_freeze(self):
  for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']: self.assertEqual(MAN.get(k),OLD.get(k))
  self.assertFalse(MAN.get('schema_migration_required')); self.assertEqual(MAN.get('object_types'),OLD.get('object_types'))
 def test_03_bootstrap_guard(self): self.assertIn('sc_workspace_bootstrap_failure',MAIN); self.assertIn('is_readable',MAIN); self.assertIn('class-sc-workspace-deployment.php',MAIN)
 def test_04_activation_preflight(self): self.assertIn('activation_preflight',DEP); self.assertIn('required_files',DEP); self.assertIn('MAX_HISTORY = 12',DEP); self.assertIn('project_data_mutated',DEP)
 def test_05_rest_contract(self): self.assertIn("'/deployment-hardening-contract'",PHP); self.assertIn('deployment_hardening_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/deployment-hardening-contract',MAN.get('rest_routes',[]))
 def test_06_current_assets(self): self.assertIn("'sc-workspace-v0810'",PHP); self.assertIn('workspace-v0.81.0.js',PHP); self.assertIn('workspace-v0.81.0.css',PHP); self.assertNotIn("'sc-workspace-v0800'",PHP)
 def test_07_deployment_assets(self): self.assertIn('sc-workspace-wordpress-deployment-hardening-v1',PHP); self.assertIn('sc-workspace-wordpress-deployment-hardening-ui-v1',PHP); self.assertIn('/* v0.81.0 — WordPress & Deployment Hardening */',CSS)
 def test_08_root_server_state(self): self.assertIn('data-scw-deployment-server-state',PHP); self.assertIn('data-scw-deployment-files-complete',PHP); self.assertIn('data-scw-deployment-expected-script',PHP)
 def test_09_navigation_defect_closed(self):
  for token in ["'final-audit'","'beta-closure'","'release-candidate'","'deployment'"]: self.assertIn(token,NAV)
  self.assertIn("id:'deployment'",EXP); self.assertIn("'deployment'",APP)
 def test_10_ui(self): self.assertIn('data-scw-workspace-view="deployment"',PHP); self.assertIn('data-scw-wordpress-deployment-hardening',PHP); self.assertIn('Run deployment check',PHP); self.assertIn('Project storage is not a cache',PHP)
 def test_11_manifest_policy(self):
  d=MAN['wordpress_deployment_hardening']; self.assertTrue(d['safe_bootstrap_guard']); self.assertTrue(d['activation_preflight']); self.assertTrue(d['mixed_version_browser_detection']); self.assertTrue(d['rollback_artifact_required']); self.assertFalse(d['automatic_cache_purge']); self.assertFalse(d['automatic_rollback']); self.assertFalse(d['schema_migration_required'])
 def test_12_registry(self): self.assertEqual((REG.get('public_version'),REG.get('previous_version'),REG.get('release_name')),('0.81.0','0.80.0','WordPress & Deployment Hardening'))
 def test_13_schemas_docs(self):
  for f in ['sc-workspace-wordpress-deployment-hardening-v1.schema.json','sc-workspace-wordpress-deployment-report-v1.schema.json','sc-workspace-wordpress-deployment-checklist-v1.schema.json','sc-workspace-deployment-state-v1.schema.json']: self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
  self.assertTrue((R/'docs/WORDPRESS_DEPLOYMENT_HARDENING_V0810.md').exists())
 def test_14_history_frozen(self): self.assertTrue((R/'history/release-manifest-v0.80.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.80.0.json').exists())
 def test_15_release_candidate_freeze(self): self.assertTrue(MAN['release_candidate_i']['feature_freeze']); self.assertFalse(MAN['wordpress_deployment_hardening']['new_product_subsystem'])
if __name__=='__main__': unittest.main()
