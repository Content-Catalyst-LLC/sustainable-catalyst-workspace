from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "v324-eval-token"


def load_runtime(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN", TOKEN)
    monkeypatch.setenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_SECONDS", "20")
    path = ROOT / "neural-runtime" / "service.py"
    spec = importlib.util.spec_from_file_location("scw_neural_v32400", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, TestClient(module.app)


def env(operation: str, payload: dict):
    return {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "3.24.0",
        "jobId": "job-v324-eval",
        "language": "neural",
        "operation": operation,
        "payload": payload,
        "arbitraryCodeExecution": False,
    }


def post(client: TestClient, operation: str, payload: dict):
    return client.post("/v1/execute", json=env(operation, payload), headers={"Authorization": f"Bearer {TOKEN}"})


def linear_regression_model():
    return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[2.0]],"bias":[1.0],"activation":"identity"}


def binary_model():
    return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[4.0]],"bias":[-2.0],"activation":"identity"}


def multiclass_model():
    return {"schema":"sc-workspace-neural-model-spec/1.0","modelType":"linear","weights":[[-2.0],[0.0],[2.0]],"bias":[1.0,0.0,-1.0],"activation":"identity"}


def test_health_exposes_v324_evaluation_calibration_uncertainty(monkeypatch):
    _, client = load_runtime(monkeypatch)
    body = client.get("/health").json()
    assert body["version"] == "3.27.0"
    assert len(body["operations"]) >= 19
    assert body["evaluationCalibrationUncertaintyEnabled"] is True
    assert body["evaluationArtifactSchema"] == "sc-workspace-neural-evaluation-artifact/1.0"
    assert body["calibrationArtifactSchema"] == "sc-workspace-neural-calibration-artifact/1.0"
    assert body["uncertaintyArtifactSchema"] == "sc-workspace-neural-uncertainty-artifact/1.0"
    assert body["devicePolicy"] in {"cpu-only-evaluation-calibration-uncertainty","cpu-only-neural-explainability","cpu-only-embedding-representation", "cpu-only-inference-prediction-provenance"}
    assert body["acceleratorExecutionEnabled"] is False


def test_regression_evaluation_is_exact_and_fingerprinted(monkeypatch):
    _, client = load_runtime(monkeypatch)
    payload={"modelSpec":linear_regression_model(),"features":[[0.0],[1.0],[2.0],[3.0]],"targets":[[1.0],[3.0],[5.0],[7.0]]}
    r=post(client,"workspace.neural.evaluate-regression",payload)
    assert r.status_code==200,r.text
    x=r.json()["result"]
    assert x["metrics"]["mse"]==0.0 and x["metrics"]["mae"]==0.0 and x["metrics"]["rmse"]==0.0
    assert x["metrics"]["r2"]==1.0
    assert x["analysisArtifact"]["schema"]=="sc-workspace-neural-evaluation-artifact/1.0"
    assert len(x["analysisArtifact"]["artifactFingerprint"])==64
    assert x["analysisArtifact"]["modelSpecFingerprint"]==x["modelSpecFingerprint"]


def test_binary_evaluation_calibration_and_uncertainty(monkeypatch):
    _, client=load_runtime(monkeypatch)
    base={"modelSpec":binary_model(),"features":[[-2.0],[-1.0],[1.0],[2.0]],"targets":[[0.0],[0.0],[1.0],[1.0]]}
    ev=post(client,"workspace.neural.evaluate-binary",base)
    assert ev.status_code==200,ev.text
    metrics=ev.json()["result"]["metrics"]
    assert metrics["accuracy"]==1.0
    assert metrics["rocAuc"]==1.0
    assert metrics["brierScore"] < 0.05
    cal=post(client,"workspace.neural.calibration-report",{**base,"task":"binary-classification","bins":5})
    assert cal.status_code==200,cal.text
    cr=cal.json()["result"]
    assert cr["metrics"]["binCount"]==5 and len(cr["bins"])==5
    assert cr["analysisArtifact"]["schema"]=="sc-workspace-neural-calibration-artifact/1.0"
    uq=post(client,"workspace.neural.uncertainty-summary",{**base,"task":"binary-classification","confidenceThreshold":0.8})
    assert uq.status_code==200,uq.text
    ur=uq.json()["result"]
    assert ur["method"]=="predictive-entropy"
    assert 0 <= ur["summary"]["meanNormalizedEntropy"] <= 1
    assert ur["analysisArtifact"]["schema"]=="sc-workspace-neural-uncertainty-artifact/1.0"


