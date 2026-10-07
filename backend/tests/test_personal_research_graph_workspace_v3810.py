from app.personal_research_graph_workspace import profile

def test_v3810_personal_research_graph_profile():
    x = profile()
    assert x["version"] == "3.81.0"
    assert x["projectOwned"] is True
    assert x["privateByDefault"] is True
    assert x["deterministicGraphProjection"] is True
    assert x["oneGraphMultipleLenses"] is True
    assert x["libraryKnowledgeAutomaticallyInserted"] is False
    assert x["externalKnowledgeRequiresExplicitImport"] is True
    assert x["sourceAuthoritiesPreserved"] is True
    assert x["automaticTruthDetermination"] is False
    assert x["automaticEvidenceRanking"] is False
    assert x["databaseMigrationRequired"] is False
    assert x["wordpressRequired"] is False
