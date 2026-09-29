from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import threading
import time
import zlib
from typing import Any
from contextvars import ContextVar

# The runtime deliberately executes as numeric UID 65532 with a read-only root FS.
# PyTorch 2.10 Dynamo/Inductor may otherwise call getpass.getuser() while deriving
# a cache path, which fails when that UID has no passwd entry. Pin all identity and
# compiler/cache locations to the writable /tmp tmpfs before importing torch._dynamo.
os.environ["HOME"] = "/tmp"
os.environ["USER"] = "scworkspace"
os.environ["LOGNAME"] = "scworkspace"
os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"
os.environ["TORCHINDUCTOR_CACHE_DIR"] = "/tmp/torchinductor"

import numpy as np
import torch
# PyTorch 2.10 lazily imports torch._dynamo from optimizer methods.
# Preload it on the single main import thread before FastAPI dispatches
# training work into AnyIO worker threads. This avoids duplicate cache-artifact
# registration observed in hardened production containers on first Adam init.
import torch._dynamo as _torch_dynamo  # noqa: F401
import torch.nn.functional as F
from fastapi import FastAPI, Header, HTTPException

SERVICE = "Sustainable Catalyst Workspace Neural Runtime"
SERVICE_VERSION = "3.39.0"
RUNTIME = "python-pytorch-neural"
ENGINE = "PyTorch"
TOKEN = os.getenv("SC_WORKSPACE_NEURAL_RUNTIME_TOKEN", "").strip()
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PAYLOAD_BYTES", str(10 * 1024 * 1024))), 25 * 1024 * 1024))
MAX_TENSOR_ELEMENTS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TENSOR_ELEMENTS", "262144")), 1_000_000))
MAX_BATCH = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_BATCH", "4096")), 16384))
MAX_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_FEATURES", "4096")), 16384))
MAX_LAYERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_LAYERS", "16")), 64))
MAX_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PARAMETERS", "5000000")), 20_000_000))
DEVICE = "cpu"  # safe process default; requests resolve through governed device orchestration.
DEVICE_PLAN_SCHEMA = "sc-workspace-neural-device-plan/1.0"
DEVICE_INVENTORY_SCHEMA = "sc-workspace-neural-device-inventory/1.0"
ACCELERATOR_ENABLED = os.getenv("SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED", "false").strip().lower() in {"1","true","yes","on"}
MAX_ACCELERATOR_DEVICES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_ACCELERATOR_DEVICES", "1")), 8))
_ALLOWED_DEVICES_RAW = os.getenv("SC_WORKSPACE_NEURAL_ALLOWED_DEVICES", "cpu,cuda:0" if ACCELERATOR_ENABLED else "cpu")
ALLOWED_DEVICES = tuple(dict.fromkeys(x.strip().lower() for x in _ALLOWED_DEVICES_RAW.split(",") if x.strip())) or ("cpu",)
if "cpu" not in ALLOWED_DEVICES:
    ALLOWED_DEVICES = ("cpu",) + ALLOWED_DEVICES
_CURRENT_DEVICE: ContextVar[str] = ContextVar("sc_workspace_neural_device", default="cpu")

OPERATIONS = {
    "workspace.neural.tensor-summary",
    "workspace.neural.model-summary",
    "workspace.neural.linear-forward",
    "workspace.neural.mlp-forward",
    "workspace.neural.tensor-contract",
    "workspace.neural.dataset-manifest",
    "workspace.neural.batch-plan",
    "workspace.neural.transformation-apply",
    "workspace.neural.training-plan",
    "workspace.neural.train-linear",
    "workspace.neural.train-mlp",
    "workspace.neural.checkpoint-inspect",
    "workspace.neural.resume-linear",
    "workspace.neural.resume-mlp",
    "workspace.neural.evaluate-regression",
    "workspace.neural.evaluate-binary",
    "workspace.neural.evaluate-multiclass",
    "workspace.neural.calibration-report",
    "workspace.neural.uncertainty-summary",
    "workspace.neural.explain-gradient",
    "workspace.neural.explain-integrated-gradients",
    "workspace.neural.explain-occlusion",
    "workspace.neural.explain-global-sensitivity",
    "workspace.neural.embedding-generate",
    "workspace.neural.representation-summary",
    "workspace.neural.embedding-similarity",
    "workspace.neural.embedding-neighbors",
    "workspace.neural.infer-regression",
    "workspace.neural.infer-binary",
    "workspace.neural.infer-multiclass",
    "workspace.neural.prediction-inspect",
    "workspace.neural.package-create",
    "workspace.neural.package-verify",
    "workspace.neural.package-inspect",
    "workspace.neural.package-infer",
    "workspace.neural.device-inventory",
    "workspace.neural.device-plan",
    "workspace.neural.device-verify",
    "workspace.neural.accelerator-smoke",
    "workspace.neural.trial-plan",
    "workspace.neural.trial-execute",
    "workspace.neural.batch-execute",
    "workspace.neural.hyperparameter-grid",
    "workspace.neural.hyperparameter-random",
    "workspace.neural.remote-gpu-plan",
    "workspace.neural.remote-gpu-submit",
    "workspace.neural.remote-gpu-status",
    "workspace.neural.remote-gpu-cancel",
    "workspace.neural.certification-plan",
    "workspace.neural.certification-execute",
    "workspace.neural.certification-verify",
    "workspace.neural.certification-report",
    "workspace.neural.graph-tensor-contract",
    "workspace.neural.graph-dataset-project",
    "workspace.neural.gnn-model-summary",
    "workspace.neural.gnn-forward",
    "workspace.neural.gnn-infer",
    "workspace.neural.gnn-split-plan",
    "workspace.neural.gnn-training-plan",
    "workspace.neural.gnn-train",
    "workspace.neural.gnn-checkpoint-create",
    "workspace.neural.gnn-checkpoint-resume",
    "workspace.neural.gnn-evaluate",
    "workspace.neural.gnn-calibration-report",
    "workspace.neural.gnn-explain-gradient",
    "workspace.neural.gnn-explain-occlusion",
    "workspace.neural.gnn-embedding-extract",
    "workspace.neural.gnn-embedding-similarity",
    "workspace.neural.gnn-embedding-neighbors",
    "workspace.neural.vision-tensor-contract",
    "workspace.neural.vision-dataset-project",
    "workspace.neural.vision-model-summary",
    "workspace.neural.vision-forward",
    "workspace.neural.vision-infer",
    "workspace.neural.vision-tile-plan",
    "workspace.neural.remote-sensing-band-project",
    "workspace.neural.remote-sensing-index-compute",
    "workspace.neural.sequence-tensor-contract",
    "workspace.neural.sequence-window-plan",
    "workspace.neural.sequence-dataset-project",
    "workspace.neural.sequence-model-summary",
    "workspace.neural.sequence-forward",
    "workspace.neural.sequence-infer",
    "workspace.neural.sequence-embedding-extract",
    "workspace.neural.sequence-forecast",
    "workspace.neural.multimodal-sample-contract",
    "workspace.neural.multimodal-dataset-project",
    "workspace.neural.multimodal-model-summary",
    "workspace.neural.multimodal-embedding-fuse",
    "workspace.neural.multimodal-representation-extract",
    "workspace.neural.multimodal-forward",
    "workspace.neural.multimodal-infer",
    "workspace.neural.multimodal-similarity",
    "workspace.neural.neural-symbolic-symbol-contract",
    "workspace.neural.neural-symbolic-context-project",
    "workspace.neural.neural-symbolic-bind",
    "workspace.neural.neural-symbolic-rule-contract",
    "workspace.neural.neural-symbolic-constraint-evaluate",
    "workspace.neural.neural-symbolic-relation-score",
    "workspace.neural.neural-symbolic-infer",
    "workspace.neural.neural-symbolic-explain",
}

BLOCKED_PAYLOAD_KEYS = {
    "code", "python", "script", "packages", "requirements", "runtimeUrl", "credentials",
    "pickleBase64", "joblibBase64", "torchModuleBase64", "stateDictBase64", "torchScriptBase64",
    "modulePath", "classPath", "importPath", "checkpointPath", "weightsPath",
    "sequenceUrl", "sequencePath", "dataUrl", "dataPath", "filePath",
    "imageUrl", "imagePath", "modalityUrl", "modalityPath", "encoderUrl", "encoderPath",
    "symbolResolverUrl", "ruleEngineUrl", "ontologyUrl", "knowledgeBaseUrl", "externalSymbolPath",
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
MAX_TRAINING_EPOCHS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_EPOCHS", "200")), 1000))
MAX_TRAINING_ROWS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_ROWS", "8192")), 50000))
MAX_TRAINING_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_PARAMETERS", "250000")), MAX_PARAMETERS))
MAX_TRAINING_SECONDS = max(1.0, min(float(os.getenv("SC_WORKSPACE_NEURAL_MAX_TRAINING_SECONDS", "30")), 300.0))
MAX_HIDDEN_LAYERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_HIDDEN_LAYERS", "8")), MAX_LAYERS))
MAX_HIDDEN_UNITS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_HIDDEN_UNITS", "1024")), MAX_FEATURES))
TRAIN_THREADS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_TRAIN_THREADS", "2")), 8))
# v3.30 bounded trial/search orchestration. These limits are intentionally independent
# of the per-training limits so a search cannot multiply a safe single job into an
# unbounded workload.
NEURAL_TRIAL_SCHEMA = "sc-workspace-neural-trial-artifact/1.0"
NEURAL_BATCH_SCHEMA = "sc-workspace-neural-batch-artifact/1.0"
NEURAL_SEARCH_SCHEMA = "sc-workspace-neural-hyperparameter-search-artifact/1.0"
NEURAL_TRIAL_PLAN_SCHEMA = "sc-workspace-neural-trial-plan/1.0"
MAX_NEURAL_TRIALS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_TRIALS", "16")), 64))
MAX_NEURAL_BATCH_TRIALS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_BATCH_TRIALS", "12")), MAX_NEURAL_TRIALS))
MAX_NEURAL_SEARCH_VALUES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEARCH_VALUES", "8")), 32))
MAX_NEURAL_SEARCH_EPOCHS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEARCH_EPOCHS", "240")), 2000))
ALLOWED_HYPERPARAMETER_PATHS = {
    "optimizer.name", "optimizer.learningRate", "optimizer.weightDecay", "batchSize", "epochs"
}
ALLOWED_TRIAL_OBJECTIVE_METRICS = {"loss", "accuracy", "mae", "rmse"}
torch.set_num_threads(TRAIN_THREADS)
_OPTIMIZER_INIT_LOCK = threading.Lock()


def _warm_optimizer_runtime() -> bool:
    """Initialize PyTorch optimizer/Dynamo integration once before request threads."""
    probe = torch.nn.Linear(1, 1, device=DEVICE)
    with _OPTIMIZER_INIT_LOCK:
        # Adam is used because it exercised the production-only failure path.
        torch.optim.Adam(probe.parameters(), lr=0.001)
    return True


OPTIMIZER_RUNTIME_WARM = _warm_optimizer_runtime()
ALLOWED_TRAINING_TASKS = {"regression", "binary-classification", "multiclass-classification"}
ALLOWED_OPTIMIZERS = {"sgd", "adam"}
ALLOWED_TRAINING_ACTIVATIONS = {"identity", "relu", "sigmoid", "tanh"}
CHECKPOINT_SCHEMA = "sc-workspace-neural-checkpoint-artifact/1.0"
CHECKPOINT_STATE_SCHEMA = "sc-workspace-neural-checkpoint-state/1.0"
CHECKPOINT_FORMAT = "sc-workspace-neural-portable-checkpoint/1.0"
CHECKPOINT_BUNDLE_ENCODING = "zlib+base64+canonical-json-v1"
CHECKPOINT_RESUME_POLICY = "same-dataset-only"
MAX_CHECKPOINT_COMPRESSED_BYTES = max(64 * 1024, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_CHECKPOINT_COMPRESSED_BYTES", str(7 * 1024 * 1024))), 12 * 1024 * 1024))
MAX_CHECKPOINT_JSON_BYTES = max(256 * 1024, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_CHECKPOINT_JSON_BYTES", str(24 * 1024 * 1024))), 48 * 1024 * 1024))

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


def _current_device_name() -> str:
    return _CURRENT_DEVICE.get()


def _device_inventory_body() -> dict[str, Any]:
    devices: list[dict[str, Any]] = [{
        "device": "cpu", "deviceClass": "cpu", "available": True, "policyAllowed": True,
        "accelerator": False, "name": "CPU", "index": None,
    }]
    cuda_available = bool(torch.cuda.is_available())
    cuda_count = int(torch.cuda.device_count()) if cuda_available else 0
    for index in range(min(cuda_count, MAX_ACCELERATOR_DEVICES)):
        dev = f"cuda:{index}"
        props = torch.cuda.get_device_properties(index)
        devices.append({
            "device": dev, "deviceClass": "cuda", "available": True,
            "policyAllowed": bool(ACCELERATOR_ENABLED and dev in ALLOWED_DEVICES),
            "accelerator": True, "name": str(props.name), "index": index,
            "totalMemoryBytes": int(props.total_memory),
            "computeCapability": f"{int(props.major)}.{int(props.minor)}",
        })
    body = {
        "schema": DEVICE_INVENTORY_SCHEMA,
        "runtime": RUNTIME,
        "runtimeVersion": SERVICE_VERSION,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "acceleratorPolicyEnabled": ACCELERATOR_ENABLED,
        "allowedDevices": list(ALLOWED_DEVICES),
        "maxAcceleratorDevices": MAX_ACCELERATOR_DEVICES,
        "cudaRuntimeAvailable": cuda_available,
        "cudaDeviceCount": cuda_count,
        "devices": devices,
    }
    body["inventoryFingerprint"] = _canonical_sha256(body)
    return body


def _parse_device_request(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("deviceRequest", "cpu")
    if isinstance(raw, str):
        preference = raw.strip().lower() or "cpu"
        strict = preference not in {"auto"}
        allow_fallback = preference == "auto"
    elif isinstance(raw, dict):
        preference = str(raw.get("preference") or raw.get("device") or "cpu").strip().lower()
        strict = bool(raw.get("strict", preference not in {"auto"}))
        allow_fallback = bool(raw.get("allowFallback", preference == "auto"))
    else:
        raise HTTPException(status_code=400, detail="deviceRequest must be a string or object")
    if preference not in {"cpu", "auto", "accelerator"} and not preference.startswith("cuda:"):
        raise HTTPException(status_code=400, detail="deviceRequest preference is not registered")
    return {"preference": preference, "strict": strict, "allowFallback": allow_fallback}


def _resolve_device_plan(payload: dict[str, Any]) -> dict[str, Any]:
    req = _parse_device_request(payload)
    inv = _device_inventory_body()
    by_name = {d["device"]: d for d in inv["devices"]}
    accel = [d for d in inv["devices"] if d.get("accelerator") and d.get("available") and d.get("policyAllowed")]
    pref = req["preference"]
    selected = "cpu"
    fallback_reason = None
    if pref == "cpu":
        selected = "cpu"
    elif pref in {"auto", "accelerator"}:
        if accel:
            selected = accel[0]["device"]
        elif pref == "auto" or req["allowFallback"]:
            selected = "cpu"
            fallback_reason = "no-policy-allowed-accelerator-available"
        else:
            raise HTTPException(status_code=409, detail="requested accelerator is unavailable or disallowed by runtime policy")
    else:
        candidate = by_name.get(pref)
        if candidate and candidate.get("available") and candidate.get("policyAllowed"):
            selected = pref
        elif req["allowFallback"] and not req["strict"]:
            selected = "cpu"
            fallback_reason = "requested-device-unavailable-or-disallowed"
        else:
            raise HTTPException(status_code=409, detail="requested device is unavailable or disallowed by runtime policy")
    plan = {
        "schema": DEVICE_PLAN_SCHEMA,
        "requestedPreference": pref,
        "strict": req["strict"],
        "allowFallback": req["allowFallback"],
        "selectedDevice": selected,
        "selectedDeviceClass": "cuda" if selected.startswith("cuda:") else "cpu",
        "acceleratorSelected": selected.startswith("cuda:"),
        "acceleratorPolicyEnabled": ACCELERATOR_ENABLED,
        "fallbackReason": fallback_reason,
        "inventoryFingerprint": inv["inventoryFingerprint"],
        "reproducibility": {
            "deterministicAlgorithmsRequested": True,
            "deviceSelectionExplicit": True,
            "crossDeviceBitwiseIdentityGuaranteed": False,
        },
    }
    plan["planFingerprint"] = _canonical_sha256(plan)
    return plan


def _validate_device_plan(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != DEVICE_PLAN_SCHEMA:
        raise HTTPException(status_code=400, detail=f"devicePlan must use {DEVICE_PLAN_SCHEMA}")
    supplied = str(value.get("planFingerprint") or "")
    base = {k:v for k,v in value.items() if k != "planFingerprint"}
    if not supplied or not hmac.compare_digest(supplied, _canonical_sha256(base)):
        raise HTTPException(status_code=400, detail="devicePlan fingerprint verification failed")
    selected = str(value.get("selectedDevice") or "")
    inv = _device_inventory_body(); current = {d["device"]: d for d in inv["devices"]}
    d = current.get(selected)
    if not d or not d.get("available") or not d.get("policyAllowed"):
        raise HTTPException(status_code=409, detail="devicePlan selected device is no longer available under current policy")
    return value


def _device_inventory(payload: dict[str, Any]) -> dict[str, Any]:
    inv = _device_inventory_body()
    return {"kind":"neural-device-inventory","deviceInventory":inv,"inventoryFingerprint":inv["inventoryFingerprint"]}


def _device_plan(payload: dict[str, Any]) -> dict[str, Any]:
    plan = _resolve_device_plan(payload)
    return {"kind":"neural-device-plan","devicePlan":plan,"planFingerprint":plan["planFingerprint"]}


def _device_verify(payload: dict[str, Any]) -> dict[str, Any]:
    plan = _validate_device_plan(payload.get("devicePlan"))
    return {"kind":"neural-device-verification","valid":True,"selectedDevice":plan["selectedDevice"],"planFingerprint":plan["planFingerprint"]}


def _accelerator_smoke(payload: dict[str, Any]) -> dict[str, Any]:
    dev = _current_device_name()
    a = _tensor(payload.get("left", [[1.0,2.0],[3.0,4.0]]), name="left", dtype_name="float32", ndim=2)
    b = _tensor(payload.get("right", [[1.0,0.0],[0.0,1.0]]), name="right", dtype_name="float32", ndim=2)
    if a.shape[1] != b.shape[0] or a.numel() > 4096 or b.numel() > 4096:
        raise HTTPException(status_code=400, detail="accelerator smoke matrices are incompatible or exceed bounded size")
    out = a @ b
    if dev.startswith("cuda:"):
        torch.cuda.synchronize(torch.device(dev))
    return {"kind":"neural-accelerator-smoke","selectedDevice":dev,"acceleratorUsed":dev.startswith("cuda:"),"output":_tensor_json(out),"outputFingerprint":_canonical_sha256(_tensor_json(out))}


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
        out = torch.tensor(value, dtype=ALLOWED_DTYPES[dtype_name], device=_current_device_name())
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
        "device": _current_device_name(),
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



def _positive_int(value: Any, *, name: str, minimum: int, maximum: int) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"{name} must be an integer") from exc
    if out < minimum or out > maximum:
        raise HTTPException(status_code=400, detail=f"{name} is outside the supported range")
    return out


def _finite_float(value: Any, *, name: str, minimum: float | None = None, maximum: float | None = None) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"{name} must be numeric") from exc
    if not math.isfinite(out):
        raise HTTPException(status_code=400, detail=f"{name} must be finite")
    if minimum is not None and out < minimum:
        raise HTTPException(status_code=400, detail=f"{name} is below the supported range")
    if maximum is not None and out > maximum:
        raise HTTPException(status_code=400, detail=f"{name} is above the supported range")
    return out


def _normalized_training_spec(payload: dict[str, Any], *, expected_model_type: str | None = None) -> dict[str, Any]:
    spec = payload.get("trainingSpec")
    if not isinstance(spec, dict) or spec.get("schema") != "sc-workspace-neural-training-spec/1.0":
        raise HTTPException(status_code=400, detail="trainingSpec must use sc-workspace-neural-training-spec/1.0")
    task = str(spec.get("task") or "regression").strip().lower()
    if task not in ALLOWED_TRAINING_TASKS:
        raise HTTPException(status_code=400, detail="training task is not registered")
    model_type = str(spec.get("modelType") or expected_model_type or "mlp").strip().lower()
    if model_type not in {"linear", "mlp"}:
        raise HTTPException(status_code=400, detail="training modelType must be linear or mlp")
    if expected_model_type and model_type != expected_model_type:
        raise HTTPException(status_code=400, detail=f"operation requires modelType={expected_model_type}")
    input_features = _positive_int(spec.get("inputFeatures"), name="trainingSpec.inputFeatures", minimum=1, maximum=MAX_FEATURES)
    output_features = _positive_int(spec.get("outputFeatures", 1), name="trainingSpec.outputFeatures", minimum=1, maximum=MAX_FEATURES)
    if task == "binary-classification" and output_features != 1:
        raise HTTPException(status_code=400, detail="binary classification requires outputFeatures=1")
    if task == "multiclass-classification" and output_features < 2:
        raise HTTPException(status_code=400, detail="multiclass classification requires outputFeatures>=2")
    hidden_raw = spec.get("hiddenLayers") or []
    if not isinstance(hidden_raw, list):
        raise HTTPException(status_code=400, detail="trainingSpec.hiddenLayers must be an array")
    if model_type == "linear" and hidden_raw:
        raise HTTPException(status_code=400, detail="linear training does not accept hiddenLayers")
    if len(hidden_raw) > MAX_HIDDEN_LAYERS:
        raise HTTPException(status_code=413, detail="hidden layer count exceeds the bounded training limit")
    hidden: list[dict[str, Any]] = []
    for index, item in enumerate(hidden_raw):
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail=f"trainingSpec.hiddenLayers[{index}] must be an object")
        units = _positive_int(item.get("units"), name=f"trainingSpec.hiddenLayers[{index}].units", minimum=1, maximum=MAX_HIDDEN_UNITS)
        activation = str(item.get("activation") or "relu").strip().lower()
        if activation not in ALLOWED_TRAINING_ACTIVATIONS:
            raise HTTPException(status_code=400, detail=f"trainingSpec.hiddenLayers[{index}].activation is not registered")
        hidden.append({"units": units, "activation": activation})
    if model_type == "mlp" and not hidden:
        raise HTTPException(status_code=400, detail="MLP training requires at least one hidden layer")
    optimizer_raw = spec.get("optimizer") or {}
    if not isinstance(optimizer_raw, dict):
        raise HTTPException(status_code=400, detail="trainingSpec.optimizer must be an object")
    optimizer_name = str(optimizer_raw.get("name") or "adam").strip().lower()
    if optimizer_name not in ALLOWED_OPTIMIZERS:
        raise HTTPException(status_code=400, detail="optimizer is not registered")
    learning_rate = _finite_float(optimizer_raw.get("learningRate", 0.01 if optimizer_name == "sgd" else 0.001), name="optimizer.learningRate", minimum=1e-8, maximum=10.0)
    weight_decay = _finite_float(optimizer_raw.get("weightDecay", 0.0), name="optimizer.weightDecay", minimum=0.0, maximum=10.0)
    epochs = _positive_int(spec.get("epochs", 10), name="trainingSpec.epochs", minimum=1, maximum=MAX_TRAINING_EPOCHS)
    batch_size = _positive_int(spec.get("batchSize", min(32, MAX_BATCH)), name="trainingSpec.batchSize", minimum=1, maximum=MAX_BATCH)
    shuffle = bool(spec.get("shuffle", True))
    validation_enabled = bool(payload.get("validationFeatures") is not None or payload.get("validationTargets") is not None)
    if (payload.get("validationFeatures") is None) != (payload.get("validationTargets") is None):
        raise HTTPException(status_code=400, detail="validationFeatures and validationTargets must be provided together")
    normalized = {
        "schema": "sc-workspace-neural-training-spec/1.0",
        "modelType": model_type,
        "task": task,
        "inputFeatures": input_features,
        "hiddenLayers": hidden,
        "outputFeatures": output_features,
        "optimizer": {"name": optimizer_name, "learningRate": learning_rate, "weightDecay": weight_decay},
        "epochs": epochs,
        "batchSize": batch_size,
        "shuffle": shuffle,
        "validationEnabled": validation_enabled,
        "device": _current_device_name(),
    }
    return normalized


def _parameter_count_for_training(spec: dict[str, Any]) -> int:
    dims = [int(spec["inputFeatures"])] + [int(x["units"]) for x in spec["hiddenLayers"]] + [int(spec["outputFeatures"])]
    total = 0
    for a, b in zip(dims[:-1], dims[1:]):
        total += a * b + b
    return total


def _training_plan(payload: dict[str, Any]) -> dict[str, Any]:
    spec = _normalized_training_spec(payload)
    parameter_count = _parameter_count_for_training(spec)
    if parameter_count > MAX_TRAINING_PARAMETERS:
        raise HTTPException(status_code=413, detail="training parameter count exceeds the bounded training limit")
    plan = {
        **spec,
        "parameterCount": parameter_count,
        "maxTrainingRows": MAX_TRAINING_ROWS,
        "maxTrainingParameters": MAX_TRAINING_PARAMETERS,
        "maxTrainingSeconds": MAX_TRAINING_SECONDS,
        "threadLimit": TRAIN_THREADS,
        "checkpointPersistenceEnabled": True,
        "resumeTrainingEnabled": True,
        "checkpointArtifactSchema": CHECKPOINT_SCHEMA,
        "checkpointStateSchema": CHECKPOINT_STATE_SCHEMA,
        "checkpointFormat": CHECKPOINT_FORMAT,
        "checkpointResumePolicy": CHECKPOINT_RESUME_POLICY,
        "acceleratorExecutionEnabled": bool(ACCELERATOR_ENABLED),
        "arbitraryCodeExecution": False,
    }
    return {
        "kind": "neural-training-plan",
        "plan": plan,
        "trainingSpecFingerprint": _canonical_sha256(spec),
        "planFingerprint": _canonical_sha256(plan),
    }


def _activation_module(name: str) -> torch.nn.Module:
    if name == "relu": return torch.nn.ReLU()
    if name == "sigmoid": return torch.nn.Sigmoid()
    if name == "tanh": return torch.nn.Tanh()
    return torch.nn.Identity()


def _build_training_model(spec: dict[str, Any]) -> torch.nn.Module:
    layers: list[torch.nn.Module] = []
    current = int(spec["inputFeatures"])
    for hidden in spec["hiddenLayers"]:
        units = int(hidden["units"])
        layers.append(torch.nn.Linear(current, units))
        layers.append(_activation_module(str(hidden["activation"])))
        current = units
    layers.append(torch.nn.Linear(current, int(spec["outputFeatures"])))
    return torch.nn.Sequential(*layers).to(_current_device_name())


def _training_tensors(payload: dict[str, Any], spec: dict[str, Any], *, validation: bool = False) -> tuple[torch.Tensor, torch.Tensor]:
    prefix = "validation" if validation else ""
    features_key = "validationFeatures" if validation else "features"
    targets_key = "validationTargets" if validation else "targets"
    x = _tensor(payload.get(features_key), name=features_key, dtype_name="float32", ndim=2)
    if int(x.shape[0]) < 2 or int(x.shape[0]) > MAX_TRAINING_ROWS:
        raise HTTPException(status_code=413, detail=f"{features_key} row count is outside the bounded training range")
    if int(x.shape[1]) != int(spec["inputFeatures"]):
        raise HTTPException(status_code=400, detail=f"{features_key} feature count does not match trainingSpec.inputFeatures")
    task = spec["task"]
    if task == "multiclass-classification":
        y = _tensor(payload.get(targets_key), name=targets_key, dtype_name="int64")
        if y.ndim == 2 and int(y.shape[1]) == 1: y = y.reshape(-1)
        if y.ndim != 1:
            raise HTTPException(status_code=400, detail=f"{targets_key} must be rank 1 for multiclass classification")
        if y.numel() and (int(y.min().item()) < 0 or int(y.max().item()) >= int(spec["outputFeatures"])):
            raise HTTPException(status_code=400, detail=f"{targets_key} contains a class outside outputFeatures")
    else:
        y = _tensor(payload.get(targets_key), name=targets_key, dtype_name="float32")
        if y.ndim == 1: y = y.reshape(-1, 1)
        if y.ndim != 2:
            raise HTTPException(status_code=400, detail=f"{targets_key} must be rank 1 or rank 2")
        expected_outputs = 1 if task == "binary-classification" else int(spec["outputFeatures"])
        if int(y.shape[1]) != expected_outputs:
            raise HTTPException(status_code=400, detail=f"{targets_key} output width does not match the training task")
        if task == "binary-classification" and y.numel() and bool(((y < 0) | (y > 1)).any()):
            raise HTTPException(status_code=400, detail=f"{targets_key} must be in [0,1] for binary classification")
    if int(x.shape[0]) != int(y.shape[0]):
        raise HTTPException(status_code=400, detail=f"{features_key} and {targets_key} row counts must match")
    return x, y


def _loss_function(task: str) -> torch.nn.Module:
    if task == "binary-classification": return torch.nn.BCEWithLogitsLoss()
    if task == "multiclass-classification": return torch.nn.CrossEntropyLoss()
    return torch.nn.MSELoss()


def _optimizer(model: torch.nn.Module, spec: dict[str, Any]) -> torch.optim.Optimizer:
    cfg = spec["optimizer"]
    kwargs = {"lr": float(cfg["learningRate"]), "weight_decay": float(cfg["weightDecay"])}
    # Keep first-use optimizer initialization serialized even though Dynamo is
    # already preloaded/warmed. This is intentionally narrow; training itself
    # remains outside the lock.
    with _OPTIMIZER_INIT_LOCK:
        if cfg["name"] == "sgd":
            return torch.optim.SGD(model.parameters(), **kwargs)
        return torch.optim.Adam(model.parameters(), **kwargs)


def _metrics_from_logits(logits: torch.Tensor, targets: torch.Tensor, task: str, loss_value: float) -> dict[str, Any]:
    metrics: dict[str, Any] = {"loss": float(loss_value)}
    if task == "binary-classification":
        pred = (torch.sigmoid(logits) >= 0.5).to(targets.dtype)
        metrics["accuracy"] = float((pred == targets).to(torch.float32).mean().item())
    elif task == "multiclass-classification":
        pred = torch.argmax(logits, dim=1)
        metrics["accuracy"] = float((pred == targets).to(torch.float32).mean().item())
    else:
        residual = (logits - targets).detach()
        metrics["mae"] = float(torch.mean(torch.abs(residual)).item())
        metrics["rmse"] = float(torch.sqrt(torch.mean(residual * residual)).item())
    return metrics


def _export_trained_model_spec(model: torch.nn.Sequential, spec: dict[str, Any]) -> dict[str, Any]:
    linear_modules = [m for m in model if isinstance(m, torch.nn.Linear)]
    if spec["modelType"] == "linear":
        layer = linear_modules[0]
        return {
            "schema": "sc-workspace-neural-model-spec/1.0", "modelType": "linear",
            "weights": _tensor_json(layer.weight), "bias": _tensor_json(layer.bias), "activation": "identity",
        }
    layers=[]
    activation_names=[x["activation"] for x in spec["hiddenLayers"]] + ["identity"]
    for layer, activation in zip(linear_modules, activation_names):
        layers.append({"weights": _tensor_json(layer.weight), "bias": _tensor_json(layer.bias), "activation": activation})
    return {"schema": "sc-workspace-neural-model-spec/1.0", "modelType": "mlp", "layers": layers}


def _checkpoint_compatibility_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "modelType": spec["modelType"],
        "task": spec["task"],
        "inputFeatures": int(spec["inputFeatures"]),
        "outputFeatures": int(spec["outputFeatures"]),
        "hiddenLayers": spec["hiddenLayers"],
        "optimizer": spec["optimizer"],
        "batchSize": int(spec["batchSize"]),
        "shuffle": bool(spec["shuffle"]),
    }


def _state_key_encode(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if isinstance(value, int):
        return {"type": "int", "value": value}
    if isinstance(value, str):
        return {"type": "str", "value": value}
    raise HTTPException(status_code=500, detail="checkpoint state contains an unsupported dictionary key")


def _state_key_decode(value: Any) -> Any:
    if not isinstance(value, dict):
        raise HTTPException(status_code=400, detail="checkpoint state dictionary key is malformed")
    kind = value.get("type")
    raw = value.get("value")
    if kind == "bool" and isinstance(raw, bool): return raw
    if kind == "int" and isinstance(raw, int) and not isinstance(raw, bool): return raw
    if kind == "str" and isinstance(raw, str): return raw
    raise HTTPException(status_code=400, detail="checkpoint state dictionary key is unsupported")


def _state_encode(value: Any) -> Any:
    if isinstance(value, torch.Tensor):
        tensor = value.detach().cpu()
        return {
            "__sc_tensor__": True,
            "dtype": str(tensor.dtype).replace("torch.", ""),
            "shape": list(tensor.shape),
            "values": tensor.tolist(),
        }
    if isinstance(value, dict):
        return {"__sc_dict__": [[_state_key_encode(k), _state_encode(v)] for k, v in value.items()]}
    if isinstance(value, (list, tuple)):
        return {"__sc_list__": [_state_encode(v) for v in value]}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise HTTPException(status_code=500, detail=f"checkpoint state value type is not portable: {type(value).__name__}")


def _state_decode(value: Any) -> Any:
    if isinstance(value, dict) and value.get("__sc_tensor__") is True:
        dtype_name = str(value.get("dtype") or "")
        dtype_map = {
            "float16": torch.float16, "float32": torch.float32, "float64": torch.float64,
            "bfloat16": torch.bfloat16, "int32": torch.int32, "int64": torch.int64, "bool": torch.bool,
        }
        dtype = dtype_map.get(dtype_name)
        if dtype is None:
            raise HTTPException(status_code=400, detail="checkpoint tensor dtype is unsupported")
        tensor = torch.tensor(value.get("values"), dtype=dtype, device="cpu")
        expected_shape = value.get("shape")
        if not isinstance(expected_shape, list) or list(tensor.shape) != expected_shape:
            raise HTTPException(status_code=400, detail="checkpoint tensor shape does not match encoded values")
        return tensor
    if isinstance(value, dict) and "__sc_dict__" in value:
        rows = value.get("__sc_dict__")
        if not isinstance(rows, list):
            raise HTTPException(status_code=400, detail="checkpoint state dictionary is malformed")
        out: dict[Any, Any] = {}
        for row in rows:
            if not isinstance(row, list) or len(row) != 2:
                raise HTTPException(status_code=400, detail="checkpoint state dictionary row is malformed")
            out[_state_key_decode(row[0])] = _state_decode(row[1])
        return out
    if isinstance(value, dict) and "__sc_list__" in value:
        rows = value.get("__sc_list__")
        if not isinstance(rows, list):
            raise HTTPException(status_code=400, detail="checkpoint state list is malformed")
        return [_state_decode(v) for v in rows]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise HTTPException(status_code=400, detail="checkpoint state value is malformed")


def _checkpoint_state_bundle(model: torch.nn.Module, optimizer: torch.optim.Optimizer) -> dict[str, Any]:
    state_doc = {
        "schema": CHECKPOINT_STATE_SCHEMA,
        "modelState": _state_encode(model.state_dict()),
        "optimizerState": _state_encode(optimizer.state_dict()),
    }
    raw = json.dumps(state_doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(raw) > MAX_CHECKPOINT_JSON_BYTES:
        raise HTTPException(status_code=413, detail="checkpoint state exceeds the bounded portable JSON limit")
    compressed = zlib.compress(raw, 9)
    if len(compressed) > MAX_CHECKPOINT_COMPRESSED_BYTES:
        raise HTTPException(status_code=413, detail="checkpoint state exceeds the bounded compressed artifact limit")
    return {
        "stateBundleEncoding": CHECKPOINT_BUNDLE_ENCODING,
        "stateBundleBase64": base64.b64encode(compressed).decode("ascii"),
        "stateBundleSha256": hashlib.sha256(compressed).hexdigest(),
        "stateBundleJsonSha256": hashlib.sha256(raw).hexdigest(),
        "stateBundleCompressedBytes": len(compressed),
        "stateBundleJsonBytes": len(raw),
    }


def _decode_checkpoint_state(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact.get("stateBundleEncoding") != CHECKPOINT_BUNDLE_ENCODING:
        raise HTTPException(status_code=400, detail="checkpoint state bundle encoding is unsupported")
    encoded = artifact.get("stateBundleBase64")
    if not isinstance(encoded, str) or not encoded:
        raise HTTPException(status_code=400, detail="checkpoint state bundle is missing")
    try:
        compressed = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="checkpoint state bundle is not valid base64") from exc
    if len(compressed) > MAX_CHECKPOINT_COMPRESSED_BYTES:
        raise HTTPException(status_code=413, detail="checkpoint compressed artifact exceeds the bounded limit")
    if hashlib.sha256(compressed).hexdigest() != artifact.get("stateBundleSha256"):
        raise HTTPException(status_code=400, detail="checkpoint compressed-state fingerprint mismatch")
    try:
        dec = zlib.decompressobj()
        raw = dec.decompress(compressed, MAX_CHECKPOINT_JSON_BYTES + 1)
        if len(raw) > MAX_CHECKPOINT_JSON_BYTES or dec.unconsumed_tail or not dec.eof:
            raise HTTPException(status_code=413, detail="checkpoint JSON state exceeds the bounded decompression limit")
        raw += dec.flush()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail="checkpoint state bundle cannot be decompressed") from exc
    if len(raw) > MAX_CHECKPOINT_JSON_BYTES:
        raise HTTPException(status_code=413, detail="checkpoint JSON state exceeds the bounded limit")
    if hashlib.sha256(raw).hexdigest() != artifact.get("stateBundleJsonSha256"):
        raise HTTPException(status_code=400, detail="checkpoint JSON-state fingerprint mismatch")
    try:
        state_doc = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="checkpoint state bundle is not canonical JSON") from exc
    if not isinstance(state_doc, dict) or state_doc.get("schema") != CHECKPOINT_STATE_SCHEMA:
        raise HTTPException(status_code=400, detail="checkpoint state schema is unsupported")
    return state_doc


def _checkpoint_body_for_fingerprint(artifact: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in artifact.items() if k not in {"artifactFingerprint", "checkpointId"}}


def _validate_checkpoint_artifact(value: Any, *, decode_state: bool = True) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not isinstance(value, dict) or value.get("schema") != CHECKPOINT_SCHEMA:
        raise HTTPException(status_code=400, detail=f"checkpointArtifact must use {CHECKPOINT_SCHEMA}")
    artifact = dict(value)
    if artifact.get("format") != CHECKPOINT_FORMAT:
        raise HTTPException(status_code=400, detail="checkpoint artifact format is unsupported")
    supplied_fp = str(artifact.get("artifactFingerprint") or "")
    expected_fp = _canonical_sha256(_checkpoint_body_for_fingerprint(artifact))
    if not supplied_fp or not hmac.compare_digest(supplied_fp, expected_fp):
        raise HTTPException(status_code=400, detail="checkpoint artifact fingerprint mismatch")
    expected_id = "nck_" + expected_fp[:24]
    if artifact.get("checkpointId") != expected_id:
        raise HTTPException(status_code=400, detail="checkpoint artifact id does not match its fingerprint")
    if artifact.get("runtime") != RUNTIME:
        raise HTTPException(status_code=400, detail="checkpoint artifact runtime is incompatible")
    state_doc = _decode_checkpoint_state(artifact) if decode_state else None
    return artifact, state_doc


def _create_checkpoint_artifact(
    model: torch.nn.Module, optimizer: torch.optim.Optimizer, spec: dict[str, Any], payload: dict[str, Any],
    *, trained_spec: dict[str, Any], starting_epoch: int, completed_segment_epochs: int,
    parent_checkpoint: dict[str, Any] | None, operation: str,
) -> dict[str, Any]:
    dataset_fp = _canonical_sha256({"features": payload.get("features"), "targets": payload.get("targets")})
    cumulative_epochs = starting_epoch + completed_segment_epochs
    parent_fp = parent_checkpoint.get("artifactFingerprint") if parent_checkpoint else None
    lineage_depth = int(parent_checkpoint.get("lineageDepth", 0)) + 1 if parent_checkpoint else 0
    body: dict[str, Any] = {
        "schema": CHECKPOINT_SCHEMA,
        "format": CHECKPOINT_FORMAT,
        "runtime": RUNTIME,
        "runtimeVersion": SERVICE_VERSION,
        "portable": True,
        "arbitrarySerializedModel": False,
        "modelType": spec["modelType"],
        "task": spec["task"],
        "seed": int(payload.get("seed", 42)),
        "startingEpoch": starting_epoch,
        "completedSegmentEpochs": completed_segment_epochs,
        "completedEpochs": cumulative_epochs,
        "optimizer": spec["optimizer"],
        "trainingSpecFingerprint": _canonical_sha256(spec),
        "trainingCompatibilityFingerprint": _canonical_sha256(_checkpoint_compatibility_spec(spec)),
        "trainingDatasetFingerprint": dataset_fp,
        "trainedModelSpecFingerprint": _canonical_sha256(trained_spec),
        "parentCheckpointFingerprint": parent_fp,
        "lineageDepth": lineage_depth,
        "resumePolicy": CHECKPOINT_RESUME_POLICY,
        "createdFromOperation": operation,
        **_checkpoint_state_bundle(model, optimizer),
    }
    fingerprint = _canonical_sha256(body)
    body["artifactFingerprint"] = fingerprint
    body["checkpointId"] = "nck_" + fingerprint[:24]
    return body


def _checkpoint_inspect(payload: dict[str, Any]) -> dict[str, Any]:
    artifact, _ = _validate_checkpoint_artifact(payload.get("checkpointArtifact"), decode_state=True)
    metadata = {k: v for k, v in artifact.items() if k != "stateBundleBase64"}
    return {
        "kind": "neural-checkpoint-inspection",
        "checkpoint": metadata,
        "stateBundleVerified": True,
        "checkpointPersistenceEnabled": True,
        "resumeTrainingEnabled": True,
        "resumePolicy": CHECKPOINT_RESUME_POLICY,
    }


def _resume_checkpoint(payload: dict[str, Any], spec: dict[str, Any], *, expected_model_type: str) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact, state_doc = _validate_checkpoint_artifact(payload.get("checkpointArtifact"), decode_state=True)
    assert state_doc is not None
    if artifact.get("modelType") != expected_model_type or spec["modelType"] != expected_model_type:
        raise HTTPException(status_code=400, detail="checkpoint model type is incompatible with the resume operation")
    if artifact.get("task") != spec["task"]:
        raise HTTPException(status_code=400, detail="checkpoint task is incompatible with the resume training spec")
    seed_value = int(payload.get("seed", artifact.get("seed", 42)))
    if seed_value != int(artifact.get("seed", -1)):
        raise HTTPException(status_code=400, detail="resume seed must match the checkpoint seed")
    compatibility_fp = _canonical_sha256(_checkpoint_compatibility_spec(spec))
    if compatibility_fp != artifact.get("trainingCompatibilityFingerprint"):
        raise HTTPException(status_code=400, detail="resume training spec is incompatible with the checkpoint architecture/optimizer contract")
    dataset_fp = _canonical_sha256({"features": payload.get("features"), "targets": payload.get("targets")})
    if CHECKPOINT_RESUME_POLICY == "same-dataset-only" and dataset_fp != artifact.get("trainingDatasetFingerprint"):
        raise HTTPException(status_code=400, detail="resume dataset fingerprint must match the checkpoint under same-dataset-only policy")
    return artifact, state_doc


def _restore_checkpoint_state(model: torch.nn.Module, optimizer: torch.optim.Optimizer, state_doc: dict[str, Any]) -> None:
    try:
        model_state = _state_decode(state_doc.get("modelState"))
        optimizer_state = _state_decode(state_doc.get("optimizerState"))
        if not isinstance(model_state, dict) or not isinstance(optimizer_state, dict):
            raise ValueError("decoded checkpoint state is not a mapping")
        model.load_state_dict(model_state, strict=True)
        optimizer.load_state_dict(optimizer_state)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"checkpoint state cannot be restored: {exc.__class__.__name__}") from exc


