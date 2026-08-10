import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.49.0.js'
class ClosingCTAContractTests(unittest.TestCase):
    def test_closing_primary_action_is_new_project(self):
        p=PHP.read_text()
        closing=p.split('<section class="scw-editorial-closing"',1)[1].split('</section>',1)[0]
        self.assertIn('data-scw-platform-new-project', closing)
        self.assertIn('>New Project</button>', closing)
        self.assertNotIn('>Open Workspace</a>', closing)
    def test_library_secondary_action_is_canonical(self):
        closing=PHP.read_text().split('<section class="scw-editorial-closing"',1)[1].split('</section>',1)[0]
        self.assertIn("home_url('/knowledge-libraries/')", closing)
        self.assertIn('>Explore the Library</a>', closing)
    def test_page_level_bridge_opens_existing_create_flow(self):
        j=JS.read_text()
        self.assertIn("document.querySelectorAll('[data-scw-platform-new-project]')", j)
        self.assertIn("workspace.querySelector('[data-scw-new-project]')", j)
        self.assertIn("workspace.querySelector('[data-scw-create-form]')", j)
        self.assertIn('trigger.click();', j)
        self.assertIn('form.scrollIntoView', j)
        self.assertIn("prefers-reduced-motion: reduce", j)
    def test_meaningful_upper_open_actions_remain(self):
        p=PHP.read_text()
        self.assertIn('href="#workspace-application">Open Workspace</a>', p)
        self.assertIn('href="#workspace-application">Go to projects</a>', p)
if __name__=='__main__': unittest.main()
