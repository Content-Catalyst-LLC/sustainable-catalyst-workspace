#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
def check(ok,msg):
    if not ok: print('FAIL - '+msg); sys.exit(1)
    print('PASS - '+msg)
main=(P/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.12.0' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.12.0')" in main,'runtime version')
php=(P/'includes/class-sc-workspace.php').read_text(); js=(P/'assets/js/workspace-v0.12.0.js').read_text(); css=(P/'assets/css/workspace-v0.12.0.css').read_text(); reg=(P/'includes/class-sc-workspace-registry.php').read_text()
check("'/personal-knowledge-contract'" in php,'Personal Knowledge REST contract'); check('data-scw-workspace-view="knowledge"' in php,'Knowledge workspace view'); check('PERSONAL KNOWLEDGE ENVIRONMENT' in php,'Personal Knowledge interface'); check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
check("const STORAGE_VERSION = 13" in js,'storage schema 13'); check("const PROJECT_SCHEMA = 'sc-workspace-project/10.0'" in js,'project schema remains 10.0'); check("const PERSONAL_KNOWLEDGE_SCHEMA = 'sc-workspace-personal-knowledge/1.0'" in js,'personal knowledge schema'); check('function migrateV12(raw)' in js,'v0.11 storage migration'); check('function knowledgeIndex()' in js,'derived cross-project index'); check('function relatedKnowledgeEntries' in js,'transparent related work'); check('cleanKnowledgeProjectReferences(project.id)' in js,'project reference cleanup'); check('cleanKnowledgeObjectReferences(project.id, object.id)' in js,'object reference cleanup')
check('.scw-personal-knowledge' in css,'knowledge interface styling')
m=json.loads((ROOT/'release-manifest-v0.12.0.json').read_text()); check(m['version']=='0.12.0','manifest version'); check(m['previous_version']=='0.11.0','previous version'); check(m['storage_schema_version']==13,'storage schema'); check(m['project_schema']=='sc-workspace-project/10.0','project schema'); check(m['personal_knowledge_schema']=='sc-workspace-personal-knowledge/1.0','knowledge manifest'); check(m['canonical_library_path']=='/knowledge-libraries/','library route'); check(m['knowledge']['derived_index'],'derived index'); check(not m['knowledge']['server_index'],'no server knowledge index'); check(not m['knowledge']['semantic_embedding_index'],'no semantic embedding index'); check(not m['migration']['rewrites_project_objects'],'project objects are not rewritten')
r=json.loads((ROOT/'registry/workspace-product-record-v0.12.0.json').read_text()); check(r['public_version']=='0.12.0','registry version'); check(r['previous_version']=='0.11.0','registry previous version'); check(r['product_url']=='/platform/','platform route')
json.loads((ROOT/'schemas/sc-workspace-personal-knowledge-v1.schema.json').read_text()); json.loads((ROOT/'schemas/sc-workspace-project-v10.schema.json').read_text()); check(True,'schema JSON')
check("const LEGACY_PENDING_KEY_V0110" in reg,'registry retry lineage')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.12.0 — Personal Knowledge Environment')
