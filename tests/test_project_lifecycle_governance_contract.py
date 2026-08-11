import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.64.1.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.64.1.json').read_text())
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.64.1.js').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.64.1.css').read_text()
AUDIT=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-audit-trail-v1.js').read_text()
HELPER=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-project-lifecycle-v1.js').read_text()
class LifecycleGovernanceContract(unittest.TestCase):
 def test_release_lineage(self):
  self.assertEqual(MAN['version'],'0.64.1'); self.assertEqual(MAN['previous_version'],'0.64.0'); self.assertEqual(MAN['release_name'],'Accessibility Runtime & Desktop Layout Recovery')
 def test_schema_migration(self):
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required']); self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35)); self.assertTrue(MAN['migration']['project_schema_unchanged'])
 def test_lifecycle_schemas(self):
  self.assertEqual(MAN['project_lifecycle_schema'],'sc-workspace-project-lifecycle/1.0'); self.assertEqual(MAN['governance_milestone_schema'],'sc-workspace-governance-milestone/1.0')
  for f in ('sc-workspace-project-lifecycle-v1.schema.json','sc-workspace-governance-milestone-v1.schema.json','sc-workspace-project-v12.schema.json'): json.loads((ROOT/'schemas'/f).read_text())
 def test_project_v12_requires_lifecycle(self):
  s=json.loads((ROOT/'schemas/sc-workspace-project-v12.schema.json').read_text()); self.assertEqual(s['properties']['schema']['const'],'sc-workspace-project/12.0'); self.assertIn('lifecycle',s['required'])
 def test_seven_states(self):
  self.assertEqual(MAN['project_lifecycle']['states'],['draft','evidence-ready','analysis-ready','decision-ready','review-ready','publication-ready','institutional-ready'])
 def test_human_control(self):
  x=MAN['project_lifecycle']; self.assertTrue(x['human_declared']); self.assertFalse(x['automatic_advancement']); self.assertTrue(x['rationale_required']); self.assertTrue(x['acknowledgement_required']); self.assertTrue(x['backward_transitions_allowed'])
 def test_no_score_or_certification(self):
  x=MAN['project_lifecycle']; self.assertFalse(x['hidden_readiness_score']); self.assertFalse(x['readiness_is_certification']); self.assertEqual(x['readiness'],'derived-visible-checklist')
 def test_no_account_identity_inference(self): self.assertFalse(MAN['project_lifecycle']['account_identity_inferred']); self.assertFalse(MAN['governance']['project_lifecycle_account_identity_inferred'])
 def test_rest_and_top_level_ui(self): self.assertIn("'/project-lifecycle-contract'",PHP); self.assertIn('public function project_lifecycle_contract()',PHP); self.assertIn('data-scw-workspace-view="lifecycle"',PHP); self.assertIn('data-scw-workspace-section="lifecycle"',PHP)
 def test_runtime_migration(self): self.assertIn('function migrateV26(raw)',JS); self.assertIn('if (raw.schemaVersion === 26) return migrateV26(raw);',JS); self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/20.0'",JS); self.assertIn('lifecycle: lifecycleTemplate()',JS)
 def test_helper_boundary(self): self.assertIn('automaticAdvance:false',HELPER); self.assertIn('readinessIsCertification:false',HELPER); self.assertIn("score:null",HELPER)
 def test_audit_integration(self): self.assertIn('project-lifecycle',MAN['audit_trail']['event_sources']); self.assertIn("'project-lifecycle'",AUDIT); self.assertIn('p.lifecycle?.milestones',AUDIT)
 def test_portability(self): self.assertTrue(MAN['project_lifecycle']['milestone_history_portable_with_project']); self.assertIn('lifecycle: normalizeLifecycle(raw.lifecycle)',JS)
 def test_visual_layer(self): self.assertIn('/* v0.29.0 — Governance Milestones & Project Lifecycle */',CSS); self.assertIn('.scw-project-lifecycle-stage.is-current',CSS)
 def test_registry(self): self.assertEqual(REG['public_version'],'0.64.1'); self.assertEqual(REG['previous_version'],'0.64.0')
 def test_v028_history_preserved(self): self.assertTrue((ROOT/'history/release-manifest-v0.28.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.28.0.json').exists())
 def test_library_route(self): self.assertEqual(MAN['canonical_library_path'],'/knowledge-libraries/'); self.assertIn('/knowledge-libraries/',PHP)
if __name__=='__main__': unittest.main()
