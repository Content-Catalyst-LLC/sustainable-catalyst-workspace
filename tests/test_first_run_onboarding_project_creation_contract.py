import json, re, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.71.0.json').read_text())
REG=json.loads((R/'registry/workspace-product-record-v0.71.0.json').read_text())
MAIN=(R/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.76.0.js').read_text()
HELP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-first-run-onboarding-v1.js').read_text()
CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.76.0.css').read_text()

class FirstRunOnboardingProjectCreationContract(unittest.TestCase):
    def test_release_lineage_and_schema_stability(self):
        self.assertEqual(MAN['version'],'0.71.0')
        self.assertEqual(MAN['previous_version'],'0.70.0')
        self.assertEqual(MAN['release_name'],'First-Run Onboarding & Project Creation')
        self.assertEqual(MAN['storage_schema_version'],35)
        self.assertEqual(MAN['project_schema'],'sc-workspace-project/20.0')
        self.assertEqual(MAN['export_schema'],'sc-workspace-project-export/20.0')
        self.assertFalse(MAN['schema_migration_required'])
    def test_first_run_contract_and_governance(self):
        o=MAN['first_run_onboarding']
        self.assertEqual(o['first_run_detection'],'zero-local-projects')
        self.assertEqual(o['starter_count'],5)
        self.assertEqual(o['starters'],['blank','research-investigation','analytical-assessment','decision-case','publication-preparation'])
        self.assertEqual(o['project_creation'],'explicit-submit')
        self.assertTrue(o['blank_projects_supported'])
        self.assertTrue(o['guest_use_first_class'])
        for k in ['account_required','separate_behavioral_profile','automatic_project_creation','automatic_starter_selection','automatic_upload','automatic_sync','automatic_lifecycle_advance','automatic_ai','schema_migration_required']:
            self.assertFalse(o[k],k)
    def test_wordpress_surface_route_and_current_assets(self):
        self.assertIn("Version: 0.76.0",MAIN)
        self.assertIn("SC_WORKSPACE_VERSION', '0.76.0",MAIN)
        self.assertIn("'/first-run-onboarding-contract'",PHP)
        self.assertIn('first_run_onboarding_contract',PHP)
        self.assertIn('data-scw-first-run',PHP)
        self.assertIn('data-scw-first-run-form',PHP)
        self.assertIn('Create first project',PHP)
        self.assertIn('No account is required',PHP)
        self.assertIn("'sc-workspace-v0760'",PHP)
        self.assertIn('workspace-v0.76.0.js',PHP)
        self.assertIn('workspace-v0.76.0.css',PHP)
        self.assertIn('sc-workspace-first-run-onboarding-v1.js',PHP)
    def test_explicit_creation_path(self):
        self.assertIn('function createFirstRunProject(input)',APP)
        self.assertIn("firstRunForm.addEventListener('submit'",APP)
        self.assertIn('onboarding.creationPlan',APP)
        self.assertIn('projectTemplate(plan.draft.title, plan.draft.description)',APP)
        self.assertIn('startGuidedWorkflow(project, plan.starter.workflow)',APP)
        self.assertIn("persist(`First-run project created explicitly:",APP)
        self.assertNotIn('automaticFirstProjectCreation',APP)
    def test_helper_boundaries(self):
        for marker in ['sc-workspace-first-run-onboarding/1.0','sc-workspace-first-project-draft/1.0','sc-workspace-first-run-onboarding-report/1.0','zero-local-projects','explicit-submit']:
            self.assertIn(marker,HELP)
        for marker in ['automaticProjectCreation:false','automaticStarterSelection:false','automaticUpload:false','automaticSync:false','automaticLifecycleAdvance:false']:
            self.assertIn(marker,HELP)
        self.assertIn('projectTitleIncluded:false',HELP)
        self.assertIn('projectDescriptionIncluded:false',HELP)
    def test_registry_history_docs_and_schemas(self):
        self.assertEqual(REG['public_version'],'0.71.0')
        self.assertEqual(REG['previous_version'],'0.70.0')
        self.assertEqual(REG['release_name'],'First-Run Onboarding & Project Creation')
        self.assertIn('first_run_onboarding',REG)
        self.assertIn("BACKUP_KEY = 'sc_workspace_registry_backup_v0760'",REGPHP)
        self.assertIn("PENDING_KEY = 'sc_workspace_registry_pending_v0760'",REGPHP)
        self.assertIn('LEGACY_PENDING_KEY_V0700',REGPHP)
        self.assertTrue((R/'history/release-manifest-v0.70.0.json').exists())
        self.assertTrue((R/'history/workspace-product-record-v0.70.0.json').exists())
        for f in ['schemas/sc-workspace-first-run-onboarding-v1.schema.json','schemas/sc-workspace-first-project-draft-v1.schema.json','schemas/sc-workspace-first-run-onboarding-report-v1.schema.json','docs/FIRST_RUN_ONBOARDING_PROJECT_CREATION_V0710.md']:
            self.assertTrue((R/f).exists(),f)
        self.assertIn('/* v0.71.0 — First-Run Onboarding & Project Creation */',CSS)

if __name__=='__main__': unittest.main()
