import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.80.0.json').read_text())
OLD=json.loads((R/'history/release-manifest-v0.79.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.80.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-release-candidate-i-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-release-candidate-i-ui-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v1.8.0.js').read_text()
EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v1.8.0.css').read_text()
class WorkspaceReleaseCandidateIContract(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.80.0','0.79.0','Workspace Release Candidate I')); self.assertIn('Version: 1.8.0',MAIN)
 def test_02_schema_freeze(self):
  for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']: self.assertEqual(MAN[k],OLD[k])
  self.assertEqual(MAN['object_types'],OLD['object_types']); self.assertFalse(MAN['schema_migration_required'])
 def test_03_feature_freeze_policy(self):
  r=MAN['release_candidate_i']; self.assertTrue(r['release_candidate']); self.assertTrue(r['feature_freeze']); self.assertTrue(r['canonical_schema_freeze']); self.assertFalse(r['new_product_subsystem']); self.assertFalse(r['automatic_promotion_to_stable']); self.assertEqual(r['feature_freeze_policy'],'defect-fixes-certification-deployment-only')
 def test_04_no_unplanned_manifest_surface(self):
  self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/release-candidate-contract'})
  self.assertEqual(set(MAN['object_types']),set(OLD['object_types']))
 def test_05_schemas(self):
  for f in ['sc-workspace-release-candidate-v1.schema.json','sc-workspace-release-candidate-report-v1.schema.json','sc-workspace-release-candidate-checklist-v1.schema.json']:
   self.assertTrue((R/'schemas'/f).exists()); json.loads((R/'schemas'/f).read_text())
 def test_06_rest_contract(self): self.assertIn("'/release-candidate-contract'",PHP); self.assertIn('release_candidate_contract',PHP); self.assertIn('/wp-json/sc-workspace/v1/release-candidate-contract',MAN['rest_routes'])
 def test_07_runtime_stage_and_ui(self): self.assertIn('data-release-stage="shared-review-rooms"',PHP); self.assertIn('data-scw-release-candidate',PHP); self.assertIn('Run RC gate',PHP); self.assertIn('Export field checklist',PHP); self.assertIn('data-scw-workspace-view="release-candidate"',PHP)
 def test_08_runtime_governance(self):
  for token in ['featureFreeze:true','newProductSubsystemsAllowed:false','canonicalSchemaChangesAllowed:false','automaticPromotionToStable:false','canonicalMutation:false','telemetry:false']: self.assertIn(token,CORE)
  self.assertIn('Production WordPress smoke test',CORE); self.assertIn('WordPress rollback rehearsal',CORE); self.assertIn('Real two-device continuity test',CORE)
 def test_09_assets(self): self.assertIn("'sc-workspace-v180'",PHP); self.assertIn('workspace-v1.8.0.js',PHP); self.assertIn('workspace-v1.8.0.css',PHP); self.assertIn('sc-workspace-release-candidate-i-v1',PHP); self.assertIn('sc-workspace-release-candidate-i-ui-v1',PHP); self.assertIn('/* v0.80.0 — Workspace Release Candidate I */',CSS); self.assertIn("'release-candidate'",APP); self.assertIn("id:'release-candidate'",EXP)
 def test_10_registry(self): self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.80.0','0.79.0','Workspace Release Candidate I')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v180'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0790',REGPHP); self.assertTrue((R/'history/release-manifest-v0.79.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.79.0.json').exists())
 def test_11_packaging_policy(self): r=MAN['release_candidate_i']; self.assertTrue(r['package_integrity_required']); self.assertTrue(r['rollback_artifact_required']); self.assertTrue(r['manual_field_validation_outstanding']); self.assertEqual(r['known_automated_blocker_count'],0)
 def test_12_docs(self): self.assertTrue((R/'docs/WORKSPACE_RELEASE_CANDIDATE_I_V0800.md').exists()); self.assertTrue((R/'RELEASE_NOTES_0.80.0.md').exists()); self.assertIn('# Sustainable Catalyst Workspace v1.8.0',(R/'README.md').read_text()); self.assertIn('General Availability',(R/'README.md').read_text())
 def test_13_validator(self): self.assertTrue((R/'scripts/validate_workspace_release_candidate_i.py').exists())
if __name__=='__main__': unittest.main()
