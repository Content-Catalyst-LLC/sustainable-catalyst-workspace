from pathlib import Path
import json
import unittest

R=Path(__file__).resolve().parents[1]
P=R/'wordpress/sustainable-catalyst-workspace'
m=json.loads((R/'release-manifest-v2.0.0.json').read_text())
old=json.loads((R/'release-manifest-v1.15.0.json').read_text())
current=json.loads((R/'release-manifest-v2.0.1.json').read_text())
reg=json.loads((R/'registry/workspace-product-record-v2.0.0.json').read_text())
main=(P/'sustainable-catalyst-workspace.php').read_text()
php=(P/'includes/class-sc-workspace.php').read_text()
dep=(P/'includes/class-sc-workspace-deployment.php').read_text()
prod=(P/'includes/class-sc-workspace-production-certification.php').read_text()
js=(P/'assets/js/sc-workspace-connected-knowledge-v2.js').read_text()

class ConnectedKnowledgeWorkspaceV2HistoricalContract(unittest.TestCase):
    def test_identity_and_lineage(self):
        self.assertEqual((m['version'],m['previous_version'],m['release_name']),('2.0.0','1.15.0','Connected Knowledge Workspace'))
        self.assertEqual((reg['public_version'],reg['previous_version']),('2.0.0','1.15.0'))
        self.assertEqual((current['version'],current['previous_version']),('2.0.1','2.0.0'))
        self.assertIn('Version: 2.0.4',main); self.assertIn("SC_WORKSPACE_VERSION', '2.0.4'",main)
        self.assertIn("PREVIOUS_RELEASE = '2.0.3'",dep); self.assertIn("ROLLBACK_RELEASE = '2.0.3'",dep); self.assertIn("PREVIOUS_RELEASE = '2.0.3'",prod)
        self.assertIn('workspace-v2.0.4.js',dep); self.assertIn('workspace-v2.0.4.css',dep)
    def test_major_version_compatibility_boundary(self):
        g=m['connected_knowledge_workspace']
        self.assertTrue(g['stable_major_release']); self.assertTrue(g['v1_rest_namespace_preserved']); self.assertTrue(g['v2_rest_namespace_available']); self.assertTrue(g['v1_project_compatibility']); self.assertTrue(g['v1_export_compatibility'])
        self.assertFalse(g['v2_native_project_schema_introduced']); self.assertFalse(g['schema_migration_required']); self.assertFalse(g['automatic_migration'])
        self.assertEqual((m['storage_schema_version'],m['project_schema'],m['export_schema']),(old['storage_schema_version'],old['project_schema'],old['export_schema']))
        self.assertIn('/wp-json/sc-workspace/v2/connected-knowledge-contract',m['rest_routes'])
    def test_connected_contract_and_boundaries(self):
        g=m['connected_knowledge_workspace']; self.assertEqual(len(g['surfaces']),11); self.assertEqual(len(g['context_families']),14)
        self.assertTrue(g['single_context_envelope']); self.assertTrue(g['canonical_ownership_preserved']); self.assertTrue(g['return_to_origin_required']); self.assertTrue(g['provenance_required'])
        for k in ['automatic_cross_product_execution','automatic_context_upload','automatic_return_commit','automatic_ai','canonical_workspace_records_mutated','behavioral_telemetry','query_telemetry']:
            self.assertFalse(g[k])
        for x in ['sc-workspace-connected-knowledge-workspace/2.0','v1RestNamespacePreserved:true','automaticCrossProductExecution:false','schemaMigrationRequired:false']:
            self.assertIn(x,js)
    def test_wordpress_surface_and_assets(self):
        self.assertIn("register_rest_route('sc-workspace/v2', '/connected-knowledge-contract'",php)
        self.assertIn('SC_Workspace_Connected_Knowledge::contract()',php)
        self.assertIn('data-scw-connected-knowledge',php); self.assertIn('Connected Knowledge Workspace',php)
        self.assertIn('sc-workspace-connected-knowledge-v2',php); self.assertIn('sc-workspace-connected-knowledge-ui-v2',php)
        self.assertIn('sc-workspace-v204',php); self.assertIn('workspace-v2.0.4.js',php); self.assertIn('workspace-v2.0.4.css',php)
        self.assertTrue((P/'assets/js/workspace-v2.0.0.js').exists()); self.assertTrue((P/'assets/css/workspace-v2.0.0.css').exists())

if __name__=='__main__': unittest.main()
