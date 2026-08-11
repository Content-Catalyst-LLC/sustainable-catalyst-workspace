import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = json.loads((ROOT / 'release-manifest-v0.66.0.json').read_text())
REG = json.loads((ROOT / 'registry/workspace-product-record-v0.66.0.json').read_text())
JS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
PHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN = (ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
REGPHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
CAPTURE = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-source-capture-v1.js').read_text()
NOTEBOOK = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()

class SourceCaptureResearchClippingContract(unittest.TestCase):
    def test_01_release_lineage(self):
        self.assertEqual((MAN['version'], MAN['previous_version'], MAN['release_name']), ('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'))
        self.assertIn('Version: 0.68.0', MAIN)

    def test_02_schema_migration(self):
        self.assertEqual((MAN['storage_schema_version'], MAN['project_schema'], MAN['export_schema']), (35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'))
        self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35))
        self.assertEqual((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to']),('sc-workspace-project/20.0','sc-workspace-project/20.0'))
        self.assertTrue(MAN['migration']['project_schema_unchanged'])

    def test_03_source_capture_contract_schemas(self):
        sc = MAN['source_capture']
        self.assertEqual(sc['schema'], 'sc-workspace-source-capture-inbox/1.0')
        self.assertEqual(sc['request_schema'], 'sc-workspace-notebook-capture-request/1.0')
        self.assertEqual(sc['provenance_schema'], 'sc-workspace-source-capture/1.0')
        self.assertEqual(sc['bibliographic_context_schema'], 'sc-workspace-bibliographic-context/1.0')

    def test_04_schema_files_load(self):
        names = (
            'sc-workspace-bibliographic-context-v1.schema.json',
            'sc-workspace-source-capture-v1.schema.json',
            'sc-workspace-notebook-capture-request-v1.schema.json',
            'sc-workspace-source-capture-inbox-v1.schema.json',
            'sc-workspace-notebook-block-v2.schema.json',
            'sc-workspace-notebook-v2.schema.json',
            'sc-workspace-notebook-workspace-v2.schema.json',
            'sc-workspace-project-v14.schema.json',
        )
        for name in names:
            json.loads((ROOT / 'schemas' / name).read_text())

    def test_05_surfaces_and_capture_types(self):
        sc = MAN['source_capture']
        self.assertEqual(sc['source_surfaces'], ['manual','knowledge-library','research-librarian','external-web','document','workspace-object','other'])
        self.assertEqual(sc['capture_types'], ['source','excerpt','note','question','claim','reference','attachment'])

    def test_06_manual_capture_ui(self):
        for token in ('Save capture to active section','Capture inbox','data-scw-notebook-capture-form','data-scw-notebook-capture-import','data-scw-notebook-capture-file'):
            self.assertIn(token, PHP)
        self.assertIn('saveCaptureToActiveSection', JS)

    def test_07_capture_inbox_is_explicit_and_bounded(self):
        sc = MAN['source_capture']
        self.assertEqual(sc['max_inbox_requests'], 100)
        self.assertTrue(sc['incoming_capture_requires_explicit_save'])
        self.assertTrue(sc['capture_inbox_workspace_level'])
        self.assertTrue(sc['capture_blocks_project_bound_after_save'])
        self.assertIn('MAX_SOURCE_CAPTURE_INBOX = 100', JS)

    def test_08_same_origin_capture_adapter(self):
        self.assertIn("const MESSAGE_TYPE='sc-workspace-notebook-capture'", CAPTURE)
        self.assertIn("const SESSION_KEY='sc_workspace_notebook_capture_v1'", CAPTURE)
        self.assertIn('postMessage', CAPTURE)
        self.assertIn('event.origin!==window.location.origin', JS)

    def test_09_research_content_not_in_handoff_url(self):
        self.assertFalse(MAN['source_capture']['research_content_in_handoff_url'])
        self.assertFalse(MAN['governance']['source_capture_content_in_handoff_url'])
        self.assertIn("'/platform/?scw-notebook-capture=1'", CAPTURE)

    def test_10_portable_capture_request_import(self):
        self.assertTrue(MAN['source_capture']['portable_json_capture_request'])
        self.assertIn('sc-workspace-notebook-capture-request/1.0', JS)
        self.assertIn('Portable capture request imported', JS)

    def test_11_no_automatic_fetch_or_ai(self):
        sc = MAN['source_capture']
        self.assertFalse(sc['automatic_remote_fetch'])
        self.assertFalse(sc['automatic_page_scraping'])
        self.assertFalse(sc['automatic_metadata_inference'])
        self.assertFalse(sc['automatic_ai'])
        self.assertFalse(sc['automatic_upload'])

    def test_12_notebook_v2_preserves_capture_context(self):
        for token in ('sc-workspace-notebook-workspace/8.0','sc-workspace-notebook-block/3.0','blockFromCapture','citationLine','bibliography','capture'):
            self.assertIn(token, NOTEBOOK)
        self.assertTrue(MAN['migration']['upgrades_notebook_blocks_to_v2'])
        self.assertTrue(MAN['migration']['preserves_existing_notebooks'])

    def test_13_public_rest_contract(self):
        self.assertIn('/wp-json/sc-workspace/v1/source-capture-contract', MAN['rest_routes'])
        self.assertIn("'/source-capture-contract'", PHP)
        self.assertIn('public function source_capture_contract()', PHP)
        self.assertIn("'automatic_remote_fetch' => false", PHP)
        self.assertIn("'incoming_capture_requires_explicit_save' => true", PHP)

    def test_14_capture_adapter_public_helper(self):
        self.assertIn('sc_workspace_source_capture_adapter_script_url', MAIN)
        self.assertIn('sc-workspace-source-capture-v1.js', MAIN)
        self.assertIn("'sc-workspace-source-capture-v1'", PHP)
        self.assertIn("'sc-workspace-research-notebook-v8'", PHP)

    def test_15_library_and_research_librarian_are_contract_surfaces(self):
        self.assertIn('knowledge-library', MAN['source_capture']['source_surfaces'])
        self.assertIn('research-librarian', MAN['source_capture']['source_surfaces'])
        self.assertEqual(MAN['canonical_library_path'], '/knowledge-libraries/')
        self.assertIn('/knowledge-libraries/', PHP)

    def test_16_registry_and_history(self):
        self.assertEqual((REG['public_version'], REG['previous_version']), ('0.66.0','0.65.0'))
        self.assertIn('Import, Export & Backward-Compatibility Hardening', REG['change_summary'])
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0680'", REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0320', REGPHP)
        self.assertTrue((ROOT / 'history/release-manifest-v0.32.0.json').exists())
        self.assertTrue((ROOT / 'history/workspace-product-record-v0.32.0.json').exists())

if __name__ == '__main__':
    unittest.main()
