from pathlib import Path
import importlib.util

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "neural-secret"


def _load(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN", TOKEN)
    spec = importlib.util.spec_from_file_location("neural_runtime_v32000", ROOT / "neural-runtime" / "service.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _env(operation, payload):
    return {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "3.20.0",
        "jobId": "job-neural-test",
        "language": "neural",
        "operation": operation,
        "payload": payload,
        "arbitraryCodeExecution": False,
    }


def test_neural_health_preserves_foundation_and_reports_training_extension(monkeypatch):
    module = _load(monkeypatch)
    with TestClient(module.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["version"] == "3.26.0"
    assert body["runtime"] == "python-pytorch-neural"
    assert body["devicePolicy"] in {"cpu-only-evaluation-calibration-uncertainty", "cpu-only-neural-explainability", "cpu-only-embedding-representation"}
    assert body["trainingEnabled"] is True
    assert body["checkpointPersistenceEnabled"] is True
    assert body["arbitraryCodeExecution"] is False
    assert body["clientSuppliedSerializedModelsAllowed"] is False
    assert len(body["operations"]) >= 4


def test_linear_forward_uses_declarative_model_spec(monkeypatch):
    module = _load(monkeypatch)
    payload = {
        "seed": 7,
        "inputs": [[1.0, 2.0], [3.0, 4.0]],
        "modelSpec": {
            "schema": "sc-workspace-neural-model-spec/1.0",
            "modelType": "linear",
            "weights": [[2.0, -1.0], [0.5, 0.5]],
            "bias": [1.0, -1.0],
            "activation": "identity",
        },
    }
    with TestClient(module.app) as client:
        response = client.post(
            "/v1/execute",
            json=_env("workspace.neural.linear-forward", payload),
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["seed"] == 7
    assert body["trainingEnabled"] is True
    assert body["checkpointPersistenceEnabled"] is True
    assert body["result"]["outputs"] == [[1.0, 0.5], [3.0, 2.5]]
    assert body["result"]["outputShape"] == [2, 2]


def test_mlp_forward_and_softmax_shape(monkeypatch):
    module = _load(monkeypatch)
    payload = {
        "inputs": [[1.0, 2.0]],
        "modelSpec": {
            "schema": "sc-workspace-neural-model-spec/1.0",
            "modelType": "mlp",
            "layers": [
                {"weights": [[1.0, 0.0], [0.0, 1.0]], "bias": [0.0, 0.0], "activation": "relu"},
                {"weights": [[1.0, -1.0], [-1.0, 1.0]], "bias": [0.0, 0.0], "activation": "softmax"},
            ],
        },
    }
    with TestClient(module.app) as client:
        response = client.post(
            "/v1/execute",
            json=_env("workspace.neural.mlp-forward", payload),
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
    assert response.status_code == 200, response.text
    out = response.json()["result"]["outputs"][0]
    assert len(out) == 2
    assert abs(sum(out) - 1.0) < 1e-6


def test_serialized_modules_and_arbitrary_code_are_rejected(monkeypatch):
    module = _load(monkeypatch)
    with TestClient(module.app) as client:
        response = client.post(
            "/v1/execute",
            json=_env("workspace.neural.model-summary", {"torchModuleBase64": "abc", "modelSpec": {}}),
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
    assert response.status_code == 400


def test_workspace_registers_neural_runtime_and_status_endpoint(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_RUNTIME_NEURAL_URL", "http://sc-workspace-neural-runtime:8101/v1/execute")
    monkeypatch.setenv("SC_WORKSPACE_RUNTIME_NEURAL_TOKEN", "secret")
    from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
    from app.main import app
    from app.polyglot import OPERATION_LANGUAGE, runtime_catalog

    assert OPERATION_LANGUAGE["workspace.neural.linear-forward"] == "neural"
    item = next(x for x in runtime_catalog() if x["language"] == "neural")
    assert item["runtime"] == "python-pytorch-neural"
    assert len(item["operations"]) >= 4
    assert "neuralRuntimeStatus" in TYPED_ENDPOINTS
    assert TYPED_ENDPOINTS["neuralRuntimeStatus"]["path"] == "/v1/polyglot/runtimes/neural/status"
    assert len(TYPED_ENDPOINTS) == 291
    cp = client_profile(app.openapi())
    assert cp["workspaceVersion"] == "3.26.0"
    assert cp["missingOpenApiOperations"] == []


def test_classical_ml_runtime_remains_separate():
    from app.polyglot import RUNTIME_BY_LANGUAGE
    assert RUNTIME_BY_LANGUAGE["ml"].runtime == "python-sklearn-predictive"
    assert RUNTIME_BY_LANGUAGE["neural"].runtime == "python-pytorch-neural"
    assert set(RUNTIME_BY_LANGUAGE["ml"].operations).isdisjoint(set(RUNTIME_BY_LANGUAGE["neural"].operations))
