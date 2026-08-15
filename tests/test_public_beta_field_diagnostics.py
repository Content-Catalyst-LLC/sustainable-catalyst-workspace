import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-diagnostics-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
FIELD=json.loads((ROOT/'schemas/sc-workspace-field-diagnostic-v1.schema.json').read_text())
ISSUE=json.loads((ROOT/'schemas/sc-workspace-field-report-v1.schema.json').read_text())
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
class FieldDiagnosticsContract(unittest.TestCase):
 def test_lineage(self): self.assertEqual(MAN['version'],'0.66.0'); self.assertEqual(MAN['previous_version'],'0.65.0'); self.assertEqual(MAN['release_name'],'Import, Export & Backward-Compatibility Hardening')
 def test_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required']); self.assertFalse(MAN['governance']['schema_migration_required'])
 def test_contract_route(self): self.assertIn('/wp-json/sc-workspace/v1/field-diagnostics-contract',MAN['rest_routes']); self.assertIn("'/field-diagnostics-contract'",PHP); self.assertIn('public function field_diagnostics_contract()',PHP)
 def test_schemas(self): self.assertEqual(MAN['field_diagnostics_schema'],'sc-workspace-field-diagnostic/1.0'); self.assertEqual(MAN['field_report_schema'],'sc-workspace-field-report/1.0'); self.assertEqual(FIELD['properties']['schema']['const'],'sc-workspace-field-diagnostic/1.0'); self.assertEqual(ISSUE['properties']['schema']['const'],'sc-workspace-field-report/1.0')
 def test_privacy(self):
  d=MAN['field_diagnostics']; self.assertFalse(d['automatic_telemetry']); self.assertFalse(d['automatic_submission']); self.assertFalse(d['project_content_automatically_included']); self.assertFalse(d['device_identifier_included']); self.assertFalse(d['source_urls_included']); self.assertFalse(d['query_string_included']); self.assertFalse(d['hash_included'])
 def test_no_hidden_health_score(self): self.assertFalse(MAN['field_diagnostics']['hidden_health_score']); self.assertFalse(MAN['governance']['field_diagnostics_hidden_health_score']); self.assertIn('hidden_health_score',PHP)
 def test_checks(self):
  for key in ['browser-capabilities','storage-write-latency','workspace-size','serialization-latency','parse-latency','dom-density','last-known-good-recovery','deployment-profile']: self.assertIn(key,MAN['field_diagnostics']['checks'])
 def test_thresholds_are_explicit(self): self.assertEqual(MAN['field_diagnostics']['advisory_thresholds']['workspace_bytes'],4194304); self.assertEqual(MAN['field_diagnostics']['advisory_thresholds']['dom_nodes'],6000); self.assertIn('THRESHOLDS',JS)
 def test_issue_form(self):
  for marker in ['data-scw-field-report-form','name="observed"','name="expected"','name="steps"','name="reviewed"']: self.assertIn(marker,PHP)
 def test_issue_export_is_human_reviewed(self): self.assertTrue(MAN['field_diagnostics']['human_review_before_issue_export']); self.assertIn('userReviewedBeforeExport',JS); self.assertIn('automaticSubmission:false',JS)
 def test_ui_surface(self):
  for marker in ['data-scw-field-diagnostics','data-scw-run-field-diagnostics','data-scw-export-field-diagnostic','data-scw-open-field-diagnostics']: self.assertIn(marker,PHP)
 def test_performance_metrics(self):
  for key in ['workspaceBytes','storageProbeMs','parseMs','serializeMs','domNodes','workspaceResourceCount']: self.assertIn(key,JS)
 def test_recovery_verification(self): self.assertIn('lastKnownGoodSnapshotAvailable',JS); self.assertIn('sc_workspace_last_good_v1',JS)
 def test_deployment_profile_excludes_query(self): self.assertIn("pathname",JS); self.assertNotIn("location.search",JS); self.assertNotIn("location.hash",JS)
 def test_accessibility(self): self.assertIn(':focus-visible',CSS); self.assertIn('prefers-reduced-motion:reduce',CSS); self.assertIn('forced-colors:active',CSS); self.assertIn('aria-live="polite"',PHP)
 def test_registry(self): self.assertEqual(REG['public_version'],'0.66.0'); self.assertEqual(REG['previous_version'],'0.65.0'); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v100'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0300',REGPHP)
 def test_plugin_version(self): self.assertIn('Version: 1.0.0',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '1.0.0",MAIN)
 def test_history_preserved(self): self.assertTrue((ROOT/'history/release-manifest-v0.30.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.30.0.json').exists())
if __name__=='__main__': unittest.main()
