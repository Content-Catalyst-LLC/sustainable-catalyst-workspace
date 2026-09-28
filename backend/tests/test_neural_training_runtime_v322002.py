from __future__ import annotations
import importlib.util
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "neural-runtime" / "service.py"
DOCKERFILE = ROOT / "neural-runtime" / "Dockerfile"
COMPOSE = ROOT / "docker-compose.example.yml"


def _load_service():
    spec = importlib.util.spec_from_file_location("scw_neural_v322002", SERVICE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hardened_runtime_identity_and_cache_contract():
    svc = _load_service()
    assert svc.SERVICE_VERSION == "3.27.0"
    assert os.environ["HOME"] == "/tmp"
    assert os.environ["USER"] == "scworkspace"
    assert os.environ["LOGNAME"] == "scworkspace"
    assert os.environ["XDG_CACHE_HOME"] == "/tmp/.cache"
    assert os.environ["TORCHINDUCTOR_CACHE_DIR"] == "/tmp/torchinductor"
    h = svc.health()
    assert h["runtimeIdentity"] == "scworkspace"
    assert h["runtimeHome"] == "/tmp"
    assert h["torchInductorCacheDir"] == "/tmp/torchinductor"
    assert h["xdgCacheHome"] == "/tmp/.cache"


def test_container_contract_keeps_numeric_uid_and_writable_tmp_cache():
    d = DOCKERFILE.read_text()
    c = COMPOSE.read_text()
    assert "USER 65532:65532" in d
    assert "TORCHINDUCTOR_CACHE_DIR=/tmp/torchinductor" in d
    assert "XDG_CACHE_HOME=/tmp/.cache" in d
    assert "TORCHINDUCTOR_CACHE_DIR: /tmp/torchinductor" in c
    assert "XDG_CACHE_HOME: /tmp/.cache" in c
    assert "read_only: true" in c
    assert "no-new-privileges:true" in c
    assert "/tmp:rw,noexec,nosuid,size=512m" in c


def test_adam_training_executes_with_pinned_runtime_identity():
    svc = _load_service()
    payload = {
        "seed": 17,
        "features": [[0.0], [1.0], [2.0], [3.0], [4.0], [5.0]],
        "targets": [[1.0], [3.0], [5.0], [7.0], [9.0], [11.0]],
        "trainingSpec": {
            "schema": "sc-workspace-neural-training-spec/1.0",
            "modelType": "linear", "task": "regression",
            "inputFeatures": 1, "outputFeatures": 1,
            "epochs": 30, "batchSize": 3, "shuffle": True,
            "optimizer": {"name": "adam", "learningRate": 0.05, "weightDecay": 0.0},
        },
    }
    r = svc._train(payload, expected_model_type="linear")
    assert r["trainingRun"]["completedEpochs"] == 30
    assert r["trainingRun"]["checkpointCreated"] is True
