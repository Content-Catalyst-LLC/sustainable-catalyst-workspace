from app.platform_core_runtime import (
    CORE_CONTRACT, profile, PlatformCoreSessionRequest,
    PlatformCoreObjectBindingRequest,
)


def test_platform_core_profile_preserves_authority_boundaries():
    item = profile()
    assert item["workspaceVersion"] == "3.1.0"
    assert item["platformCoreContract"] == CORE_CONTRACT
    assert item["referenceFirst"] is True
    assert item["workspaceOwnsProjectData"] is True
    assert item["workspaceOwnsScientificObjects"] is True
    assert item["workspaceOwnsScientificExecution"] is True
    assert item["coreOwnsUnifiedSessionRegistry"] is True
    assert item["objectContentReplicatedToCore"] is False
    assert item["coreExecutesWorkspaceScientificWork"] is False
    assert item["coreInfersWorkspaceFindings"] is False
    assert item["coreAuthorizesWorkspaceUsers"] is False
    assert item["serviceCredentialBrowserVisible"] is False


def test_v3100_request_contracts_validate_reference_first_inputs():
    session = PlatformCoreSessionRequest(schema="sc-workspace-platform-core-session-request/1.0", projectId="p-1")
    assert session.projectId == "p-1"
    binding = PlatformCoreObjectBindingRequest(
        schema="sc-workspace-platform-core-object-binding-request/1.0",
        projectId="p-1", kind="dataset", objectId="d-1"
    )
    assert binding.kind == "dataset"


def test_health_and_typed_contract_advertise_v3100_platform_core_integration():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    health = TestClient(app).get('/health').json()
    assert health['version'] == '3.1.0'
    assert health['platformCoreV3UnifiedResearchRuntimeIntegration'] is True
    assert health['platformCoreRuntimeContract'] == CORE_CONTRACT
    assert health['platformCoreReferenceFirst'] is True
    assert health['platformCoreObjectContentReplication'] is False
    typed = client_profile(app.openapi())
    assert typed['workspaceVersion'] == '3.1.0'
    assert typed['typedEndpointCount'] == len(TYPED_ENDPOINTS) == 51
    assert typed['typedEndpoints']['platformCoreRuntimeReadiness']['path'] == '/v1/platform-core-runtime/readiness'
    assert typed['typedEndpoints']['platformCoreExecutionBind']['path'] == '/v1/platform-core-runtime/execution-bindings'
    assert typed['missingOpenApiOperations'] == []


def test_platform_core_integration_endpoints_are_protected():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    for path in ('/v1/platform-core-runtime', '/v1/platform-core-runtime/readiness', '/v1/platform-core-runtime/receipts'):
        assert client.get(path).status_code in (401, 503)
