from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import ExecutionRun, ExecutionRunOutput, ReproductionPlan, ReproductionVerification
from .runtime_adapters import check_environment_compatibility, resolve_runtime_adapter_ref
from .environments import get_environment, get_environment_revision
from .schemas import ReproductionPlanCreateRequest, ReproductionVerificationCreateRequest
from .utils import iso, sha256_hex


def _now(): return datetime.now(timezone.utc)


def _outputs(db: Session, user_key: str, run_id: str) -> list[dict]:
    rows=db.scalars(select(ExecutionRunOutput).where(ExecutionRunOutput.user_key==user_key,ExecutionRunOutput.run_id==run_id).order_by(ExecutionRunOutput.output_id.asc())).all()
    return [{"outputId":r.output_id,"role":r.role,"sha256":r.sha256,"bytes":int(r.bytes),"mediaType":r.media_type} for r in rows]


def plan_metadata(row) -> dict:
    return {"planId":row.plan_id,"originalRunId":row.original_run_id,"status":row.status,"fingerprint":row.fingerprint,
            "runtimeAdapterRef":row.runtime_adapter_ref,"environmentRef":row.environment_ref,"expectedOutputs":row.expected_outputs_json,
            "compatibility":row.compatibility_json,"details":row.details_json,"createdAt":iso(row.created_at)}


def verification_metadata(row) -> dict:
    return {"verificationId":row.verification_id,"originalRunId":row.original_run_id,"reproductionRunId":row.reproduction_run_id,
            "classification":row.classification,"exactInputs":row.exact_inputs,"exactEnvironment":row.exact_environment,
            "exactRuntimeAdapter":row.exact_runtime_adapter,"exactOutputs":row.exact_outputs,"fingerprint":row.fingerprint,
            "details":row.details_json,"createdAt":iso(row.created_at)}


def create_reproduction_plan(db: Session, user_key: str, payload: ReproductionPlanCreateRequest):
    original=db.get(ExecutionRun,{"user_key":user_key,"run_id":payload.originalRunId})
    if original is None: raise HTTPException(status_code=404,detail="Original Workspace execution run not found.")
    adapter_ref, adapter_row=resolve_runtime_adapter_ref(db,user_key,payload.runtimeAdapterRef) if payload.runtimeAdapterRef else (original.runtime_adapter_ref,None)
    if adapter_row is None and adapter_ref:
        class Ref: pass
        ref=Ref(); ref.adapterId=adapter_ref.get("adapterId"); ref.revision=adapter_ref.get("revision")
        adapter_ref,adapter_row=resolve_runtime_adapter_ref(db,user_key,ref)
    env_ref=original.environment_ref or {}
    compatibility={"compatible":False,"readiness":"missing-runtime-adapter","checks":[],"executionPerformed":False}
    if adapter_row is not None and env_ref:
        class ERef: pass
        er=ERef(); er.environmentId=env_ref.get("environmentId"); er.revision=env_ref.get("revision")
        compatibility=check_environment_compatibility(db,user_key,adapter_row,er)
    expected=_outputs(db,user_key,original.run_id)
    plan_id=(payload.planId or f"repro-plan-{uuid4()}").strip()
    if db.get(ReproductionPlan,{"user_key":user_key,"plan_id":plan_id}) is not None:
        raise HTTPException(status_code=409,detail="Workspace reproduction plan id already exists.")
    doc={"originalRunId":original.run_id,"inputFingerprint":original.input_fingerprint,"environmentFingerprint":original.environment_fingerprint,
         "runtimeAdapterRef":adapter_ref,"runtimeAdapterFingerprint":original.runtime_adapter_fingerprint,"expectedOutputs":expected,
         "targetProduct":original.target_product,"operation":original.operation}
    row=ReproductionPlan(user_key=user_key,plan_id=plan_id,original_run_id=original.run_id,status="ready" if compatibility.get("readiness")=="ready" else "planned",
                         fingerprint=sha256_hex(doc),runtime_adapter_ref=adapter_ref or {},environment_ref=env_ref,expected_outputs_json=expected,
                         compatibility_json=compatibility,details_json={"notes":payload.notes,"inputFingerprint":original.input_fingerprint,
                         "environmentFingerprint":original.environment_fingerprint,"runtimeAdapterFingerprint":original.runtime_adapter_fingerprint},created_at=_now())
    db.add(row)
    try: db.commit()
    except IntegrityError: db.rollback(); raise HTTPException(status_code=409,detail="A concurrent reproduction plan was detected.")
    db.refresh(row); return row


