#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

OLD = "3.32.0"
NEW = "3.33.0"
OPS = [
    "workspace.neural.graph-tensor-contract",
    "workspace.neural.graph-dataset-project",
    "workspace.neural.gnn-model-summary",
    "workspace.neural.gnn-forward",
    "workspace.neural.gnn-infer",
]

GNN_CODE = r'''
# v3.33.0 Graph Neural Network Runtime Foundation.
GRAPH_TENSOR_CONTRACT_SCHEMA = "sc-workspace-neural-graph-tensor-contract/1.0"
GRAPH_DATASET_PROJECTION_SCHEMA = "sc-workspace-neural-graph-dataset-projection/1.0"
GNN_MODEL_SPEC_SCHEMA = "sc-workspace-neural-gnn-model-spec/1.0"
GNN_EXECUTION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-execution-artifact/1.0"
GNN_PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-prediction-artifact/1.0"
GNN_ADAPTERS = {"gcn", "graphsage-mean"}
GNN_ACTIVATIONS = {"identity", "relu", "tanh"}
GNN_TASKS = {"node-regression", "node-binary-classification", "node-multiclass-classification"}
MAX_GRAPH_NODES = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GRAPH_NODES", "4096")), 16384))
MAX_GRAPH_EDGES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GRAPH_EDGES", "32768")), 131072))
MAX_GNN_OUTPUT_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_OUTPUT_FEATURES", "1024")), 4096))


def _graph_components(payload: dict[str, Any]) -> tuple[torch.Tensor, list[list[int]], list[str], bool]:
    raw_x = payload.get("nodeFeatures")
    if not isinstance(raw_x, list) or not raw_x or len(raw_x) > MAX_GRAPH_NODES:
        raise HTTPException(status_code=400, detail="nodeFeatures must be a bounded non-empty row matrix")
    if not all(isinstance(r, list) and r for r in raw_x):
        raise HTTPException(status_code=400, detail="nodeFeatures rows must be non-empty arrays")
    width = len(raw_x[0])
    if width < 1 or width > MAX_FEATURES or any(len(r) != width for r in raw_x):
        raise HTTPException(status_code=400, detail="nodeFeatures must be rectangular and within the feature limit")
    if len(raw_x) * width > MAX_TENSOR_ELEMENTS:
        raise HTTPException(status_code=400, detail="graph node feature tensor exceeds element limit")
    try:
        x = torch.tensor(raw_x, dtype=torch.float32, device=_current_device_name())
    except Exception as exc:
        raise HTTPException(status_code=400, detail="nodeFeatures must contain finite numeric values") from exc
    if not torch.isfinite(x).all():
        raise HTTPException(status_code=400, detail="nodeFeatures must contain finite numeric values")
    raw_edges = payload.get("edges")
    if not isinstance(raw_edges, list) or len(raw_edges) > MAX_GRAPH_EDGES:
        raise HTTPException(status_code=400, detail="edges must be a bounded array of [source,target] pairs")
    edges: list[list[int]] = []
    n = len(raw_x)
    for item in raw_edges:
        if not isinstance(item, list) or len(item) != 2 or not all(isinstance(v, int) and not isinstance(v, bool) for v in item):
            raise HTTPException(status_code=400, detail="each edge must be [sourceIndex,targetIndex]")
        s, d = int(item[0]), int(item[1])
        if s < 0 or d < 0 or s >= n or d >= n:
            raise HTTPException(status_code=400, detail="edge index is outside the node range")
        edges.append([s, d])
    raw_ids = payload.get("nodeIds")
    if raw_ids is None:
        node_ids = [str(i) for i in range(n)]
    else:
        if not isinstance(raw_ids, list) or len(raw_ids) != n:
            raise HTTPException(status_code=400, detail="nodeIds must align one-for-one with nodeFeatures")
        node_ids = [str(v)[:256] for v in raw_ids]
        if any(not v for v in node_ids) or len(set(node_ids)) != len(node_ids):
            raise HTTPException(status_code=400, detail="nodeIds must be non-empty and unique")
    return x, edges, node_ids, bool(payload.get("directed", False))


def _graph_fingerprint(node_features: list, edges: list[list[int]], node_ids: list[str], directed: bool) -> str:
    return _canonical_sha256({"nodeFeatures": node_features, "edges": edges, "nodeIds": node_ids, "directed": directed})


def _graph_tensor_contract(payload: dict[str, Any]) -> dict[str, Any]:
    x, edges, node_ids, directed = _graph_components(payload)
    contract = {
        "schema": GRAPH_TENSOR_CONTRACT_SCHEMA,
        "kind": "graph-tensor-contract",
        "nodeCount": int(x.shape[0]),
        "edgeCount": len(edges),
        "featureCount": int(x.shape[1]),
        "directed": directed,
        "nodeIdsFingerprint": _canonical_sha256(node_ids),
        "graphFingerprint": _graph_fingerprint(payload["nodeFeatures"], edges, node_ids, directed),
        "dtype": "float32",
        "device": _current_device_name(),
        "externalGraphReadEnabled": False,
        "arbitraryGraphCodeAllowed": False,
    }
    contract["artifactFingerprint"] = _canonical_sha256(contract)
    return {"graphTensorContract": contract}


def _graph_dataset_project(payload: dict[str, Any]) -> dict[str, Any]:
    ds = payload.get("graphDataset")
    if not isinstance(ds, dict):
        raise HTTPException(status_code=400, detail="graphDataset must be an object")
    nodes, raw_edges = ds.get("nodes"), ds.get("edges")
    if not isinstance(nodes, list) or not nodes or len(nodes) > MAX_GRAPH_NODES:
        raise HTTPException(status_code=400, detail="graphDataset.nodes must be a bounded non-empty array")
    if not isinstance(raw_edges, list) or len(raw_edges) > MAX_GRAPH_EDGES:
        raise HTTPException(status_code=400, detail="graphDataset.edges must be a bounded array")
    ids: list[str] = []
    features: list[list[float]] = []
    for node in nodes:
        if not isinstance(node, dict):
            raise HTTPException(status_code=400, detail="each graph node must be an object")
        nid, feat = str(node.get("id") or "")[:256], node.get("features")
        if not nid or not isinstance(feat, list) or not feat:
            raise HTTPException(status_code=400, detail="each graph node requires id and numeric features")
        ids.append(nid); features.append(feat)
    if len(set(ids)) != len(ids):
        raise HTTPException(status_code=400, detail="graph node ids must be unique")
    idx = {nid: i for i, nid in enumerate(ids)}
    edges: list[list[int]] = []
    for edge in raw_edges:
        if not isinstance(edge, dict):
            raise HTTPException(status_code=400, detail="each graph edge must be an object")
        s, d = str(edge.get("source") or ""), str(edge.get("target") or "")
        if s not in idx or d not in idx:
            raise HTTPException(status_code=400, detail="graph edge references an unknown node id")
        edges.append([idx[s], idx[d]])
    normalized = {"nodeFeatures": features, "edges": edges, "nodeIds": ids, "directed": bool(ds.get("directed", False))}
    x, edges2, ids2, directed = _graph_components(normalized)
    projection = {
        "schema": GRAPH_DATASET_PROJECTION_SCHEMA,
        "kind": "graph-dataset-projection",
        "nodeCount": int(x.shape[0]),
        "edgeCount": len(edges2),
        "featureCount": int(x.shape[1]),
        "directed": directed,
        "nodeIds": ids2,
        "nodeFeatures": features,
        "edges": edges2,
        "sourceFingerprint": str(ds.get("sourceFingerprint") or "")[:128] or None,
        "graphFingerprint": _graph_fingerprint(features, edges2, ids2, directed),
        "projectionPolicy": "explicit-source-nodes-and-edges-only",
        "inferredEdges": False,
        "inferredFeatures": False,
        "isObservedEvidence": False,
    }
    projection["artifactFingerprint"] = _canonical_sha256(projection)
    return {"graphProjectionArtifact": projection}


def _gnn_validate_model_spec(spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict) or spec.get("schema") != GNN_MODEL_SPEC_SCHEMA:
        raise HTTPException(status_code=400, detail=f"modelSpec.schema must be {GNN_MODEL_SPEC_SCHEMA}")
    blocked = sorted(k for k in BLOCKED_PAYLOAD_KEYS if k in spec)
    if blocked:
        raise HTTPException(status_code=400, detail="GNN modelSpec does not accept code, packages, runtime URLs, credentials, or serialized modules")
    adapter = str(spec.get("adapter") or "").lower()
    if adapter not in GNN_ADAPTERS:
        raise HTTPException(status_code=400, detail="unsupported GNN adapter")
    inp, out = spec.get("inputFeatures"), spec.get("outputFeatures")
    if not isinstance(inp, int) or isinstance(inp, bool) or inp < 1 or inp > MAX_FEATURES:
        raise HTTPException(status_code=400, detail="inputFeatures is outside the allowed range")
    if not isinstance(out, int) or isinstance(out, bool) or out < 1 or out > MAX_GNN_OUTPUT_FEATURES:
        raise HTTPException(status_code=400, detail="outputFeatures is outside the allowed range")
    activation = str(spec.get("activation") or "identity").lower()
    if activation not in GNN_ACTIVATIONS:
        raise HTTPException(status_code=400, detail="unsupported GNN activation")
    rows = inp if adapter == "gcn" else inp * 2
    weights, bias = spec.get("weights"), spec.get("bias", [0.0] * out)
    if not isinstance(weights, list) or len(weights) != rows or not all(isinstance(r, list) and len(r) == out for r in weights):
        raise HTTPException(status_code=400, detail=f"weights must have shape [{rows},{out}] for adapter {adapter}")
    if not isinstance(bias, list) or len(bias) != out:
        raise HTTPException(status_code=400, detail=f"bias must contain {out} values")
    try:
        w = torch.tensor(weights, dtype=torch.float32, device=_current_device_name())
        b = torch.tensor(bias, dtype=torch.float32, device=_current_device_name())
    except Exception as exc:
        raise HTTPException(status_code=400, detail="GNN weights and bias must be numeric") from exc
    if not torch.isfinite(w).all() or not torch.isfinite(b).all():
        raise HTTPException(status_code=400, detail="GNN weights and bias must be finite")
    normalized = {
        "schema": GNN_MODEL_SPEC_SCHEMA,
        "adapter": adapter,
        "inputFeatures": inp,
        "outputFeatures": out,
        "activation": activation,
        "weights": weights,
        "bias": bias,
        "addSelfLoops": bool(spec.get("addSelfLoops", True)),
    }
    normalized["modelSpecFingerprint"] = _canonical_sha256(normalized)
    return normalized


def _gnn_model_summary(payload: dict[str, Any]) -> dict[str, Any]:
    spec = _gnn_validate_model_spec(payload.get("modelSpec"))
    rows = spec["inputFeatures"] if spec["adapter"] == "gcn" else spec["inputFeatures"] * 2
    return {
        "kind": "gnn-model-summary",
        "modelSpec": spec,
        "parameterCount": rows * spec["outputFeatures"] + spec["outputFeatures"],
        "trainable": False,
        "executionContract": "bounded-single-layer-message-passing/1.0",
        "serializedModuleAccepted": False,
    }


def _gnn_edge_index(edges: list[list[int]], n: int, directed: bool, add_self_loops: bool) -> tuple[torch.Tensor, torch.Tensor]:
    pairs = [tuple(e) for e in edges]
    if not directed:
        pairs += [(d, s) for s, d in pairs if s != d]
    if add_self_loops:
        pairs += [(i, i) for i in range(n)]
    if not pairs:
        pairs = [(i, i) for i in range(n)]
    src = torch.tensor([p[0] for p in pairs], dtype=torch.long, device=_current_device_name())
    dst = torch.tensor([p[1] for p in pairs], dtype=torch.long, device=_current_device_name())
    return src, dst


def _gnn_activate(y: torch.Tensor, name: str) -> torch.Tensor:
    if name == "relu": return torch.relu(y)
    if name == "tanh": return torch.tanh(y)
    return y


def _gnn_compute(payload: dict[str, Any]) -> tuple[torch.Tensor, dict[str, Any], str, list[str], int, int, bool]:
    x, edges, node_ids, directed = _graph_components(payload)
    spec = _gnn_validate_model_spec(payload.get("modelSpec"))
    if int(x.shape[1]) != spec["inputFeatures"]:
        raise HTTPException(status_code=400, detail="model inputFeatures does not match graph node feature width")
    n = int(x.shape[0])
    src, dst = _gnn_edge_index(edges, n, directed, spec["addSelfLoops"])
    w = torch.tensor(spec["weights"], dtype=torch.float32, device=_current_device_name())
    b = torch.tensor(spec["bias"], dtype=torch.float32, device=_current_device_name())
    if spec["adapter"] == "gcn":
        degree = torch.zeros(n, dtype=torch.float32, device=_current_device_name())
        degree.index_add_(0, dst, torch.ones(dst.numel(), dtype=torch.float32, device=_current_device_name()))
        degree = torch.clamp(degree, min=1.0)
        coeff = torch.rsqrt(degree[src] * degree[dst])
        agg = torch.zeros_like(x)
        agg.index_add_(0, dst, x[src] * coeff.unsqueeze(1))
        y = agg @ w + b
    else:
        agg = torch.zeros_like(x)
        counts = torch.zeros(n, dtype=torch.float32, device=_current_device_name())
        agg.index_add_(0, dst, x[src])
        counts.index_add_(0, dst, torch.ones(dst.numel(), dtype=torch.float32, device=_current_device_name()))
        agg = agg / torch.clamp(counts, min=1.0).unsqueeze(1)
        y = torch.cat([x, agg], dim=1) @ w + b
    y = _gnn_activate(y, spec["activation"])
    return y, spec, _graph_fingerprint(payload["nodeFeatures"], edges, node_ids, directed), node_ids, len(edges), int(x.shape[1]), directed


def _gnn_forward(payload: dict[str, Any]) -> dict[str, Any]:
    y, spec, graph_fp, node_ids, edge_count, feature_count, directed = _gnn_compute(payload)
    values = y.detach().cpu().tolist()
    artifact = {
        "schema": GNN_EXECUTION_ARTIFACT_SCHEMA,
        "kind": "gnn-forward-execution",
        "adapter": spec["adapter"],
        "modelSpecFingerprint": spec["modelSpecFingerprint"],
        "graphFingerprint": graph_fp,
        "nodeCount": len(node_ids),
        "edgeCount": edge_count,
        "inputFeatures": feature_count,
        "outputFeatures": spec["outputFeatures"],
        "directed": directed,
        "nodeIdsFingerprint": _canonical_sha256(node_ids),
        "outputFingerprint": _canonical_sha256(values),
        "device": _current_device_name(),
        "seed": _seed(payload),
        "messagePassingLayers": 1,
        "arbitraryCodeExecution": False,
        "isObservedEvidence": False,
    }
    artifact["artifactFingerprint"] = _canonical_sha256(artifact)
    return {"kind": "gnn-forward", "nodeIds": node_ids, "nodeEmbeddings": values, "gnnExecutionArtifact": artifact}


def _gnn_infer(payload: dict[str, Any]) -> dict[str, Any]:
    task = str(payload.get("task") or "").lower()
    if task not in GNN_TASKS:
        raise HTTPException(status_code=400, detail="unsupported GNN inference task")
    y, spec, graph_fp, node_ids, edge_count, _feature_count, directed = _gnn_compute(payload)
    if task == "node-binary-classification":
        if spec["outputFeatures"] != 1:
            raise HTTPException(status_code=400, detail="binary GNN inference requires outputFeatures=1")
        probs = torch.sigmoid(y[:, 0]).detach().cpu().tolist()
        predictions = [{"nodeId": node_ids[i], "probability": float(probs[i]), "label": int(probs[i] >= 0.5)} for i in range(len(node_ids))]
    elif task == "node-multiclass-classification":
        if spec["outputFeatures"] < 2:
            raise HTTPException(status_code=400, detail="multiclass GNN inference requires outputFeatures>=2")
        probs_t = torch.softmax(y, dim=1)
        probs = probs_t.detach().cpu().tolist()
        predictions = [{"nodeId": node_ids[i], "probabilities": probs[i], "label": int(torch.argmax(probs_t[i]).item())} for i in range(len(node_ids))]
    else:
        raw = y.detach().cpu().tolist()
        predictions = [{"nodeId": node_ids[i], "values": raw[i]} for i in range(len(node_ids))]
    artifact = {
        "schema": GNN_PREDICTION_ARTIFACT_SCHEMA,
        "kind": "gnn-node-prediction",
        "task": task,
        "adapter": spec["adapter"],
        "modelSpecFingerprint": spec["modelSpecFingerprint"],
        "graphFingerprint": graph_fp,
        "predictionFingerprint": _canonical_sha256(predictions),
        "nodeCount": len(node_ids),
        "edgeCount": edge_count,
        "directed": directed,
        "device": _current_device_name(),
        "seed": _seed(payload),
        "targetsAccepted": False,
        "isObservedEvidence": False,
        "predictionPolicy": "model-derived-node-output-not-source-evidence",
    }
    artifact["artifactFingerprint"] = _canonical_sha256(artifact)
    return {"kind": "gnn-inference", "task": task, "predictions": predictions, "gnnPredictionArtifact": artifact}
'''

