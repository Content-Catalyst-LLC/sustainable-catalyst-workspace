import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text()) if (ROOT/'registry/workspace-product-record-v0.66.0.json').exists() else {}
class VersionHistoryContract(unittest.TestCase):
  def test_plugin_version(self): self.assertIn('Version: 1.2.0',MAIN)
  def test_storage_schema_23(self): self.assertIn('const STORAGE_VERSION = 35;',JS)
  def test_project_schema_unchanged(self): self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/20.0';",JS)
  def test_contract_route(self): self.assertIn("/version-history-contract",PHP)
  def test_history_schema(self): self.assertIn("sc-workspace-version-history/1.0",JS)
  def test_restore_schema(self): self.assertIn("sc-workspace-restore-point/1.0",JS)
  def test_restore_copy_only(self): self.assertIn("'restore_mode' => 'new-local-copy'",PHP); self.assertIn("'overwrite_current_project' => false",PHP)
  def test_limits(self): self.assertIn('const MAX_RESTORE_POINTS = 80;',JS); self.assertIn('const MAX_RESTORE_POINTS_PER_PROJECT = 20;',JS); self.assertIn('const MAX_RESTORE_POINT_BYTES = 1572864;',JS)
  def test_sha256_integrity(self): self.assertIn("integrity_algorithm' => 'SHA-256",PHP); self.assertIn('sha256Text(JSON.stringify(snapshot))',JS)
  def test_top_level_history_view(self): self.assertIn('data-scw-workspace-view="history"',PHP); self.assertIn('data-scw-workspace-section="history"',PHP)
  def test_restore_as_copy_ui(self): self.assertIn("restore.textContent='Restore as copy'",JS); self.assertIn('cloneProject(point.snapshot)',JS)
  def test_no_cloud_history(self): self.assertIn("'automatic_cloud_upload' => false",PHP); self.assertIn("'server_version_history' => false",PHP)
  def test_migrate_v22(self): self.assertIn('function migrateV22(raw)',JS); self.assertIn('raw.schemaVersion === 22',JS)
  def test_current_state_preserves_account_and_sync(self): self.assertIn('state.accountPersistence = normalizeAccountPersistence(raw.accountPersistence, state.projects);',JS); self.assertIn('state.crossDeviceSync = normalizeCrossDeviceSync(raw.crossDeviceSync, state.projects);',JS)
  def test_registry_previous(self): self.assertEqual(REG.get('previous_version'),'0.65.0')
if __name__=='__main__': unittest.main()
