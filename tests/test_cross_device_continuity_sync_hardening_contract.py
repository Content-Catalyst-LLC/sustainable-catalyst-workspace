from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.67.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.67.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAIN=MAINP.read_text(); HEAD=MAINP.read_bytes()[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.0.1.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-cross-device-continuity-v1.js').read_text()
class ContinuityHardening(unittest.TestCase):
 def test_01_lineage_and_header(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.67.0','0.66.1','Cross-Device Continuity & Sync Hardening'))
  self.assertIn('Version: 2.0.1',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '2.0.1",MAIN)
  for label,value in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','2.0.1'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
   m=re.search(r'^[ \\t\\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); self.assertTrue(m and m.group(1).strip()==value)
 def test_02_canonical_schema_stability(self):
  self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'))
  self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['cross_device_continuity_only_release']); self.assertFalse(MAN['migration']['cross_device_continuity_canonical_data_rewrite'])
  self.assertEqual(MAN['account_persistence']['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['cross_device_sync']['storage_schema_version'],35)
 def test_03_assets_and_contract_route(self):
  self.assertIn("'sc-workspace-cross-device-continuity-v1'",PHP); self.assertIn('sc-workspace-cross-device-continuity-v1.js',PHP)
  self.assertIn("'sc-workspace-v201'",PHP); self.assertIn('workspace-v2.0.1.js',PHP); self.assertIn('workspace-v2.0.1.css',PHP)
  self.assertIn("'/continuity-contract'",PHP); self.assertIn('public function continuity_contract()',PHP); self.assertIn('/wp-json/sc-workspace/v1/continuity-contract',MAN['rest_routes'])
 def test_04_current_project_schema_cloud_storage(self):
  self.assertIn("array('sc-workspace-project/20.0','sc-workspace-project/19.0'",PHP)
  self.assertIn("'project_schema' => 'sc-workspace-project/20.0'",PHP)
 def test_05_retry_safe_sync_operation_id(self):
  self.assertIn("$payload['operationId']",PHP); self.assertIn("$existing['lastOperationId']",PHP); self.assertIn("'replayed' => true",PHP)
  self.assertIn('operationId',APP); self.assertIn("retryStrategy: 'idempotent-operation-id'",APP)
 def test_06_interrupted_operation_recovery(self):
  self.assertIn('recoverInterruptedSyncOperations()',APP); self.assertIn('beginSyncOperation',APP); self.assertIn('interruptSyncOperation',APP); self.assertIn('finishSyncOperation',APP)
  self.assertIn("state:'interrupted'",HELP); self.assertIn('markInterrupted',HELP)
 def test_07_pull_safety_restore_point(self):
  self.assertIn("'sync-safety'",APP); self.assertIn('createRestorePoint(project',APP); self.assertIn('pull_creates_sync_safety_restore_point',PHP)
 def test_08_device_migration_boundary(self):
  for s in ['sc-workspace-device-migration/1.0','new-local-copy','syncEnrollmentTransferred:false','deviceIdentityIncluded:false','accountProfileIncluded:false','backgroundSync:false']:
   self.assertIn(s,HELP)
  self.assertIn('data-scw-sync-migration-export',PHP); self.assertIn('data-scw-sync-migration-import',PHP)
  self.assertIn('Sync remains disabled until you explicitly enroll the new copy.',APP)
 def test_09_duplicate_guard(self):
  self.assertIn('migrationKey',HELP); self.assertIn('This exact migration package was already imported on this device.',APP); self.assertTrue(MAN['cross_device_continuity']['duplicate_migration_guard'])
 def test_10_manual_backup_cannot_replace_sync_head(self):
  self.assertIn('scw_manual_backup_sync_head_conflict',PHP); self.assertIn('Manual backup cannot replace an active sync head.',PHP); self.assertFalse(MAN['cross_device_continuity']['manual_backup_overwrites_sync_head'])
 def test_11_no_automatic_sync(self):
  self.assertFalse(MAN['cross_device_continuity']['automatic_sync']); self.assertFalse(MAN['cross_device_continuity']['background_sync'])
  self.assertIn("'background_sync' => false",PHP); self.assertIn("'automatic_sync' => false",PHP)
 def test_12_schemas_registry_history(self):
  for f in ['schemas/sc-workspace-cross-device-continuity-v1.schema.json','schemas/sc-workspace-sync-operation-v1.schema.json','schemas/sc-workspace-device-migration-v1.schema.json']:
   self.assertTrue((ROOT/f).exists())
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.67.0','0.66.1','Cross-Device Continuity & Sync Hardening'))
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0661',REGPHP)
  self.assertTrue((ROOT/'history/release-manifest-v0.66.1.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.66.1.json').exists())
if __name__=='__main__': unittest.main()
