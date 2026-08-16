import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';MAN=json.loads((R/'history/release-manifest-v1.9.0.json').read_text());OLD=json.loads((R/'history/release-manifest-v1.8.0.json').read_text());REG=json.loads((R/'history/workspace-product-record-v1.9.0.json').read_text());MAIN=(P/'sustainable-catalyst-workspace.php').read_text();PHP=(P/'includes/class-sc-workspace.php').read_text();DEP=(P/'includes/class-sc-workspace-deployment.php').read_text();REGPHP=(P/'includes/class-sc-workspace-registry.php').read_text()
class InstitutionalAuditStudio(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('1.9.0','1.8.0','Institutional Governance, Provenance & Audit Studio'))
 def test_02_schema_freeze(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(OLD['storage_schema_version'],OLD['project_schema'],OLD['export_schema']))
 def test_03_only_route(self): self.assertEqual(set(MAN['rest_routes'])-set(OLD['rest_routes']),{'/wp-json/sc-workspace/v1/institutional-audit-studio-contract'})
 def test_04_evidence_families(self): self.assertEqual(MAN['institutional_audit_studio']['evidence_families'],['audit-trail','version-history','reconciliation-receipts','review-room-snapshots','decisions','institutional-handoff','knowledge-graph','project-lifecycle','citations','provenance'])
 def test_05_governance(self):
  g=MAN['institutional_audit_studio'];
  for k in ['explicit_scope','derived_from_authoritative_ledgers','canonical_records_remain_owned_by_source_subsystems','evidence_lineage_visible','decision_lineage_visible','relationship_explanations_visible','immutable_evidence_fingerprint','reproducible_audit_package_export','attestation_user_supplied','institutional_handoff_linked','review_room_evidence_linked']: self.assertTrue(g[k])
  for k in ['audit_package_copies_canonical_bodies','attestation_identity_inferred','regulatory_certification_claimed','compliance_score','automatic_compliance_inference','automatic_external_submission','automatic_canonical_mutation','automatic_ai','behavioral_telemetry','query_telemetry','schema_migration_required']: self.assertFalse(g[k])
 def test_06_wordpress(self): self.assertIn('Version: 1.13.0',MAIN);self.assertIn("SC_WORKSPACE_VERSION', '1.13.0'",MAIN);self.assertIn("'/institutional-audit-studio-contract'",PHP);self.assertIn('Institutional Audit Studio',PHP);self.assertIn('Auditability, not automatic compliance',PHP);self.assertIn('data-release-stage="connected-intelligence"',PHP)
 def test_07_deployment(self): self.assertIn("PREVIOUS_RELEASE = '1.12.0'",DEP);self.assertIn("ROLLBACK_RELEASE = '1.12.0'",DEP);self.assertIn('workspace-v1.13.0.js',DEP);self.assertIn('class-sc-workspace-institutional-audit-studio.php',DEP)
 def test_08_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('1.9.0','1.8.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v1130'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V180',REGPHP)
if __name__=='__main__':unittest.main()
