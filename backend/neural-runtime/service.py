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
SERVICE_VERSION = "3.30.0"
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
        "result": result,
    }
