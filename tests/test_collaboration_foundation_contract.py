import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.26.0.js';PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php';CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.26.0.css';MANIFEST=ROOT/'release-manifest-v0.26.0.json'
class CollaborationFoundationContract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.26.0');self.assertEqual(m['previous_version'],'0.25.0');self.assertEqual(m['storage_schema_version'],25);self.assertEqual(m['project_schema'],'sc-workspace-project/11.0');self.assertEqual(m['collaboration_schema'],'sc-workspace-collaboration/1.0')
 def test_schema(self):
  s=json.loads((ROOT/'schemas/sc-workspace-collaboration-v1.schema.json').read_text());self.assertEqual(s['properties']['schema']['const'],'sc-workspace-collaboration/1.0');rp=json.loads((ROOT/'schemas/sc-workspace-review-package-v1.schema.json').read_text());self.assertEqual(rp['properties']['schema']['const'],'sc-workspace-review-package/1.0')
 def test_storage_migration_only(self):
  j=JS.read_text();self.assertIn('const STORAGE_VERSION = 25',j);self.assertIn('function migrateV18(raw)',j);self.assertIn('if (raw.schemaVersion === 18) return migrateV18(raw)',j);self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/11.0'",j)
 def test_top_level_view(self):
  p=PHP.read_text();self.assertIn('data-scw-workspace-view="collaboration"',p);self.assertIn('COLLABORATION FOUNDATION',p)
 def test_roles_are_descriptive(self):
  j=JS.read_text();self.assertIn("COLLAB_ROLES = new Set(['owner','contributor','reviewer','observer'])",j);m=json.loads(MANIFEST.read_text());self.assertFalse(m['collaboration_foundation']['roles_are_server_permissions'])
 def test_threads(self):
  j=JS.read_text();self.assertIn("COLLAB_THREAD_KIND = new Set(['comment','suggestion','question'])",j);self.assertIn("COLLAB_THREAD_STATUS = new Set(['open','resolved'])",j)
 def test_portable_request_response(self):
  j=JS.read_text();self.assertIn('async function collaborationRequestPackage',j);self.assertIn('async function collaborationResponsePackage',j);self.assertIn("kind:'request'",j);self.assertIn("kind:'response'",j)
 def test_integrity(self): self.assertIn("algorithm:'SHA-256'",JS.read_text())
 def test_request_imports_copy(self):
  j=JS.read_text();self.assertIn("copy.id=id('scwp')",j);self.assertIn('review copy',j)
 def test_response_requires_match(self):
  j=JS.read_text();self.assertIn('s.requestId===String(request.id',j);self.assertIn('s.sourceProjectId===String(request.sourceProjectId',j)
 def test_response_excludes_request_package_threads(self):
  j=JS.read_text();self.assertIn("t.origin!=='request-package'",j)
 def test_response_thread_deduplication_uses_source_thread_id(self):
  j=JS.read_text();self.assertIn('sourceThreadId',j);self.assertIn("known=new Set(session.threads.filter(t=>t.origin==='response'&&t.sourceThreadId)",j)
 def test_no_auto_mutation_or_cloud(self):
  m=json.loads(MANIFEST.read_text());c=m['collaboration_foundation'];self.assertFalse(c['live_collaboration']);self.assertFalse(c['server_collaboration']);self.assertFalse(c['imported_feedback_mutates_project_automatically'])
 def test_contract_endpoint(self): self.assertIn("'/collaboration-contract'",PHP.read_text())
 def test_styles(self): self.assertIn('.scw-collaboration{',CSS.read_text())
if __name__=='__main__': unittest.main()
