from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import zipfile
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    ArtifactHead, CommandReceipt, ComputeExecutionReceipt, CrossRuntimeVerificationReceipt,
    DatasetHead, DecisionOptimizationReceipt, DomainMutationReceipt, ExecutionEnvironmentHead,
    ExecutionRun, ForecastEvaluationReceipt, ForecastReceipt, InterchangeReceipt, JobRecord,
    ModelEvaluationReceipt, ModelHead, NotebookExecutionPlan, NotebookHead, NotebookOrchestrationReceipt,
    NumericalSimulationReceipt, OptimizationReceipt, ParameterSetHead, PolyglotExecutionReceipt,
    PredictiveModelReceipt, ProbabilisticInferenceReceipt, ProjectHead, ReliabilityAnalysisReceipt,
    RuntimeAdapterHead, ScientificStudyPackage, ScientificStudyPackageReceipt, StatisticalModelReceipt,
    UncertaintyAnalysisReceipt, VisualizationSpecHead,
)
from .object_store import artifact_metadata, delete_artifact, get_artifact, read_artifact_content, store_artifact
from .schemas import ArtifactStoreRequest, ScientificStudyPackageCreateRequest
from .utils import canonical_bytes, iso, sha256_hex

STUDY_SCHEMA = "sc-workspace-scientific-study-package/1.0"
PROFILE_SCHEMA = "sc-workspace-scientific-study-package-profile/1.0"
BUNDLE_MEDIA_TYPE = "application/vnd.sustainable-catalyst.workspace-study+zip"

RECEIPT_MODELS = (
    ComputeExecutionReceipt, PolyglotExecutionReceipt, StatisticalModelReceipt, NumericalSimulationReceipt,
    PredictiveModelReceipt, ModelEvaluationReceipt, ForecastReceipt, ForecastEvaluationReceipt,
    ProbabilisticInferenceReceipt, UncertaintyAnalysisReceipt, OptimizationReceipt,
    DecisionOptimizationReceipt, ReliabilityAnalysisReceipt, InterchangeReceipt,
    CrossRuntimeVerificationReceipt,
)


def profile() -> dict[str, Any]:
    return {
        "schema": PROFILE_SCHEMA,
        "mode": "reproducible-scientific-study-packages",
        "backendAuthoritative": True,
        "deterministicManifest": True,
        "contentAddressedBundle": True,
        "artifactRevisionAndSha256Pinning": True,
        "executionEnvironmentFingerprints": True,
        "scientificReceiptClosure": True,
        "notebookExecutionPlanClosure": True,
        "embeddedArtifactSnapshots": True,
        "bundleFormat": "zip+canonical-json",
        "integrityAlgorithm": "SHA-256",
        "arbitraryCodeExecution": False,
    }


def _row_dict(row: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for attr in sa_inspect(row).mapper.column_attrs:
        key = attr.key
        if key == "user_key":
            continue
        value = getattr(row, key)
        if isinstance(value, datetime):
            value = iso(value)
        out[key] = value
    return out


def _sort_rows(rows: list[Any], *keys: str) -> list[dict[str, Any]]:
    docs = [_row_dict(x) for x in rows]
    return sorted(docs, key=lambda d: tuple(str(d.get(k, "")) for k in keys))


def _manifest_fingerprint(manifest: dict[str, Any]) -> str:
    doc=dict(manifest); doc.pop("manifestFingerprint",None)
    return sha256_hex(doc)


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "artifact").strip("._")
    return cleaned[:180] or "artifact"


