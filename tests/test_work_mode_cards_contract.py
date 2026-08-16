from pathlib import Path
import json
import unittest

R = Path(__file__).resolve().parents[1]
P = R / 'wordpress/sustainable-catalyst-workspace'
M = json.loads((R / 'release-manifest-v2.0.2.json').read_text())
C = (P / 'includes/class-sc-workspace-work-mode-cards.php').read_text()
W = (P / 'includes/class-sc-workspace.php').read_text()
CSS = (P / 'assets/css/workspace-v2.0.2.css').read_text()
JS = (P / 'assets/js/workspace-v2.0.2.js').read_text()

class WorkModeCardsContract(unittest.TestCase):
    def test_release_identity_and_freeze(self):
        self.assertEqual(M['version'], '2.0.2')
        self.assertEqual(M['previous_version'], '2.0.1')
        self.assertEqual(M['release_name'], 'Work Mode Cards, Cockpit Hierarchy & Navigation-State Repair')
        self.assertEqual(M['storage_schema_version'], 35)
        self.assertEqual(M['project_schema'], 'sc-workspace-project/20.0')
        self.assertEqual(M['export_schema'], 'sc-workspace-project-export/20.0')

    def test_card_contract_and_markup(self):
        w = M['work_mode_cards_repair']
        self.assertEqual(w['modes'], ['objects', 'analysis', 'decision', 'briefing'])
        self.assertTrue(w['disabled_without_active_project'])
        self.assertTrue(w['explicit_active_state'])
        self.assertEqual(W.count('class="scw-work-mode-card"'), 4)
        self.assertEqual(W.count('data-scw-work-mode-action'), 4)
        self.assertIn("register_rest_route('sc-workspace/v2', '/work-mode-cards-contract'", W)
        self.assertIn('SC_Workspace_Work_Mode_Cards::contract()', W)

    def test_visual_navigation_states(self):
        for marker in ['grid-auto-rows:1fr', 'min-height:132px', 'scw-work-mode-card.is-active', 'scw-work-mode-card:disabled', 'scw-work-mode-card:focus-visible', '@media(forced-colors:active)']:
            self.assertIn(marker, CSS)
        for marker in ['syncCockpitModeCards', 'aria-pressed', 'aria-current', 'Choose project', 'Open →']:
            self.assertIn(marker, JS)

    def test_surgical_boundary(self):
        w = M['work_mode_cards_repair']
        self.assertFalse(w['routing_semantics_changed'])
        self.assertFalse(w['canonical_content_mutation'])
        self.assertFalse(w['schema_migration_required'])

if __name__ == '__main__':
    unittest.main()
