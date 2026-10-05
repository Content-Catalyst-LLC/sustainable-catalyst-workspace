from app.dataset_exploration_workspace import profile

def test_v3760_dataset_exploration_profile():
    x=profile()
    assert x["version"]=="3.76.0"
    assert x["datasetAuthority"]=="workspace-dataset-registry"
    assert x["revisionHistory"] is True
    assert x["schemaInspection"] is True
    assert x["lineageInspection"] is True
    assert x["fingerprintInspection"] is True
    assert x["visualizationHandoffReady"] is True
    assert x["genericMutation"] is False
    assert x["automaticDataTransformation"] is False
    assert x["databaseMigrationRequired"] is False
