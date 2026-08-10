import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.50.0.js'
class Identity(unittest.TestCase):
 def test_identity_schema(self):
  i=json.loads((ROOT/'schemas/sc-workspace-identity-v1.schema.json').read_text()); self.assertEqual(i['properties']['schema']['const'],'sc-workspace-identity/1.0'); self.assertFalse(i['properties']['cloudSync']['const']); self.assertFalse(i['properties']['serverProjectStorage']['const'])
 def test_project_persistence(self):
  s=json.loads((ROOT/'schemas/sc-workspace-project-v4.schema.json').read_text()); self.assertIn('persistence',s['required']); p=s['properties']['persistence']['properties']; self.assertEqual(p['scope']['const'],'device'); self.assertEqual(p['syncState']['const'],'local-only'); self.assertFalse(p['serverStored']['const'])
 def test_js_boundary(self):
  t=JS.read_text();
  for x in ('DEVICE_KEY','function deviceId()','function identityTemplate()','function projectPersistenceTemplate()','function renderIdentity()','function migrateV4(raw)',"if (raw.schemaVersion === 4) return migrateV4(raw)"): self.assertIn(x,t)
 def test_export_redacts_device_id(self):
  t=JS.read_text(); self.assertIn("deviceId: 'scwd-portable'",t)
 def test_no_project_upload(self):
  m=json.loads((ROOT/'release-manifest-v0.50.0.json').read_text()); self.assertFalse(m['governance']['automatic_cloud_upload']); self.assertFalse(m['governance']['account_session_uploads_project_content']); self.assertFalse(m['governance']['sign_in_changes_storage_scope'])
if __name__=='__main__': unittest.main()
