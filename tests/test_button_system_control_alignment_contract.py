from pathlib import Path
import json
import unittest

R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
m=json.loads((R/'release-manifest-v2.0.1.json').read_text())
old=json.loads((R/'release-manifest-v2.0.0.json').read_text())
reg=json.loads((R/'registry/workspace-product-record-v2.0.1.json').read_text())
main=(P/'sustainable-catalyst-workspace.php').read_text()
php=(P/'includes/class-sc-workspace.php').read_text()
dep=(P/'includes/class-sc-workspace-deployment.php').read_text()
css=(P/'assets/css/workspace-v2.0.1.css').read_text()

class ButtonSystemControlAlignmentContract(unittest.TestCase):
    def test_release_identity_and_schema_freeze(self):
        self.assertEqual((m['version'],m['previous_version']),('2.0.1','2.0.0'))
        self.assertEqual((reg['public_version'],reg['previous_version']),('2.0.1','2.0.0'))
        self.assertEqual((m['storage_schema_version'],m['project_schema'],m['export_schema']),(old['storage_schema_version'],old['project_schema'],old['export_schema']))
        self.assertIn('Version: 2.0.4',main); self.assertIn("SC_WORKSPACE_VERSION', '2.0.4'",main)
        self.assertIn("PREVIOUS_RELEASE = '2.0.3'",dep); self.assertIn('workspace-v2.0.4.css',dep); self.assertIn('workspace-v2.0.4.js',dep)
    def test_button_contract_boundaries(self):
        b=m['button_system_repair']
        self.assertEqual(b['desktop_minimum_control_height_px'],40); self.assertEqual(b['touch_minimum_control_height_px'],44)
        self.assertTrue(b['focus_visible']); self.assertTrue(b['forced_colors_supported']); self.assertTrue(b['connected_product_actions_use_intentional_grid']); self.assertTrue(b['status_outputs_are_information_surfaces'])
        self.assertFalse(b['javascript_behavior_change']); self.assertFalse(b['canonical_content_mutation']); self.assertFalse(b['schema_migration_required'])
    def test_css_repairs_pdf_observed_controls(self):
        for marker in ['/* v2.0.1 — Button System, Control Alignment & Interaction-State Repair */','--scw-control-height:40px','.scw-connected-knowledge .scw-collab-contract-actions','[data-scw-connected-export]{grid-column:1/-1}','background:#f7f7f4','cursor:not-allowed','@media (forced-colors:active)']:
            self.assertIn(marker,css)
        self.assertIn("register_rest_route('sc-workspace/v2', '/button-system-contract'",php)
        self.assertIn('data-release-stage="visual-regression-theme-isolation"',php)

if __name__=='__main__': unittest.main()