GNN_ARTIFACT = r'''
    neural_gnn_artifact = None
    neural_gnn_ops = {
        "workspace.neural.graph-dataset-project", "workspace.neural.gnn-forward", "workspace.neural.gnn-infer",
    }
    if language == "neural" and row.operation in neural_gnn_ops and isinstance(result, dict):
        remote_body=result.get("remote") if isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=nr.get("graphProjectionArtifact") if isinstance(nr.get("graphProjectionArtifact"),dict) else None
        if blob is None and isinstance(nr.get("gnnExecutionArtifact"),dict): blob=nr.get("gnnExecutionArtifact")
        if blob is None and isinstance(nr.get("gnnPredictionArtifact"),dict): blob=nr.get("gnnPredictionArtifact")
        if blob:
            raw_blob=json.dumps(blob,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
            schema=blob.get("schema")
            if schema=="sc-workspace-neural-graph-dataset-projection/1.0": media="application/vnd.sc.workspace.neural-graph-projection+json"; prefix="neural-graph-projection"; role="dataset-projection"
            elif schema=="sc-workspace-neural-gnn-prediction-artifact/1.0": media="application/vnd.sc.workspace.neural-gnn-prediction+json"; prefix="neural-gnn-prediction"; role="prediction"
            else: media="application/vnd.sc.workspace.neural-gnn-execution+json"; prefix="neural-gnn-execution"; role="execution"
            aid=f"{prefix}-{row.job_id}"
            existing_gnn=get_artifact(db,row.user_key,aid)
            req=ArtifactStoreRequest.model_validate({
                "schema":"sc-workspace-artifact-store/1.0","artifactId":aid,"projectId":row.project_id or None,
                "filename":f"{prefix}-{row.job_id}.json","mediaType":media,
                "contentBase64":__import__('base64').b64encode(raw_blob).decode("ascii"),
                "expectedRevision":existing_gnn.revision if existing_gnn is not None else 0,
                "metadata":{"kind":blob.get("kind"),"language":"neural","operation":row.operation,"jobId":row.job_id,
                            "runtime":RUNTIME_BY_LANGUAGE[language].runtime,"artifactFingerprint":blob.get("artifactFingerprint"),
                            "graphFingerprint":blob.get("graphFingerprint"),"modelSpecFingerprint":blob.get("modelSpecFingerprint"),
                            "role":role,"isObservedEvidence":False},
            })
            neural_gnn_artifact=store_artifact(db,row.user_key,req)
            nr["workspaceGnnArtifact"]={"artifactId":neural_gnn_artifact.artifact_id,"mediaType":neural_gnn_artifact.media_type,
                                       "sha256":neural_gnn_artifact.sha256,"bytes":neural_gnn_artifact.bytes,
                                       "artifactFingerprint":blob.get("artifactFingerprint")}
'''

