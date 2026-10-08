from app.shared_research_surface import profile, context

def test_v3823_shared_research_surface_profile():
    p=profile()
    assert p["version"]=="3.82.3"
    assert p["sameRenderer"] is True
    assert p["sameTerrainRuntime"] is True
    assert p["contextPreservingHandoff"] is True
    assert p["publicSurfacePrivateDataAccess"] is False
    assert p["workspaceProjectAuthorityPreserved"] is True
    assert p["databaseMigrationRequired"] is False

def test_v3823_context_is_non_authoritative_navigation_envelope():
    c=context(source="wordpress", object_id="src-1", kind="source", return_url="https://sustainablecatalyst.com/workspace/")
    assert c["schema"]=="sc-shared-research-surface-context/1.0"
    assert c["objectId"]=="src-1"
    assert c["authoritative"] is False
    assert c["mutationRequested"] is False
