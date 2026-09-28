from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "v323-checkpoint-token"


def load_runtime(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN", TOKEN)
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_SECONDS", "20")
    path = ROOT / "neural-runtime" / "service.py"
    spec = importlib.util.spec_from_file_location("scw_neural_v32300", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, TestClient(module.app)


def env(operation: str, payload: dict):
    return {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "3.28.0",
        "jobId": "job-v323-checkpoint",
        "language": "neural",
        "operation": operation,
        "payload": payload,
        "arbitraryCodeExecution": False,
    }


def post(client: TestClient, operation: str, payload: dict):
    return client.post(
        "/v1/execute",
        json=env(operation, payload),
        headers={"Authorization": f"Bearer {TOKEN}"},
    )


def spec(epochs: int):
    return {
        "schema": "sc-workspace-neural-training-spec/1.0",
        "modelType": "linear",
        "task": "regression",
        "inputFeatures": 1,
        "outputFeatures": 1,
        "epochs": epochs,
        "batchSize": 3,
        "shuffle": True,
        "optimizer": {"name": "adam", "learningRate": 0.05, "weightDecay": 0.0},
    }


def dataset(training_spec: dict):
    return {
        "seed": 17,
        "features": [[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]],
        "targets": [[1.0], [3.0], [5.0], [7.0], [9.0], [11.0]],
        "trainingSpec": training_spec,
    }


def test_health_enables_portable_checkpoint_resume(monkeypatch):
    _, client = load_runtime(monkeypatch)
    body = client.get("/health").json()
    assert body["version"] == "3.28.0"
    assert len(body["operations"]) >= 14
    assert body["checkpointPersistenceEnabled"] is True
    assert body["resumeTrainingEnabled"] is True
    assert body["checkpointArtifactSchema"] == "sc-workspace-neural-checkpoint-artifact/1.0"
    assert body["checkpointStateSchema"] == "sc-workspace-neural-checkpoint-state/1.0"
    assert body["checkpointFormat"] == "sc-workspace-neural-portable-checkpoint/1.0"
    assert body["checkpointResumePolicy"] == "same-dataset-only"
    assert body["clientSuppliedSerializedModelsAllowed"] is False
    assert body["acceleratorExecutionEnabled"] is False


def test_fresh_training_emits_integrity_checked_checkpoint(monkeypatch):
    _, client = load_runtime(monkeypatch)
    response = post(client, "workspace.neural.train-linear", dataset(spec(5)))
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    checkpoint = result["checkpointArtifact"]
    run = result["trainingRun"]
    assert checkpoint["schema"] == "sc-workspace-neural-checkpoint-artifact/1.0"
    assert checkpoint["checkpointId"].startswith("nck_")
    assert len(checkpoint["artifactFingerprint"]) == 64
    assert checkpoint["parentCheckpointFingerprint"] is None
    assert checkpoint["lineageDepth"] == 0
    assert checkpoint["completedEpochs"] == 5
    assert checkpoint["stateBundleEncoding"] == "zlib+base64+canonical-json-v1"
    assert checkpoint["stateBundleCompressedBytes"] > 0
    assert run["checkpointCreated"] is True
    assert run["checkpointFingerprint"] == checkpoint["artifactFingerprint"]

    inspected = post(client, "workspace.neural.checkpoint-inspect", {"checkpointArtifact": checkpoint})
    assert inspected.status_code == 200, inspected.text
    inspection = inspected.json()["result"]
    assert inspection["stateBundleVerified"] is True
    assert inspection["checkpoint"]["artifactFingerprint"] == checkpoint["artifactFingerprint"]
    assert "stateBundleBase64" not in inspection["checkpoint"]


def test_resume_restores_optimizer_state_and_matches_continuous_training(monkeypatch):
    _, client = load_runtime(monkeypatch)
    first = post(client, "workspace.neural.train-linear", dataset(spec(5)))
    assert first.status_code == 200, first.text
    first_result = first.json()["result"]
    checkpoint = first_result["checkpointArtifact"]

    resume_payload = dataset(spec(3))
    resume_payload["checkpointArtifact"] = checkpoint
    resumed = post(client, "workspace.neural.resume-linear", resume_payload)
    assert resumed.status_code == 200, resumed.text
    resumed_result = resumed.json()["result"]
    resumed_run = resumed_result["trainingRun"]
    child = resumed_result["checkpointArtifact"]

    continuous = post(client, "workspace.neural.train-linear", dataset(spec(8)))
    assert continuous.status_code == 200, continuous.text
    continuous_result = continuous.json()["result"]

    assert resumed_run["resumed"] is True
    assert resumed_run["startingEpoch"] == 5
    assert resumed_run["completedEpochs"] == 3
    assert resumed_run["cumulativeEpochs"] == 8
    assert resumed_run["resumedFromCheckpointFingerprint"] == checkpoint["artifactFingerprint"]
    assert child["parentCheckpointFingerprint"] == checkpoint["artifactFingerprint"]
    assert child["lineageDepth"] == 1
    assert child["completedEpochs"] == 8
    assert resumed_result["trainedModelSpecFingerprint"] == continuous_result["trainedModelSpecFingerprint"]


def test_resume_rejects_dataset_transition_under_v323_policy(monkeypatch):
    _, client = load_runtime(monkeypatch)
    first = post(client, "workspace.neural.train-linear", dataset(spec(3)))
    checkpoint = first.json()["result"]["checkpointArtifact"]
    changed = dataset(spec(2))
    changed["targets"] = [[0.0], [3.0], [5.0], [7.0], [9.0], [11.0]]
    changed["checkpointArtifact"] = checkpoint
    response = post(client, "workspace.neural.resume-linear", changed)
    assert response.status_code == 400
    assert "dataset fingerprint" in response.text


def test_resume_rejects_tampered_checkpoint_and_incompatible_optimizer(monkeypatch):
    _, client = load_runtime(monkeypatch)
    first = post(client, "workspace.neural.train-linear", dataset(spec(3)))
    checkpoint = first.json()["result"]["checkpointArtifact"]

    tampered = deepcopy(checkpoint)
    tampered["completedEpochs"] = 99
    response = post(client, "workspace.neural.checkpoint-inspect", {"checkpointArtifact": tampered})
    assert response.status_code == 400
    assert "fingerprint mismatch" in response.text

    incompatible = dataset(spec(2))
    incompatible["trainingSpec"]["optimizer"] = {"name": "sgd", "learningRate": 0.05, "weightDecay": 0.0}
    incompatible["checkpointArtifact"] = checkpoint
    response = post(client, "workspace.neural.resume-linear", incompatible)
    assert response.status_code == 400
    assert "incompatible" in response.text


def test_raw_checkpoint_paths_and_serialized_state_remain_blocked(monkeypatch):
    _, client = load_runtime(monkeypatch)
    response = post(client, "workspace.neural.resume-linear", {
        **dataset(spec(2)),
        "checkpointPath": "/tmp/model.pt",
    })
    assert response.status_code == 400
    response = post(client, "workspace.neural.resume-linear", {
        **dataset(spec(2)),
        "stateDictBase64": "AAAA",
    })
    assert response.status_code == 400


def test_polyglot_registry_and_workspace_contract_expose_v323_checkpoint_lineage():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE

    neural = RUNTIME_BY_LANGUAGE["neural"]
    assert len(neural.operations) >= 14
    assert "workspace.neural.checkpoint-inspect" in neural.operations
    assert "workspace.neural.resume-linear" in neural.operations
    assert "workspace.neural.resume-mlp" in neural.operations
    contract = profile(app.openapi())
    assert contract["workspaceVersion"] == "3.28.0"
    assert contract["typedEndpointCount"] == 291
    assert contract["missingOpenApiOperations"] == []
