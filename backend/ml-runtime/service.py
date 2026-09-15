from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import math
import os
from typing import Any

import joblib
import numpy as np
from fastapi import FastAPI, Header, HTTPException
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, precision_score, r2_score, recall_score
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SERVICE = "Sustainable Catalyst Workspace Predictive Analytics Runtime"
SERVICE_VERSION = "2.15.0"
RUNTIME = "python-sklearn-predictive"
TOKEN = os.getenv("SC_WORKSPACE_ML_RUNTIME_TOKEN", "").strip()
TIMEOUT = max(1.0, min(float(os.getenv("SC_WORKSPACE_ML_TIMEOUT_SECONDS", "90")), 240.0))
MAX_PAYLOAD = max(1024, min(int(os.getenv("SC_WORKSPACE_ML_MAX_PAYLOAD_BYTES", str(10 * 1024 * 1024))), 25 * 1024 * 1024))
MAX_ROWS = max(100, min(int(os.getenv("SC_WORKSPACE_ML_MAX_ROWS", "50000")), 100000))
MAX_FEATURES = max(1, min(int(os.getenv("SC_WORKSPACE_ML_MAX_FEATURES", "128")), 256))
MAX_MODEL_BYTES = max(1024 * 1024, min(int(os.getenv("SC_WORKSPACE_ML_MAX_MODEL_BYTES", str(20 * 1024 * 1024))), 25 * 1024 * 1024))

OPERATIONS = {
    "workspace.ml.linear-regression",
    "workspace.ml.logistic-classification",
    "workspace.ml.random-forest-regression",
    "workspace.ml.random-forest-classification",
    "workspace.ml.gradient-boosting-regression",
    "workspace.ml.gradient-boosting-classification",
    "workspace.ml.cross-validate",
    "workspace.ml.predict",
}
TRAIN_OPERATIONS = OPERATIONS - {"workspace.ml.cross-validate", "workspace.ml.predict"}

app = FastAPI(title=SERVICE, version=SERVICE_VERSION, docs_url=None, redoc_url=None)


def _require_auth(authorization: str | None) -> None:
    if not TOKEN:
        raise HTTPException(status_code=503, detail="ML runtime service credential is not configured")
    expected = f"Bearer {TOKEN}"
    if not authorization or not hmac.compare_digest(authorization.strip(), expected):
        raise HTTPException(status_code=401, detail="ML runtime service authentication failed")


def _bounded_float(value: Any, default: float, low: float, high: float) -> float:
    try: out = float(value)
    except (TypeError, ValueError): out = default
    if not math.isfinite(out): out = default
    return max(low, min(high, out))


def _bounded_int(value: Any, default: int, low: int, high: int) -> int:
    try: out = int(value)
    except (TypeError, ValueError): out = default
    return max(low, min(high, out))


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise HTTPException(status_code=400, detail="rows must be a non-empty array")
    if len(rows) > MAX_ROWS:
        raise HTTPException(status_code=413, detail="ML row limit exceeded")
    if any(not isinstance(row, dict) for row in rows):
        raise HTTPException(status_code=400, detail="every row must be an object")
    return rows


def _dataset(payload: dict[str, Any], classification: bool) -> tuple[np.ndarray, np.ndarray, list[str], str, str]:
    rows = _rows(payload)
    target = str(payload.get("target") or "").strip()
    if not target:
        raise HTTPException(status_code=400, detail="target is required")
    supplied = payload.get("features")
    if supplied is None:
        first = rows[0]
        features = sorted(str(k) for k in first.keys() if str(k) != target)
    elif isinstance(supplied, list):
        features = [str(x).strip() for x in supplied if str(x).strip()]
    else:
        raise HTTPException(status_code=400, detail="features must be an array")
    features = list(dict.fromkeys(features))
    if not features or len(features) > MAX_FEATURES:
        raise HTTPException(status_code=400, detail="feature count is outside the bounded range")
    x=[]; y=[]
    for row in rows:
        vals=[]
        for name in features:
            if name not in row or row[name] is None:
                raise HTTPException(status_code=400, detail=f"missing feature value: {name}")
            try: v=float(row[name])
            except (TypeError, ValueError): raise HTTPException(status_code=400, detail=f"feature must be numeric: {name}")
            if not math.isfinite(v): raise HTTPException(status_code=400, detail=f"feature must be finite: {name}")
            vals.append(v)
        if target not in row or row[target] is None:
            raise HTTPException(status_code=400, detail="target contains missing values")
        if classification:
            label=row[target]
            if isinstance(label,(dict,list)): raise HTTPException(status_code=400, detail="classification target must be scalar")
            y.append(str(label))
        else:
            try: tv=float(row[target])
            except (TypeError, ValueError): raise HTTPException(status_code=400, detail="regression target must be numeric")
            if not math.isfinite(tv): raise HTTPException(status_code=400, detail="regression target must be finite")
            y.append(tv)
        x.append(vals)
    if len(rows) < 6:
        raise HTTPException(status_code=400, detail="at least six rows are required for model training")
    canonical=json.dumps([{k:r.get(k) for k in [*features,target]} for r in rows], sort_keys=True, separators=(",",":"), default=str)
    fingerprint=hashlib.sha256(canonical.encode()).hexdigest()
    return np.asarray(x,dtype=float), np.asarray(y,dtype=object if classification else float), features, target, fingerprint