def test_multiclass_evaluation_calibration_and_uncertainty(monkeypatch):
    _, client=load_runtime(monkeypatch)
    base={"modelSpec":multiclass_model(),"features":[[-2.0],[-1.0],[1.0],[2.0]],"targets":[0,0,2,2]}
    ev=post(client,"workspace.neural.evaluate-multiclass",base)
    assert ev.status_code==200,ev.text
    result=ev.json()["result"]
    assert result["metrics"]["accuracy"]==1.0
    assert len(result["metrics"]["confusionMatrix"])==3
    cal=post(client,"workspace.neural.calibration-report",{**base,"task":"multiclass-classification","bins":4})
    assert cal.status_code==200,cal.text
    assert len(cal.json()["result"]["bins"])==4
    uq=post(client,"workspace.neural.uncertainty-summary",{**base,"task":"multiclass-classification"})
    assert uq.status_code==200,uq.text
    assert uq.json()["result"]["summary"]["meanMargin"] > 0


def test_regression_uncertainty_is_explicitly_empirical_residual(monkeypatch):
    _, client=load_runtime(monkeypatch)
    payload={"modelSpec":linear_regression_model(),"features":[[0.0],[1.0],[2.0],[3.0]],"targets":[[1.0],[3.2],[4.8],[7.0]],"task":"regression"}
    r=post(client,"workspace.neural.uncertainty-summary",payload)
    assert r.status_code==200,r.text
    x=r.json()["result"]
    assert x["method"]=="empirical-residual"
    assert x["summary"]["method"]=="empirical-residual"
    assert x["summary"]["residualStd"] > 0


def training_spec(epochs=2):
    return {"schema":"sc-workspace-neural-training-spec/1.0","modelType":"linear","task":"regression","inputFeatures":1,"outputFeatures":1,"epochs":epochs,"batchSize":2,"shuffle":True,"optimizer":{"name":"adam","learningRate":0.05,"weightDecay":0.0}}


def test_evaluation_binds_model_to_checkpoint_lineage(monkeypatch):
    _, client=load_runtime(monkeypatch)
    train_payload={"seed":17,"features":[[0.0],[1.0],[2.0],[3.0]],"targets":[[1.0],[3.0],[5.0],[7.0]],"trainingSpec":training_spec()}
    trained=post(client,"workspace.neural.train-linear",train_payload)
    assert trained.status_code==200,trained.text
    tr=trained.json()["result"]
    payload={"modelSpec":tr["trainedModelSpec"],"checkpointArtifact":tr["checkpointArtifact"],"features":train_payload["features"],"targets":train_payload["targets"]}
    ev=post(client,"workspace.neural.evaluate-regression",payload)
    assert ev.status_code==200,ev.text
    er=ev.json()["result"]
    assert er["checkpointFingerprint"]==tr["checkpointArtifactFingerprint"]
    bad=deepcopy(payload); bad["modelSpec"]=linear_regression_model()
    rejected=post(client,"workspace.neural.evaluate-regression",bad)
    assert rejected.status_code==400
    assert "checkpoint trained model fingerprint" in rejected.text


def test_registry_and_workspace_contract_expose_v324_runtime():
    from app.client_contracts import profile
    from app.main import app
    from app.polyglot import RUNTIME_BY_LANGUAGE
    neural=RUNTIME_BY_LANGUAGE["neural"]
    assert len(neural.operations)>=19
    assert "workspace.neural.evaluate-regression" in neural.operations
    assert "workspace.neural.calibration-report" in neural.operations
    assert "workspace.neural.uncertainty-summary" in neural.operations
    cp=profile(app.openapi())
    assert cp["workspaceVersion"]=="3.27.0"
    assert cp["typedEndpointCount"]==291
    assert cp["missingOpenApiOperations"]==[]
