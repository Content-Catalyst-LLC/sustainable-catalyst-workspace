from app.backend_native_workspace import profile


def test_backend_native_profile_is_major_v3_boundary():
    item=profile()
    assert item["workspaceVersion"]=="3.0.0"
    assert item["architectureGeneration"]==3
    assert item["backendNative"] is True
    assert item["backendAuthoritative"] is True
    assert item["browserAuthoritativeState"] is False
    assert item["signedInLocalCanonicalFallback"] is False
    assert item["canonicalStore"]=="postgresql"
    assert item["canonicalDomainRuntime"]=="python"
    assert item["scientificExecutionAuthority"]=="bounded-internal-runtime-services"
    assert item["runtimeArbitraryCodeExecution"] is False
    assert item["typedClientTransport"]=="wordpress-server-proxy"
    assert item["rollbackBaseline"]=="2.36.0"


def test_backend_native_profile_preserves_scientific_boundaries():
    item=profile()
    assert item["scientificObjectGenericMutation"] is False
    assert item["handoffGenericDestinationMutation"] is False
    assert item["offlineOutboxAuthoritative"] is False
    assert item["syncAutomaticSemanticMerge"] is False
    assert item["durableProvenanceAndReceipts"] is True
    assert item["reproducibleStudyPackages"] is True
    assert item["rendererNeutralVisualizationSpecifications"] is True


def test_health_and_typed_contract_advertise_backend_native_v3():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    health=TestClient(app).get('/health').json()
    assert health['version']=='3.0.0'
    assert health['backendNativeScientificWorkspace'] is True
    assert health['backendNativeBootstrap'] is True
    assert health['signedInLocalCanonicalFallback'] is False
    typed=client_profile(app.openapi())
    assert typed['workspaceVersion']=='3.0.0'
    assert typed['typedEndpointCount']==len(TYPED_ENDPOINTS)==38
    assert typed['typedEndpoints']['backendNativeWorkspace']['path']=='/v1/backend-native-workspace'
    assert typed['typedEndpoints']['backendNativeBootstrap']['path']=='/v1/backend-native-workspace/bootstrap'
    assert typed['missingOpenApiOperations']==[]


def test_backend_native_endpoints_are_protected():
    from fastapi.testclient import TestClient
    from app.main import app
    client=TestClient(app)
    assert client.get('/v1/backend-native-workspace').status_code in (401,503)
    assert client.get('/v1/backend-native-workspace/bootstrap').status_code in (401,503)
