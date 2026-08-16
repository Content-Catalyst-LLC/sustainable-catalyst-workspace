from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'release-manifest-v1.14.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.13.0.json').read_text());REG=json.loads((R/'registry/workspace-product-record-v1.14.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();H=(P/'includes/class-sc-workspace-public-research-packages.php').read_text();JS=(P/'assets/js/sc-workspace-public-research-packages-v1.js').read_text()
class PublicResearchPackages(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.14.0','1.13.0','Public Research Packages & Portable Knowledge Objects'))
 def test_02_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/public-research-packages-contract'})
 def test_04_boundary(self):
  g=MAN['public_research_packages'];self.assertTrue(g['private_by_default']);self.assertTrue(g['explicit_selection_required']);self.assertTrue(g['explicit_publication_confirmation_required']);self.assertTrue(g['license_required_for_public'])
 def test_05_prohibited(self):
  g=MAN['public_research_packages'];
  for k in ['canonical_workspace_records_mutated','automatic_publication','automatic_upload','automatic_network_request','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(g[k])
 def test_06_integrity(self): self.assertEqual(MAN['public_research_packages']['integrity_algorithm'],'SHA-256');self.assertIn('sha256Hex',JS)
 def test_07_wordpress(self): self.assertIn('Version: 2.0.2',MAIN);self.assertIn("'/public-research-packages-contract'",PHP);self.assertIn('data-scw-public-research-packages',PHP);self.assertIn('data-release-stage="work-mode-cards-repair"',PHP)
 def test_08_deployment(self): self.assertIn("PREVIOUS_RELEASE = '2.0.1'",DEP);self.assertIn('class-sc-workspace-public-research-packages.php',DEP);self.assertIn('workspace-v2.0.2.js',DEP)
 def test_09_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.14.0','1.13.0'))
 def test_10_contract(self): self.assertIn('sc-workspace-portable-knowledge-object/1.0',H);self.assertIn('explicitPublicationConfirmationRequired',H)
if __name__=='__main__':unittest.main()
