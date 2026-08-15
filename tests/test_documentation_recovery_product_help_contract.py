import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.76.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.76.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-product-help-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-product-help-ui-v1.js').read_text()
NAV=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v1.5.0.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v1.5.0.css').read_text()

class ProductHelpContract(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.76.0','0.75.0','Documentation, Recovery Guidance & Product Help'))
  self.assertIn('Version: 1.5.0',MAIN)
 def test_02_schema_stable(self):
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_03_rest_contract(self):
  self.assertIn("'/product-help-contract'",PHP); self.assertIn('product_help_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/product-help-contract',MAN['rest_routes'])
 def test_04_help_route(self):
  self.assertIn("views:['start','journey','help']",NAV); self.assertIn("help:'Help & Recovery'",NAV); self.assertIn('data-scw-workspace-section="help"',PHP); self.assertIn("'start','journey','help','projects'",APP)
 def test_05_topics_and_recovery(self):
  self.assertIn("const TOPICS=[",HELP); self.assertIn("id:'save-failed'",HELP); self.assertIn("id:'sync-conflict'",HELP); self.assertIn("id:'institutional-handoff'",HELP); self.assertEqual(MAN['documentation_recovery_product_help']['searchable_topic_count'],10)
 def test_06_governance(self):
  h=MAN['documentation_recovery_product_help']; self.assertFalse(h['automatic_repair']); self.assertFalse(h['automatic_restore']); self.assertFalse(h['automatic_upload']); self.assertFalse(h['automatic_sync']); self.assertFalse(h['behavioral_tracking']); self.assertFalse(h['telemetry']); self.assertFalse(h['canonical_mutation']); self.assertTrue(h['restore_as_copy_preferred'])
 def test_07_privacy_report(self):
  for tok in ['projectContentIncluded:false','projectTitleIncluded:false','sourceUrlsIncluded:false','queryTextIncluded:false','deviceIdentifierIncluded:false','accountIdentityIncluded:false']: self.assertIn(tok,HELP)
  self.assertIn('data-scw-help-export',PHP); self.assertIn('workspace-product-help-report.json',UI)
 def test_08_product_boundaries_visible(self):
  self.assertIn('Browser-local first',PHP); self.assertIn('Explicit recovery copy',PHP); self.assertIn('Conflict-safe, user initiated',PHP); self.assertIn('Prefer restore-as-copy',PHP); self.assertIn('avoid clearing browser storage',PHP)
 def test_09_assets(self):
  self.assertIn("'sc-workspace-v150'",PHP); self.assertIn('workspace-v1.5.0.js',PHP); self.assertIn('workspace-v1.5.0.css',PHP); self.assertIn('sc-workspace-product-help-v1',PHP); self.assertIn('sc-workspace-product-help-ui-v1',PHP); self.assertIn('/* v0.76.0 — Documentation, Recovery Guidance & Product Help */',CSS)
 def test_10_registry_history(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.76.0','0.75.0','Documentation, Recovery Guidance & Product Help')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v150'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0750',REGPHP); self.assertTrue((R/'history/release-manifest-v0.75.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.75.0.json').exists())
 def test_11_artifacts(self):
  for f in ['schemas/sc-workspace-product-help-v1.schema.json','schemas/sc-workspace-recovery-guidance-v1.schema.json','schemas/sc-workspace-product-help-report-v1.schema.json','docs/DOCUMENTATION_RECOVERY_GUIDANCE_PRODUCT_HELP_V0760.md','RELEASE_NOTES_0.76.0.md']: self.assertTrue((R/f).exists(),f)
if __name__=='__main__': unittest.main()
