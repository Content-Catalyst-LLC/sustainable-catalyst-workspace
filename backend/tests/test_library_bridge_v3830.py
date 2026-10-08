from app.library_workspace_bridge import profile, reference, handoff_context

def test_profile():
    p=profile(); assert p["version"]=="3.83.0"; assert p["libraryAuthorityPreserved"] is True; assert p["automaticImport"] is False; assert p["databaseMigrationRequired"] is False

def test_reference_boundaries():
    x=reference(library_id="lib:123",kind="publication",canonical_url="https://library.sustainablecatalyst.com/item/123")
    assert x["referenceOnly"] is True and x["contentReplicated"] is False and x["mutationRequested"] is False

def test_handoff_requires_acceptance():
    h=handoff_context(project_id="p1",library_id="lib:123",kind="source")
    assert h["acceptanceRequired"] is True and h["automaticProjectMutation"] is False
