import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.16.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.16.0.css'
MANIFEST=ROOT/'release-manifest-v0.16.0.json'
SCHEMA=ROOT/'schemas/sc-workspace-interoperability-v1.schema.json'
class InteroperabilityTests(unittest.TestCase):
 def test_release(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.16.0');self.assertEqual(m['previous_version'],'0.15.0');self.assertEqual(m['storage_schema_version'],17);self.assertEqual(m['project_schema'],'sc-workspace-project/11.0')
 def test_contract(self):
  p=PHP.read_text();self.assertIn("'/interoperability-contract'",p);self.assertIn("'staged_review_required' => true",p);self.assertIn("'automatic_overwrite' => false",p);self.assertIn("'server_import_pipeline' => false",p)
 def test_schema(self):
  s=json.loads(SCHEMA.read_text());self.assertEqual(s['properties']['schema']['const'],'sc-workspace-interoperability/1.0');self.assertEqual(s['properties']['history']['maxItems'],60)
 def test_local_staging_formats(self):
  j=JS.read_text();
  for token in ["'json','csv','tsv','markdown','html','text'",'stageExternalContent','csvRows','htmlToText','MAX_INTEROP_IMPORT_OBJECTS'] : self.assertIn(token,j)
 def test_sha256(self):
  j=JS.read_text();self.assertIn("digest('SHA-256'",j);self.assertEqual(json.loads(MANIFEST.read_text())['interoperability']['file_fingerprint_algorithm'],'SHA-256')
 def test_no_overwrite(self):
  j=JS.read_text();self.assertIn("const finalId=id('scwo')",j);self.assertFalse(json.loads(MANIFEST.read_text())['interoperability']['automatic_overwrite'])
 def test_imported_provenance(self):
  j=JS.read_text();self.assertIn("sourceType:'imported'",j);self.assertIn("obj.status='draft'",j)
 def test_interchange_export(self):
  j=JS.read_text();self.assertIn('function interchangePackage(project)',j);self.assertIn("sc-workspace-interchange/1.0",j);self.assertIn('canonicalObjectOverwrite:false',j);self.assertIn('Imported interoperability relationship',j);self.assertIn('sourceMap.get(rel.fromObjectId)',j)
 def test_project_schema_unchanged(self):
  j=JS.read_text();m=json.loads(MANIFEST.read_text());self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/11.0'",j);self.assertTrue(m['migration']['project_schema_unchanged'])
 def test_ui(self):
  p=PHP.read_text();c=CSS.read_text();self.assertIn('IMPORT &amp; INTEROPERABILITY',p);self.assertIn('data-scw-interoperability-form',p);self.assertIn('.scw-interoperability{',c)
 def test_human_commit(self):
  j=JS.read_text();m=json.loads(MANIFEST.read_text());self.assertIn('data-scw-interoperability-commit',PHP.read_text());self.assertFalse(m['interoperability']['automatic_commit']);self.assertTrue(m['interoperability']['staged_review_required'])
 def test_migrate_v14(self):
  j=JS.read_text();self.assertIn('function migrateV14(raw)',j);self.assertIn('if (raw.schemaVersion === 14) return migrateV14(raw)',j);self.assertIn('interoperability: interoperabilityTemplate()',j)
if __name__=='__main__':unittest.main()