GNN_OUTPUT = r'''
        if neural_gnn_artifact is not None:
            gnn_output = ExecutionRunOutputRequest.model_validate({
                "schema":"sc-workspace-execution-run-output/1.0","outputId":"neural-gnn-artifact",
                "artifactId":neural_gnn_artifact.artifact_id,"role":"analysis","label":"Governed graph neural network artifact",
                "mediaType":neural_gnn_artifact.media_type,"sha256":neural_gnn_artifact.sha256,"bytes":neural_gnn_artifact.bytes,
                "metadata":{"language":"neural","operation":row.operation,"governedGnnArtifact":True,"isObservedEvidence":False},
            })
            store_run_output(db,row.user_key,run_id,gnn_output)
'''

GNN_RECEIPT = r'''
    if language == "neural" and row.operation in {
        "workspace.neural.graph-tensor-contract","workspace.neural.graph-dataset-project","workspace.neural.gnn-model-summary",
        "workspace.neural.gnn-forward","workspace.neural.gnn-infer",
    }:
        remote_body=result.get("remote") if isinstance(result,dict) and isinstance(result.get("remote"),dict) else {}
        nr=remote_body.get("result") if isinstance(remote_body.get("result"),dict) else {}
        blob=nr.get("graphTensorContract") if isinstance(nr.get("graphTensorContract"),dict) else {}
        if not blob and isinstance(nr.get("graphProjectionArtifact"),dict): blob=nr.get("graphProjectionArtifact")
        if not blob and isinstance(nr.get("gnnExecutionArtifact"),dict): blob=nr.get("gnnExecutionArtifact")
        if not blob and isinstance(nr.get("gnnPredictionArtifact"),dict): blob=nr.get("gnnPredictionArtifact")
        receipt_details.update({
            "graphNeuralNetworkRuntimeFoundation":True,"gnnArtifactSchema":blob.get("schema"),
            "gnnArtifactFingerprint":blob.get("artifactFingerprint"),"graphFingerprint":blob.get("graphFingerprint"),
            "modelSpecFingerprint":blob.get("modelSpecFingerprint"),"task":blob.get("task"),"adapter":blob.get("adapter"),
            "isObservedEvidence":False,"clientSuppliedGraphRuntimeUrlAllowed":False,
            "workspaceGnnArtifactId":neural_gnn_artifact.artifact_id if neural_gnn_artifact is not None else None,
            "workspaceGnnArtifactSha256":neural_gnn_artifact.sha256 if neural_gnn_artifact is not None else None,
        })
'''

