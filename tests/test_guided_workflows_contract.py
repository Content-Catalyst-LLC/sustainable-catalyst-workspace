import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.38.0.js'
SCHEMA=ROOT/'schemas/sc-workspace-guided-workflows-v1.schema.json'
PROJECT=ROOT/'schemas/sc-workspace-project-v10.schema.json'
MANIFEST=ROOT/'release-manifest-v0.38.0.json'
class GuidedWorkflowContractTests(unittest.TestCase):
    def test_release_boundary(self):
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m['version'],'0.38.0'); self.assertEqual(m['previous_version'],'0.37.0')
        self.assertEqual(m['storage_schema_version'],34); self.assertEqual(m['project_schema'],'sc-workspace-project/19.0')
        self.assertEqual(m['guided_workflows_schema'],'sc-workspace-guided-workflows/1.0')
        self.assertTrue(m['workflow_principles']['blank_projects_supported']); self.assertFalse(m['workflow_principles']['automatic_step_completion'])
    def test_schema_and_project_reference(self):
        s=json.loads(SCHEMA.read_text()); p=json.loads(PROJECT.read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-guided-workflows/1.0')
        self.assertEqual(s['properties']['runs']['maxItems'],20)
        self.assertIn('guidedWorkflows',p['required']); self.assertEqual(p['properties']['guidedWorkflows']['$ref'],'sc-workspace-guided-workflows-v1.schema.json')
    def test_six_visible_templates(self):
        j=JS.read_text()
        for token in ('Research Investigation','Evidence Review','Analytical Assessment','Decision Case','Systems Mapping','Publication Preparation'):
            self.assertIn(token,j)
        self.assertIn('function guidedWorkflowDefinitions()',j)
    def test_guide_mode_and_rest_contract(self):
        p=PHP.read_text()
        self.assertIn('data-scw-project-mode="guide"',p); self.assertIn('data-scw-project-panel="guide"',p)
        self.assertIn("'/guided-workflows-contract'",p); self.assertIn('public function guided_workflows_contract()',p)
    def test_human_control_boundary(self):
        p=PHP.read_text(); j=JS.read_text()
        self.assertIn("'templates_create_hidden_content' => false",p); self.assertIn("'user_controls_step_completion' => true",p)
        self.assertIn('Mark completion yourself; Workspace never interprets activity as approval or completion.',p)
        self.assertIn("WORKFLOW_STEP_STATUS.has(status.value)",j)
        self.assertNotIn('autoCompleteWorkflow',j)
    def test_blank_project_boundary(self):
        p=PHP.read_text(); j=JS.read_text()
        self.assertIn('blank projects remain fully supported',j)
        self.assertIn('projectTemplate(title, description',j)
        self.assertIn('guidedWorkflows: guidedWorkflowsTemplate()',j)
    def test_migration_and_import_compatibility(self):
        j=JS.read_text()
        for token in ("const STORAGE_VERSION = 34","const PROJECT_SCHEMA = 'sc-workspace-project/19.0'","const LEGACY_PROJECT_SCHEMA_V10 = 'sc-workspace-project/10.0'",'function migrateV14(raw)','function migrateV15(raw)',"if (raw.schemaVersion === 15) return migrateV15(raw)","LEGACY_EXPORT_SCHEMA_V9"):
            self.assertIn(token,j)
    def test_duplicate_and_cleanup_refs(self):
        j=JS.read_text()
        self.assertIn('copy.guidedWorkflows.runs = copy.guidedWorkflows.runs.map',j)
        self.assertIn('step.objectIds.map(v=>objectMap.get(v))',j)
        self.assertIn('cleanGuidedWorkflowReferences(project, object.id)',j)
    def test_steps_open_native_modes(self):
        j=JS.read_text()
        self.assertIn("open.textContent='Open workspace'",j)
        self.assertIn('setProjectMode(step.mode)',j)
        self.assertIn("['overview','guide','research','analysis','decision','canvas','traceability','assist','briefing','objects']",j)
    def test_no_new_server_boundary(self):
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m['server_project_storage'],'manual-backup-plus-explicit-sync-head'); self.assertEqual(m['cloud_sync'],'explicit-project-enrollment'); self.assertFalse(m['governance']['templates_generate_findings'])
if __name__=='__main__': unittest.main()