def _receipt_rows(db: Session, user_key: str, job_ids: set[str], run_ids: set[str]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for model in RECEIPT_MODELS:
        clauses=[]
        if hasattr(model, "job_id") and job_ids:
            clauses.append(model.job_id.in_(sorted(job_ids)))
        if hasattr(model, "execution_run_id") and run_ids:
            clauses.append(model.execution_run_id.in_(sorted(run_ids)))
        if not clauses:
            continue
        rows=db.scalars(select(model).where(model.user_key==user_key, or_(*clauses))).all()
        if rows:
            out[model.__tablename__] = _sort_rows(list(rows), "receipt_id", "created_at")
    return dict(sorted(out.items()))


def compile_manifest(db: Session, user_key: str, request: ScientificStudyPackageCreateRequest) -> tuple[dict[str, Any], list[ArtifactHead]]:
    project=db.get(ProjectHead,{"user_key":user_key,"project_id":request.projectId})
    if project is None:
        raise HTTPException(status_code=404, detail="Workspace project not found for scientific study package.")

    notebooks=list(db.scalars(select(NotebookHead).where(NotebookHead.user_key==user_key, NotebookHead.project_id==request.projectId)).all())
    if request.selectedNotebookIds:
        wanted=set(request.selectedNotebookIds)
        found={n.notebook_id for n in notebooks}
        missing=sorted(wanted-found)
        if missing:
            raise HTTPException(status_code=400, detail={"code":"study-notebook-not-found","notebookIds":missing})
        notebooks=[n for n in notebooks if n.notebook_id in wanted]

    artifacts=list(db.scalars(select(ArtifactHead).where(ArtifactHead.user_key==user_key, ArtifactHead.project_id==request.projectId)).all())
    # Never recursively embed earlier study bundles.
    artifacts=[a for a in artifacts if (a.metadata_json or {}).get("kind")!="scientific-study-package"]
    datasets=list(db.scalars(select(DatasetHead).where(DatasetHead.user_key==user_key, DatasetHead.project_id==request.projectId)).all())
    models=list(db.scalars(select(ModelHead).where(ModelHead.user_key==user_key, ModelHead.project_id==request.projectId)).all())
    params=list(db.scalars(select(ParameterSetHead).where(ParameterSetHead.user_key==user_key, ParameterSetHead.project_id==request.projectId)).all())
    envs=list(db.scalars(select(ExecutionEnvironmentHead).where(ExecutionEnvironmentHead.user_key==user_key, ExecutionEnvironmentHead.project_id==request.projectId)).all())
    adapters=list(db.scalars(select(RuntimeAdapterHead).where(RuntimeAdapterHead.user_key==user_key, RuntimeAdapterHead.project_id==request.projectId)).all())
    runs=list(db.scalars(select(ExecutionRun).where(ExecutionRun.user_key==user_key, ExecutionRun.project_id==request.projectId)).all())
    plans=list(db.scalars(select(NotebookExecutionPlan).where(NotebookExecutionPlan.user_key==user_key, NotebookExecutionPlan.project_id==request.projectId)).all())
    jobs=list(db.scalars(select(JobRecord).where(JobRecord.user_key==user_key, JobRecord.project_id==request.projectId)).all())
    visualization_specs=list(db.scalars(select(VisualizationSpecHead).where(VisualizationSpecHead.user_key==user_key, VisualizationSpecHead.project_id==request.projectId)).all())
    job_ids={j.job_id for j in jobs}
    run_ids={r.run_id for r in runs}

    artifact_docs=[]
    for a in sorted(artifacts,key=lambda x:x.artifact_id):
        d=artifact_metadata(a)
        d["embedded"] = bool(request.includeArtifactBlobs)
        artifact_docs.append(d)

    scientific_receipts=_receipt_rows(db,user_key,job_ids,run_ids) if request.includeScientificReceipts else {}
    mutation_rows=list(db.scalars(select(DomainMutationReceipt).where(DomainMutationReceipt.user_key==user_key, DomainMutationReceipt.object_id==request.projectId)).all())
    command_rows=list(db.scalars(select(CommandReceipt).where(CommandReceipt.user_key==user_key, CommandReceipt.target_id==request.projectId)).all())
    orchestration_receipts=[]
    plan_ids={p.plan_id for p in plans}
    if plan_ids:
        orchestration_receipts=list(db.scalars(select(NotebookOrchestrationReceipt).where(NotebookOrchestrationReceipt.user_key==user_key, NotebookOrchestrationReceipt.plan_id.in_(sorted(plan_ids)))).all())

    manifest={
        "schema":STUDY_SCHEMA,
        "project":{
            "projectId":project.project_id,"revision":project.revision,"projectFingerprint":project.project_fingerprint,
            "packageFingerprint":project.fingerprint,"title":project.title,"package":project.package,
        },
        "notebooks":[{
            "notebookId":n.notebook_id,"revision":n.revision,"notebookFingerprint":n.notebook_fingerprint,
            "packageFingerprint":n.fingerprint,"title":n.title,"package":n.package,
        } for n in sorted(notebooks,key=lambda x:x.notebook_id)],
        "artifacts":artifact_docs,
        "datasets":_sort_rows(datasets,"dataset_id"),
        "models":_sort_rows(models,"model_id"),
        "parameterSets":_sort_rows(params,"parameter_set_id"),
        "executionEnvironments":_sort_rows(envs,"environment_id"),
        "runtimeAdapters":_sort_rows(adapters,"adapter_id"),
        "executionRuns":_sort_rows(runs,"run_id"),
        "notebookExecutionPlans":_sort_rows(plans,"plan_id"),
        "jobs":_sort_rows(jobs,"job_id"),
        "visualizationSpecs":_sort_rows(visualization_specs,"visualization_id"),
        "scientificReceipts":scientific_receipts,
        "provenance":{
            "domainMutationReceipts":_sort_rows(mutation_rows,"receipt_id"),
            "commandReceipts":_sort_rows(command_rows,"receipt_id"),
            "notebookOrchestrationReceipts":_sort_rows(orchestration_receipts,"receipt_id"),
        },
        "closure":{
            "artifactPins":[{"artifactId":a.artifact_id,"revision":a.revision,"sha256":a.sha256,"bytes":a.bytes} for a in sorted(artifacts,key=lambda x:x.artifact_id)],
            "executionEnvironmentFingerprints":sorted({r.environment_fingerprint for r in runs if r.environment_fingerprint}),
            "runtimeAdapterFingerprints":sorted({r.runtime_adapter_fingerprint for r in runs if r.runtime_adapter_fingerprint}),
            "reproducibilityFingerprints":sorted({r.reproducibility_fingerprint for r in runs if r.reproducibility_fingerprint}),
        },
        "policy":{
            "backendAuthoritative":True,"deterministicManifest":True,"artifactBlobsEmbedded":bool(request.includeArtifactBlobs),
            "scientificReceiptsIncluded":bool(request.includeScientificReceipts),"arbitraryCodeExecution":False,
        },
    }
    manifest["manifestFingerprint"]=_manifest_fingerprint(manifest)
    return manifest, sorted(artifacts,key=lambda x:x.artifact_id)


def _bundle_bytes(manifest: dict[str, Any], artifacts: list[ArtifactHead], include_blobs: bool) -> bytes:
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_STORED) as zf:
        def write(name: str, data: bytes) -> None:
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_STORED; info.external_attr=0o100644<<16
            zf.writestr(info,data)
        write("manifest.json", canonical_bytes(manifest))
        if include_blobs:
            for row in artifacts:
                data=read_artifact_content(row)
                write(f"artifacts/{_safe_filename(row.artifact_id)}/{_safe_filename(row.filename)}",data)
    return buf.getvalue()


