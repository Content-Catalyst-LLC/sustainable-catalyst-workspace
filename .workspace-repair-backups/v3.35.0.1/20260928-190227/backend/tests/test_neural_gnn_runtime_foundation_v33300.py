from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sc_workspace_neural_v33300", ROOT / "neural-runtime" / "service.py")
service = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(service)


def graph_payload():
    return {
        "seed": 333,
        "nodeFeatures": [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        "nodeIds": ["a", "b", "c"],
        "edges": [[0, 1], [1, 2]],
        "directed": False,
    }


def gcn_spec(output_features=2):
    weights = [[1.0] * output_features, [0.5] * output_features]
    return {
        "schema": service.GNN_MODEL_SPEC_SCHEMA,
        "adapter": "gcn",
        "inputFeatures": 2,
        "outputFeatures": output_features,
        "activation": "relu",
        "weights": weights,
        "bias": [0.0] * output_features,
        "addSelfLoops": True,
    }


def sage_spec():
    return {
        "schema": service.GNN_MODEL_SPEC_SCHEMA,
        "adapter": "graphsage-mean",
        "inputFeatures": 2,
        "outputFeatures": 1,
        "activation": "identity",
        "weights": [[0.3], [0.2], [0.4], [0.1]],
        "bias": [0.0],
        "addSelfLoops": False,
    }


def test_health_and_registry():
    h = service.health()
    assert h["version"] == "3.33.0"
    assert h["graphNeuralNetworkRuntimeFoundation"] is True
    assert h["gnnAdapters"] == ["gcn", "graphsage-mean"]
    assert h["gnnTrainingEnabled"] is False
    for op in [
        "workspace.neural.graph-tensor-contract",
        "workspace.neural.graph-dataset-project",
        "workspace.neural.gnn-model-summary",
        "workspace.neural.gnn-forward",
        "workspace.neural.gnn-infer",
    ]:
        assert op in h["operations"]


def test_graph_tensor_contract_is_fingerprinted():
    out = service._graph_tensor_contract(graph_payload())["graphTensorContract"]
    assert out["schema"] == service.GRAPH_TENSOR_CONTRACT_SCHEMA
    assert out["nodeCount"] == 3 and out["edgeCount"] == 2 and out["featureCount"] == 2
    assert len(out["graphFingerprint"]) == 64 and len(out["artifactFingerprint"]) == 64


def test_graph_dataset_projection_never_infers_edges():
    out = service._graph_dataset_project({"graphDataset": {
        "sourceFingerprint": "source-123",
        "nodes": [{"id": "a", "features": [1.0, 0.0]}, {"id": "b", "features": [0.0, 1.0]}],
        "edges": [{"source": "a", "target": "b"}],
        "directed": True,
    }})["graphProjectionArtifact"]
    assert out["schema"] == service.GRAPH_DATASET_PROJECTION_SCHEMA
    assert out["nodeIds"] == ["a", "b"]
    assert out["edges"] == [[0, 1]]
    assert out["inferredEdges"] is False and out["inferredFeatures"] is False


def test_gcn_forward_artifact():
    p = graph_payload(); p["modelSpec"] = gcn_spec()
    out = service._gnn_forward(p)
    assert len(out["nodeEmbeddings"]) == 3 and len(out["nodeEmbeddings"][0]) == 2
    art = out["gnnExecutionArtifact"]
    assert art["schema"] == service.GNN_EXECUTION_ARTIFACT_SCHEMA
    assert art["adapter"] == "gcn" and art["messagePassingLayers"] == 1
    assert len(art["artifactFingerprint"]) == 64


def test_graphsage_node_regression():
    p = graph_payload(); p["modelSpec"] = sage_spec(); p["task"] = "node-regression"
    out = service._gnn_infer(p)
    assert out["task"] == "node-regression"
    assert len(out["predictions"]) == 3
    art = out["gnnPredictionArtifact"]
    assert art["schema"] == service.GNN_PREDICTION_ARTIFACT_SCHEMA
    assert art["targetsAccepted"] is False and art["isObservedEvidence"] is False


def test_binary_and_multiclass_contracts():
    p = graph_payload(); p["modelSpec"] = gcn_spec(1); p["task"] = "node-binary-classification"
    out = service._gnn_infer(p)
    assert 0.0 <= out["predictions"][0]["probability"] <= 1.0
    p2 = graph_payload(); p2["modelSpec"] = gcn_spec(3); p2["task"] = "node-multiclass-classification"
    out2 = service._gnn_infer(p2)
    assert len(out2["predictions"][0]["probabilities"]) == 3


def test_invalid_edge_is_rejected():
    p = graph_payload(); p["edges"] = [[0, 99]]
    with pytest.raises(HTTPException): service._graph_tensor_contract(p)


def test_serialized_module_not_accepted_by_gnn_model_spec():
    p = graph_payload(); spec = gcn_spec(); spec["torchModuleBase64"] = "forbidden"; p["modelSpec"] = spec
    with pytest.raises(HTTPException):
        service._gnn_model_summary(p)
