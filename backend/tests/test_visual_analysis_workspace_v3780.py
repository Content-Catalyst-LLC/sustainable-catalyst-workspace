from app.visual_analysis_workspace import profile
def test_v3780_visual_analysis_profile():
    x=profile()
    assert x["version"]=="3.78.0"
    assert x["visualizationAuthority"]=="workspace-visualization-spec-registry"
    assert x["visualResearchAuthority"]=="workspace-visual-research-workspace"
    assert x["linkedViews"] is True
    assert x["sourceProvenancePinning"] is True
    assert x["sceneGraphProjection"] is True
    assert x["linkedViewGraph"] is True
    assert x["browserDefinesAnalyticalMeaning"] is False
    assert x["automaticScientificInterpretation"] is False
    assert x["databaseMigrationRequired"] is False
