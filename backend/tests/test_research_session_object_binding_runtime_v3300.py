import pytest
from pydantic import ValidationError
from app.research_session_bindings import (
    profile, ResearchSessionBindingRequest, ResearchSessionBindingReconcileRequest,
    BINDING_RUNTIME_SCHEMA, BINDING_TYPES,
)


def test_v3300_profile_preserves_authority_boundaries():
    item = profile()
    assert item['workspaceVersion'] == '3.3.0'
    assert item['schema'] == BINDING_RUNTIME_SCHEMA
    assert item['backendAuthoritative'] is True
    assert item['referenceFirst'] is True
    assert item['specialistObjectAuthorityPreserved'] is True
    assert item['objectContentReplicatedToCore'] is False
    assert item['durableBindingRegistry'] is True
    assert item['idempotentBindingReplay'] is True
    assert item['explicitReconciliation'] is True
    assert item['automaticMassBinding'] is False
    assert tuple(item['supportedBindingTypes']) == BINDING_TYPES


def test_v3300_binding_request_validation():
    req = ResearchSessionBindingRequest(
        schema='sc-workspace-research-session-binding-request/1.0',
        bindingType='scientific-object', objectKind='dataset', objectId='dataset-1'
    )
    assert req.ensureSession is True
    with pytest.raises(ValidationError):
        ResearchSessionBindingRequest(
            schema='sc-workspace-research-session-binding-request/1.0',
            bindingType='scientific-object', objectId='dataset-1'
        )
    batch = ResearchSessionBindingReconcileRequest(
        schema='sc-workspace-research-session-binding-reconcile-request/1.0', bindings=[req]
    )
    assert batch.stopOnError is False


def test_v3300_health_and_typed_contract():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.client_contracts import profile as client_profile, TYPED_ENDPOINTS
    health = TestClient(app).get('/health').json()
    assert health['version'] == '3.3.0'
    assert health['researchSessionObjectBindingRuntime'] is True
    assert health['researchSessionObjectBindingSchema'] == BINDING_RUNTIME_SCHEMA
    assert health['researchSessionBindingFingerprintPinning'] is True
    assert health['researchSessionBindingIdempotentReplay'] is True
    typed = client_profile(app.openapi())
    assert typed['workspaceVersion'] == '3.3.0'
    assert typed['typedEndpointCount'] == len(TYPED_ENDPOINTS) == 59
    assert typed['typedEndpoints']['researchSessionBindingCreate']['method'] == 'POST'
    assert typed['typedEndpoints']['researchSessionBindingsReconcile']['path'] == '/v1/research-bindings/projects/{project_id}/reconcile'
    assert typed['missingOpenApiOperations'] == []


def test_v3300_binding_routes_are_protected():
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    assert c.get('/v1/research-bindings').status_code in (401, 503)
    assert c.get('/v1/research-bindings/projects/test').status_code in (401, 503)
    assert c.post('/v1/research-bindings/projects/test', json={}).status_code in (401, 422, 503)
    assert c.post('/v1/research-bindings/projects/test/reconcile', json={}).status_code in (401, 422, 503)
