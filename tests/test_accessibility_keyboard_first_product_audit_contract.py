from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
A11Y=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-v1.js').read_text()
A11YUI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-ui-v1.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
EXP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class T(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening'));self.assertIn('Version: 0.75.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual(MAN['storage_schema_version'],35);self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0');self.assertFalse(MAN['schema_migration_required'])
 def test_03_contract_schemas(self):
  for n in ['sc-workspace-accessibility-v1.schema.json','sc-workspace-accessibility-report-v1.schema.json','sc-workspace-accessibility-checklist-v1.schema.json']: json.loads((ROOT/'schemas'/n).read_text())
 def test_04_target_and_claim_boundary(self): self.assertEqual(MAN['accessibility_keyboard_audit']['target'],'WCAG 2.2 AA');self.assertFalse(MAN['accessibility_keyboard_audit']['automated_certification']);self.assertTrue(MAN['accessibility_keyboard_audit']['manual_audit_required']);self.assertIn('Automated checks and this checklist support field QA',A11Y)
 def test_05_keyboard_groups(self): self.assertIn('wireKeyboardGroup',A11Y);self.assertIn("['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End']",A11Y);self.assertIn('data-scw-keyboard-nav="1"',PHP)
 def test_06_dialog_focus(self): self.assertIn('containTab',A11Y);self.assertIn('installDialogGuard',A11Y);self.assertIn('opener=lastOutside||doc.activeElement',A11Y);self.assertIn("event.key==='Escape'",A11Y);self.assertIn('dialogOpener=document.activeElement',EXP)
 def test_07_semantic_audit(self):
  for marker in ['skip-link','primary-navigation','section-labels','dialogs','status-messages','form-labels','zoom-reflow','screen-reader']: self.assertIn(marker,A11Y)
 def test_08_privacy(self): self.assertIn('projectContentIncluded:false',A11Y);self.assertIn('sourceContentIncluded:false',A11Y);self.assertIn('rawUserAgentIncluded:false',A11Y);self.assertIn('deviceIdentifierIncluded:false',A11Y);self.assertFalse(MAN['accessibility_keyboard_audit']['telemetry'])
 def test_09_manual_checklist(self):
  for marker in ['keyboard-complete','focus-order','zoom-200','reflow-400','screen-reader-voiceover','screen-reader-windows','forced-colors','contrast','errors']: self.assertIn(marker,A11Y)
 def test_10_route_and_rest(self): self.assertIn('data-scw-workspace-view="accessibility"',PHP);self.assertIn('data-scw-workspace-section="accessibility"',PHP);self.assertIn("accessibility:'Accessibility'",NAV);self.assertIn("'/accessibility-contract'",PHP);self.assertIn('/wp-json/sc-workspace/v1/accessibility-contract',MAN['rest_routes'])
 def test_11_route_visibility_normalized(self): self.assertIn("root.querySelectorAll('[data-scw-workspace-section]').forEach(section => { section.hidden = section.dataset.scwWorkspaceSection !== workspaceView; });",APP);self.assertIn("'compatibility','accessibility','interoperability'",APP)
 def test_12_command_palette(self): self.assertIn("id:'accessibility'",EXP);self.assertIn('keyboard focus wcag screen reader',EXP)
 def test_13_css(self): self.assertIn(':focus-visible{outline:3px solid currentColor!important',CSS);self.assertIn('@media(prefers-reduced-motion:reduce)',CSS);self.assertIn('@media(forced-colors:active)',CSS);self.assertIn('min-height:44px',CSS)
 def test_14_ui(self): self.assertIn('helper.enhance(root,window)',A11YUI);self.assertIn('helper.audit(root,window)',A11YUI);self.assertIn('helper.checklist()',A11YUI);self.assertIn('This is not an accessibility certification.',A11YUI)
 def test_15_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0'));self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0750'",REGPHP);self.assertIn('LEGACY_PENDING_KEY_V0630',REGPHP);self.assertTrue((ROOT/'history/release-manifest-v0.64.0.json').exists())
if __name__=='__main__': unittest.main()
