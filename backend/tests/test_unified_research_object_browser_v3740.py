from app.research_object_browser import profile, KINDS

def test_profile():
    item = profile()
    assert item["version"] == "3.74.0"
    assert item["unifiedDiscovery"] is True
    assert item["databaseMigrationRequired"] is False
    assert "project" in KINDS
    assert "notebook" in KINDS
    assert "dataset" in KINDS