def get_reproduction_plan(db: Session,user_key:str,plan_id:str): return db.get(ReproductionPlan,{"user_key":user_key,"plan_id":plan_id})

def list_reproduction_plans(db:Session,user_key:str)->list[dict]:
    return [plan_metadata(r) for r in db.scalars(select(ReproductionPlan).where(ReproductionPlan.user_key==user_key).order_by(ReproductionPlan.created_at.desc())).all()]


def create_verification(db:Session,user_key:str,payload:ReproductionVerificationCreateRequest):
    original=db.get(ExecutionRun,{"user_key":user_key,"run_id":payload.originalRunId})
    reproduced=db.get(ExecutionRun,{"user_key":user_key,"run_id":payload.reproductionRunId})
    if original is None or reproduced is None: raise HTTPException(status_code=404,detail="Both original and reproduction Workspace runs are required.")
    original_outputs=_outputs(db,user_key,original.run_id); reproduced_outputs=_outputs(db,user_key,reproduced.run_id)
    exact_inputs=original.input_fingerprint==reproduced.input_fingerprint
    exact_env=original.environment_fingerprint==reproduced.environment_fingerprint
    exact_adapter=(original.runtime_adapter_fingerprint or "")== (reproduced.runtime_adapter_fingerprint or "")
    original_digests=sorted((x["role"],x["sha256"],x["bytes"]) for x in original_outputs)
    reproduced_digests=sorted((x["role"],x["sha256"],x["bytes"]) for x in reproduced_outputs)
    exact_outputs=bool(original_outputs) and original_digests==reproduced_digests
    terminal_ok=original.status=="succeeded" and reproduced.status=="succeeded"
    if not terminal_ok or not original_outputs or not reproduced_outputs: classification="incomplete"
    elif exact_inputs and exact_env and exact_adapter and exact_outputs: classification="exact"
    elif exact_inputs and exact_outputs: classification="compatible"
    else: classification="divergent"
    details={"originalStatus":original.status,"reproductionStatus":reproduced.status,"originalOutputDigests":original_digests,
             "reproductionOutputDigests":reproduced_digests,"comparisonExecuted":False,"comparisonMode":"metadata-and-content-digests"}
    doc={"originalRunId":original.run_id,"reproductionRunId":reproduced.run_id,"classification":classification,
         "exactInputs":exact_inputs,"exactEnvironment":exact_env,"exactRuntimeAdapter":exact_adapter,"exactOutputs":exact_outputs,"details":details}
    vid=(payload.verificationId or f"repro-verify-{uuid4()}").strip()
    if db.get(ReproductionVerification,{"user_key":user_key,"verification_id":vid}) is not None:
        raise HTTPException(status_code=409,detail="Workspace reproduction verification id already exists.")
    row=ReproductionVerification(user_key=user_key,verification_id=vid,original_run_id=original.run_id,reproduction_run_id=reproduced.run_id,
                                 classification=classification,exact_inputs=exact_inputs,exact_environment=exact_env,exact_runtime_adapter=exact_adapter,
                                 exact_outputs=exact_outputs,fingerprint=sha256_hex(doc),details_json=details,created_at=_now())
    db.add(row); db.commit(); db.refresh(row); return row


def get_verification(db:Session,user_key:str,verification_id:str): return db.get(ReproductionVerification,{"user_key":user_key,"verification_id":verification_id})

def list_verifications(db:Session,user_key:str)->list[dict]:
    return [verification_metadata(r) for r in db.scalars(select(ReproductionVerification).where(ReproductionVerification.user_key==user_key).order_by(ReproductionVerification.created_at.desc())).all()]
