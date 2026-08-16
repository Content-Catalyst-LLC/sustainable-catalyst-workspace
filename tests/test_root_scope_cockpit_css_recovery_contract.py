from pathlib import Path
import json,re,unittest
R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
M=json.loads((R/'release-manifest-v2.0.3.json').read_text())
W=(P/'includes/class-sc-workspace.php').read_text()
CSS=(P/'assets/css/workspace-v2.0.3.css').read_text()
MAIN=(P/'sustainable-catalyst-workspace.php').read_text()
class RootScopeRecoveryContract(unittest.TestCase):
    def test_release_identity_and_schema_freeze(self):
        self.assertEqual((M['version'],M['previous_version']),('2.0.3','2.0.2'))
        self.assertEqual(M['storage_schema_version'],35)
        self.assertEqual(M['project_schema'],'sc-workspace-project/20.0')
        self.assertEqual(M['export_schema'],'sc-workspace-project-export/20.0')
    def test_live_root_contains_both_scope_classes(self):
        self.assertIn('class="scw-shell scw-root" data-sc-workspace',W)
        self.assertIn('data-release-stage="root-scope-cockpit-recovery"',W)
        self.assertIn("register_rest_route('sc-workspace/v2', '/root-scope-contract'",W)
    def test_scoped_selectors_can_match_live_dom(self):
        root=re.search(r'<section class="([^"]+)" data-sc-workspace',W)
        self.assertIsNotNone(root)
        classes=set(root.group(1).split())
        self.assertTrue({'scw-shell','scw-root'}.issubset(classes))
        for selector in ['.scw-root .scw-project-cockpit','.scw-root .scw-project-cockpit-lanes','.scw-root .scw-project-cockpit-lanes .scw-work-mode-card']:
            self.assertIn(selector,CSS)
    def test_compound_safeguard_and_identity(self):
        self.assertIn('.scw-shell.scw-root .scw-project-cockpit-lanes{display:grid}',CSS)
        self.assertIn('Version: 2.0.3',MAIN)
        self.assertFalse(M['root_scope_cockpit_recovery']['schema_migration_required'])
if __name__=='__main__': unittest.main()