def package_metadata(row: ScientificStudyPackage) -> dict[str, Any]:
    return {
        "packageId":row.package_id,"projectId":row.project_id,"title":row.title,"description":row.description,
        "projectRevision":row.project_revision,"manifestFingerprint":row.manifest_fingerprint,
        "bundleArtifactId":row.bundle_artifact_id,"bundleSha256":row.bundle_sha256,"bundleBytes":row.bundle_bytes,
        "componentCount":row.component_count,"embeddedArtifactCount":row.embedded_artifact_count,
        "closureVerified":row.closure_verified,"createdAt":iso(row.created_at),
    }


def receipt_metadata(row: ScientificStudyPackageReceipt) -> dict[str, Any]:
    return {"receiptId":row.receipt_id,"packageId":row.package_id,"action":row.action,"status":row.status,
            "manifestFingerprint":row.manifest_fingerprint,"bundleSha256":row.bundle_sha256,"details":row.details_json,"createdAt":iso(row.created_at)}


def _add_receipt(db: Session,user_key:str,row:ScientificStudyPackage,action:str,status:str,details:dict[str,Any]) -> None:
    db.add(ScientificStudyPackageReceipt(user_key=user_key,receipt_id=f"stpr_{uuid4().hex}",package_id=row.package_id,
        action=action,status=status,manifest_fingerprint=row.manifest_fingerprint,bundle_sha256=row.bundle_sha256,details_json=details))


