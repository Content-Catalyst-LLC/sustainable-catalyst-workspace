from __future__ import annotations

import importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "neural-runtime" / "service.py"
REQ = ROOT / "neural-runtime" / "requirements.txt"


def _load_service():
    spec = importlib.util.spec_from_file_location("scw_neural_v322001", SERVICE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_repair_dependencies_and_warmup():
    requirements = REQ.read_text()
    assert "torch==2.10.0" in requirements
    assert "numpy==2.2.6" in requirements
    svc = _load_service()
    assert svc.SERVICE_VERSION == "3.27.0"
    assert svc.OPTIMIZER_RUNTIME_WARM is True
    health = svc.health()
    assert health["torchDynamoPreloaded"] is True
    assert health["optimizerRuntimeWarm"] is True
    assert health["optimizerInitializationSerialized"] is True
    assert health["numpyVersion"]


def test_optimizer_construction_from_worker_threads_after_warmup():
    svc = _load_service()
    training_spec = {
        "optimizer": {"name": "adam", "learningRate": 0.01, "weightDecay": 0.0}
    }
    def build(_):
        model = svc.torch.nn.Linear(1, 1)
        opt = svc._optimizer(model, training_spec)
        return opt.__class__.__name__
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(build, range(16)))
    assert results == ["Adam"] * 16


def test_bounded_training_still_executes_after_repair():
    svc = _load_service()
    payload = {
        "seed": 17,
        "features": [[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]],
        "targets": [[1.0], [3.0], [5.0], [7.0], [9.0], [11.0]],
        "trainingSpec": {
            "schema": "sc-workspace-neural-training-spec/1.0",
            "modelType": "linear",
            "task": "regression",
            "inputFeatures": 1,
            "outputFeatures": 1,
            "epochs": 30,
            "batchSize": 3,
            "shuffle": True,
            "optimizer": {"name": "adam", "learningRate": 0.05, "weightDecay": 0.0},
        },
    }
    result = svc._train(payload, expected_model_type="linear")
    run = result["trainingRun"]
    assert run["completedEpochs"] == 30
    assert run["checkpointCreated"] is True
    assert result["trainedModelSpecFingerprint"]
