import json, shutil, sys, tempfile, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage

class InstallerValidationLineageRepair(unittest.TestCase):
    def test_01_current_release_discovery_is_not_pinned(self):
        self.assertEqual(current_release(R).version,'1.4.0')
        self.assertEqual(current_release(R).previous_version,'1.3.0')
    def test_02_historical_v0821_is_frozen(self):
        man=load_manifest(R,'0.82.1'); reg=load_registry(R,'0.82.1')
        self.assertEqual((man['version'],man['previous_version'],man['release_name']),('0.82.1','0.82.0','Production Certification Installer & Validation Lineage Repair'))
        self.assertEqual((reg['installed_version'],reg['public_version'],reg['previous_version']),('0.82.1','0.82.1','0.82.0'))
    def test_03_historical_v0821_no_rest_or_schema_expansion(self):
        cur=load_manifest(R,'0.82.1'); old=load_manifest(R,'0.82.0')
        self.assertEqual(cur['rest_routes'],old['rest_routes']); self.assertEqual(cur['storage_schema_version'],35); self.assertEqual(cur['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(cur['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(cur['schema_migration_required'])
    def test_04_current_cumulative_assets_exist(self):
        cur=current_release(R); self.assertTrue(cur.script_path.exists()); self.assertTrue(cur.style_path.exists()); self.assertEqual(cur.asset_handle,'sc-workspace-v140')
    def test_05_lineage_gate_passes_current_tree(self):
        result=validate_current_release_lineage(R,'1.4.0','1.3.0'); self.assertTrue(result['ok'],result['errors'])
    def test_06_security_gate_derives_current_release(self):
        text=(R/'scripts/validate_security_privacy_audit_ii.py').read_text(); self.assertIn('current_release(R)',text); self.assertIn('CUR.script_path',text)
    def test_07_inherited_deployment_and_production_gates_are_dynamic(self):
        for name in ['validate_wordpress_deployment_hardening.py','validate_production_smoke_cache_rollback_certification.py']:
            text=(R/'scripts'/name).read_text(); self.assertIn('current_release(R)',text)
    def test_08_v0821_validator_is_historical_safe(self):
        text=(R/'scripts/validate_production_certification_installer_validation_lineage_repair.py').read_text()
        self.assertNotIn("validate_current_release_lineage(R,'0.82.1','0.82.0')",text)
        self.assertIn("load_manifest(R,'0.82.1')",text)
    def test_09_live_runtime_predecessors_advance(self):
        dep=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text(); prod=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php').read_text()
        self.assertIn("PREVIOUS_RELEASE = '1.3.0'",dep); self.assertIn("PREVIOUS_RELEASE = '1.3.0'",prod)
    def test_10_registry_retry_includes_v0821_legacy_state(self):
        text=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v140'",text); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v140'",text); self.assertIn('LEGACY_PENDING_KEY_V0821',text)
    def test_11_compact_wordpress_header(self):
        raw=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_bytes(); self.assertLess(raw.find(b'Version:'),512); self.assertLess(raw.find(b'Requires PHP:'),512); self.assertIn(b'Version: 1.4.0',raw[:8192])
    def test_12_historical_repair_policy_still_blocks_mismatch(self):
        p=load_manifest(R,'0.82.1')['production_certification_installer_validation_lineage_repair']
        self.assertTrue(p['source_archive_lineage_preflight']); self.assertTrue(p['post_rsync_lineage_gate']); self.assertTrue(p['pre_commit_lineage_gate']); self.assertTrue(p['no_commit_on_lineage_failure']); self.assertTrue(p['no_push_on_lineage_failure']); self.assertEqual(p['rollback_release'],'0.81.0')
    def test_13_stale_current_identity_is_rejected(self):
        # The current verifier must reject a wrong required version even when the source tree itself is coherent.
        result=validate_current_release_lineage(R,'0.82.1','0.82.0')
        self.assertFalse(result['ok']); self.assertTrue(any('expected 0.82.1' in e or 'expected 0.82.0' in e for e in result['errors']))
if __name__=='__main__': unittest.main()
