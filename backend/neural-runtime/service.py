from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from typing import Any

import torch
import torch.nn.functional as F
from fastapi import FastAPI, Header, HTTPException

SERVICE = "Sustainable Catalyst Workspace Neural Runtime"
SERVICE_VERSION = "3.21.0"
RUNTIME = "python-pytorch-neural"
ENGINE = "PyTorch"
TOKEN = os.getenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN", "").strip()
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PAYLOAD_BYTES", str(10 * 1024 * 1024))), 25 * 1024 * 1024))
MAX_TENSOR_ELEMENTS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TENSOR_ELEMENTS", "262144")), 1_000_000))
MAX_BATCH = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_BATCH", "4096")), 16384))
MAX_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_FEATURES", "4096")), 16384))
MAX_LAYERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_LAYERS", "16")), 64))
MAX_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PARAMETERS", "5000000")), 20_000_000))
DEVICE = "cpu"  # v3.21.0 remains CPU-only; accelerator orchestration is a later milestone.

OPERATIONS = {
    "workspace.neural.tensor-summary",
    "workspace.neural.model-summary",
    "workspace.neural.linear-forward",
    "workspace.neural.mlp-forward",
    "workspace.neural.tensor-contract",
    "workspace.neural.dataset-manifest",
    "workspace.neural.batch-plan",
    "workspace.neural.transformation-apply",
}

BLOCKED_PAYLOAD_KEYS = {
    "code", "python", "script", "packages", "requirements", "runtimeUrl", "credentials",
    "pickleBase64", "joblibBase64", "torchModuleBase64", "stateDictBase64", "torchScriptBase64",
    "modulePath", "classPath", "importPath", "checkpointPath", "weightsPath",
}

ALLOWED_DTYPES: dict[str, torch.dtype] = {
    "float32": torch.float32,
    "float64": torch.float64,
    "int64": torch.int64,
    "bool": torch.bool,
}
ALLOWED_ACTIVATIONS = {"identity", "relu", "sigmoid", "tanh", "softmax"}
ALLOWED_TRANSFORMS = {"identity", "cast", "standardize", "minmax", "clip", "select-columns"}
MAX_TRANSFORMS = 16
MAX_FEATURE_NAMES = 4096

app = FastAPI(title=SERVICE, version=SERVICE_VERSION, docs_url=None, redoc_url=None)


def _require_auth(authorization: str | None) -> None:
    if not TOKEN:
        raise HTTPException(status_code=503, detail="Neural runtime service credential is not configured")
    expected = f"Bearer {TOKEN}"
    if not authorization or not hmac.compare_digest(authorization.strip(), expected):
        raise HTTPException(status_code=401, detail="Neural runtime service authentication failed")


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _seed(payload: dict[str, Any]) -> int:
    raw = payload.get("seed", 42)
    try:
        seed = int(raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="seed must be an integer")
    if seed < 0 or seed > 2_147_483_647:
        raise HTTPException(status_code=400, detail="seed is outside the supported range")
    torch.manual_seed(seed)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass
    return seed


def _nested_element_count(value: Any) -> int:
    if isinstance(value, list):
        return sum(_nested_element_count(x) for x in value)
    return 1


def _tensor(value: Any, *, name: str, dtype_name: str = "float32", ndim: int | None = None) -> torch.Tensor:
    if dtype_name not in ALLOWED_DTYPES:
        raise HTTPException(status_code=400, detail=f"{name} dtype is not supported")
    if not isinstance(value, (list, int, float, bool)):
        raise HTTPException(status_code=400, detail=f"{name} must be a scalar or nested array")
    if _nested_element_count(value) > MAX_TENSOR_ELEMENTS:
        raise HTTPException(status_code=413, detail=f"{name} exceeds the bounded tensor element limit")
    try:
        out = torch.tensor(value, dtype=ALLOWED_DTYPES[dtype_name], device=DEVICE)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"{name} is not a rectangular numeric tensor") from exc
    if ndim is not None and out.ndim != ndim:
        raise HTTPException(status_code=400, detail=f"{name} must have rank {ndim}")
    if out.numel() > MAX_TENSOR_ELEMENTS:
        raise HTTPException(status_code=413, detail=f"{name} exceeds the bounded tensor element limit")
    if out.dtype.is_floating_point and not bool(torch.isfinite(out).all()):
        raise HTTPException(status_code=400, detail=f"{name} must contain only finite values")
    return out


def _tensor_json(t: torch.Tensor) -> Any:
    value = t.detach().cpu().tolist()
    return value


