from fastapi.testclient import TestClient
from app.main import app
from app.production_certification import profile


def test_architecture_certification_profile_is_explicit_and_bounded():
    p = profile()
    assert p["workspaceVersion"] == "3.0.0"
    assert p["architectureCertified"] is True
    assert p["liveProductionCertified"] is False
    assert p["liveFieldChecksRequired"] is True
    assert p["backendAuthoritative"] is True
    assert p["browserAuthoritativeState"] is False
    assert p["browserAuthoritativeAuthorization"] is False
    assert p["runtimeArbitraryCodeExecution"] is False


def test_certification_preserves_backend_native_boundaries():
    p = profile()
    assert p["canonicalStore"] == "postgresql"
    assert p["authorizationDefaultEffect"] == "deny"
    assert p["typedClientTransport"] == "wordpress-server-proxy"
    assert p["browserDirectBackendAccess"] is False
    assert p["canonicalClientCachePersistent"] is False
    assert p["offlineOutboxAuthoritative"] is False
    assert p["scientificObjectGenericMutation"] is False
    assert p["handoffGenericDestinationMutation"] is False


def test_certification_has_no_new_schema_migration():
    p = profile()
    assert p["migrationRequired"] is False
    assert p["migrationLineage"] == "031_backend_policy_identity_authorization_consolidation.sql"
    assert p["rollbackBaseline"] == "2.36.0"
    assert p["rollbackSchemaCompatible"] is True


def test_production_certification_endpoint_is_protected():
    r = TestClient(app).get('/v1/production-certification')
    assert r.status_code in (401, 503)


def test_health_advertises_production_architecture_certification():
    d = TestClient(app).get('/health').json()
    assert d['version'] == '3.0.0'
    assert d['productionArchitectureCertification'] is True
    assert d['architectureCertificationAutomated'] is True
    assert d['liveProductionCertificationAutomatic'] is False
    assert d['releaseMigrationLineage'] == '031_backend_policy_identity_authorization_consolidation.sql'
    assert d['rollbackBaseline'] == '2.36.0'


def test_typed_contract_includes_certification_endpoint():
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    p = client_profile(app.openapi())
    assert p['workspaceVersion'] == '3.0.0'
    assert p['typedEndpointCount'] == len(TYPED_ENDPOINTS) == 38
    assert p['typedEndpoints']['productionCertification']['path'] == '/v1/production-certification'
    assert p['missingOpenApiOperations'] == []
