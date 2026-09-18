from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain_authority import list_mutation_receipts
from .jobs import create_job, job_metadata, list_jobs, request_cancel, retry_job
from .models import CommandReceipt
from .object_store import artifact_metadata, delete_artifact, list_artifacts, store_artifact
from .registry import list_datasets, list_execution_runs, list_models, list_parameter_sets
from .repository import (
    delete_notebook, delete_project, get_notebook, get_project, list_notebooks, list_projects,
    notebook_metadata, project_metadata, store_notebook, store_project,
)
from .schemas import ArtifactStoreRequest, JobActionRequest, JobCreateRequest, NotebookStoreRequest, ProjectStoreRequest
from .utils import iso, sha256_hex

COMMAND_SCHEMA = "sc-workspace-command-query/1.0"
COMMANDS = (
    "project.put", "project.delete", "notebook.put", "notebook.delete",
    "artifact.put", "artifact.delete", "job.submit", "job.cancel", "job.retry",
)
QUERIES = (
    "workspace.overview", "project.detail", "notebook.detail", "artifact.index",
    "dataset.index", "model.index", "execution.index", "provenance.receipts", "command.receipts",
)


def profile() -> dict[str, Any]:
    return {
        "schema": COMMAND_SCHEMA,
        "mode": "server-command-query",
        "backendAuthoritative": True,
        "browserCommandAuthority": False,
        "commandsMutate": True,
        "queriesMutate": False,
        "commandCount": len(COMMANDS),
        "queryCount": len(QUERIES),
        "commands": list(COMMANDS),
        "queries": list(QUERIES),
        "canonicalStore": "postgresql",
        "readModelsGeneratedServerSide": True,
        "idempotentCommandReceipts": True,
        "arbitraryCodeExecution": False,
    }


def command_receipt_metadata(row: CommandReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "commandId": row.command_id,
        "idempotencyKey": row.idempotency_key,
        "command": row.command,
        "targetKind": row.target_kind,
        "targetId": row.target_id,
        "status": row.status,
        "requestFingerprint": row.request_fingerprint,
        "linkedMutationReceiptId": row.linked_mutation_receipt_id,
        "result": row.result_json,
        "createdAt": iso(row.created_at),
    }


def list_command_receipts(db: Session, user_key: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(CommandReceipt).where(CommandReceipt.user_key == user_key)
        .order_by(CommandReceipt.created_at.desc()).limit(max(1, min(int(limit), 500)))
    ).all()
    return [command_receipt_metadata(r) for r in rows]


def _replay(db: Session, user_key: str, idempotency_key: str) -> CommandReceipt | None:
    if not idempotency_key:
        return None
    return db.scalar(select(CommandReceipt).where(
        CommandReceipt.user_key == user_key,
        CommandReceipt.idempotency_key == idempotency_key,
    ).order_by(CommandReceipt.created_at.desc()).limit(1))


def _latest_mutation_receipt_id(db: Session, user_key: str, object_kind: str, object_id: str) -> str:
    items = list_mutation_receipts(db, user_key, 50)
    for item in items:
        if item.get("objectKind") == object_kind and item.get("objectId") == object_id:
            return str(item.get("receiptId") or "")
    return ""