def _train(payload: dict[str, Any], *, expected_model_type: str, resume: bool = False) -> dict[str, Any]:
    spec = _normalized_training_spec(payload, expected_model_type=expected_model_type)
    parameter_count = _parameter_count_for_training(spec)
    if parameter_count > MAX_TRAINING_PARAMETERS:
        raise HTTPException(status_code=413, detail="training parameter count exceeds the bounded training limit")
    x, y = _training_tensors(payload, spec)
    vx = vy = None
    if spec["validationEnabled"]:
        vx, vy = _training_tensors(payload, spec, validation=True)
    checkpoint_in: dict[str, Any] | None = None
    state_doc: dict[str, Any] | None = None
    if resume:
        checkpoint_in, state_doc = _resume_checkpoint(payload, spec, expected_model_type=expected_model_type)
    seed_value = int(payload.get("seed", checkpoint_in.get("seed", 42) if checkpoint_in else 42))
    torch.manual_seed(seed_value)
    model = _build_training_model(spec)
    loss_fn = _loss_function(spec["task"])
    optimizer = _optimizer(model, spec)
    starting_epoch = int(checkpoint_in.get("completedEpochs", 0)) if checkpoint_in else 0
    if state_doc is not None:
        _restore_checkpoint_state(model, optimizer, state_doc)
    started = time.monotonic()
    telemetry: list[dict[str, Any]] = []
    n = int(x.shape[0]); batch_size = min(int(spec["batchSize"]), n)
    completed_epochs = 0; stopped_reason = "completed"
    for epoch in range(int(spec["epochs"])):
        if time.monotonic() - started >= MAX_TRAINING_SECONDS:
            stopped_reason = "time-budget"
            break
        global_epoch = starting_epoch + epoch
        if spec["shuffle"]:
            g = torch.Generator(device="cpu"); g.manual_seed(seed_value + global_epoch)
            order = torch.randperm(n, generator=g)
        else:
            order = torch.arange(n)
        model.train(); running = 0.0; seen = 0
        for start in range(0, n, batch_size):
            idx = order[start:start + batch_size]
            bx = x[idx]; by = y[idx]
            optimizer.zero_grad(set_to_none=True)
            logits = model(bx)
            loss = loss_fn(logits, by)
            if not bool(torch.isfinite(loss)):
                raise HTTPException(status_code=422, detail="training produced a non-finite loss")
            loss.backward(); optimizer.step()
            size = int(idx.numel()); running += float(loss.detach().item()) * size; seen += size
        completed_epochs += 1
        row = {"epoch": starting_epoch + completed_epochs, "segmentEpoch": completed_epochs, "trainingLoss": running / max(1, seen)}
        if vx is not None and vy is not None:
            model.eval()
            with torch.no_grad():
                v_logits = model(vx); v_loss = loss_fn(v_logits, vy)
            row["validationLoss"] = float(v_loss.item())
        telemetry.append(row)
    if completed_epochs == 0:
        raise HTTPException(status_code=408, detail="training time budget elapsed before the first epoch completed")
    model.eval()
    with torch.no_grad():
        train_logits = model(x); train_loss = float(loss_fn(train_logits, y).item())
        final_training_metrics = _metrics_from_logits(train_logits, y, spec["task"], train_loss)
        validation_metrics = None
        if vx is not None and vy is not None:
            val_logits = model(vx); val_loss = float(loss_fn(val_logits, vy).item())
            validation_metrics = _metrics_from_logits(val_logits, vy, spec["task"], val_loss)
    trained_spec = _export_trained_model_spec(model, spec)
    elapsed = time.monotonic() - started
    operation = f"workspace.neural.{'resume' if resume else 'train'}-{expected_model_type}"
    checkpoint_out = _create_checkpoint_artifact(
        model, optimizer, spec, payload, trained_spec=trained_spec, starting_epoch=starting_epoch,
        completed_segment_epochs=completed_epochs, parent_checkpoint=checkpoint_in, operation=operation,
    )
    cumulative_epochs = starting_epoch + completed_epochs
    training_run = {
        "schema": "sc-workspace-neural-training-run/1.0",
        "modelType": spec["modelType"], "task": spec["task"], "seed": seed_value,
        "requestedEpochs": int(spec["epochs"]), "completedEpochs": completed_epochs,
        "startingEpoch": starting_epoch, "cumulativeEpochs": cumulative_epochs,
        "batchSize": batch_size, "shuffle": bool(spec["shuffle"]),
        "optimizer": spec["optimizer"], "parameterCount": parameter_count,
        "trainingRows": int(x.shape[0]), "validationRows": int(vx.shape[0]) if vx is not None else 0,
        "elapsedSeconds": elapsed, "stoppedReason": stopped_reason,
        "trainingMetrics": final_training_metrics, "validationMetrics": validation_metrics,
        "telemetry": telemetry,
        "checkpointCreated": True, "checkpointPersistenceEnabled": True, "resumeTrainingEnabled": True,
        "checkpointArtifactSchema": CHECKPOINT_SCHEMA, "checkpointId": checkpoint_out["checkpointId"],
        "checkpointFingerprint": checkpoint_out["artifactFingerprint"],
        "resumed": resume,
        "resumedFromCheckpointFingerprint": checkpoint_in.get("artifactFingerprint") if checkpoint_in else None,
        "lineageDepth": checkpoint_out["lineageDepth"],
        "device": _current_device_name(), "threadLimit": TRAIN_THREADS,
    }
    dataset_fp = _canonical_sha256({"features": payload.get("features"), "targets": payload.get("targets")})
    return {
        "kind": "neural-resume-result" if resume else "neural-training-result",
        "trainingRun": training_run,
        "trainingSpecFingerprint": _canonical_sha256(spec),
        "trainingDatasetFingerprint": dataset_fp,
        "validationDatasetFingerprint": _canonical_sha256({"features": payload.get("validationFeatures"), "targets": payload.get("validationTargets")}) if vx is not None else None,
        "trainedModelSpec": trained_spec,
        "trainedModelSpecFingerprint": _canonical_sha256(trained_spec),
        "checkpointArtifact": checkpoint_out,
        "checkpointArtifactFingerprint": checkpoint_out["artifactFingerprint"],
        "parentCheckpointFingerprint": checkpoint_out["parentCheckpointFingerprint"],
        "checkpointLineageDepth": checkpoint_out["lineageDepth"],
        "externalCodeExecuted": False,
    }


# ---- v3.30 neural batch, trial, and hyperparameter execution ----
def _copy_json(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str))


def _trial_objective(payload: dict[str, Any], training_spec: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("objective") or {}
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="objective must be an object")
    dataset = str(raw.get("dataset") or ("validation" if training_spec.get("validationEnabled") else "training")).strip().lower()
    if dataset not in {"training", "validation"}:
        raise HTTPException(status_code=400, detail="objective.dataset must be training or validation")
    if dataset == "validation" and not training_spec.get("validationEnabled"):
        raise HTTPException(status_code=400, detail="validation objective requires validationFeatures and validationTargets")
    default_metric = "accuracy" if training_spec.get("task") in {"binary-classification", "multiclass-classification"} else "loss"
    metric = str(raw.get("metric") or default_metric).strip().lower()
    if metric not in ALLOWED_TRIAL_OBJECTIVE_METRICS:
        raise HTTPException(status_code=400, detail="objective.metric is not registered")
    default_direction = "maximize" if metric == "accuracy" else "minimize"
    direction = str(raw.get("direction") or default_direction).strip().lower()
    if direction not in {"minimize", "maximize"}:
        raise HTTPException(status_code=400, detail="objective.direction must be minimize or maximize")
    if metric == "accuracy" and training_spec.get("task") == "regression":
        raise HTTPException(status_code=400, detail="accuracy is not available for regression trials")
    if metric in {"mae", "rmse"} and training_spec.get("task") != "regression":
        raise HTTPException(status_code=400, detail=f"{metric} is only available for regression trials")
    return {"dataset": dataset, "metric": metric, "direction": direction}


