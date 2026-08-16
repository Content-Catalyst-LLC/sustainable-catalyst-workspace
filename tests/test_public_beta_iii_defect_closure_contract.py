import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.79.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.79.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-defect-closure-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-defect-closure-ui-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v1.14.0.js').read_text()
EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v1.14.0.css').read_text()
class PublicBetaIIIDefectClosureContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.79.0','0.78.0','Public Beta III Defect Closure')); self.assertIn('Version: 1.14.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_03_schemas(self):
  for f in ['sc-workspace-public-beta-iii-defect-closure-v1.schema.json','sc-workspace-public-beta-iii-defect-closure-report-v1.schema.json']:
   self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
 def test_04_rest_contract(self): self.assertIn("'/public-beta-iii-defect-closure-contract'",PHP); self.assertIn('public_beta_iii_defect_closure_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/public-beta-iii-defect-closure-contract',MAN['rest_routes'])
 def test_05_automated_gate(self):
  c=MAN['public_beta_iii_defect_closure']; self.assertTrue(c['automated_defect_gate']); self.assertEqual(c['known_automated_blocker_count'],0); self.assertTrue(c['current_release_consistency_required']); self.assertTrue(c['security_privacy_gate_required']); self.assertTrue(c['accessibility_performance_gate_required']); self.assertTrue(c['recovery_disaster_gate_required']); self.assertTrue(c['beta_iii_topology_gate_required'])
 def test_06_manual_boundary(self):
  c=MAN['public_beta_iii_defect_closure']; self.assertTrue(c['manual_field_validation_outstanding']); self.assertTrue(c['manual_field_items_are_not_silently_closed']); self.assertTrue(c['no_new_product_subsystem']); self.assertIn('Production WordPress smoke test',CORE); self.assertIn('Real two-device continuity test',CORE); self.assertIn('Real shared/institutional handoff test',CORE)
 def test_07_closed_defect_classes(self): self.assertEqual(len(MAN['public_beta_iii_defect_closure']['closed_defect_classes']),10); self.assertIn('wordpress-plugin-header-window-overflow',CORE); self.assertIn('desktop-grid-min-content-collapse',CORE); self.assertIn('accessibility-performance-critical-regression',CORE)
 def test_08_privacy_governance(self): self.assertIn('projectContentIncluded:false',CORE); self.assertIn('deviceIdentifierIncluded:false',CORE); self.assertIn('automaticRepair:false',CORE); self.assertIn('automaticMutation:false',CORE); self.assertIn('telemetry:false',CORE)
 def test_09_ui(self): self.assertIn('data-scw-beta-closure',PHP); self.assertIn('Run closure gate',PHP); self.assertIn('Export closure report',PHP); self.assertIn('AUTOMATED DEFECT CLOSURE',PHP); self.assertIn('data-scw-workspace-view="beta-closure"',PHP)
 def test_10_assets(self): self.assertIn("'sc-workspace-v1140'",PHP); self.assertIn('workspace-v1.14.0.js',PHP); self.assertIn('workspace-v1.14.0.css',PHP); self.assertIn('sc-workspace-public-beta-iii-defect-closure-v1',PHP); self.assertIn('sc-workspace-public-beta-iii-defect-closure-ui-v1',PHP); self.assertIn('/* v0.79.0 — Public Beta III Defect Closure */',CSS); self.assertIn("'beta-closure'",APP); self.assertIn("id:'beta-closure'",EXP)
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.79.0','0.78.0','Public Beta III Defect Closure')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v1140'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0780',REGPHP); self.assertTrue((R/'history/release-manifest-v0.78.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.78.0.json').exists())
 def test_12_docs(self): self.assertTrue((R/'docs/PUBLIC_BETA_III_DEFECT_CLOSURE_V0790.md').exists()); self.assertTrue((R/'RELEASE_NOTES_0.79.0.md').exists())
 def test_13_release_validator(self): self.assertTrue((R/'scripts/validate_public_beta_iii_defect_closure.py').exists())
if __name__=='__main__': unittest.main()
