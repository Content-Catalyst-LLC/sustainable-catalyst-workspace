import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.78.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.78.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-ui-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.0.1.js').read_text()
EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.1.css').read_text()
class AccessibilityPerformanceFinalAuditContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.78.0','0.77.0','Accessibility & Performance Final Audit')); self.assertIn('Version: 2.0.1',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_03_schemas(self):
  for f in ['sc-workspace-accessibility-performance-final-audit-v1.schema.json','sc-workspace-accessibility-performance-final-audit-report-v1.schema.json','sc-workspace-accessibility-performance-final-checklist-v1.schema.json']:
   self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
 def test_04_rest_contract(self): self.assertIn("'/accessibility-performance-final-audit-contract'",PHP); self.assertIn('accessibility_performance_final_audit_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/accessibility-performance-final-audit-contract',MAN['rest_routes'])
 def test_05_reuses_existing_audit_engines(self): self.assertIn('SCWorkspaceAccessibility',UI); self.assertIn('SCWorkspacePerformanceSession',UI); self.assertIn('existing_accessibility_engine_reused',PHP); self.assertIn('existing_long_session_monitor_reused',PHP)
 def test_06_blocking_budgets(self):
  a=MAN['accessibility_performance_final_audit']; self.assertEqual(a['dom_critical'],10000); self.assertEqual(a['render_p95_critical_ms'],100); self.assertEqual(a['index_p95_critical_ms'],1000); self.assertEqual(a['long_task_critical_count'],5); self.assertTrue(a['critical_automated_release_gate'])
 def test_07_manual_boundary(self):
  a=MAN['accessibility_performance_final_audit']; self.assertTrue(a['manual_field_audit_required']); self.assertFalse(a['automated_accessibility_certification']); self.assertFalse(a['automated_performance_certification']); self.assertIn('VoiceOver + Safari',JS); self.assertIn('400% / 320 CSS px reflow',JS); self.assertIn('Representative four-hour session',JS)
 def test_08_privacy_governance(self):
  a=MAN['accessibility_performance_final_audit']; self.assertTrue(a['privacy_minimized_report']); self.assertFalse(a['automatic_repair']); self.assertFalse(a['automatic_optimization']); self.assertFalse(a['automatic_deletion']); self.assertFalse(a['automatic_upload']); self.assertFalse(a['telemetry']); self.assertFalse(a['canonical_mutation']); self.assertIn('projectContentIncluded:false',JS); self.assertIn('deviceIdentifierIncluded:false',JS)
 def test_09_ui(self): self.assertIn('data-scw-final-audit',PHP); self.assertIn('Run final audit',PHP); self.assertIn('Export final field-QA checklist',PHP); self.assertIn('Automated gate, not certification',PHP); self.assertIn('data-scw-workspace-view="final-audit"',PHP)
 def test_10_assets(self): self.assertIn("'sc-workspace-v201'",PHP); self.assertIn('workspace-v2.0.1.js',PHP); self.assertIn('workspace-v2.0.1.css',PHP); self.assertIn('sc-workspace-accessibility-performance-final-audit-v1',PHP); self.assertIn('sc-workspace-accessibility-performance-final-audit-ui-v1',PHP); self.assertIn('/* v0.78.0 — Accessibility & Performance Final Audit */',CSS); self.assertIn("'final-audit'",APP); self.assertIn("id:'final-audit'",EXP)
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.78.0','0.77.0','Accessibility & Performance Final Audit')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0770',REGPHP); self.assertTrue((R/'history/release-manifest-v0.77.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.77.0.json').exists())
 def test_12_docs(self): self.assertTrue((R/'docs/ACCESSIBILITY_PERFORMANCE_FINAL_AUDIT_V0780.md').exists()); self.assertTrue((R/'RELEASE_NOTES_0.78.0.md').exists())
 def test_13_release_validator(self): self.assertTrue((R/'scripts/validate_accessibility_performance_final_audit.py').exists())
if __name__=='__main__': unittest.main()