def need(condition: bool, message: str) -> None:
    if not condition: raise SystemExit("ERROR: " + message)

def locate(target: Path):
    if (target / "backend/neural-runtime/service.py").exists(): return target / "backend", target
    if (target / "neural-runtime/service.py").exists() and (target / "app/config.py").exists(): return target, None
    raise SystemExit(f"ERROR: no Workspace backend found under {target}")

def replace_version(path: Path, strict=False):
    if not path.exists():
        if strict: raise SystemExit(f"ERROR: required file missing: {path}")
        return
    text = path.read_text()
    if NEW in text: return
    if OLD not in text:
        if strict: raise SystemExit(f"ERROR: expected {OLD} marker missing: {path}")
        return
    path.write_text(text.replace(OLD, NEW))

def patch_service(path: Path):
    text = path.read_text()
    if 'SERVICE_VERSION = "3.33.0"' in text and 'GRAPH_TENSOR_CONTRACT_SCHEMA' in text: return
    need('SERVICE_VERSION = "3.32.0"' in text, "v3.32.0 neural runtime baseline required")
    need('workspace.neural.certification-report' in text, "v3.32 production certification operations are missing")
    text = text.replace('SERVICE_VERSION = "3.32.0"', 'SERVICE_VERSION = "3.33.0"', 1)
    marker = 'BLOCKED_PAYLOAD_KEYS = {'
    need(marker in text, "neural operation registry marker missing")
    prefix, suffix = text.split(marker, 1)
    close = prefix.rfind('}\n')
    need(close >= 0 and 'OPERATIONS = {' in prefix, "neural OPERATIONS registry could not be located")
    prefix = prefix[:close] + ''.join(f'    "{op}",\n' for op in OPS) + prefix[close:]
    text = prefix + marker + suffix
    health = '''        "graphNeuralNetworkRuntimeFoundation": True,\n        "graphTensorContractSchema": GRAPH_TENSOR_CONTRACT_SCHEMA,\n        "graphDatasetProjectionSchema": GRAPH_DATASET_PROJECTION_SCHEMA,\n        "gnnModelSpecSchema": GNN_MODEL_SPEC_SCHEMA,\n        "gnnExecutionArtifactSchema": GNN_EXECUTION_ARTIFACT_SCHEMA,\n        "gnnPredictionArtifactSchema": GNN_PREDICTION_ARTIFACT_SCHEMA,\n        "gnnAdapters": sorted(GNN_ADAPTERS),\n        "gnnOperations": ["graph-tensor-contract", "graph-dataset-project", "gnn-model-summary", "gnn-forward", "gnn-infer"],\n        "gnnTrainingEnabled": False,\n        "gnnExternalGraphReadEnabled": False,\n'''
    marker = '        "operations": sorted(OPERATIONS),'
    need(marker in text, "neural health operation marker missing")
    text = text.replace(marker, health + marker, 1)
    marker = '\n@app.get("/health")\n'
    need(marker in text, "neural health route marker missing")
    text = text.replace(marker, GNN_CODE + marker, 1)
    marker = '    if operation == "workspace.neural.tensor-summary":\n'
    need(marker in text, "neural dispatch marker missing")
    dispatch = '''    if operation == "workspace.neural.graph-tensor-contract":\n        result = _graph_tensor_contract(payload)\n    elif operation == "workspace.neural.graph-dataset-project":\n        result = _graph_dataset_project(payload)\n    elif operation == "workspace.neural.gnn-model-summary":\n        result = _gnn_model_summary(payload)\n    elif operation == "workspace.neural.gnn-forward":\n        result = _gnn_forward(payload)\n    elif operation == "workspace.neural.gnn-infer":\n        result = _gnn_infer(payload)\n    elif operation == "workspace.neural.tensor-summary":\n'''
    text = text.replace(marker, dispatch, 1)
    marker = '        "result": result,\n'
    need(marker in text, "neural result envelope marker missing")
    meta = '''        "graphNeuralNetworkRuntimeFoundation": True,\n        "gnnModelSpecSchema": GNN_MODEL_SPEC_SCHEMA,\n        "gnnTrainingEnabled": False,\n        "gnnExternalGraphReadEnabled": False,\n'''
    text = text.replace(marker, meta + marker, 1)
    path.write_text(text)

