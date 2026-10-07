from app.shared_research_graph_renderer import renderer_profile

def test_v3821_shared_research_graph_renderer_profile():
    p=renderer_profile()
    assert p["version"]=="3.82.1"
    assert p["forceDirected"] is True
    assert p["semanticClustering"] is True
    assert p["dragAndPin"] is True
    assert p["minimap"] is True
    assert p["curvedDirectedEdges"] is True
    assert p["fullscreen"] is True
    assert p["timelineLayout"] is True
    assert p["provenanceLayout"] is True
    assert p["dataAuthoritySeparatedFromRenderer"] is True
    assert p["databaseMigrationRequired"] is False
    assert p["automaticTruthDetermination"] is False
