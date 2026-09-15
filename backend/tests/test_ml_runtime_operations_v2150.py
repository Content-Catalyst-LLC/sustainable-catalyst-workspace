from pathlib import Path
import importlib.util

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "ops-secret"


def _load(monkeypatch):
    monkeypatch.setenv("SC_WORKSPACE_ML_RUNTIME_TOKEN", TOKEN)
    spec = importlib.util.spec_from_file_location("mlsvc_ops", ROOT / "ml-runtime/service.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _post(client, operation, payload):
    env = {
        "schema": "sc-workspace-polyglot-execution-envelope/1.0",
        "workspaceVersion": "2.15.0",
        "jobId": f"job-{operation.rsplit('.', 1)[-1]}",
        "language": "ml",
        "operation": operation,
        "payload": payload,
        "arbitraryCodeExecution": False,
    }
    r = client.post("/v1/execute", json=env, headers={"Authorization": f"Bearer {TOKEN}"})
    assert r.status_code == 200, r.text
    return r.json()["result"]


def test_all_eight_bounded_operations_execute(monkeypatch):
    module = _load(monkeypatch)
    regression_rows = [
        {"x1": float(i), "x2": float(i % 5), "y": 2.5 * i - 0.75 * (i % 5) + 3.0}
        for i in range(1, 41)
    ]
    classification_rows = [
        {"x1": float(i), "x2": float(i % 4), "label": "high" if i >= 21 else "low"}
        for i in range(1, 41)
    ]
    with TestClient(module.app) as client:
        linear = _post(client, "workspace.ml.linear-regression", {
            "rows": regression_rows, "features": ["x1", "x2"], "target": "y", "seed": 17,
        })
        assert linear["metrics"]["r2"] > 0.99

        logistic = _post(client, "workspace.ml.logistic-classification", {
            "rows": classification_rows, "features": ["x1", "x2"], "target": "label", "seed": 17,
            "preprocessing": {"standardize": True},
        })
        assert logistic["metrics"]["accuracy"] >= 0.75

        rf_reg = _post(client, "workspace.ml.random-forest-regression", {
            "rows": regression_rows, "features": ["x1", "x2"], "target": "y", "seed": 17,
            "hyperparameters": {"nEstimators": 20, "maxDepth": 6},
        })
        assert "rmse" in rf_reg["metrics"]

        rf_cls = _post(client, "workspace.ml.random-forest-classification", {
            "rows": classification_rows, "features": ["x1", "x2"], "target": "label", "seed": 17,
            "hyperparameters": {"nEstimators": 20, "maxDepth": 6},
        })
        assert "f1Macro" in rf_cls["metrics"]

        gb_reg = _post(client, "workspace.ml.gradient-boosting-regression", {
            "rows": regression_rows, "features": ["x1", "x2"], "target": "y", "seed": 17,
            "hyperparameters": {"nEstimators": 20, "maxDepth": 2},
        })
        assert "r2" in gb_reg["metrics"]

        gb_cls = _post(client, "workspace.ml.gradient-boosting-classification", {
            "rows": classification_rows, "features": ["x1", "x2"], "target": "label", "seed": 17,
            "hyperparameters": {"nEstimators": 20, "maxDepth": 2},
        })
        assert "accuracy" in gb_cls["metrics"]

        cv = _post(client, "workspace.ml.cross-validate", {
            "rows": regression_rows, "features": ["x1", "x2"], "target": "y", "seed": 17,
            "modelType": "linear-regression", "folds": 4,
        })
        assert cv["folds"] == 4 and len(cv["foldMetrics"]) == 4

        pred = _post(client, "workspace.ml.predict", {
            "rows": [{"x1": 7.0, "x2": 2.0}, {"x1": 19.0, "x2": 4.0}],
            "modelSpec": linear["modelSpec"],
        })
        assert pred["rowCount"] == 2 and len(pred["predictions"]) == 2
