from app.client_contracts import CLIENT_CONTRACT_SCHEMA, REQUEST_SCHEMAS, TYPED_ENDPOINTS, profile
from app.main import app

def test_contract_profile_is_backend_authoritative_and_proxy_only():
    item=profile(app.openapi())
    assert item["schema"]==CLIENT_CONTRACT_SCHEMA and item["workspaceVersion"] in {"2.30.0","2.31.0","2.32.0","2.34.0","2.36.0"}
    assert item["backendAuthoritative"] is True and item["browserAuthoritativeState"] is False
    assert item["transport"]=="wordpress-server-proxy" and item["browserDirectBackendAccess"] is False
    assert item["serviceCredentialsBrowserVisible"] is False and item["strictTypeScript"] is True
    assert item["runtimeEnvelopeChecks"] is True and item["arbitraryCodeExecution"] is False

def test_typed_endpoint_projection_has_no_missing_openapi_operations():
    item=profile(app.openapi())
    assert item["typedEndpointCount"]==len(TYPED_ENDPOINTS) and item["typedEndpointCount"]>=15
    assert item["missingOpenApiOperations"]==[]
    assert len(item["openApiProjectionSha256"])==64

def test_command_and_query_unions_are_bounded():
    item=profile(app.openapi())
    assert item["commandCount"]==9 and item["queryCount"]==9
    assert "project.put" in item["commands"] and "workspace.overview" in item["queries"]

def test_typed_request_schema_catalog_is_explicit():
    assert REQUEST_SCHEMAS["executeCommand"]=="sc-workspace-command-request/1.0"
    assert REQUEST_SCHEMAS["executeQuery"]=="sc-workspace-query-request/1.0"
    assert REQUEST_SCHEMAS["visualizationSpecs"]=="sc-workspace-visualization-spec-request/1.0"

def test_projection_fingerprint_is_deterministic():
    assert profile(app.openapi())["openApiProjectionSha256"]==profile(app.openapi())["openApiProjectionSha256"]
