import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.25.0.js'
CSS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.25.0.css'
SCHEMA=ROOT/'schemas/sc-workspace-personal-knowledge-v1.schema.json'
MANIFEST=ROOT/'release-manifest-v0.25.0.json'

class PersonalKnowledgeContractTests(unittest.TestCase):
    def test_release_boundary(self):
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(m['version'],'0.25.0'); self.assertEqual(m['previous_version'],'0.24.0')
        self.assertEqual(m['storage_schema_version'],24); self.assertEqual(m['project_schema'],'sc-workspace-project/11.0')
        self.assertEqual(m['personal_knowledge_schema'],'sc-workspace-personal-knowledge/1.0')
        self.assertTrue(m['migration']['non_destructive']); self.assertTrue(m['migration']['preserves_existing_objects'])

    def test_schema_limits_and_reference_shape(self):
        s=json.loads(SCHEMA.read_text())
        self.assertEqual(s['properties']['schema']['const'],'sc-workspace-personal-knowledge/1.0')
        self.assertEqual(s['properties']['collections']['maxItems'],30)
        items=s['properties']['collections']['items']['properties']['items']
        self.assertEqual(items['maxItems'],200)
        self.assertEqual(items['items']['required'],['projectId','objectId'])

    def test_workspace_level_view_not_project_subschema(self):
        p=PHP.read_text(); j=JS.read_text()
        self.assertIn('data-scw-workspace-view="projects"',p); self.assertIn('data-scw-workspace-view="knowledge"',p)
        self.assertIn('data-scw-workspace-section="knowledge"',p)
        self.assertNotIn("personalKnowledge: knowledgeTemplate()",j)
        project=json.loads((ROOT/'schemas/sc-workspace-project-v11.schema.json').read_text())
        self.assertNotIn('personalKnowledge',project['properties'])

    def test_derived_index_single_source_of_truth(self):
        j=JS.read_text(); m=json.loads(MANIFEST.read_text())
        self.assertIn('function knowledgeIndex()',j)
        self.assertIn('project.objects.forEach(object =>',j)
        self.assertIn('collections: []',j)
        self.assertFalse(m['governance']['knowledge_index_duplicates_object_content'])
        self.assertTrue(m['knowledge']['derived_index'])

    def test_local_search_fields_and_filters(self):
        p=PHP.read_text(); j=JS.read_text()
        for token in ('data-scw-knowledge-search','data-scw-knowledge-type','data-scw-knowledge-project','data-scw-knowledge-tag','data-scw-knowledge-scope'):
            self.assertIn(token,p)
        for token in ('e.projectTitle','e.object.title','e.object.summary','e.object.content','e.object.tags.join','e.object.provenance?.sourceTitle','e.object.provenance?.sourceUrl'):
            self.assertIn(token,j)

    def test_transparent_related_work(self):
        j=JS.read_text(); p=PHP.read_text(); m=json.loads(MANIFEST.read_text())
        self.assertIn('function relatedKnowledgeEntries',j)
        for reason in ('shared tags:','same source URL','same provenance title'):
            self.assertIn(reason,j)
        self.assertIn('visible deterministic signals',p)
        self.assertFalse(m['governance']['related_work_hidden_scoring'])
        self.assertFalse(m['knowledge']['semantic_embedding_index'])

    def test_collections_hold_refs_and_do_not_delete_objects(self):
        j=JS.read_text(); m=json.loads(MANIFEST.read_text())
        self.assertIn("c.items.push({projectId:e.projectId,objectId:e.objectId})",j)
        self.assertIn("Remove collection",j)
        self.assertNotIn('project.objects=[]',j)
        self.assertFalse(m['knowledge'].get('delete_collection_deletes_objects',False))

    def test_cleanup_on_project_and_object_delete(self):
        j=JS.read_text()
        self.assertIn('cleanKnowledgeProjectReferences(project.id)',j)
        self.assertIn('cleanKnowledgeObjectReferences(project.id, object.id)',j)
        self.assertIn('validObjectKeys',j)

    def test_open_returns_to_canonical_project_object(self):
        j=JS.read_text()
        self.assertIn('state.activeProjectId = project.id',j)
        self.assertIn('project.activeObjectId = entry.objectId',j)
        self.assertIn("setProjectMode('objects')",j)

    def test_privacy_boundary(self):
        m=json.loads(MANIFEST.read_text()); p=PHP.read_text()
        self.assertFalse(m['knowledge']['server_index']); self.assertFalse(m['governance']['semantic_embedding_index'])
        self.assertEqual(m['server_project_storage'],'manual-backup-plus-explicit-sync-head'); self.assertEqual(m['cloud_sync'],'explicit-project-enrollment')
        self.assertIn("'server_index' => false",p); self.assertIn("'external_search_index' => false",p)

    def test_rest_and_public_experience(self):
        p=PHP.read_text(); css=CSS.read_text()
        self.assertIn("'/personal-knowledge-contract'",p); self.assertIn('public function personal_knowledge_contract()',p)
        self.assertIn('PERSONAL KNOWLEDGE ENVIRONMENT',p); self.assertIn('Personal knowledge',p)
        self.assertIn('.scw-personal-knowledge',css); self.assertIn('.scw-knowledge-layout',css)
        self.assertIn("home_url('/knowledge-libraries/')",p)

    def test_migration_from_v011(self):
        j=JS.read_text()
        for token in ("const STORAGE_VERSION = 24","const PROJECT_SCHEMA = 'sc-workspace-project/11.0'",'function migrateV14(raw)','function migrateV15(raw)',"if (raw.schemaVersion === 15) return migrateV15(raw)",'state.knowledge = normalizeKnowledge(raw.knowledge, state.projects)'):
            self.assertIn(token,j)

if __name__=='__main__': unittest.main()
