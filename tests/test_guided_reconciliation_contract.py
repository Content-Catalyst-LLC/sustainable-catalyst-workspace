import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.62.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.62.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reconciliation-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.62.0.css').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class GuidedReconciliationContract(unittest.TestCase):
    def test_release_lineage(self):
        self.assertEqual(MAN['version'],'0.62.0'); self.assertEqual(MAN['previous_version'],'0.61.0'); self.assertEqual(MAN['release_name'],'Product Hardening II: Persistence, Corruption & Recovery Integrity')
    def test_storage_migration_project_schema_stable(self):
        self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required']); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged'])
    def test_contracts_and_schemas(self):
        self.assertEqual(MAN['reconciliation_schema'],'sc-workspace-reconciliation/1.0'); self.assertEqual(MAN['reconciliation_plan_schema'],'sc-workspace-reconciliation-plan/1.0')
        json.loads((ROOT/'schemas/sc-workspace-reconciliation-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-reconciliation-plan-v1.schema.json').read_text())
    def test_public_rest_contract(self):
        self.assertIn('/wp-json/sc-workspace/v1/reconciliation-contract',MAN['rest_routes']); self.assertIn("'/reconciliation-contract'",PHP); self.assertIn('public function reconciliation_contract()',PHP); self.assertIn("'storage_schema_version' => 35",PHP)
    def test_top_level_reconcile_view(self):
        self.assertIn('data-scw-workspace-view="reconcile"',PHP); self.assertIn('data-scw-workspace-section="reconcile"',PHP); self.assertIn("'reconcile'",JS)
    def test_explicit_selection_no_auto_merge(self):
        r=MAN['reconciliation']; self.assertTrue(r['explicit_selection_required']); self.assertFalse(r['automatic_selection']); self.assertFalse(r['automatic_merge']); self.assertFalse(r['automatic_overwrite']); self.assertTrue(r['creates_new_project_copy']); self.assertTrue(r['preserves_both_source_states'])
        for token in ['automaticSelection:false','automaticMerge:false','automaticOverwrite:false','createsNewProjectCopy:true','preservesBothSourceStates:true']: self.assertIn(token,HELP)
    def test_selection_ui_defaults_manual(self):
        self.assertIn('data-scw-reconcile-select-all',PHP); self.assertIn('data-scw-reconcile-clear',PHP); self.assertIn('selected:new Set()',JS); self.assertIn('Nothing is selected automatically.',JS)
    def test_dependency_validation_blocks_invalid_plan(self):
        self.assertTrue(MAN['reconciliation']['dependency_validation']); self.assertIn('function validate(candidate)',HELP); self.assertIn('canCreate:errors.length===0&&blockers.length===0',HELP); self.assertIn('blocking issue',JS)
    def test_reconciled_output_is_new_copy(self):
        self.assertIn('const copy=cloneProject(ctx.result.candidate)',JS); self.assertIn('(Reconciled)',JS); self.assertIn("addActivity(copy,'reconciled'",JS); self.assertNotIn('Object.assign(ctx.project,ctx.result.candidate)',JS)
    def test_human_acknowledgement(self):
        self.assertTrue(MAN['reconciliation']['human_acknowledgement_required']); self.assertIn('data-scw-reconcile-ack',PHP); self.assertIn('reconcileAck?.checked&&activeReconciliation?.result?.canCreate',JS)
    def test_plan_export(self):
        self.assertIn('data-scw-reconcile-export',PHP); self.assertIn('reconciliation-plan-',JS); self.assertIn('sc-workspace-reconciliation-plan/1.0',HELP)
    def test_workspace_level_ledger(self):
        self.assertEqual(MAN['reconciliation']['scope'],'browser-local-workspace-level'); self.assertEqual(MAN['reconciliation']['history_limit'],80); self.assertIn('MAX_RECONCILIATION_HISTORY = 80',JS); self.assertIn('function recordReconciliation',JS)
    def test_v24_migration_preserves_existing_state(self):
        self.assertIn('function migrateV24(raw)',JS); self.assertIn('if (raw.schemaVersion === 24) return migrateV24(raw)',JS)
        seg=JS[JS.index('function migrateV24(raw)'):JS.index('function normalizeState',JS.index('function migrateV24(raw)'))]
        for token in ['raw.accountPersistence','raw.crossDeviceSync','raw.versionHistory','raw.safeActions','reconciliationTemplate()']: self.assertIn(token,seg)
    def test_change_review_integration(self):
        self.assertIn('data-scw-change-reconcile',PHP); self.assertIn('SCWorkspaceProjectDiff',JS); self.assertIn('buildActiveReconciliation',JS)
    def test_registry_lineage(self):
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0620'",REG); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0620'",REG); self.assertIn("LEGACY_PENDING_KEY_V0260",REG); self.assertIn("'previous_version' => '0.61.0'",REG)
    def test_accessibility_and_library_route(self):
        self.assertIn('@media(forced-colors:active)',CSS); self.assertIn('aria-live="polite"',PHP); self.assertEqual(MAN['canonical_library_path'],'/knowledge-libraries/'); self.assertIn('/knowledge-libraries/',PHP)
if __name__=='__main__': unittest.main()
