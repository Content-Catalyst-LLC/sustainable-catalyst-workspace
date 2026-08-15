import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; P=R/'wordpress/sustainable-catalyst-workspace'
MAN=json.loads((R/'history/release-manifest-v0.82.0.json').read_text()); OLD=json.loads((R/'history/release-manifest-v0.81.0.json').read_text()); REG=json.loads((R/'history/workspace-product-record-v0.82.0.json').read_text())
MAIN=(P/'sustainable-catalyst-workspace.php').read_text(); PHP=(P/'includes/class-sc-workspace.php').read_text(); PROD=(P/'includes/class-sc-workspace-production-certification.php').read_text(); DEP=(P/'includes/class-sc-workspace-deployment.php').read_text(); NAV=(P/'assets/js/sc-workspace-research-navigation-v1.js').read_text(); EXP=(P/'assets/js/sc-workspace-experience-v1.js').read_text(); RUN=(P/'assets/js/sc-workspace-production-smoke-cache-rollback-v1.js').read_text(); CSS=(P/'assets/css/workspace-v1.7.0.css').read_text()
class ProductionCertificationContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.82.0','0.81.0','Production Smoke, Cache & Rollback Certification')); self.assertIn('Version: 1.7.0',MAIN)
 def test_02_freeze(self):
  for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']: self.assertEqual(MAN[k],OLD[k])
  self.assertEqual(MAN['object_types'],OLD['object_types']); self.assertFalse(MAN['schema_migration_required'])
 def test_03_rest_delta(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/production-certification-contract'})
 def test_04_server_boundaries(self):
  for t in ["PREVIOUS_RELEASE = '1.6.0'",'production_certification_requires_live_field_checks','production_certified','automatic_cache_purge','automatic_rollback','project_data_inspected']: self.assertIn(t,PROD)
 def test_05_deployment_inheritance(self): self.assertIn("PREVIOUS_RELEASE = '1.6.0'",DEP); self.assertIn('workspace-v1.7.0.js',DEP); self.assertIn('production_runtime',DEP)
 def test_06_ui(self): self.assertIn('data-scw-workspace-view="production-certification"',PHP); self.assertIn('data-scw-production-certification',PHP); self.assertIn('Run package certification',PHP); self.assertIn('Package ready is not production certified',PHP)
 def test_07_navigation(self): self.assertIn("'production-certification'",NAV); self.assertIn("id:'production-certification'",EXP)
 def test_08_runtime_governance(self):
  for t in ['productionCertified:false','automaticProductionCertification:false','automaticCachePurge:false','automaticRollback:false','projectDataRead:false','projectDataMutation:false']: self.assertIn(t,RUN)
 def test_09_current_assets(self): self.assertIn("'sc-workspace-v170'",PHP); self.assertIn('workspace-v1.7.0.js',PHP); self.assertIn('workspace-v1.7.0.css',PHP); self.assertNotIn('sc-workspace-v0810',PHP)
 def test_10_registry(self): self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.82.0','0.81.0','Production Smoke, Cache & Rollback Certification'))
 def test_11_policy(self):
  c=MAN['production_smoke_cache_rollback_certification']; self.assertTrue(c['package_smoke_gate']); self.assertTrue(c['live_production_checks_manual']); self.assertTrue(c['rollback_artifact_required']); self.assertFalse(c['automatic_production_certification']); self.assertFalse(c['new_product_subsystem'])
 def test_12_schemas(self):
  for f in ['sc-workspace-production-certification-v1.schema.json','sc-workspace-production-certification-report-v1.schema.json','sc-workspace-production-certification-checklist-v1.schema.json','sc-workspace-rollback-rehearsal-v1.schema.json']: self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
 def test_13_css(self): self.assertIn('/* v0.82.0 — Production Smoke, Cache & Rollback Certification */',CSS); self.assertIn('.scw-production-certification-grid',CSS)
 def test_14_history(self): self.assertTrue((R/'history/release-manifest-v0.81.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.81.0.json').exists())
 def test_15_docs_tooling(self): self.assertTrue((R/'docs/PRODUCTION_SMOKE_CACHE_ROLLBACK_CERTIFICATION_V0820.md').exists()); self.assertTrue((R/'scripts/verify_wordpress_production_v0_82_0.sh').exists())
if __name__=='__main__': unittest.main()
