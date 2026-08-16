from pathlib import Path
import json, unittest
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.12.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.11.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.12.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text();H=(P/'includes/class-sc-workspace-institutional-scale-hardening.php').read_text();JS=(P/'assets/js/sc-workspace-institutional-scale-hardening-v1.js').read_text()
class InstitutionalScaleHardening(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.12.0','1.11.0','Large Workspace & Institutional Scale Hardening'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_only_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/institutional-scale-hardening-contract'})
 def test_04_scale_envelope(self):
  g=MAN['institutional_scale_hardening'];self.assertEqual((g['projects_attention'],g['objects_attention'],g['search_entries_attention']),(250,25000,75000));self.assertTrue(g['deterministic_scale_assessment']);self.assertTrue(g['bounded_rendering']);self.assertTrue(g['chunked_local_indexing']);self.assertTrue(g['bounded_graph_expansion']);self.assertTrue(g['sharded_institutional_exports'])
 def test_05_recovery_first(self): self.assertTrue(MAN['institutional_scale_hardening']['recovery_first_critical_mode']);self.assertTrue(MAN['institutional_scale_hardening']['operation_journal_required']);self.assertTrue(MAN['institutional_scale_hardening']['last_known_good_required'])
 def test_06_governance(self):
  g=MAN['institutional_scale_hardening'];
  for k in ['local_first','advisory_only','rollback_schema_compatible']: self.assertTrue(g[k])
  for k in ['canonical_mutation','automatic_deletion','automatic_compaction','automatic_archival','automatic_migration','automatic_upload','server_offload','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(g[k])
 def test_07_wordpress(self): self.assertIn('Version: 2.0.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '2.0.0'",MAIN);self.assertIn("'/institutional-scale-hardening-contract'",PHP);self.assertIn('institutional_scale_hardening_contract',PHP);self.assertIn('data-release-stage="connected-knowledge-workspace"',PHP);self.assertIn('Large Workspace &amp; Institutional Scale Hardening',PHP)
 def test_08_runtime_contract(self):
  for t in ['sc-workspace-institutional-scale-hardening/1.0','function deriveMetrics','function assess','function plan','function checkpoint','function exportShardManifest','automaticDeletion:false','serverOffload:false']: self.assertIn(t,JS)
  self.assertIn('sc-workspace-institutional-scale-hardening/1.0',H)
 def test_09_deployment(self): self.assertIn("PREVIOUS_RELEASE = '1.15.0'",DEP);self.assertIn("ROLLBACK_RELEASE = '1.15.0'",DEP);self.assertIn('workspace-v2.0.0.js',DEP);self.assertIn('class-sc-workspace-institutional-scale-hardening.php',DEP)
 def test_10_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.12.0','1.11.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v200'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V1120',REGPHP)
if __name__=='__main__':unittest.main()
