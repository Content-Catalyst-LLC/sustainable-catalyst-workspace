import json, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.72.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.72.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-workflow-guidance-v1.js').read_text()
UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-workflow-guidance-ui-v1.js').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.0.1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.0.1.css').read_text()
class ResearchWorkflowGuidanceContract(unittest.TestCase):
 def test_release_lineage_schema_stability(self):
  self.assertEqual((MAN['version'],MAN['previous_version'],MAN['release_name']),('0.72.0','0.71.0','Research Workflow Guidance & Empty-State Refinement'))
  self.assertEqual(MAN['storage_schema_version'],35); self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0'); self.assertFalse(MAN['schema_migration_required'])
 def test_guidance_contract(self):
  g=MAN['research_workflow_guidance']; self.assertEqual(g['mode'],'derived-contextual-advisory'); self.assertEqual(g['stages'],['orient','frame','gather','extract','connect','synthesize','compose','review'])
  for k in ['canonical_mutation','automatic_completion','automatic_task_creation','automatic_ai','automatic_navigation','hidden_readiness_score','behavioral_tracking','telemetry','schema_migration_required']: self.assertFalse(g[k],k)
 def test_runtime_and_ui(self):
  for marker in ['frame-question','capture-source','extract-evidence','test-claim','synthesize-notes','compose','review-next','hiddenReadinessScore:false','automaticTaskCreation:false','automaticAi:false']: self.assertIn(marker,HELP)
  self.assertIn('data-scw-workflow-guidance',PHP); self.assertIn('data-scw-project-research-guidance',PHP); self.assertIn('SCWorkspaceWorkflowGuidance',UI)
  self.assertIn('No research questions yet. Frame one explicit question',APP); self.assertIn('No sources in the reading queue. Capture a source',APP); self.assertIn('No research claims yet. Create a claim',APP)
  self.assertIn('/* v0.72.0 — Research Workflow Guidance & Empty-State Refinement */',CSS)
 def test_wordpress_current_assets_and_rest(self):
  self.assertIn('Version: 2.0.1',MAIN); self.assertIn("SC_WORKSPACE_VERSION', '2.0.1",MAIN); self.assertIn("'/workflow-guidance-contract'",PHP); self.assertIn('workflow_guidance_contract',PHP)
  self.assertIn("'sc-workspace-v201'",PHP); self.assertIn('workspace-v2.0.1.js',PHP); self.assertIn('workspace-v2.0.1.css',PHP); self.assertIn('sc-workspace-workflow-guidance-v1.js',PHP); self.assertIn('sc-workspace-workflow-guidance-ui-v1.js',PHP)
 def test_registry_history_docs_schemas(self):
  self.assertEqual((REG['public_version'],REG['previous_version'],REG['release_name']),('0.72.0','0.71.0','Research Workflow Guidance & Empty-State Refinement'))
  self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v201'",REGPHP); self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v201'",REGPHP); self.assertIn('LEGACY_PENDING_KEY_V0710',REGPHP)
  self.assertTrue((R/'history/release-manifest-v0.71.0.json').exists()); self.assertTrue((R/'history/workspace-product-record-v0.71.0.json').exists())
  for f in ['schemas/sc-workspace-workflow-guidance-v1.schema.json','schemas/sc-workspace-empty-state-guidance-v1.schema.json','schemas/sc-workspace-workflow-guidance-report-v1.schema.json','docs/RESEARCH_WORKFLOW_GUIDANCE_EMPTY_STATES_V0720.md']: self.assertTrue((R/f).exists(),f)
if __name__=='__main__': unittest.main()
