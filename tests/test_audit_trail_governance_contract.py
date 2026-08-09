import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.31.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.31.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-audit-trail-v1.js').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class AuditTrailContract(unittest.TestCase):
  def test_lineage(self): self.assertEqual(MAN['version'],'0.31.0'); self.assertEqual(MAN['previous_version'],'0.30.0'); self.assertEqual(MAN['release_name'],'Public Beta Hardening & Field Diagnostics')
  def test_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],27); self.assertEqual(MAN['project_schema'],'sc-workspace-project/12.0'); self.assertFalse(MAN['schema_migration_required']); self.assertEqual(MAN['migration']['storage_from'],27); self.assertEqual(MAN['migration']['storage_to'],27); self.assertTrue(MAN['migration']['project_schema_unchanged'])
  def test_audit_schemas(self): self.assertEqual(MAN['audit_trail_schema'],'sc-workspace-audit-trail/1.0'); self.assertEqual(MAN['audit_event_schema'],'sc-workspace-audit-event/1.0'); self.assertEqual(MAN['audit_export_schema'],'sc-workspace-audit-export/1.0')
  def test_rest_contract(self): self.assertIn('/wp-json/sc-workspace/v1/audit-trail-contract',MAN['rest_routes']); self.assertIn("'/audit-trail-contract'",PHP); self.assertIn('public function audit_trail_contract()',PHP)
  def test_top_level_view(self): self.assertIn('data-scw-workspace-view="audit"',PHP); self.assertIn('data-scw-workspace-section="audit"',PHP); self.assertIn("workspaceView === 'audit'",JS)
  def test_derived_no_shadow(self): a=MAN['audit_trail']; self.assertTrue(a['derived_from_authoritative_ledgers']); self.assertFalse(a['stored_shadow_database']); self.assertIn('storedShadowDatabase:false',HELP)
  def test_expected_sources(self):
    for source in ['version-history','account-recovery','cross-device-sync','safe-actions','reconciliation','collaboration','institutional-handoff','share','interoperability','project-activity']: self.assertIn(source,MAN['audit_trail']['event_sources']); self.assertIn(source,HELP)
  def test_filters(self): self.assertTrue(MAN['audit_trail']['project_filter']); self.assertTrue(MAN['audit_trail']['source_filter']); self.assertIn('data-scw-audit-project',PHP); self.assertIn('data-scw-audit-source',PHP)
  def test_export_privacy(self): self.assertTrue(MAN['audit_trail']['portable_json_export']); self.assertFalse(MAN['audit_trail']['project_content_in_export']); self.assertIn('projectContentIncluded:false',HELP); self.assertIn('data-scw-audit-export',PHP)
  def test_no_scores_or_people_ranking(self): a=MAN['audit_trail']; self.assertFalse(a['hidden_governance_score']); self.assertFalse(a['people_ranking']); self.assertFalse(a['automatic_compliance_inference']); self.assertIn('No hidden governance score',PHP)
  def test_read_only_events(self): self.assertFalse(MAN['audit_trail']['events_editable']); self.assertIn('editable:false',HELP); self.assertIn('derived:true',HELP)
  def test_storage_attribute_corrected(self): self.assertIn('data-storage-version="27"',PHP); self.assertNotIn('data-storage-version="25"',PHP)
  def test_registry_lineage(self): self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0310'",REG); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0310'",REG); self.assertIn("LEGACY_PENDING_KEY_V0270",REG); self.assertIn("'previous_version' => '0.30.0'",REG)
  def test_history_preserved(self): self.assertTrue((ROOT/'history/release-manifest-v0.27.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.27.0.json').exists())
if __name__=='__main__': unittest.main()
