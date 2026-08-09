import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.28.0.js';PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php';CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.28.0.css';MANIFEST=ROOT/'release-manifest-v0.28.0.json'
class SharePortableProjectsTests(unittest.TestCase):
 def test_release(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.28.0');self.assertEqual(m['previous_version'],'0.27.0');self.assertEqual(m['storage_schema_version'],26);self.assertEqual(m['project_schema'],'sc-workspace-project/11.0')
 def test_contract(self):
  p=PHP.read_text();self.assertIn("'/share-contract'",p);self.assertIn("'public_share_links' => false",p);self.assertIn("'collaboration' => false",p);self.assertIn("'import_overwrites_existing_project' => false",p)
 def test_package(self):
  j=JS.read_text();self.assertIn("const PORTABLE_PROJECT_SCHEMA = 'sc-workspace-portable-project/1.0'",j);self.assertIn('function portableProjectPackage',j);self.assertIn("digest('SHA-256'",j);self.assertIn('function verifyPortablePackage',j)
 def test_privacy(self):
  j=JS.read_text();self.assertIn('delete clone.persistence',j);self.assertIn('delete clone.recentTools',j);self.assertIn('delete clone.handoffs',j);self.assertIn('activityIncluded:Boolean(options.includeActivity)',j);self.assertIn('aiReviewHistoryIncluded:Boolean(options.includeAi)',j)
 def test_import_as_copy(self):
  j=JS.read_text();self.assertIn("copy.id=id('scwp')",j);self.assertIn('copy.persistence=projectPersistenceTemplate()',j);self.assertIn('copy.handoffs=handoffLedgerTemplate()',j);self.assertIn('Import as copy',PHP.read_text())
 def test_review_copy(self):
  j=JS.read_text();self.assertIn('function reviewCopyHtml',j);self.assertIn('Static review copy.',j)
 def test_storage_only_migration(self):
  j=JS.read_text();m=json.loads(MANIFEST.read_text());self.assertIn('function migrateV15(raw)',j);self.assertIn('if (raw.schemaVersion === 15) return migrateV15(raw)',j);self.assertTrue(m['migration']['project_schema_unchanged']);self.assertIn('state.share = normalizeShare(raw.share)',j)
 def test_ui(self):
  p=PHP.read_text();c=CSS.read_text();self.assertIn('SHARE &amp; PORTABLE PROJECTS',p);self.assertIn('data-scw-share-export',p);self.assertIn('data-scw-share-import',p);self.assertIn('.scw-share{',c);self.assertIn("['projects','knowledge','graph','activity','history','changes','reconcile','safety','audit','interoperability','collaboration','institutional','share']",JS.read_text());self.assertIn("shareSection.hidden = workspaceView !== 'share'",JS.read_text())
if __name__=='__main__':unittest.main()