def _summary(t: torch.Tensor) -> dict[str, Any]:
    result: dict[str, Any] = {
        "shape": list(t.shape),
        "rank": int(t.ndim),
        "elementCount": int(t.numel()),
        "dtype": str(t.dtype).replace("torch.", ""),
        "device": str(t.device),
    }
    if t.numel() and (t.dtype.is_floating_point or t.dtype in {torch.int64, torch.int32, torch.int16, torch.int8}):
        tf = t.to(torch.float64)
        result.update({
            "min": float(tf.min().item()),
            "max": float(tf.max().item()),
            "mean": float(tf.mean().item()),
        })
    return result


def _activation(x: torch.Tensor, name: str) -> torch.Tensor:
    name = str(name or "identity").strip().lower()
    if name not in ALLOWED_ACTIVATIONS:
        raise HTTPException(status_code=400, detail="activation is not registered")
    if name == "identity":
        return x
    if name == "relu":
        return F.relu(x)
    if name == "sigmoid":
        return torch.sigmoid(x)
    if name == "tanh":
        return torch.tanh(x)
    return torch.softmax(x, dim=-1)


def _linear_spec(spec: dict[str, Any], *, layer_name: str) -> tuple[torch.Tensor, torch.Tensor | None, str, int]:
    if not isinstance(spec, dict):
        raise HTTPException(status_code=400, detail=f"{layer_name} must be an object")
    weights = _tensor(spec.get("weights"), name=f"{layer_name}.weights", ndim=2)
    out_features, in_features = int(weights.shape[0]), int(weights.shape[1])
    if in_features > MAX_FEATURES or out_features > MAX_FEATURES:
        raise HTTPException(status_code=413, detail=f"{layer_name} exceeds the bounded feature limit")
    bias_value = spec.get("bias")
    bias = None
    if bias_value is not None:
        bias = _tensor(bias_value, name=f"{layer_name}.bias", ndim=1)
        if int(bias.shape[0]) != out_features:
            raise HTTPException(status_code=400, detail=f"{layer_name}.bias length must equal output features")
    activation = str(spec.get("activation") or "identity").strip().lower()
    if activation not in ALLOWED_ACTIVATIONS:
        raise HTTPException(status_code=400, detail=f"{layer_name}.activation is not registered")
    parameters = int(weights.numel() + (bias.numel() if bias is not None else 0))
    return weights, bias, activation, parameters


def _validate_model_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict) or spec.get("schema") != "sc-workspace-neural-model-spec/1.0":
        raise HTTPException(status_code=400, detail="modelSpec must use sc-workspace-neural-model-spec/1.0")
    model_type = str(spec.get("modelType") or "").strip().lower()
    if model_type == "linear":
        weights, bias, activation, parameters = _linear_spec(spec, layer_name="modelSpec")
        return {
            "modelType": "linear",
            "inputFeatures": int(weights.shape[1]),
            "outputFeatures": int(weights.shape[0]),
            "layerCount": 1,
            "parameterCount": parameters,
            "activations": [activation],
            "hasBias": bias is not None,
        }
    if model_type == "mlp":
        layers = spec.get("layers")
        if not isinstance(layers, list) or not layers:
            raise HTTPException(status_code=400, detail="MLP modelSpec.layers must be a non-empty array")
        if len(layers) > MAX_LAYERS:
            raise HTTPException(status_code=413, detail="MLP layer count exceeds the bounded limit")
        input_features = None
        output_features = None
        previous_output = None
        parameter_count = 0
        activations: list[str] = []
        has_bias: list[bool] = []
        for index, layer in enumerate(layers):
            weights, bias, activation, parameters = _linear_spec(layer, layer_name=f"modelSpec.layers[{index}]")
            current_in = int(weights.shape[1])
            current_out = int(weights.shape[0])
            if previous_output is not None and current_in != previous_output:
                raise HTTPException(status_code=400, detail=f"MLP layer {index} input features do not match previous output features")
            input_features = current_in if input_features is None else input_features
            output_features = current_out
            previous_output = current_out
            parameter_count += parameters
            activations.append(activation)
            has_bias.append(bias is not None)
        if parameter_count > MAX_PARAMETERS:
            raise HTTPException(status_code=413, detail="model parameter count exceeds the bounded limit")
        return {
            "modelType": "mlp",
            "inputFeatures": input_features,
            "outputFeatures": output_features,
            "layerCount": len(layers),
            "parameterCount": parameter_count,
            "activations": activations,
            "hasBias": has_bias,
        }
    raise HTTPException(status_code=400, detail="modelType is not registered")


