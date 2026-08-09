import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.31.0.js';PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php';CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.31.0.css';MANIFEST=ROOT/'release-manifest-v0.31.0.json'
class WorkflowActivityIntelligenceContract(unittest.TestCase):
 def test_manifest(self):
  m=json.loads(MANIFEST.read_text());self.assertEqual(m['version'],'0.31.0');self.assertEqual(m['previous_version'],'0.30.0');self.assertEqual(m['storage_schema_version'],27);self.assertEqual(m['project_schema'],'sc-workspace-project/12.0');self.assertEqual(m['activity_intelligence_schema'],'sc-workspace-activity-intelligence/1.0')
 def test_schema(self):
  s=json.loads((ROOT/'schemas/sc-workspace-activity-intelligence-v1.schema.json').read_text());self.assertEqual(s['properties']['schema']['const'],'sc-workspace-activity-intelligence/1.0')
 def test_storage_migration_only(self):
  j=JS.read_text();self.assertIn('const STORAGE_VERSION = 27',j);self.assertIn('function migrateV17(raw)',j);self.assertIn('if (raw.schemaVersion === 17) return migrateV17(raw)',j);self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/12.0'",j)
 def test_top_level_activity_view(self):
  p=PHP.read_text();self.assertIn('data-scw-workspace-view="activity"',p);self.assertIn('WORKFLOW &amp; ACTIVITY INTELLIGENCE',p)
 def test_next_actions_are_user_controlled(self):
  j=JS.read_text();self.assertIn('MAX_NEXT_ACTIONS = 120',j);self.assertIn('data-scw-next-action-form',PHP.read_text());self.assertIn("status:'open'",j)
 def test_explainable_signals(self):
  j=JS.read_text();self.assertIn('function derivedAttentionSignals',j);self.assertIn("kind:'research'",j);self.assertIn("kind:'analysis'",j);self.assertIn("kind:'decision'",j);self.assertIn("kind:'stale'",j)
 def test_workflow_status(self):
  self.assertIn('function workflowIntelligenceRows',JS.read_text());self.assertIn('Active workflow status',PHP.read_text())
 def test_cross_project_timeline(self):
  j=JS.read_text();self.assertIn('function workspaceActivityTimeline',j);self.assertIn('Recent local changes',PHP.read_text())
 def test_no_surveillance_scoring(self):
  m=json.loads(MANIFEST.read_text());w=m['workflow_activity_intelligence'];self.assertFalse(w['productivity_score']);self.assertFalse(w['time_on_page_tracking']);self.assertFalse(w['server_activity_analytics']);self.assertFalse(w['automatic_completion'])
 def test_contract_endpoint(self): self.assertIn("'/activity-intelligence-contract'",PHP.read_text())
 def test_styles(self): self.assertIn('.scw-activity-intelligence{',CSS.read_text())
 def test_library_route(self): self.assertIn("home_url('/knowledge-libraries/')",PHP.read_text())
if __name__=='__main__': unittest.main()
