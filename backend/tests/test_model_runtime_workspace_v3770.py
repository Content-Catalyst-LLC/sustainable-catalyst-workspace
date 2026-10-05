from app.model_runtime_workspace import profile
def test_v3770_model_runtime_profile():
    x=profile()
    assert x["version"]=="3.77.0"
    assert x["modelAuthority"]=="workspace-model-registry"
    assert x["environmentAuthority"]=="workspace-execution-environment-registry"
    assert x["runtimeAdapterAuthority"]=="workspace-runtime-adapter-registry"
    assert x["runtimeCompatibilityChecksAvailable"] is True
    assert x["executionProvenanceVisible"] is True
    assert x["genericMutation"] is False
    assert x["automaticModelSelection"] is False
    assert x["automaticRuntimeSelection"] is False
    assert x["automaticExecution"] is False
    assert x["databaseMigrationRequired"] is False
