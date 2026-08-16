from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.11.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.10.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.11.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
class DeveloperAPI(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.11.0','1.10.0','Developer API, SDK & Extension Contracts'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_only_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/developer-api-contract'})
 def test_04_capabilities(self): self.assertEqual(len(MAN['developer_api']['capabilities']),10);self.assertEqual(MAN['developer_api']['default_capability_mode'],'read-only-descriptive')
 def test_05_governance(self):
  g=MAN['developer_api']
  for k in ['extension_manifest_required','capability_grant_required','grants_are_explicit','grants_are_portable_records','browser_local_sdk']: self.assertTrue(g[k])
  for k in ['grant_is_authentication_credential','mutating_rest_endpoints','arbitrary_code_execution','dynamic_plugin_installation','remote_extension_loading','automatic_network_request','automatic_canonical_mutation','automatic_ai','behavioral_telemetry','query_telemetry','secrets_in_manifest','tokens_in_urls','schema_migration_required']: self.assertFalse(g[k])
 def test_06_wordpress(self): self.assertIn('Version: 2.0.2',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '2.0.2'",MAIN);self.assertIn("'/developer-api-contract'",PHP);self.assertIn('Developer API &amp; Extensions',PHP);self.assertIn('data-release-stage="work-mode-cards-repair"',PHP)
 def test_07_deployment(self): self.assertIn("PREVIOUS_RELEASE = '2.0.1'",DEP);self.assertIn("ROLLBACK_RELEASE = '2.0.1'",DEP);self.assertIn('workspace-v2.0.2.js',DEP);self.assertIn('class-sc-workspace-developer-api.php',DEP)
 def test_08_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.11.0','1.10.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v202'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V1110',REGPHP)
if __name__=='__main__':unittest.main()