def patch_polyglot(path: Path):
    text = path.read_text()
    if all(op in text for op in OPS) and 'neural_gnn_artifact = None' in text:
        return
    need('workspace.neural.certification-report' in text, "v3.32 neural registry baseline missing")

    # Locate the neural RuntimeSpec structurally. v3.31/v3.32 changed the
    # human-readable runtime description, so matching the old description text
    # ("Hardened PyTorch neural runtime ...") is intentionally avoided.
    start = text.find('RuntimeSpec("neural"')
    need(start >= 0, "neural RuntimeSpec registry entry missing")
    next_spec = text.find('\n    RuntimeSpec("', start + len('RuntimeSpec("neural"'))
    need(next_spec >= 0, "next RuntimeSpec registry entry missing after neural runtime")
    neural_segment = text[start:next_spec]
    tuple_close_rel = neural_segment.find('\n    ),')
    need(tuple_close_rel >= 0, "neural RuntimeSpec operation tuple terminator missing")

    missing_ops = [op for op in OPS if op not in neural_segment]
    if missing_ops:
        insert_at = start + tuple_close_rel + 1
        text = text[:insert_at] + ''.join(f'        "{op}",\n' for op in missing_ops) + text[insert_at:]

    if 'neural_gnn_artifact = None' not in text:
        marker = '    neural_trial_search_artifact = None\n'
        if marker not in text:
            # v3.32 may place certification/remote artifacts adjacent to the
            # historical trial artifact. Fall back to the execution-finalize
            # anchor, which is stable across the Workspace polyglot executor.
            marker = '    finished=datetime.now(timezone.utc)\n'
        need(marker in text, "neural artifact persistence anchor missing")
        text = text.replace(marker, GNN_ARTIFACT + '\n' + marker, 1)

    if 'outputId":"neural-gnn-artifact"' not in text and 'outputId": "neural-gnn-artifact"' not in text:
        marker = '    finished=datetime.now(timezone.utc)\n'
        need(marker in text, "polyglot execution output marker missing")
        text = text.replace(marker, GNN_OUTPUT + '\n' + marker, 1)

    if 'graphNeuralNetworkRuntimeFoundation":True' not in text and 'graphNeuralNetworkRuntimeFoundation": True' not in text:
        marker = '    receipt=PolyglotExecutionReceipt(\n'
        need(marker in text, "polyglot receipt marker missing")
        text = text.replace(marker, GNN_RECEIPT + '\n' + marker, 1)

    path.write_text(text)

