import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.46.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.46.0.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.46.0.css').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class CrossDeviceSyncContract(unittest.TestCase):
 def test_lineage(self): self.assertEqual(MAN['version'],'0.46.0');self.assertEqual(MAN['previous_version'],'0.45.0');self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0')
 def test_sync_schemas(self): self.assertEqual(MAN['cross_device_sync_schema'],'sc-workspace-cross-device-sync/1.0');self.assertEqual(MAN['sync_push_schema'],'sc-workspace-sync-push/1.0')
 def test_sync_endpoint(self): self.assertIn("'/sync-contract'",PHP);self.assertIn('public function sync_contract()',PHP)
 def test_explicit_enrollment(self): self.assertTrue(MAN['cross_device_sync']['explicit_project_enrollment']);self.assertFalse(MAN['cross_device_sync']['enrollment_uploads_content']);self.assertIn('data-scw-sync-toggle',PHP)
 def test_no_background(self): self.assertFalse(MAN['cross_device_sync']['background_sync']);self.assertFalse(MAN['cross_device_sync']['automatic_upload']);self.assertFalse(MAN['governance']['background_cloud_sync'])
 def test_revision_precondition(self): self.assertTrue(MAN['cross_device_sync']['server_revision_precondition']);self.assertEqual(MAN['cross_device_sync']['stale_push_http_status'],409);self.assertIn("'scw_sync_conflict'",PHP);self.assertIn("'status' => 409",PHP)
 def test_no_silent_last_write_wins(self): self.assertFalse(MAN['cross_device_sync']['silent_last_write_wins']);self.assertFalse(MAN['governance']['sync_silent_last_write_wins'])
 def test_sha256_comparison(self): self.assertIn('syncProjectFingerprint',JS);self.assertIn("hash('sha256', $canonical)",PHP);self.assertEqual(MAN['cross_device_sync']['integrity_algorithm'],'SHA-256')
 def test_conflict_copy(self): self.assertIn('(Local conflict copy)',JS);self.assertIn('data-scw-sync-resolve-cloud',PHP);self.assertIn('data-scw-sync-resolve-local',PHP)
 def test_safe_pull(self): self.assertTrue(MAN['cross_device_sync']['safe_remote_pull_when_local_unchanged']);self.assertIn("'remote-ahead'",JS);self.assertIn('applyRemoteInPlace',JS)
 def test_v21_migration(self): self.assertIn('function migrateV21(raw)',JS);self.assertIn('raw.schemaVersion === 21',JS);self.assertIn('crossDeviceSyncTemplate()',JS)
 def test_manual_backup_retained(self): self.assertTrue(MAN['account_persistence']['manual_backup']);self.assertIn('data-scw-cloud-backup',PHP)
 def test_account_limits(self): self.assertEqual(MAN['account_persistence']['max_projects_per_account'],25);self.assertEqual(MAN['account_persistence']['max_project_bytes'],2621440);self.assertEqual(MAN['account_persistence']['max_account_bytes'],26214400)
 def test_schema_files(self):
  for f in ['sc-workspace-cross-device-sync-v1.schema.json','sc-workspace-sync-push-v1.schema.json']: json.loads((ROOT/'schemas'/f).read_text())
 def test_registry_lineage(self): self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0460'",REG);self.assertIn("LEGACY_PENDING_KEY_V0240 = 'sc_workspace_registry_pending_v0240'",REG);self.assertIn("LEGACY_PENDING_KEY_V0220 = 'sc_workspace_registry_pending_v0220'",REG)
 def test_css(self): self.assertIn('/* v0.22.0 — Cross-Device Sync & Conflict-Safe Recovery */',CSS);self.assertIn('.scw-sync-grid',CSS)
 def test_history(self): self.assertTrue((ROOT/'history/release-manifest-v0.21.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.21.0.json').exists())
if __name__=='__main__':unittest.main()
