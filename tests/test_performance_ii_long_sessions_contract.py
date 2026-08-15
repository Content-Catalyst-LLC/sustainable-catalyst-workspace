from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'history/release-manifest-v0.68.0.json').read_text())
REG=json.loads((ROOT/'history/workspace-product-record-v0.68.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAIN=MAINP.read_text(); HEAD=MAINP.read_bytes()[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v1.7.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-long-session-performance-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-long-session-performance-ui-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v1.7.0.css').read_text()
class PerformanceII(unittest.TestCase):
 def test_01_lineage_and_wordpress_header(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.68.0','0.67.0','Performance II: Long Sessions & Very Large Workspaces'))
  self.assertIn('Version: 1.7.0',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '1.7.0",MAIN)
  for label,value in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','1.7.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
   m=re.search(r'^[ \\t\\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); self.assertTrue(m and m.group(1).strip()==value)
 def test_02_schema_stability(self):
  self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'))
  self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['performance_ii_only_release']); self.assertFalse(MAN['migration']['performance_ii_canonical_data_rewrite'])
 def test_03_contract_and_assets(self):
  self.assertIn('/wp-json/sc-workspace/v1/long-session-performance-contract',MAN['rest_routes'])
  self.assertIn("'/long-session-performance-contract'",PHP); self.assertIn('public function long_session_performance_contract()',PHP)
  self.assertIn('sc-workspace-long-session-performance-v1.js',PHP); self.assertIn('sc-workspace-long-session-performance-ui-v1.js',PHP)
  self.assertIn("'sc-workspace-v170'",PHP); self.assertIn('workspace-v1.7.0.js',PHP); self.assertIn('workspace-v1.7.0.css',PHP)
  self.assertIn("wp_localize_script('sc-workspace-v170'",PHP)
 def test_04_bounded_memory_only_profile(self):
  perf=MAN['long_session_performance']; self.assertEqual(perf['bounded_in_memory_samples'],120); self.assertFalse(perf['persistent_profiling']); self.assertFalse(perf['automatic_telemetry']); self.assertFalse(perf['automatic_submission'])
  self.assertIn('maxSamples:120',HELP); self.assertIn('boundedPush',HELP); self.assertIn('persisted:false',HELP)
 def test_05_route_render_index_instrumentation(self):
  self.assertIn('longSessionMonitor?.markRoute(workspaceView)',APP); self.assertIn("longSessionMonitor?.markRender",APP); self.assertIn("longSessionMonitor?.markIndex",APP)
  self.assertIn('derivedIntegratedEntries(api)',APP); self.assertIn('integrated-knowledge',APP)
 def test_06_cooperative_and_memoized_helpers(self):
  self.assertTrue(MAN['long_session_performance']['cooperative_chunk_yield']); self.assertTrue(MAN['long_session_performance']['revision_memoization'])
  self.assertIn('function cooperativeYield',HELP); self.assertIn('async function chunkedMap',HELP); self.assertIn('function createRevisionMemo',HELP); self.assertIn('function boundedWindow',HELP)
 def test_07_optional_browser_signals(self):
  self.assertTrue(MAN['long_session_performance']['performance_observer_optional']); self.assertTrue(MAN['long_session_performance']['heap_signal_optional_nonportable'])
  self.assertIn("supportedEntryTypes.includes('longtask')",HELP); self.assertIn('performance?.memory',HELP)
 def test_08_privacy_and_governance(self):
  perf=MAN['long_session_performance'];
  for k in ['project_content_in_report','query_text_in_report','source_urls_in_report','device_identifier_in_report','automatic_deletion','automatic_archival','automatic_compaction','automatic_migration','canonical_mutation']: self.assertFalse(perf[k])
  self.assertIn('projectContentIncluded:false',HELP); self.assertIn('automaticTelemetry:false',HELP)
 def test_09_performance_surface(self):
  for token in ['data-scw-performance-session','data-scw-perf-session-run','data-scw-perf-session-reset','data-scw-perf-session-export','PERFORMANCE II / LONG SESSION']:
   self.assertIn(token,PHP)
  self.assertIn('No advisory long-session signals',PHP); self.assertIn('Canonical Workspace data was unchanged',UI); self.assertIn('Performance II: Long Sessions',CSS)
 def test_10_registry_history(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.68.0','0.67.0','Performance II: Long Sessions & Very Large Workspaces'))
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v170'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0670',REGPHP)
  self.assertTrue((ROOT/'history/release-manifest-v0.67.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.67.0.json').exists())
 def test_11_schemas_and_docs(self):
  for f in ['schemas/sc-workspace-long-session-performance-v1.schema.json','schemas/sc-workspace-performance-session-v1.schema.json','schemas/sc-workspace-performance-session-report-v1.schema.json','docs/PERFORMANCE_LONG_SESSIONS_V0680.md']:
   self.assertTrue((ROOT/f).exists())
if __name__=='__main__': unittest.main()