def _estimator(model_kind: str, classification: bool, payload: dict[str, Any], seed: int):
    hp=payload.get("hyperparameters") if isinstance(payload.get("hyperparameters"),dict) else {}
    standardize=bool((payload.get("preprocessing") or {}).get("standardize", False)) if isinstance(payload.get("preprocessing") or {},dict) else False
    if model_kind == "linear-regression":
        model=LinearRegression(); classification=False
    elif model_kind == "logistic-classification":
        model=LogisticRegression(C=_bounded_float(hp.get("C"),1.0,0.0001,1000.0), max_iter=_bounded_int(hp.get("maxIter"),500,50,2000), random_state=seed)
    elif model_kind == "random-forest-regression":
        model=RandomForestRegressor(n_estimators=_bounded_int(hp.get("nEstimators"),100,10,250), max_depth=None if hp.get("maxDepth") in (None,"",0) else _bounded_int(hp.get("maxDepth"),12,1,64), min_samples_leaf=_bounded_int(hp.get("minSamplesLeaf"),1,1,64), random_state=seed, n_jobs=1)
    elif model_kind == "random-forest-classification":
        model=RandomForestClassifier(n_estimators=_bounded_int(hp.get("nEstimators"),100,10,250), max_depth=None if hp.get("maxDepth") in (None,"",0) else _bounded_int(hp.get("maxDepth"),12,1,64), min_samples_leaf=_bounded_int(hp.get("minSamplesLeaf"),1,1,64), random_state=seed, n_jobs=1)
    elif model_kind == "gradient-boosting-regression":
        model=GradientBoostingRegressor(n_estimators=_bounded_int(hp.get("nEstimators"),100,10,250), learning_rate=_bounded_float(hp.get("learningRate"),0.1,0.001,1.0), max_depth=_bounded_int(hp.get("maxDepth"),3,1,12), random_state=seed)
    elif model_kind == "gradient-boosting-classification":
        model=GradientBoostingClassifier(n_estimators=_bounded_int(hp.get("nEstimators"),100,10,250), learning_rate=_bounded_float(hp.get("learningRate"),0.1,0.001,1.0), max_depth=_bounded_int(hp.get("maxDepth"),3,1,12), random_state=seed)
    else:
        raise HTTPException(status_code=400, detail="modelType is not registered")
    if standardize and model_kind in {"linear-regression","logistic-classification"}:
        model=Pipeline([("scale",StandardScaler()),("model",model)])
    return model, hp, {"standardize": standardize}


def _metrics(y_true, y_pred, classification: bool) -> dict[str, float]:
    if classification:
        return {
            "accuracy": float(accuracy_score(y_true,y_pred)),
            "precisionMacro": float(precision_score(y_true,y_pred,average="macro",zero_division=0)),
            "recallMacro": float(recall_score(y_true,y_pred,average="macro",zero_division=0)),
            "f1Macro": float(f1_score(y_true,y_pred,average="macro",zero_division=0)),
        }
    return {
        "mae": float(mean_absolute_error(y_true,y_pred)),
        "rmse": float(mean_squared_error(y_true,y_pred) ** 0.5),
        "r2": float(r2_score(y_true,y_pred)),
    }


def _serialize_model(model) -> dict[str, Any]:
    buf=io.BytesIO(); joblib.dump(model,buf,compress=3); raw=buf.getvalue()
    if len(raw)>MAX_MODEL_BYTES: raise HTTPException(status_code=413,detail="trained model artifact exceeds the bounded model size")
    return {"format":"joblib","mediaType":"application/vnd.sc.workspace.ml-model+joblib","contentBase64":base64.b64encode(raw).decode("ascii"),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}


