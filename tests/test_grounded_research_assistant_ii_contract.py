import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.0.json').read_text())
PREV=json.loads((ROOT/'history/release-manifest-v0.50.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.66.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-grounded-research-assistant-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.66.0.css').read_text()
class GroundedResearchAssistantII(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.66.0','0.65.0','Import, Export & Backward-Compatibility Hardening')); self.assertIn('Version: 1.1.0',MAIN); self.assertEqual(PREV['release_name'],'Workspace Experience Consolidation')
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['grounded_research_assistant_only_release']); self.assertFalse(MAN['migration']['grounded_research_canonical_data_rewrite'])
 def test_03_schemas(self):
  self.assertEqual(MAN['grounded_research_assistant_schema'],'sc-workspace-grounded-research-assistant/1.0'); self.assertEqual(MAN['grounded_research_request_schema'],'sc-workspace-grounded-research-request/1.0'); self.assertEqual(MAN['grounded_research_response_schema'],'sc-workspace-grounded-research-response/1.0')
  for n in ('sc-workspace-grounded-research-assistant-v1.schema.json','sc-workspace-grounded-research-request-v1.schema.json','sc-workspace-grounded-research-response-v1.schema.json','sc-workspace-grounded-research-request-export-v1.schema.json','sc-workspace-grounded-research-response-export-v1.schema.json'): json.loads((ROOT/'schemas'/n).read_text())
 def test_04_explicit_scope_and_freeze(self): self.assertTrue(MAN['grounded_research_assistant']['scope_selection']=='explicit-multi-record'); self.assertIn('prepareRequest',HELP); self.assertIn('groundingFingerprint',HELP); self.assertIn('canonicalGrounding',HELP); self.assertIn('MAX_SCOPE=64',HELP)
 def test_05_citation_enforcement(self): self.assertTrue(MAN['grounded_research_assistant']['citation_enforcement']); self.assertTrue(MAN['grounded_research_assistant']['substantive_segment_citation_required']); self.assertIn('citationCoverage',HELP); self.assertIn('invalidMarkers',HELP); self.assertIn('uncitedSegments',HELP)
 def test_06_draft_review_materialization(self): self.assertTrue(MAN['grounded_research_assistant']['human_review_required']); self.assertEqual(MAN['grounded_research_assistant']['materialization'],'explicit-document-only'); self.assertIn("session.status='reviewed'",JS); self.assertIn("session.status='rejected'",JS); self.assertIn("session.status='materialized'",JS); self.assertIn('grounded-research-document',JS)
 def test_07_provider_neutral_no_auto_ai(self): self.assertTrue(MAN['grounded_research_assistant']['provider_neutral']); self.assertFalse(MAN['grounded_research_assistant']['automatic_ai']); self.assertFalse(MAN['governance']['grounded_research_automatic_ai']); self.assertIn('Copy grounded prompt',PHP); self.assertIn('Export request',PHP)
 def test_08_no_scope_expansion_or_mutation(self): self.assertFalse(MAN['governance']['grounded_research_automatic_scope_expansion']); self.assertFalse(MAN['governance']['grounded_research_automatic_canonical_write']); self.assertFalse(MAN['grounded_research_assistant']['metadata_invention']); self.assertIn('automaticScopeExpansion:false',HELP); self.assertIn('automaticCanonicalMutation:false',HELP)
 def test_09_ui(self):
  for t in ('data-scw-grounded-research-assistant','data-scw-grounded-add-selected','data-scw-grounded-form','data-scw-grounded-prompt','data-scw-grounded-response','data-scw-grounded-materialize'): self.assertIn(t,PHP)
  self.assertIn('scw-grounded-research-layout',CSS); self.assertIn('renderGroundedResearchAssistant()',JS)
 def test_10_rest_and_assets(self): self.assertIn("'/grounded-research-assistant-contract'",PHP); self.assertIn('public function grounded_research_assistant_contract()',PHP); self.assertIn('/wp-json/sc-workspace/v1/grounded-research-assistant-contract',MAN['rest_routes']); self.assertIn('sc-workspace-grounded-research-assistant-v1.js',PHP); self.assertIn('workspace-v1.1.0.js',PHP); self.assertIn('workspace-v1.1.0.css',PHP)
 def test_11_browser_local(self): self.assertTrue(MAN['grounded_research_assistant']['browser_local_library']); self.assertTrue(MAN['migration']['grounded_research_library_browser_local']); self.assertIn("STORAGE_KEY='sc_workspace_grounded_research_assistant_v1'",HELP); self.assertIn('localStorage.setItem(api.STORAGE_KEY',JS)
 def test_12_registry_and_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.66.0','0.65.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v110'",REGPHP); self.assertIn("LEGACY_PENDING_KEY_V0500 = 'sc_workspace_registry_pending_v0500'",REGPHP); self.assertTrue((ROOT/'history/workspace-product-record-v0.50.0.json').exists())
 def test_13_v050_experience_retained(self): self.assertIn('.scw-editorial-header-bar{height:4px',CSS); self.assertEqual(MAN['workspace_experience']['editorial_header_rule_px'],4); self.assertIn('sc-workspace-experience-v1.js',PHP); self.assertEqual(PREV['experience_schema'],'sc-workspace-experience/1.0')
if __name__=='__main__': unittest.main()
