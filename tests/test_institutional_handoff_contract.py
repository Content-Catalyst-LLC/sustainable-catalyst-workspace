import json, re, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'release-manifest-v0.34.0.json'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.34.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.34.0.css'
REG=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php'
class InstitutionalHandoffContract(unittest.TestCase):
 def test_release_metadata(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.34.0');self.assertEqual(m['previous_version'],'0.33.0');self.assertEqual(m['release_name'],'Notebook Collections & Knowledge Linking');self.assertEqual(m['storage_schema_version'],30);self.assertEqual(m['project_schema'],'sc-workspace-project/15.0')
 def test_contracts(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['institutional_handoff_schema'],'sc-workspace-institutional-handoff/1.0');self.assertEqual(m['institutional_handoff_package_schema'],'sc-workspace-institutional-handoff-package/1.0');self.assertEqual(m['institutional_handoff_receipt_schema'],'sc-workspace-institutional-handoff-receipt/1.0')
 def test_schema_json(self):
  for f in ('sc-workspace-institutional-handoff-v1.schema.json','sc-workspace-institutional-handoff-package-v1.schema.json','sc-workspace-institutional-handoff-receipt-v1.schema.json'): json.loads((ROOT/'schemas'/f).read_text())
 def test_storage_only_migration(self):
  j=JS.read_text();self.assertIn('const STORAGE_VERSION = 30',j);self.assertIn('function migrateV19(raw)',j);self.assertIn('if (raw.schemaVersion === 19) return migrateV19(raw)',j);self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/15.0'",j)
 def test_top_level_view(self):
  p=PHP.read_text();self.assertIn('data-scw-workspace-view="institutional"',p);self.assertIn('data-scw-workspace-section="institutional"',p);self.assertIn('INSTITUTIONAL HANDOFF',p)
 def test_explicit_scope(self):
  p=PHP.read_text();j=JS.read_text();self.assertIn('data-scw-institutional-object-scope',p);self.assertIn('renderInstitutionalObjectScope',j);self.assertIn('objectIds',j)
 def test_human_acknowledgements(self):
  p=PHP.read_text();j=JS.read_text();self.assertIn('name="copyModel" required',p);self.assertIn('name="institutionalGovernance" required',p);self.assertIn('name="sharingReviewed" required',p);self.assertIn('copyModel:Boolean',j);self.assertIn('institutionalGovernance:Boolean',j);self.assertIn('sharingReviewed:Boolean',j)
 def test_readiness_is_not_score(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['institutional_handoff']['readiness_model'],'explainable-checklist-no-score');self.assertFalse(m['governance']['institutional_readiness_score']);self.assertIn('institutionalReadiness',JS.read_text())
 def test_target_and_copy_model(self):
  j=JS.read_text();self.assertIn("targetProduct:'catalyst-intelligence-platform'",j);self.assertIn("requestedMode:'institutional-copy'",j);self.assertIn('sourceWorkspaceRetainsIndependentCopy:true',j)
 def test_sha256_integrity(self):
  j=JS.read_text();self.assertIn("algorithm:'SHA-256'",j);self.assertIn('sha256Text',j)
 def test_privacy_minimized_package(self):
  j=JS.read_text();
  for token in ('deviceIdentityIncluded:false','accountIdentityIncluded:false','connectedToolHandoffStateIncluded:false','recentToolsIncluded:false','activityHistoryIncluded:false','aiReviewHistoryIncluded:false','collaborationHistoryIncluded:false'): self.assertIn(token,j)
 def test_receipt_matching(self):
  j=JS.read_text();self.assertIn("pkg.schema!==INSTITUTIONAL_RECEIPT_SCHEMA",j);self.assertIn("h.id===String(pkg.handoffId||'')",j);self.assertIn("h.sourceProjectId===String(pkg.sourceProjectId||'')",j);self.assertIn("pkg.targetProduct==='catalyst-intelligence-platform'",j)
 def test_receipt_does_not_mutate_project_content(self):
  m=json.loads(MANIFEST.read_text());self.assertFalse(m['governance']['institutional_handoff_source_project_mutation']);self.assertFalse(m['institutional_handoff']['source_project_mutation_on_receipt'])
 def test_no_auto_upload_or_ingestion(self):
  m=json.loads(MANIFEST.read_text());self.assertFalse(m['institutional_handoff']['automatic_upload']);self.assertFalse(m['institutional_handoff']['automatic_ingestion']);self.assertFalse(m['governance']['organization_permissions_in_workspace'])
 def test_activity_signal(self):
  j=JS.read_text();p=PHP.read_text();self.assertIn("'institutional'",j);self.assertIn('Institutional handoff awaiting institutional receipt',j);self.assertIn('<option value="institutional">Institutional handoff</option>',p)
 def test_rest_contract(self):
  p=PHP.read_text();self.assertIn("'/institutional-handoff-contract'",p);self.assertIn('institutional_handoff_contract',p);self.assertIn("'storage_schema_version' => 30",p)
 def test_registry_lineage(self):
  r=REG.read_text();self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0340'",r);self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0340'",r);self.assertIn("LEGACY_PENDING_KEY_V0240 = 'sc_workspace_registry_pending_v0240'",r);self.assertIn("LEGACY_PENDING_KEY_V0220 = 'sc_workspace_registry_pending_v0220'",r)
 def test_css(self):
  c=CSS.read_text();self.assertIn('/* v0.21.0 — Institutional Handoff */',c);self.assertIn('.scw-institutional-boundary',c);self.assertIn('.scw-institutional-readiness',c)
if __name__=='__main__': unittest.main()