def patch_main(path: Path):
    text = path.read_text()
    import re
    text, count = re.subn(r'("neuralRuntimeBoundedOperations"\s*:\s*)\d+', r'\g<1>57', text, count=1)
    need(count == 1 or '"neuralRuntimeBoundedOperations": 57' in text, "Workspace neural operation-count marker missing")
    if '"graphNeuralNetworkRuntimeFoundation": True' not in text:
        marker = '        "neuralRuntimeTrainingEnabled": True,\n'
        need(marker in text, "Workspace neural capability marker missing")
        cap = '''        "graphNeuralNetworkRuntimeFoundation": True,\n        "neuralGraphTensorContractSchema": "sc-workspace-neural-graph-tensor-contract/1.0",\n        "neuralGraphDatasetProjectionSchema": "sc-workspace-neural-graph-dataset-projection/1.0",\n        "neuralGnnModelSpecSchema": "sc-workspace-neural-gnn-model-spec/1.0",\n        "neuralGnnExecutionArtifactSchema": "sc-workspace-neural-gnn-execution-artifact/1.0",\n        "neuralGnnPredictionArtifactSchema": "sc-workspace-neural-gnn-prediction-artifact/1.0",\n        "neuralGnnAdapters": ["gcn", "graphsage-mean"],\n        "neuralGnnTrainingEnabled": False,\n'''
        text = text.replace(marker, cap + marker)
    path.write_text(text)

