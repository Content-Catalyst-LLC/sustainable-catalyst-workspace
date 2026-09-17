from __future__ import annotations

import base64
import json
import math
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import CrossRuntimeVerificationReceipt, ExecutionRun, ExecutionRunOutput
from .object_store import get_artifact, read_artifact_content, store_artifact
from .schemas import ArtifactStoreRequest, CrossRuntimeVerificationCreateRequest
from .utils import sha256_hex

JSON_MEDIA_HINTS=("json","+json")

def _now(): return datetime.now(timezone.utc)

def _runtime_label(run:ExecutionRun)->str:
    ref=run.runtime_adapter_ref or {}
    if ref:
        rid=str(ref.get("adapterId") or "").strip()
        rev=ref.get("revision")
        if rid: return f"{rid}@{rev}" if rev is not None else rid
    op=(run.operation or "").lower()
    if op.startswith("workspace.ml."): return "ml"
    if op.startswith("workspace.polyglot.r.") or ".r." in op: return "r"
    if op.startswith("workspace.polyglot.julia.") or ".julia." in op: return "julia"
    if op.startswith("workspace.compute."): return "python-scientific"
    if op.startswith("workspace.interchange."): return "arrow-parquet-interchange"
    return (run.target_product or "workspace")[:96]

def _outputs(db:Session,user_key:str,run_id:str)->list[ExecutionRunOutput]:
    return list(db.scalars(select(ExecutionRunOutput).where(
        ExecutionRunOutput.user_key==user_key,
        ExecutionRunOutput.run_id==run_id,
    ).order_by(ExecutionRunOutput.role.asc(),ExecutionRunOutput.output_id.asc())).all())

def _is_json_media(media:str)->bool:
    m=(media or "").lower()
    return any(h in m for h in JSON_MEDIA_HINTS) or m in {"application/json","text/json"}

