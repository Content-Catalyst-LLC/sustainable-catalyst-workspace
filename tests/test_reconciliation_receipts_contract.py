import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reconciliation-receipt-v1.js').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class ReconciliationReceiptsContract(unittest.TestCase):
  def test_lineage(self): self.assertEqual(MAN['version'],'0.66.0'); self.assertEqual(MAN['previous_version'],'0.65.0'); self.assertEqual(MAN['release_name'],'Import, Export & Backward-Compatibility Hardening')
  def test_storage_migration_project_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged'])
  def test_receipt_contracts(self): self.assertEqual(MAN['reconciliation_receipt_schema'],'sc-workspace-reconciliation-receipt/1.0'); self.assertEqual(MAN['reconciliation_receipt_export_schema'],'sc-workspace-reconciliation-receipt-export/1.0'); json.loads((ROOT/'schemas/sc-workspace-reconciliation-receipt-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-reconciliation-receipt-export-v1.schema.json').read_text())
  def test_rest(self): self.assertIn('/wp-json/sc-workspace/v1/reconciliation-receipts-contract',MAN['rest_routes']); self.assertIn("'/reconciliation-receipts-contract'",PHP); self.assertIn('public function reconciliation_receipts_contract()',PHP)
  def test_explicit_decision_fields(self): self.assertIn('data-scw-reconcile-reviewer',PHP); self.assertIn('data-scw-reconcile-rationale',PHP); self.assertIn('Decision maker / reviewer label',PHP); self.assertIn('Decision rationale',PHP)
  def test_accepted_declined(self): self.assertIn('accepted',HELP); self.assertIn('declined',HELP); self.assertTrue(MAN['reconciliation_receipts']['accepted_changes_recorded']); self.assertTrue(MAN['reconciliation_receipts']['declined_changes_recorded'])
  def test_integrity(self): self.assertIn("algorithm:'SHA-256'",HELP); self.assertIn('fingerprintPayload',HELP); self.assertIn('sha256Text(receiptHelper.fingerprintPayload(receipt))',JS)
  def test_human_identity_boundary(self): self.assertTrue(MAN['reconciliation_receipts']['reviewer_label_user_supplied']); self.assertFalse(MAN['reconciliation_receipts']['account_identity_inferred']); self.assertIn('accountIdentityInferred:false',HELP)
  def test_receipt_ledger_and_document_summary(self): self.assertIn('receipts: []',JS); self.assertIn('MAX_RECONCILIATION_RECEIPTS = 80',JS); self.assertIn("objectTemplate('document','Reconciliation Decision Receipt')",JS); self.assertIn('Editing this Document object does not alter the receipt ledger.',HELP)
  def test_sources_unchanged_no_auto_decision(self): r=MAN['reconciliation_receipts']; self.assertFalse(r['source_states_mutated']); self.assertFalse(r['automatic_decision_authority']); self.assertIn('sourceStatesMutated:false',HELP)
  def test_v25_migration_preserves(self):
    self.assertIn('function migrateV25(raw)',JS); seg=JS[JS.index('function migrateV25(raw)'):JS.index('function normalizeState',JS.index('function migrateV25(raw)'))]
    for token in ['raw.accountPersistence','raw.crossDeviceSync','raw.versionHistory','raw.safeActions','raw.reconciliation']: self.assertIn(token,seg)
  def test_registry(self): self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0740'",REG); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0740'",REG); self.assertIn("LEGACY_PENDING_KEY_V0260",REG); self.assertIn("'previous_version' => '0.73.0'",REG)
if __name__=='__main__': unittest.main()
