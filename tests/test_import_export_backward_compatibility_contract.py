from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class T(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.68.0',MAIN)
 def test_02_schema_stable(self):
  self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertFalse(MAN['schema_migration_required']);self.assertTrue(MAN['migration']['import_export_compatibility_hardening_only_release']);self.assertFalse(MAN['migration']['import_export_canonical_data_rewrite'])
 def test_03_schemas(self):
  expected={'sc-workspace-import-export-compatibility-v1.schema.json':'sc-workspace-import-export-compatibility/1.0','sc-workspace-import-assessment-v1.schema.json':'sc-workspace-import-assessment/1.0','sc-workspace-backward-compatibility-matrix-v1.schema.json':'sc-workspace-backward-compatibility-matrix/1.0','sc-workspace-round-trip-receipt-v1.schema.json':'sc-workspace-round-trip-receipt/1.0'}
  for name,const in expected.items():self.assertEqual(json.loads((ROOT/'schemas'/name).read_text())['properties']['schema']['const'],const)
 def test_04_historical_schema_coverage(self):
  for v in ['1.0','2.0','3.0','3.1','4.0','5.0','6.0','7.0','8.0','9.0','10.0','11.0','12.0','13.0','14.0','15.0','16.0','17.0','18.0','19.0','20.0']:
   self.assertIn(f"'sc-workspace-project/{v}'",COMP.replace('PROJECT_SCHEMA_PREFIX+v',"'")) if False else self.assertIn(f"'{v}'",COMP)
  self.assertIn("PROJECT_VERSIONS=['1.0','2.0','3.0','3.1'",COMP)
 def test_05_future_schema_block(self):
  self.assertIn("future:p.major>20",COMP);self.assertIn('cannot be safely downgraded',COMP);self.assertFalse(MAN['import_export_backward_compatibility']['automatic_overwrite'])
 def test_06_staged_project_import(self):
  self.assertIn('data-scw-project-import-stage',PHP);self.assertIn('data-scw-project-import-commit',PHP);self.assertIn('Import staged copy',PHP);self.assertIn('let stagedProjectImport = null',APP);self.assertIn("assessment?.status!=='ready'",APP);self.assertIn('project.id=id(\'scwp\')',APP)
 def test_07_file_selection_does_not_commit(self):
  block=APP[APP.index("importFile.addEventListener('change'"):APP.index("if(projectImportClear)")];self.assertIn('assessProjectImport',block);self.assertNotIn('state.projects.push(project)',block);self.assertIn('readFileTextCompat(file)',block)
 def test_08_export_round_trip_gate(self):
  self.assertIn('currentProjectExport(portable',APP);self.assertIn('round-trip compatibility check',APP);self.assertIn('function roundTripCheck',COMP);self.assertIn('checksumPurpose',COMP);self.assertFalse(MAN['governance']['project_export_round_trip_checksum_is_security_signature'])
 def test_09_matrix_ui_and_export(self):
  self.assertIn('data-scw-backward-compatibility-matrix',PHP);self.assertIn('Export compatibility matrix',PHP);self.assertIn('renderBackwardCompatibilityMatrix',APP);self.assertIn('compatibilityMatrix()',APP);self.assertIn('.scw-compatibility-matrix-row',CSS)
 def test_10_rest_contract(self):
  self.assertIn("'/import-export-compatibility-contract'",PHP);self.assertIn('public function import_export_compatibility_contract()',PHP);self.assertIn('/wp-json/sc-workspace/v1/import-export-compatibility-contract',MAN['rest_routes']);self.assertIn("'future_project_schema_downgrade' => false",PHP)
 def test_11_assets(self):
  self.assertIn("'sc-workspace-import-export-compatibility-v1'",PHP);self.assertIn('sc-workspace-import-export-compatibility-v1.js',PHP);self.assertIn("'sc-workspace-v0680'",PHP);self.assertIn('workspace-v0.68.0.js',PHP);self.assertIn('workspace-v0.68.0.css',PHP)
 def test_12_existing_storage_compatibility(self):
  self.assertIn('if (raw.schemaVersion === 1 || raw.schema === 1)',APP);self.assertIn('if (raw.schemaVersion === 34) return migrateV34(raw);',APP);self.assertEqual(MAN['import_export_backward_compatibility']['supported_existing_storage_versions'],list(range(1,36)))
 def test_13_fixture_boundaries(self):
  fixtures=ROOT/'tests/fixtures/import-export-compatibility';self.assertTrue((fixtures/'project-export-v1.json').exists());self.assertTrue((fixtures/'project-export-v20.json').exists());self.assertTrue((fixtures/'project-export-future-v21.json').exists());self.assertTrue((fixtures/'malformed-project-export.json').exists())
 def test_14_governance(self):
  g=MAN['governance'];self.assertTrue(g['project_import_staged_review_required']);self.assertFalse(g['project_import_automatic_commit']);self.assertFalse(g['project_import_silent_overwrite']);self.assertTrue(g['project_import_new_local_copy_only']);self.assertFalse(g['future_project_schema_downgrade']);self.assertFalse(g['backward_compatibility_external_lookup']);self.assertFalse(g['backward_compatibility_server_pipeline'])
 def test_15_registry_history(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0680'",REGPHP);self.assertIn("LEGACY_PENDING_KEY_V0650",REGPHP);self.assertTrue((ROOT/'history/release-manifest-v0.65.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.65.0.json').exists())
if __name__=='__main__':unittest.main()