def patch_plugin(repo: Path | None):
    if repo is None: return
    plugin = repo / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
    klass = repo / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
    replace_version(plugin); replace_version(klass)
    assets = repo / 'wordpress/sustainable-catalyst-workspace/assets'
    pairs = [
        (assets/'css/workspace-v3.32.0.css', assets/'css/workspace-v3.33.0.css'),
        (assets/'js/workspace-v3.32.0.js', assets/'js/workspace-v3.33.0.js'),
        (assets/'js/sc-workspace-typed-client-v33200.js', assets/'js/sc-workspace-typed-client-v33300.js'),
    ]
    for src, dst in pairs:
        if src.exists() and not dst.exists(): dst.write_text(src.read_text().replace(OLD, NEW).replace('v33200', 'v33300'))
    if klass.exists():
        text = klass.read_text().replace('workspace-v3.32.0.css','workspace-v3.33.0.css').replace('workspace-v3.32.0.js','workspace-v3.33.0.js').replace('sc-workspace-typed-client-v33200','sc-workspace-typed-client-v33300')
        klass.write_text(text)
    gen_src = repo/'scripts/generate_typed_client_contracts_v33200.py'
    gen_dst = repo/'scripts/generate_typed_client_contracts_v33300.py'
    if gen_src.exists() and not gen_dst.exists():
        gen_dst.write_text(gen_src.read_text().replace('3.32.0','3.33.0').replace('v33200','v33300').replace('V33200','V33300'))

