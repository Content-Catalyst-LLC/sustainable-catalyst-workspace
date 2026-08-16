import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.73.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.73.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-ui-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.1.css').read_text()
class CollaborationSharedReviewHardeningContract(unittest.TestCase):
 def test_release_lineage_schema_stability(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.73.0','0.72.0','Collaboration & Shared Review Hardening'))
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_hardening_contract(self):
  h=MAN['collaboration_review_hardening']; self.assertTrue(h['source_revision_fingerprint']); self.assertTrue(h['stale_response_detection']); self.assertTrue(h['duplicate_response_commit_blocked']); self.assertTrue(h['stale_response_requires_owner_acknowledgement']); self.assertTrue(h['reconciliation_receipt'])
  for k in ['canonical_mutation','proposal_acceptance_applies_change','live_coediting','server_collaboration','automatic_send','schema_migration_required']: self.assertFalse(h[k],k)
 def test_revision_duplicate_and_receipt_runtime(self):
  for marker in ['sourceSnapshotFingerprint','assessResponseImport','duplicateResponseCommitBlocked:true','staleResponseRequiresOwnerAcknowledgement:true','commitResponseHardened','RECEIPT_STORAGE_KEY','reconciliation-receipt/1.0','ownerIdentityCryptographicallyVerified:false']: self.assertIn(marker,HELP)
  self.assertIn('data-scw-handoff-integrity',PHP); self.assertIn('data-scw-handoff-owner-ack',PHP); self.assertIn('Reconcile staged response',PHP)
  self.assertIn('stagedAssessment',UI); self.assertIn('ownerAcknowledged',UI); self.assertIn('Duplicate commit blocked',HELP)
 def test_identity_boundary(self):
  h=MAN['collaboration_review_hardening']; self.assertEqual(h['reviewer_identity'],'declarative-not-cryptographically-verified'); self.assertEqual(h['owner_identity'],'declarative-not-cryptographically-verified')
  self.assertFalse(MAN['governance']['shared_review_owner_identity_cryptographically_verified']); self.assertFalse(MAN['governance']['shared_review_reviewer_identity_cryptographically_verified'])
 def test_wordpress_current_assets_and_rest(self):
  self.assertIn('Version: 2.0.1',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '2.0.1",MAIN); self.assertIn("'/collaboration-review-hardening-contract'",PHP); self.assertIn('collaboration_review_hardening_contract',PHP)
  self.assertIn("'sc-workspace-v201'",PHP); self.assertIn('workspace-v2.0.1.js',PHP); self.assertIn('workspace-v2.0.1.css',PHP)
 def test_registry_history_docs_schemas(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.73.0','0.72.0','Collaboration & Shared Review Hardening'))
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v201'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0720',REGPHP)
  self.assertTrue((R/'history/release-manifest-v0.72.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.72.0.json').exists())
  for f in ['schemas/sc-workspace-collaboration-review-hardening-v1.schema.json','schemas/sc-workspace-shared-review-import-assessment-v1.schema.json','schemas/sc-workspace-shared-review-reconciliation-receipt-v1.schema.json','docs/COLLABORATION_SHARED_REVIEW_HARDENING_V0730.md']: self.assertTrue((R/f).exists(),f)
 def test_css_and_review_text(self):
  self.assertIn('/* v0.73.0 — Collaboration & Shared Review Hardening */',CSS); self.assertIn('.scw-review-integrity',CSS); self.assertIn('.scw-review-owner-ack',CSS)
  self.assertIn('source-revision fingerprints',PHP.lower()); self.assertIn('does not provide live co-editing',PHP)
if __name__=='__main__': unittest.main()
