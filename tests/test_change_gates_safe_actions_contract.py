import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.25.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.25.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-safe-actions-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.25.0.css').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()

class ChangeGatesSafeActionsContract(unittest.TestCase):
    def test_release_lineage_and_storage_migration(self):
        self.assertEqual(MAN['version'],'0.25.0'); self.assertEqual(MAN['previous_version'],'0.24.0')
        self.assertEqual(MAN['release_name'],'Change Gates & Safe Actions')
        self.assertEqual(MAN['storage_schema_version'],24); self.assertEqual(MAN['project_schema'],'sc-workspace-project/11.0')
        self.assertTrue(MAN['schema_migration_required']); self.assertEqual(MAN['migration']['storage_from'],23); self.assertEqual(MAN['migration']['storage_to'],24)
        self.assertTrue(MAN['migration']['initializes_safe_actions']); self.assertTrue(MAN['migration']['project_schema_unchanged'])
    def test_contract_schemas(self):
        self.assertEqual(MAN['safe_actions_schema'],'sc-workspace-safe-actions/1.0')
        self.assertEqual(MAN['action_gate_schema'],'sc-workspace-action-gate/1.0')
        json.loads((ROOT/'schemas/sc-workspace-safe-actions-v1.schema.json').read_text())
    def test_public_rest_contract(self):
        self.assertIn('/wp-json/sc-workspace/v1/safe-actions-contract',MAN['rest_routes'])
        self.assertIn("'/safe-actions-contract'",PHP); self.assertIn('public function safe_actions_contract()',PHP)
        self.assertIn("'storage_schema_version' => 24",PHP)
    def test_all_high_risk_actions_are_gated(self):
        expected=['restore-copy','sync-resolve-local','sync-resolve-cloud','share-portable','share-review-copy','institutional-promotion']
        self.assertEqual(MAN['safe_actions']['gated_actions'],expected)
        for action in expected: self.assertIn("'%s'"%action,HELP)
    def test_human_acknowledgement_and_no_auto_governance(self):
        s=MAN['safe_actions']; g=MAN['governance']
        self.assertTrue(s['human_acknowledgement_required']); self.assertTrue(g['safe_action_human_acknowledgement_required'])
        self.assertFalse(s['automatic_proceed']); self.assertFalse(s['automatic_apply']); self.assertFalse(s['automatic_merge']); self.assertFalse(s['hidden_risk_score'])
        self.assertFalse(g['safe_action_automatic_proceed']); self.assertFalse(g['safe_action_automatic_apply']); self.assertFalse(g['safe_action_automatic_merge']); self.assertFalse(g['safe_action_hidden_risk_score'])
    def test_top_level_safety_view_and_modal(self):
        self.assertIn('data-scw-workspace-view="safety"',PHP); self.assertIn('data-scw-workspace-section="safety"',PHP)
        self.assertIn('data-scw-action-gate',PHP); self.assertIn('data-scw-action-gate-ack',PHP); self.assertIn('data-scw-action-gate-proceed',PHP)
        self.assertIn("'safety'",JS)
    def test_restore_is_gated(self):
        self.assertIn("action:'restore-copy'",JS); self.assertIn('await openSafeActionGate',JS)
        self.assertIn("kind:'restore-point'",JS); self.assertIn("kind:'current-project'",JS)
    def test_sync_conflict_resolutions_are_gated(self):
        self.assertIn("action:'sync-resolve-local'",JS); self.assertIn("action:'sync-resolve-cloud'",JS)
        self.assertIn("kind:'cloud-revision'",JS); self.assertTrue(MAN['safe_actions']['sync_revision_preconditions_preserved'])
        self.assertTrue(MAN['governance']['sync_revision_precondition_required'])
    def test_share_and_institutional_exports_are_gated(self):
        self.assertIn("gateFromLatestRestore('share-portable'",JS); self.assertIn("gateFromLatestRestore('share-review-copy'",JS)
        self.assertIn("gateFromLatestRestore('institutional-promotion'",JS)
    def test_latest_restore_baseline_is_explicit(self):
        self.assertIn('function latestRestorePoint',JS); self.assertIn("{kind:'none',label:'No named restore point'}",JS)
        self.assertIn('function gateFromLatestRestore',JS)
    def test_gate_uses_project_diff_not_hidden_score(self):
        self.assertIn('SCWorkspaceProjectDiff',JS); self.assertIn('reviewSummary',HELP)
        self.assertIn('hiddenRiskScore:false',HELP); self.assertIn('automaticMerge:false',HELP); self.assertIn('automaticApply:false',HELP)
    def test_local_safe_action_ledger(self):
        self.assertEqual(MAN['safe_actions']['storage_scope'],'browser-local-workspace-level'); self.assertEqual(MAN['safe_actions']['history_limit'],120)
        self.assertIn('MAX_SAFE_ACTION_HISTORY = 120',JS); self.assertIn('function recordSafeAction',JS); self.assertIn('helper.historyRecord',JS)
    def test_v23_migration_preserves_cloud_history(self):
        self.assertIn('function migrateV23(raw)',JS); self.assertIn('if (raw.schemaVersion === 23) return migrateV23(raw)',JS)
        segment=JS[JS.index('function migrateV23(raw)'):JS.index('function normalizeState',JS.index('function migrateV23(raw)'))]
        for token in ['raw.accountPersistence','raw.crossDeviceSync','raw.versionHistory','safeActionsTemplate()']: self.assertIn(token,segment)
    def test_change_review_contract_remains_available(self):
        self.assertIn('/wp-json/sc-workspace/v1/change-review-contract',MAN['rest_routes']); self.assertIn('sc-workspace-project-diff-v1.js',PHP)
        self.assertIn('cloud-revision',MAN['change_review']['sources'])
    def test_registry_lineage(self):
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0250'",REG); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0250'",REG)
        self.assertIn("LEGACY_PENDING_KEY_V0240 = 'sc_workspace_registry_pending_v0240'",REG); self.assertIn("'previous_version' => '0.24.0'",REG)
    def test_accessibility_and_forced_colors(self):
        self.assertIn('.scw-action-gate',CSS); self.assertIn('@media(forced-colors:active)',CSS)
        self.assertIn('aria-live="polite"',PHP); self.assertIn('role="dialog"',PHP)
    def test_canonical_library_route(self):
        self.assertEqual(MAN['canonical_library_path'],'/knowledge-libraries/'); self.assertIn('/knowledge-libraries/',PHP)

if __name__=='__main__': unittest.main()