def create_package(db: Session,user_key:str,request:ScientificStudyPackageCreateRequest) -> ScientificStudyPackage:
    settings=get_settings()
    count=int(db.scalar(select(func.count()).select_from(ScientificStudyPackage).where(ScientificStudyPackage.user_key==user_key)) or 0)
    if count>=settings.max_scientific_study_packages_per_account:
        raise HTTPException(status_code=409,detail="Scientific study package count limit reached.")
    manifest,artifacts=compile_manifest(db,user_key,request)
    bundle=_bundle_bytes(manifest,artifacts,request.includeArtifactBlobs)
    if len(bundle)>settings.max_scientific_study_package_bytes or len(bundle)>settings.max_artifact_bytes:
        raise HTTPException(status_code=413,detail={"code":"study-package-too-large","bytes":len(bundle),"limit":min(settings.max_scientific_study_package_bytes,settings.max_artifact_bytes)})
    package_id=f"study_{uuid4().hex}"
    artifact_id=f"{package_id}_bundle"
    stored=store_artifact(db,user_key,ArtifactStoreRequest.model_validate({
        "schema":"sc-workspace-artifact-store/1.0","artifactId":artifact_id,"projectId":request.projectId,
        "filename":f"{package_id}.sc-study.zip","mediaType":BUNDLE_MEDIA_TYPE,
        "contentBase64":base64.b64encode(bundle).decode("ascii"),"expectedRevision":0,
        "metadata":{"kind":"scientific-study-package","schema":STUDY_SCHEMA,"manifestFingerprint":manifest["manifestFingerprint"]},
    }))
    component_count=sum(len(x) for x in [manifest["notebooks"],manifest["artifacts"],manifest["datasets"],manifest["models"],manifest["parameterSets"],manifest["executionRuns"],manifest["notebookExecutionPlans"],manifest["jobs"]])
    component_count += sum(len(v) for v in manifest["scientificReceipts"].values())
    row=ScientificStudyPackage(user_key=user_key,package_id=package_id,project_id=request.projectId,
        title=(request.title or manifest["project"]["title"] or "Scientific study package")[:1000],description=request.description,
        project_revision=manifest["project"]["revision"],manifest_fingerprint=manifest["manifestFingerprint"],
        bundle_artifact_id=stored.artifact_id,bundle_sha256=stored.sha256,bundle_bytes=stored.bytes,component_count=component_count,
        embedded_artifact_count=len(artifacts) if request.includeArtifactBlobs else 0,closure_verified=True,manifest_json=manifest)
    db.add(row); db.flush(); _add_receipt(db,user_key,row,"create","verified",{"componentCount":component_count,"embeddedArtifactCount":row.embedded_artifact_count})
    db.commit(); db.refresh(row); return row


def get_package(db:Session,user_key:str,package_id:str) -> ScientificStudyPackage|None:
    return db.get(ScientificStudyPackage,{"user_key":user_key,"package_id":package_id})


