from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
FIELD=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-use-v1.js').read_text()
class T(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.82.1',MAIN)
 def test_02_schema_stable(self):
  self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['schema_migration_required'])
 def test_03_profile_schema(self):
  schema=json.loads((ROOT/'schemas/sc-workspace-field-use-profile-v1.schema.json').read_text());self.assertEqual(schema['properties']['schema']['const'],'sc-workspace-field-use-profile/1.0')
 def test_04_runtime_profile_boundaries(self):
  for marker in ["SCHEMA='sc-workspace-field-use-profile/1.0'","wide:1200","narrow:760","short:700","viewport:w>=TARGETS.wide?'wide'","profilePersistence:false","deviceFingerprinting:false"]:self.assertIn(marker,FIELD)
 def test_05_rest_contract(self):
  self.assertIn("'/field-use-contract'",PHP);self.assertIn('public function field_use_contract()',PHP);self.assertIn('/wp-json/sc-workspace/v1/field-use-contract',MAN['rest_routes'])
 def test_06_asset_wiring(self):
  self.assertIn("'sc-workspace-field-use-v1'",PHP);self.assertIn("array('sc-workspace-browser-compatibility-v1', 'sc-workspace-accessibility-v1')",PHP);self.assertIn("'sc-workspace-v0821'",PHP);self.assertIn('workspace-v0.82.1.css',PHP);self.assertIn('workspace-v0.82.1.js',PHP);self.assertIn('SCWorkspaceFieldUse.boot(window)',APP)
 def test_07_touch_and_short_viewport_css(self):
  self.assertIn('data-scw-input="coarse"',CSS);self.assertIn('min-height:44px',CSS);self.assertIn('data-scw-short-viewport="1"',CSS);self.assertIn('@media(max-height:700px) and (orientation:landscape)',CSS)
 def test_08_reflow_and_bounded_dense_surfaces(self):
  for marker in ['@media(max-width:1180px)','@media(max-width:980px)','@media(max-width:760px)','@media(max-width:620px)','@media(max-width:430px)','table{display:block;overflow-x:auto']:
   self.assertIn(marker,CSS)
 def test_09_lab_handoffs(self):
  self.assertIn('class="scw-pathway-link"',PHP);self.assertIn('Explore the Lab',PHP);self.assertIn('class="scw-button scw-lab-handoff"',PHP);self.assertIn('Open the Lab',PHP);self.assertGreaterEqual(PHP.count("home_url('/lab/')"),3)
 def test_10_hero_remains_uncluttered(self):
  hero=PHP[PHP.index('scw-platform-actions'):PHP.index('scw-platform-access-grid')];self.assertIn('Explore the Library',hero);self.assertNotIn('Explore the Lab',hero)
 def test_11_privacy_and_governance(self):
  r=MAN['responsive_field_use_experience'];self.assertFalse(r['device_fingerprinting']);self.assertFalse(r['profile_persistence']);self.assertFalse(r['automatic_upload']);self.assertFalse(r['telemetry']);self.assertFalse(r['canonical_mutation']);self.assertTrue(r['manual_device_qa_required'])
 def test_12_registry_and_history(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0821'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0641',REGPHP);self.assertTrue((ROOT/'history/release-manifest-v0.64.1.json').exists());self.assertTrue((ROOT/'history/workspace-product-record-v0.64.1.json').exists())
 def test_13_previous_hardening_retained(self):
  block=re.search(r"wp_enqueue_script\(\s*'sc-workspace-accessibility-v1'.*?\n\s*\);",PHP,re.S).group(0);self.assertIn("array('sc-workspace-browser-compatibility-v1')",block);self.assertNotIn("'sc-workspace-accessibility-v1'",re.search(r'array\((.*?)\)',block,re.S).group(1));self.assertIn('.scw-platform-hero-grid{grid-template-columns:minmax(0,1.18fr) minmax(0,.82fr)}',CSS)
if __name__=='__main__':unittest.main()
