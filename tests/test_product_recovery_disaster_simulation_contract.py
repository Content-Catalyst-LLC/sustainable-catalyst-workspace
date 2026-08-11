import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.69.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.69.0.json').read_text())
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
JS=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-recovery-disaster-simulation-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-recovery-disaster-simulation-ui-v1.js').read_text()
NAV=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
class RecoveryDisasterContract(unittest.TestCase):
    def test_release_lineage_and_schema_stability(self):
        self.assertEqual(MAN['version'],'0.69.0'); self.assertEqual(MAN['previous_version'],'0.68.0')
        self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required'])
    def test_sandboxed_governance(self):
        x=MAN['product_recovery_disaster_simulation']; self.assertEqual(x['scenario_count'],8); self.assertTrue(x['sandboxed_failure_injection']); self.assertFalse(x['production_data_injection'])
        for k in ['canonical_mutation','automatic_repair','automatic_restore','automatic_import_commit','automatic_sync','background_network','automatic_submission']: self.assertFalse(x[k])
    def test_scenarios_and_surface(self):
        for marker in ['corrupt-state','interrupted-write','storage-exhaustion','malformed-import','stale-restore','sync-conflict','missing-reference','future-version']: self.assertIn(marker,JS)
        self.assertIn('data-scw-recovery-drills',PHP); self.assertIn("'recovery-drills':'Recovery Drills'",NAV); self.assertIn('SCWorkspaceRecoveryDisasterSimulation',UI)
    def test_registry(self):
        self.assertEqual(REG['public_version'],'0.69.0'); self.assertIn('product_recovery_disaster_simulation',REG)
if __name__=='__main__': unittest.main()
