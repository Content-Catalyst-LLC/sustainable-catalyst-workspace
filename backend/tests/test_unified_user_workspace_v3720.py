from app.user_workspace import profile

def test_unified_user_workspace_profile():
    item=profile()
    assert item["version"]=="3.72.0"
    assert item["serverAuthoritativeWhenAuthenticated"] is True
    assert item["anonymousLocalFirstSupported"] is True
    assert item["automaticDestructiveMerge"] is False
    assert item["databaseMigrationRequired"] is False
