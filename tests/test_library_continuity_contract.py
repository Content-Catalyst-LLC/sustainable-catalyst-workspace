from pathlib import Path
import json,unittest,subprocess,sys
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace'
MAN=json.loads((R/'history/release-manifest-v1.3.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.2.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();JS=(P/'assets/js/sc-workspace-library-continuity-v1.js').read_text()
class LibraryContinuity(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version']),('1.3.0','1.2.0'));self.assertIn('Version: 1.14.0',MAIN)
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertEqual(MAN['object_types'],OLD['object_types'])
 def test_03_route(self): self.assertIn('/wp-json/sc-workspace/v1/library-continuity-contract',MAN['rest_routes']);self.assertIn("'/library-continuity-contract'",PHP)
 def test_04_families(self): self.assertEqual(set(MAN['library_continuity']['record_families']),{'saved-search','watchlist','research-queue-item','source-bundle','personal-recommendation'})
 def test_05_identity(self): self.assertFalse(MAN['library_continuity']['second_account_required']);self.assertTrue(MAN['library_continuity']['authenticated_identity_reused']);self.assertTrue(MAN['library_continuity']['guest_workspace_preserved'])
 def test_06_privacy(self): self.assertTrue(MAN['library_continuity']['personal_recommendations_private_by_default']);self.assertFalse(MAN['library_continuity']['behavioral_telemetry']);self.assertFalse(MAN['library_continuity']['query_telemetry'])
 def test_07_no_auto_mutation(self): self.assertFalse(MAN['library_continuity']['automatic_library_pull']);self.assertFalse(MAN['library_continuity']['automatic_background_sync']);self.assertFalse(MAN['library_continuity']['canonical_library_records_mutated'])
 def test_08_provenance(self): self.assertTrue(MAN['library_continuity']['provenance_preserved']);self.assertTrue(MAN['library_continuity']['origin_ids_preserved']);self.assertIn('/knowledge-libraries/',JS)
 def test_09_ui(self): self.assertIn('data-scw-library-continuity',PHP);self.assertIn('Open Knowledge Library',PHP);self.assertIn('Add to project',(P/'assets/js/workspace-v1.3.0.js').read_text())
 def test_10_validator(self): subprocess.run([sys.executable,str(R/'scripts/validate_library_continuity.py')],cwd=R,check=True)
if __name__=='__main__': unittest.main()
