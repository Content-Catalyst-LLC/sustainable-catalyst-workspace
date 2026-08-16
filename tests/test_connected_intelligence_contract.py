from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'release-manifest-v1.13.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.12.0.json').read_text());REG=json.loads((R/'registry/workspace-product-record-v1.13.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();H=(P/'includes/class-sc-workspace-connected-intelligence.php').read_text();JS=(P/'assets/js/sc-workspace-connected-intelligence-v1.js').read_text()
class ConnectedIntelligence(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.13.0','1.12.0','Connected Intelligence Workspace'))
 def test_02_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/connected-intelligence-contract'})
 def test_04_products(self): self.assertEqual(MAN['connected_intelligence']['products'],['knowledge-library','site-intelligence','lab','workbench','decision-studio'])
 def test_05_governance(self):
  g=MAN['connected_intelligence'];
  for k in ['explicit_context_selection','stable_ids_only_in_urls','portable_context_export','provenance_preserved','return_to_origin','context_receipts_metadata_only']: self.assertTrue(g[k])
  for k in ['automatic_cross_product_execution','automatic_network_request','automatic_context_upload','automatic_return_commit','automatic_ai','background_federation','canonical_specialist_records_mutated','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(g[k])
 def test_06_wordpress(self): self.assertIn('Version: 2.0.2',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '2.0.2'",MAIN);self.assertIn("'/connected-intelligence-contract'",PHP);self.assertIn('Connected Intelligence Workspace',PHP);self.assertIn('data-release-stage="work-mode-cards-repair"',PHP)
 def test_07_runtime(self):
  for x in ['sc-workspace-connected-intelligence/1.0','function buildContext','function route','function receipt','backgroundFederation:false']: self.assertIn(x,JS)
  self.assertIn('sc-workspace-connected-intelligence/1.0',H)
 def test_08_deployment(self): self.assertIn("PREVIOUS_RELEASE = '2.0.1'",DEP);self.assertIn("ROLLBACK_RELEASE = '2.0.1'",DEP);self.assertIn('workspace-v2.0.2.js',DEP);self.assertIn('class-sc-workspace-connected-intelligence.php',DEP)
 def test_09_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.13.0','1.12.0'))
if __name__=='__main__':unittest.main()
