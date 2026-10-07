from app.scientific_knowledge_terrain import terrain_profile
def test_v3822_scientific_knowledge_terrain_profile():
    p=terrain_profile()
    assert p["version"]=="3.82.2"
    assert "4d-terrain" in p["modes"]
    assert p["camera"]["orbit"] is True
    assert p["semanticNodePlanes"] is True
    assert p["temporalAxis"] is True
    assert p["objectTypeGeometry"] is True
    assert p["sharedWordPressAndStandaloneRenderer"] is True
    assert p["databaseMigrationRequired"] is False
