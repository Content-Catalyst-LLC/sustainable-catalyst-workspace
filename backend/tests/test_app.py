from fastapi.testclient import TestClient

from app.main import app


def test_health_is_database_independent():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["version"] == "2.34.0"
    assert body["persistence"] == "postgresql"
    assert body["juliaSimulationNumericalRuntime"] is True
    assert body["juliaRuntimeBoundedOperations"] == 8
    assert body["numericalSimulationReceipts"] is True
    assert body["predictiveAnalyticsMachineLearningRuntime"] is True
    assert body["mlRuntimeBoundedOperations"] == 8
    assert body["predictiveModelReceipts"] is True
    assert body["modelEvaluationReceipts"] is True
    assert body["crossRuntimeReproductionVerification"] is True
    assert body["toleranceAwareNumericComparison"] is True
    assert body["crossRuntimeVerificationReceipts"] is True
    assert body["backendDomainAuthority"] is True
    assert body["backendAuthoritativeState"] is True
    assert body["browserAuthoritativeState"] is False
    assert body["serverSideDomainValidation"] is True
    assert body["domainMutationReceipts"] is True


def test_capabilities_require_service_configuration():
    with TestClient(app) as client:
        response = client.get("/v1/capabilities", headers={"Authorization": "Bearer wrong", "X-SC-User-ID": "1"})
    assert response.status_code in (401, 503)
