import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.51.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.51.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.51.0.js').read_text()
NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text()
REVIEW=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-notebook-review-provenance-v1.js').read_text()
class NotebookReviewProvenance(unittest.TestCase):
 def test_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.51.0','0.50.0','Grounded Research Assistant II'));self.assertIn('Version: 0.51.0',MAIN)
 def test_migration(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35));self.assertTrue(MAN['migration']['project_schema_unchanged']);self.assertIn('function migrateV34(raw)',JS);self.assertIn('if (raw.schemaVersion === 34) return migrateV34(raw);',JS)
 def test_notebook_v8(self): self.assertEqual((MAN['notebook_workspace_schema'],MAN['notebook_export_schema']),('sc-workspace-notebook-workspace/8.0','sc-workspace-notebook-export/8.0'));self.assertIn("WORKSPACE_SCHEMA='sc-workspace-notebook-workspace/8.0'",NB);self.assertIn('governanceState',NB);self.assertIn('reviewProvenance',NB)
 def test_review_runtime(self):
  for x in ('buildReview','diff','hiddenChangeScore:false','reviewOnly:true','sourceStatesUnchanged:true'): self.assertIn(x,REVIEW)
 def test_reconciliation(self):
  for x in ('buildReconciliation','applyReconciliation','newNotebookCopyOnly:true','preservesBothSourceStates:true','A reconciled notebook copy was created'): self.assertIn(x,REVIEW)
 def test_audit_lineage(self):
  for x in ('auditEvents','lineage','shadowProvenanceDatabase:false','automaticInference:false','derivedFromAuthoritativeRecords:true'): self.assertIn(x,REVIEW)
 def test_ui(self):
  for x in ('data-scw-notebook-review-create','data-scw-notebook-review-list','data-scw-notebook-reconcile-create','data-scw-notebook-lineage-inspect','data-scw-notebook-audit-list'): self.assertIn(x,PHP)
 def test_governance(self):
  g=MAN['governance'];self.assertTrue(g['notebook_change_review_explicit']);self.assertFalse(g['notebook_change_review_hidden_score']);self.assertTrue(g['notebook_reconciliation_explicit_selection_required']);self.assertTrue(g['notebook_reconciliation_new_copy_only']);self.assertTrue(g['notebook_audit_history_derived']);self.assertFalse(g['notebook_audit_shadow_database']);self.assertFalse(g['notebook_lineage_automatic_inference'])
 def test_registry(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.51.0','0.50.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0510'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0380',REGPHP)
 def test_history(self): self.assertTrue((ROOT/'history/release-manifest-v0.39.0.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.39.0.json').exists())
 def test_schemas(self):
  for n in ('sc-workspace-project-v20.schema.json','sc-workspace-notebook-workspace-v8.schema.json','sc-workspace-notebook-export-v8.schema.json','sc-workspace-notebook-change-review-v1.schema.json','sc-workspace-notebook-reconciliation-v1.schema.json','sc-workspace-notebook-audit-event-v1.schema.json','sc-workspace-notebook-lineage-v1.schema.json','sc-workspace-notebook-governance-v1.schema.json'): json.loads((ROOT/'schemas'/n).read_text())
if __name__=='__main__':unittest.main()
