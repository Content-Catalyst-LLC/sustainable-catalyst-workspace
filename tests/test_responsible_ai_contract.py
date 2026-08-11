import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.62.0.js'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.62.0.css'
SCHEMA=ROOT/'schemas/sc-workspace-ai-assistance-v1.schema.json'
PROJECT=ROOT/'schemas/sc-workspace-project-v12.schema.json'
MANIFEST=ROOT/'release-manifest-v0.62.0.json'
AI_ADAPTER=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-ai-adapter-v1.js'
class ResponsibleAIContractTests(unittest.TestCase):
  def test_release_boundary(self):
    m=json.loads(MANIFEST.read_text()); self.assertEqual(m['version'],'0.62.0'); self.assertEqual(m['previous_version'],'0.61.0'); self.assertEqual(m['storage_schema_version'],35); self.assertEqual(m['project_schema'],'sc-workspace-project/20.0'); self.assertEqual(m['ai_assistance_schema'],'sc-workspace-ai-assistance/1.0'); self.assertIn('responsible_ai_assistance',m['capabilities'])
  def test_schema_and_limits(self):
    s=json.loads(SCHEMA.read_text()); self.assertEqual(s['properties']['schema']['const'],'sc-workspace-ai-assistance/1.0'); self.assertEqual(s['properties']['sessions']['maxItems'],40); props=s['properties']['sessions']['items']['properties']; self.assertEqual(props['objectIds']['maxItems'],24); self.assertEqual(props['response']['maxLength'],30000)
  def test_project_contains_ai_assistance(self):
    p=json.loads(PROJECT.read_text()); self.assertIn('aiAssistance',p['required']); self.assertEqual(p['properties']['aiAssistance']['$ref'],'sc-workspace-ai-assistance-v1.schema.json')
  def test_explicit_grounding(self):
    j=JS.read_text(); self.assertIn('selectedWorkspaceContextOnly:true',j); self.assertIn('aiSelectedObjects(project,session)',j); self.assertIn('Only these selected Workspace Objects are included',j)
  def test_no_automatic_remote_submission(self):
    p=PHP.read_text(); m=json.loads(MANIFEST.read_text()); self.assertIn("'automatic_remote_send' => false",p); self.assertFalse(m['ai_assistance']['automatic_remote_send']); self.assertFalse(m['governance']['automatic_ai_submission']); self.assertFalse(m['governance']['workspace_configures_server_ai_provider'])
  def test_human_acceptance_boundary(self):
    j=JS.read_text(); p=PHP.read_text(); self.assertIn('data-scw-ai-accept-document',p); self.assertIn("session.status='accepted'",j); self.assertIn("objectTemplate('document'",j); self.assertIn("'ai-assisted','human-accepted'",j)
  def test_ai_output_not_evidence(self):
    p=PHP.read_text(); m=json.loads(MANIFEST.read_text()); self.assertIn('AI output as a draft, not evidence',p); self.assertFalse(m['governance']['ai_output_is_evidence_by_default']); self.assertEqual(m['ai_assistance']['accepted_output_type'],'document')
  def test_decision_and_publication_authority_false(self):
    p=PHP.read_text(); m=json.loads(MANIFEST.read_text()); self.assertIn("'automatic_decision_authority' => false",p); self.assertIn("'automatic_publication' => false",p); self.assertFalse(m['governance']['ai_decision_authority']); self.assertFalse(m['governance']['ai_publication_authority'])
  def test_traceable_acceptance(self):
    j=JS.read_text(); self.assertIn("relation:'derived-from'",j); self.assertIn('AI-assisted draft grounding reference accepted by user',j); self.assertIn('citationObjectIds',j)
  def test_request_exports_and_session_handoff(self):
    j=JS.read_text(); self.assertIn("AI_REQUEST_EXPORT_SCHEMA",j); self.assertIn("AI_RESPONSE_EXPORT_SCHEMA",j); self.assertIn("AI_REQUEST_KEY = 'sc_workspace_ai_request_v1'",j); self.assertIn('writeAiRequestToSession',j)

  def test_same_origin_ai_return_adapter(self):
    j=JS.read_text(); a=AI_ADAPTER.read_text(); m=json.loads(MANIFEST.read_text())
    self.assertIn("const AI_RESPONSE_KEY = 'sc_workspace_ai_response_v1'",j)
    self.assertIn("sc-workspace-ai-response/1.0",a)
    self.assertIn("g.opener.postMessage({type:'sc-workspace-ai-response',packet},g.location.origin)",a)
    self.assertIn("event.origin !== window.location.origin",j)
    self.assertIn("envelope.type === 'sc-workspace-ai-response'",j)
    self.assertEqual(m['ai_assistance']['producer_helper'],'assets/js/sc-workspace-ai-adapter-v1.js')
    self.assertTrue(m['ai_assistance']['same_origin_postmessage_only'])
  def test_adapter_citations_are_limited_to_grounding_set(self):
    a=AI_ADAPTER.read_text(); m=json.loads(MANIFEST.read_text())
    self.assertIn('filter(v=>allowed.has(v))',a)
    self.assertTrue(m['ai_assistance']['citation_object_ids_must_be_selected_grounding_objects'])
    self.assertTrue(m['governance']['ai_response_citations_limited_to_selected_grounding_objects'])
  def test_v10_raw_project_import_compatibility(self):
    j=JS.read_text(); self.assertIn('rawProject.schema !== LEGACY_PROJECT_SCHEMA_V10',j)

  def test_rest_ui_and_css(self):
    p=PHP.read_text(); c=CSS.read_text(); self.assertIn("'/ai-assistance-contract'",p); self.assertIn('public function ai_assistance_contract()',p); self.assertIn('RESPONSIBLE AI ASSISTANCE',p); self.assertIn('data-scw-project-mode="assist"',p); self.assertIn('.scw-ai{',c)
  def test_migration(self):
    j=JS.read_text(); self.assertIn('const STORAGE_VERSION = 35',j); self.assertIn("const PROJECT_SCHEMA = 'sc-workspace-project/20.0'",j); self.assertIn('function migrateV13(raw)',j); self.assertIn('Project upgraded to Responsible AI Assistance',j)
  def test_object_cleanup_and_clone_remap(self):
    j=JS.read_text(); self.assertIn('cleanAiAssistanceReferences(project, object.id)',j); self.assertIn('copy.aiAssistance.sessions=copy.aiAssistance.sessions.map',j); self.assertIn('objectMap.get(v)',j)
  def test_v10_project_export_import_compatibility(self):
    j=JS.read_text(); self.assertIn("const EXPORT_SCHEMA = 'sc-workspace-project-export/20.0'",j); self.assertIn("LEGACY_EXPORT_SCHEMA_V10",j); self.assertIn('payload.schema === LEGACY_EXPORT_SCHEMA_V10',j)
if __name__=='__main__': unittest.main()