def list_packages(db:Session,user_key:str,project_id:str|None=None,limit:int=100) -> list[dict[str,Any]]:
    stmt=select(ScientificStudyPackage).where(ScientificStudyPackage.user_key==user_key)
    if project_id: stmt=stmt.where(ScientificStudyPackage.project_id==project_id)
    rows=db.scalars(stmt.order_by(ScientificStudyPackage.created_at.desc()).limit(max(1,min(limit,500)))).all()
    return [package_metadata(x) for x in rows]


def list_receipts(db:Session,user_key:str,package_id:str|None=None,limit:int=100) -> list[dict[str,Any]]:
    stmt=select(ScientificStudyPackageReceipt).where(ScientificStudyPackageReceipt.user_key==user_key)
    if package_id: stmt=stmt.where(ScientificStudyPackageReceipt.package_id==package_id)
    rows=db.scalars(stmt.order_by(ScientificStudyPackageReceipt.created_at.desc()).limit(max(1,min(limit,500)))).all()
    return [receipt_metadata(x) for x in rows]


def verify_package(db:Session,user_key:str,package_id:str,deep:bool=True) -> dict[str,Any]:
    row=get_package(db,user_key,package_id)
    if row is None: raise HTTPException(status_code=404,detail="Scientific study package not found.")
    artifact=get_artifact(db,user_key,row.bundle_artifact_id)
    if artifact is None: raise HTTPException(status_code=503,detail={"code":"study-bundle-artifact-missing","artifactId":row.bundle_artifact_id})
    bundle=read_artifact_content(artifact)
    errors=[]
    if artifact.sha256!=row.bundle_sha256: errors.append("bundle-sha256-mismatch")
    if _manifest_fingerprint(row.manifest_json)!=row.manifest_fingerprint: errors.append("stored-manifest-fingerprint-mismatch")
    embedded_checked=0
    try:
        with zipfile.ZipFile(io.BytesIO(bundle),"r") as zf:
            archive_manifest=json.loads(zf.read("manifest.json"))
            if archive_manifest!=row.manifest_json: errors.append("archive-manifest-mismatch")
            if deep:
                names=set(zf.namelist())
                for ref in row.manifest_json.get("artifacts",[]):
                    if not ref.get("embedded"): continue
                    prefix=f"artifacts/{_safe_filename(ref['artifactId'])}/"
                    matches=[n for n in names if n.startswith(prefix)]
                    if len(matches)!=1:
                        errors.append(f"embedded-artifact-entry:{ref['artifactId']}"); continue
                    data=zf.read(matches[0]); embedded_checked+=1
                    if hashlib.sha256(data).hexdigest()!=ref.get("sha256") or len(data)!=int(ref.get("bytes") or 0): errors.append(f"embedded-artifact-integrity:{ref['artifactId']}")
    except (zipfile.BadZipFile,KeyError,json.JSONDecodeError): errors.append("invalid-study-bundle")
    ok=not errors
    row.closure_verified=ok
    _add_receipt(db,user_key,row,"verify","verified" if ok else "failed",{"deep":deep,"embeddedArtifactsChecked":embedded_checked,"errors":errors})
    db.commit()
    return {"ok":ok,"packageId":row.package_id,"manifestFingerprint":row.manifest_fingerprint,"bundleSha256":row.bundle_sha256,"embeddedArtifactsChecked":embedded_checked,"errors":errors}


def delete_package(db:Session,user_key:str,package_id:str) -> bool:
    row=get_package(db,user_key,package_id)
    if row is None: return False
    artifact_id=row.bundle_artifact_id
    receipt=ScientificStudyPackageReceipt(user_key=user_key,receipt_id=f"stpr_{uuid4().hex}",package_id=row.package_id,action="delete",status="deleted",manifest_fingerprint=row.manifest_fingerprint,bundle_sha256=row.bundle_sha256,details_json={"bundleArtifactId":artifact_id})
    db.add(receipt); db.delete(row); db.commit()
    delete_artifact(db,user_key,artifact_id)
    return True