def _tensor_summary(payload: dict[str, Any]) -> dict[str, Any]:
    dtype = str(payload.get("dtype") or "float32")
    t = _tensor(payload.get("tensor"), name="tensor", dtype_name=dtype)
    return {
        "kind": "tensor-summary",
        "tensorFingerprint": _canonical_sha256(payload.get("tensor")),
        "summary": _summary(t),
    }


def _model_summary(payload: dict[str, Any]) -> dict[str, Any]:
    spec = payload.get("modelSpec")
    summary = _validate_model_spec(spec)
    return {
        "kind": "neural-model-summary",
        "modelSpecFingerprint": _canonical_sha256(spec),
        "summary": summary,
        "serializedModelAccepted": False,
        "declarativeSpecOnly": True,
    }


def _linear_forward(payload: dict[str, Any]) -> dict[str, Any]:
    inputs = _tensor(payload.get("inputs"), name="inputs", ndim=2)
    if int(inputs.shape[0]) > MAX_BATCH or int(inputs.shape[1]) > MAX_FEATURES:
        raise HTTPException(status_code=413, detail="input batch or feature dimension exceeds the bounded limit")
    spec = payload.get("modelSpec")
    summary = _validate_model_spec(spec)
    if summary["modelType"] != "linear":
        raise HTTPException(status_code=400, detail="linear-forward requires modelType=linear")
    weights, bias, activation, _ = _linear_spec(spec, layer_name="modelSpec")
    if int(inputs.shape[1]) != int(weights.shape[1]):
        raise HTTPException(status_code=400, detail="input feature dimension does not match model weights")
    outputs = _activation(F.linear(inputs, weights, bias), activation)
    return {
        "kind": "neural-inference",
        "modelType": "linear",
        "inputShape": list(inputs.shape),
        "outputShape": list(outputs.shape),
        "modelSpecFingerprint": _canonical_sha256(spec),
        "inputFingerprint": _canonical_sha256(payload.get("inputs")),
        "outputs": _tensor_json(outputs),
    }


def _mlp_forward(payload: dict[str, Any]) -> dict[str, Any]:
    inputs = _tensor(payload.get("inputs"), name="inputs", ndim=2)
    if int(inputs.shape[0]) > MAX_BATCH or int(inputs.shape[1]) > MAX_FEATURES:
        raise HTTPException(status_code=413, detail="input batch or feature dimension exceeds the bounded limit")
    spec = payload.get("modelSpec")
    summary = _validate_model_spec(spec)
    if summary["modelType"] != "mlp":
        raise HTTPException(status_code=400, detail="mlp-forward requires modelType=mlp")
    if int(inputs.shape[1]) != int(summary["inputFeatures"]):
        raise HTTPException(status_code=400, detail="input feature dimension does not match model specification")
    x = inputs
    layer_shapes: list[list[int]] = []
    for index, layer in enumerate(spec["layers"]):
        weights, bias, activation, _ = _linear_spec(layer, layer_name=f"modelSpec.layers[{index}]")
        x = _activation(F.linear(x, weights, bias), activation)
        layer_shapes.append(list(x.shape))
    return {
        "kind": "neural-inference",
        "modelType": "mlp",
        "inputShape": list(inputs.shape),
        "outputShape": list(x.shape),
        "layerOutputShapes": layer_shapes,
        "modelSpecFingerprint": _canonical_sha256(spec),
        "inputFingerprint": _canonical_sha256(payload.get("inputs")),
        "outputs": _tensor_json(x),
    }


def _tensor_contract(payload: dict[str, Any]) -> dict[str, Any]:
    dtype = str(payload.get("dtype") or "float32")
    tensor = _tensor(payload.get("tensor"), name="tensor", dtype_name=dtype)
    logical_name = str(payload.get("logicalName") or "tensor").strip()[:128] or "tensor"
    role = str(payload.get("role") or "features").strip().lower()
    if role not in {"features", "target", "weights", "mask", "embedding", "generic"}:
        raise HTTPException(status_code=400, detail="tensor role is not registered")
    contract = {
        "schema": "sc-workspace-neural-tensor-contract/1.0",
        "logicalName": logical_name,
        "role": role,
        "shape": list(tensor.shape),
        "rank": int(tensor.ndim),
        "elementCount": int(tensor.numel()),
        "dtype": str(tensor.dtype).replace("torch.", ""),
        "device": DEVICE,
        "contiguous": bool(tensor.is_contiguous()),
    }
    return {
        "kind": "neural-tensor-contract",
        "contract": contract,
        "tensorFingerprint": _canonical_sha256({"contract": contract, "values": _tensor_json(tensor)}),
        "values": _tensor_json(tensor),
    }


