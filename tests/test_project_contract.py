import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.2.0.js"


class ProjectPersistenceTests(unittest.TestCase):
    def test_project_schema(self):
        schema = json.loads((ROOT / "schemas/sc-workspace-project-v1.schema.json").read_text())
        self.assertEqual(schema["properties"]["schema"]["const"], "sc-workspace-project/1.0")
        self.assertEqual(schema["properties"]["status"]["enum"], ["active", "paused", "complete"])
        self.assertEqual(schema["properties"]["notes"]["maxLength"], 20000)
        self.assertEqual(schema["properties"]["activity"]["maxItems"], 40)

    def test_local_persistence_and_migration(self):
        js = JS.read_text()
        for token in (
            "const STORAGE_KEY = 'sc_workspace'",
            "const LEGACY_KEY = 'sc_workspace_v0_1'",
            "const STORAGE_VERSION = 2",
            "function migrateLegacyV1",
            "window.localStorage",
            "RECOVERY_KEY",
            "function quarantine",
            "function projectTemplate",
        ):
            self.assertIn(token, js)

    def test_project_operations(self):
        js = JS.read_text()
        for token in (
            "data-scw-new-project",
            "data-scw-duplicate",
            "data-scw-export",
            "data-scw-archive",
            "data-scw-delete",
            "data-scw-import-file",
            "Project restored",
            "Project pinned",
        ):
            self.assertIn(token, js)

    def test_handoff_minimizes_url_content(self):
        js = JS.read_text()
        self.assertIn("sc_workspace_project", js)
        self.assertIn("sc_workspace_origin", js)
        self.assertIn("sc_workspace_return", js)
        self.assertIn("window.sessionStorage.setItem(HANDOFF_KEY", js)
        self.assertNotIn("searchParams.set('sc_workspace_title'", js)
        self.assertNotIn("searchParams.set('sc_workspace_notes'", js)
        self.assertNotIn("searchParams.set('sc_workspace_description'", js)


if __name__ == "__main__":
    unittest.main()