def _apply_hyperparameters(base_spec: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise HTTPException(status_code=400, detail="trial hyperparameters must be an object")
    unknown = sorted(set(params) - ALLOWED_HYPERPARAMETER_PATHS)
    if unknown:
        raise HTTPException(status_code=400, detail="unsupported hyperparameter path(s): " + ", ".join(unknown))
    spec = _copy_json(base_spec)
    spec.setdefault("optimizer", {})
    for path, value in params.items():
        if path.startswith("optimizer."):
            spec["optimizer"][path.split(".", 1)[1]] = value
        else:
            spec[path] = value
    return spec


def _trial_plan(payload: dict[str, Any]) -> dict[str, Any]:
    base = payload.get("trainingSpec")
    params = payload.get("hyperparameters") or {}
    if not isinstance(base, dict):
        raise HTTPException(status_code=400, detail="trainingSpec must be supplied for a neural trial")
    trial_payload = dict(payload)
    trial_payload["trainingSpec"] = _apply_hyperparameters(base, params)
    spec = _normalized_training_spec(trial_payload)
    obj = _trial_objective(trial_payload, spec)
    parameter_count = _parameter_count_for_training(spec)
    if parameter_count > MAX_TRAINING_PARAMETERS:
        raise HTTPException(status_code=413, detail="trial parameter count exceeds the bounded training limit")
    plan = {
        "schema": NEURAL_TRIAL_PLAN_SCHEMA,
        "trainingSpec": spec,
        "trainingSpecFingerprint": _canonical_sha256(spec),
        "hyperparameters": _copy_json(params),
        "hyperparametersFingerprint": _canonical_sha256(params),
        "objective": obj,
        "seed": int(payload.get("seed", 42)),
        "device": _current_device_name(),
        "devicePlanFingerprint": (_resolve_device_plan(payload)).get("planFingerprint"),
        "parameterCount": parameter_count,
        "bounded": True,
        "arbitraryCodeExecution": False,
    }
    plan["planFingerprint"] = _canonical_sha256(plan)
    return {"kind": "neural-trial-plan", "trialPlan": plan, "planFingerprint": plan["planFingerprint"]}


def _objective_value(training_result: dict[str, Any], objective: dict[str, Any]) -> float:
    run = training_result.get("trainingRun") if isinstance(training_result.get("trainingRun"), dict) else {}
    metrics = run.get("validationMetrics") if objective["dataset"] == "validation" else run.get("trainingMetrics")
    if not isinstance(metrics, dict) or objective["metric"] not in metrics:
        raise HTTPException(status_code=422, detail="requested trial objective metric was not produced")
    value = float(metrics[objective["metric"]])
    if not math.isfinite(value):
        raise HTTPException(status_code=422, detail="trial objective produced a non-finite value")
    return value


def _execute_trial(payload: dict[str, Any], *, trial_index: int = 0, inherited_hyperparameters: dict[str, Any] | None = None, inherited_seed: int | None = None) -> dict[str, Any]:
    params = inherited_hyperparameters if inherited_hyperparameters is not None else (payload.get("hyperparameters") or {})
    base = payload.get("trainingSpec")
    if not isinstance(base, dict):
        raise HTTPException(status_code=400, detail="trainingSpec must be supplied for trial execution")
    trial_payload = dict(payload)
    trial_payload.pop("hyperparameters", None)
    trial_payload.pop("objective", None)
    trial_payload["trainingSpec"] = _apply_hyperparameters(base, params)
    seed_value = int(inherited_seed if inherited_seed is not None else payload.get("seed", 42))
    trial_payload["seed"] = seed_value
    spec = _normalized_training_spec(trial_payload)
    objective = _trial_objective(payload, spec)
    model_type = str(spec["modelType"])
    result = _train(trial_payload, expected_model_type=model_type, resume=False)
    objective_value = _objective_value(result, objective)
    training_run_for_artifact = _copy_json(result.get("trainingRun") or {})
    training_run_for_artifact.pop("elapsedSeconds", None)
    artifact = {
        "schema": NEURAL_TRIAL_SCHEMA,
        "kind": "neural-trial",
        "trialIndex": int(trial_index),
        "trialId": None,
        "seed": seed_value,
        "hyperparameters": _copy_json(params),
        "hyperparametersFingerprint": _canonical_sha256(params),
        "objective": objective,
        "objectiveValue": objective_value,
        "trainingSpecFingerprint": result.get("trainingSpecFingerprint"),
        "trainingDatasetFingerprint": result.get("trainingDatasetFingerprint"),
        "validationDatasetFingerprint": result.get("validationDatasetFingerprint"),
        "trainedModelSpecFingerprint": result.get("trainedModelSpecFingerprint"),
        "checkpointArtifactFingerprint": result.get("checkpointArtifactFingerprint"),
        "device": _current_device_name(),
        "trainingRun": training_run_for_artifact,
        "trainedModelSpec": result.get("trainedModelSpec"),
        "checkpointArtifact": result.get("checkpointArtifact"),
        "bounded": True,
        "arbitraryCodeExecution": False,
    }
    base_for_fp = {k: v for k, v in artifact.items() if k not in {"trialId"}}
    fp = _canonical_sha256(base_for_fp)
    artifact["artifactFingerprint"] = fp
    artifact["trialId"] = "ntr_" + fp[:24]
    return {"kind": "neural-trial-result", "trialArtifact": artifact, "trialArtifactFingerprint": fp, "objectiveValue": objective_value}


def _validate_trial_artifact(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != NEURAL_TRIAL_SCHEMA or value.get("kind") != "neural-trial":
        raise HTTPException(status_code=400, detail="trialArtifact must use the governed neural trial schema")
    fp = str(value.get("artifactFingerprint") or "")
    base = {k: v for k, v in value.items() if k not in {"artifactFingerprint", "trialId"}}
    if not fp or not hmac.compare_digest(fp, _canonical_sha256(base)):
        raise HTTPException(status_code=400, detail="trialArtifact fingerprint verification failed")
    if value.get("trialId") != "ntr_" + fp[:24]:
        raise HTTPException(status_code=400, detail="trialArtifact identifier does not match its fingerprint")
    return value


def _rank_trials(trials: list[dict[str, Any]], objective: dict[str, Any]) -> list[dict[str, Any]]:
    reverse = objective["direction"] == "maximize"
    return sorted(trials, key=lambda t: (float(t["objectiveValue"]), str(t["trialId"])), reverse=reverse)


def _batch_from_params(payload: dict[str, Any], parameter_sets: list[dict[str, Any]], *, kind: str, search_space_fingerprint: str | None = None) -> dict[str, Any]:
    if not parameter_sets or len(parameter_sets) > MAX_NEURAL_BATCH_TRIALS:
        raise HTTPException(status_code=413, detail="trial batch size is outside the bounded range")
    base_seed = int(payload.get("seed", 42))
    # Validate all specs and total epoch budget before executing any training.
    total_epochs = 0
    normalized_specs: list[dict[str, Any]] = []
    for params in parameter_sets:
        tp = dict(payload); tp["trainingSpec"] = _apply_hyperparameters(payload.get("trainingSpec"), params)
        spec = _normalized_training_spec(tp)
        total_epochs += int(spec["epochs"])
        normalized_specs.append(spec)
    if total_epochs > MAX_NEURAL_SEARCH_EPOCHS:
        raise HTTPException(status_code=413, detail="trial batch total epoch budget exceeds the bounded limit")
    objective = _trial_objective(payload, normalized_specs[0])
    trials: list[dict[str, Any]] = []
    for index, params in enumerate(parameter_sets):
        res = _execute_trial(payload, trial_index=index, inherited_hyperparameters=params, inherited_seed=base_seed + index)
        trials.append(res["trialArtifact"])
    ranked = _rank_trials(trials, objective)
    best = ranked[0]
    artifact = {
        "schema": NEURAL_BATCH_SCHEMA if kind == "batch" else NEURAL_SEARCH_SCHEMA,
        "kind": "neural-trial-batch" if kind == "batch" else "neural-hyperparameter-search",
        "searchKind": None if kind == "batch" else kind,
        "trialCount": len(trials),
        "totalEpochBudget": total_epochs,
        "baseSeed": base_seed,
        "objective": objective,
        "trialArtifactFingerprints": [t["artifactFingerprint"] for t in trials],
        "trials": [{
            "trialId": t["trialId"], "trialIndex": t["trialIndex"], "seed": t["seed"],
            "hyperparameters": t["hyperparameters"], "hyperparametersFingerprint": t["hyperparametersFingerprint"],
            "objectiveValue": t["objectiveValue"], "trainingSpecFingerprint": t["trainingSpecFingerprint"],
            "trainingDatasetFingerprint": t["trainingDatasetFingerprint"],
            "validationDatasetFingerprint": t.get("validationDatasetFingerprint"),
            "trainedModelSpecFingerprint": t["trainedModelSpecFingerprint"],
            "checkpointArtifactFingerprint": t["checkpointArtifactFingerprint"],
            "artifactFingerprint": t["artifactFingerprint"], "device": t["device"],
            "trainingMetrics": ((t.get("trainingRun") or {}).get("trainingMetrics")),
            "validationMetrics": ((t.get("trainingRun") or {}).get("validationMetrics")),
        } for t in trials],
        "ranking": [{"rank": i + 1, "trialId": t["trialId"], "objectiveValue": t["objectiveValue"], "hyperparameters": t["hyperparameters"]} for i, t in enumerate(ranked)],
        "bestTrialId": best["trialId"],
        "bestTrialArtifactFingerprint": best["artifactFingerprint"],
        "bestObjectiveValue": best["objectiveValue"],
        "searchSpaceFingerprint": search_space_fingerprint,
        "device": _current_device_name(),
        "bounded": True,
        "arbitraryCodeExecution": False,
    }
    fp = _canonical_sha256(artifact)
    artifact["artifactFingerprint"] = fp
    artifact["artifactId"] = ("ntb_" if kind == "batch" else "nhs_") + fp[:24]
    return {"kind": "neural-batch-result" if kind == "batch" else "neural-hyperparameter-search-result", "batchArtifact" if kind == "batch" else "searchArtifact": artifact, "artifactFingerprint": fp, "bestTrial": best}


def _batch_execute(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("trials")
    if not isinstance(raw, list):
        raise HTTPException(status_code=400, detail="trials must be an array of hyperparameter objects")
    params = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail=f"trials[{i}] must be an object")
        params.append(item)
    return _batch_from_params(payload, params, kind="batch")


def _grid_parameter_sets(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    grid = payload.get("parameterGrid")
    if not isinstance(grid, dict) or not grid:
        raise HTTPException(status_code=400, detail="parameterGrid must be a non-empty object")
    unknown = sorted(set(grid) - ALLOWED_HYPERPARAMETER_PATHS)
    if unknown:
        raise HTTPException(status_code=400, detail="unsupported hyperparameter path(s): " + ", ".join(unknown))
    keys = sorted(grid)
    values: list[list[Any]] = []
    combinations = 1
    for key in keys:
        vals = grid[key]
        if not isinstance(vals, list) or not vals or len(vals) > MAX_NEURAL_SEARCH_VALUES:
            raise HTTPException(status_code=413, detail=f"parameterGrid.{key} value count is outside the bounded range")
        combinations *= len(vals)
        if combinations > MAX_NEURAL_BATCH_TRIALS:
            raise HTTPException(status_code=413, detail="grid search expands beyond the bounded trial limit")
        values.append(vals)
    out: list[dict[str, Any]] = []
    def build(i: int, row: dict[str, Any]) -> None:
        if i == len(keys): out.append(dict(row)); return
        for v in values[i]: row[keys[i]] = v; build(i + 1, row)
    build(0, {})
    return out, _canonical_sha256(grid)


def _hyperparameter_grid(payload: dict[str, Any]) -> dict[str, Any]:
    params, fp = _grid_parameter_sets(payload)
    return _batch_from_params(payload, params, kind="grid", search_space_fingerprint=fp)


def _random_parameter_sets(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    space = payload.get("searchSpace")
    if not isinstance(space, dict) or not space:
        raise HTTPException(status_code=400, detail="searchSpace must be a non-empty object")
    unknown = sorted(set(space) - ALLOWED_HYPERPARAMETER_PATHS)
    if unknown:
        raise HTTPException(status_code=400, detail="unsupported hyperparameter path(s): " + ", ".join(unknown))
    trials = _positive_int(payload.get("trialCount", min(8, MAX_NEURAL_BATCH_TRIALS)), name="trialCount", minimum=1, maximum=MAX_NEURAL_BATCH_TRIALS)
    rng = np.random.default_rng(int(payload.get("seed", 42)))
    out: list[dict[str, Any]] = []
    for _ in range(trials):
        row: dict[str, Any] = {}
        for key in sorted(space):
            spec = space[key]
            if not isinstance(spec, dict):
                raise HTTPException(status_code=400, detail=f"searchSpace.{key} must be an object")
            kind = str(spec.get("type") or "choice").strip().lower()
            if kind == "choice":
                vals = spec.get("values")
                if not isinstance(vals, list) or not vals or len(vals) > MAX_NEURAL_SEARCH_VALUES:
                    raise HTTPException(status_code=413, detail=f"searchSpace.{key}.values count is outside the bounded range")
                row[key] = _copy_json(vals[int(rng.integers(0, len(vals)))])
            elif kind == "uniform":
                low = _finite_float(spec.get("low"), name=f"searchSpace.{key}.low")
                high = _finite_float(spec.get("high"), name=f"searchSpace.{key}.high")
                if not high > low: raise HTTPException(status_code=400, detail=f"searchSpace.{key} high must exceed low")
                row[key] = float(rng.uniform(low, high))
            elif kind == "loguniform":
                low = _finite_float(spec.get("low"), name=f"searchSpace.{key}.low", minimum=1e-12)
                high = _finite_float(spec.get("high"), name=f"searchSpace.{key}.high", minimum=1e-12)
                if not high > low: raise HTTPException(status_code=400, detail=f"searchSpace.{key} high must exceed low")
                row[key] = float(math.exp(rng.uniform(math.log(low), math.log(high))))
            elif kind == "integer":
                low = _positive_int(spec.get("low"), name=f"searchSpace.{key}.low", minimum=1, maximum=MAX_TRAINING_EPOCHS if key=="epochs" else MAX_BATCH)
                high = _positive_int(spec.get("high"), name=f"searchSpace.{key}.high", minimum=low, maximum=MAX_TRAINING_EPOCHS if key=="epochs" else MAX_BATCH)
                row[key] = int(rng.integers(low, high + 1))
            else:
                raise HTTPException(status_code=400, detail=f"searchSpace.{key}.type is not registered")
        out.append(row)
    return out, _canonical_sha256(space)


def _hyperparameter_random(payload: dict[str, Any]) -> dict[str, Any]:
    params, fp = _random_parameter_sets(payload)
    return _batch_from_params(payload, params, kind="random", search_space_fingerprint=fp)


EVALUATION_ARTIFACT_SCHEMA = "sc-workspace-neural-evaluation-artifact/1.0"
CALIBRATION_ARTIFACT_SCHEMA = "sc-workspace-neural-calibration-artifact/1.0"
UNCERTAINTY_ARTIFACT_SCHEMA = "sc-workspace-neural-uncertainty-artifact/1.0"
MAX_EVALUATION_ROWS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_EVALUATION_ROWS", "16384")), 50000))
MAX_CALIBRATION_BINS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_CALIBRATION_BINS", "20")), 50))
DEFAULT_CALIBRATION_BINS = 10

EXPLAINABILITY_ARTIFACT_SCHEMA = "sc-workspace-neural-explainability-artifact/1.0"
MAX_EXPLAINABILITY_ROWS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_EXPLAINABILITY_ROWS", "128")), 1024))
MAX_EXPLAINABILITY_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_EXPLAINABILITY_FEATURES", "256")), 4096))
MAX_INTEGRATED_GRADIENT_STEPS = max(8, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_IG_STEPS", "64")), 256))
DEFAULT_INTEGRATED_GRADIENT_STEPS = 32



def _analysis_source(payload: dict[str, Any]) -> tuple[dict[str, Any], str, str | None]:
    spec = payload.get("modelSpec")
    summary = _validate_model_spec(spec)
    model_fp = _canonical_sha256(spec)
    checkpoint_fp = None
    checkpoint = payload.get("checkpointArtifact")
    if checkpoint is not None:
        checkpoint, _ = _validate_checkpoint_artifact(checkpoint, decode_state=False)
        if checkpoint.get("trainedModelSpecFingerprint") != model_fp:
            raise HTTPException(status_code=400, detail="modelSpec fingerprint does not match checkpoint trained model fingerprint")
        checkpoint_fp = str(checkpoint.get("artifactFingerprint") or "")
    return summary, model_fp, checkpoint_fp


def _analysis_logits(payload: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any], str, str | None, str]:
    summary, model_fp, checkpoint_fp = _analysis_source(payload)
    features = _tensor(payload.get("features"), name="features", dtype_name="float32", ndim=2)
    if int(features.shape[0]) < 2 or int(features.shape[0]) > MAX_EVALUATION_ROWS:
        raise HTTPException(status_code=413, detail="evaluation row count is outside the bounded range")
    if int(features.shape[1]) != int(summary["inputFeatures"]):
        raise HTTPException(status_code=400, detail="features width does not match model specification")
    spec = payload.get("modelSpec")
    if summary["modelType"] == "linear":
        weights, bias, activation, _ = _linear_spec(spec, layer_name="modelSpec")
        logits = F.linear(features, weights, bias)
        if activation not in {"identity", "sigmoid", "softmax"}:
            logits = _activation(logits, activation)
    else:
        x = features
        for index, layer in enumerate(spec["layers"]):
            weights, bias, activation, _ = _linear_spec(layer, layer_name=f"modelSpec.layers[{index}]")
            raw = F.linear(x, weights, bias)
            x = raw if index == len(spec["layers"]) - 1 else _activation(raw, activation)
        logits = x
    dataset_fp = _canonical_sha256({"features": payload.get("features"), "targets": payload.get("targets")})
    return features, logits, summary, model_fp, checkpoint_fp, dataset_fp


def _binary_targets(value: Any, rows: int) -> torch.Tensor:
    y = _tensor(value, name="targets", dtype_name="float32")
    if y.ndim == 1: y = y.reshape(-1, 1)
    if y.ndim != 2 or int(y.shape[1]) != 1 or int(y.shape[0]) != rows:
        raise HTTPException(status_code=400, detail="binary targets must be [rows] or [rows,1]")
    if bool(((y < 0) | (y > 1)).any()):
        raise HTTPException(status_code=400, detail="binary targets must be in [0,1]")
    return y


def _multiclass_targets(value: Any, rows: int, classes: int) -> torch.Tensor:
    y = _tensor(value, name="targets", dtype_name="int64")
    if y.ndim == 2 and int(y.shape[1]) == 1: y = y.reshape(-1)
    if y.ndim != 1 or int(y.shape[0]) != rows:
        raise HTTPException(status_code=400, detail="multiclass targets must be rank 1 with one label per row")
    if y.numel() and (int(y.min().item()) < 0 or int(y.max().item()) >= classes):
        raise HTTPException(status_code=400, detail="multiclass target is outside the model class range")
    return y


def _artifact(schema: str, kind: str, body: dict[str, Any]) -> dict[str, Any]:
    doc = {"schema": schema, "kind": kind, **body}
    fp = _canonical_sha256(doc)
    doc["artifactFingerprint"] = fp
    doc["artifactId"] = "nea_" + fp[:24]
    return doc


def _roc_auc_binary(prob: torch.Tensor, y: torch.Tensor) -> float | None:
    pairs = [(float(p), int(t)) for p, t in zip(prob.reshape(-1).tolist(), y.reshape(-1).tolist())]
    pos = sum(t for _, t in pairs); neg = len(pairs) - pos
    if pos == 0 or neg == 0: return None
    ordered = sorted(enumerate(pairs), key=lambda x: x[1][0])
    ranks = [0.0] * len(pairs); i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1][0] == ordered[i][1][0]: j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j): ranks[ordered[k][0]] = avg
        i = j
    rank_sum_pos = sum(r for r, (_, t) in zip(ranks, pairs) if t == 1)
    return float((rank_sum_pos - pos * (pos + 1) / 2.0) / (pos * neg))


def _evaluate_regression(payload: dict[str, Any]) -> dict[str, Any]:
    features, pred, summary, model_fp, checkpoint_fp, dataset_fp = _analysis_logits(payload)
    y = _tensor(payload.get("targets"), name="targets", dtype_name="float32")
    if y.ndim == 1: y = y.reshape(-1, 1)
    if y.ndim != 2 or list(y.shape) != list(pred.shape):
        raise HTTPException(status_code=400, detail="regression targets shape must match model outputs")
    residual = pred - y
    mse = float(torch.mean(residual * residual).item())
    mae = float(torch.mean(torch.abs(residual)).item())
    rmse = math.sqrt(mse)
    denom = float(torch.sum((y - torch.mean(y)) ** 2).item())
    r2 = None if denom == 0 else float(1.0 - float(torch.sum(residual * residual).item()) / denom)
    metrics = {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}
    artifact = _artifact(EVALUATION_ARTIFACT_SCHEMA, "neural-evaluation", {
        "task":"regression","operation":"workspace.neural.evaluate-regression","modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp,
        "rows":int(features.shape[0]),"metrics":metrics,
    })
    return {"kind":"neural-evaluation-result","task":"regression","metrics":metrics,"analysisArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp}


def _binary_eval_core(payload: dict[str, Any]) -> tuple[dict[str, Any], torch.Tensor, torch.Tensor, dict[str, Any], str, str | None, str]:
    features, logits, summary, model_fp, checkpoint_fp, dataset_fp = _analysis_logits(payload)
    if int(logits.shape[1]) != 1:
        raise HTTPException(status_code=400, detail="binary evaluation requires one model output")
    y = _binary_targets(payload.get("targets"), int(features.shape[0]))
    prob = torch.sigmoid(logits)
    pred = (prob >= 0.5).to(torch.int64); yi = y.to(torch.int64)
    tp=int(((pred==1)&(yi==1)).sum().item()); tn=int(((pred==0)&(yi==0)).sum().item())
    fp=int(((pred==1)&(yi==0)).sum().item()); fn=int(((pred==0)&(yi==1)).sum().item())
    eps=1e-7
    logloss=float(-(y*torch.log(prob.clamp(eps,1-eps))+(1-y)*torch.log((1-prob).clamp(eps,1-eps))).mean().item())
    precision=tp/(tp+fp) if tp+fp else 0.0; recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    metrics={"accuracy":float((pred==yi).to(torch.float32).mean().item()),"logLoss":logloss,
             "brierScore":float(torch.mean((prob-y)**2).item()),"precision":precision,"recall":recall,"f1":f1,
             "rocAuc":_roc_auc_binary(prob,y),"confusionMatrix":{"tn":tn,"fp":fp,"fn":fn,"tp":tp}}
    return metrics, prob, y, summary, model_fp, checkpoint_fp, dataset_fp


def _evaluate_binary(payload: dict[str, Any]) -> dict[str, Any]:
    metrics, prob, y, summary, model_fp, checkpoint_fp, dataset_fp = _binary_eval_core(payload)
    artifact=_artifact(EVALUATION_ARTIFACT_SCHEMA,"neural-evaluation",{
        "task":"binary-classification","operation":"workspace.neural.evaluate-binary","modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp,
        "rows":int(y.shape[0]),"metrics":metrics})
    return {"kind":"neural-evaluation-result","task":"binary-classification","metrics":metrics,"analysisArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp}


def _multiclass_eval_core(payload: dict[str, Any]) -> tuple[dict[str, Any], torch.Tensor, torch.Tensor, dict[str, Any], str, str | None, str]:
    features, logits, summary, model_fp, checkpoint_fp, dataset_fp = _analysis_logits(payload)
    classes=int(logits.shape[1])
    if classes < 2: raise HTTPException(status_code=400, detail="multiclass evaluation requires at least two outputs")
    y=_multiclass_targets(payload.get("targets"),int(features.shape[0]),classes)
    prob=torch.softmax(logits,dim=1); pred=torch.argmax(prob,dim=1); eps=1e-7
    logloss=float(-torch.log(prob[torch.arange(len(y)),y].clamp(eps,1.0)).mean().item())
    onehot=F.one_hot(y,num_classes=classes).to(torch.float32)
    confusion=[]
    for c in range(classes):
        row=[]
        for d in range(classes): row.append(int(((y==c)&(pred==d)).sum().item()))
        confusion.append(row)
    ps=[]; rs=[]; f1s=[]
    for c in range(classes):
        tp=confusion[c][c]; fp=sum(confusion[r][c] for r in range(classes) if r!=c); fn=sum(confusion[c][d] for d in range(classes) if d!=c)
        pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0; ff=2*pr*rc/(pr+rc) if pr+rc else 0.0
        ps.append(pr); rs.append(rc); f1s.append(ff)
    metrics={"accuracy":float((pred==y).to(torch.float32).mean().item()),"logLoss":logloss,
             "brierScore":float(torch.mean(torch.sum((prob-onehot)**2,dim=1)).item()),
             "macroPrecision":sum(ps)/classes,"macroRecall":sum(rs)/classes,"macroF1":sum(f1s)/classes,"confusionMatrix":confusion}
    return metrics,prob,y,summary,model_fp,checkpoint_fp,dataset_fp


def _evaluate_multiclass(payload: dict[str, Any]) -> dict[str, Any]:
    metrics, prob, y, summary, model_fp, checkpoint_fp, dataset_fp=_multiclass_eval_core(payload)
    artifact=_artifact(EVALUATION_ARTIFACT_SCHEMA,"neural-evaluation",{
        "task":"multiclass-classification","operation":"workspace.neural.evaluate-multiclass","modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp,
        "rows":int(y.shape[0]),"classes":int(prob.shape[1]),"metrics":metrics})
    return {"kind":"neural-evaluation-result","task":"multiclass-classification","metrics":metrics,"analysisArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp}


def _calibration_report(payload: dict[str, Any]) -> dict[str, Any]:
    task=str(payload.get("task") or "binary-classification").strip().lower()
    bins=int(payload.get("bins") or DEFAULT_CALIBRATION_BINS)
    if bins < 2 or bins > MAX_CALIBRATION_BINS: raise HTTPException(status_code=400, detail="bins is outside the supported calibration range")
    if task=="binary-classification":
        _, prob, y, summary, model_fp, checkpoint_fp, dataset_fp=_binary_eval_core(payload)
        confidence=prob.reshape(-1); correct=y.reshape(-1)
    elif task=="multiclass-classification":
        _, prob, y, summary, model_fp, checkpoint_fp, dataset_fp=_multiclass_eval_core(payload)
        confidence,pred=torch.max(prob,dim=1); correct=(pred==y).to(torch.float32)
    else: raise HTTPException(status_code=400, detail="calibration-report supports classification tasks only")
    rows=[]; n=int(confidence.numel()); ece=0.0; mce=0.0
    for i in range(bins):
        lo=i/bins; hi=(i+1)/bins
        mask=(confidence>=lo)&(confidence<=hi if i==bins-1 else confidence<hi)
        count=int(mask.sum().item())
        if count:
            ac=float(confidence[mask].mean().item()); aa=float(correct[mask].mean().item()); gap=abs(ac-aa)
            ece += (count/n)*gap; mce=max(mce,gap)
        else: ac=aa=gap=None
        rows.append({"bin":i,"lower":lo,"upper":hi,"count":count,"averageConfidence":ac,"empiricalAccuracy":aa,"absoluteGap":gap})
    metrics={"expectedCalibrationError":ece,"maximumCalibrationError":mce,"binCount":bins,"strategy":"uniform"}
    artifact=_artifact(CALIBRATION_ARTIFACT_SCHEMA,"neural-calibration",{
        "task":task,"operation":"workspace.neural.calibration-report","modelType":summary["modelType"],"modelSpecFingerprint":model_fp,
        "checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp,"metrics":metrics,"bins":rows})
    return {"kind":"neural-calibration-result","task":task,"metrics":metrics,"bins":rows,"analysisArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp}


def _uncertainty_summary(payload: dict[str, Any]) -> dict[str, Any]:
    task=str(payload.get("task") or "binary-classification").strip().lower()
    threshold=float(payload.get("confidenceThreshold") or 0.6)
    if not 0.0 < threshold < 1.0: raise HTTPException(status_code=400, detail="confidenceThreshold must be in (0,1)")
    if task=="binary-classification":
        _, prob, y, summary, model_fp, checkpoint_fp, dataset_fp=_binary_eval_core(payload)
        p=torch.cat([1-prob,prob],dim=1); confidence=torch.max(p,dim=1).values
        entropy=-(p.clamp(1e-7,1.0)*torch.log(p.clamp(1e-7,1.0))).sum(dim=1); max_entropy=math.log(2.0)
        margin=torch.abs(prob.reshape(-1)-0.5)*2.0
        details={"meanPredictiveEntropy":float(entropy.mean().item()),"meanNormalizedEntropy":float((entropy/max_entropy).mean().item()),
                 "meanConfidence":float(confidence.mean().item()),"meanMargin":float(margin.mean().item()),
                 "lowConfidenceCount":int((confidence<threshold).sum().item()),"confidenceThreshold":threshold}
        method="predictive-entropy"
    elif task=="multiclass-classification":
        _, prob, y, summary, model_fp, checkpoint_fp, dataset_fp=_multiclass_eval_core(payload)
        confidence,top=torch.max(prob,dim=1); sortedp=torch.sort(prob,dim=1,descending=True).values
        entropy=-(prob.clamp(1e-7,1.0)*torch.log(prob.clamp(1e-7,1.0))).sum(dim=1); max_entropy=math.log(float(prob.shape[1]))
        details={"meanPredictiveEntropy":float(entropy.mean().item()),"meanNormalizedEntropy":float((entropy/max_entropy).mean().item()),
                 "meanConfidence":float(confidence.mean().item()),"meanMargin":float((sortedp[:,0]-sortedp[:,1]).mean().item()),
                 "lowConfidenceCount":int((confidence<threshold).sum().item()),"confidenceThreshold":threshold}
        method="predictive-entropy"
    elif task=="regression":
        features,pred,summary,model_fp,checkpoint_fp,dataset_fp=_analysis_logits(payload)
        y=_tensor(payload.get("targets"),name="targets",dtype_name="float32")
        if y.ndim==1:y=y.reshape(-1,1)
        if list(y.shape)!=list(pred.shape):raise HTTPException(status_code=400,detail="regression targets shape must match model outputs")
        residual=(pred-y).reshape(-1); q=torch.quantile(residual,torch.tensor([0.05,0.5,0.95]))
        details={"method":"empirical-residual","residualStd":float(torch.std(residual,unbiased=False).item()),"residualMean":float(residual.mean().item()),
                 "residualQuantiles":{"p05":float(q[0].item()),"p50":float(q[1].item()),"p95":float(q[2].item())},
                 "rmse":float(torch.sqrt(torch.mean(residual*residual)).item())}; method="empirical-residual"
    else: raise HTTPException(status_code=400, detail="uncertainty task is not registered")
    artifact=_artifact(UNCERTAINTY_ARTIFACT_SCHEMA,"neural-uncertainty",{
        "task":task,"operation":"workspace.neural.uncertainty-summary","modelType":summary["modelType"],"modelSpecFingerprint":model_fp,
        "checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp,"method":method,"summary":details})
    return {"kind":"neural-uncertainty-result","task":task,"method":method,"summary":details,"analysisArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"evaluationDatasetFingerprint":dataset_fp}


def _explain_forward(spec: dict[str, Any], summary: dict[str, Any], features: torch.Tensor) -> torch.Tensor:
    """Differentiable raw model output for bounded explainability methods."""
    if summary["modelType"] == "linear":
        weights, bias, activation, _ = _linear_spec(spec, layer_name="modelSpec")
        raw = F.linear(features, weights, bias)
        if activation not in {"identity", "sigmoid", "softmax"}:
            raw = _activation(raw, activation)
        return raw
    x = features
    for index, layer in enumerate(spec["layers"]):
        weights, bias, activation, _ = _linear_spec(layer, layer_name=f"modelSpec.layers[{index}]")
        raw = F.linear(x, weights, bias)
        x = raw if index == len(spec["layers"]) - 1 else _activation(raw, activation)
    return x


def _explainability_context(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], torch.Tensor, str, str | None, str, list[str]]:
    summary, model_fp, checkpoint_fp = _analysis_source(payload)
    features = _tensor(payload.get("features"), name="features", dtype_name="float32", ndim=2)
    rows, width = int(features.shape[0]), int(features.shape[1])
    if rows < 1 or rows > MAX_EXPLAINABILITY_ROWS:
        raise HTTPException(status_code=413, detail="explainability row count is outside the bounded range")
    if width != int(summary["inputFeatures"]):
        raise HTTPException(status_code=400, detail="features width does not match model specification")
    if width > MAX_EXPLAINABILITY_FEATURES:
        raise HTTPException(status_code=413, detail="explainability feature count exceeds the bounded limit")
    names = payload.get("featureNames")
    if names is None:
        names = [f"feature_{i}" for i in range(width)]
    if not isinstance(names, list) or len(names) != width or any(not isinstance(x, str) or not x.strip() for x in names):
        raise HTTPException(status_code=400, detail="featureNames must contain one non-empty string per input feature")
    names = [x.strip()[:160] for x in names]
    dataset_fp = _canonical_sha256({"features": payload.get("features"), "featureNames": names})
    return payload.get("modelSpec"), summary, features, model_fp, checkpoint_fp, dataset_fp, names


def _score_for_explanation(raw: torch.Tensor, task: str, target_index: int | None = None, fixed_targets: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor, str]:
    if raw.ndim != 2:
        raise HTTPException(status_code=400, detail="model output must be rank 2 for explainability")
    rows, outputs = int(raw.shape[0]), int(raw.shape[1])
    if task == "regression":
        idx = 0 if target_index is None else int(target_index)
        if idx < 0 or idx >= outputs:
            raise HTTPException(status_code=400, detail="targetIndex is outside regression output range")
        targets = torch.full((rows,), idx, dtype=torch.long)
        return raw[:, idx], targets, "raw-output"
    if task == "binary-classification":
        if outputs != 1:
            raise HTTPException(status_code=400, detail="binary explainability requires one model output")
        targets = torch.ones(rows, dtype=torch.long)
        return torch.sigmoid(raw[:, 0]), targets, "positive-class-probability"
    if task == "multiclass-classification":
        if outputs < 2:
            raise HTTPException(status_code=400, detail="multiclass explainability requires at least two model outputs")
        probs = torch.softmax(raw, dim=1)
        if fixed_targets is not None:
            targets = fixed_targets.to(dtype=torch.long)
        elif target_index is None:
            targets = torch.argmax(probs.detach(), dim=1)
        else:
            idx = int(target_index)
            if idx < 0 or idx >= outputs:
                raise HTTPException(status_code=400, detail="targetIndex is outside multiclass output range")
            targets = torch.full((rows,), idx, dtype=torch.long)
        score = probs.gather(1, targets.reshape(-1,1)).reshape(-1)
        return score, targets, "selected-class-probability"
    raise HTTPException(status_code=400, detail="explainability task is not registered")


def _explain_task(payload: dict[str, Any]) -> str:
    task = str(payload.get("task") or "").strip()
    if task not in {"regression", "binary-classification", "multiclass-classification"}:
        raise HTTPException(status_code=400, detail="task must be regression, binary-classification, or multiclass-classification")
    return task


def _target_index(payload: dict[str, Any]) -> int | None:
    value = payload.get("targetIndex")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise HTTPException(status_code=400, detail="targetIndex must be an integer")
    return value


def _baseline_tensor(payload: dict[str, Any], features: torch.Tensor) -> torch.Tensor:
    baseline = payload.get("baseline")
    if baseline is None:
        return torch.zeros_like(features)
    b = _tensor(baseline, name="baseline", dtype_name="float32")
    if b.ndim == 1:
        if int(b.shape[0]) != int(features.shape[1]):
            raise HTTPException(status_code=400, detail="baseline vector width must match features")
        return b.reshape(1,-1).repeat(int(features.shape[0]),1)
    if b.ndim == 2 and list(b.shape) == list(features.shape):
        return b
    raise HTTPException(status_code=400, detail="baseline must be a feature vector or match the feature matrix")


def _feature_summary(attributions: torch.Tensor, names: list[str]) -> list[dict[str, Any]]:
    abs_attr = torch.abs(attributions)
    mean_abs = torch.mean(abs_attr, dim=0)
    signed = torch.mean(attributions, dim=0)
    order = torch.argsort(mean_abs, descending=True).tolist()
    return [{"featureIndex":int(i),"featureName":names[i],"meanAbsoluteAttribution":float(mean_abs[i].item()),"meanSignedAttribution":float(signed[i].item())} for i in order]


def _explain_artifact(operation: str, method: str, task: str, summary: dict[str, Any], model_fp: str, checkpoint_fp: str | None, dataset_fp: str, names: list[str], target_mode: str, targets: torch.Tensor, parameters: dict[str, Any], attributions: torch.Tensor, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    body = {
        "task":task,"operation":operation,"method":method,"modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,
        "explanationDatasetFingerprint":dataset_fp,"rows":int(attributions.shape[0]),"features":int(attributions.shape[1]),
        "featureNames":names,"targetSelection":{"mode":target_mode,"selectedTargets":[int(x) for x in targets.tolist()]},
        "parameters":parameters,"featureSummary":_feature_summary(attributions,names),
        "attributions":[[float(v) for v in row] for row in attributions.tolist()],
    }
    if extra: body.update(extra)
    return _artifact(EXPLAINABILITY_ARTIFACT_SCHEMA,"neural-explainability",body)


def _explain_gradient(payload: dict[str, Any]) -> dict[str, Any]:
    spec, summary, features, model_fp, checkpoint_fp, dataset_fp, names = _explainability_context(payload)
    task = _explain_task(payload); target_index = _target_index(payload)
    x = features.detach().clone().requires_grad_(True)
    raw = _explain_forward(spec, summary, x)
    score, targets, target_mode = _score_for_explanation(raw, task, target_index)
    grad = torch.autograd.grad(score.sum(), x, create_graph=False, retain_graph=False)[0].detach()
    artifact = _explain_artifact("workspace.neural.explain-gradient","input-gradient",task,summary,model_fp,checkpoint_fp,dataset_fp,names,target_mode,targets,{"absoluteSummary":True},grad)
    return {"kind":"neural-explainability-result","task":task,"method":"input-gradient","attributions":artifact["attributions"],"featureSummary":artifact["featureSummary"],"explainabilityArtifact":artifact,"modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"explanationDatasetFingerprint":dataset_fp}


def _explain_integrated_gradients(payload: dict[str, Any]) -> dict[str, Any]:
    spec, summary, features, model_fp, checkpoint_fp, dataset_fp, names = _explainability_context(payload)
    task = _explain_task(payload); target_index = _target_index(payload)
    steps = payload.get("steps", DEFAULT_INTEGRATED_GRADIENT_STEPS)
    if isinstance(steps,bool) or not isinstance(steps,int) or steps < 8 or steps > MAX_INTEGRATED_GRADIENT_STEPS:
        raise HTTPException(status_code=400, detail="steps is outside the bounded integrated-gradients range")
    baseline = _baseline_tensor(payload, features)
    with torch.no_grad():
        raw0 = _explain_forward(spec, summary, features)
        score0, fixed_targets, target_mode = _score_for_explanation(raw0, task, target_index)
        base_raw = _explain_forward(spec, summary, baseline)
        base_score, _, _ = _score_for_explanation(base_raw, task, target_index, fixed_targets=fixed_targets)
    total_grad = torch.zeros_like(features)
    for step in range(1, steps + 1):
        alpha = float(step) / float(steps)
        x = (baseline + alpha * (features - baseline)).detach().requires_grad_(True)
        raw = _explain_forward(spec, summary, x)
        score, _, _ = _score_for_explanation(raw, task, target_index, fixed_targets=fixed_targets)
        total_grad += torch.autograd.grad(score.sum(), x, create_graph=False, retain_graph=False)[0].detach()
    attr = (features - baseline) * (total_grad / float(steps))
    completeness = score0 - base_score - torch.sum(attr, dim=1)
    artifact = _explain_artifact("workspace.neural.explain-integrated-gradients","integrated-gradients",task,summary,model_fp,checkpoint_fp,dataset_fp,names,target_mode,fixed_targets,{"steps":steps,"baseline":"user-supplied" if payload.get("baseline") is not None else "zeros"},attr,{"completenessDelta":[float(v) for v in completeness.tolist()],"meanAbsoluteCompletenessDelta":float(torch.mean(torch.abs(completeness)).item())})
    return {"kind":"neural-explainability-result","task":task,"method":"integrated-gradients","attributions":artifact["attributions"],"featureSummary":artifact["featureSummary"],"completenessDelta":artifact["completenessDelta"],"explainabilityArtifact":artifact,"modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"explanationDatasetFingerprint":dataset_fp}


def _explain_occlusion(payload: dict[str, Any]) -> dict[str, Any]:
    spec, summary, features, model_fp, checkpoint_fp, dataset_fp, names = _explainability_context(payload)
    task = _explain_task(payload); target_index = _target_index(payload)
    baseline = _baseline_tensor(payload, features)
    with torch.no_grad():
        raw = _explain_forward(spec, summary, features)
        score, fixed_targets, target_mode = _score_for_explanation(raw, task, target_index)
        attr = torch.zeros_like(features)
        for col in range(int(features.shape[1])):
            occluded = features.clone(); occluded[:,col] = baseline[:,col]
            occ_raw = _explain_forward(spec, summary, occluded)
            occ_score, _, _ = _score_for_explanation(occ_raw, task, target_index, fixed_targets=fixed_targets)
            attr[:,col] = score - occ_score
    artifact = _explain_artifact("workspace.neural.explain-occlusion","feature-occlusion",task,summary,model_fp,checkpoint_fp,dataset_fp,names,target_mode,fixed_targets,{"baseline":"user-supplied" if payload.get("baseline") is not None else "zeros"},attr)
    return {"kind":"neural-explainability-result","task":task,"method":"feature-occlusion","attributions":artifact["attributions"],"featureSummary":artifact["featureSummary"],"explainabilityArtifact":artifact,"modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"explanationDatasetFingerprint":dataset_fp}


def _explain_global_sensitivity(payload: dict[str, Any]) -> dict[str, Any]:
    spec, summary, features, model_fp, checkpoint_fp, dataset_fp, names = _explainability_context(payload)
    task = _explain_task(payload); target_index = _target_index(payload)
    x = features.detach().clone().requires_grad_(True)
    raw = _explain_forward(spec, summary, x)
    score, targets, target_mode = _score_for_explanation(raw, task, target_index)
    grad = torch.autograd.grad(score.sum(), x, create_graph=False, retain_graph=False)[0].detach()
    abs_grad = torch.abs(grad); mean_abs = torch.mean(abs_grad,dim=0); rms = torch.sqrt(torch.mean(grad*grad,dim=0)); max_abs=torch.max(abs_grad,dim=0).values
    order=torch.argsort(mean_abs,descending=True).tolist()
    sensitivity=[{"featureIndex":int(i),"featureName":names[i],"meanAbsoluteGradient":float(mean_abs[i].item()),"rmsGradient":float(rms[i].item()),"maxAbsoluteGradient":float(max_abs[i].item())} for i in order]
    artifact = _artifact(EXPLAINABILITY_ARTIFACT_SCHEMA,"neural-explainability",{
        "task":task,"operation":"workspace.neural.explain-global-sensitivity","method":"global-gradient-sensitivity","modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"explanationDatasetFingerprint":dataset_fp,
        "rows":int(features.shape[0]),"features":int(features.shape[1]),"featureNames":names,
        "targetSelection":{"mode":target_mode,"selectedTargets":[int(x) for x in targets.tolist()]},
        "parameters":{"aggregation":"mean-absolute/rms/max-absolute-gradient"},"sensitivity":sensitivity,
    })
    return {"kind":"neural-explainability-result","task":task,"method":"global-gradient-sensitivity","sensitivity":sensitivity,"explainabilityArtifact":artifact,"modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"explanationDatasetFingerprint":dataset_fp}


EMBEDDING_ARTIFACT_SCHEMA = "sc-workspace-neural-embedding-artifact/1.0"
REPRESENTATION_ANALYSIS_ARTIFACT_SCHEMA = "sc-workspace-neural-representation-analysis-artifact/1.0"
MAX_EMBEDDING_ROWS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_EMBEDDING_ROWS", "512")), 4096))
MAX_EMBEDDING_DIMENSIONS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_EMBEDDING_DIMENSIONS", "512")), 4096))
MAX_SIMILARITY_PAIRS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SIMILARITY_PAIRS", "4096")), 20000))
MAX_NEIGHBOR_QUERIES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_NEIGHBOR_QUERIES", "128")), 1024))
MAX_NEIGHBORS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_NEIGHBORS", "50")), 256))
ALLOWED_EMBEDDING_NORMALIZATION = {"none", "l2"}
ALLOWED_EMBEDDING_METRICS = {"cosine", "euclidean", "dot"}


def _row_ids(payload: dict[str, Any], rows: int) -> list[str]:
    raw = payload.get("rowIds")
    if raw is None:
        return [str(i) for i in range(rows)]
    if not isinstance(raw, list) or len(raw) != rows:
        raise HTTPException(status_code=400, detail="rowIds must contain one value per embedding row")
    out=[]
    for value in raw:
        if not isinstance(value, (str, int)):
            raise HTTPException(status_code=400, detail="rowIds must contain only strings or integers")
        v=str(value).strip()
        if not v or len(v)>160:
            raise HTTPException(status_code=400, detail="rowIds values must be non-empty and bounded")
        out.append(v)
    if len(set(out)) != len(out):
        raise HTTPException(status_code=400, detail="rowIds must be unique")
    return out


def _representation_tensor(spec: dict[str, Any], summary: dict[str, Any], features: torch.Tensor, selector: str, layer_index: int | None) -> tuple[torch.Tensor, dict[str, Any]]:
    selector = str(selector or "").strip().lower()
    if not selector:
        selector = "penultimate" if summary["modelType"] == "mlp" and int(summary["layerCount"]) > 1 else "output"
    if selector == "input":
        return features, {"kind":"input","layerIndex":None,"activation":"identity"}
    if summary["modelType"] == "linear":
        if selector != "output":
            raise HTTPException(status_code=400, detail="linear models support input or output representation only")
        weights,bias,activation,_=_linear_spec(spec,layer_name="modelSpec")
        out=_activation(F.linear(features,weights,bias),activation)
        return out,{"kind":"output","layerIndex":0,"activation":activation}
    layers=spec.get("layers") or []
    outputs=[]
    x=features
    for index,layer in enumerate(layers):
        weights,bias,activation,_=_linear_spec(layer,layer_name=f"modelSpec.layers[{index}]")
        x=_activation(F.linear(x,weights,bias),activation)
        outputs.append((x,activation))
    if selector == "output":
        idx=len(outputs)-1
    elif selector == "penultimate":
        if len(outputs)<2:
            raise HTTPException(status_code=400, detail="penultimate representation requires an MLP with at least two layers")
        idx=len(outputs)-2
    elif selector == "hidden":
        if isinstance(layer_index,bool) or not isinstance(layer_index,int):
            raise HTTPException(status_code=400, detail="hidden representation requires integer layerIndex")
        if layer_index < 0 or layer_index >= len(outputs)-1:
            raise HTTPException(status_code=400, detail="hidden layerIndex must address a non-output MLP layer")
        idx=layer_index
    else:
        raise HTTPException(status_code=400, detail="representation must be input, output, penultimate, or hidden")
    tensor,activation=outputs[idx]
    return tensor,{"kind":selector,"layerIndex":idx,"activation":activation}


def _embedding_context(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], torch.Tensor, str, str | None, str, list[str]]:
    summary,model_fp,checkpoint_fp=_analysis_source(payload)
    spec=payload.get("modelSpec")
    features=_tensor(payload.get("features"),name="features",dtype_name="float32",ndim=2)
    rows,width=int(features.shape[0]),int(features.shape[1])
    if rows<1 or rows>MAX_EMBEDDING_ROWS:
        raise HTTPException(status_code=413, detail="embedding row count is outside the bounded range")
    if width != int(summary["inputFeatures"]):
        raise HTTPException(status_code=400, detail="features width does not match model specification")
    ids=_row_ids(payload,rows)
    dataset_fp=_canonical_sha256({"features":payload.get("features"),"rowIds":ids})
    return spec,summary,features,model_fp,checkpoint_fp,dataset_fp,ids


def _embedding_generate(payload: dict[str, Any]) -> dict[str, Any]:
    spec,summary,features,model_fp,checkpoint_fp,dataset_fp,ids=_embedding_context(payload)
    selector=str(payload.get("representation") or "")
    layer_index=payload.get("layerIndex")
    representation,selector_doc=_representation_tensor(spec,summary,features,selector,layer_index)
    if representation.ndim != 2:
        raise HTTPException(status_code=400, detail="selected representation must be rank 2")
    rows,dims=int(representation.shape[0]),int(representation.shape[1])
    if dims<1 or dims>MAX_EMBEDDING_DIMENSIONS:
        raise HTTPException(status_code=413, detail="embedding dimension is outside the bounded range")
    mode=str(payload.get("normalization") or "none").strip().lower()
    if mode not in ALLOWED_EMBEDDING_NORMALIZATION:
        raise HTTPException(status_code=400, detail="normalization must be none or l2")
    source_norms=torch.linalg.vector_norm(representation,ord=2,dim=1)
    vectors=representation
    if mode=="l2":
        denom=torch.where(source_norms>1e-12,source_norms,torch.ones_like(source_norms)).reshape(-1,1)
        vectors=representation/denom
    norms=torch.linalg.vector_norm(vectors,ord=2,dim=1)
    artifact=_artifact(EMBEDDING_ARTIFACT_SCHEMA,"neural-embedding",{
        "operation":"workspace.neural.embedding-generate","modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,
        "representationDatasetFingerprint":dataset_fp,"representation":selector_doc,
        "normalization":mode,"rows":rows,"dimensions":dims,"rowIds":ids,
        "sourceVectorNorms":[float(v) for v in source_norms.tolist()],
        "vectorNorms":[float(v) for v in norms.tolist()],
        "vectors":[[float(v) for v in row] for row in vectors.tolist()],
    })
    return {"kind":"neural-embedding-result","embeddingArtifact":artifact,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,
            "representationDatasetFingerprint":dataset_fp,"representation":selector_doc,
            "normalization":mode,"rows":rows,"dimensions":dims,"rowIds":ids,
            "vectors":artifact["vectors"]}


def _validate_embedding_artifact(value: Any) -> tuple[dict[str, Any], torch.Tensor]:
    if not isinstance(value,dict) or value.get("schema")!=EMBEDDING_ARTIFACT_SCHEMA or value.get("kind")!="neural-embedding":
        raise HTTPException(status_code=400, detail="embeddingArtifact must use the governed neural embedding schema")
    supplied=str(value.get("artifactFingerprint") or "")
    base={k:v for k,v in value.items() if k not in {"artifactFingerprint","artifactId"}}
    if len(supplied)!=64 or not hmac.compare_digest(supplied,_canonical_sha256(base)):
        raise HTTPException(status_code=400, detail="embeddingArtifact fingerprint verification failed")
    vectors=_tensor(value.get("vectors"),name="embeddingArtifact.vectors",dtype_name="float32",ndim=2)
    rows,dims=int(vectors.shape[0]),int(vectors.shape[1])
    if rows<1 or rows>MAX_EMBEDDING_ROWS or dims<1 or dims>MAX_EMBEDDING_DIMENSIONS:
        raise HTTPException(status_code=413, detail="embeddingArtifact dimensions exceed bounded representation limits")
    if value.get("rows")!=rows or value.get("dimensions")!=dims:
        raise HTTPException(status_code=400, detail="embeddingArtifact shape metadata does not match vectors")
    ids=value.get("rowIds")
    if not isinstance(ids,list) or len(ids)!=rows or any(not isinstance(x,str) or not x for x in ids):
        raise HTTPException(status_code=400, detail="embeddingArtifact rowIds are invalid")
    return value,vectors


def _representation_artifact(operation: str, analysis_type: str, source: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    return _artifact(REPRESENTATION_ANALYSIS_ARTIFACT_SCHEMA,"neural-representation-analysis",{
        "operation":operation,"analysisType":analysis_type,
        "sourceEmbeddingArtifactFingerprint":source.get("artifactFingerprint"),
        "modelSpecFingerprint":source.get("modelSpecFingerprint"),
        "checkpointFingerprint":source.get("checkpointFingerprint"),
        "representationDatasetFingerprint":source.get("representationDatasetFingerprint"),
        "representation":source.get("representation"),"normalization":source.get("normalization"),
        "rows":source.get("rows"),"dimensions":source.get("dimensions"),**body,
    })


def _representation_summary(payload: dict[str, Any]) -> dict[str, Any]:
    source,vectors=_validate_embedding_artifact(payload.get("embeddingArtifact"))
    norms=torch.linalg.vector_norm(vectors,ord=2,dim=1)
    mean=torch.mean(vectors,dim=0); std=torch.std(vectors,dim=0,unbiased=False)
    minv=torch.min(vectors,dim=0).values; maxv=torch.max(vectors,dim=0).values
    body={"centroid":[float(v) for v in mean.tolist()],"dimensionStd":[float(v) for v in std.tolist()],
          "dimensionMin":[float(v) for v in minv.tolist()],"dimensionMax":[float(v) for v in maxv.tolist()],
          "normSummary":{"min":float(norms.min().item()),"max":float(norms.max().item()),"mean":float(norms.mean().item()),"std":float(norms.std(unbiased=False).item())}}
    art=_representation_artifact("workspace.neural.representation-summary","summary",source,body)
    return {"kind":"neural-representation-analysis-result","analysisType":"summary","summary":body,"representationArtifact":art,
            "sourceEmbeddingArtifactFingerprint":source["artifactFingerprint"]}


def _metric_value(a: torch.Tensor,b: torch.Tensor,metric: str) -> float:
    if metric=="cosine": return float(F.cosine_similarity(a.reshape(1,-1),b.reshape(1,-1),dim=1,eps=1e-12).item())
    if metric=="euclidean": return float(torch.linalg.vector_norm(a-b,ord=2).item())
    return float(torch.dot(a,b).item())


def _embedding_similarity(payload: dict[str, Any]) -> dict[str, Any]:
    source,vectors=_validate_embedding_artifact(payload.get("embeddingArtifact"))
    metric=str(payload.get("metric") or "cosine").strip().lower()
    if metric not in ALLOWED_EMBEDDING_METRICS: raise HTTPException(status_code=400,detail="embedding metric is not registered")
    rows=int(vectors.shape[0]); raw_pairs=payload.get("pairs")
    if raw_pairs is None:
        if rows>32: raise HTTPException(status_code=400,detail="pairs are required when an embedding artifact has more than 32 rows")
        raw_pairs=[[i,j] for i in range(rows) for j in range(i+1,rows)]
    if not isinstance(raw_pairs,list) or len(raw_pairs)>MAX_SIMILARITY_PAIRS:
        raise HTTPException(status_code=413,detail="similarity pair count exceeds the bounded limit")
    out=[]; ids=source["rowIds"]
    for pair in raw_pairs:
        if not isinstance(pair,list) or len(pair)!=2 or any(isinstance(x,bool) or not isinstance(x,int) for x in pair):
            raise HTTPException(status_code=400,detail="pairs must contain [leftIndex,rightIndex] integers")
        i,j=pair
        if i<0 or j<0 or i>=rows or j>=rows: raise HTTPException(status_code=400,detail="similarity pair index is out of range")
        value=_metric_value(vectors[i],vectors[j],metric)
        rec={"leftIndex":i,"rightIndex":j,"leftRowId":ids[i],"rightRowId":ids[j],"value":value}
        rec["distance" if metric=="euclidean" else "similarity"]=value
        out.append(rec)
    art=_representation_artifact("workspace.neural.embedding-similarity","pairwise-similarity",source,{"metric":metric,"pairCount":len(out),"pairs":out})
    return {"kind":"neural-representation-analysis-result","analysisType":"pairwise-similarity","metric":metric,"pairs":out,"representationArtifact":art,
            "sourceEmbeddingArtifactFingerprint":source["artifactFingerprint"]}


def _embedding_neighbors(payload: dict[str, Any]) -> dict[str, Any]:
    source,vectors=_validate_embedding_artifact(payload.get("embeddingArtifact"))
    metric=str(payload.get("metric") or "cosine").strip().lower()
    if metric not in ALLOWED_EMBEDDING_METRICS: raise HTTPException(status_code=400,detail="embedding metric is not registered")
    rows=int(vectors.shape[0])
    queries=payload.get("queryIndices")
    if not isinstance(queries,list) or not queries or len(queries)>MAX_NEIGHBOR_QUERIES or any(isinstance(x,bool) or not isinstance(x,int) for x in queries):
        raise HTTPException(status_code=400,detail="queryIndices must be a non-empty bounded integer array")
    if len(set(queries))!=len(queries): raise HTTPException(status_code=400,detail="queryIndices must be unique")
    if any(x<0 or x>=rows for x in queries): raise HTTPException(status_code=400,detail="query index is out of range")
    k=payload.get("k",min(5,max(1,rows-1)))
    if isinstance(k,bool) or not isinstance(k,int) or k<1 or k>MAX_NEIGHBORS or k>=rows:
        raise HTTPException(status_code=400,detail="k is outside the bounded neighbor range or must be smaller than row count")
    ids=source["rowIds"]; groups=[]
    for qi in queries:
        scored=[]
        for j in range(rows):
            if j==qi: continue
            value=_metric_value(vectors[qi],vectors[j],metric)
            scored.append((value,j))
        scored.sort(key=lambda x:x[0],reverse=(metric!="euclidean"))
        neighbors=[]
        for value,j in scored[:k]:
            rec={"index":j,"rowId":ids[j],"value":value}; rec["distance" if metric=="euclidean" else "similarity"]=value; neighbors.append(rec)
        groups.append({"queryIndex":qi,"queryRowId":ids[qi],"neighbors":neighbors})
    art=_representation_artifact("workspace.neural.embedding-neighbors","nearest-neighbors",source,{"metric":metric,"k":k,"queryCount":len(groups),"queries":groups})
    return {"kind":"neural-representation-analysis-result","analysisType":"nearest-neighbors","metric":metric,"k":k,"queries":groups,"representationArtifact":art,
            "sourceEmbeddingArtifactFingerprint":source["artifactFingerprint"]}



PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-prediction-artifact/1.0"
MAX_INFERENCE_ROWS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_INFERENCE_ROWS", "4096")), 16384))
MAX_PREDICTION_OUTPUTS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PREDICTION_OUTPUTS", "512")), 4096))
DEFAULT_BINARY_THRESHOLD = 0.5


def _prediction_row_ids(payload: dict[str, Any], rows: int) -> list[str]:
    raw = payload.get("rowIds")
    if raw is None:
        return [str(i) for i in range(rows)]
    if not isinstance(raw, list) or len(raw) != rows:
        raise HTTPException(status_code=400, detail="rowIds must contain one value per inference row")
    out=[]
    for value in raw:
        if not isinstance(value,(str,int)):
            raise HTTPException(status_code=400, detail="rowIds must contain only strings or integers")
        v=str(value).strip()
        if not v or len(v)>160:
            raise HTTPException(status_code=400, detail="rowIds values must be non-empty and bounded")
        out.append(v)
    if len(set(out)) != len(out):
        raise HTTPException(status_code=400, detail="rowIds must be unique within an inference job")
    return out


def _inference_logits(payload: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any], str, str | None, str, list[str]]:
    if "targets" in payload:
        raise HTTPException(status_code=400, detail="inference operations do not accept targets; use evaluation operations for observed outcomes")
    summary, model_fp, checkpoint_fp = _analysis_source(payload)
    features = _tensor(payload.get("features"), name="features", dtype_name="float32", ndim=2)
    rows=int(features.shape[0]); outputs=int(summary["outputFeatures"])
    if rows < 1 or rows > MAX_INFERENCE_ROWS:
        raise HTTPException(status_code=413, detail="inference row count is outside the bounded range")
    if outputs < 1 or outputs > MAX_PREDICTION_OUTPUTS:
        raise HTTPException(status_code=413, detail="prediction output dimension is outside the bounded range")
    if int(features.shape[1]) != int(summary["inputFeatures"]):
        raise HTTPException(status_code=400, detail="features width does not match model specification")
    spec=payload.get("modelSpec")
    if summary["modelType"] == "linear":
        weights,bias,activation,_=_linear_spec(spec,layer_name="modelSpec")
        raw=F.linear(features,weights,bias)
        logits=raw if activation in {"identity","sigmoid","softmax"} else _activation(raw,activation)
    else:
        x=features
        for index,layer in enumerate(spec["layers"]):
            weights,bias,activation,_=_linear_spec(layer,layer_name=f"modelSpec.layers[{index}]")
            raw=F.linear(x,weights,bias)
            x=raw if index==len(spec["layers"])-1 else _activation(raw,activation)
        logits=x
    ids=_prediction_row_ids(payload,rows)
    dataset_fp=_canonical_sha256({"features":payload.get("features"),"rowIds":ids})
    return features,logits,summary,model_fp,checkpoint_fp,dataset_fp,ids


def _prediction_artifact(operation: str, task: str, summary: dict[str, Any], model_fp: str, checkpoint_fp: str | None, dataset_fp: str, row_ids: list[str], policy: dict[str, Any], uncertainty: dict[str, Any], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    return _artifact(PREDICTION_ARTIFACT_SCHEMA,"neural-prediction",{
        "operation":operation,"task":task,"modelType":summary["modelType"],
        "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,
        "inferenceDatasetFingerprint":dataset_fp,"rows":len(row_ids),
        "outputDimensions":int(summary["outputFeatures"]),"rowIds":row_ids,
        "predictionPolicy":policy,"uncertaintySemantics":uncertainty,
        "evidenceBoundary":{
            "source":"model-inference","isObservedEvidence":False,"isEvaluation":False,
            "targetsAccepted":False,"interpretationRequired":True,
        },
        "predictions":predictions,
    })


def _infer_regression(payload: dict[str, Any]) -> dict[str, Any]:
    _,raw,summary,model_fp,checkpoint_fp,dataset_fp,ids=_inference_logits(payload)
    preds=[]
    for i,row_id in enumerate(ids):
        values=[float(v) for v in raw[i].detach().tolist()]
        preds.append({"rowId":row_id,"outputs":values,"uncertainty":{"status":"not-estimated","method":None}})
    uncertainty={
        "status":"not-estimated","method":None,
        "meaning":"deterministic forward-pass outputs do not by themselves provide predictive uncertainty",
    }
    policy={"output":"raw-regression-output","decisionRule":None,"calibrationStatus":"not-applicable"}
    art=_prediction_artifact("workspace.neural.infer-regression","regression",summary,model_fp,checkpoint_fp,dataset_fp,ids,policy,uncertainty,preds)
    return {"kind":"neural-inference-result","task":"regression","predictions":preds,"predictionArtifact":art,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"inferenceDatasetFingerprint":dataset_fp}


def _binary_entropy(p: float) -> float:
    eps=1e-12; q=min(max(p,eps),1.0-eps)
    return float(-(q*math.log(q)+(1.0-q)*math.log(1.0-q)))


def _infer_binary(payload: dict[str, Any]) -> dict[str, Any]:
    _,logits,summary,model_fp,checkpoint_fp,dataset_fp,ids=_inference_logits(payload)
    if int(logits.shape[1]) != 1:
        raise HTTPException(status_code=400,detail="binary inference requires one model output")
    threshold=float(payload.get("threshold",DEFAULT_BINARY_THRESHOLD))
    if not (0.0 < threshold < 1.0):
        raise HTTPException(status_code=400,detail="binary threshold must be between 0 and 1")
    prob=torch.sigmoid(logits).reshape(-1)
    preds=[]
    for row_id,logit,p in zip(ids,logits.reshape(-1).tolist(),prob.tolist()):
        ent=_binary_entropy(float(p))
        preds.append({"rowId":row_id,"logit":float(logit),"probability":float(p),
                      "predictedClass":int(p>=threshold),"confidence":float(max(p,1.0-p)),
                      "entropy":ent,"normalizedEntropy":float(ent/math.log(2.0))})
    policy={"output":"sigmoid-probability","threshold":threshold,"calibrationStatus":"not-assessed"}
    uncertainty={"status":"model-derived","method":"predictive-entropy","probabilitySemantics":"model-output-not-calibrated-real-world-probability"}
    art=_prediction_artifact("workspace.neural.infer-binary","binary-classification",summary,model_fp,checkpoint_fp,dataset_fp,ids,policy,uncertainty,preds)
    return {"kind":"neural-inference-result","task":"binary-classification","predictions":preds,"predictionArtifact":art,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"inferenceDatasetFingerprint":dataset_fp}


def _infer_multiclass(payload: dict[str, Any]) -> dict[str, Any]:
    _,logits,summary,model_fp,checkpoint_fp,dataset_fp,ids=_inference_logits(payload)
    classes=int(logits.shape[1])
    if classes < 2:
        raise HTTPException(status_code=400,detail="multiclass inference requires at least two model outputs")
    prob=torch.softmax(logits,dim=1)
    preds=[]
    norm=math.log(float(classes))
    for i,row_id in enumerate(ids):
        ps=[float(v) for v in prob[i].tolist()]; ls=[float(v) for v in logits[i].tolist()]
        order=sorted(range(classes),key=lambda j:ps[j],reverse=True); top=order[0]; second=order[1]
        ent=float(-sum(max(p,1e-12)*math.log(max(p,1e-12)) for p in ps))
        preds.append({"rowId":row_id,"logits":ls,"probabilities":ps,"predictedClass":int(top),
                      "confidence":ps[top],"margin":float(ps[top]-ps[second]),
                      "entropy":ent,"normalizedEntropy":float(ent/norm)})
    policy={"output":"softmax-probabilities","decisionRule":"argmax","calibrationStatus":"not-assessed"}
    uncertainty={"status":"model-derived","method":"predictive-entropy-and-margin","probabilitySemantics":"model-output-not-calibrated-real-world-probability"}
    art=_prediction_artifact("workspace.neural.infer-multiclass","multiclass-classification",summary,model_fp,checkpoint_fp,dataset_fp,ids,policy,uncertainty,preds)
    return {"kind":"neural-inference-result","task":"multiclass-classification","predictions":preds,"predictionArtifact":art,
            "modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp,"inferenceDatasetFingerprint":dataset_fp}


def _validate_prediction_artifact(value: Any) -> dict[str, Any]:
    if not isinstance(value,dict) or value.get("schema")!=PREDICTION_ARTIFACT_SCHEMA or value.get("kind")!="neural-prediction":
        raise HTTPException(status_code=400,detail="predictionArtifact must use the governed neural prediction schema")
    fp=str(value.get("artifactFingerprint") or "")
    base={k:v for k,v in value.items() if k not in {"artifactFingerprint","artifactId"}}
    if not fp or not hmac.compare_digest(fp,_canonical_sha256(base)):
        raise HTTPException(status_code=400,detail="predictionArtifact fingerprint verification failed")
    rows=int(value.get("rows") or 0); preds=value.get("predictions"); ids=value.get("rowIds")
    if rows<1 or rows>MAX_INFERENCE_ROWS or not isinstance(preds,list) or len(preds)!=rows or not isinstance(ids,list) or len(ids)!=rows:
        raise HTTPException(status_code=400,detail="predictionArtifact row metadata is invalid")
    if value.get("evidenceBoundary",{}).get("isObservedEvidence") is not False or value.get("evidenceBoundary",{}).get("targetsAccepted") is not False:
        raise HTTPException(status_code=400,detail="predictionArtifact evidence boundary is invalid")
    return value


def _prediction_inspect(payload: dict[str, Any]) -> dict[str, Any]:
    art=_validate_prediction_artifact(payload.get("predictionArtifact"))
    summary={
        "task":art.get("task"),"rows":art.get("rows"),"outputDimensions":art.get("outputDimensions"),
        "modelSpecFingerprint":art.get("modelSpecFingerprint"),"checkpointFingerprint":art.get("checkpointFingerprint"),
        "inferenceDatasetFingerprint":art.get("inferenceDatasetFingerprint"),
        "predictionPolicy":art.get("predictionPolicy"),"uncertaintySemantics":art.get("uncertaintySemantics"),
        "evidenceBoundary":art.get("evidenceBoundary"),"artifactFingerprint":art.get("artifactFingerprint"),
    }
    return {"kind":"neural-prediction-inspection","summary":summary,"predictionArtifactFingerprint":art.get("artifactFingerprint")}


MODEL_PACKAGE_SCHEMA = "sc-workspace-neural-model-package/1.0"
MODEL_PACKAGE_MANIFEST_SCHEMA = "sc-workspace-neural-model-package-manifest/1.0"
MODEL_PACKAGE_FORMAT = "sc-workspace-neural-reproducible-model-package/1.0"
MODEL_PACKAGE_RUNTIME_CONTRACT_SCHEMA = "sc-workspace-neural-runtime-contract/1.0"
MODEL_PACKAGE_DEPENDENCY_PINS = {"torch": "2.10.0", "numpy": "2.2.6"}
MAX_MODEL_PACKAGE_FEATURE_NAMES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_PACKAGE_FEATURE_NAMES", "4096")), 16384))
ALLOWED_MODEL_PACKAGE_TASKS = {"regression", "binary-classification", "multiclass-classification"}


def _package_feature_names(payload: dict[str, Any], expected: int) -> list[str]:
    raw = payload.get("featureNames")
    if raw is None:
        return [f"feature_{i}" for i in range(expected)]
    if not isinstance(raw, list) or len(raw) != expected or len(raw) > MAX_MODEL_PACKAGE_FEATURE_NAMES:
        raise HTTPException(status_code=400, detail="featureNames must match the model input width and remain bounded")
    out=[]
    for value in raw:
        if not isinstance(value,str):
            raise HTTPException(status_code=400, detail="featureNames must contain strings")
        value=value.strip()
        if not value or len(value)>160:
            raise HTTPException(status_code=400, detail="featureNames values must be non-empty and bounded")
        out.append(value)
    if len(set(out)) != len(out):
        raise HTTPException(status_code=400, detail="featureNames must be unique")
    return out


def _package_runtime_contract() -> dict[str, Any]:
    return {
        "schema": MODEL_PACKAGE_RUNTIME_CONTRACT_SCHEMA,
        "runtime": RUNTIME,
        "runtimeVersion": SERVICE_VERSION,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "numpyVersion": np.__version__,
        "requiredDependencyPins": dict(MODEL_PACKAGE_DEPENDENCY_PINS),
        "devicePolicy": "governed-explicit-device-orchestration",
        "acceleratorRequired": False,
        "supportedDeviceClasses": ["cpu", "cuda"],
        "deviceSelectionMustBeExplicit": True,
        "arbitraryCodeRequired": False,
        "serializedModelRequired": False,
        "declarativeModelSpecRequired": True,
    }


def _model_package_body_for_fingerprint(package: dict[str, Any]) -> dict[str, Any]:
    return {k:v for k,v in package.items() if k not in {"artifactFingerprint","packageId"}}


def _validate_model_package(value: Any) -> dict[str, Any]:
    if not isinstance(value,dict) or value.get("schema") != MODEL_PACKAGE_SCHEMA:
        raise HTTPException(status_code=400, detail=f"modelPackage must use {MODEL_PACKAGE_SCHEMA}")
    pkg=dict(value)
    if pkg.get("format") != MODEL_PACKAGE_FORMAT or pkg.get("kind") != "neural-model-package":
        raise HTTPException(status_code=400, detail="model package format is unsupported")
    supplied=str(pkg.get("artifactFingerprint") or "")
    expected=_canonical_sha256(_model_package_body_for_fingerprint(pkg))
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=400, detail="model package fingerprint verification failed")
    if pkg.get("packageId") != "nmp_"+expected[:24]:
        raise HTTPException(status_code=400, detail="model package id does not match its fingerprint")
    spec=pkg.get("modelSpec")
    summary=_validate_model_spec(spec)
    model_fp=_canonical_sha256(spec)
    if pkg.get("modelSpecFingerprint") != model_fp:
        raise HTTPException(status_code=400, detail="model package model fingerprint mismatch")
    contract=pkg.get("runtimeContract")
    if not isinstance(contract,dict) or contract.get("schema") != MODEL_PACKAGE_RUNTIME_CONTRACT_SCHEMA:
        raise HTTPException(status_code=400, detail="model package runtime contract is missing")
    if contract.get("runtime") != RUNTIME or contract.get("requiredDependencyPins") != MODEL_PACKAGE_DEPENDENCY_PINS:
        raise HTTPException(status_code=400, detail="model package runtime/dependency contract is incompatible")
    if contract.get("arbitraryCodeRequired") is not False or contract.get("serializedModelRequired") is not False:
        raise HTTPException(status_code=400, detail="model package requests an unsafe execution contract")
    manifest=pkg.get("manifest")
    if not isinstance(manifest,dict) or manifest.get("schema") != MODEL_PACKAGE_MANIFEST_SCHEMA:
        raise HTTPException(status_code=400, detail="model package manifest is missing")
    inf=pkg.get("inferenceContract")
    if not isinstance(inf,dict) or inf.get("task") not in ALLOWED_MODEL_PACKAGE_TASKS:
        raise HTTPException(status_code=400, detail="model package inference contract is invalid")
    if int(inf.get("inputFeatures") or -1) != int(summary["inputFeatures"]) or int(inf.get("outputFeatures") or -1) != int(summary["outputFeatures"]):
        raise HTTPException(status_code=400, detail="model package inference shape contract is invalid")
    names=inf.get("featureNames")
    if not isinstance(names,list) or len(names) != int(summary["inputFeatures"]) or len(set(names)) != len(names):
        raise HTTPException(status_code=400, detail="model package feature contract is invalid")
    checkpoint=pkg.get("checkpointArtifact")
    if checkpoint is not None:
        checkpoint,_=_validate_checkpoint_artifact(checkpoint,decode_state=False)
        if checkpoint.get("trainedModelSpecFingerprint") != model_fp or pkg.get("checkpointFingerprint") != checkpoint.get("artifactFingerprint"):
            raise HTTPException(status_code=400, detail="model package checkpoint lineage does not match model")
    elif pkg.get("checkpointFingerprint") is not None:
        raise HTTPException(status_code=400, detail="model package checkpoint fingerprint is orphaned")
    task=inf["task"]
    outputs=int(summary["outputFeatures"])
    if task=="binary-classification" and outputs!=1:
        raise HTTPException(status_code=400, detail="binary package requires one model output")
    if task=="multiclass-classification" and outputs<2:
        raise HTTPException(status_code=400, detail="multiclass package requires at least two model outputs")
    return pkg


def _model_package_create(payload: dict[str, Any]) -> dict[str, Any]:
    spec=payload.get("modelSpec")
    summary=_validate_model_spec(spec)
    model_fp=_canonical_sha256(spec)
    task=str(payload.get("task") or "").strip()
    if task not in ALLOWED_MODEL_PACKAGE_TASKS:
        raise HTTPException(status_code=400, detail="task is not supported for reproducible model packages")
    outputs=int(summary["outputFeatures"])
    if task=="binary-classification" and outputs!=1:
        raise HTTPException(status_code=400, detail="binary package requires one model output")
    if task=="multiclass-classification" and outputs<2:
        raise HTTPException(status_code=400, detail="multiclass package requires at least two model outputs")
    names=_package_feature_names(payload,int(summary["inputFeatures"]))
    threshold=None
    if task=="binary-classification":
        threshold=float(payload.get("threshold",DEFAULT_BINARY_THRESHOLD))
        if not (0.0 < threshold < 1.0):
            raise HTTPException(status_code=400, detail="binary threshold must be between 0 and 1")
    checkpoint=payload.get("checkpointArtifact")
    checkpoint_fp=None
    provenance={"trainingSpecFingerprint":None,"trainingDatasetFingerprint":None,"checkpointLineageDepth":None}
    if checkpoint is not None:
        checkpoint,_=_validate_checkpoint_artifact(checkpoint,decode_state=False)
        if checkpoint.get("trainedModelSpecFingerprint") != model_fp:
            raise HTTPException(status_code=400, detail="checkpoint trained model does not match package modelSpec")
        checkpoint_fp=checkpoint.get("artifactFingerprint")
        provenance={
            "trainingSpecFingerprint":checkpoint.get("trainingSpecFingerprint"),
            "trainingDatasetFingerprint":checkpoint.get("trainingDatasetFingerprint"),
            "checkpointLineageDepth":checkpoint.get("lineageDepth"),
        }
    inference_contract={
        "task":task,
        "inputFeatures":int(summary["inputFeatures"]),
        "outputFeatures":outputs,
        "featureNames":names,
        "rowIdPolicy":"caller-supplied-or-stable-zero-based",
        "targetsAccepted":False,
        "decisionRule":"threshold" if task=="binary-classification" else ("argmax" if task=="multiclass-classification" else None),
        "threshold":threshold,
        "calibrationStatus":"not-assessed" if task!="regression" else "not-applicable",
    }
    runtime_contract=_package_runtime_contract()
    manifest={
        "schema":MODEL_PACKAGE_MANIFEST_SCHEMA,
        "packageFormat":MODEL_PACKAGE_FORMAT,
        "portable":True,
        "selfContainedInference":True,
        "containsDeclarativeModelSpec":True,
        "containsCheckpoint":checkpoint is not None,
        "containsArbitraryCode":False,
        "containsSerializedPyTorchModel":False,
        "requiredFiles":[],
        "runtimeContractFingerprint":_canonical_sha256(runtime_contract),
        "inferenceContractFingerprint":_canonical_sha256(inference_contract),
    }
    pkg={
        "schema":MODEL_PACKAGE_SCHEMA,"kind":"neural-model-package","format":MODEL_PACKAGE_FORMAT,
        "portable":True,"selfContainedInference":True,
        "modelType":summary["modelType"],"task":task,"modelSpec":spec,"modelSpecFingerprint":model_fp,
        "checkpointArtifact":checkpoint,"checkpointFingerprint":checkpoint_fp,
        "runtimeContract":runtime_contract,"inferenceContract":inference_contract,"manifest":manifest,
        "provenance":provenance,
        "evidenceBoundary":{"isObservedEvidence":False,"isPrediction":False,"isEvaluation":False,"packageDefinesExecutableModel":True},
    }
    fp=_canonical_sha256(pkg); pkg["artifactFingerprint"]=fp; pkg["packageId"]="nmp_"+fp[:24]
    return {"kind":"neural-model-package-result","modelPackage":pkg,"modelPackageFingerprint":fp,"packageId":pkg["packageId"],"modelSpecFingerprint":model_fp,"checkpointFingerprint":checkpoint_fp}


def _model_package_verify(payload: dict[str, Any]) -> dict[str, Any]:
    pkg=_validate_model_package(payload.get("modelPackage"))
    contract=pkg["runtimeContract"]
    compatible=contract.get("runtime")==RUNTIME and contract.get("requiredDependencyPins")==MODEL_PACKAGE_DEPENDENCY_PINS
    return {
        "kind":"neural-model-package-verification","valid":True,"compatible":compatible,
        "packageId":pkg["packageId"],"modelPackageFingerprint":pkg["artifactFingerprint"],
        "modelSpecFingerprint":pkg["modelSpecFingerprint"],"checkpointFingerprint":pkg.get("checkpointFingerprint"),
        "runtimeContractFingerprint":pkg["manifest"]["runtimeContractFingerprint"],
        "inferenceContractFingerprint":pkg["manifest"]["inferenceContractFingerprint"],
        "requiredDependencyPins":dict(MODEL_PACKAGE_DEPENDENCY_PINS),
    }


def _model_package_inspect(payload: dict[str, Any]) -> dict[str, Any]:
    pkg=_validate_model_package(payload.get("modelPackage"))
    inf=pkg["inferenceContract"]
    return {
        "kind":"neural-model-package-inspection","packageId":pkg["packageId"],
        "modelPackageFingerprint":pkg["artifactFingerprint"],"modelType":pkg["modelType"],"task":pkg["task"],
        "modelSpecFingerprint":pkg["modelSpecFingerprint"],"checkpointFingerprint":pkg.get("checkpointFingerprint"),
        "inputFeatures":inf["inputFeatures"],"outputFeatures":inf["outputFeatures"],"featureNames":inf["featureNames"],
        "portable":pkg["portable"],"selfContainedInference":pkg["selfContainedInference"],
        "runtimeContract":pkg["runtimeContract"],"manifest":pkg["manifest"],"provenance":pkg["provenance"],
    }


def _model_package_infer(payload: dict[str, Any]) -> dict[str, Any]:
    if "targets" in payload:
        raise HTTPException(status_code=400, detail="packaged inference does not accept targets; use evaluation operations for observed outcomes")
    pkg=_validate_model_package(payload.get("modelPackage"))
    inf=pkg["inferenceContract"]
    req={"modelSpec":pkg["modelSpec"],"features":payload.get("features")}
    if pkg.get("checkpointArtifact") is not None:
        req["checkpointArtifact"]=pkg["checkpointArtifact"]
    if "rowIds" in payload:
        req["rowIds"]=payload.get("rowIds")
    if inf["task"]=="binary-classification":
        req["threshold"]=inf.get("threshold",DEFAULT_BINARY_THRESHOLD)
        result=_infer_binary(req)
    elif inf["task"]=="multiclass-classification":
        result=_infer_multiclass(req)
    else:
        result=_infer_regression(req)
    art=result.get("predictionArtifact")
    if not isinstance(art,dict):
        raise HTTPException(status_code=500,detail="packaged inference did not produce a prediction artifact")
    art={k:v for k,v in art.items() if k not in {"artifactFingerprint","artifactId"}}
    art["sourceModelPackageFingerprint"]=pkg["artifactFingerprint"]
    art["sourceModelPackageId"]=pkg["packageId"]
    art["sourceRuntimeContractFingerprint"]=pkg["manifest"]["runtimeContractFingerprint"]
    fp=_canonical_sha256(art); art["artifactFingerprint"]=fp; art["artifactId"]="nea_"+fp[:24]
    result["predictionArtifact"]=art
    result["sourceModelPackageFingerprint"]=pkg["artifactFingerprint"]
    result["sourceModelPackageId"]=pkg["packageId"]
    result["packageVerified"]=True
    result["kind"]="neural-packaged-inference-result"
    return result

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

# v3.34.0 Graph Neural Network Training Runtime.
GNN_SPLIT_PLAN_SCHEMA = "sc-workspace-neural-gnn-split-plan/1.0"
GNN_TRAINING_PLAN_SCHEMA = "sc-workspace-neural-gnn-training-plan/1.0"
GNN_TRAINING_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-training-artifact/1.0"
GNN_CHECKPOINT_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-checkpoint-artifact/1.0"
GNN_TRAINING_TASKS = {
    "node-regression", "node-binary-classification", "node-multiclass-classification",
    "graph-regression", "graph-binary-classification", "graph-multiclass-classification",
    "link-prediction",
}
GNN_TRAINING_OPTIMIZERS = {"sgd"}
MAX_GNN_EPOCHS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_EPOCHS", "500")), 2000))
MAX_GNN_GRAPHS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_GRAPHS", "256")), 1024))
MAX_GNN_LINK_EXAMPLES = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_LINK_EXAMPLES", "65536")), 262144))


def _gnn_float(payload: dict[str, Any], key: str, default: float, low: float, high: float) -> float:
    raw = payload.get(key, default)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise HTTPException(status_code=400, detail=f"{key} must be numeric")
    value = float(raw)
    if not math.isfinite(value) or value < low or value > high:
        raise HTTPException(status_code=400, detail=f"{key} is outside the allowed range")
    return value


def _gnn_indices(raw: Any, count: int, label: str, allow_empty: bool = False) -> list[int]:
    if not isinstance(raw, list) or (not raw and not allow_empty):
        raise HTTPException(status_code=400, detail=f"{label} must be {'an array' if allow_empty else 'a non-empty array'}")
    out: list[int] = []
    for v in raw:
        if not isinstance(v, int) or isinstance(v, bool) or v < 0 or v >= count:
            raise HTTPException(status_code=400, detail=f"{label} contains an invalid index")
        out.append(int(v))
    if len(set(out)) != len(out):
        raise HTTPException(status_code=400, detail=f"{label} contains duplicate indices")
    return out


def _gnn_split_plan(payload: dict[str, Any]) -> dict[str, Any]:
    count = payload.get("itemCount")
    if not isinstance(count, int) or isinstance(count, bool) or count < 2 or count > max(MAX_GNN_LINK_EXAMPLES, MAX_GRAPH_NODES, MAX_GNN_GRAPHS):
        raise HTTPException(status_code=400, detail="itemCount is outside the governed split range")
    train_fraction = _gnn_float(payload, "trainFraction", 0.70, 0.05, 0.95)
    validation_fraction = _gnn_float(payload, "validationFraction", 0.15, 0.0, 0.90)
    if train_fraction + validation_fraction >= 1.0:
        raise HTTPException(status_code=400, detail="trainFraction + validationFraction must be less than 1")
    seed = _seed(payload)
    gen = torch.Generator(device="cpu"); gen.manual_seed(seed)
    perm = torch.randperm(count, generator=gen).tolist()
    n_train = max(1, int(round(count * train_fraction)))
    n_val = int(round(count * validation_fraction))
    if n_train + n_val >= count:
        n_val = max(0, count - n_train - 1)
    train = perm[:n_train]; validation = perm[n_train:n_train+n_val]; test = perm[n_train+n_val:]
    if not test:
        test = [validation.pop()] if validation else [train.pop()]
    artifact = {
        "schema": GNN_SPLIT_PLAN_SCHEMA, "kind": "gnn-split-plan", "itemCount": count,
        "trainIndices": train, "validationIndices": validation, "testIndices": test,
        "trainFractionRequested": train_fraction, "validationFractionRequested": validation_fraction,
        "seed": seed, "shufflePolicy": "torch-randperm-seeded", "stratificationEnabled": False,
        "splitInferenceEnabled": False, "isObservedEvidence": False,
    }
    artifact["artifactFingerprint"] = _canonical_sha256(artifact)
    return {"splitIndices": {"train": train, "validation": validation, "test": test}, "gnnSplitPlanArtifact": artifact}


def _gnn_training_plan(payload: dict[str, Any]) -> dict[str, Any]:
    task = str(payload.get("task") or "").lower()
    if task not in GNN_TRAINING_TASKS:
        raise HTTPException(status_code=400, detail="unsupported GNN training task")
    spec = _gnn_validate_model_spec(payload.get("modelSpec"))
    if spec.get("activation") != "identity":
        raise HTTPException(status_code=400, detail="v3.34 supervised GNN training requires modelSpec.activation=identity")
    epochs = payload.get("epochs", 25)
    if not isinstance(epochs, int) or isinstance(epochs, bool) or epochs < 1 or epochs > MAX_GNN_EPOCHS:
        raise HTTPException(status_code=400, detail="epochs is outside the governed range")
    optimizer = str(payload.get("optimizer") or "sgd").lower()
    if optimizer not in GNN_TRAINING_OPTIMIZERS:
        raise HTTPException(status_code=400, detail="v3.34 GNN training supports governed stateless SGD only")
    lr = _gnn_float(payload, "learningRate", 0.05, 1e-6, 1.0)
    wd = _gnn_float(payload, "weightDecay", 0.0, 0.0, 1.0)
    clip = _gnn_float(payload, "gradientClip", 5.0, 0.0, 1000.0)
    split = payload.get("splitIndices")
    split_fp = _canonical_sha256(split) if isinstance(split, dict) else None
    plan = {
        "schema": GNN_TRAINING_PLAN_SCHEMA, "kind": "gnn-training-plan", "task": task,
        "adapter": spec["adapter"], "initialModelSpecFingerprint": spec["modelSpecFingerprint"],
        "epochs": epochs, "optimizer": optimizer, "learningRate": lr, "weightDecay": wd,
        "gradientClip": clip, "seed": _seed(payload), "splitFingerprint": split_fp,
        "device": _current_device_name(), "fullBatch": True, "shuffleWithinEpoch": False,
        "opaqueSerializedOptimizerStateAllowed": False, "arbitraryTrainingCodeAllowed": False,
        "externalDatasetReadEnabled": False, "isObservedEvidence": False,
    }
    plan["artifactFingerprint"] = _canonical_sha256(plan)
    return {"gnnTrainingPlanArtifact": plan}


def _gnn_neighbor_mean(x: torch.Tensor, edges: list[list[int]], directed: bool, add_self: bool) -> torch.Tensor:
    n = int(x.shape[0]); device = x.device
    agg = torch.zeros_like(x); counts = torch.zeros((n, 1), dtype=x.dtype, device=device)
    src: list[int] = []; dst: list[int] = []
    for s, d in edges:
        src.append(s); dst.append(d)
        if not directed and s != d:
            src.append(d); dst.append(s)
    if src:
        sidx = torch.tensor(src, dtype=torch.long, device=device); didx = torch.tensor(dst, dtype=torch.long, device=device)
        agg.index_add_(0, didx, x[sidx])
        counts.index_add_(0, didx, torch.ones((len(dst), 1), dtype=x.dtype, device=device))
    if add_self:
        agg = agg + x; counts = counts + 1.0
    return agg / torch.clamp(counts, min=1.0)


def _gnn_train_logits(graph_payload: dict[str, Any], spec: dict[str, Any], weight: torch.Tensor, bias: torch.Tensor) -> tuple[torch.Tensor, str]:
    x, edges, node_ids, directed = _graph_components(graph_payload)
    if int(x.shape[1]) != spec["inputFeatures"]:
        raise HTTPException(status_code=400, detail="graph feature width does not match modelSpec.inputFeatures")
    if spec["adapter"] == "gcn":
        basis = _gnn_neighbor_mean(x, edges, directed, bool(spec.get("addSelfLoops", True)))
    else:
        neighbor = _gnn_neighbor_mean(x, edges, directed, bool(spec.get("addSelfLoops", False)))
        basis = torch.cat([x, neighbor], dim=1)
    logits = basis @ weight + bias
    fp = _graph_fingerprint(graph_payload["nodeFeatures"], edges, node_ids, directed)
    return logits, fp


def _gnn_loss(payload: dict[str, Any], spec: dict[str, Any], weight: torch.Tensor, bias: torch.Tensor, indices: list[int]) -> tuple[torch.Tensor, str, str]:
    task = str(payload.get("task") or "").lower()
    if task.startswith("node-"):
        logits, graph_fp = _gnn_train_logits(payload, spec, weight, bias)
        labels = payload.get("labels")
        if not isinstance(labels, list) or len(labels) != int(logits.shape[0]):
            raise HTTPException(status_code=400, detail="node training labels must align one-for-one with nodes")
        idx = torch.tensor(indices, dtype=torch.long, device=logits.device)
        if task == "node-regression":
            if spec["outputFeatures"] != 1: raise HTTPException(status_code=400, detail="node regression requires outputFeatures=1")
            y = torch.tensor(labels, dtype=torch.float32, device=logits.device).reshape(-1)
            loss = torch.nn.functional.mse_loss(logits[idx, 0], y[idx])
        elif task == "node-binary-classification":
            if spec["outputFeatures"] != 1: raise HTTPException(status_code=400, detail="node binary classification requires outputFeatures=1")
            y = torch.tensor(labels, dtype=torch.float32, device=logits.device).reshape(-1)
            if not torch.all((y == 0) | (y == 1)): raise HTTPException(status_code=400, detail="binary labels must be 0 or 1")
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logits[idx, 0], y[idx])
        else:
            if spec["outputFeatures"] < 2: raise HTTPException(status_code=400, detail="node multiclass classification requires outputFeatures>=2")
            y = torch.tensor(labels, dtype=torch.long, device=logits.device).reshape(-1)
            if int(y.min()) < 0 or int(y.max()) >= spec["outputFeatures"]: raise HTTPException(status_code=400, detail="multiclass label is outside outputFeatures")
            loss = torch.nn.functional.cross_entropy(logits[idx], y[idx])
        return loss, graph_fp, _canonical_sha256(labels)

    if task.startswith("graph-"):
        graphs = payload.get("graphs")
        if not isinstance(graphs, list) or not graphs or len(graphs) > MAX_GNN_GRAPHS:
            raise HTTPException(status_code=400, detail="graphs must be a bounded non-empty array")
        pooled=[]; labels=[]; graph_fps=[]
        for i in indices:
            g=graphs[i]
            if not isinstance(g, dict): raise HTTPException(status_code=400, detail="each graph must be an object")
            logits, fp = _gnn_train_logits(g, spec, weight, bias); pooled.append(logits.mean(dim=0)); graph_fps.append(fp)
            labels.append(g.get("label"))
        pred=torch.stack(pooled, dim=0)
        if task == "graph-regression":
            if spec["outputFeatures"] != 1: raise HTTPException(status_code=400, detail="graph regression requires outputFeatures=1")
            y=torch.tensor(labels,dtype=torch.float32,device=pred.device); loss=torch.nn.functional.mse_loss(pred[:,0],y)
        elif task == "graph-binary-classification":
            if spec["outputFeatures"] != 1: raise HTTPException(status_code=400, detail="graph binary classification requires outputFeatures=1")
            y=torch.tensor(labels,dtype=torch.float32,device=pred.device)
            if not torch.all((y==0)|(y==1)): raise HTTPException(status_code=400, detail="binary labels must be 0 or 1")
            loss=torch.nn.functional.binary_cross_entropy_with_logits(pred[:,0],y)
        else:
            if spec["outputFeatures"] < 2: raise HTTPException(status_code=400, detail="graph multiclass classification requires outputFeatures>=2")
            y=torch.tensor(labels,dtype=torch.long,device=pred.device)
            if int(y.min())<0 or int(y.max())>=spec["outputFeatures"]: raise HTTPException(status_code=400, detail="multiclass label is outside outputFeatures")
            loss=torch.nn.functional.cross_entropy(pred,y)
        return loss, _canonical_sha256(graph_fps), _canonical_sha256(labels)

    if task == "link-prediction":
        logits, graph_fp = _gnn_train_logits(payload, spec, weight, bias)
        examples = payload.get("linkExamples")
        if not isinstance(examples, list) or len(examples) < 2 or len(examples) > MAX_GNN_LINK_EXAMPLES:
            raise HTTPException(status_code=400, detail="linkExamples must be a bounded array with positive and negative examples")
        scores=[]; labels=[]; n=int(logits.shape[0])
        for i in indices:
            ex=examples[i]
            if not isinstance(ex,dict): raise HTTPException(status_code=400, detail="each link example must be an object")
            s,d,l=ex.get("source"),ex.get("target"),ex.get("label")
            if not isinstance(s,int) or isinstance(s,bool) or not isinstance(d,int) or isinstance(d,bool) or s<0 or d<0 or s>=n or d>=n:
                raise HTTPException(status_code=400, detail="link example node index is invalid")
            if l not in (0,1): raise HTTPException(status_code=400, detail="link example label must be 0 or 1")
            scores.append((logits[s]*logits[d]).sum()/max(1.0,float(spec["outputFeatures"])**0.5)); labels.append(float(l))
        score=torch.stack(scores); y=torch.tensor(labels,dtype=torch.float32,device=score.device)
        loss=torch.nn.functional.binary_cross_entropy_with_logits(score,y)
        return loss, graph_fp, _canonical_sha256(examples)
    raise HTTPException(status_code=400, detail="unsupported GNN training task")


def _gnn_training_count(payload: dict[str, Any]) -> int:
    task=str(payload.get("task") or "").lower()
    if task.startswith("node-"):
        raw=payload.get("nodeFeatures"); return len(raw) if isinstance(raw,list) else 0
    if task.startswith("graph-"):
        raw=payload.get("graphs"); return len(raw) if isinstance(raw,list) else 0
    if task=="link-prediction":
        raw=payload.get("linkExamples"); return len(raw) if isinstance(raw,list) else 0
    return 0


def _gnn_train(payload: dict[str, Any]) -> dict[str, Any]:
    plan = _gnn_training_plan(payload)["gnnTrainingPlanArtifact"]
    spec = _gnn_validate_model_spec(payload.get("modelSpec"))
    count = _gnn_training_count(payload)
    if count < 1: raise HTTPException(status_code=400, detail="training data is empty")
    split = payload.get("splitIndices")
    if not isinstance(split,dict): raise HTTPException(status_code=400, detail="splitIndices is required; use workspace.neural.gnn-split-plan")
    train_idx=_gnn_indices(split.get("train"),count,"splitIndices.train")
    val_idx=_gnn_indices(split.get("validation",[]),count,"splitIndices.validation",allow_empty=True)
    test_idx=_gnn_indices(split.get("test",[]),count,"splitIndices.test",allow_empty=True)
    if set(train_idx)&set(val_idx) or set(train_idx)&set(test_idx) or set(val_idx)&set(test_idx):
        raise HTTPException(status_code=400, detail="train/validation/test split indices must be disjoint")
    rows = spec["inputFeatures"] if spec["adapter"]=="gcn" else spec["inputFeatures"]*2
    device=_current_device_name(); seed=_seed(payload); torch.manual_seed(seed)
    weight=torch.nn.Parameter(torch.tensor(spec["weights"],dtype=torch.float32,device=device))
    bias=torch.nn.Parameter(torch.tensor(spec["bias"],dtype=torch.float32,device=device))
    optimizer=torch.optim.SGD([weight,bias],lr=plan["learningRate"],weight_decay=plan["weightDecay"],momentum=0.0)
    losses=[]; epochs=int(plan["epochs"]); base_epoch=int(payload.get("baseEpoch") or 0)
    initial_fp=spec["modelSpecFingerprint"]
    graph_fp=None; label_fp=None
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        loss, graph_fp, label_fp = _gnn_loss(payload,spec,weight,bias,train_idx)
        if not torch.isfinite(loss): raise HTTPException(status_code=400, detail="GNN training produced a non-finite loss")
        loss.backward()
        if plan["gradientClip"]>0: torch.nn.utils.clip_grad_norm_([weight,bias],plan["gradientClip"])
        optimizer.step(); losses.append(float(loss.detach().cpu().item()))
    trained={k:v for k,v in spec.items() if k!="modelSpecFingerprint"}
    trained["weights"]=weight.detach().cpu().tolist(); trained["bias"]=bias.detach().cpu().tolist()
    trained=_gnn_validate_model_spec(trained)
    def eval_loss(ix: list[int]):
        if not ix: return None
        with torch.no_grad(): return float(_gnn_loss(payload,trained,weight,bias,ix)[0].detach().cpu().item())
    artifact={
        "schema":GNN_TRAINING_ARTIFACT_SCHEMA,"kind":"gnn-training","task":plan["task"],"adapter":spec["adapter"],
        "trainingPlanFingerprint":plan["artifactFingerprint"],"initialModelSpecFingerprint":initial_fp,
        "finalModelSpecFingerprint":trained["modelSpecFingerprint"],"graphFingerprint":graph_fp,"labelFingerprint":label_fp,
        "epochStart":base_epoch,"epochsCompleted":epochs,"epochEnd":base_epoch+epochs,
        "trainingLossFirst":losses[0],"trainingLossLast":losses[-1],"validationLoss":eval_loss(val_idx),"testLoss":eval_loss(test_idx),
        "lossCurve":losses,"optimizer":"sgd","optimizerMomentum":0.0,"learningRate":plan["learningRate"],
        "weightDecay":plan["weightDecay"],"gradientClip":plan["gradientClip"],"seed":seed,"device":device,
        "fullBatch":True,"checkpointResumeExactForSameInputs":True,"opaqueSerializedOptimizerStateAllowed":False,
        "trainingLabelsPersisted":False,"isObservedEvidence":False,
    }
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    checkpoint={
        "schema":GNN_CHECKPOINT_ARTIFACT_SCHEMA,"kind":"gnn-training-checkpoint","task":plan["task"],
        "trainedModelSpec":trained,"currentEpoch":base_epoch+epochs,"trainingPlanFingerprint":plan["artifactFingerprint"],
        "trainingArtifactFingerprint":artifact["artifactFingerprint"],"graphFingerprint":graph_fp,"labelFingerprint":label_fp,
        "optimizer":"sgd","optimizerMomentum":0.0,"seed":seed,"resumePolicy":"exact-full-batch-stateless-sgd-same-inputs",
        "opaqueSerializedState":False,"isObservedEvidence":False,
    }
    checkpoint["artifactFingerprint"]=_canonical_sha256(checkpoint)
    return {"kind":"gnn-training","trainedModelSpec":trained,"gnnTrainingPlanArtifact":plan,"gnnTrainingArtifact":artifact,"gnnCheckpointArtifact":checkpoint}


def _gnn_checkpoint_create(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_gnn_validate_model_spec(payload.get("modelSpec")); epoch=payload.get("currentEpoch",0)
    if not isinstance(epoch,int) or isinstance(epoch,bool) or epoch<0: raise HTTPException(status_code=400, detail="currentEpoch must be a non-negative integer")
    task=str(payload.get("task") or "").lower()
    if task not in GNN_TRAINING_TASKS: raise HTTPException(status_code=400, detail="unsupported GNN training task")
    cp={"schema":GNN_CHECKPOINT_ARTIFACT_SCHEMA,"kind":"gnn-training-checkpoint","task":task,"trainedModelSpec":spec,
        "currentEpoch":epoch,"trainingPlanFingerprint":str(payload.get("trainingPlanFingerprint") or "")[:128] or None,
        "trainingArtifactFingerprint":str(payload.get("trainingArtifactFingerprint") or "")[:128] or None,
        "graphFingerprint":str(payload.get("graphFingerprint") or "")[:128] or None,"labelFingerprint":str(payload.get("labelFingerprint") or "")[:128] or None,
        "optimizer":"sgd","optimizerMomentum":0.0,"seed":_seed(payload),"resumePolicy":"exact-full-batch-stateless-sgd-same-inputs",
        "opaqueSerializedState":False,"isObservedEvidence":False}
    cp["artifactFingerprint"]=_canonical_sha256(cp); return {"gnnCheckpointArtifact":cp}


def _gnn_checkpoint_resume(payload: dict[str, Any]) -> dict[str, Any]:
    checkpoint=payload.get("checkpoint")
    if not isinstance(checkpoint,dict) or checkpoint.get("schema")!=GNN_CHECKPOINT_ARTIFACT_SCHEMA:
        raise HTTPException(status_code=400, detail=f"checkpoint.schema must be {GNN_CHECKPOINT_ARTIFACT_SCHEMA}")
    if checkpoint.get("optimizer")!="sgd" or checkpoint.get("optimizerMomentum") not in (0,0.0):
        raise HTTPException(status_code=400, detail="v3.34 resume accepts stateless SGD checkpoints only")
    additional=payload.get("additionalEpochs")
    if not isinstance(additional,int) or isinstance(additional,bool) or additional<1 or additional>MAX_GNN_EPOCHS:
        raise HTTPException(status_code=400, detail="additionalEpochs is outside the governed range")
    p=dict(payload); p.pop("checkpoint",None); p.pop("additionalEpochs",None)
    p["modelSpec"]=checkpoint.get("trainedModelSpec"); p["task"]=checkpoint.get("task"); p["epochs"]=additional; p["baseEpoch"]=int(checkpoint.get("currentEpoch") or 0)
    out=_gnn_train(p); out["resumedFromCheckpointFingerprint"]=checkpoint.get("artifactFingerprint")
    out["gnnTrainingArtifact"]["resumedFromCheckpointFingerprint"]=checkpoint.get("artifactFingerprint")
    out["gnnTrainingArtifact"]["artifactFingerprint"]=_canonical_sha256({k:v for k,v in out["gnnTrainingArtifact"].items() if k!="artifactFingerprint"})
    return out


# v3.35.0 GNN Evaluation, Explainability & Graph Embeddings.
GNN_EVALUATION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-evaluation-artifact/1.0"
GNN_CALIBRATION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-calibration-artifact/1.0"
GNN_EXPLAINABILITY_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-explainability-artifact/1.0"
GNN_EMBEDDING_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-embedding-artifact/1.0"
GNN_EMBEDDING_ANALYSIS_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-embedding-analysis-artifact/1.0"
MAX_GNN_EVALUATION_ITEMS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_EVALUATION_ITEMS", "65536")), 262144))
MAX_GNN_CALIBRATION_BINS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_CALIBRATION_BINS", "25")), 100))
MAX_GNN_EMBEDDING_PAIRS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_EMBEDDING_PAIRS", "4096")), 20000))
MAX_GNN_NEIGHBOR_QUERIES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_NEIGHBOR_QUERIES", "128")), 1024))
MAX_GNN_NEIGHBORS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_GNN_NEIGHBORS", "50")), 256))
GNN_EMBEDDING_METRICS = {"cosine", "euclidean", "dot"}


def _gnn_forward_tensor(x: torch.Tensor, edges: list[list[int]], directed: bool, spec: dict[str, Any]) -> torch.Tensor:
    n=int(x.shape[0]); src,dst=_gnn_edge_index(edges,n,directed,spec["addSelfLoops"])
    w=torch.tensor(spec["weights"],dtype=torch.float32,device=x.device); b=torch.tensor(spec["bias"],dtype=torch.float32,device=x.device)
    if spec["adapter"]=="gcn":
        degree=torch.zeros(n,dtype=torch.float32,device=x.device); degree.index_add_(0,dst,torch.ones(dst.numel(),dtype=torch.float32,device=x.device)); degree=torch.clamp(degree,min=1.0)
        coeff=torch.rsqrt(degree[src]*degree[dst]); agg=torch.zeros_like(x); agg.index_add_(0,dst,x[src]*coeff.unsqueeze(1)); y=agg@w+b
    else:
        agg=torch.zeros_like(x); counts=torch.zeros(n,dtype=torch.float32,device=x.device); agg.index_add_(0,dst,x[src]); counts.index_add_(0,dst,torch.ones(dst.numel(),dtype=torch.float32,device=x.device)); agg=agg/torch.clamp(counts,min=1.0).unsqueeze(1); y=torch.cat([x,agg],dim=1)@w+b
    return _gnn_activate(y,spec["activation"])


def _gnn_eval_vectors(payload: dict[str, Any]) -> tuple[str, torch.Tensor, torch.Tensor, list[str], str, dict[str, Any]]:
    task=str(payload.get("task") or "").lower()
    if task not in GNN_TRAINING_TASKS: raise HTTPException(status_code=400,detail="unsupported GNN evaluation task")
    spec=_gnn_validate_model_spec(payload.get("modelSpec")); ids: list[str]=[]; source_fp=""
    if task.startswith("node-"):
        logits, _spec, source_fp, node_ids, _ec, _fc, _dir=_gnn_compute(payload); labels=payload.get("labels")
        if not isinstance(labels,list) or len(labels)!=int(logits.shape[0]): raise HTTPException(status_code=400,detail="node evaluation labels must align with nodes")
        raw_idx=payload.get("evaluationIndices")
        idx=list(range(len(labels))) if raw_idx is None else _gnn_indices(raw_idx,len(labels),"evaluationIndices")
        if len(idx)>MAX_GNN_EVALUATION_ITEMS: raise HTTPException(status_code=413,detail="GNN evaluation item limit exceeded")
        t=torch.tensor(idx,dtype=torch.long,device=logits.device); pred=logits[t]; ids=[node_ids[i] for i in idx]
        if task.endswith("multiclass-classification"): y=torch.tensor([labels[i] for i in idx],dtype=torch.long,device=logits.device)
        else: y=torch.tensor([labels[i] for i in idx],dtype=torch.float32,device=logits.device)
        return task,pred,y,ids,source_fp,spec
    if task.startswith("graph-"):
        graphs=payload.get("graphs")
        if not isinstance(graphs,list) or not graphs or len(graphs)>MAX_GNN_GRAPHS: raise HTTPException(status_code=400,detail="graphs must be a bounded non-empty array")
        raw_idx=payload.get("evaluationIndices"); idx=list(range(len(graphs))) if raw_idx is None else _gnn_indices(raw_idx,len(graphs),"evaluationIndices")
        preds=[]; labels=[]; fps=[]
        for i in idx:
            g=graphs[i]
            if not isinstance(g,dict): raise HTTPException(status_code=400,detail="each graph must be an object")
            z,fp=_gnn_train_logits(g,spec,torch.tensor(spec["weights"],dtype=torch.float32,device=_current_device_name()),torch.tensor(spec["bias"],dtype=torch.float32,device=_current_device_name())); preds.append(z.mean(dim=0)); labels.append(g.get("label")); fps.append(fp); ids.append(str(g.get("graphId") or f"graph-{i}"))
        pred=torch.stack(preds,dim=0)
        y=torch.tensor(labels,dtype=torch.long if task.endswith("multiclass-classification") else torch.float32,device=pred.device)
        return task,pred,y,ids,_canonical_sha256(fps),spec
    logits,spec2,source_fp,node_ids,_ec,_fc,_dir=_gnn_compute(payload); examples=payload.get("linkExamples")
    if not isinstance(examples,list) or not examples or len(examples)>MAX_GNN_EVALUATION_ITEMS: raise HTTPException(status_code=400,detail="linkExamples must be a bounded non-empty array")
    raw_idx=payload.get("evaluationIndices"); idx=list(range(len(examples))) if raw_idx is None else _gnn_indices(raw_idx,len(examples),"evaluationIndices")
    scores=[]; labels=[]
    for i in idx:
        ex=examples[i]
        if not isinstance(ex,dict): raise HTTPException(status_code=400,detail="each link example must be an object")
        a,b,l=ex.get("source"),ex.get("target"),ex.get("label")
        if not isinstance(a,int) or isinstance(a,bool) or not isinstance(b,int) or isinstance(b,bool) or a<0 or b<0 or a>=len(node_ids) or b>=len(node_ids): raise HTTPException(status_code=400,detail="link example node index is invalid")
        if l not in (0,1): raise HTTPException(status_code=400,detail="link example label must be 0 or 1")
        scores.append((logits[a]*logits[b]).sum()/max(1.0,float(spec2["outputFeatures"])**0.5)); labels.append(float(l)); ids.append(f"{node_ids[a]}->{node_ids[b]}")
    return task,torch.stack(scores).reshape(-1,1),torch.tensor(labels,dtype=torch.float32,device=logits.device),ids,source_fp,spec2


def _gnn_metrics(task: str, pred: torch.Tensor, y: torch.Tensor) -> tuple[dict[str, Any], torch.Tensor | None]:
    if task.endswith("regression"):
        v=pred[:,0] if pred.ndim==2 else pred.reshape(-1); yy=y.to(torch.float32).reshape(-1); r=v-yy; mse=float(torch.mean(r*r).item()); mae=float(torch.mean(torch.abs(r)).item()); denom=float(torch.sum((yy-torch.mean(yy))**2).item()); r2=None if denom==0 else float(1.0-float(torch.sum(r*r).item())/denom)
        return {"mse":mse,"rmse":math.sqrt(mse),"mae":mae,"r2":r2},None
    if task.endswith("binary-classification") or task=="link-prediction":
        raw=pred[:,0] if pred.ndim==2 else pred.reshape(-1); prob=torch.sigmoid(raw); yy=y.to(torch.float32).reshape(-1); cls=(prob>=0.5).to(torch.int64); yi=yy.to(torch.int64); tp=int(((cls==1)&(yi==1)).sum()); tn=int(((cls==0)&(yi==0)).sum()); fp=int(((cls==1)&(yi==0)).sum()); fn=int(((cls==0)&(yi==1)).sum()); eps=1e-7; ll=float(-(yy*torch.log(prob.clamp(eps,1-eps))+(1-yy)*torch.log((1-prob).clamp(eps,1-eps))).mean()); pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0; f1=2*pr*rc/(pr+rc) if pr+rc else 0.0
        return {"accuracy":float((cls==yi).to(torch.float32).mean()),"logLoss":ll,"brierScore":float(torch.mean((prob-yy)**2)),"precision":pr,"recall":rc,"f1":f1,"rocAuc":_roc_auc_binary(prob,yy),"confusionMatrix":{"tn":tn,"fp":fp,"fn":fn,"tp":tp}},prob
    if pred.ndim!=2 or int(pred.shape[1])<2: raise HTTPException(status_code=400,detail="multiclass GNN evaluation requires outputFeatures>=2")
    yy=y.to(torch.long).reshape(-1); classes=int(pred.shape[1]); prob=torch.softmax(pred,dim=1); cls=torch.argmax(prob,dim=1); eps=1e-7; ll=float(-torch.log(prob[torch.arange(len(yy),device=prob.device),yy].clamp(eps,1.0)).mean()); confusion=[[int(((yy==a)&(cls==b)).sum()) for b in range(classes)] for a in range(classes)]; f1s=[]
    for c in range(classes):
        tp=confusion[c][c]; fp=sum(confusion[r][c] for r in range(classes) if r!=c); fn=sum(confusion[c][d] for d in range(classes) if d!=c); pr=tp/(tp+fp) if tp+fp else 0.0; rc=tp/(tp+fn) if tp+fn else 0.0; f1s.append(2*pr*rc/(pr+rc) if pr+rc else 0.0)
    return {"accuracy":float((cls==yy).to(torch.float32).mean()),"logLoss":ll,"macroF1":sum(f1s)/classes,"confusionMatrix":confusion},prob


def _gnn_evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    task,pred,y,ids,source_fp,spec=_gnn_eval_vectors(payload); metrics,_=_gnn_metrics(task,pred,y); artifact={"schema":GNN_EVALUATION_ARTIFACT_SCHEMA,"kind":"gnn-evaluation","task":task,"adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceGraphFingerprint":source_fp,"evaluationItemCount":len(ids),"evaluationIdsFingerprint":_canonical_sha256(ids),"metrics":metrics,"labelsPersisted":False,"predictionsPersisted":False,"isObservedEvidence":False}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-evaluation","task":task,"metrics":metrics,"gnnEvaluationArtifact":artifact}


def _gnn_calibration_report(payload: dict[str, Any]) -> dict[str, Any]:
    task,pred,y,ids,source_fp,spec=_gnn_eval_vectors(payload)
    if task.endswith("regression"): raise HTTPException(status_code=400,detail="GNN calibration requires a classification task")
    metrics,prob=_gnn_metrics(task,pred,y); bins=payload.get("bins",10)
    if not isinstance(bins,int) or isinstance(bins,bool) or bins<2 or bins>MAX_GNN_CALIBRATION_BINS: raise HTTPException(status_code=400,detail="bins is outside the governed range")
    if prob is None: raise HTTPException(status_code=400,detail="classification probabilities unavailable")
    if prob.ndim==2:
        conf,cls=torch.max(prob,dim=1); correct=(cls==y.to(torch.long).reshape(-1)).to(torch.float32)
    else:
        conf=torch.maximum(prob,1-prob); cls=(prob>=0.5).to(torch.long); correct=(cls==y.to(torch.long).reshape(-1)).to(torch.float32)
    rows=[]; ece=0.0; mce=0.0; n=max(1,int(conf.numel()))
    for i in range(bins):
        lo=i/bins; hi=(i+1)/bins; mask=(conf>=lo)&(conf<=hi if i==bins-1 else conf<hi); count=int(mask.sum())
        if count: c=float(conf[mask].mean()); a=float(correct[mask].mean()); gap=abs(c-a); ece+=gap*count/n; mce=max(mce,gap); rows.append({"bin":i,"lower":lo,"upper":hi,"count":count,"meanConfidence":c,"accuracy":a,"gap":gap})
    artifact={"schema":GNN_CALIBRATION_ARTIFACT_SCHEMA,"kind":"gnn-calibration","task":task,"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceGraphFingerprint":source_fp,"itemCount":len(ids),"bins":rows,"expectedCalibrationError":ece,"maximumCalibrationError":mce,"brierScore":metrics.get("brierScore"),"labelsPersisted":False,"isObservedEvidence":False}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-calibration","task":task,"expectedCalibrationError":ece,"maximumCalibrationError":mce,"bins":rows,"gnnCalibrationArtifact":artifact}


def _gnn_target(payload: dict[str, Any], node_count: int, output_count: int) -> tuple[int,int]:
    node=payload.get("targetNodeIndex",0); out=payload.get("targetOutputIndex",0)
    if not isinstance(node,int) or isinstance(node,bool) or node<0 or node>=node_count: raise HTTPException(status_code=400,detail="targetNodeIndex is invalid")
    if not isinstance(out,int) or isinstance(out,bool) or out<0 or out>=output_count: raise HTTPException(status_code=400,detail="targetOutputIndex is invalid")
    return node,out


def _gnn_explain_gradient(payload: dict[str, Any]) -> dict[str, Any]:
    x0,edges,node_ids,directed=_graph_components(payload); spec=_gnn_validate_model_spec(payload.get("modelSpec")); x=x0.detach().clone().requires_grad_(True); y=_gnn_forward_tensor(x,edges,directed,spec); node,out=_gnn_target(payload,len(node_ids),int(y.shape[1])); y[node,out].backward(); g=x.grad.detach(); vals=g.cpu().tolist(); artifact={"schema":GNN_EXPLAINABILITY_ARTIFACT_SCHEMA,"kind":"gnn-explainability","method":"input-gradient","targetNodeId":node_ids[node],"targetNodeIndex":node,"targetOutputIndex":out,"modelSpecFingerprint":spec["modelSpecFingerprint"],"graphFingerprint":_graph_fingerprint(payload["nodeFeatures"],edges,node_ids,directed),"attributionFingerprint":_canonical_sha256(vals),"nodeCount":len(node_ids),"featureCount":int(x.shape[1]),"isObservedEvidence":False,"attributionPolicy":"model-derived-sensitivity-not-causal-evidence"}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-explainability","method":"input-gradient","nodeIds":node_ids,"attributions":vals,"gnnExplainabilityArtifact":artifact}


def _gnn_explain_occlusion(payload: dict[str, Any]) -> dict[str, Any]:
    x,edges,node_ids,directed=_graph_components(payload); spec=_gnn_validate_model_spec(payload.get("modelSpec")); base=_gnn_forward_tensor(x,edges,directed,spec); node,out=_gnn_target(payload,len(node_ids),int(base.shape[1])); baseline=float(payload.get("occlusionValue",0.0));
    if not math.isfinite(baseline): raise HTTPException(status_code=400,detail="occlusionValue must be finite")
    scores=[]
    for f in range(int(x.shape[1])):
        xx=x.clone(); xx[:,f]=baseline; yy=_gnn_forward_tensor(xx,edges,directed,spec); scores.append(float((base[node,out]-yy[node,out]).detach().cpu().item()))
    artifact={"schema":GNN_EXPLAINABILITY_ARTIFACT_SCHEMA,"kind":"gnn-explainability","method":"feature-occlusion","targetNodeId":node_ids[node],"targetNodeIndex":node,"targetOutputIndex":out,"modelSpecFingerprint":spec["modelSpecFingerprint"],"graphFingerprint":_graph_fingerprint(payload["nodeFeatures"],edges,node_ids,directed),"featureScores":scores,"occlusionValue":baseline,"isObservedEvidence":False,"attributionPolicy":"model-derived-perturbation-not-causal-evidence"}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-explainability","method":"feature-occlusion","featureScores":scores,"gnnExplainabilityArtifact":artifact}


def _gnn_embedding_body(payload: dict[str, Any]) -> tuple[torch.Tensor,list[str],dict[str,Any],str]:
    y,spec,graph_fp,node_ids,_ec,_fc,_dir=_gnn_compute(payload); norm=str(payload.get("normalization") or "none").lower()
    if norm not in {"none","l2"}: raise HTTPException(status_code=400,detail="normalization must be none or l2")
    z=y.detach()
    if norm=="l2": z=torch.nn.functional.normalize(z,p=2,dim=1,eps=1e-12)
    return z,node_ids,spec,graph_fp


def _gnn_embedding_extract(payload: dict[str, Any]) -> dict[str, Any]:
    z,node_ids,spec,graph_fp=_gnn_embedding_body(payload); nodes=z.cpu().tolist(); pooled=z.mean(dim=0).cpu().tolist(); artifact={"schema":GNN_EMBEDDING_ARTIFACT_SCHEMA,"kind":"gnn-embedding","adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"graphFingerprint":graph_fp,"nodeCount":len(node_ids),"dimensions":int(z.shape[1]),"nodeIdsFingerprint":_canonical_sha256(node_ids),"nodeEmbeddingsFingerprint":_canonical_sha256(nodes),"graphEmbeddingFingerprint":_canonical_sha256(pooled),"normalization":str(payload.get("normalization") or "none").lower(),"isObservedEvidence":False}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-embedding","nodeIds":node_ids,"nodeEmbeddings":nodes,"graphEmbedding":pooled,"gnnEmbeddingArtifact":artifact}


def _gnn_similarity_value(a: torch.Tensor,b: torch.Tensor,metric: str) -> float:
    if metric=="cosine": return float(torch.nn.functional.cosine_similarity(a.reshape(1,-1),b.reshape(1,-1),dim=1,eps=1e-12).item())
    if metric=="euclidean": return float(torch.linalg.vector_norm(a-b).item())
    return float(torch.dot(a,b).item())


def _gnn_embedding_similarity(payload: dict[str, Any]) -> dict[str, Any]:
    z,node_ids,spec,graph_fp=_gnn_embedding_body(payload); metric=str(payload.get("metric") or "cosine").lower()
    if metric not in GNN_EMBEDDING_METRICS: raise HTTPException(status_code=400,detail="unsupported GNN embedding metric")
    pairs=payload.get("pairs")
    if not isinstance(pairs,list) or not pairs or len(pairs)>MAX_GNN_EMBEDDING_PAIRS: raise HTTPException(status_code=400,detail="pairs must be a bounded non-empty array")
    out=[]
    for p in pairs:
        if not isinstance(p,list) or len(p)!=2 or not all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(node_ids) for i in p): raise HTTPException(status_code=400,detail="each pair must contain two valid node indices")
        a,b=p; out.append({"leftIndex":a,"rightIndex":b,"leftNodeId":node_ids[a],"rightNodeId":node_ids[b],"value":_gnn_similarity_value(z[a],z[b],metric)})
    artifact={"schema":GNN_EMBEDDING_ANALYSIS_ARTIFACT_SCHEMA,"kind":"gnn-embedding-similarity","metric":metric,"modelSpecFingerprint":spec["modelSpecFingerprint"],"graphFingerprint":graph_fp,"pairCount":len(out),"resultsFingerprint":_canonical_sha256(out),"isObservedEvidence":False}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-embedding-similarity","metric":metric,"results":out,"gnnEmbeddingAnalysisArtifact":artifact}


def _gnn_embedding_neighbors(payload: dict[str, Any]) -> dict[str, Any]:
    z,node_ids,spec,graph_fp=_gnn_embedding_body(payload); metric=str(payload.get("metric") or "cosine").lower()
    if metric not in GNN_EMBEDDING_METRICS: raise HTTPException(status_code=400,detail="unsupported GNN embedding metric")
    queries=payload.get("queryNodeIndices"); topk=payload.get("topK",5)
    if not isinstance(queries,list) or not queries or len(queries)>MAX_GNN_NEIGHBOR_QUERIES or not all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(node_ids) for i in queries): raise HTTPException(status_code=400,detail="queryNodeIndices must be a bounded array of valid node indices")
    if not isinstance(topk,int) or isinstance(topk,bool) or topk<1 or topk>MAX_GNN_NEIGHBORS: raise HTTPException(status_code=400,detail="topK is outside the governed range")
    results=[]
    for q in queries:
        rows=[]
        for j in range(len(node_ids)):
            if j==q: continue
            value=_gnn_similarity_value(z[q],z[j],metric); rows.append({"nodeIndex":j,"nodeId":node_ids[j],"value":value})
        rows.sort(key=lambda r:r["value"],reverse=(metric!="euclidean")); results.append({"queryNodeIndex":q,"queryNodeId":node_ids[q],"neighbors":rows[:topk]})
    artifact={"schema":GNN_EMBEDDING_ANALYSIS_ARTIFACT_SCHEMA,"kind":"gnn-embedding-neighbors","metric":metric,"modelSpecFingerprint":spec["modelSpecFingerprint"],"graphFingerprint":graph_fp,"queryCount":len(results),"topK":topk,"resultsFingerprint":_canonical_sha256(results),"isObservedEvidence":False}; artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"gnn-embedding-neighbors","metric":metric,"results":results,"gnnEmbeddingAnalysisArtifact":artifact}



# v3.36.0 Computer Vision & Remote Sensing Neural Runtime.
IMAGE_TENSOR_CONTRACT_SCHEMA = "sc-workspace-neural-image-tensor-contract/1.0"
VISION_DATASET_PROJECTION_SCHEMA = "sc-workspace-neural-vision-dataset-projection/1.0"
VISION_MODEL_SPEC_SCHEMA = "sc-workspace-neural-vision-model-spec/1.0"
VISION_EXECUTION_ARTIFACT_SCHEMA = "sc-workspace-neural-vision-execution-artifact/1.0"
VISION_PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-vision-prediction-artifact/1.0"
VISION_TILE_PLAN_SCHEMA = "sc-workspace-neural-vision-tile-plan/1.0"
REMOTE_SENSING_PROJECTION_ARTIFACT_SCHEMA = "sc-workspace-neural-remote-sensing-projection-artifact/1.0"
REMOTE_SENSING_INDEX_ARTIFACT_SCHEMA = "sc-workspace-neural-remote-sensing-index-artifact/1.0"
VISION_ADAPTERS = {"bounded-cnn"}
VISION_ACTIVATIONS = {"identity", "relu", "tanh"}
VISION_TASKS = {"regression", "binary-classification", "multiclass-classification"}
SPECTRAL_INDEX_PRESETS = {
    "ndvi": ("nir", "red"),
    "ndwi": ("green", "nir"),
    "nbr": ("nir", "swir2"),
    "ndmi": ("nir", "swir1"),
}
MAX_VISION_CHANNELS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_CHANNELS", "32")), 128))
MAX_VISION_SIDE = max(8, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_SIDE", "1024")), 4096))
MAX_VISION_ELEMENTS = max(1024, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_ELEMENTS", "1048576")), 8388608))
MAX_VISION_CONV_LAYERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_CONV_LAYERS", "4")), 8))
MAX_VISION_CONV_CHANNELS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_CONV_CHANNELS", "128")), 512))
MAX_VISION_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_PARAMETERS", "500000")), MAX_PARAMETERS))
MAX_VISION_SCENES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_SCENES", "16")), 128))
MAX_VISION_TILES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_VISION_TILES", "4096")), 20000))


def _vision_activation(x: torch.Tensor, name: str) -> torch.Tensor:
    if name == "identity": return x
    if name == "relu": return F.relu(x)
    if name == "tanh": return torch.tanh(x)
    raise HTTPException(status_code=400, detail="unsupported vision activation")


def _vision_image(payload: dict[str, Any], key: str = "imageTensor") -> tuple[torch.Tensor, list[str]]:
    raw = payload.get(key)
    if not isinstance(raw, list) or not raw:
        raise HTTPException(status_code=400, detail=f"{key} must be a non-empty nested array")
    try: x = torch.tensor(raw, dtype=torch.float32, device=_current_device_name())
    except Exception as exc: raise HTTPException(status_code=400, detail=f"{key} must be a rectangular numeric array") from exc
    if x.ndim == 2: x = x.unsqueeze(0)
    if x.ndim != 3: raise HTTPException(status_code=400, detail=f"{key} must have shape [channels,height,width] or [height,width]")
    c,h,w = map(int, x.shape)
    if c < 1 or c > MAX_VISION_CHANNELS or h < 1 or w < 1 or h > MAX_VISION_SIDE or w > MAX_VISION_SIDE or x.numel() > MAX_VISION_ELEMENTS:
        raise HTTPException(status_code=413, detail="vision tensor exceeds governed channel/shape/element limits")
    if not torch.isfinite(x).all(): raise HTTPException(status_code=400, detail="vision tensor values must be finite")
    names = payload.get("bandNames")
    if names is None: names = [f"band-{i+1}" for i in range(c)]
    if not isinstance(names, list) or len(names) != c or any(not isinstance(v, str) or not v.strip() for v in names):
        raise HTTPException(status_code=400, detail="bandNames must align with channels")
    lowered=[v.strip().lower() for v in names]
    if len(set(lowered)) != len(lowered): raise HTTPException(status_code=400, detail="bandNames must be unique")
    return x, [v.strip() for v in names]


def _vision_spatial_context(payload: dict[str, Any]) -> dict[str, Any]:
    ctx={k:payload.get(k) for k in ("sceneId","crs","bbox","transform","capturedAt") if payload.get(k) is not None}
    return {"value":ctx,"fingerprint":_canonical_sha256(ctx)}


def _vision_tensor_contract(payload: dict[str, Any]) -> dict[str, Any]:
    x,names=_vision_image(payload); c,h,w=map(int,x.shape); spatial=_vision_spatial_context(payload)
    body={"schema":IMAGE_TENSOR_CONTRACT_SCHEMA,"kind":"vision-tensor-contract","dtype":"float32","layout":"CHW","channels":c,"height":h,"width":w,"elements":int(x.numel()),"bandNames":names,"tensorFingerprint":_canonical_sha256(x.detach().cpu().tolist()),"spatialContextFingerprint":spatial["fingerprint"],"externalRasterRead":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"vision-tensor-contract","visionTensorContractArtifact":body}


def _vision_dataset_project(payload: dict[str, Any]) -> dict[str, Any]:
    scenes=payload.get("scenes")
    if not isinstance(scenes,list) or not scenes or len(scenes)>MAX_VISION_SCENES: raise HTTPException(status_code=400,detail="scenes must be a bounded non-empty array")
    items=[]; total=0
    for i,scene in enumerate(scenes):
        if not isinstance(scene,dict): raise HTTPException(status_code=400,detail="each scene must be an object")
        x,names=_vision_image(scene); total += int(x.numel())
        if total > MAX_VISION_ELEMENTS*MAX_VISION_SCENES: raise HTTPException(status_code=413,detail="vision dataset projection exceeds aggregate limit")
        spatial=_vision_spatial_context(scene); c,h,w=map(int,x.shape)
        items.append({"sceneId":str(scene.get("sceneId") or f"scene-{i}"),"channels":c,"height":h,"width":w,"bandNames":names,"tensorFingerprint":_canonical_sha256(x.detach().cpu().tolist()),"spatialContextFingerprint":spatial["fingerprint"]})
    artifact={"schema":VISION_DATASET_PROJECTION_SCHEMA,"kind":"vision-dataset-projection","sceneCount":len(items),"totalElements":total,"scenes":items,"externalRasterRead":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"vision-dataset-projection","scenes":items,"visionDatasetProjectionArtifact":artifact}


def _vision_validate_model_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw,dict) or raw.get("schema") != VISION_MODEL_SPEC_SCHEMA: raise HTTPException(status_code=400,detail="modelSpec schema is invalid")
    adapter=str(raw.get("adapter") or "").lower(); in_c=raw.get("inputChannels"); out_f=raw.get("outputFeatures"); layers=raw.get("convLayers")
    if adapter not in VISION_ADAPTERS: raise HTTPException(status_code=400,detail="unsupported vision adapter")
    if not isinstance(in_c,int) or isinstance(in_c,bool) or in_c<1 or in_c>MAX_VISION_CHANNELS: raise HTTPException(status_code=400,detail="inputChannels invalid")
    if not isinstance(out_f,int) or isinstance(out_f,bool) or out_f<1 or out_f>MAX_FEATURES: raise HTTPException(status_code=400,detail="outputFeatures invalid")
    if not isinstance(layers,list) or not layers or len(layers)>MAX_VISION_CONV_LAYERS: raise HTTPException(status_code=400,detail="convLayers must be bounded and non-empty")
    normalized=[]; current=in_c; params=0
    for idx,layer in enumerate(layers):
        if not isinstance(layer,dict): raise HTTPException(status_code=400,detail="each conv layer must be an object")
        oc=layer.get("outChannels"); k=layer.get("kernelSize"); act=str(layer.get("activation") or "relu").lower()
        if not isinstance(oc,int) or isinstance(oc,bool) or oc<1 or oc>MAX_VISION_CONV_CHANNELS: raise HTTPException(status_code=400,detail="outChannels invalid")
        if k not in (1,3,5): raise HTTPException(status_code=400,detail="kernelSize must be 1, 3, or 5")
        if act not in VISION_ACTIVATIONS: raise HTTPException(status_code=400,detail="vision activation invalid")
        weights=layer.get("weights"); bias=layer.get("bias")
        try: wt=torch.tensor(weights,dtype=torch.float32); bt=torch.tensor(bias,dtype=torch.float32)
        except Exception as exc: raise HTTPException(status_code=400,detail="conv weights/bias must be rectangular numeric arrays") from exc
        if tuple(wt.shape)!=(oc,current,k,k) or tuple(bt.shape)!=(oc,): raise HTTPException(status_code=400,detail=f"conv layer {idx} weight/bias shape mismatch")
        if not torch.isfinite(wt).all() or not torch.isfinite(bt).all(): raise HTTPException(status_code=400,detail="vision model parameters must be finite")
        params += wt.numel()+bt.numel(); normalized.append({"outChannels":oc,"kernelSize":k,"padding":k//2,"activation":act,"weights":wt.tolist(),"bias":bt.tolist()}); current=oc
    try: hw=torch.tensor(raw.get("headWeights"),dtype=torch.float32); hb=torch.tensor(raw.get("headBias"),dtype=torch.float32)
    except Exception as exc: raise HTTPException(status_code=400,detail="head weights/bias must be rectangular numeric arrays") from exc
    if tuple(hw.shape)!=(out_f,current) or tuple(hb.shape)!=(out_f,): raise HTTPException(status_code=400,detail="head weight/bias shape mismatch")
    if not torch.isfinite(hw).all() or not torch.isfinite(hb).all(): raise HTTPException(status_code=400,detail="vision head parameters must be finite")
    params += hw.numel()+hb.numel()
    if params > MAX_VISION_PARAMETERS: raise HTTPException(status_code=413,detail="vision model exceeds parameter limit")
    spec={"schema":VISION_MODEL_SPEC_SCHEMA,"adapter":adapter,"inputChannels":in_c,"outputFeatures":out_f,"convLayers":normalized,"headWeights":hw.tolist(),"headBias":hb.tolist(),"parameterCount":int(params)}
    spec["modelSpecFingerprint"]=_canonical_sha256(spec)
    return spec


def _vision_model_summary(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_vision_validate_model_spec(payload.get("modelSpec")); return {"kind":"vision-model-summary","adapter":spec["adapter"],"inputChannels":spec["inputChannels"],"outputFeatures":spec["outputFeatures"],"convLayerCount":len(spec["convLayers"]),"parameterCount":spec["parameterCount"],"modelSpecFingerprint":spec["modelSpecFingerprint"]}


def _vision_forward_body(payload: dict[str, Any]) -> tuple[torch.Tensor, dict[str,Any], str, list[str], list[int]]:
    x,names=_vision_image(payload); spec=_vision_validate_model_spec(payload.get("modelSpec"))
    if int(x.shape[0]) != spec["inputChannels"]: raise HTTPException(status_code=400,detail="image channels do not match modelSpec inputChannels")
    y=x.unsqueeze(0)
    for layer in spec["convLayers"]:
        wt=torch.tensor(layer["weights"],dtype=torch.float32,device=x.device); bt=torch.tensor(layer["bias"],dtype=torch.float32,device=x.device)
        y=F.conv2d(y,wt,bt,padding=int(layer["padding"])); y=_vision_activation(y,layer["activation"])
    pooled=y.mean(dim=(2,3)); hw=torch.tensor(spec["headWeights"],dtype=torch.float32,device=x.device); hb=torch.tensor(spec["headBias"],dtype=torch.float32,device=x.device); logits=pooled@hw.t()+hb
    return logits.squeeze(0),spec,_canonical_sha256(x.detach().cpu().tolist()),names,list(map(int,y.shape))


def _vision_forward(payload: dict[str, Any]) -> dict[str, Any]:
    logits,spec,image_fp,names,feature_shape=_vision_forward_body(payload); values=logits.detach().cpu().tolist(); spatial=_vision_spatial_context(payload)
    artifact={"schema":VISION_EXECUTION_ARTIFACT_SCHEMA,"kind":"vision-forward","adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":image_fp,"spatialContextFingerprint":spatial["fingerprint"],"bandNames":names,"featureMapShape":feature_shape,"outputFeatures":spec["outputFeatures"],"outputFingerprint":_canonical_sha256(values),"isObservedEvidence":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"vision-forward","outputs":values,"visionExecutionArtifact":artifact}


def _vision_infer(payload: dict[str, Any]) -> dict[str, Any]:
    task=str(payload.get("task") or "").lower()
    if task not in VISION_TASKS: raise HTTPException(status_code=400,detail="unsupported vision inference task")
    logits,spec,image_fp,names,_shape=_vision_forward_body(payload); raw=logits.detach().cpu()
    if task=="regression": prediction={"values":raw.tolist()}
    elif task=="binary-classification":
        if raw.numel()!=1: raise HTTPException(status_code=400,detail="binary classification requires outputFeatures=1")
        p=float(torch.sigmoid(raw.reshape(-1)[0])); prediction={"probability":p,"class":int(p>=0.5)}
    else:
        if raw.numel()<2: raise HTTPException(status_code=400,detail="multiclass classification requires outputFeatures>=2")
        prob=torch.softmax(raw.reshape(-1),dim=0); prediction={"probabilities":prob.tolist(),"class":int(torch.argmax(prob))}
    artifact={"schema":VISION_PREDICTION_ARTIFACT_SCHEMA,"kind":"vision-prediction","task":task,"adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":image_fp,"predictionFingerprint":_canonical_sha256(prediction),"bandNames":names,"isObservedEvidence":False,"isEvaluation":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"vision-infer","task":task,"prediction":prediction,"visionPredictionArtifact":artifact}


def _axis_starts(length: int, tile: int, overlap: int) -> list[int]:
    if tile<1 or tile>length or overlap<0 or overlap>=tile: raise HTTPException(status_code=400,detail="invalid tile/overlap dimensions")
    step=tile-overlap; starts=list(range(0,max(1,length-tile+1),step)); last=length-tile
    if not starts or starts[-1]!=last: starts.append(last)
    return sorted(set(starts))


def _vision_tile_plan(payload: dict[str, Any]) -> dict[str, Any]:
    h=payload.get("height"); w=payload.get("width"); th=payload.get("tileHeight"); tw=payload.get("tileWidth"); oh=int(payload.get("overlapHeight",0)); ow=int(payload.get("overlapWidth",0))
    if any(not isinstance(v,int) or isinstance(v,bool) for v in (h,w,th,tw)): raise HTTPException(status_code=400,detail="height/width/tile dimensions must be integers")
    if h<1 or w<1 or h>MAX_VISION_SIDE or w>MAX_VISION_SIDE: raise HTTPException(status_code=400,detail="scene dimensions invalid")
    ys=_axis_starts(h,th,oh); xs=_axis_starts(w,tw,ow); windows=[]
    for y in ys:
        for x in xs:
            windows.append({"tileIndex":len(windows),"y":y,"x":x,"height":th,"width":tw})
            if len(windows)>MAX_VISION_TILES: raise HTTPException(status_code=413,detail="vision tile plan exceeds tile limit")
    artifact={"schema":VISION_TILE_PLAN_SCHEMA,"kind":"vision-tile-plan","height":h,"width":w,"tileHeight":th,"tileWidth":tw,"overlapHeight":oh,"overlapWidth":ow,"tileCount":len(windows),"windowsFingerprint":_canonical_sha256(windows)}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"vision-tile-plan","windows":windows,"visionTilePlanArtifact":artifact}


def _band_index(names: list[str], name: str) -> int:
    lowered=[n.lower() for n in names]; key=str(name).strip().lower()
    if key not in lowered: raise HTTPException(status_code=400,detail=f"band '{name}' not present")
    return lowered.index(key)


def _remote_sensing_band_project(payload: dict[str, Any]) -> dict[str, Any]:
    x,names=_vision_image(payload); selected=payload.get("selectBands")
    if not isinstance(selected,list) or not selected or len(selected)>len(names) or any(not isinstance(v,str) for v in selected): raise HTTPException(status_code=400,detail="selectBands must be a bounded non-empty band-name array")
    idx=[_band_index(names,n) for n in selected]
    if len(set(idx))!=len(idx): raise HTTPException(status_code=400,detail="selectBands must be unique")
    projected=x[idx,:,:].detach().cpu().tolist(); spatial=_vision_spatial_context(payload)
    artifact={"schema":REMOTE_SENSING_PROJECTION_ARTIFACT_SCHEMA,"kind":"remote-sensing-band-projection","sourceBandNames":names,"selectedBandNames":[names[i] for i in idx],"sourceTensorFingerprint":_canonical_sha256(x.detach().cpu().tolist()),"projectedTensorFingerprint":_canonical_sha256(projected),"spatialContextFingerprint":spatial["fingerprint"],"externalRasterRead":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"remote-sensing-band-projection","bandNames":[names[i] for i in idx],"imageTensor":projected,"remoteSensingProjectionArtifact":artifact}


def _remote_sensing_index_compute(payload: dict[str, Any]) -> dict[str, Any]:
    x,names=_vision_image(payload); index_name=str(payload.get("index") or "").lower(); pair=payload.get("bands")
    if index_name in SPECTRAL_INDEX_PRESETS: a_name,b_name=SPECTRAL_INDEX_PRESETS[index_name]
    elif index_name in {"normalized-difference","nd"}:
        if not isinstance(pair,list) or len(pair)!=2 or any(not isinstance(v,str) for v in pair): raise HTTPException(status_code=400,detail="custom normalized difference requires bands=[A,B]")
        a_name,b_name=pair
    else: raise HTTPException(status_code=400,detail="unsupported remote-sensing spectral index")
    a=x[_band_index(names,a_name)]; b=x[_band_index(names,b_name)]; denom=a+b; valid=torch.abs(denom)>1e-12; out=torch.zeros_like(a); out[valid]=(a[valid]-b[valid])/denom[valid]; vals=out.detach().cpu().tolist(); mask=valid.detach().cpu().tolist(); valid_vals=out[valid]
    stats={"validCount":int(valid.sum()),"invalidCount":int((~valid).sum()),"min":float(valid_vals.min()) if valid_vals.numel() else None,"max":float(valid_vals.max()) if valid_vals.numel() else None,"mean":float(valid_vals.mean()) if valid_vals.numel() else None}
    spatial=_vision_spatial_context(payload); artifact={"schema":REMOTE_SENSING_INDEX_ARTIFACT_SCHEMA,"kind":"remote-sensing-spectral-index","index":index_name,"numeratorBand":names[_band_index(names,a_name)],"referenceBand":names[_band_index(names,b_name)],"sourceTensorFingerprint":_canonical_sha256(x.detach().cpu().tolist()),"indexFingerprint":_canonical_sha256({"values":vals,"validMask":mask}),"statistics":stats,"spatialContextFingerprint":spatial["fingerprint"],"isObservedEvidence":False,"interpretationPolicy":"derived-spectral-index-not-ground-truth"}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact); return {"kind":"remote-sensing-spectral-index","index":index_name,"values":vals,"validMask":mask,"statistics":stats,"remoteSensingIndexArtifact":artifact}


# v3.37 Temporal Deep Learning & Sequence Models
SEQUENCE_TENSOR_CONTRACT_SCHEMA = "sc-workspace-neural-sequence-tensor-contract/1.0"
SEQUENCE_WINDOW_PLAN_SCHEMA = "sc-workspace-neural-sequence-window-plan/1.0"
SEQUENCE_DATASET_PROJECTION_SCHEMA = "sc-workspace-neural-sequence-dataset-projection/1.0"
SEQUENCE_MODEL_SPEC_SCHEMA = "sc-workspace-neural-sequence-model-spec/1.0"
SEQUENCE_EXECUTION_ARTIFACT_SCHEMA = "sc-workspace-neural-sequence-execution-artifact/1.0"
SEQUENCE_PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-sequence-prediction-artifact/1.0"
SEQUENCE_EMBEDDING_ARTIFACT_SCHEMA = "sc-workspace-neural-sequence-embedding-artifact/1.0"
SEQUENCE_FORECAST_ARTIFACT_SCHEMA = "sc-workspace-neural-sequence-forecast-artifact/1.0"
SEQUENCE_ADAPTERS = {"tanh-rnn", "gru"}
SEQUENCE_TASKS = {"regression", "binary-classification", "multiclass-classification"}
MAX_SEQUENCE_STEPS = max(2, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_STEPS", "4096")), 32768))
MAX_SEQUENCE_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_FEATURES", "512")), 4096))
MAX_SEQUENCE_HIDDEN = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_HIDDEN", "512")), 2048))
MAX_SEQUENCE_OUTPUTS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_OUTPUTS", "512")), 4096))
MAX_SEQUENCE_WINDOWS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_WINDOWS", "4096")), 20000))
MAX_SEQUENCE_HORIZON = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_HORIZON", "64")), 512))
MAX_SEQUENCE_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SEQUENCE_PARAMETERS", "500000")), MAX_PARAMETERS))


def _sequence_tensor(payload: dict[str, Any], key: str = "sequenceTensor") -> tuple[torch.Tensor, list[str], list[Any]]:
    raw = payload.get(key)
    if not isinstance(raw, list) or not raw:
        raise HTTPException(status_code=400, detail=f"{key} must be a non-empty [steps,features] array")
    try:
        x = torch.tensor(raw, dtype=torch.float32, device=_current_device_name())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"{key} must be a rectangular numeric array") from exc
    if x.ndim != 2:
        raise HTTPException(status_code=400, detail=f"{key} must have rank 2 [steps,features]")
    steps, features = int(x.shape[0]), int(x.shape[1])
    if steps < 1 or steps > MAX_SEQUENCE_STEPS or features < 1 or features > MAX_SEQUENCE_FEATURES:
        raise HTTPException(status_code=413, detail="sequence tensor exceeds bounded shape limits")
    if x.numel() > MAX_TENSOR_ELEMENTS or not bool(torch.isfinite(x).all()):
        raise HTTPException(status_code=400, detail="sequence tensor exceeds element limit or contains non-finite values")
    names = payload.get("featureNames")
    if names is None:
        names = [f"feature-{i}" for i in range(features)]
    if not isinstance(names, list) or len(names) != features or any(not isinstance(n, str) or not n.strip() for n in names):
        raise HTTPException(status_code=400, detail="featureNames must match sequence feature count")
    names = [str(n).strip()[:128] for n in names]
    timestamps = payload.get("timestamps") or []
    if timestamps and (not isinstance(timestamps, list) or len(timestamps) != steps):
        raise HTTPException(status_code=400, detail="timestamps must be omitted or match sequence length")
    return x, names, list(timestamps)


def _sequence_tensor_contract(payload: dict[str, Any]) -> dict[str, Any]:
    x, names, timestamps = _sequence_tensor(payload)
    body = {
        "schema": SEQUENCE_TENSOR_CONTRACT_SCHEMA,
        "kind": "sequence-tensor-contract",
        "layout": "TF",
        "steps": int(x.shape[0]),
        "features": int(x.shape[1]),
        "featureNames": names,
        "timestampsPresent": bool(timestamps),
        "sequenceFingerprint": _canonical_sha256(_tensor_json(x)),
        "timestampFingerprint": _canonical_sha256(timestamps) if timestamps else None,
        "externalSequenceRead": False,
    }
    body["artifactFingerprint"] = _canonical_sha256(body)
    return {"kind": "sequence-tensor-contract", "sequenceTensorContractArtifact": body}


def _sequence_window_plan(payload: dict[str, Any]) -> dict[str, Any]:
    length = int(payload.get("length") or 0)
    window = int(payload.get("windowLength") or 0)
    horizon = int(payload.get("horizon") or 1)
    stride = int(payload.get("stride") or 1)
    if length < 2 or length > MAX_SEQUENCE_STEPS:
        raise HTTPException(status_code=400, detail="length is outside bounded sequence limits")
    if window < 1 or window >= length:
        raise HTTPException(status_code=400, detail="windowLength must be positive and less than sequence length")
    if horizon < 1 or horizon > MAX_SEQUENCE_HORIZON or window + horizon > length:
        raise HTTPException(status_code=400, detail="horizon is invalid for the requested sequence")
    if stride < 1 or stride > window:
        raise HTTPException(status_code=400, detail="stride must be between 1 and windowLength")
    windows=[]
    start=0
    while start + window + horizon <= length:
        windows.append({"inputStart":start,"inputEnd":start+window,"targetStart":start+window,"targetEnd":start+window+horizon})
        if len(windows) > MAX_SEQUENCE_WINDOWS:
            raise HTTPException(status_code=413, detail="sequence window plan exceeds bounded window count")
        start += stride
    body={"schema":SEQUENCE_WINDOW_PLAN_SCHEMA,"kind":"sequence-window-plan","length":length,"windowLength":window,"horizon":horizon,"stride":stride,"windowCount":len(windows),"windowsFingerprint":_canonical_sha256(windows),"deterministic":True}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"sequence-window-plan","windows":windows,"sequenceWindowPlanArtifact":body}


def _sequence_dataset_project(payload: dict[str, Any]) -> dict[str, Any]:
    x,names,timestamps=_sequence_tensor(payload)
    plan=_sequence_window_plan({"length":int(x.shape[0]),"windowLength":payload.get("windowLength",8),"horizon":payload.get("horizon",1),"stride":payload.get("stride",1)})
    windows=[]; targets=[]; time_windows=[]
    for w in plan["windows"]:
        windows.append(_tensor_json(x[w["inputStart"]:w["inputEnd"]]))
        targets.append(_tensor_json(x[w["targetStart"]:w["targetEnd"]]))
        if timestamps:
            time_windows.append({"inputs":timestamps[w["inputStart"]:w["inputEnd"]],"targets":timestamps[w["targetStart"]:w["targetEnd"]]})
    body={"schema":SEQUENCE_DATASET_PROJECTION_SCHEMA,"kind":"sequence-dataset-projection","featureNames":names,"windowLength":plan["sequenceWindowPlanArtifact"]["windowLength"],"horizon":plan["sequenceWindowPlanArtifact"]["horizon"],"stride":plan["sequenceWindowPlanArtifact"]["stride"],"windowCount":len(windows),"sourceSequenceFingerprint":_canonical_sha256(_tensor_json(x)),"windowsFingerprint":_canonical_sha256(windows),"targetsFingerprint":_canonical_sha256(targets),"timestampsPresent":bool(timestamps),"externalSequenceRead":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"sequence-dataset-projection","windows":windows,"targets":targets,"timestampWindows":time_windows,"sequenceDatasetProjectionArtifact":body}


def _sequence_weight(value: Any, rows: int, cols: int, name: str) -> torch.Tensor:
    t=_tensor(value,name=name,dtype_name="float32",ndim=2)
    if list(t.shape)!=[rows,cols]:
        raise HTTPException(status_code=400, detail=f"{name} shape must be [{rows},{cols}]")
    return t


def _sequence_bias(value: Any, size: int, name: str) -> torch.Tensor:
    t=_tensor(value,name=name,dtype_name="float32",ndim=1)
    if list(t.shape)!=[size]:
        raise HTTPException(status_code=400, detail=f"{name} shape must be [{size}]")
    return t


def _sequence_validate_model_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw,dict) or raw.get("schema") != SEQUENCE_MODEL_SPEC_SCHEMA:
        raise HTTPException(status_code=400, detail="modelSpec schema is invalid")
    adapter=str(raw.get("adapter") or "")
    if adapter not in SEQUENCE_ADAPTERS:
        raise HTTPException(status_code=400, detail="unsupported sequence adapter")
    f=int(raw.get("inputFeatures") or 0); h=int(raw.get("hiddenFeatures") or 0); o=int(raw.get("outputFeatures") or 0)
    if f<1 or f>MAX_SEQUENCE_FEATURES or h<1 or h>MAX_SEQUENCE_HIDDEN or o<1 or o>MAX_SEQUENCE_OUTPUTS:
        raise HTTPException(status_code=400, detail="sequence model dimensions are invalid")
    spec={"schema":SEQUENCE_MODEL_SPEC_SCHEMA,"adapter":adapter,"inputFeatures":f,"hiddenFeatures":h,"outputFeatures":o}
    params=0
    if adapter=="tanh-rnn":
        wi=_sequence_weight(raw.get("inputWeights"),h,f,"inputWeights"); wh=_sequence_weight(raw.get("recurrentWeights"),h,h,"recurrentWeights"); b=_sequence_bias(raw.get("hiddenBias"),h,"hiddenBias")
        spec.update(inputWeights=_tensor_json(wi),recurrentWeights=_tensor_json(wh),hiddenBias=_tensor_json(b)); params += h*f+h*h+h
    else:
        for gate,prefix in (("update","update"),("reset","reset"),("candidate","candidate")):
            wi=_sequence_weight(raw.get(prefix+"InputWeights"),h,f,prefix+"InputWeights"); wh=_sequence_weight(raw.get(prefix+"RecurrentWeights"),h,h,prefix+"RecurrentWeights"); b=_sequence_bias(raw.get(prefix+"Bias"),h,prefix+"Bias")
            spec[prefix+"InputWeights"]=_tensor_json(wi); spec[prefix+"RecurrentWeights"]=_tensor_json(wh); spec[prefix+"Bias"]=_tensor_json(b); params += h*f+h*h+h
    ow=_sequence_weight(raw.get("outputWeights"),o,h,"outputWeights"); ob=_sequence_bias(raw.get("outputBias"),o,"outputBias")
    spec["outputWeights"]=_tensor_json(ow); spec["outputBias"]=_tensor_json(ob); params += o*h+o
    if params > MAX_SEQUENCE_PARAMETERS:
        raise HTTPException(status_code=413, detail="sequence model exceeds parameter limit")
    spec["parameterCount"]=int(params)
    spec["modelSpecFingerprint"]=_canonical_sha256(spec)
    return spec


def _sequence_model_summary(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_sequence_validate_model_spec(payload.get("modelSpec"))
    return {"kind":"sequence-model-summary","adapter":spec["adapter"],"inputFeatures":spec["inputFeatures"],"hiddenFeatures":spec["hiddenFeatures"],"outputFeatures":spec["outputFeatures"],"parameterCount":spec["parameterCount"],"modelSpecFingerprint":spec["modelSpecFingerprint"]}


def _sequence_step(spec: dict[str, Any], x: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
    if spec["adapter"]=="tanh-rnn":
        wi=torch.tensor(spec["inputWeights"],dtype=torch.float32,device=_current_device_name()); wh=torch.tensor(spec["recurrentWeights"],dtype=torch.float32,device=_current_device_name()); b=torch.tensor(spec["hiddenBias"],dtype=torch.float32,device=_current_device_name())
        return torch.tanh(wi @ x + wh @ h + b)
    def gate(prefix: str):
        wi=torch.tensor(spec[prefix+"InputWeights"],dtype=torch.float32,device=_current_device_name()); wh=torch.tensor(spec[prefix+"RecurrentWeights"],dtype=torch.float32,device=_current_device_name()); b=torch.tensor(spec[prefix+"Bias"],dtype=torch.float32,device=_current_device_name())
        return wi,wh,b
    zwi,zwh,zb=gate("update"); rwi,rwh,rb=gate("reset"); nwi,nwh,nb=gate("candidate")
    z=torch.sigmoid(zwi@x+zwh@h+zb); r=torch.sigmoid(rwi@x+rwh@h+rb); n=torch.tanh(nwi@x+nwh@(r*h)+nb)
    return (1.0-z)*n+z*h


def _sequence_forward_body(payload: dict[str, Any]) -> tuple[torch.Tensor,torch.Tensor,dict[str,Any],str,list[str],list[Any]]:
    x,names,timestamps=_sequence_tensor(payload); spec=_sequence_validate_model_spec(payload.get("modelSpec"))
    if int(x.shape[1]) != spec["inputFeatures"]:
        raise HTTPException(status_code=400, detail="sequence feature count does not match modelSpec inputFeatures")
    h=torch.zeros(spec["hiddenFeatures"],dtype=torch.float32,device=_current_device_name())
    for t in range(int(x.shape[0])): h=_sequence_step(spec,x[t],h)
    ow=torch.tensor(spec["outputWeights"],dtype=torch.float32,device=_current_device_name()); ob=torch.tensor(spec["outputBias"],dtype=torch.float32,device=_current_device_name()); out=ow@h+ob
    return out,h,spec,_canonical_sha256(_tensor_json(x)),names,timestamps


def _sequence_forward(payload: dict[str, Any]) -> dict[str, Any]:
    out,h,spec,seq_fp,names,timestamps=_sequence_forward_body(payload); vals=_tensor_json(out)
    artifact={"schema":SEQUENCE_EXECUTION_ARTIFACT_SCHEMA,"kind":"sequence-forward","adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceSequenceFingerprint":seq_fp,"steps":len(payload.get("sequenceTensor") or []),"featureNames":names,"hiddenFingerprint":_canonical_sha256(_tensor_json(h)),"outputFingerprint":_canonical_sha256(vals),"isObservedEvidence":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"sequence-forward","outputs":vals,"hiddenState":_tensor_json(h),"sequenceExecutionArtifact":artifact}


def _sequence_infer(payload: dict[str, Any]) -> dict[str, Any]:
    task=str(payload.get("task") or "regression")
    if task not in SEQUENCE_TASKS: raise HTTPException(status_code=400,detail="unsupported sequence inference task")
    out,h,spec,seq_fp,names,timestamps=_sequence_forward_body(payload)
    if task=="regression": prediction={"values":_tensor_json(out)}
    elif task=="binary-classification":
        if out.numel()!=1: raise HTTPException(status_code=400,detail="binary classification requires outputFeatures=1")
        p=float(torch.sigmoid(out[0]).item()); prediction={"probability":p,"label":int(p>=0.5)}
    else:
        probs=torch.softmax(out,dim=0); prediction={"probabilities":_tensor_json(probs),"label":int(torch.argmax(probs).item())}
    artifact={"schema":SEQUENCE_PREDICTION_ARTIFACT_SCHEMA,"kind":"sequence-prediction","task":task,"adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceSequenceFingerprint":seq_fp,"predictionFingerprint":_canonical_sha256(prediction),"isObservedEvidence":False,"isEvaluation":False,"predictionPolicy":"model-derived-sequence-inference"}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"sequence-inference","prediction":prediction,"sequencePredictionArtifact":artifact}


def _sequence_embedding_extract(payload: dict[str, Any]) -> dict[str, Any]:
    out,h,spec,seq_fp,names,timestamps=_sequence_forward_body(payload); emb=_tensor_json(h)
    artifact={"schema":SEQUENCE_EMBEDDING_ARTIFACT_SCHEMA,"kind":"sequence-embedding","adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceSequenceFingerprint":seq_fp,"dimensions":len(emb),"embeddingFingerprint":_canonical_sha256(emb),"isObservedEvidence":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"sequence-embedding-extract","embedding":emb,"sequenceEmbeddingArtifact":artifact}


def _sequence_forecast(payload: dict[str, Any]) -> dict[str, Any]:
    x,names,timestamps=_sequence_tensor(payload); spec=_sequence_validate_model_spec(payload.get("modelSpec")); horizon=int(payload.get("forecastHorizon") or 1)
    if horizon<1 or horizon>MAX_SEQUENCE_HORIZON: raise HTTPException(status_code=400,detail="forecastHorizon exceeds bounded limit")
    if spec["outputFeatures"] != spec["inputFeatures"] and horizon>1: raise HTTPException(status_code=400,detail="recursive multi-step forecast requires outputFeatures=inputFeatures")
    current=x.clone(); values=[]
    for _ in range(horizon):
        local=dict(payload); local["sequenceTensor"]=_tensor_json(current); out,h,_,_,_,_=_sequence_forward_body(local); step=_tensor_json(out); values.append(step)
        if horizon>1: current=torch.cat([current[1:],out.reshape(1,-1)],dim=0)
    source_fp=_canonical_sha256(_tensor_json(x))
    artifact={"schema":SEQUENCE_FORECAST_ARTIFACT_SCHEMA,"kind":"sequence-forecast","adapter":spec["adapter"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"sourceSequenceFingerprint":source_fp,"forecastHorizon":horizon,"forecastFingerprint":_canonical_sha256(values),"isObservedEvidence":False,"uncertaintySemantics":"point-forecast-only-no-calibrated-uncertainty","recursive":horizon>1}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"sequence-forecast","forecast":values,"sequenceForecastArtifact":artifact}


# v3.38 Multimodal Neural Runtime
MULTIMODAL_SAMPLE_CONTRACT_SCHEMA = "sc-workspace-neural-multimodal-sample-contract/1.0"
MULTIMODAL_DATASET_PROJECTION_SCHEMA = "sc-workspace-neural-multimodal-dataset-projection/1.0"
MULTIMODAL_MODEL_SPEC_SCHEMA = "sc-workspace-neural-multimodal-model-spec/1.0"
MULTIMODAL_FUSION_ARTIFACT_SCHEMA = "sc-workspace-neural-multimodal-fusion-artifact/1.0"
MULTIMODAL_REPRESENTATION_ARTIFACT_SCHEMA = "sc-workspace-neural-multimodal-representation-artifact/1.0"
MULTIMODAL_EXECUTION_ARTIFACT_SCHEMA = "sc-workspace-neural-multimodal-execution-artifact/1.0"
MULTIMODAL_PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-multimodal-prediction-artifact/1.0"
MULTIMODAL_SIMILARITY_ARTIFACT_SCHEMA = "sc-workspace-neural-multimodal-similarity-artifact/1.0"
MULTIMODAL_FUSION_MODES = {"concat", "weighted-mean"}
MULTIMODAL_TASKS = {"regression", "binary-classification", "multiclass-classification"}
MULTIMODAL_SIMILARITY_METRICS = {"cosine", "euclidean", "dot"}
MAX_MULTIMODAL_SAMPLES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_MULTIMODAL_SAMPLES", "256")), 2048))
MAX_MULTIMODAL_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_MULTIMODAL_FEATURES", "1024")), 4096))
MAX_MULTIMODAL_PARAMETERS = max(1, min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_MULTIMODAL_PARAMETERS", "750000")), MAX_PARAMETERS))


def _multimodal_sample_contract(payload: dict[str, Any]) -> dict[str, Any]:
    image, band_names = _vision_image(payload)
    sequence, feature_names, timestamps = _sequence_tensor(payload)
    spatial = _vision_spatial_context(payload)
    alignment = str(payload.get("alignmentPolicy") or "operator-declared").strip().lower()
    if alignment not in {"operator-declared", "paired-sample", "same-observation-window"}:
        raise HTTPException(status_code=400, detail="unsupported multimodal alignmentPolicy")
    sample_id = payload.get("sampleId")
    if sample_id is not None and (not isinstance(sample_id, str) or not sample_id.strip() or len(sample_id) > 256):
        raise HTTPException(status_code=400, detail="sampleId must be a bounded non-empty string when supplied")
    image_fp = _canonical_sha256(_tensor_json(image))
    sequence_fp = _canonical_sha256(_tensor_json(sequence))
    body = {
        "schema": MULTIMODAL_SAMPLE_CONTRACT_SCHEMA,
        "kind": "multimodal-sample-contract",
        "modalities": ["vision", "sequence"],
        "sampleId": sample_id.strip() if isinstance(sample_id, str) else None,
        "alignmentPolicy": alignment,
        "alignmentDeclaredByOperator": True,
        "imageTensorFingerprint": image_fp,
        "sequenceTensorFingerprint": sequence_fp,
        "spatialContextFingerprint": spatial["fingerprint"],
        "imageShape": list(map(int, image.shape)),
        "sequenceShape": list(map(int, sequence.shape)),
        "bandNames": band_names,
        "featureNames": feature_names,
        "timestampsPresent": bool(timestamps),
        "externalModalityRead": False,
        "isObservedEvidence": False,
    }
    body["sampleFingerprint"] = _canonical_sha256({"image": image_fp, "sequence": sequence_fp, "alignment": alignment, "sampleId": body["sampleId"]})
    body["artifactFingerprint"] = _canonical_sha256(body)
    return {"kind": "multimodal-sample-contract", "multimodalSampleContractArtifact": body}


def _multimodal_dataset_project(payload: dict[str, Any]) -> dict[str, Any]:
    samples = payload.get("samples")
    if not isinstance(samples, list) or not samples or len(samples) > MAX_MULTIMODAL_SAMPLES:
        raise HTTPException(status_code=400, detail="samples must be a bounded non-empty array")
    projected=[]
    for idx, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise HTTPException(status_code=400, detail="each multimodal sample must be an object")
        c=_multimodal_sample_contract(sample)["multimodalSampleContractArtifact"]
        projected.append({"sampleIndex":idx,"sampleId":c.get("sampleId"),"sampleFingerprint":c["sampleFingerprint"],"imageTensorFingerprint":c["imageTensorFingerprint"],"sequenceTensorFingerprint":c["sequenceTensorFingerprint"],"alignmentPolicy":c["alignmentPolicy"]})
    body={
        "schema": MULTIMODAL_DATASET_PROJECTION_SCHEMA,
        "kind": "multimodal-dataset-projection",
        "modalities": ["vision", "sequence"],
        "sampleCount": len(projected),
        "samplesFingerprint": _canonical_sha256(projected),
        "alignmentSemantics": "operator-declared-per-sample",
        "externalModalityRead": False,
        "isObservedEvidence": False,
    }
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"multimodal-dataset-projection","samples":projected,"multimodalDatasetProjectionArtifact":body}


def _multimodal_validate_model_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("schema") != MULTIMODAL_MODEL_SPEC_SCHEMA:
        raise HTTPException(status_code=400, detail="multimodal modelSpec schema is invalid")
    vision=_vision_validate_model_spec(raw.get("visionModelSpec"))
    sequence=_sequence_validate_model_spec(raw.get("sequenceModelSpec"))
    mode=str(raw.get("fusionMode") or "concat").lower()
    if mode not in MULTIMODAL_FUSION_MODES:
        raise HTTPException(status_code=400, detail="unsupported multimodal fusionMode")
    vision_dim=int(vision["outputFeatures"]); sequence_dim=int(sequence["hiddenFeatures"])
    if mode=="concat":
        fused_dim=vision_dim+sequence_dim; weights=None
    else:
        if vision_dim != sequence_dim:
            raise HTTPException(status_code=400, detail="weighted-mean fusion requires equal vision and sequence representation dimensions")
        raw_weights=raw.get("fusionWeights", [0.5,0.5])
        if not isinstance(raw_weights,list) or len(raw_weights)!=2:
            raise HTTPException(status_code=400, detail="fusionWeights must contain [visionWeight, sequenceWeight]")
        try: weights=[float(raw_weights[0]),float(raw_weights[1])]
        except Exception as exc: raise HTTPException(status_code=400,detail="fusionWeights must be numeric") from exc
        if any((not math.isfinite(v) or v<0) for v in weights) or sum(weights)<=0:
            raise HTTPException(status_code=400, detail="fusionWeights must be finite, non-negative, and have positive sum")
        total=sum(weights); weights=[v/total for v in weights]; fused_dim=vision_dim
    if fused_dim < 1 or fused_dim > MAX_MULTIMODAL_FEATURES:
        raise HTTPException(status_code=413, detail="multimodal fused representation exceeds bounded dimension")
    out_f=raw.get("outputFeatures")
    if not isinstance(out_f,int) or isinstance(out_f,bool) or out_f<1 or out_f>MAX_FEATURES:
        raise HTTPException(status_code=400, detail="multimodal outputFeatures invalid")
    try:
        hw=torch.tensor(raw.get("headWeights"),dtype=torch.float32); hb=torch.tensor(raw.get("headBias"),dtype=torch.float32)
    except Exception as exc:
        raise HTTPException(status_code=400,detail="multimodal head weights/bias must be rectangular numeric arrays") from exc
    if tuple(hw.shape)!=(out_f,fused_dim) or tuple(hb.shape)!=(out_f,):
        raise HTTPException(status_code=400,detail=f"multimodal head shape must be [{out_f},{fused_dim}] plus [{out_f}]")
    if not torch.isfinite(hw).all() or not torch.isfinite(hb).all():
        raise HTTPException(status_code=400,detail="multimodal head parameters must be finite")
    params=int(vision["parameterCount"])+int(sequence["parameterCount"])+int(hw.numel()+hb.numel())
    if params>MAX_MULTIMODAL_PARAMETERS:
        raise HTTPException(status_code=413,detail="multimodal model exceeds parameter limit")
    spec={"schema":MULTIMODAL_MODEL_SPEC_SCHEMA,"visionModelSpec":vision,"sequenceModelSpec":sequence,"fusionMode":mode,"fusionWeights":weights,"visionRepresentationFeatures":vision_dim,"sequenceRepresentationFeatures":sequence_dim,"fusedFeatures":fused_dim,"outputFeatures":out_f,"headWeights":hw.tolist(),"headBias":hb.tolist(),"parameterCount":params}
    spec["modelSpecFingerprint"]=_canonical_sha256(spec)
    return spec


def _multimodal_model_summary(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_multimodal_validate_model_spec(payload.get("modelSpec"))
    return {"kind":"multimodal-model-summary","modalities":["vision","sequence"],"fusionMode":spec["fusionMode"],"visionAdapter":spec["visionModelSpec"]["adapter"],"sequenceAdapter":spec["sequenceModelSpec"]["adapter"],"visionRepresentationFeatures":spec["visionRepresentationFeatures"],"sequenceRepresentationFeatures":spec["sequenceRepresentationFeatures"],"fusedFeatures":spec["fusedFeatures"],"outputFeatures":spec["outputFeatures"],"parameterCount":spec["parameterCount"],"modelSpecFingerprint":spec["modelSpecFingerprint"]}


def _multimodal_encode(payload: dict[str, Any], spec: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str,Any]]:
    v_payload=dict(payload); v_payload["modelSpec"]=spec["visionModelSpec"]
    s_payload=dict(payload); s_payload["modelSpec"]=spec["sequenceModelSpec"]
    vision_out,_,image_fp,band_names,_shape=_vision_forward_body(v_payload)
    _seq_out,sequence_hidden,_,sequence_fp,feature_names,timestamps=_sequence_forward_body(s_payload)
    vision_rep=vision_out.reshape(-1); sequence_rep=sequence_hidden.reshape(-1)
    if spec["fusionMode"]=="concat":
        fused=torch.cat([vision_rep,sequence_rep],dim=0)
    else:
        w=spec["fusionWeights"]; fused=vision_rep*float(w[0])+sequence_rep*float(w[1])
    if int(fused.numel()) != spec["fusedFeatures"] or not bool(torch.isfinite(fused).all()):
        raise HTTPException(status_code=500,detail="multimodal fused representation violated runtime contract")
    context={"imageTensorFingerprint":image_fp,"sequenceTensorFingerprint":sequence_fp,"bandNames":band_names,"featureNames":feature_names,"timestampsPresent":bool(timestamps)}
    return vision_rep,sequence_rep,fused,context


def _multimodal_embedding_fuse(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_multimodal_validate_model_spec(payload.get("modelSpec")); v,s,fused,ctx=_multimodal_encode(payload,spec); vals=_tensor_json(fused)
    artifact={"schema":MULTIMODAL_FUSION_ARTIFACT_SCHEMA,"kind":"multimodal-fusion","fusionMode":spec["fusionMode"],"fusionWeights":spec["fusionWeights"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":ctx["imageTensorFingerprint"],"sequenceTensorFingerprint":ctx["sequenceTensorFingerprint"],"visionRepresentationFingerprint":_canonical_sha256(_tensor_json(v)),"sequenceRepresentationFingerprint":_canonical_sha256(_tensor_json(s)),"fusedFeatures":len(vals),"fusedEmbeddingFingerprint":_canonical_sha256(vals),"isObservedEvidence":False,"fusionSemantics":"model-derived-representation-fusion"}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"multimodal-embedding-fuse","fusedEmbedding":vals,"multimodalFusionArtifact":artifact}


def _multimodal_representation_extract(payload: dict[str, Any]) -> dict[str, Any]:
    spec=_multimodal_validate_model_spec(payload.get("modelSpec")); v,s,fused,ctx=_multimodal_encode(payload,spec)
    vr=_tensor_json(v); sr=_tensor_json(s); fr=_tensor_json(fused)
    artifact={"schema":MULTIMODAL_REPRESENTATION_ARTIFACT_SCHEMA,"kind":"multimodal-representation","fusionMode":spec["fusionMode"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":ctx["imageTensorFingerprint"],"sequenceTensorFingerprint":ctx["sequenceTensorFingerprint"],"visionRepresentationFingerprint":_canonical_sha256(vr),"sequenceRepresentationFingerprint":_canonical_sha256(sr),"fusedRepresentationFingerprint":_canonical_sha256(fr),"visionDimensions":len(vr),"sequenceDimensions":len(sr),"fusedDimensions":len(fr),"isObservedEvidence":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"multimodal-representation-extract","visionRepresentation":vr,"sequenceRepresentation":sr,"fusedRepresentation":fr,"multimodalRepresentationArtifact":artifact}


def _multimodal_forward_body(payload: dict[str, Any]) -> tuple[torch.Tensor,dict[str,Any],dict[str,Any],torch.Tensor]:
    spec=_multimodal_validate_model_spec(payload.get("modelSpec")); _v,_s,fused,ctx=_multimodal_encode(payload,spec)
    hw=torch.tensor(spec["headWeights"],dtype=torch.float32,device=_current_device_name()); hb=torch.tensor(spec["headBias"],dtype=torch.float32,device=_current_device_name())
    out=hw@fused+hb
    return out,spec,ctx,fused


def _multimodal_forward(payload: dict[str, Any]) -> dict[str, Any]:
    out,spec,ctx,fused=_multimodal_forward_body(payload); vals=_tensor_json(out)
    artifact={"schema":MULTIMODAL_EXECUTION_ARTIFACT_SCHEMA,"kind":"multimodal-forward","modalities":["vision","sequence"],"fusionMode":spec["fusionMode"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":ctx["imageTensorFingerprint"],"sequenceTensorFingerprint":ctx["sequenceTensorFingerprint"],"fusedRepresentationFingerprint":_canonical_sha256(_tensor_json(fused)),"outputFingerprint":_canonical_sha256(vals),"outputFeatures":spec["outputFeatures"],"isObservedEvidence":False}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"multimodal-forward","outputs":vals,"multimodalExecutionArtifact":artifact}


def _multimodal_infer(payload: dict[str, Any]) -> dict[str, Any]:
    task=str(payload.get("task") or "regression").lower()
    if task not in MULTIMODAL_TASKS: raise HTTPException(status_code=400,detail="unsupported multimodal inference task")
    out,spec,ctx,fused=_multimodal_forward_body(payload)
    if task=="regression": prediction={"values":_tensor_json(out)}
    elif task=="binary-classification":
        if out.numel()!=1: raise HTTPException(status_code=400,detail="binary multimodal classification requires outputFeatures=1")
        p=float(torch.sigmoid(out.reshape(-1)[0])); prediction={"probability":p,"label":int(p>=0.5)}
    else:
        if out.numel()<2: raise HTTPException(status_code=400,detail="multiclass multimodal classification requires outputFeatures>=2")
        probs=torch.softmax(out.reshape(-1),dim=0); prediction={"probabilities":_tensor_json(probs),"label":int(torch.argmax(probs).item())}
    artifact={"schema":MULTIMODAL_PREDICTION_ARTIFACT_SCHEMA,"kind":"multimodal-prediction","task":task,"fusionMode":spec["fusionMode"],"modelSpecFingerprint":spec["modelSpecFingerprint"],"imageTensorFingerprint":ctx["imageTensorFingerprint"],"sequenceTensorFingerprint":ctx["sequenceTensorFingerprint"],"predictionFingerprint":_canonical_sha256(prediction),"isObservedEvidence":False,"isEvaluation":False,"predictionPolicy":"model-derived-multimodal-inference"}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"multimodal-infer","task":task,"prediction":prediction,"multimodalPredictionArtifact":artifact}


def _multimodal_similarity(payload: dict[str, Any]) -> dict[str, Any]:
    metric=str(payload.get("metric") or "cosine").lower()
    if metric not in MULTIMODAL_SIMILARITY_METRICS: raise HTTPException(status_code=400,detail="unsupported multimodal similarity metric")
    left=_tensor(payload.get("leftEmbedding"),name="leftEmbedding",dtype_name="float32",ndim=1); right=_tensor(payload.get("rightEmbedding"),name="rightEmbedding",dtype_name="float32",ndim=1)
    if left.numel()<1 or left.numel()>MAX_MULTIMODAL_FEATURES or right.numel()!=left.numel(): raise HTTPException(status_code=400,detail="multimodal similarity embeddings must have equal bounded dimensions")
    if metric=="cosine":
        denom=float(torch.linalg.vector_norm(left)*torch.linalg.vector_norm(right)); value=float(torch.dot(left,right)/denom) if denom>0 else 0.0
    elif metric=="euclidean": value=float(torch.linalg.vector_norm(left-right))
    else: value=float(torch.dot(left,right))
    artifact={"schema":MULTIMODAL_SIMILARITY_ARTIFACT_SCHEMA,"kind":"multimodal-similarity","metric":metric,"dimensions":int(left.numel()),"leftFingerprint":_canonical_sha256(_tensor_json(left)),"rightFingerprint":_canonical_sha256(_tensor_json(right)),"value":value,"isObservedEvidence":False,"interpretationPolicy":"representation-similarity-not-semantic-or-causal-proof"}
    artifact["artifactFingerprint"]=_canonical_sha256(artifact)
    return {"kind":"multimodal-similarity","metric":metric,"value":value,"multimodalSimilarityArtifact":artifact}



# v3.39 Neural-Symbolic Research Intelligence Runtime
NEURAL_SYMBOLIC_SYMBOL_CONTRACT_SCHEMA = "sc-workspace-neural-symbolic-symbol-contract/1.0"
NEURAL_SYMBOLIC_CONTEXT_SCHEMA = "sc-workspace-neural-symbolic-context-projection/1.0"
NEURAL_SYMBOLIC_BINDING_SCHEMA = "sc-workspace-neural-symbolic-binding-artifact/1.0"
NEURAL_SYMBOLIC_RULESET_SCHEMA = "sc-workspace-neural-symbolic-rule-set/1.0"
NEURAL_SYMBOLIC_CONSTRAINT_SCHEMA = "sc-workspace-neural-symbolic-constraint-evaluation/1.0"
NEURAL_SYMBOLIC_RELATION_SCHEMA = "sc-workspace-neural-symbolic-relation-score/1.0"
NEURAL_SYMBOLIC_INFERENCE_SCHEMA = "sc-workspace-neural-symbolic-inference-artifact/1.0"
NEURAL_SYMBOLIC_EXPLANATION_SCHEMA = "sc-workspace-neural-symbolic-explanation-artifact/1.0"
NEURAL_SYMBOLIC_SYMBOL_TYPES = {"concept","claim-ref","evidence-ref","finding-ref","hypothesis-ref","entity-ref","observation-ref","custom"}
NEURAL_SYMBOLIC_RULE_OPERATORS = {"implies","requires","excludes","at-least-one","all-or-none"}
NEURAL_SYMBOLIC_RELATION_METRICS = {"cosine","euclidean","dot"}
MAX_NEURAL_SYMBOLIC_SYMBOLS = max(1,min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SYMBOLS","512")),4096))
MAX_NEURAL_SYMBOLIC_RULES = max(1,min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SYMBOLIC_RULES","512")),4096))
MAX_NEURAL_SYMBOLIC_INFERENCE_STEPS = max(1,min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SYMBOLIC_INFERENCE_STEPS","32")),128))
MAX_NEURAL_SYMBOLIC_EMBEDDING_DIMENSIONS = max(1,min(int(os.getenv("SC_WORKSPACE_NEURAL_MAX_SYMBOLIC_EMBEDDING_DIMENSIONS","2048")),MAX_FEATURES))


def _ns_clean_id(value: Any, field: str="symbolId") -> str:
    if not isinstance(value,str) or not value.strip() or len(value.strip())>256:
        raise HTTPException(status_code=400,detail=f"{field} must be a bounded non-empty string")
    return value.strip()


def _ns_symbol_contract(payload: dict[str,Any]) -> dict[str,Any]:
    raw=payload.get("symbol") if isinstance(payload.get("symbol"),dict) else payload
    sid=_ns_clean_id(raw.get("symbolId"))
    st=str(raw.get("symbolType") or "custom").strip().lower()
    if st not in NEURAL_SYMBOLIC_SYMBOL_TYPES:
        raise HTTPException(status_code=400,detail="unsupported neural-symbolic symbolType")
    label=raw.get("label")
    if label is not None and (not isinstance(label,str) or len(label)>512):
        raise HTTPException(status_code=400,detail="symbol label must be a bounded string when supplied")
    source_ref=raw.get("sourceRef")
    if source_ref is not None and (not isinstance(source_ref,str) or len(source_ref)>512):
        raise HTTPException(status_code=400,detail="sourceRef must be a bounded string when supplied")
    attrs=raw.get("attributes") or {}
    if not isinstance(attrs,dict) or len(attrs)>64:
        raise HTTPException(status_code=400,detail="symbol attributes must be a bounded object")
    body={"schema":NEURAL_SYMBOLIC_SYMBOL_CONTRACT_SCHEMA,"kind":"neural-symbolic-symbol-contract","symbolId":sid,"symbolType":st,"label":label,"sourceRef":source_ref,"attributes":attrs,"semanticAuthority":"external-governed-research-object-reference","truthValueAssigned":False,"isObservedEvidence":False}
    body["symbolFingerprint"]=_canonical_sha256({k:v for k,v in body.items() if k!="schema"})
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-symbol-contract","neuralSymbolicSymbolArtifact":body}


def _ns_context_project(payload: dict[str,Any]) -> dict[str,Any]:
    symbols=payload.get("symbols")
    if not isinstance(symbols,list) or not symbols or len(symbols)>MAX_NEURAL_SYMBOLIC_SYMBOLS:
        raise HTTPException(status_code=400,detail="symbols must be a bounded non-empty array")
    projected=[]; seen=set()
    for raw in symbols:
        if not isinstance(raw,dict): raise HTTPException(status_code=400,detail="each symbol must be an object")
        c=_ns_symbol_contract({"symbol":raw})["neuralSymbolicSymbolArtifact"]
        if c["symbolId"] in seen: raise HTTPException(status_code=400,detail="duplicate symbolId")
        seen.add(c["symbolId"]); projected.append({"symbolId":c["symbolId"],"symbolType":c["symbolType"],"symbolFingerprint":c["symbolFingerprint"],"sourceRef":c.get("sourceRef")})
    body={"schema":NEURAL_SYMBOLIC_CONTEXT_SCHEMA,"kind":"neural-symbolic-context-projection","symbolCount":len(projected),"symbolIds":[x["symbolId"] for x in projected],"symbolsFingerprint":_canonical_sha256(projected),"semanticAuthority":"references-only-no-truth-adjudication","externalKnowledgeBaseRead":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-context-project","symbols":projected,"neuralSymbolicContextArtifact":body}


def _ns_embedding(raw: Any, field: str) -> list[float]:
    if not isinstance(raw,list) or not raw or len(raw)>MAX_NEURAL_SYMBOLIC_EMBEDDING_DIMENSIONS:
        raise HTTPException(status_code=400,detail=f"{field} must be a bounded non-empty numeric vector")
    try: vals=[float(x) for x in raw]
    except Exception as exc: raise HTTPException(status_code=400,detail=f"{field} must be numeric") from exc
    if any(not math.isfinite(x) for x in vals): raise HTTPException(status_code=400,detail=f"{field} must contain finite values")
    return vals


def _ns_bind(payload: dict[str,Any]) -> dict[str,Any]:
    symbol=_ns_symbol_contract({"symbol":payload.get("symbol") or {}})["neuralSymbolicSymbolArtifact"]
    emb=_ns_embedding(payload.get("embedding"),"embedding")
    representation_ref=payload.get("representationRef")
    if representation_ref is not None and (not isinstance(representation_ref,str) or len(representation_ref)>512):
        raise HTTPException(status_code=400,detail="representationRef must be a bounded string when supplied")
    body={"schema":NEURAL_SYMBOLIC_BINDING_SCHEMA,"kind":"neural-symbolic-binding","symbolId":symbol["symbolId"],"symbolFingerprint":symbol["symbolFingerprint"],"embeddingDimensions":len(emb),"embeddingFingerprint":_canonical_sha256(emb),"representationRef":representation_ref,"bindingPolicy":"operator-supplied-symbol-to-model-representation","semanticEquivalenceAsserted":False,"truthValueAssigned":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-bind","embedding":emb,"neuralSymbolicBindingArtifact":body}


def _ns_normalize_rule(raw: Any) -> dict[str,Any]:
    if not isinstance(raw,dict): raise HTTPException(status_code=400,detail="each neural-symbolic rule must be an object")
    rid=_ns_clean_id(raw.get("ruleId"),"ruleId"); op=str(raw.get("operator") or "").strip().lower()
    if op not in NEURAL_SYMBOLIC_RULE_OPERATORS: raise HTTPException(status_code=400,detail="unsupported neural-symbolic rule operator")
    out={"ruleId":rid,"operator":op}
    if op in {"implies","requires","excludes"}:
        out["leftSymbolId"]=_ns_clean_id(raw.get("leftSymbolId"),"leftSymbolId"); out["rightSymbolId"]=_ns_clean_id(raw.get("rightSymbolId"),"rightSymbolId")
        if out["leftSymbolId"]==out["rightSymbolId"] and op=="excludes": raise HTTPException(status_code=400,detail="excludes rule cannot target the same symbol")
    else:
        ids=raw.get("symbolIds")
        if not isinstance(ids,list) or len(ids)<2 or len(ids)>64: raise HTTPException(status_code=400,detail=f"{op} rule requires 2-64 symbolIds")
        out["symbolIds"]=[_ns_clean_id(x,"symbolId") for x in ids]
        if len(set(out["symbolIds"]))!=len(out["symbolIds"]): raise HTTPException(status_code=400,detail="rule symbolIds must be unique")
    out["ruleFingerprint"]=_canonical_sha256(out)
    return out


def _ns_rule_contract(payload: dict[str,Any]) -> dict[str,Any]:
    rules=payload.get("rules")
    if not isinstance(rules,list) or not rules or len(rules)>MAX_NEURAL_SYMBOLIC_RULES:
        raise HTTPException(status_code=400,detail="rules must be a bounded non-empty array")
    normalized=[_ns_normalize_rule(x) for x in rules]
    ids=[r["ruleId"] for r in normalized]
    if len(set(ids))!=len(ids): raise HTTPException(status_code=400,detail="duplicate ruleId")
    body={"schema":NEURAL_SYMBOLIC_RULESET_SCHEMA,"kind":"neural-symbolic-rule-set","ruleCount":len(normalized),"operators":sorted(set(r["operator"] for r in normalized)),"rulesFingerprint":_canonical_sha256(normalized),"executionPolicy":"bounded-declarative-no-eval","truthValueAssigned":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-rule-contract","rules":normalized,"neuralSymbolicRuleSetArtifact":body}


def _ns_constraint_evaluate(payload: dict[str,Any]) -> dict[str,Any]:
    rules=_ns_rule_contract({"rules":payload.get("rules")})["rules"]
    active_raw=payload.get("activeSymbolIds") or []
    if not isinstance(active_raw,list) or len(active_raw)>MAX_NEURAL_SYMBOLIC_SYMBOLS: raise HTTPException(status_code=400,detail="activeSymbolIds must be a bounded array")
    active=set(_ns_clean_id(x,"activeSymbolId") for x in active_raw)
    evaluations=[]
    for r in rules:
        op=r["operator"]; ok=True; detail="satisfied"
        if op=="requires":
            ok=not (r["leftSymbolId"] in active and r["rightSymbolId"] not in active); detail="required symbol absent" if not ok else "satisfied"
        elif op=="excludes":
            ok=not (r["leftSymbolId"] in active and r["rightSymbolId"] in active); detail="mutually excluded symbols active" if not ok else "satisfied"
        elif op=="implies":
            ok=not (r["leftSymbolId"] in active and r["rightSymbolId"] not in active); detail="implication not closed" if not ok else "satisfied"
        elif op=="at-least-one":
            ok=any(x in active for x in r["symbolIds"]); detail="none of required alternatives active" if not ok else "satisfied"
        elif op=="all-or-none":
            n=sum(x in active for x in r["symbolIds"]); ok=n in {0,len(r["symbolIds"])}; detail="partial all-or-none activation" if not ok else "satisfied"
        evaluations.append({"ruleId":r["ruleId"],"operator":op,"satisfied":ok,"detail":detail})
    violations=[x for x in evaluations if not x["satisfied"]]
    body={"schema":NEURAL_SYMBOLIC_CONSTRAINT_SCHEMA,"kind":"neural-symbolic-constraint-evaluation","activeSymbolIds":sorted(active),"ruleCount":len(rules),"satisfiedCount":len(evaluations)-len(violations),"violationCount":len(violations),"validUnderDeclaredRules":len(violations)==0,"evaluations":evaluations,"rulesFingerprint":_canonical_sha256(rules),"truthValueAssigned":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-constraint-evaluate","evaluations":evaluations,"violations":violations,"neuralSymbolicConstraintArtifact":body}


def _ns_relation_score(payload: dict[str,Any]) -> dict[str,Any]:
    left=_ns_embedding(payload.get("leftEmbedding"),"leftEmbedding"); right=_ns_embedding(payload.get("rightEmbedding"),"rightEmbedding")
    if len(left)!=len(right): raise HTTPException(status_code=400,detail="relation embeddings must have equal dimensions")
    metric=str(payload.get("metric") or "cosine").lower()
    if metric not in NEURAL_SYMBOLIC_RELATION_METRICS: raise HTTPException(status_code=400,detail="unsupported neural-symbolic relation metric")
    a=torch.tensor(left,dtype=torch.float32); b=torch.tensor(right,dtype=torch.float32)
    if metric=="cosine": value=float(F.cosine_similarity(a.view(1,-1),b.view(1,-1),dim=1).item())
    elif metric=="euclidean": value=float(torch.linalg.vector_norm(a-b).item())
    else: value=float(torch.dot(a,b).item())
    relation=str(payload.get("relationType") or "unspecified")
    if len(relation)>128: raise HTTPException(status_code=400,detail="relationType too long")
    body={"schema":NEURAL_SYMBOLIC_RELATION_SCHEMA,"kind":"neural-symbolic-relation-score","metric":metric,"relationType":relation,"dimensions":len(left),"leftFingerprint":_canonical_sha256(left),"rightFingerprint":_canonical_sha256(right),"value":value,"interpretationPolicy":"representation-relation-score-not-logical-proof-or-truth","isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-relation-score","metric":metric,"value":value,"neuralSymbolicRelationArtifact":body}


def _ns_infer(payload: dict[str,Any]) -> dict[str,Any]:
    rules=_ns_rule_contract({"rules":payload.get("rules")})["rules"]
    initial_raw=payload.get("activeSymbolIds") or []
    if not isinstance(initial_raw,list) or len(initial_raw)>MAX_NEURAL_SYMBOLIC_SYMBOLS: raise HTTPException(status_code=400,detail="activeSymbolIds must be a bounded array")
    active=set(_ns_clean_id(x,"activeSymbolId") for x in initial_raw); initial=set(active); trace=[]
    for step in range(MAX_NEURAL_SYMBOLIC_INFERENCE_STEPS):
        additions=[]
        for r in rules:
            if r["operator"]=="implies" and r["leftSymbolId"] in active and r["rightSymbolId"] not in active:
                additions.append((r["rightSymbolId"],r["ruleId"],r["leftSymbolId"]))
        if not additions: break
        for sid,rid,left in additions:
            if sid not in active:
                active.add(sid); trace.append({"step":step+1,"ruleId":rid,"fromSymbolId":left,"inferredSymbolId":sid})
        if len(active)>MAX_NEURAL_SYMBOLIC_SYMBOLS: raise HTTPException(status_code=413,detail="neural-symbolic inference exceeded symbol bound")
    else:
        raise HTTPException(status_code=413,detail="neural-symbolic inference exceeded step bound")
    constraints=_ns_constraint_evaluate({"rules":rules,"activeSymbolIds":sorted(active)})
    body={"schema":NEURAL_SYMBOLIC_INFERENCE_SCHEMA,"kind":"neural-symbolic-inference","initialSymbolIds":sorted(initial),"inferredSymbolIds":sorted(active-initial),"finalSymbolIds":sorted(active),"trace":trace,"inferenceSteps":max([x["step"] for x in trace],default=0),"ruleCount":len(rules),"validUnderDeclaredRules":constraints["neuralSymbolicConstraintArtifact"]["validUnderDeclaredRules"],"violationCount":constraints["neuralSymbolicConstraintArtifact"]["violationCount"],"inferencePolicy":"bounded-forward-chaining-over-operator-declared-rules","truthValueAssigned":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-infer","inferredSymbolIds":body["inferredSymbolIds"],"finalSymbolIds":body["finalSymbolIds"],"trace":trace,"violations":constraints["violations"],"neuralSymbolicInferenceArtifact":body}


def _ns_explain(payload: dict[str,Any]) -> dict[str,Any]:
    inference=payload.get("inferenceArtifact")
    if not isinstance(inference,dict) or inference.get("schema")!=NEURAL_SYMBOLIC_INFERENCE_SCHEMA:
        raise HTTPException(status_code=400,detail="inferenceArtifact schema is invalid")
    trace=inference.get("trace") or []
    if not isinstance(trace,list) or len(trace)>MAX_NEURAL_SYMBOLIC_RULES: raise HTTPException(status_code=400,detail="inference trace invalid")
    reasons=[{"inferredSymbolId":x.get("inferredSymbolId"),"ruleId":x.get("ruleId"),"fromSymbolId":x.get("fromSymbolId"),"step":x.get("step")} for x in trace if isinstance(x,dict)]
    body={"schema":NEURAL_SYMBOLIC_EXPLANATION_SCHEMA,"kind":"neural-symbolic-explanation","inferenceArtifactFingerprint":inference.get("artifactFingerprint"),"reasonCount":len(reasons),"reasons":reasons,"validUnderDeclaredRules":bool(inference.get("validUnderDeclaredRules")),"explanationPolicy":"deterministic-rule-trace-no-natural-language-truth-claim","truthValueAssigned":False,"isObservedEvidence":False}
    body["artifactFingerprint"]=_canonical_sha256(body)
    return {"kind":"neural-symbolic-explain","reasons":reasons,"neuralSymbolicExplanationArtifact":body}


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": SERVICE,
        "version": SERVICE_VERSION,
        "runtime": RUNTIME,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "numpyVersion": np.__version__,
        "runtimeIdentity": os.getenv("USER", ""),
        "runtimeHome": os.getenv("HOME", ""),
        "torchInductorCacheDir": os.getenv("TORCHINDUCTOR_CACHE_DIR", ""),
        "xdgCacheHome": os.getenv("XDG_CACHE_HOME", ""),
        "torchDynamoPreloaded": True,
        "optimizerRuntimeWarm": OPTIMIZER_RUNTIME_WARM,
        "optimizerInitializationSerialized": True,
        "devicePolicy": "governed-explicit-device-orchestration",
        "tensorDatasetTransformationInterchange": True,
        "tensorContractSchema": "sc-workspace-neural-tensor-contract/1.0",
        "datasetManifestSchema": "sc-workspace-neural-dataset-manifest/1.0",
        "batchPlanSchema": "sc-workspace-neural-batch-plan/1.0",
        "transformationLineage": True,
        "externalDatasetReadEnabled": False,
        "availableDevices": [d["device"] for d in _device_inventory_body()["devices"] if d.get("available") and d.get("policyAllowed")],
        "deviceInventorySchema": DEVICE_INVENTORY_SCHEMA,
        "devicePlanSchema": DEVICE_PLAN_SCHEMA,
        "deviceOrchestrationEnabled": True,
        "deviceRequestModes": ["cpu", "auto", "accelerator", "cuda:N"],
        "acceleratorPolicyEnabled": ACCELERATOR_ENABLED,
        "graphNeuralNetworkRuntimeFoundation": True,
        "graphTensorContractSchema": GRAPH_TENSOR_CONTRACT_SCHEMA,
        "graphDatasetProjectionSchema": GRAPH_DATASET_PROJECTION_SCHEMA,
        "gnnModelSpecSchema": GNN_MODEL_SPEC_SCHEMA,
        "gnnExecutionArtifactSchema": GNN_EXECUTION_ARTIFACT_SCHEMA,
        "gnnPredictionArtifactSchema": GNN_PREDICTION_ARTIFACT_SCHEMA,
        "gnnAdapters": sorted(GNN_ADAPTERS),
        "gnnOperations": ["graph-tensor-contract", "graph-dataset-project", "gnn-model-summary", "gnn-forward", "gnn-infer"],
        "gnnTrainingEnabled": True,
        "gnnExternalGraphReadEnabled": False,
        "gnnTrainingRuntime": True,
        "gnnSplitPlanSchema": GNN_SPLIT_PLAN_SCHEMA,
        "gnnTrainingPlanSchema": GNN_TRAINING_PLAN_SCHEMA,
        "gnnTrainingArtifactSchema": GNN_TRAINING_ARTIFACT_SCHEMA,
        "gnnCheckpointArtifactSchema": GNN_CHECKPOINT_ARTIFACT_SCHEMA,
        "gnnTrainingTasks": sorted(GNN_TRAINING_TASKS),
        "gnnTrainingOptimizers": sorted(GNN_TRAINING_OPTIMIZERS),
        "gnnCheckpointResumeEnabled": True,
        "gnnEvaluationExplainabilityEmbeddingsEnabled": True,
        "gnnEvaluationArtifactSchema": GNN_EVALUATION_ARTIFACT_SCHEMA,
        "gnnCalibrationArtifactSchema": GNN_CALIBRATION_ARTIFACT_SCHEMA,
        "gnnExplainabilityArtifactSchema": GNN_EXPLAINABILITY_ARTIFACT_SCHEMA,
        "gnnEmbeddingArtifactSchema": GNN_EMBEDDING_ARTIFACT_SCHEMA,
        "gnnEmbeddingAnalysisArtifactSchema": GNN_EMBEDDING_ANALYSIS_ARTIFACT_SCHEMA,
        "gnnExplainabilityMethods": ["input-gradient", "feature-occlusion"],
        "gnnEmbeddingMetrics": sorted(GNN_EMBEDDING_METRICS),
        "computerVisionRemoteSensingRuntime": True,
        "imageTensorContractSchema": IMAGE_TENSOR_CONTRACT_SCHEMA,
        "visionDatasetProjectionSchema": VISION_DATASET_PROJECTION_SCHEMA,
        "visionModelSpecSchema": VISION_MODEL_SPEC_SCHEMA,
        "visionExecutionArtifactSchema": VISION_EXECUTION_ARTIFACT_SCHEMA,
        "visionPredictionArtifactSchema": VISION_PREDICTION_ARTIFACT_SCHEMA,
        "visionTilePlanSchema": VISION_TILE_PLAN_SCHEMA,
        "remoteSensingProjectionArtifactSchema": REMOTE_SENSING_PROJECTION_ARTIFACT_SCHEMA,
        "remoteSensingIndexArtifactSchema": REMOTE_SENSING_INDEX_ARTIFACT_SCHEMA,
        "visionAdapters": sorted(VISION_ADAPTERS),
        "visionTasks": sorted(VISION_TASKS),
        "remoteSensingSpectralIndices": sorted(SPECTRAL_INDEX_PRESETS),
        "visionExternalRasterReadEnabled": False,
        "temporalDeepLearningSequenceRuntime": True,
        "sequenceTensorContractSchema": SEQUENCE_TENSOR_CONTRACT_SCHEMA,
        "sequenceWindowPlanSchema": SEQUENCE_WINDOW_PLAN_SCHEMA,
        "sequenceDatasetProjectionSchema": SEQUENCE_DATASET_PROJECTION_SCHEMA,
        "sequenceModelSpecSchema": SEQUENCE_MODEL_SPEC_SCHEMA,
        "sequenceExecutionArtifactSchema": SEQUENCE_EXECUTION_ARTIFACT_SCHEMA,
        "sequencePredictionArtifactSchema": SEQUENCE_PREDICTION_ARTIFACT_SCHEMA,
        "sequenceEmbeddingArtifactSchema": SEQUENCE_EMBEDDING_ARTIFACT_SCHEMA,
        "sequenceForecastArtifactSchema": SEQUENCE_FORECAST_ARTIFACT_SCHEMA,
        "sequenceAdapters": sorted(SEQUENCE_ADAPTERS),
        "sequenceTasks": sorted(SEQUENCE_TASKS),
        "sequenceExternalDataReadEnabled": False,
        "multimodalNeuralRuntime": True,
        "multimodalSampleContractSchema": MULTIMODAL_SAMPLE_CONTRACT_SCHEMA,
        "multimodalDatasetProjectionSchema": MULTIMODAL_DATASET_PROJECTION_SCHEMA,
        "multimodalModelSpecSchema": MULTIMODAL_MODEL_SPEC_SCHEMA,
        "multimodalFusionArtifactSchema": MULTIMODAL_FUSION_ARTIFACT_SCHEMA,
        "multimodalRepresentationArtifactSchema": MULTIMODAL_REPRESENTATION_ARTIFACT_SCHEMA,
        "multimodalExecutionArtifactSchema": MULTIMODAL_EXECUTION_ARTIFACT_SCHEMA,
        "multimodalPredictionArtifactSchema": MULTIMODAL_PREDICTION_ARTIFACT_SCHEMA,
        "multimodalSimilarityArtifactSchema": MULTIMODAL_SIMILARITY_ARTIFACT_SCHEMA,
        "multimodalModalities": ["vision", "sequence"],
        "multimodalFusionModes": sorted(MULTIMODAL_FUSION_MODES),
        "multimodalTasks": sorted(MULTIMODAL_TASKS),
        "multimodalExternalDataReadEnabled": False,
        "neuralSymbolicResearchIntelligenceRuntime": True,
        "neuralSymbolicSymbolContractSchema": NEURAL_SYMBOLIC_SYMBOL_CONTRACT_SCHEMA,
        "neuralSymbolicContextSchema": NEURAL_SYMBOLIC_CONTEXT_SCHEMA,
        "neuralSymbolicBindingSchema": NEURAL_SYMBOLIC_BINDING_SCHEMA,
        "neuralSymbolicRuleSetSchema": NEURAL_SYMBOLIC_RULESET_SCHEMA,
        "neuralSymbolicConstraintSchema": NEURAL_SYMBOLIC_CONSTRAINT_SCHEMA,
        "neuralSymbolicRelationSchema": NEURAL_SYMBOLIC_RELATION_SCHEMA,
        "neuralSymbolicInferenceSchema": NEURAL_SYMBOLIC_INFERENCE_SCHEMA,
        "neuralSymbolicExplanationSchema": NEURAL_SYMBOLIC_EXPLANATION_SCHEMA,
        "neuralSymbolicRuleOperators": sorted(NEURAL_SYMBOLIC_RULE_OPERATORS),
        "neuralSymbolicTruthAdjudicationEnabled": False,
        "neuralSymbolicExternalKnowledgeBaseReadEnabled": False,
        "operations": sorted(OPERATIONS),
        "boundedOperationsOnly": True,
        "arbitraryCodeExecution": False,
        "trainingEnabled": True,
        "trainingSpecSchema": "sc-workspace-neural-training-spec/1.0",
        "trainingRunSchema": "sc-workspace-neural-training-run/1.0",
        "trainingModelTypes": ["linear", "mlp"],
        "trainingTasks": sorted(ALLOWED_TRAINING_TASKS),
        "trainingOptimizers": sorted(ALLOWED_OPTIMIZERS),
        "checkpointPersistenceEnabled": True,
        "resumeTrainingEnabled": True,
        "checkpointArtifactSchema": CHECKPOINT_SCHEMA,
        "checkpointStateSchema": CHECKPOINT_STATE_SCHEMA,
        "checkpointFormat": CHECKPOINT_FORMAT,
        "checkpointBundleEncoding": CHECKPOINT_BUNDLE_ENCODING,
        "checkpointResumePolicy": CHECKPOINT_RESUME_POLICY,
        "checkpointStoragePolicy": "workspace-artifact-store-via-job-result",
        "maxCheckpointCompressedBytes": MAX_CHECKPOINT_COMPRESSED_BYTES,
        "maxCheckpointJsonBytes": MAX_CHECKPOINT_JSON_BYTES,
        "batchTrialHyperparameterExecutionEnabled": True,
        "trialArtifactSchema": NEURAL_TRIAL_SCHEMA,
        "batchArtifactSchema": NEURAL_BATCH_SCHEMA,
        "hyperparameterSearchArtifactSchema": NEURAL_SEARCH_SCHEMA,
        "maxNeuralBatchTrials": MAX_NEURAL_BATCH_TRIALS,
        "maxNeuralSearchEpochs": MAX_NEURAL_SEARCH_EPOCHS,
        "evaluationCalibrationUncertaintyEnabled": True,
        "evaluationArtifactSchema": EVALUATION_ARTIFACT_SCHEMA,
        "calibrationArtifactSchema": CALIBRATION_ARTIFACT_SCHEMA,
        "uncertaintyArtifactSchema": UNCERTAINTY_ARTIFACT_SCHEMA,
        "maxEvaluationRows": MAX_EVALUATION_ROWS,
        "maxCalibrationBins": MAX_CALIBRATION_BINS,
        "explainabilityRuntimeEnabled": True,
        "explainabilityArtifactSchema": EXPLAINABILITY_ARTIFACT_SCHEMA,
        "explainabilityMethods": ["input-gradient", "integrated-gradients", "feature-occlusion", "global-gradient-sensitivity"],
        "maxExplainabilityRows": MAX_EXPLAINABILITY_ROWS,
        "maxExplainabilityFeatures": MAX_EXPLAINABILITY_FEATURES,
        "maxIntegratedGradientSteps": MAX_INTEGRATED_GRADIENT_STEPS,
        "embeddingRepresentationRuntimeEnabled": True,
        "embeddingArtifactSchema": EMBEDDING_ARTIFACT_SCHEMA,
        "representationAnalysisArtifactSchema": REPRESENTATION_ANALYSIS_ARTIFACT_SCHEMA,
        "embeddingOperations": ["embedding-generate", "representation-summary", "embedding-similarity", "embedding-neighbors"],
        "embeddingNormalizations": sorted(ALLOWED_EMBEDDING_NORMALIZATION),
        "embeddingMetrics": sorted(ALLOWED_EMBEDDING_METRICS),
        "maxEmbeddingRows": MAX_EMBEDDING_ROWS,
        "maxEmbeddingDimensions": MAX_EMBEDDING_DIMENSIONS,
        "maxSimilarityPairs": MAX_SIMILARITY_PAIRS,
        "maxNeighborQueries": MAX_NEIGHBOR_QUERIES,
        "maxNeighbors": MAX_NEIGHBORS,
        "neuralInferencePredictionProvenanceEnabled": True,
        "predictionArtifactSchema": PREDICTION_ARTIFACT_SCHEMA,
        "inferenceOperations": ["infer-regression", "infer-binary", "infer-multiclass", "prediction-inspect"],
        "inferenceTargetsAccepted": False,
        "maxInferenceRows": MAX_INFERENCE_ROWS,
        "maxPredictionOutputs": MAX_PREDICTION_OUTPUTS,
        "reproducibleModelPackagesEnabled": True,
        "modelPackageSchema": MODEL_PACKAGE_SCHEMA,
        "modelPackageManifestSchema": MODEL_PACKAGE_MANIFEST_SCHEMA,
        "modelPackageFormat": MODEL_PACKAGE_FORMAT,
        "modelPackageRuntimeContractSchema": MODEL_PACKAGE_RUNTIME_CONTRACT_SCHEMA,
        "modelPackageOperations": ["package-create", "package-verify", "package-inspect", "package-infer"],
        "acceleratorDeviceOrchestrationEnabled": True,
        "deviceOperations": ["device-inventory", "device-plan", "device-verify", "accelerator-smoke"],
        "batchTrialHyperparameterExecutionEnabled": True,
        "trialArtifactSchema": NEURAL_TRIAL_SCHEMA,
        "batchArtifactSchema": NEURAL_BATCH_SCHEMA,
        "hyperparameterSearchArtifactSchema": NEURAL_SEARCH_SCHEMA,
        "trialPlanSchema": NEURAL_TRIAL_PLAN_SCHEMA,
        "batchTrialOperations": ["trial-plan", "trial-execute", "batch-execute", "hyperparameter-grid", "hyperparameter-random"],
        "maxNeuralTrials": MAX_NEURAL_TRIALS,
        "maxNeuralBatchTrials": MAX_NEURAL_BATCH_TRIALS,
        "maxNeuralSearchEpochs": MAX_NEURAL_SEARCH_EPOCHS,
        "modelPackageDependencyPins": dict(MODEL_PACKAGE_DEPENDENCY_PINS),
        "modelPackageArbitraryCodeAllowed": False,
        "modelPackageSerializedPyTorchAllowed": False,
        "acceleratorExecutionEnabled": bool(ACCELERATOR_ENABLED),
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
        "maxTrainingEpochs": MAX_TRAINING_EPOCHS,
        "maxTrainingRows": MAX_TRAINING_ROWS,
        "maxTrainingParameters": MAX_TRAINING_PARAMETERS,
        "maxTrainingSeconds": MAX_TRAINING_SECONDS,
        "trainingThreadLimit": TRAIN_THREADS,
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
    if operation in {"workspace.neural.checkpoint-inspect", "workspace.neural.resume-linear", "workspace.neural.resume-mlp"} and "seed" not in payload:
        candidate = payload.get("checkpointArtifact")
        if isinstance(candidate, dict) and isinstance(candidate.get("seed"), int):
            payload = dict(payload)
            payload["seed"] = candidate["seed"]
    device_plan = _resolve_device_plan(payload)
    device_token = _CURRENT_DEVICE.set(device_plan["selectedDevice"])
    seed = _seed(payload)
    if operation == "workspace.neural.neural-symbolic-symbol-contract":
        result = _ns_symbol_contract(payload)
    elif operation == "workspace.neural.neural-symbolic-context-project":
        result = _ns_context_project(payload)
    elif operation == "workspace.neural.neural-symbolic-bind":
        result = _ns_bind(payload)
    elif operation == "workspace.neural.neural-symbolic-rule-contract":
        result = _ns_rule_contract(payload)
    elif operation == "workspace.neural.neural-symbolic-constraint-evaluate":
        result = _ns_constraint_evaluate(payload)
    elif operation == "workspace.neural.neural-symbolic-relation-score":
        result = _ns_relation_score(payload)
    elif operation == "workspace.neural.neural-symbolic-infer":
        result = _ns_infer(payload)
    elif operation == "workspace.neural.neural-symbolic-explain":
        result = _ns_explain(payload)
    elif operation == "workspace.neural.multimodal-sample-contract":
        result = _multimodal_sample_contract(payload)
    elif operation == "workspace.neural.multimodal-dataset-project":
        result = _multimodal_dataset_project(payload)
    elif operation == "workspace.neural.multimodal-model-summary":
        result = _multimodal_model_summary(payload)
    elif operation == "workspace.neural.multimodal-embedding-fuse":
        result = _multimodal_embedding_fuse(payload)
    elif operation == "workspace.neural.multimodal-representation-extract":
        result = _multimodal_representation_extract(payload)
    elif operation == "workspace.neural.multimodal-forward":
        result = _multimodal_forward(payload)
    elif operation == "workspace.neural.multimodal-infer":
        result = _multimodal_infer(payload)
    elif operation == "workspace.neural.multimodal-similarity":
        result = _multimodal_similarity(payload)
    elif operation == "workspace.neural.sequence-tensor-contract":
        result = _sequence_tensor_contract(payload)
    elif operation == "workspace.neural.sequence-window-plan":
        result = _sequence_window_plan(payload)
    elif operation == "workspace.neural.sequence-dataset-project":
        result = _sequence_dataset_project(payload)
    elif operation == "workspace.neural.sequence-model-summary":
        result = _sequence_model_summary(payload)
    elif operation == "workspace.neural.sequence-forward":
        result = _sequence_forward(payload)
    elif operation == "workspace.neural.sequence-infer":
        result = _sequence_infer(payload)
    elif operation == "workspace.neural.sequence-embedding-extract":
        result = _sequence_embedding_extract(payload)
    elif operation == "workspace.neural.sequence-forecast":
        result = _sequence_forecast(payload)
    elif operation == "workspace.neural.vision-tensor-contract":
        result = _vision_tensor_contract(payload)
    elif operation == "workspace.neural.vision-dataset-project":
        result = _vision_dataset_project(payload)
    elif operation == "workspace.neural.vision-model-summary":
        result = _vision_model_summary(payload)
    elif operation == "workspace.neural.vision-forward":
        result = _vision_forward(payload)
    elif operation == "workspace.neural.vision-infer":
        result = _vision_infer(payload)
    elif operation == "workspace.neural.vision-tile-plan":
        result = _vision_tile_plan(payload)
    elif operation == "workspace.neural.remote-sensing-band-project":
        result = _remote_sensing_band_project(payload)
    elif operation == "workspace.neural.remote-sensing-index-compute":
        result = _remote_sensing_index_compute(payload)
    elif operation == "workspace.neural.gnn-evaluate":
        result = _gnn_evaluate(payload)
    elif operation == "workspace.neural.gnn-calibration-report":
        result = _gnn_calibration_report(payload)
    elif operation == "workspace.neural.gnn-explain-gradient":
        result = _gnn_explain_gradient(payload)
    elif operation == "workspace.neural.gnn-explain-occlusion":
        result = _gnn_explain_occlusion(payload)
    elif operation == "workspace.neural.gnn-embedding-extract":
        result = _gnn_embedding_extract(payload)
    elif operation == "workspace.neural.gnn-embedding-similarity":
        result = _gnn_embedding_similarity(payload)
    elif operation == "workspace.neural.gnn-embedding-neighbors":
        result = _gnn_embedding_neighbors(payload)
    elif operation == "workspace.neural.gnn-split-plan":
        result = _gnn_split_plan(payload)
    elif operation == "workspace.neural.gnn-training-plan":
        result = _gnn_training_plan(payload)
    elif operation == "workspace.neural.gnn-train":
        result = _gnn_train(payload)
    elif operation == "workspace.neural.gnn-checkpoint-create":
        result = _gnn_checkpoint_create(payload)
    elif operation == "workspace.neural.gnn-checkpoint-resume":
        result = _gnn_checkpoint_resume(payload)
    elif operation == "workspace.neural.graph-tensor-contract":
        result = _graph_tensor_contract(payload)
    elif operation == "workspace.neural.graph-dataset-project":
        result = _graph_dataset_project(payload)
    elif operation == "workspace.neural.gnn-model-summary":
        result = _gnn_model_summary(payload)
    elif operation == "workspace.neural.gnn-forward":
        result = _gnn_forward(payload)
    elif operation == "workspace.neural.gnn-infer":
        result = _gnn_infer(payload)
    elif operation == "workspace.neural.tensor-summary":
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
    elif operation == "workspace.neural.transformation-apply":
        result = _transformation_apply(payload)
    elif operation == "workspace.neural.training-plan":
        result = _training_plan(payload)
    elif operation == "workspace.neural.train-linear":
        result = _train(payload, expected_model_type="linear", resume=False)
    elif operation == "workspace.neural.train-mlp":
        result = _train(payload, expected_model_type="mlp", resume=False)
    elif operation == "workspace.neural.checkpoint-inspect":
        result = _checkpoint_inspect(payload)
    elif operation == "workspace.neural.resume-linear":
        result = _train(payload, expected_model_type="linear", resume=True)
    elif operation == "workspace.neural.resume-mlp":
        result = _train(payload, expected_model_type="mlp", resume=True)
    elif operation == "workspace.neural.evaluate-regression":
        result = _evaluate_regression(payload)
    elif operation == "workspace.neural.evaluate-binary":
        result = _evaluate_binary(payload)
    elif operation == "workspace.neural.evaluate-multiclass":
        result = _evaluate_multiclass(payload)
    elif operation == "workspace.neural.calibration-report":
        result = _calibration_report(payload)
    elif operation == "workspace.neural.uncertainty-summary":
        result = _uncertainty_summary(payload)
    elif operation == "workspace.neural.explain-gradient":
        result = _explain_gradient(payload)
    elif operation == "workspace.neural.explain-integrated-gradients":
        result = _explain_integrated_gradients(payload)
    elif operation == "workspace.neural.explain-occlusion":
        result = _explain_occlusion(payload)
    elif operation == "workspace.neural.explain-global-sensitivity":
        result = _explain_global_sensitivity(payload)
    elif operation == "workspace.neural.embedding-generate":
        result = _embedding_generate(payload)
    elif operation == "workspace.neural.representation-summary":
        result = _representation_summary(payload)
    elif operation == "workspace.neural.embedding-similarity":
        result = _embedding_similarity(payload)
    elif operation == "workspace.neural.embedding-neighbors":
        result = _embedding_neighbors(payload)
    elif operation == "workspace.neural.infer-regression":
        result = _infer_regression(payload)
    elif operation == "workspace.neural.infer-binary":
        result = _infer_binary(payload)
    elif operation == "workspace.neural.infer-multiclass":
        result = _infer_multiclass(payload)
    elif operation == "workspace.neural.prediction-inspect":
        result = _prediction_inspect(payload)
    elif operation == "workspace.neural.package-create":
        result = _model_package_create(payload)
    elif operation == "workspace.neural.package-verify":
        result = _model_package_verify(payload)
    elif operation == "workspace.neural.package-inspect":
        result = _model_package_inspect(payload)
    elif operation == "workspace.neural.package-infer":
        result = _model_package_infer(payload)
    elif operation == "workspace.neural.device-inventory":
        result = _device_inventory(payload)
    elif operation == "workspace.neural.device-plan":
        result = _device_plan(payload)
    elif operation == "workspace.neural.device-verify":
        result = _device_verify(payload)
    elif operation == "workspace.neural.accelerator-smoke":
        result = _accelerator_smoke(payload)
    elif operation == "workspace.neural.trial-plan":
        result = _trial_plan(payload)
    elif operation == "workspace.neural.trial-execute":
        result = _execute_trial(payload)
    elif operation == "workspace.neural.batch-execute":
        result = _batch_execute(payload)
    elif operation == "workspace.neural.hyperparameter-grid":
        result = _hyperparameter_grid(payload)
    else:
        result = _hyperparameter_random(payload)
    selected_device = _current_device_name()
    _CURRENT_DEVICE.reset(device_token)
    return {
        "ok": True,
        "schema": "sc-workspace-neural-runtime-result/1.0",
        "runtime": RUNTIME,
        "runtimeVersion": SERVICE_VERSION,
        "engine": ENGINE,
        "engineVersion": torch.__version__,
        "device": selected_device,
        "devicePlan": device_plan,
        "seed": seed,
        "operation": operation,
        "boundedOperationsOnly": True,
        "arbitraryCodeExecution": False,
        "trainingEnabled": True,
        "trainingSpecSchema": "sc-workspace-neural-training-spec/1.0",
        "trainingRunSchema": "sc-workspace-neural-training-run/1.0",
        "trainingModelTypes": ["linear", "mlp"],
        "trainingTasks": sorted(ALLOWED_TRAINING_TASKS),
        "trainingOptimizers": sorted(ALLOWED_OPTIMIZERS),
        "checkpointPersistenceEnabled": True,
        "resumeTrainingEnabled": True,
        "checkpointArtifactSchema": CHECKPOINT_SCHEMA,
        "checkpointStateSchema": CHECKPOINT_STATE_SCHEMA,
        "checkpointFormat": CHECKPOINT_FORMAT,
        "checkpointBundleEncoding": CHECKPOINT_BUNDLE_ENCODING,
        "checkpointResumePolicy": CHECKPOINT_RESUME_POLICY,
        "checkpointStoragePolicy": "workspace-artifact-store-via-job-result",
        "maxCheckpointCompressedBytes": MAX_CHECKPOINT_COMPRESSED_BYTES,
        "maxCheckpointJsonBytes": MAX_CHECKPOINT_JSON_BYTES,
        "batchTrialHyperparameterExecutionEnabled": True,
        "trialArtifactSchema": NEURAL_TRIAL_SCHEMA,
        "batchArtifactSchema": NEURAL_BATCH_SCHEMA,
        "hyperparameterSearchArtifactSchema": NEURAL_SEARCH_SCHEMA,
        "maxNeuralBatchTrials": MAX_NEURAL_BATCH_TRIALS,
        "maxNeuralSearchEpochs": MAX_NEURAL_SEARCH_EPOCHS,
        "evaluationCalibrationUncertaintyEnabled": True,
        "evaluationArtifactSchema": EVALUATION_ARTIFACT_SCHEMA,
        "calibrationArtifactSchema": CALIBRATION_ARTIFACT_SCHEMA,
        "uncertaintyArtifactSchema": UNCERTAINTY_ARTIFACT_SCHEMA,
        "maxEvaluationRows": MAX_EVALUATION_ROWS,
        "maxCalibrationBins": MAX_CALIBRATION_BINS,
        "explainabilityRuntimeEnabled": True,
        "explainabilityArtifactSchema": EXPLAINABILITY_ARTIFACT_SCHEMA,
        "explainabilityMethods": ["input-gradient", "integrated-gradients", "feature-occlusion", "global-gradient-sensitivity"],
        "maxExplainabilityRows": MAX_EXPLAINABILITY_ROWS,
        "maxExplainabilityFeatures": MAX_EXPLAINABILITY_FEATURES,
        "maxIntegratedGradientSteps": MAX_INTEGRATED_GRADIENT_STEPS,
        "embeddingRepresentationRuntimeEnabled": True,
        "embeddingArtifactSchema": EMBEDDING_ARTIFACT_SCHEMA,
        "representationAnalysisArtifactSchema": REPRESENTATION_ANALYSIS_ARTIFACT_SCHEMA,
        "embeddingOperations": ["embedding-generate", "representation-summary", "embedding-similarity", "embedding-neighbors"],
        "embeddingNormalizations": sorted(ALLOWED_EMBEDDING_NORMALIZATION),
        "embeddingMetrics": sorted(ALLOWED_EMBEDDING_METRICS),
        "maxEmbeddingRows": MAX_EMBEDDING_ROWS,
        "maxEmbeddingDimensions": MAX_EMBEDDING_DIMENSIONS,
        "maxSimilarityPairs": MAX_SIMILARITY_PAIRS,
        "maxNeighborQueries": MAX_NEIGHBOR_QUERIES,
        "maxNeighbors": MAX_NEIGHBORS,
        "neuralInferencePredictionProvenanceEnabled": True,
        "predictionArtifactSchema": PREDICTION_ARTIFACT_SCHEMA,
        "inferenceOperations": ["infer-regression", "infer-binary", "infer-multiclass", "prediction-inspect"],
        "inferenceTargetsAccepted": False,
        "maxInferenceRows": MAX_INFERENCE_ROWS,
        "maxPredictionOutputs": MAX_PREDICTION_OUTPUTS,
        "acceleratorExecutionEnabled": bool(ACCELERATOR_ENABLED),
        "graphNeuralNetworkRuntimeFoundation": True,
        "gnnModelSpecSchema": GNN_MODEL_SPEC_SCHEMA,
        "gnnTrainingEnabled": True,
        "gnnExternalGraphReadEnabled": False,
        "gnnTrainingRuntime": True,
        "gnnTrainingArtifactSchema": GNN_TRAINING_ARTIFACT_SCHEMA,
        "gnnCheckpointArtifactSchema": GNN_CHECKPOINT_ARTIFACT_SCHEMA,
        "result": result,
    }
