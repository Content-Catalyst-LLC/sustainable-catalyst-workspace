from app.shared_research_graph_runtime import profile, demo_graph

def test_v3820_shared_graph_profile_and_demo():
    p=profile()
    assert p["version"]=="3.82.0"
    assert p["sharedAcrossProducts"] is True
    assert p["dataAuthoritySeparatedFromRenderer"] is True
    assert p["publicDemoProject"] is True
    assert p["databaseMigrationRequired"] is False
    assert p["wordpressRequired"] is False
    g=demo_graph()
    assert g["schema"]=="sc-shared-research-graph/1.0"
    assert g["publicDemo"] is True
    assert g["nodeCount"] >= 8
    assert g["edgeCount"] >= 10
    assert g["interaction"]["selectionInspector"] is True
    assert g["boundaries"]["automaticTruthDetermination"] is False
    evidence=demo_graph("evidence")
    assert evidence["lens"]=="evidence"
    assert evidence["nodeCount"] < g["nodeCount"]
