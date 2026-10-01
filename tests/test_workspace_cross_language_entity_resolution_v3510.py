from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def test_release_identity():
    assert 'service_version: str = "3.51.0"' in (ROOT/'backend/app/config.py').read_text()
    p=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); assert 'Version: 3.51.0' in p and "SC_WORKSPACE_VERSION', '3.51.0'" in p
def test_runtime_and_routes():
    r=(ROOT/'backend/app/cross_language_entity_resolution_runtime.py').read_text(); m=(ROOT/'backend/app/main.py').read_text()
    assert 'workspace.linguistics.toponym-candidate-search' in r and 'automaticEntityMergeEnabled' in r
    assert '@app.get("/v1/cross-language-entity-toponym-resolution-workspace")' in m
    assert '@app.post("/v1/cross-language-entity-resolution-runtime/execute")' in m
def test_frontend_contract():
    t=(ROOT/'app/linguistics/workspace-cross-language-entity-toponym-resolution-v3510.js').read_text()
    assert 'sc-workspace-cross-language-entity-toponym-resolution-workspace/1.0' in t
    assert 'automaticEntityMergeEnabled:false' in t and 'wordpressRequired:false' in t
def test_manifest():
    m=json.loads((ROOT/'release-manifest-v3.51.0.json').read_text()); assert m['predecessor']=='3.50.0' and m['databaseMigration'] is False
    b=json.loads((ROOT/'build/workspace-runtime-assets-v3510.json').read_text()); ids={x['id'] for x in b['assets']}; assert 'workspace.linguistics.cross-language-entity-resolution' in ids
