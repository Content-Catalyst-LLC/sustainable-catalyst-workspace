from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(P/'sustainable-catalyst-workspace.php').read_text();php=(P/'includes/class-sc-workspace.php').read_text();js=(P/'assets/js/workspace-v0.16.0.js').read_text();css=(P/'assets/css/workspace-v0.16.0.css').read_text();reg=(P/'includes/class-sc-workspace-registry.php').read_text()
def check(ok,msg):
    if not ok: raise SystemExit('FAIL - '+msg)
    print('PASS - '+msg)
check('Version: 0.16.0' in main,'plugin version')
check("define('SC_WORKSPACE_VERSION', '0.16.0')" in main,'runtime version')
check("'/knowledge-graph-contract'" in php,'knowledge graph REST contract')
check('WORKSPACE SEARCH &amp; KNOWLEDGE GRAPH' in php,'knowledge graph UI')
check('const STORAGE_VERSION = 17' in js,'storage schema 17')
check("const PROJECT_SCHEMA = 'sc-workspace-project/11.0'" in js,'project schema unchanged')
check("const KNOWLEDGE_GRAPH_SCHEMA = 'sc-workspace-knowledge-graph/1.0'" in js,'knowledge graph schema')
check('function migrateV16(raw)' in js,'v0.15 storage migration')
check('function buildKnowledgeGraph()' in js,'derived graph engine')
check('function graphNeighborhood' in js,'focus neighborhood engine')
check("'same-source'" in js,'deterministic cross-project source relationship')
check('semantic embeddings' in php.lower(),'explicit no-embedding boundary')
check('.scw-knowledge-graph{' in css,'knowledge graph styling')
check("home_url('/knowledge-libraries/')" in php,'canonical Knowledge Library route')
m=json.loads((ROOT/'release-manifest-v0.16.0.json').read_text());check(m['version']=='0.16.0','manifest version');check(m['previous_version']=='0.15.0','previous version');check(m['storage_schema_version']==17,'storage schema');check(m['project_schema']=='sc-workspace-project/11.0','project schema');check(m['knowledge_graph_schema']=='sc-workspace-knowledge-graph/1.0','graph manifest');check(not m['knowledge_graph']['semantic_embeddings'],'no semantic embeddings');check(not m['knowledge_graph']['server_graph_database'],'no server graph database');check(not m['knowledge_graph']['hidden_relationship_inference'],'no hidden relationship inference')
r=json.loads((ROOT/'registry/workspace-product-record-v0.16.0.json').read_text());check(r['public_version']=='0.16.0','registry version');check(r['previous_version']=='0.15.0','registry previous version');json.loads((ROOT/'schemas/sc-workspace-knowledge-graph-v1.schema.json').read_text());check(True,'schema JSON');check('const LEGACY_PENDING_KEY_V0150' in reg,'registry retry lineage')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.16.0 — Workspace Search & Knowledge Graph')
