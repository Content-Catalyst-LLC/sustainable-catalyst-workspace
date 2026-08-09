from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.31.0.js').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.31.0.css').read_text()
REG=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
MANIFEST=json.loads((ROOT/'release-manifest-v0.31.0.json').read_text())

class StabilityAccessibilityReleaseReadiness(unittest.TestCase):
    def test_release_metadata_and_schema_stability(self):
        self.assertEqual(MANIFEST['version'],'0.31.0')
        self.assertEqual(MANIFEST['previous_version'],'0.30.0')
        self.assertEqual(MANIFEST['release_name'],'Public Beta Hardening & Field Diagnostics')
        self.assertEqual(MANIFEST['storage_schema_version'],27)
        self.assertEqual(MANIFEST['project_schema'],'sc-workspace-project/12.0')
        self.assertFalse(MANIFEST['schema_migration_required'])
    def test_public_readiness_contract(self):
        self.assertIn("'/readiness-contract'",PHP)
        self.assertIn('public function readiness_contract()',PHP)
        self.assertIn("'schema' => 'sc-workspace-release-readiness-contract/1.0'",PHP)
    def test_last_known_good_snapshot_contract(self):
        self.assertIn("const LAST_GOOD_KEY = 'sc_workspace_last_good_v1'",JS)
        self.assertIn('function captureLastGoodSnapshot()',JS)
        self.assertIn("schema: 'sc-workspace-last-known-good/1.0'",JS)
    def test_damaged_state_falls_back_visibly(self):
        self.assertIn('const recovered = readLastGoodState()',JS)
        self.assertIn('restored the last-known-good local snapshot',JS)
        self.assertIn('quarantine(current',JS)
    def test_write_is_verified(self):
        self.assertIn('captureLastGoodSnapshot();',JS)
        self.assertIn('const verified = window.localStorage.getItem(STORAGE_KEY)',JS)
        self.assertIn("throw new Error('read-after-write verification failed')",JS)
    def test_diagnostic_export_is_privacy_minimized(self):
        self.assertIn("const READINESS_DIAGNOSTIC_SCHEMA = 'sc-workspace-diagnostic-report/1.0'",JS)
        self.assertIn('projectContentIncluded: false',JS)
        self.assertIn('objectContentIncluded: false',JS)
        self.assertIn('sourceUrlsIncluded: false',JS)
        self.assertIn('deviceIdentifierIncluded: false',JS)
        self.assertFalse(MANIFEST['governance']['diagnostic_export_includes_project_content'])
    def test_diagnostics_are_local_and_no_telemetry(self):
        self.assertIn('automaticTelemetry: false',JS)
        self.assertTrue(MANIFEST['readiness']['diagnostics_local_only'])
        self.assertFalse(MANIFEST['readiness']['automatic_telemetry'])
        self.assertFalse(MANIFEST['governance']['automatic_telemetry'])
    def test_diagnostic_checks_are_inspectable(self):
        for marker in ['browserStorageAvailable','currentStateSerializable','lastKnownGoodSnapshotAvailable','webCryptoSha256Available','reducedMotionPreferred','browserOnline','approximateWorkspaceBytes']:
            self.assertIn(marker,JS)
    def test_emergency_backup_is_explicit_and_device_minimized(self):
        self.assertIn("const EMERGENCY_BACKUP_SCHEMA = 'sc-workspace-emergency-backup/1.0'",JS)
        self.assertIn('includesProjectContent: true',JS)
        self.assertIn('deviceIdentifierIncluded: false',JS)
        self.assertIn('data-scw-emergency-backup',PHP)
        self.assertTrue(MANIFEST['readiness']['emergency_backup_explicit_only'])
    def test_readiness_ui_is_accessible(self):
        for marker in ['data-scw-readiness-status','aria-live="polite"','data-scw-run-diagnostics','data-scw-export-diagnostics']:
            self.assertIn(marker,PHP)
    def test_skip_link_and_view_focus(self):
        self.assertIn('scw-skip-link',PHP)
        self.assertIn('href="#scw-workspace-main"',PHP)
        self.assertIn('setWorkspaceView(view, moveFocus = false)',JS)
        self.assertIn("heading.focus({ preventScroll: true })",JS)
    def test_reduced_motion_support(self):
        self.assertIn('function prefersReducedMotion()',JS)
        self.assertIn('(prefers-reduced-motion: reduce)',JS)
        self.assertIn('@media(prefers-reduced-motion:reduce)',CSS)
    def test_visible_focus_and_forced_colors_support(self):
        self.assertIn(':focus-visible',CSS)
        self.assertIn('@media(forced-colors:active)',CSS)
        self.assertEqual(MANIFEST['readiness']['accessibility_target'],'WCAG 2.2 AA')
    def test_release_keeps_cloud_and_behavioral_boundaries(self):
        self.assertEqual(MANIFEST['cloud_sync'],'explicit-project-enrollment')
        self.assertEqual(MANIFEST['server_project_storage'],'manual-backup-plus-explicit-sync-head')
        self.assertFalse(MANIFEST['governance']['behavioral_telemetry'])
        self.assertFalse(MANIFEST['governance']['productivity_score'])
    def test_registry_lineage_advances_with_safe_actions_storage_migration(self):
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0310'",REG)
        self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0310'",REG)
        self.assertIn("LEGACY_PENDING_KEY_V0260 = 'sc_workspace_registry_pending_v0260'",REG)
        self.assertIn("LEGACY_PENDING_KEY_V0240 = 'sc_workspace_registry_pending_v0240'",REG)
        self.assertIn("LEGACY_PENDING_KEY_V0200 = 'sc_workspace_registry_pending_v0200'",REG)
        self.assertIn("'previous_version' => '0.30.0'",REG)
    def test_canonical_library_route_is_unchanged(self):
        self.assertEqual(MANIFEST['canonical_library_path'],'/knowledge-libraries/')
        self.assertIn('/knowledge-libraries/',PHP)

if __name__=='__main__': unittest.main()
