import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace'
MAN=json.loads((R/'history/release-manifest-v1.8.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.7.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.8.0.json').read_text())
MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text();ROOM=(P/'includes/class-sc-workspace-review-rooms.php').read_text();JS=(P/'assets/js/sc-workspace-review-rooms-v1.js').read_text();UI=(P/'assets/js/sc-workspace-review-rooms-ui-v1.js').read_text()
class SharedReviewRooms(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.8.0','1.7.0','Shared Review Rooms & Controlled Collaboration'))
 def test_02_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.8.0','1.7.0'));self.assertIn("LEGACY_PENDING_KEY_V180",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V170',REGPHP)
 def test_03_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_04_only_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/shared-review-rooms-contract'});self.assertIn("'/shared-review-rooms-contract'",PHP)
 def test_05_room_states_roles(self):
  g=MAN['shared_review_rooms'];self.assertEqual(g['room_states'],['draft','open','in-review','changes-requested','approved','closed']);self.assertEqual(g['roles'],['owner','editor','reviewer','observer']);self.assertTrue(g['scoped_permissions']);self.assertTrue(g['explicit_invitations'])
 def test_06_snapshot_and_audit(self):
  g=MAN['shared_review_rooms'];self.assertTrue(g['immutable_review_snapshots']);self.assertTrue(g['snapshot_scope_uses_explicit_object_ids']);self.assertTrue(g['snapshot_fingerprint_required']);self.assertTrue(g['review_state_transitions_audited'])
 def test_07_boundaries(self):
  g=MAN['shared_review_rooms'];self.assertTrue(g['permissions_are_local_governance_records']);self.assertFalse(g['server_acl_created']);self.assertFalse(g['automatic_invitation_delivery']);self.assertFalse(g['live_coediting']);self.assertFalse(g['team_cloud_storage']);self.assertFalse(g['automatic_canonical_mutation']);self.assertFalse(g['automatic_ai']);self.assertFalse(g['behavioral_telemetry'])
 def test_08_ui(self): self.assertIn('Shared Review Rooms',PHP);self.assertIn('Freeze review snapshot',PHP);self.assertIn('Record invitation',PHP);self.assertIn('Controlled review, not a shared tenant',PHP)
 def test_09_runtime(self): self.assertIn('data-release-stage="product-maturity"',PHP);self.assertIn('workspace-v1.15.0.js',PHP);self.assertIn('sc-workspace-review-rooms-v1',PHP);self.assertIn('SCWorkspaceReviewRoomsUI',UI)
 def test_10_deployment(self): self.assertIn("PREVIOUS_RELEASE = '1.14.0'",DEP);self.assertIn("ROLLBACK_RELEASE = '1.14.0'",DEP);self.assertIn('class-sc-workspace-review-rooms.php',DEP)
 def test_11_identity(self): self.assertIn('Version: 1.15.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '1.15.0'",MAIN)
 def test_12_schemas(self):
  for f in ['sc-workspace-shared-review-room-v1.schema.json','sc-workspace-review-room-invitation-v1.schema.json','sc-workspace-review-room-snapshot-v1.schema.json','sc-workspace-review-room-event-v1.schema.json','sc-workspace-review-room-export-v1.schema.json']: self.assertTrue((R/'schemas'/f).exists())
 def test_13_model(self): self.assertIn("const STORAGE_KEY='sc_workspace_review_rooms_v1'",JS);self.assertIn('freezeSnapshot',JS);self.assertIn('exportRoom',JS);self.assertIn('serverAclCreated:false',JS)
if __name__=='__main__': unittest.main()