def _model_spec(model, model_kind: str, features: list[str]) -> dict[str, Any]:
    scaler=None; estimator=model
    if isinstance(model,Pipeline):
        scaler=model.named_steps.get("scale"); estimator=model.named_steps.get("model")
    spec={"schema":"sc-workspace-predictive-model-spec/1.0","modelKind":model_kind,"features":features}
    if scaler is not None:
        spec["scalerMean"]=[float(x) for x in scaler.mean_]; spec["scalerScale"]=[float(x) for x in scaler.scale_]
    if model_kind=="linear-regression":
        spec["coefficients"]=[float(x) for x in np.asarray(estimator.coef_).reshape(-1)]; spec["intercept"]=float(np.asarray(estimator.intercept_).reshape(-1)[0])
    elif model_kind=="logistic-classification":
        spec["coefficients"]=[[float(x) for x in row] for row in np.asarray(estimator.coef_)]; spec["intercept"]=[float(x) for x in np.asarray(estimator.intercept_)]; spec["classes"]=[str(x) for x in estimator.classes_]
    elif hasattr(estimator,"feature_importances_"):
        spec["featureImportances"]=[float(x) for x in estimator.feature_importances_]
    return spec


def _operation_model(operation: str) -> tuple[str,bool]:
    mapping={
        "workspace.ml.linear-regression":("linear-regression",False),
        "workspace.ml.logistic-classification":("logistic-classification",True),
        "workspace.ml.random-forest-regression":("random-forest-regression",False),
        "workspace.ml.random-forest-classification":("random-forest-classification",True),
        "workspace.ml.gradient-boosting-regression":("gradient-boosting-regression",False),
        "workspace.ml.gradient-boosting-classification":("gradient-boosting-classification",True),
    }
    if operation not in mapping: raise HTTPException(status_code=400,detail="ML training operation is not registered")
    return mapping[operation]


def _train(operation: str, payload: dict[str,Any]) -> dict[str,Any]:
    kind, classification=_operation_model(operation)
    X,y,features,target,dataset_fp=_dataset(payload,classification)
    seed=_bounded_int(payload.get("seed"),42,0,2_147_483_647)
    test_fraction=_bounded_float(payload.get("testFraction"),0.2,0.1,0.4)
    if classification and len(set(y.tolist()))<2: raise HTTPException(status_code=400,detail="classification requires at least two classes")
    stratify=y if classification and min(list(y).count(c) for c in set(y.tolist()))>=2 else None
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=test_fraction,random_state=seed,stratify=stratify)
    model,hp,pre=_estimator(kind,classification,payload,seed); model.fit(Xtr,ytr); pred=model.predict(Xte)
    metrics=_metrics(yte,pred,classification)
    return {
        "kind":"predictive-model","task":"classification" if classification else "regression","modelKind":kind,
        "features":features,"target":target,"datasetFingerprint":dataset_fp,"seed":seed,
        "trainRows":int(len(Xtr)),"testRows":int(len(Xte)),"testFraction":test_fraction,
        "hyperparameters":hp,"preprocessing":pre,"metrics":metrics,
        "predictions":[str(x) if classification else float(x) for x in pred[:500]],
        "modelSpec":_model_spec(model,kind,features),"modelArtifact":_serialize_model(model),
    }


def _cross_validate(payload: dict[str,Any]) -> dict[str,Any]:
    kind=str(payload.get("modelType") or "linear-regression").strip()
    classification=kind.endswith("classification")
    X,y,features,target,dataset_fp=_dataset(payload,classification)
    seed=_bounded_int(payload.get("seed"),42,0,2_147_483_647)
    folds=_bounded_int(payload.get("folds"),5,2,10)
    if classification:
        counts=[list(y).count(c) for c in set(y.tolist())]
        folds=min(folds,min(counts))
        if folds<2: raise HTTPException(status_code=400,detail="not enough rows per class for cross validation")
        splitter=StratifiedKFold(n_splits=folds,shuffle=True,random_state=seed)
        iterator=splitter.split(X,y)
    else:
        folds=min(folds,len(y)); splitter=KFold(n_splits=folds,shuffle=True,random_state=seed); iterator=splitter.split(X)
    base,hp,pre=_estimator(kind,classification,payload,seed)
    fold_metrics=[]
    for train_idx,test_idx in iterator:
        m=clone(base); m.fit(X[train_idx],y[train_idx]); p=m.predict(X[test_idx]); fold_metrics.append(_metrics(y[test_idx],p,classification))
    keys=fold_metrics[0].keys(); metrics={k:float(np.mean([fm[k] for fm in fold_metrics])) for k in keys}
    return {"kind":"cross-validation","task":"classification" if classification else "regression","modelKind":kind,"features":features,"target":target,"datasetFingerprint":dataset_fp,"seed":seed,"folds":folds,"hyperparameters":hp,"preprocessing":pre,"metrics":metrics,"foldMetrics":fold_metrics}


