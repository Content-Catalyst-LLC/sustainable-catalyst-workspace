import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.74.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.74.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-ui-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.75.0.css').read_text()
class ApiEmbedIntegrationHardeningContract(unittest.TestCase):
 def test_release_and_schema_stability(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.74.0','0.73.0','API, Embed & Integration Hardening')); self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_hardening_boundaries(self):
  h=MAN['api_embed_integration_hardening'];
  for k in ['integrity_verification_before_export','bounded_embed_payload','bounded_api_payload','trusted_https_renderer_origin','fail_closed_invalid_embed','privacy_minimized_safety_report']: self.assertTrue(h[k],k)
  for k in ['durable_reference_is_authorization','credentialed_fetch','post_message_bridge','remote_write','live_server_project_api','canonical_mutation','automatic_publication','schema_migration_required']: self.assertFalse(h[k],k)
 def test_runtime_markers(self):
  for x in ['MAX_EMBED_BYTES=98304','MAX_API_BYTES=131072','rendererAssessment','validateDescriptor','integrationAssessment','safetyReport','renderFailure','credentialedFetch:false','postMessage:false','remoteMutation:false']: self.assertIn(x,HELP)
  self.assertIn('data-scw-api-verify',PHP); self.assertIn('data-scw-api-export-safety',PHP); self.assertIn('data-scw-api-safety',PHP); self.assertIn('data-trusted-origin',PHP); self.assertIn('lastAssessment',UI)
 def test_rest_and_assets(self):
  self.assertIn('Version: 0.75.0',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '0.75.0",MAIN); self.assertIn("'/api-embed-hardening-contract'",PHP); self.assertIn('api_embed_hardening_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/api-embed-hardening-contract',MAN['rest_routes']); self.assertIn("'sc-workspace-v0750'",PHP); self.assertIn('workspace-v0.75.0.js',PHP); self.assertIn('workspace-v0.75.0.css',PHP)
 def test_registry_history_and_artifacts(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.74.0','0.73.0','API, Embed & Integration Hardening')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0750'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0730',REGPHP); self.assertTrue((R/'history/release-manifest-v0.73.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.73.0.json').exists())
  for f in ['schemas/sc-workspace-api-embed-hardening-v1.schema.json','schemas/sc-workspace-integration-safety-report-v1.schema.json','schemas/sc-workspace-integration-origin-policy-v1.schema.json','docs/API_EMBED_INTEGRATION_HARDENING_V0740.md']: self.assertTrue((R/f).exists(),f)
 def test_css(self): self.assertIn('/* v0.74.0 — API, Embed & Integration Hardening */',CSS); self.assertIn('.scw-api-safety-metrics',CSS)
if __name__=='__main__': unittest.main()