def _dataset_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    spec = payload.get("datasetSpec")
    if not isinstance(spec, dict) or spec.get("schema") != "sc-workspace-neural-dataset-manifest/1.0":
        raise HTTPException(status_code=400, detail="datasetSpec must use sc-workspace-neural-dataset-manifest/1.0")
    dataset_id = str(spec.get("datasetId") or "").strip()
    source_ref = str(spec.get("sourceDatasetRef") or "").strip()
    split = str(spec.get("split") or "unspecified").strip().lower()
    if not dataset_id or len(dataset_id) > 160:
        raise HTTPException(status_code=400, detail="datasetId is required and bounded")
    if split not in {"train", "validation", "test", "inference", "unspecified"}:
        raise HTTPException(status_code=400, detail="dataset split is not registered")
    features = spec.get("featureNames") or []
    if not isinstance(features, list) or len(features) > MAX_FEATURE_NAMES or any(not isinstance(x, str) or not x.strip() or len(x) > 160 for x in features):
        raise HTTPException(status_code=400, detail="featureNames must be a bounded string array")
    rows = spec.get("rowCount")
    if rows is not None:
        try: rows = int(rows)
        except Exception as exc: raise HTTPException(status_code=400, detail="rowCount must be an integer") from exc
        if rows < 0 or rows > 100_000_000:
            raise HTTPException(status_code=400, detail="rowCount is outside the supported manifest range")
    bindings=spec.get("tensorBindings") or []
    if not isinstance(bindings,list) or len(bindings)>16:
        raise HTTPException(status_code=400, detail="tensorBindings must be a bounded array")
    normalized_bindings=[]
    for i,b in enumerate(bindings):
        if not isinstance(b,dict): raise HTTPException(status_code=400,detail=f"tensorBindings[{i}] must be an object")
        fp=str(b.get("tensorFingerprint") or "").strip()
        role=str(b.get("role") or "generic").strip().lower()
        if not fp or len(fp)>160 or role not in {"features","target","weights","mask","embedding","generic"}:
            raise HTTPException(status_code=400,detail=f"tensorBindings[{i}] is invalid")
        normalized_bindings.append({"logicalName":str(b.get("logicalName") or "tensor").strip()[:128] or "tensor","role":role,"tensorFingerprint":fp})
    normalized = {
        "schema": "sc-workspace-neural-dataset-manifest/1.0",
        "datasetId": dataset_id,
        "sourceDatasetRef": source_ref or None,
        "split": split,
        "rowCount": rows,
        "featureNames": features,
        "targetName": str(spec.get("targetName") or "").strip() or None,
        "contentFingerprint": str(spec.get("contentFingerprint") or "").strip() or None,
        "transformationFingerprint": str(spec.get("transformationFingerprint") or "").strip() or None,
        "tensorBindings": normalized_bindings,
    }
    return {
        "kind": "neural-dataset-manifest",
        "manifest": normalized,
        "manifestFingerprint": _canonical_sha256(normalized),
        "externalDatasetReadPerformed": False,
        "sourceDataEmbedded": False,
    }


