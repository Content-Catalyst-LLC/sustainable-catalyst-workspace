import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.70.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.70.0.json').read_text())
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-iii-ui-v1.js').read_text()
NAV=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v1.7.0.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v1.7.0.css').read_text()

class PublicProductBetaIIIContract(unittest.TestCase):
    def test_release_lineage_and_schema_stability(self):
        self.assertEqual(MAN['version'],'0.70.0')
        self.assertEqual(MAN['previous_version'],'0.69.0')
        self.assertEqual(MAN['release_name'],'Public Product Beta III')
        self.assertEqual(MAN['storage_schema_version'],35)
        self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0')
        self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0')
        self.assertFalse(MAN['schema_migration_required'])
    def test_nine_stage_journey_and_governance(self):
        beta=MAN['public_product_beta_iii']
        ids=[x['id'] for x in beta['journey']]
        self.assertEqual(ids,['discover','capture','organize','analyze','synthesize','decide','compose','review','export-handoff'])
        self.assertEqual(beta['step_count'],9)
        self.assertEqual(beta['manual_walkthrough_storage'],'sessionStorage')
        self.assertFalse(beta['manual_walkthrough_persistent'])
        self.assertTrue(beta['topology_check_local_only'])
        self.assertTrue(beta['privacy_minimized_report'])
        for k in ['hidden_readiness_score','automatic_completion','behavioral_tracking','automatic_telemetry','automatic_submission','canonical_mutation']:
            self.assertFalse(beta[k],k)
    def test_product_journey_is_routed_and_visible(self):
        self.assertIn("views:['start','journey','help']",NAV)
        self.assertIn("journey:'Product Journey'",NAV)
        self.assertIn("data-scw-workspace-view=\"journey\"",PHP)
        self.assertIn('data-scw-public-beta-iii',PHP)
        self.assertIn('PUBLIC PRODUCT BETA III / PRODUCT JOURNEY',PHP)
        self.assertIn('data-scw-open-product-journey',PHP)
        self.assertIn('Object.values(navApi.AREAS||{})',APP)
        self.assertIn('/* v0.70.0 — Public Product Beta III */',CSS)
    def test_helper_and_ui_boundaries(self):
        for marker in ['discover','capture','organize','analyze','synthesize','decide','compose','review','export-handoff']:
            self.assertIn(marker,JS)
        self.assertIn("SESSION_KEY='sc_workspace_public_beta_iii_journey_v0700'",JS)
        self.assertIn('session-only',JS)
        self.assertIn('hiddenScore:false',JS)
        self.assertIn('behavioralTracking:false',JS)
        self.assertIn('SCWorkspacePublicBetaIII',UI)
        self.assertIn('Reviewed in this session',UI)
    def test_rest_registry_and_history(self):
        self.assertIn("'/public-product-beta-iii-contract'",PHP)
        self.assertIn('/wp-json/sc-workspace/v1/public-product-beta-iii-contract',MAN['rest_routes'])
        self.assertEqual(REG['public_version'],'0.70.0')
        self.assertEqual(REG['previous_version'],'0.69.0')
        self.assertEqual(REG['release_name'],'Public Product Beta III')
        self.assertIn('public_product_beta_iii',REG)
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v170'",REGPHP)
        self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v170'",REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0690',REGPHP)
        self.assertTrue((R/'history/release-manifest-v0.69.0.json').exists())
        self.assertTrue((R/'history/workspace-product-record-v0.69.0.json').exists())

if __name__=='__main__': unittest.main()
