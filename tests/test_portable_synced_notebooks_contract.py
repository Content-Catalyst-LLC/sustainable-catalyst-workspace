import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text());PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text();NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v8.js').read_text();PORT=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-notebook-portability-v1.js').read_text()
class PortableSyncedNotebooks(unittest.TestCase):
 def test_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'))
 def test_migration(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'));self.assertEqual((MAN['migration']['storage_from'],MAN['migration']['storage_to']),(35,35));self.assertTrue(MAN['migration']['project_schema_unchanged']);self.assertIn('function migrateV34(raw)',JS);self.assertIn('if (raw.schemaVersion === 34) return migrateV34(raw);',JS)
 def test_notebook_v7(self): self.assertEqual(MAN['notebook_workspace_schema'],'sc-workspace-notebook-workspace/8.0');self.assertEqual(MAN['notebook_export_schema'],'sc-workspace-notebook-export/8.0');self.assertIn("WORKSPACE_SCHEMA='sc-workspace-notebook-workspace/8.0'",NB);self.assertIn('portabilityState',NB)
 def test_portability_integrity(self):
  for x in ('portablePackage','validatePortable','importAsCopy','restorePoint','restoreAsCopy','SHA-256','new-notebook-copy'):self.assertIn(x,PORT)
 def test_conflict_safety(self):
  for x in ('expectedRevision','revision-precondition','silentLastWriteWins:false','conflict'):self.assertIn(x,PORT)
  for x in ('scw_notebook_sync_conflict','currentRevision','Nothing was overwritten'):self.assertIn(x,PHP)
 def test_rest(self):
  for x in ("'/cloud-notebooks'","'/cloud-notebooks/(?P<notebook_id>",'cloud_notebook_store','cloud_notebooks_list'):self.assertIn(x,PHP)
 def test_ui(self):
  for x in ('data-scw-notebook-portable-import','data-scw-notebook-restore-create','data-scw-notebook-backup','data-scw-notebook-sync-toggle','data-scw-notebook-sync-now','No silent last-write-wins'):self.assertIn(x,PHP)
 def test_governance(self):
  g=MAN['governance'];self.assertTrue(g['notebook_portable_import_new_copy_only']);self.assertTrue(g['notebook_sync_explicit_enrollment_required']);self.assertTrue(g['notebook_sync_server_revision_precondition']);self.assertTrue(g['notebook_sync_conflicts_preserve_both']);self.assertFalse(g['notebook_background_sync']);self.assertFalse(g['notebook_silent_last_write_wins'])
 def test_schemas(self):
  for n in ('sc-workspace-project-v19.schema.json','sc-workspace-notebook-workspace-v7.schema.json','sc-workspace-notebook-export-v7.schema.json','sc-workspace-notebook-portable-package-v1.schema.json','sc-workspace-notebook-restore-point-v1.schema.json','sc-workspace-notebook-sync-enrollment-v1.schema.json','sc-workspace-notebook-cloud-backup-v1.schema.json','sc-workspace-notebook-sync-push-v1.schema.json'):json.loads((ROOT/'schemas'/n).read_text())
if __name__=='__main__':unittest.main()