def _batch_plan(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        row_count = int(payload.get("rowCount"))
        batch_size = int(payload.get("batchSize"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="rowCount and batchSize must be integers") from exc
    if row_count < 0 or row_count > 10_000_000:
        raise HTTPException(status_code=400, detail="rowCount is outside the bounded range")
    if batch_size < 1 or batch_size > MAX_BATCH:
        raise HTTPException(status_code=400, detail="batchSize is outside the bounded range")
    drop_last = bool(payload.get("dropLast", False))
    shuffle = bool(payload.get("shuffle", False))
    full = row_count // batch_size
    remainder = row_count % batch_size
    batch_count = full + (1 if remainder and not drop_last else 0)
    preview=[]
    preview_cap=min(batch_count, 64)
    seed_value=int(payload.get("seed",42))
    order=None
    if shuffle and row_count:
        generator=torch.Generator(device="cpu"); generator.manual_seed(seed_value)
        order=torch.randperm(row_count,generator=generator).tolist()
    for i in range(preview_cap):
        start=i*batch_size
        stop=min(start+batch_size,row_count)
        if stop-start < batch_size and drop_last: break
        item={"batchIndex":i,"start":start,"stop":stop,"size":stop-start}
        if order is not None: item["rowIndices"]=order[start:stop]
        preview.append(item)
    plan={
        "schema":"sc-workspace-neural-batch-plan/1.0",
        "rowCount":row_count,"batchSize":batch_size,"batchCount":batch_count,
        "dropLast":drop_last,"shuffle":shuffle,"deterministicShuffle":shuffle,"seed":seed_value,
        "remainderRows":remainder,"preview":preview,"previewTruncated":batch_count>len(preview),
    }
    return {"kind":"neural-batch-plan","plan":plan,"planFingerprint":_canonical_sha256(plan)}


def _apply_transform(x: torch.Tensor, spec: dict[str, Any], index: int) -> torch.Tensor:
    if not isinstance(spec, dict):
        raise HTTPException(status_code=400, detail=f"transforms[{index}] must be an object")
    op=str(spec.get("op") or "").strip().lower()
    if op not in ALLOWED_TRANSFORMS:
        raise HTTPException(status_code=400, detail=f"transforms[{index}].op is not registered")
    if op=="identity": return x
    if op=="cast":
        dtype=str(spec.get("dtype") or "")
        if dtype not in ALLOWED_DTYPES: raise HTTPException(status_code=400, detail=f"transforms[{index}].dtype is not supported")
        return x.to(ALLOWED_DTYPES[dtype])
    if op=="clip":
        try: lo=float(spec.get("min")); hi=float(spec.get("max"))
        except Exception as exc: raise HTTPException(status_code=400, detail=f"transforms[{index}] clip bounds must be numeric") from exc
        if not math.isfinite(lo) or not math.isfinite(hi) or lo>hi: raise HTTPException(status_code=400, detail=f"transforms[{index}] clip bounds are invalid")
        return torch.clamp(x,lo,hi)
    if op=="select-columns":
        if x.ndim!=2: raise HTTPException(status_code=400, detail="select-columns requires a rank-2 tensor")
        cols=spec.get("columns")
        if not isinstance(cols,list) or not cols or len(cols)>MAX_FEATURES: raise HTTPException(status_code=400, detail="select-columns requires a bounded columns array")
        try: cols=[int(c) for c in cols]
        except Exception as exc: raise HTTPException(status_code=400, detail="select-columns values must be integers") from exc
        if any(c<0 or c>=x.shape[1] for c in cols): raise HTTPException(status_code=400, detail="select-columns index is out of range")
        return x[:,cols]
    if x.ndim!=2:
        raise HTTPException(status_code=400, detail=f"{op} requires a rank-2 tensor")
    if op=="standardize":
        mean=_tensor(spec.get("mean"),name=f"transforms[{index}].mean",ndim=1).to(x.dtype)
        scale=_tensor(spec.get("scale"),name=f"transforms[{index}].scale",ndim=1).to(x.dtype)
        if mean.numel()!=x.shape[1] or scale.numel()!=x.shape[1] or bool((scale==0).any()):
            raise HTTPException(status_code=400, detail="standardize mean/scale must match feature count and scale must be nonzero")
        return (x-mean)/scale
    if op=="minmax":
        mn=_tensor(spec.get("min"),name=f"transforms[{index}].min",ndim=1).to(x.dtype)
        mx=_tensor(spec.get("max"),name=f"transforms[{index}].max",ndim=1).to(x.dtype)
        if mn.numel()!=x.shape[1] or mx.numel()!=x.shape[1] or bool(((mx-mn)==0).any()):
            raise HTTPException(status_code=400, detail="minmax bounds must match feature count and have nonzero range")
        return (x-mn)/(mx-mn)
    raise HTTPException(status_code=400, detail="transformation is not implemented")


def _transformation_apply(payload: dict[str, Any]) -> dict[str, Any]:
    dtype=str(payload.get("dtype") or "float32")
    x=_tensor(payload.get("tensor"),name="tensor",dtype_name=dtype)
    transforms=payload.get("transforms") or []
    if not isinstance(transforms,list) or len(transforms)>MAX_TRANSFORMS:
        raise HTTPException(status_code=400, detail="transforms must be a bounded array")
    input_summary=_summary(x)
    input_fp=_canonical_sha256({"dtype":dtype,"values":payload.get("tensor")})
    lineage=[]
    for i,spec in enumerate(transforms):
        before=list(x.shape)
        x=_apply_transform(x,spec,i)
        if x.numel()>MAX_TENSOR_ELEMENTS: raise HTTPException(status_code=413, detail="transformed tensor exceeds bounded element limit")
        lineage.append({"index":i,"spec":spec,"specFingerprint":_canonical_sha256(spec),"inputShape":before,"outputShape":list(x.shape)})
    pipeline_fp=_canonical_sha256(transforms)
    output_values=_tensor_json(x)
    return {
        "kind":"neural-transformation-result",
        "inputFingerprint":input_fp,
        "transformationFingerprint":pipeline_fp,
        "outputFingerprint":_canonical_sha256({"pipeline":pipeline_fp,"values":output_values}),
        "inputSummary":input_summary,"outputSummary":_summary(x),
        "lineage":lineage,"values":output_values,
        "sourceDatasetRef":str(payload.get("sourceDatasetRef") or "").strip() or None,
        "sourceTensorFingerprint":str(payload.get("sourceTensorFingerprint") or "").strip() or input_fp,
        "transformationCount":len(transforms),"externalCodeExecuted":False,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": SERVICE,
        "version": SERVICE_VERSION,
        "runtime": RUNTIME,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "devicePolicy": "cpu-only-foundation",
        "tensorDatasetTransformationInterchange": True,
        "tensorContractSchema": "sc-workspace-neural-tensor-contract/1.0",
        "datasetManifestSchema": "sc-workspace-neural-dataset-manifest/1.0",
        "batchPlanSchema": "sc-workspace-neural-batch-plan/1.0",
        "transformationLineage": True,
        "externalDatasetReadEnabled": False,
        "availableDevices": ["cpu"],
        "operations": sorted(OPERATIONS),
        "boundedOperationsOnly": True,
        "arbitraryCodeExecution": False,
        "trainingEnabled": False,
        "clientSuppliedCodeAllowed": False,
        "clientSuppliedPackagesAllowed": False,
        "clientSuppliedRuntimeUrlsAllowed": False,
        "clientSuppliedSerializedModelsAllowed": False,
        "declarativeModelSpecsOnly": True,
        "deterministicSeedControl": True,
        "maxTensorElements": MAX_TENSOR_ELEMENTS,
        "maxBatch": MAX_BATCH,
        "maxFeatures": MAX_FEATURES,
        "maxLayers": MAX_LAYERS,
        "maxParameters": MAX_PARAMETERS,
    }


@app.post("/v1/execute")
def execute(envelope: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    raw = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    if len(raw) > MAX_PAYLOAD:
        raise HTTPException(status_code=413, detail="Neural runtime payload limit exceeded")
    if envelope.get("schema") != "sc-workspace-polyglot-execution-envelope/1.0":
        raise HTTPException(status_code=400, detail="Unsupported polyglot execution envelope")
    if envelope.get("language") != "neural":
        raise HTTPException(status_code=400, detail="Neural runtime only accepts language=neural")
    operation = str(envelope.get("operation") or "")
    if operation not in OPERATIONS:
        raise HTTPException(status_code=400, detail="Neural operation is not registered")
    if envelope.get("arbitraryCodeExecution") is not False:
        raise HTTPException(status_code=400, detail="Arbitrary-code execution must remain disabled")
    payload = envelope.get("payload") or {}
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")
    blocked = sorted(k for k in BLOCKED_PAYLOAD_KEYS if k in payload)
    if blocked:
        raise HTTPException(status_code=400, detail="client-supplied code/packages/runtime credentials/serialized neural models are not accepted")
    seed = _seed(payload)
    if operation == "workspace.neural.tensor-summary":
        result = _tensor_summary(payload)
    elif operation == "workspace.neural.model-summary":
        result = _model_summary(payload)
    elif operation == "workspace.neural.linear-forward":
        result = _linear_forward(payload)
    elif operation == "workspace.neural.mlp-forward":
        result = _mlp_forward(payload)
    elif operation == "workspace.neural.tensor-contract":
        result = _tensor_contract(payload)
    elif operation == "workspace.neural.dataset-manifest":
        result = _dataset_manifest(payload)
    elif operation == "workspace.neural.batch-plan":
        result = _batch_plan(payload)
    else:
        result = _transformation_apply(payload)
    return {
        "ok": True,
        "schema": "sc-workspace-neural-runtime-result/1.0",
        "runtime": RUNTIME,
        "runtimeVersion": SERVICE_VERSION,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "device": DEVICE,
        "seed": seed,
        "operation": operation,
        "boundedOperationsOnly": True,
        "arbitraryCodeExecution": False,
        "trainingEnabled": False,
        "result": result,
    }
