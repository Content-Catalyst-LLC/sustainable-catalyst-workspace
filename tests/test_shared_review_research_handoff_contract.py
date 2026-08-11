import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-ui-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class TestSharedReviewResearchHandoff(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.68.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['schema_migration_required'])
 def test_03_schemas(self): self.assertEqual(MAN['shared_review_package_schema'],'sc-workspace-shared-review-package/1.0');self.assertTrue((ROOT/'schemas/sc-workspace-shared-review-response-v1.schema.json').exists())
 def test_04_explicit_frozen_scope(self): self.assertIn('scopeObjectIds',HELP);self.assertIn('frozenSnapshot:true',HELP);self.assertTrue(MAN['governance']['shared_review_scope_explicit']);self.assertTrue(MAN['governance']['shared_review_scope_frozen_on_prepare'])
 def test_05_package_integrity(self): self.assertIn('validatePackage',HELP);self.assertIn('packageFingerprint',HELP);self.assertTrue(MAN['governance']['shared_review_package_fingerprint_required'])
 def test_06_response_match(self): self.assertIn('validateResponse',HELP);self.assertIn('Response does not match the originating review package.',HELP);self.assertTrue(MAN['governance']['shared_review_response_must_match_package'])
 def test_07_stage_before_commit(self): self.assertIn('stageResponse',HELP);self.assertIn('commitResponse',HELP);self.assertTrue(MAN['governance']['shared_review_response_staged_before_commit']);self.assertIn('Commit staged response',PHP)
 def test_08_no_canonical_mutation(self): self.assertIn('canonicalMutation:false',HELP);self.assertFalse(MAN['governance']['shared_review_import_mutates_canonical_project']);self.assertFalse(MAN['governance']['shared_review_proposal_acceptance_mutates_canonical'])
 def test_09_external_reviewer_flow(self): self.assertIn('data-scw-reviewer-package-import',PHP);self.assertIn('Export matched response',PHP);self.assertIn('createResponse',UI)
 def test_10_rest_and_assets(self): self.assertIn("'/shared-review-handoff-contract'",PHP);self.assertIn('public function shared_review_handoff_contract()',PHP);self.assertIn('sc-workspace-shared-review-handoff-v1.js',PHP);self.assertIn('/wp-json/sc-workspace/v1/shared-review-handoff-contract',MAN['rest_routes'])
 def test_11_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0680'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0530',REGPHP)
 def test_12_header_retained(self): self.assertEqual(MAN['governance']['editorial_header_rule_px'],4);self.assertRegex(CSS,r'\.scw-editorial-header-bar\{height:4px');self.assertIn('border-top:4px solid #000',CSS)
 def test_13_history_retained(self): self.assertTrue((ROOT/'history/release-manifest-v0.53.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.53.0.json').exists())
if __name__=='__main__':unittest.main()