def execute_command(db: Session, user_key: str, request: Any) -> dict[str, Any]:
    command = request.command
    if command not in COMMANDS:
        raise HTTPException(status_code=400, detail={"code":"unsupported-command","message":f"Unsupported Workspace command: {command}"})
    replay = _replay(db, user_key, request.idempotencyKey or "")
    if replay is not None:
        return {"schema":"sc-workspace-command-result/1.0","ok":True,"replayed":True,"receipt":command_receipt_metadata(replay),"result":replay.result_json}

    payload = dict(request.payload or {})
    result: dict[str, Any]
    target_kind = ""
    target_id = ""
    linked = ""

    if command == "project.put":
        p = ProjectStoreRequest.model_validate(payload)
        row, replayed = store_project(db, user_key, p)
        result = {"replayed": replayed, "item": project_metadata(row)}
        target_kind, target_id = "project", row.project_id
        linked = _latest_mutation_receipt_id(db, user_key, target_kind, target_id)
    elif command == "project.delete":
        target_id = str(payload.get("projectId") or "").strip()
        if not target_id: raise HTTPException(status_code=400, detail="projectId is required.")
        result = {"deleted": delete_project(db, user_key, target_id)}
        target_kind = "project"
        linked = _latest_mutation_receipt_id(db, user_key, target_kind, target_id)
    elif command == "notebook.put":
        p = NotebookStoreRequest.model_validate(payload)
        row, replayed = store_notebook(db, user_key, p)
        result = {"replayed": replayed, "item": notebook_metadata(row)}
        target_kind, target_id = "notebook", row.notebook_id
        linked = _latest_mutation_receipt_id(db, user_key, target_kind, target_id)
    elif command == "notebook.delete":
        target_id = str(payload.get("notebookId") or "").strip()
        if not target_id: raise HTTPException(status_code=400, detail="notebookId is required.")
        result = {"deleted": delete_notebook(db, user_key, target_id)}
        target_kind = "notebook"
        linked = _latest_mutation_receipt_id(db, user_key, target_kind, target_id)
    elif command == "artifact.put":
        p = ArtifactStoreRequest.model_validate(payload)
        row = store_artifact(db, user_key, p)
        result = {"item": artifact_metadata(row)}
        target_kind, target_id = "artifact", row.artifact_id
    elif command == "artifact.delete":
        target_id = str(payload.get("artifactId") or "").strip()
        if not target_id: raise HTTPException(status_code=400, detail="artifactId is required.")
        result = {"deleted": delete_artifact(db, user_key, target_id)}
        target_kind = "artifact"
    elif command == "job.submit":
        p = JobCreateRequest.model_validate(payload)
        row, replayed = create_job(db, user_key, p)
        result = {"replayed": replayed, "item": job_metadata(row)}
        target_kind, target_id = "job", row.job_id
    elif command == "job.cancel":
        target_id = str(payload.get("jobId") or "").strip()
        if not target_id: raise HTTPException(status_code=400, detail="jobId is required.")
        action = JobActionRequest.model_validate({"schema":"sc-workspace-job-action/1.0","reason":payload.get("reason") or "command-api"})
        row = request_cancel(db, user_key, target_id, action.reason)
        result = {"item": job_metadata(row)}
        target_kind = "job"
    else:  # job.retry
        target_id = str(payload.get("jobId") or "").strip()
        if not target_id: raise HTTPException(status_code=400, detail="jobId is required.")
        action = JobActionRequest.model_validate({"schema":"sc-workspace-job-action/1.0","reason":payload.get("reason") or "command-api"})
        row = retry_job(db, user_key, target_id, action.reason)
        result = {"item": job_metadata(row)}
        target_kind = "job"

    receipt = CommandReceipt(
        user_key=user_key,
        receipt_id=f"cmdr_{uuid4().hex}",
        command_id=request.commandId or f"cmd_{uuid4().hex}",
        idempotency_key=request.idempotencyKey or "",
        command=command,
        target_kind=target_kind,
        target_id=target_id,
        status="applied",
        request_fingerprint=sha256_hex({"command":command,"payload":payload}),
        linked_mutation_receipt_id=linked,
        result_json=result,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return {"schema":"sc-workspace-command-result/1.0","ok":True,"replayed":False,"receipt":command_receipt_metadata(receipt),"result":result}


def workspace_overview(db: Session, user_key: str) -> dict[str, Any]:
    projects = list_projects(db, user_key)
    notebooks = list_notebooks(db, user_key)
    artifacts = list_artifacts(db, user_key)
    datasets = list_datasets(db, user_key)
    models = list_models(db, user_key)
    runs = list_execution_runs(db, user_key, limit=100)
    jobs = list_jobs(db, user_key, None, None, 100)
    return {
        "schema":"sc-workspace-read-model/workspace-overview/1.0",
        "canonicalStore":"postgresql",
        "generatedServerSide":True,
        "counts":{"projects":len(projects),"notebooks":len(notebooks),"artifacts":len(artifacts),"datasets":len(datasets),"models":len(models),"executionRuns":len(runs),"jobs":len(jobs)},
        "projects":projects[:25], "notebooks":notebooks[:25], "recentJobs":jobs[:25], "recentRuns":runs[:25],
    }


def project_read_model(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    row = get_project(db, user_key, project_id)
    if row is None: raise HTTPException(status_code=404, detail="Workspace project not found.")
    return {
        "schema":"sc-workspace-read-model/project-detail/1.0", "generatedServerSide":True,
        "project":project_metadata(row),
        "notebooks":[x for x in list_notebooks(db,user_key) if x.get("projectId")==project_id],
        "artifacts":[x for x in list_artifacts(db,user_key) if x.get("projectId")==project_id],
        "datasets":list_datasets(db,user_key,project_id), "models":list_models(db,user_key,project_id),
        "executionRuns":list_execution_runs(db,user_key,project_id=project_id,limit=100),
    }


def notebook_read_model(db: Session, user_key: str, notebook_id: str) -> dict[str, Any]:
    row = get_notebook(db,user_key,notebook_id)
    if row is None: raise HTTPException(status_code=404, detail="Workspace notebook not found.")
    return {"schema":"sc-workspace-read-model/notebook-detail/1.0","generatedServerSide":True,"notebook":notebook_metadata(row),"package":row.package}


def execute_query(db: Session, user_key: str, request: Any) -> dict[str, Any]:
    q=request.query
    if q not in QUERIES:
        raise HTTPException(status_code=400, detail={"code":"unsupported-query","message":f"Unsupported Workspace query: {q}"})
    p=dict(request.parameters or {})
    if q=="workspace.overview": data=workspace_overview(db,user_key)
    elif q=="project.detail": data=project_read_model(db,user_key,str(p.get("projectId") or ""))
    elif q=="notebook.detail": data=notebook_read_model(db,user_key,str(p.get("notebookId") or ""))
    elif q=="artifact.index": data={"schema":"sc-workspace-read-model/artifact-index/1.0","items":list_artifacts(db,user_key)}
    elif q=="dataset.index": data={"schema":"sc-workspace-read-model/dataset-index/1.0","items":list_datasets(db,user_key,p.get("projectId"))}
    elif q=="model.index": data={"schema":"sc-workspace-read-model/model-index/1.0","items":list_models(db,user_key,p.get("projectId"))}
    elif q=="execution.index": data={"schema":"sc-workspace-read-model/execution-index/1.0","items":list_execution_runs(db,user_key,project_id=p.get("projectId"),limit=min(int(p.get("limit") or 100),250))}
    elif q=="provenance.receipts": data={"schema":"sc-workspace-read-model/provenance-receipts/1.0","items":list_mutation_receipts(db,user_key,min(int(p.get("limit") or 100),500))}
    else: data={"schema":"sc-workspace-read-model/command-receipts/1.0","items":list_command_receipts(db,user_key,min(int(p.get("limit") or 100),500))}
    return {"schema":"sc-workspace-query-result/1.0","ok":True,"query":q,"mutated":False,"data":data}
