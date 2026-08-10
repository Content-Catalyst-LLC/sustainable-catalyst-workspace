from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.44.0.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.44.0.css').read_text()
MAN=json.loads((ROOT/'release-manifest-v0.44.0.json').read_text())
class AccountCloudPersistenceContract(unittest.TestCase):
  def test_release_lineage(self): self.assertEqual(MAN['version'],'0.44.0'); self.assertEqual(MAN['previous_version'],'0.43.0'); self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0')
  def test_contract_route(self): self.assertIn("'/account-persistence-contract'",PHP); self.assertIn('public function account_persistence_contract()',PHP)
  def test_cloud_routes(self): self.assertIn("'/cloud-projects'",PHP); self.assertIn("'/cloud-projects/(?P<project_id>",PHP)
  def test_auth_required(self): self.assertIn("is_user_logged_in() && current_user_can('read')",PHP); self.assertIn("'X-WP-Nonce'",JS)
  def test_server_store_is_user_meta(self): self.assertIn('get_user_meta(get_current_user_id()',PHP); self.assertIn('update_user_meta(get_current_user_id()',PHP); self.assertEqual(MAN['account_persistence']['server_store'],'wordpress-user-meta')
  def test_manual_not_automatic(self): self.assertFalse(MAN['account_persistence']['automatic_upload']); self.assertFalse(MAN['account_persistence']['background_sync']); self.assertTrue(MAN['account_persistence']['manual_backup'])
  def test_guest_remains_first_class(self): self.assertFalse(MAN['account_required']); self.assertTrue(MAN['anonymous_access']); self.assertTrue(MAN['account_persistence']['guest_local_first'])
  def test_restore_is_copy(self): self.assertEqual(MAN['account_persistence']['restore_mode'],'new-local-copy'); self.assertIn("copy=cloneProject(source)",JS); self.assertFalse(MAN['governance']['cloud_restore_overwrites_local_project'])
  def test_limits(self): self.assertEqual(MAN['account_persistence']['max_projects_per_account'],25); self.assertEqual(MAN['account_persistence']['max_project_bytes'],2621440); self.assertEqual(MAN['account_persistence']['max_account_bytes'],26214400)
  def test_sha256(self): self.assertIn("hash('sha256', $canonical)",PHP); self.assertEqual(MAN['account_persistence']['integrity_algorithm'],'SHA-256')
  def test_project_schema_unchanged(self): self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/20.0'",JS)
  def test_storage_migration(self): self.assertIn('function migrateV20(raw)',JS); self.assertIn('if (raw.schemaVersion === 20) return migrateV20(raw);',JS); self.assertIn('const STORAGE_VERSION = 35;',JS)
  def test_workspace_level_account_state(self): self.assertIn("const ACCOUNT_PERSISTENCE_SCHEMA = 'sc-workspace-account-persistence/1.0'",JS); self.assertIn('accountPersistence: accountPersistenceTemplate()',JS)
  def test_ui(self):
    for marker in ['ACCOUNT CLOUD RECOVERY','data-scw-cloud-backup','data-scw-cloud-refresh','data-scw-cloud-list','Restore as copy']: self.assertIn(marker,PHP+JS)
  def test_no_team_storage(self): self.assertFalse(MAN['account_persistence']['team_storage']); self.assertFalse(MAN['governance']['team_cloud_storage'])
  def test_css_surface(self): self.assertIn('.scw-cloud-recovery',CSS); self.assertIn('@media(forced-colors:active)',CSS)
if __name__=='__main__': unittest.main()