def _predict(payload: dict[str,Any]) -> dict[str,Any]:
    rows=_rows(payload); spec=payload.get("modelSpec")
    if not isinstance(spec,dict) or spec.get("schema")!="sc-workspace-predictive-model-spec/1.0": raise HTTPException(status_code=400,detail="trusted modelSpec is required")
    kind=str(spec.get("modelKind") or ""); features=[str(x) for x in spec.get("features") or []]
    if kind not in {"linear-regression","logistic-classification"}: raise HTTPException(status_code=400,detail="v2.15 predict accepts bounded linear/logistic model specs only")
    X=[]
    for row in rows:
        try: vals=[float(row[x]) for x in features]
        except Exception: raise HTTPException(status_code=400,detail="prediction rows must contain numeric model features")
        if not all(math.isfinite(x) for x in vals): raise HTTPException(status_code=400,detail="prediction features must be finite")
        X.append(vals)
    X=np.asarray(X,dtype=float)
    if spec.get("scalerMean") is not None:
        mean=np.asarray(spec.get("scalerMean"),dtype=float); scale=np.asarray(spec.get("scalerScale"),dtype=float); X=(X-mean)/scale
    if kind=="linear-regression":
        coef=np.asarray(spec.get("coefficients"),dtype=float); intercept=float(spec.get("intercept") or 0.0); pred=X@coef+intercept; out=[float(x) for x in pred]
    else:
        coef=np.asarray(spec.get("coefficients"),dtype=float); intercept=np.asarray(spec.get("intercept"),dtype=float); classes=[str(x) for x in spec.get("classes") or []]; scores=X@coef.T+intercept
        if len(classes)==2 and scores.shape[1]==1:
            idx=(scores[:,0]>=0).astype(int)
        else: idx=np.argmax(scores,axis=1)
        out=[classes[int(i)] for i in idx]
    return {"kind":"prediction","modelKind":kind,"features":features,"rowCount":len(rows),"predictions":out}


@app.get("/health")
def health() -> dict[str,Any]:
    import sklearn
    return {"ok":True,"service":SERVICE,"version":SERVICE_VERSION,"runtime":RUNTIME,"engine":"Python/scikit-learn","engineVersion":sklearn.__version__,"operations":sorted(OPERATIONS),"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"clientSuppliedCodeAllowed":False,"clientSuppliedPackagesAllowed":False,"clientSuppliedRuntimeUrlsAllowed":False,"clientSuppliedSerializedModelsAllowed":False,"maxRows":MAX_ROWS,"maxFeatures":MAX_FEATURES}


@app.post("/v1/execute")
def execute(envelope: dict[str,Any], authorization: str|None=Header(default=None)) -> dict[str,Any]:
    _require_auth(authorization)
    raw=json.dumps(envelope,ensure_ascii=False,separators=(",",":"),default=str).encode()
    if len(raw)>MAX_PAYLOAD: raise HTTPException(status_code=413,detail="ML runtime payload limit exceeded")
    if envelope.get("schema")!="sc-workspace-polyglot-execution-envelope/1.0": raise HTTPException(status_code=400,detail="Unsupported polyglot execution envelope")
    if envelope.get("language")!="ml": raise HTTPException(status_code=400,detail="ML runtime only accepts language=ml")
    operation=str(envelope.get("operation") or "")
    if operation not in OPERATIONS: raise HTTPException(status_code=400,detail="ML operation is not registered")
    if envelope.get("arbitraryCodeExecution") is not False: raise HTTPException(status_code=400,detail="Arbitrary-code execution must remain disabled")
    payload=envelope.get("payload") or {}
    if not isinstance(payload,dict): raise HTTPException(status_code=400,detail="payload must be an object")
    if any(k in payload for k in ("code","python","script","packages","requirements","runtimeUrl","credentials","pickleBase64","joblibBase64")):
        raise HTTPException(status_code=400,detail="client-supplied code/packages/runtime credentials/serialized models are not accepted")
    if operation in TRAIN_OPERATIONS: result=_train(operation,payload)
    elif operation=="workspace.ml.cross-validate": result=_cross_validate(payload)
    else: result=_predict(payload)
    return {"ok":True,"schema":"sc-workspace-ml-runtime-result/1.0","runtime":RUNTIME,"operation":operation,"boundedOperationsOnly":True,"arbitraryCodeExecution":False,"result":result}
