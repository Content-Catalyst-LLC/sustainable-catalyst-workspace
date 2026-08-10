import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.56.0.js'
SCHEMA=ROOT/'schemas/sc-workspace-traceability-v1.schema.json'
PROJECT=ROOT/'schemas/sc-workspace-project-v8.schema.json'
MANIFEST=ROOT/'release-manifest-v0.56.0.json'
class TraceabilityContract(unittest.TestCase):
    def test_release_contract(self):
        m=json.loads(MANIFEST.read_text()); self.assertEqual(m['version'],'0.56.0'); self.assertEqual(m['previous_version'],'0.55.0'); self.assertEqual(m['storage_schema_version'],35); self.assertEqual(m['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(m['traceability_schema'],'sc-workspace-traceability/1.0')
    def test_schema(self):
        s=json.loads(SCHEMA.read_text()); self.assertEqual(s['properties']['schema']['const'],'sc-workspace-traceability/1.0'); self.assertEqual(s['properties']['evidenceAssessments']['maxItems'],250); self.assertEqual(s['properties']['lineage']['maxItems'],1000); self.assertEqual(s['properties']['reproducibility']['maxItems'],100)
    def test_project_references_traceability(self):
        p=json.loads(PROJECT.read_text()); self.assertEqual(p['properties']['schema']['const'],'sc-workspace-project/8.0'); self.assertIn('traceability',p['required']); self.assertEqual(p['properties']['traceability']['$ref'],'sc-workspace-traceability-v1.schema.json')
    def test_ui_mode_and_contract_endpoint(self):
        p=PHP.read_text(); self.assertIn('data-scw-project-mode="traceability"',p); self.assertIn("'/traceability-contract'",p); self.assertIn("sc-workspace-traceability-contract/1.0",p); self.assertIn('data-scw-evidence-assessment-form',p); self.assertIn('data-scw-lineage-form',p); self.assertIn('data-scw-repro-form',p)
    def test_sha256_and_no_composite_truth_score(self):
        j=JS.read_text(); self.assertIn("digest('SHA-256'",j); self.assertIn('fingerprintState',j); self.assertNotIn('truthScore',j); self.assertNotIn('truth_score',j)
    def test_lineage_and_repro_export(self):
        j=JS.read_text(); self.assertIn("'derived-from','supports','contradicts','uses','produced-by','informs','supersedes','cites'",j); self.assertIn("sc-workspace-reproducibility-export/1.0",j); self.assertIn('referencedObjects',j)
    def test_library_route(self):
        p=PHP.read_text(); self.assertIn("home_url('/knowledge-libraries/')",p); self.assertNotIn("home_url('/library/')",p)
    def test_migration_and_cleanup(self):
        j=JS.read_text(); self.assertIn('if (raw.schemaVersion === 9) return migrateV9(raw);',j); self.assertIn('cleanTraceabilityReferences(project, object.id)',j); self.assertIn("LEGACY_PROJECT_SCHEMA_V7 = 'sc-workspace-project/7.0'",j)
if __name__=='__main__': unittest.main()
