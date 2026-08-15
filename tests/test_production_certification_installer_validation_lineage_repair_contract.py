import json, shutil, sys, tempfile, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from release_lineage import current_release, load_manifest, load_registry, validate_current_release_lineage

class InstallerValidationLineageRepair(unittest.TestCase):
    def test_01_current_release_detected_from_plugin(self):
        self.assertEqual(current_release(R).version,'0.82.1')
    def test_02_predecessor_is_v0820(self):
        self.assertEqual(current_release(R).previous_version,'0.82.0')
    def test_03_current_manifest_registry_agree(self):
        cur=current_release(R); man=json.loads(cur.manifest_path.read_text()); reg=json.loads(cur.registry_path.read_text())
        self.assertEqual((man['version'],man['previous_version']),('0.82.1','0.82.0'))
        self.assertEqual((reg['installed_version'],reg['public_version'],reg['previous_version']),('0.82.1','0.82.1','0.82.0'))
    def test_04_current_cumulative_assets_exist(self):
        cur=current_release(R); self.assertTrue(cur.script_path.exists()); self.assertTrue(cur.style_path.exists()); self.assertEqual(cur.asset_handle,'sc-workspace-v0821')
    def test_05_lineage_gate_passes_current_tree(self):
        result=validate_current_release_lineage(R,'0.82.1','0.82.0'); self.assertTrue(result['ok'],result['errors'])
    def test_06_historical_v0820_is_frozen(self):
        man=load_manifest(R,'0.82.0'); reg=load_registry(R,'0.82.0')
        self.assertEqual((man['version'],man['previous_version'],man['release_name']),('0.82.0','0.81.0','Production Smoke, Cache & Rollback Certification'))
        self.assertEqual((reg['public_version'],reg['previous_version']),('0.82.0','0.81.0'))
    def test_07_no_rest_or_schema_expansion(self):
        cur=load_manifest(R,'0.82.1'); old=load_manifest(R,'0.82.0')
        self.assertEqual(cur['rest_routes'],old['rest_routes']); self.assertEqual(cur['storage_schema_version'],35); self.assertEqual(cur['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(cur['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(cur['schema_migration_required'])
    def test_08_security_gate_derives_current_release(self):
        text=(R/'scripts/validate_security_privacy_audit_ii.py').read_text()
        self.assertIn('current_release(R)',text); self.assertIn('CUR.script_path',text); self.assertNotIn('workspace-v0.82.0.js',text); self.assertNotIn("Version: 0.82.0",text)
    def test_09_inherited_deployment_and_production_gates_are_dynamic(self):
        for name in ['validate_wordpress_deployment_hardening.py','validate_production_smoke_cache_rollback_certification.py']:
            text=(R/'scripts'/name).read_text(); self.assertIn('current_release(R)',text)
    def test_10_live_runtime_predecessors_advance(self):
        dep=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text()
        prod=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php').read_text()
        self.assertIn("PREVIOUS_RELEASE = '0.82.0'",dep); self.assertIn("PREVIOUS_RELEASE = '0.82.0'",prod)
    def test_11_registry_retry_includes_failed_release_state(self):
        text=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0821'",text); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0821'",text); self.assertIn('LEGACY_PENDING_KEY_V0820',text)
    def test_12_compact_wordpress_header(self):
        raw=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_bytes()
        self.assertLess(raw.find(b'Version:'),512); self.assertLess(raw.find(b'Requires PHP:'),512); self.assertIn(b'Version: 0.82.1',raw[:8192])
    def test_13_stale_archive_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); plugin=root/'wordpress/sustainable-catalyst-workspace'; (plugin/'assets/js').mkdir(parents=True); (plugin/'assets/css').mkdir(parents=True); (plugin/'includes').mkdir(parents=True); (root/'registry').mkdir()
            # Construct a coherent stale v0.82.0 tree and ask the verifier to require v0.82.1.
            shutil.copy2(R/'history/release-manifest-v0.82.0.json',root/'release-manifest-v0.82.0.json')
            shutil.copy2(R/'history/workspace-product-record-v0.82.0.json',root/'registry/workspace-product-record-v0.82.0.json')
            for rel in ['sustainable-catalyst-workspace.php','includes/class-sc-workspace.php','includes/class-sc-workspace-deployment.php','includes/class-sc-workspace-production-certification.php']:
                src=plugin/rel; src.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(R/'wordpress/sustainable-catalyst-workspace'/rel,src)
            main=plugin/'sustainable-catalyst-workspace.php'; t=main.read_text().replace('0.82.1','0.82.0'); main.write_text(t)
            shutil.copy2(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.82.0.js',plugin/'assets/js/workspace-v0.82.0.js')
            shutil.copy2(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.82.0.css',plugin/'assets/css/workspace-v0.82.0.css')
            result=validate_current_release_lineage(root,'0.82.1','0.82.0')
            self.assertFalse(result['ok']); self.assertTrue(any('expected 0.82.1' in e for e in result['errors']))
    def test_14_repair_policy_blocks_commit_push_on_mismatch(self):
        p=load_manifest(R,'0.82.1')['production_certification_installer_validation_lineage_repair']
        self.assertTrue(p['source_archive_lineage_preflight']); self.assertTrue(p['post_rsync_lineage_gate']); self.assertTrue(p['pre_commit_lineage_gate']); self.assertTrue(p['no_commit_on_lineage_failure']); self.assertTrue(p['no_push_on_lineage_failure']); self.assertEqual(p['rollback_release'],'0.81.0')

if __name__=='__main__': unittest.main()
