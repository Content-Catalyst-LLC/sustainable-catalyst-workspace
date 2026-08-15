import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
REF=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reference-library-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class CitationLibraryReferenceManagement(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 0.84.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['schema_stable']); self.assertTrue(json.loads((ROOT/'history/release-manifest-v0.45.0.json').read_text())['migration']['composition_studio_only_release']); self.assertFalse(MAN['migration']['canonical_data_rewrite'])
 def test_03_rest_contract(self): self.assertIn('/wp-json/sc-workspace/v1/citation-library-contract',MAN['rest_routes']); self.assertIn("'/citation-library-contract'",PHP); self.assertIn('public function citation_library_contract()',PHP)
 def test_04_schemas(self):
  self.assertEqual(MAN['reference_schema'],'sc-workspace-reference/1.0'); self.assertEqual(MAN['reference_library_schema'],'sc-workspace-reference-library/1.0'); self.assertEqual(MAN['citation_preferences_schema'],'sc-workspace-citation-preferences/1.0'); self.assertEqual(MAN['reference_library_export_schema'],'sc-workspace-reference-library-export/1.0')
  for name in ('sc-workspace-reference-v1.schema.json','sc-workspace-reference-library-v1.schema.json','sc-workspace-citation-preferences-v1.schema.json','sc-workspace-reference-library-export-v1.schema.json'): json.loads((ROOT/'schemas'/name).read_text())
 def test_05_normalization_and_duplicates(self): self.assertIn('function normalizeDoi',REF); self.assertIn('function normalizeReference',REF); self.assertIn('function fingerprint',REF); self.assertIn('function duplicateGroups',REF); self.assertEqual(MAN['citation_library']['duplicate_detection'],['normalized-doi','bibliographic-fingerprint']); self.assertFalse(MAN['citation_library']['automatic_deduplication'])
 def test_06_citation_keys_styles(self): self.assertIn('function citationKeyBase',REF); self.assertIn('function uniqueCitationKey',REF); self.assertIn('function format(raw',REF); self.assertEqual(MAN['citation_library']['styles'],['apa7','chicago-author-date','mla9','ieee']); self.assertEqual(MAN['citation_library']['citation_keys'],'deterministic-local-collision-safe')
 def test_07_recorded_origin_only(self): self.assertTrue(MAN['citation_library']['canonical_origin_refs']); self.assertFalse(MAN['citation_library']['metadata_lookup']); self.assertFalse(MAN['citation_library']['metadata_inference']); self.assertIn('function referenceFromEntry',REF); self.assertIn('A reference with the same deterministic fingerprint already exists',JS)
 def test_08_browser_local_and_portable(self): self.assertEqual(MAN['citation_library']['storage'],'browser-local-workspace-library'); self.assertIn("STORAGE_KEY='sc_workspace_reference_library_v1'",REF); self.assertIn("PREFS_KEY='sc_workspace_citation_preferences_v1'",REF); self.assertIn('function exportPackage',REF); self.assertIn('data-scw-reference-export',PHP); self.assertIn('data-scw-reference-import',PHP)
 def test_09_presentation(self): self.assertIn('data-scw-reference-library',PHP); self.assertIn('data-scw-citation-style',PHP); self.assertIn('data-scw-reference-add-selected',PHP); self.assertIn('data-scw-reference-list',PHP); self.assertIn('data-scw-reference-detail',PHP); self.assertIn('.scw-reference-library{',CSS); self.assertIn('@media(forced-colors:active)',CSS)
 def test_10_governance(self):
  g=MAN['governance']; self.assertTrue(g['citation_library_browser_local']); self.assertFalse(g['citation_library_mutates_projects']); self.assertFalse(g['citation_library_metadata_lookup']); self.assertFalse(g['citation_library_metadata_inference']); self.assertFalse(g['citation_library_automatic_merge']); self.assertFalse(g['citation_library_automatic_ai']); self.assertTrue(g['citation_library_missing_fields_remain_missing']); self.assertTrue(g['citation_library_duplicate_reasons_visible'])
 def test_11_v043_collections_retained(self):
  prev=json.loads((ROOT/'history/release-manifest-v0.43.0.json').read_text()); self.assertTrue(prev['migration']['collections_views_only_release']); self.assertIn('sc-workspace-research-collections-v1.js',PHP); self.assertIn('function researchCollectionsApi()',JS)
 def test_12_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0840'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0430',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.43.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.43.0.json').exists())
if __name__=='__main__': unittest.main()
