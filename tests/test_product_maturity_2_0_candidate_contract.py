from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'release-manifest-v1.15.0.json').read_text());OLD=json.loads((R/'release-manifest-v1.14.0.json').read_text());REG=json.loads((R/'registry/workspace-product-record-v1.15.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();H=(P/'includes/class-sc-workspace-product-maturity.php').read_text();JS=(P/'assets/js/sc-workspace-product-maturity-v1.js').read_text()
class ProductMaturity(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.15.0','1.14.0','1.x Product Maturity & 2.0 Candidate'))
 def test_02_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/product-maturity-contract'})
 def test_04_dimensions(self): self.assertEqual(len(MAN['product_maturity']['dimensions']),12);self.assertEqual(MAN['product_maturity']['states'],['ready','attention','blocked']);self.assertFalse(MAN['product_maturity']['numeric_score'])
 def test_05_candidate_boundary(self):
  g=MAN['product_maturity'];self.assertTrue(g['human_candidate_designation_required']);self.assertTrue(g['unresolved_blocker_prevents_candidate']);self.assertFalse(g['automatic_2_0_promotion']);self.assertFalse(g['v2_schema_introduced']);self.assertFalse(g['automatic_migration']);self.assertTrue(g['v1_api_compatibility_preserved'])
 def test_06_wordpress(self): self.assertIn('Version: 2.0.4',MAIN);self.assertIn("'/product-maturity-contract'",PHP);self.assertIn('data-scw-product-maturity',PHP);self.assertIn('data-release-stage="visual-regression-theme-isolation"',PHP)
 def test_07_deployment(self): self.assertIn("PREVIOUS_RELEASE = '2.0.3'",DEP);self.assertIn('class-sc-workspace-product-maturity.php',DEP);self.assertIn('workspace-v2.0.4.js',DEP)
 def test_08_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.15.0','1.14.0'))
 def test_09_runtime(self): self.assertIn('sc-workspace-2-0-candidate-boundary/1.0',JS);self.assertIn('numericScore:false',JS);self.assertIn('function candidateBoundary',JS)
 def test_10_files(self):
  for f in ['docs/PRODUCT_MATURITY_2_0_CANDIDATE_V1150.md','schemas/sc-workspace-product-maturity-v1.schema.json','schemas/sc-workspace-product-maturity-dossier-v1.schema.json','schemas/sc-workspace-product-maturity-compatibility-matrix-v1.schema.json','schemas/sc-workspace-1x-deprecation-register-v1.schema.json','schemas/sc-workspace-2-0-candidate-boundary-v1.schema.json']: self.assertTrue((R/f).is_file(),f)
if __name__=='__main__':unittest.main()