def _json_from_output(db:Session,user_key:str,row:ExecutionRunOutput)->Any|None:
    if not row.artifact_id or not _is_json_media(row.media_type): return None
    art=get_artifact(db,user_key,row.artifact_id)
    if art is None or art.bytes>5*1024*1024: return None
    try: return json.loads(read_artifact_content(art).decode("utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError): return None

def _number(x:Any)->bool:
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(float(x))

def _compare_json(a:Any,b:Any,abs_tol:float,rel_tol:float,path:str="$",stats:dict|None=None)->tuple[bool,dict]:
    if stats is None: stats={"numericComparisons":0,"exactScalarComparisons":0,"maxAbsoluteDelta":0.0,"maxRelativeDelta":0.0,"mismatches":[]}
    def mismatch(reason:str):
        if len(stats["mismatches"])<25: stats["mismatches"].append({"path":path,"reason":reason})
        return False,stats
    if _number(a) and _number(b):
        av=float(a); bv=float(b); delta=abs(av-bv); denom=max(abs(av),abs(bv),1e-300); rel=delta/denom
        stats["numericComparisons"]+=1; stats["maxAbsoluteDelta"]=max(stats["maxAbsoluteDelta"],delta); stats["maxRelativeDelta"]=max(stats["maxRelativeDelta"],rel)
        if math.isclose(av,bv,rel_tol=rel_tol,abs_tol=abs_tol): return True,stats
        return mismatch(f"numeric delta {delta:.12g} exceeds tolerances")
    if type(a) is not type(b): return mismatch(f"type mismatch {type(a).__name__}!={type(b).__name__}")
    if isinstance(a,dict):
        if set(a)!=set(b): return mismatch("object keys differ")
        ok=True
        for k in sorted(a):
            sub,_=_compare_json(a[k],b[k],abs_tol,rel_tol,f"{path}.{k}",stats); ok=ok and sub
        return ok,stats
    if isinstance(a,list):
        if len(a)!=len(b): return mismatch("array lengths differ")
        ok=True
        for i,(av,bv) in enumerate(zip(a,b)):
            sub,_=_compare_json(av,bv,abs_tol,rel_tol,f"{path}[{i}]",stats); ok=ok and sub
        return ok,stats
    stats["exactScalarComparisons"]+=1
    if a==b: return True,stats
    return mismatch("scalar values differ")

def _pair_outputs(original:list[ExecutionRunOutput],reproduced:list[ExecutionRunOutput])->list[tuple[ExecutionRunOutput|None,ExecutionRunOutput|None]]:
    def groups(rows):
        out={}
        for r in rows: out.setdefault(r.role or "result",[]).append(r)
        return out
    a=groups(original); b=groups(reproduced); pairs=[]
    for role in sorted(set(a)|set(b)):
        aa=a.get(role,[]); bb=b.get(role,[]); n=max(len(aa),len(bb))
        for i in range(n): pairs.append((aa[i] if i<len(aa) else None,bb[i] if i<len(bb) else None))
    return pairs

def _output_comparison(db:Session,user_key:str,a:ExecutionRunOutput|None,b:ExecutionRunOutput|None,mode:str,abs_tol:float,rel_tol:float)->dict[str,Any]:
    if a is None or b is None:
        return {"role":(a or b).role if (a or b) else "","equivalent":False,"exact":False,"mode":"missing-output","reason":"paired output missing"}
    base={"role":a.role,"originalOutputId":a.output_id,"reproductionOutputId":b.output_id,"originalSha256":a.sha256,"reproductionSha256":b.sha256,"originalMediaType":a.media_type,"reproductionMediaType":b.media_type}
    exact=bool(a.sha256 and b.sha256 and a.sha256==b.sha256 and int(a.bytes)==int(b.bytes))
    if exact: return {**base,"equivalent":True,"exact":True,"mode":"exact-digest"}
    if mode=="exact-digest": return {**base,"equivalent":False,"exact":False,"mode":"exact-digest","reason":"digests differ"}
    aj=_json_from_output(db,user_key,a); bj=_json_from_output(db,user_key,b)
    if aj is not None and bj is not None:
        equivalent,stats=_compare_json(aj,bj,abs_tol,rel_tol)
        return {**base,"equivalent":equivalent,"exact":False,"mode":"tolerance-aware-json","stats":stats}
    return {**base,"equivalent":False,"exact":False,"mode":"digest-only","reason":"non-JSON outputs require exact content digest in v2.17"}

def create_cross_runtime_verification(db:Session,user_key:str,payload:CrossRuntimeVerificationCreateRequest)->CrossRuntimeVerificationReceipt:
    original=db.get(ExecutionRun,{"user_key":user_key,"run_id":payload.originalRunId})
    reproduced=db.get(ExecutionRun,{"user_key":user_key,"run_id":payload.reproductionRunId})
    if original is None or reproduced is None: raise HTTPException(status_code=404,detail="Both original and reproduction Workspace runs are required.")
    receipt_id=(payload.receiptId or f"xrv_{uuid4().hex}").strip()
    if db.get(CrossRuntimeVerificationReceipt,{"user_key":user_key,"receipt_id":receipt_id}) is not None: raise HTTPException(status_code=409,detail="Cross-runtime verification receipt id already exists.")
    count=int(db.scalar(select(func.count()).select_from(CrossRuntimeVerificationReceipt).where(CrossRuntimeVerificationReceipt.user_key==user_key)) or 0)
    if count>=get_settings().max_cross_runtime_verification_receipts_per_account: raise HTTPException(status_code=409,detail="Cross-runtime verification receipt limit reached.")
    original_outputs=_outputs(db,user_key,original.run_id); reproduced_outputs=_outputs(db,user_key,reproduced.run_id)
    comparisons=[_output_comparison(db,user_key,a,b,payload.comparisonMode,payload.absoluteTolerance,payload.relativeTolerance) for a,b in _pair_outputs(original_outputs,reproduced_outputs)]
    terminal_ok=original.status=="succeeded" and reproduced.status=="succeeded"
    exact_inputs=original.input_fingerprint==reproduced.input_fingerprint
    exact_env=original.environment_fingerprint==reproduced.environment_fingerprint
    exact_runtime=(original.runtime_adapter_fingerprint or "")== (reproduced.runtime_adapter_fingerprint or "")
    exact_outputs=bool(comparisons) and all(bool(x.get("exact")) for x in comparisons)
    equivalent_outputs=bool(comparisons) and all(bool(x.get("equivalent")) for x in comparisons)
    if not terminal_ok or not comparisons: classification="incomplete"
    elif payload.requireSameInputs and not exact_inputs: classification="divergent"
    elif exact_inputs and exact_env and exact_runtime and exact_outputs: classification="exact"
    elif exact_inputs and equivalent_outputs: classification="equivalent"
    else: classification="divergent"
    source_runtime=_runtime_label(original); target_runtime=_runtime_label(reproduced)
    details={"schema":"sc-workspace-cross-runtime-verification-result/1.0","originalRunId":original.run_id,"reproductionRunId":reproduced.run_id,"sourceRuntime":source_runtime,"targetRuntime":target_runtime,"classification":classification,"exactInputs":exact_inputs,"exactEnvironment":exact_env,"exactRuntime":exact_runtime,"exactOutputs":exact_outputs,"equivalentOutputs":equivalent_outputs,"absoluteTolerance":payload.absoluteTolerance,"relativeTolerance":payload.relativeTolerance,"comparisonMode":payload.comparisonMode,"requireSameInputs":payload.requireSameInputs,"comparisons":comparisons,"notes":payload.notes,"automaticExecution":False,"arbitraryCodeExecution":False}
    fingerprint=sha256_hex(details)
    raw=json.dumps(details,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode("utf-8")
    artifact_id=f"cross-runtime-verification-{receipt_id}"
    existing=get_artifact(db,user_key,artifact_id)
    art=store_artifact(db,user_key,ArtifactStoreRequest.model_validate({"schema":"sc-workspace-artifact-store/1.0","artifactId":artifact_id,"projectId":original.project_id or None,"filename":f"{artifact_id}.json","mediaType":"application/vnd.sc.workspace.cross-runtime-verification+json","contentBase64":base64.b64encode(raw).decode("ascii"),"expectedRevision":existing.revision if existing else 0,"metadata":{"kind":"cross-runtime-verification","originalRunId":original.run_id,"reproductionRunId":reproduced.run_id,"classification":classification,"sourceRuntime":source_runtime,"targetRuntime":target_runtime}}))
    row=CrossRuntimeVerificationReceipt(user_key=user_key,receipt_id=receipt_id,original_run_id=original.run_id,reproduction_run_id=reproduced.run_id,source_runtime=source_runtime,target_runtime=target_runtime,comparison_mode=payload.comparisonMode,classification=classification,exact_inputs=exact_inputs,exact_environment=exact_env,exact_runtime=exact_runtime,exact_outputs=exact_outputs,equivalent_outputs=equivalent_outputs,absolute_tolerance=payload.absoluteTolerance,relative_tolerance=payload.relativeTolerance,compared_output_count=len(comparisons),result_artifact_id=art.artifact_id,result_sha256=art.sha256,fingerprint=fingerprint,details_json=details,created_at=_now())
    db.add(row); db.commit(); db.refresh(row); return row

def receipt_metadata(r:CrossRuntimeVerificationReceipt)->dict[str,Any]:
    return {"receiptId":r.receipt_id,"originalRunId":r.original_run_id,"reproductionRunId":r.reproduction_run_id,"sourceRuntime":r.source_runtime,"targetRuntime":r.target_runtime,"comparisonMode":r.comparison_mode,"classification":r.classification,"exactInputs":r.exact_inputs,"exactEnvironment":r.exact_environment,"exactRuntime":r.exact_runtime,"exactOutputs":r.exact_outputs,"equivalentOutputs":r.equivalent_outputs,"absoluteTolerance":r.absolute_tolerance,"relativeTolerance":r.relative_tolerance,"comparedOutputCount":r.compared_output_count,"resultArtifactId":r.result_artifact_id,"resultSha256":r.result_sha256,"fingerprint":r.fingerprint,"details":r.details_json or {},"createdAt":r.created_at.isoformat()}

def list_receipts(db:Session,user_key:str,limit:int=100)->list[dict[str,Any]]:
    rows=db.scalars(select(CrossRuntimeVerificationReceipt).where(CrossRuntimeVerificationReceipt.user_key==user_key).order_by(CrossRuntimeVerificationReceipt.created_at.desc()).limit(limit)).all()
    return [receipt_metadata(r) for r in rows]

def get_receipt(db:Session,user_key:str,receipt_id:str):
    return db.get(CrossRuntimeVerificationReceipt,{"user_key":user_key,"receipt_id":receipt_id})

def profile_catalog()->list[dict[str,Any]]:
    return [
        {"mode":"auto","description":"Prefer exact digest; otherwise compare bounded JSON numerics using tolerances.","binaryPolicy":"exact-digest-only"},
        {"mode":"exact-digest","description":"Require byte-identical content digests and sizes.","binaryPolicy":"exact-digest-only"},
        {"mode":"tolerance-aware-json","description":"Compare structured JSON recursively; numeric values use absolute and relative tolerances.","binaryPolicy":"exact-digest-only"},
    ]
