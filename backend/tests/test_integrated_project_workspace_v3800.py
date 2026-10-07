from app.integrated_project_workspace import profile
def test_v3800_integrated_project_profile():
    x=profile()
    assert x["version"]=="3.80.0"
    assert x["projectAuthority"]=="workspace-project-registry"
    assert x["sourceEvidenceIntegrated"] is True
    assert x["datasetsIntegrated"] is True
    assert x["modelsRuntimesIntegrated"] is True
    assert x["visualAnalysisIntegrated"] is True
    assert x["sessionTimelineIntegrated"] is True
    assert x["sourceAuthoritiesPreserved"] is True
    assert x["standaloneFirst"] is True
    assert x["wordpressRequired"] is False
    assert x["genericMutation"] is False
    assert x["databaseMigrationRequired"] is False
