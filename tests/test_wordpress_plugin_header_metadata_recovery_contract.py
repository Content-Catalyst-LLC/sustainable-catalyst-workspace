from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAN=json.loads((ROOT/'release-manifest-v0.66.1.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.1.json').read_text())
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
B=MAIN.read_bytes(); T=MAIN.read_text()
WINDOW=B[:8192].decode('utf-8',errors='replace')
class HeaderRecovery(unittest.TestCase):
 def test_01_lineage(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.1','0.66.0','WordPress Plugin Header Metadata Recovery'))
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.66.1','0.66.0','WordPress Plugin Header Metadata Recovery'))
 def test_02_required_headers_inside_wordpress_window(self):
  for label in ['Plugin Name:','Version:','Author:','Requires at least:','Requires PHP:','Text Domain:']:
   pos=B.find(label.encode()); self.assertGreaterEqual(pos,0,label); self.assertLess(pos,8192,label)
 def test_03_wordpress_style_parse_window_finds_metadata(self):
  patterns={
   'name':r'^[ \t\/*#@]*Plugin Name:(.*)$','version':r'^[ \t\/*#@]*Version:(.*)$','author':r'^[ \t\/*#@]*Author:(.*)$',
   'wp':r'^[ \t\/*#@]*Requires at least:(.*)$','php':r'^[ \t\/*#@]*Requires PHP:(.*)$'}
  found={k:(re.search(v,WINDOW,re.I|re.M).group(1).strip() if re.search(v,WINDOW,re.I|re.M) else None) for k,v in patterns.items()}
  self.assertEqual(found,{'name':'Sustainable Catalyst Workspace','version':'1.0.0','author':'Content Catalyst LLC','wp':'6.4','php':'8.0'})
 def test_04_header_is_compact(self):
  self.assertLess(B.find(b'Description:'),1024); self.assertLess(B.find(b'Requires PHP:'),512)
  self.assertLess(len(re.search(r'/\*\*(.*?)\*/',T,re.S).group(0).encode()),2048)
 def test_05_plugin_constant(self): self.assertIn("define('SC_WORKSPACE_VERSION', '1.0.0');",T)
 def test_06_registry_lineage(self):
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v100'",REGPHP)
  self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v100'",REGPHP)
  self.assertIn("LEGACY_PENDING_KEY_V0660",REGPHP)
  self.assertIn("'previous_version' => '0.84.0'",REGPHP)
 def test_07_schema_stability(self):
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_08_v066_assets_retained(self):
  self.assertIn('workspace-v1.0.0.css',PHP); self.assertIn('workspace-v1.0.0.js',PHP)
if __name__=='__main__': unittest.main()
