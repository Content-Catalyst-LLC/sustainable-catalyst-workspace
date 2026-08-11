import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-ui-v1.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class ApiEmbedContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 0.67.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertTrue(MAN['api_embed']['schema_migration'] is False)
 def test_03_schemas(self):
  for n in ['sc-workspace-durable-reference-v1.schema.json','sc-workspace-readonly-projection-v1.schema.json','sc-workspace-readonly-api-envelope-v1.schema.json','sc-workspace-embed-descriptor-v1.schema.json']: self.assertTrue((ROOT/'schemas'/n).exists())
 def test_04_private_default(self): self.assertEqual(MAN['api_embed']['canonical_workspace_default'],'private-browser-local'); self.assertFalse(MAN['api_embed']['live_server_project_api']); self.assertFalse(MAN['api_embed']['server_project_discovery'])
 def test_05_durable_ref_not_auth(self): self.assertFalse(MAN['api_embed']['durable_reference_is_authorization']); self.assertIn('authorization:false',HELP); self.assertIn('identifierIsNotAuthorization:true',HELP)
 def test_06_explicit_projection(self): self.assertIn("exposure:'public-readonly'",HELP); self.assertIn('explicitDisclosure:true',HELP); self.assertIn('Full content <strong>explicit disclosure</strong>',PHP)
 def test_07_static_api(self): self.assertIn("'/api-embed-contract'",PHP); self.assertIn('public function api_embed_contract()',PHP); self.assertIn('serverDataEndpoint:false',HELP); self.assertIn('/wp-json/sc-workspace/v1/api-embed-contract',MAN['rest_routes'])
 def test_08_embed_renderer(self): self.assertIn('sc_workspace_api_embed_script_url',MAIN); self.assertIn('data-sc-workspace-embed',HELP); self.assertIn('noLiveDataFetch:true',HELP); self.assertIn('sc-workspace-api-embed-v1.js',PHP)
 def test_09_ui(self): self.assertIn('data-scw-api-embed',PHP); self.assertIn('data-scw-api-create',PHP); self.assertIn('data-scw-api-copy-embed',PHP); self.assertIn('sc-workspace-api-embed-ui-v1.js',PHP)
 def test_10_navigation(self): self.assertIn("'api-embed':'API & Embed'",NAV); self.assertIn('data-scw-workspace-view="api-embed"',PHP)
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0670'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0540',REGPHP)
 def test_12_history(self): self.assertTrue((ROOT/'history/release-manifest-v0.54.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.54.0.json').exists())
 def test_13_header_rule(self): self.assertIn('border-top:4px solid #000',CSS); self.assertIn('.scw-editorial-header-bar{height:4px',CSS)
 def test_14_docs_and_governance(self): self.assertTrue((ROOT/'docs/WORKSPACE_API_EMBED_FOUNDATION_V0550.md').exists()); self.assertFalse(MAN['api_embed']['automatic_publication']); self.assertFalse(MAN['api_embed']['automatic_canonical_mutation'])
if __name__=='__main__': unittest.main()
