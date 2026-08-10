import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.52.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.52.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.52.0.js').read_text()
NAV=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-navigation-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.52.0.css').read_text()
class UnifiedResearchNavigation(unittest.TestCase):
 def test_01_lineage(self): self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.52.0','0.51.0','Research Tasks & Workflow State')); self.assertIn('Version: 0.52.0',MAIN)
 def test_02_schema_stable(self): self.assertEqual((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema']),(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0')); self.assertFalse(MAN['schema_migration_required']); self.assertTrue(MAN['migration']['schema_stable']); self.assertTrue(json.loads((ROOT/'history/release-manifest-v0.41.0.json').read_text())['migration']['navigation_only_release']); self.assertFalse(MAN['migration']['canonical_data_rewrite'])
 def test_03_navigation_contract(self): self.assertIn('/wp-json/sc-workspace/v1/navigation-contract',MAN['rest_routes']); self.assertIn("'/navigation-contract'",PHP); self.assertIn('public function navigation_contract()',PHP); self.assertIn("'moves_canonical_data' => false",PHP)
 def test_04_primary_areas(self): self.assertEqual(MAN['primary_navigation'],['start','projects','research','review','exchange']); self.assertIn('data-scw-workspace-area="research"',PHP); self.assertIn('data-scw-workspace-area="review"',PHP); self.assertIn('data-scw-workspace-area="exchange"',PHP)
 def test_05_contextual_routes(self):
  self.assertEqual(MAN['navigation_routes']['research'],['research','notebook','knowledge','graph']); self.assertEqual(MAN['navigation_routes']['review'],['activity','lifecycle','history','changes','reconcile','safety','audit']); self.assertEqual(MAN['navigation_routes']['exchange'],['interoperability','collaboration','institutional','share'])
  for token in ('data-scw-workspace-context-nav="research"','data-scw-workspace-context-nav="review"','data-scw-workspace-context-nav="exchange"'): self.assertIn(token,PHP)
 def test_06_research_pathways(self):
  for token in ('data-scw-research-route="research"','data-scw-research-route="notebook"','data-scw-research-route="knowledge"','data-scw-research-route="graph"'): self.assertIn(token,PHP)
  self.assertIn('Sources, Evidence, Datasets, Analysis, Decisions, and Documents',PHP)
 def test_07_runtime(self):
  for token in ("const SCHEMA='sc-workspace-navigation-map/1.0'",'function areaForView(view)','function defaultView(area)','function context(view)','function map()'): self.assertIn(token,NAV)
  self.assertIn('function syncWorkspaceNavigation()',JS); self.assertIn("data-scw-research-route",JS); self.assertIn('workspaceContextNavs.forEach',JS)
 def test_08_specialized_surfaces_retained(self):
  for view in ('research','notebook','knowledge','graph','activity','lifecycle','history','changes','reconcile','safety','audit','interoperability','collaboration','institutional','share'): self.assertIn(f'data-scw-workspace-view="{view}"',PHP)
 def test_09_governance(self):
  g=MAN['governance']; self.assertTrue(g['navigation_derived_from_existing_surfaces']); self.assertFalse(g['navigation_moves_canonical_data']); self.assertFalse(g['navigation_duplicates_canonical_content']); self.assertFalse(g['navigation_automatic_semantic_inference']); self.assertFalse(g['navigation_automatic_ai']); self.assertTrue(g['specialized_research_surfaces_retained'])
 def test_10_accessibility_css(self): self.assertIn('.scw-workspace-primary-nav',CSS); self.assertIn('.scw-workspace-context-nav',CSS); self.assertIn('@media(forced-colors:active)',CSS); self.assertIn('ArrowLeft',JS); self.assertIn('ArrowRight',JS)
 def test_11_registry_history(self): self.assertEqual((REG['public_version'],REG['previous_version']),('0.52.0','0.51.0')); self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0520'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0410',REGPHP); self.assertTrue((ROOT/'history/release-manifest-v0.41.0.json').exists()); self.assertTrue((ROOT/'history/workspace-product-record-v0.41.0.json').exists())
 def test_12_schema_json(self): json.loads((ROOT/'schemas/sc-workspace-navigation-map-v1.schema.json').read_text())
if __name__=='__main__': unittest.main()
