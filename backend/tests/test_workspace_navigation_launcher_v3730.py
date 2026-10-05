from app.workspace_navigation import profile
def test_profile():
    x=profile(); assert x["version"]=="3.73.0"; assert x["globalNavigation"]; assert x["commandPalette"]; assert x["researchLauncher"]
    t={i["id"]:i for i in x["targets"]}; assert t["workspace"]["availability"]=="ready"; assert t["workbench"]["availability"]=="registered"