def copy_payload(payload: Path | None, target: Path, backend: Path, repo: Path | None):
    if payload is None or not payload.is_dir(): return
    if repo is not None:
        for src in sorted(x for x in payload.rglob('*') if x.is_file()):
            rel = src.relative_to(payload); dst = target/rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    else:
        bp = payload/'backend'
        if bp.exists():
            for src in sorted(x for x in bp.rglob('*') if x.is_file()):
                rel = src.relative_to(bp); dst = backend/rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--payload')
    args = ap.parse_args()
    target = Path(args.target).expanduser().resolve()
    need(target.exists(), f"target missing: {target}")
    backend, repo = locate(target)
    patch_service(backend/'neural-runtime/service.py')
    patch_polyglot(backend/'app/polyglot.py')
    patch_main(backend/'app/main.py')
    replace_version(backend/'app/config.py', strict=True)
    replace_version(backend/'app/client_contracts.py')
    patch_plugin(repo)
    copy_payload(Path(args.payload).resolve() if args.payload else None, target, backend, repo)
    print('APPLIED_WORKSPACE_V33300=PASS')
    print(f'WORKSPACE_V33300_BACKEND={backend}')
    print('WORKSPACE_V33300_GNN_OPERATIONS=5')

if __name__ == '__main__': main()
