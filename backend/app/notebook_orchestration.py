from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .jobs import create_job, get_job, job_metadata, request_cancel
from .models import NotebookExecutionPlan, NotebookOrchestrationReceipt
from .object_store import get_artifact
from .repository import get_notebook
from .routing import route_registry
from .schemas import JobCreateRequest, NotebookExecutionPlanRequest
from .utils import iso, sha256_hex

ORCHESTRATION_SCHEMA = "sc-workspace-notebook-orchestration/1.0"
EXECUTION_SCHEMA = "sc-workspace-notebook-cell-execution/1.0"
ALLOWED_TARGETS = {"workspace", "core", "lab", "workbench", "decision-studio", "library", "site-intelligence"}
WORKSPACE_PREFIXES = (
    "workspace.compute.", "workspace.polyglot.", "workspace.ml.", "workspace.forecast.",
    "workspace.probability.", "workspace.uncertainty.", "workspace.optimize.",
    "workspace.decision.", "workspace.reliability.", "workspace.interchange.",
)
WORKSPACE_EXACT = {"workspace.echo", "workspace.storage-integrity", "workspace.recovery-snapshot"}


def profile() -> dict[str, Any]:
    return {
        "schema": ORCHESTRATION_SCHEMA,
        "mode": "server-side-notebook-artifact-orchestration",
        "backendAuthoritative": True,
        "browserSchedulesDependencies": False,
        "explicitExecutionDeclarationsOnly": True,
        "artifactRevisionPinning": True,
        "artifactSha256Pinning": True,
        "topologicalDependencyPlanning": True,
        "dependencyCyclesRejected": True,
        "dependencyAwareDispatch": True,
        "downstreamDispatchAfterSuccess": True,
        "serverConfiguredRoutesOnly": True,
        "arbitraryCodeExecution": False,
    }


def plan_metadata(row: NotebookExecutionPlan) -> dict[str, Any]:
    return {
        "planId": row.plan_id,
        "notebookId": row.notebook_id,
        "notebookRevision": row.notebook_revision,
        "notebookFingerprint": row.notebook_fingerprint,
        "projectId": row.project_id,
        "status": row.status,
        "requestFingerprint": row.request_fingerprint,
        "dependencyGraph": row.dependency_graph_json,
        "artifactBindings": row.artifact_bindings_json,
        "steps": row.steps_json,
        "jobIds": row.job_ids_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def receipt_metadata(row: NotebookOrchestrationReceipt) -> dict[str, Any]:
    return {
        "receiptId": row.receipt_id,
        "planId": row.plan_id,
        "action": row.action,
        "status": row.status,
        "requestFingerprint": row.request_fingerprint,
        "details": row.details_json,
        "createdAt": iso(row.created_at),
    }


def _execution_cells(notebook: dict[str, Any]) -> list[dict[str, Any]]:
    cells = notebook.get("cells") or []
    if not isinstance(cells, list):
        raise HTTPException(status_code=400, detail="Notebook cells must be a list.")
    out=[]
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        execution=cell.get("execution")
        if isinstance(execution, dict):
            out.append(cell)
    return out


def _validate_workspace_operation(operation: str) -> None:
    if operation in WORKSPACE_EXACT:
        return
    if any(operation.startswith(prefix) for prefix in WORKSPACE_PREFIXES):
        return
    raise HTTPException(status_code=400, detail={"code":"unsupported-notebook-operation","operation":operation})


def _topological_order(step_docs: list[dict[str, Any]]) -> list[str]:
    ids={s["stepId"] for s in step_docs}
    deps={s["stepId"]: list(s.get("dependsOnStepIds") or []) for s in step_docs}
    for step_id, items in deps.items():
        unknown=[x for x in items if x not in ids]
        if unknown:
            raise HTTPException(status_code=400, detail={"code":"unknown-notebook-dependency","stepId":step_id,"unknown":unknown})
        if step_id in items:
            raise HTTPException(status_code=400, detail={"code":"self-notebook-dependency","stepId":step_id})
    order=[]
    ready=sorted([k for k,v in deps.items() if not v])
    remaining={k:set(v) for k,v in deps.items()}
    while ready:
        current=ready.pop(0)
        if current in order:
            continue
        order.append(current)
        for key in sorted(remaining):
            if current in remaining[key]:
                remaining[key].remove(current)
                if not remaining[key] and key not in order and key not in ready:
                    ready.append(key); ready.sort()
    if len(order)!=len(step_docs):
        blocked=sorted(set(ids)-set(order))
        raise HTTPException(status_code=400, detail={"code":"notebook-dependency-cycle","steps":blocked})
    return order


def compile_plan(notebook: dict[str, Any], selected_cell_ids: list[str] | None = None) -> dict[str, Any]:
    selected=set(selected_cell_ids or [])
    all_cells=_execution_cells(notebook)
    by_id={str(c.get("id") or ""): c for c in all_cells if str(c.get("id") or "")}
    if selected:
        missing=sorted(selected-set(by_id))
        if missing:
            raise HTTPException(status_code=400, detail={"code":"selected-cells-not-executable","cellIds":missing})
        chosen=[by_id[cid] for cid in sorted(selected)]
    else:
        chosen=all_cells
    if not chosen:
        raise HTTPException(status_code=400, detail={"code":"no-executable-notebook-cells"})
    steps=[]
    for cell in chosen:
        cid=str(cell.get("id") or "").strip()
        if not cid:
            raise HTTPException(status_code=400, detail={"code":"execution-cell-id-required"})
        ex=cell.get("execution") or {}
        if ex.get("schema") not in (None, EXECUTION_SCHEMA):
            raise HTTPException(status_code=400, detail={"code":"unsupported-cell-execution-schema","cellId":cid})
        target=str(ex.get("targetProduct") or "workspace").strip()
        operation=str(ex.get("operation") or "").strip()
        if target not in ALLOWED_TARGETS:
            raise HTTPException(status_code=400, detail={"code":"unsupported-target-product","cellId":cid,"targetProduct":target})
        if not operation:
            raise HTTPException(status_code=400, detail={"code":"execution-operation-required","cellId":cid})
        if target=="workspace": _validate_workspace_operation(operation)
        deps=[str(x) for x in (ex.get("dependsOnCellIds") or [])]
        artifacts=[str(x) for x in (ex.get("inputArtifactIds") or [])]
        steps.append({
            "stepId":cid,"cellId":cid,"targetProduct":target,"operation":operation,
            "dependsOnStepIds":deps,"inputArtifactIds":artifacts,
            "priority":max(0,min(9,int(ex.get("priority",5)))),
            "maxAttempts":max(1,min(5,int(ex.get("maxAttempts",3)))),
            "executionPolicy":dict(ex.get("executionPolicy") or {}),
            "resourceBudget":dict(ex.get("resourceBudget") or {}),
            "sandbox":dict(ex.get("sandbox") or {}),
            "payload":dict(ex.get("payload") or {}),
            "state":"pending","jobId":"",
        })
    order=_topological_order(steps)
    index={sid:i for i,sid in enumerate(order)}
    steps.sort(key=lambda x:index[x["stepId"]])
    return {"steps":steps,"order":order,"edges":[{"from":d,"to":s["stepId"]} for s in steps for d in s["dependsOnStepIds"]]}


def _bind_artifacts(db: Session, user_key: str, project_id: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    bindings={}
    for aid in sorted({a for s in steps for a in s.get("inputArtifactIds",[])}):
        row=get_artifact(db,user_key,aid)
        if row is None:
            raise HTTPException(status_code=400, detail={"code":"notebook-artifact-not-found","artifactId":aid})
        if project_id and row.project_id and row.project_id != project_id:
            raise HTTPException(status_code=409, detail={"code":"notebook-artifact-project-mismatch","artifactId":aid,"artifactProjectId":row.project_id,"notebookProjectId":project_id})
        bindings[aid]={"artifactId":aid,"revision":row.revision,"sha256":row.sha256,"bytes":row.bytes,"mediaType":row.media_type}
    return bindings


def _add_receipt(db: Session, user_key: str, plan_id: str, action: str, status: str, details: dict[str, Any]) -> None:
    db.add(NotebookOrchestrationReceipt(
        user_key=user_key, receipt_id=f"nbor_{uuid4().hex}", plan_id=plan_id, action=action,
        status=status, request_fingerprint=sha256_hex({"planId":plan_id,"action":action,"details":details}), details_json=details,
    ))


def create_plan(db: Session, user_key: str, request: NotebookExecutionPlanRequest) -> NotebookExecutionPlan:
    notebook=get_notebook(db,user_key,request.notebookId)
    if notebook is None:
        raise HTTPException(status_code=404, detail="Workspace notebook not found.")
    if request.expectedNotebookRevision is not None and request.expectedNotebookRevision != notebook.revision:
        raise HTTPException(status_code=409, detail={"code":"notebook-revision-conflict","currentRevision":notebook.revision})
    doc=(notebook.package or {}).get("notebook") or {}
    compiled=compile_plan(doc, request.selectedCellIds)
    routes=route_registry()
    for step in compiled["steps"]:
        route=routes.get(step["targetProduct"]) or {}
        if not route.get("configured"):
            raise HTTPException(status_code=409, detail={"code":"notebook-route-unconfigured","targetProduct":step["targetProduct"],"stepId":step["stepId"]})
    bindings=_bind_artifacts(db,user_key,notebook.project_id,compiled["steps"])
    request_doc=request.model_dump(mode="json",by_alias=True)
    row=NotebookExecutionPlan(
        user_key=user_key,plan_id=f"nbxp_{uuid4().hex}",notebook_id=notebook.notebook_id,
        notebook_revision=notebook.revision,notebook_fingerprint=notebook.notebook_fingerprint,
        project_id=notebook.project_id,status="ready",request_fingerprint=sha256_hex(request_doc),
        dependency_graph_json={"order":compiled["order"],"edges":compiled["edges"]},
        artifact_bindings_json=bindings,steps_json=compiled["steps"],job_ids_json=[],
    )
    db.add(row); _add_receipt(db,user_key,row.plan_id,"plan","ready",{"stepCount":len(compiled["steps"]),"artifactCount":len(bindings)})
    db.commit(); db.refresh(row); return row


def get_plan(db: Session, user_key: str, plan_id: str) -> NotebookExecutionPlan | None:
    return db.get(NotebookExecutionPlan,{"user_key":user_key,"plan_id":plan_id})


def list_plans(db: Session, user_key: str, limit: int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(NotebookExecutionPlan).where(NotebookExecutionPlan.user_key==user_key).order_by(NotebookExecutionPlan.created_at.desc()).limit(max(1,min(limit,500)))).all()
    return [plan_metadata(x) for x in rows]


def list_receipts(db: Session, user_key: str, limit: int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(NotebookOrchestrationReceipt).where(NotebookOrchestrationReceipt.user_key==user_key).order_by(NotebookOrchestrationReceipt.created_at.desc()).limit(max(1,min(limit,500)))).all()
    return [receipt_metadata(x) for x in rows]


def _queue_step(db: Session, row: NotebookExecutionPlan, step: dict[str,Any]) -> dict[str,Any]:
    payload=JobCreateRequest.model_validate({
        "schema":"sc-workspace-job-request/1.0","jobType":"compute-handoff" if step["targetProduct"]!="workspace" else "workspace-task",
        "targetProduct":step["targetProduct"],"operation":step["operation"],"projectId":row.project_id or None,
        "priority":step["priority"],"maxAttempts":step["maxAttempts"],
        "idempotencyKey":f"notebook-plan:{row.plan_id}:{step['stepId']}","inputArtifactIds":step["inputArtifactIds"],
        "executionPolicy":step["executionPolicy"],"resourceBudget":step["resourceBudget"],"sandbox":step["sandbox"],
        "payload":{**step["payload"],"notebookExecution":{"planId":row.plan_id,"stepId":step["stepId"],"notebookId":row.notebook_id,"notebookRevision":row.notebook_revision,"artifactBindings":row.artifact_bindings_json}},
    })
    job,_=create_job(db,row.user_key,payload)
    step["state"]="queued"; step["jobId"]=job.job_id
    return job_metadata(job)


def _queue_ready_steps(db: Session, row: NotebookExecutionPlan) -> list[dict[str,Any]]:
    steps=[dict(x) for x in (row.steps_json or [])]
    states={s["stepId"]:s.get("state") for s in steps}
    queued=[]
    for step in steps:
        if step.get("state")!="pending": continue
        if all(states.get(dep)=="succeeded" for dep in step.get("dependsOnStepIds",[])):
            meta=_queue_step(db,row,step); queued.append(meta); states[step["stepId"]]="queued"
    row.steps_json=steps
    row.job_ids_json=list(dict.fromkeys(list(row.job_ids_json or [])+[x["jobId"] for x in queued]))
    row.updated_at=datetime.now(timezone.utc)
    return queued


def dispatch_plan(db: Session, user_key: str, plan_id: str, idempotency_key: str="", reason: str="user-authorized") -> NotebookExecutionPlan:
    row=get_plan(db,user_key,plan_id)
    if row is None: raise HTTPException(status_code=404, detail="Notebook execution plan not found.")
    if row.status in {"running","succeeded"}: return row
    if row.status not in {"ready"}: raise HTTPException(status_code=409, detail={"code":"plan-not-dispatchable","status":row.status})
    row.status="running"
    queued=_queue_ready_steps(db,row)
    if not queued: raise HTTPException(status_code=409, detail={"code":"plan-has-no-ready-steps"})
    _add_receipt(db,user_key,plan_id,"dispatch","running",{"reason":reason,"idempotencyKey":idempotency_key,"queuedJobIds":[x["jobId"] for x in queued]})
    db.commit(); db.refresh(row); return row


def cancel_plan(db: Session, user_key: str, plan_id: str, reason: str="user-request") -> NotebookExecutionPlan:
    row=get_plan(db,user_key,plan_id)
    if row is None: raise HTTPException(status_code=404, detail="Notebook execution plan not found.")
    if row.status in {"succeeded","failed","blocked","cancelled"}: return row
    steps=[dict(x) for x in (row.steps_json or [])]
    for step in steps:
        jid=step.get("jobId") or ""
        if jid and step.get("state") in {"queued","running"}:
            request_cancel(db,user_key,jid,reason)
        if step.get("state")=="pending": step["state"]="cancelled"
    row.steps_json=steps; row.status="cancelled"; row.updated_at=datetime.now(timezone.utc)
    _add_receipt(db,user_key,plan_id,"cancel","cancelled",{"reason":reason})
    db.commit(); db.refresh(row); return row


def advance_for_job(db: Session, job_row) -> None:
    if not job_row or not getattr(job_row,"job_id",""): return
    rows=db.scalars(select(NotebookExecutionPlan).where(NotebookExecutionPlan.user_key==job_row.user_key,NotebookExecutionPlan.status=="running")).all()
    for row in rows:
        steps=[dict(x) for x in (row.steps_json or [])]
        touched=False
        for step in steps:
            if step.get("jobId")==job_row.job_id:
                state=job_row.status if job_row.status in {"succeeded","failed","blocked","cancelled"} else step.get("state")
                if step.get("state")!=state: step["state"]=state; touched=True
        if not touched: continue
        row.steps_json=steps
        terminal_failure=next((s for s in steps if s.get("state") in {"failed","blocked","cancelled"}),None)
        if terminal_failure:
            row.status=terminal_failure["state"]
            _add_receipt(db,row.user_key,row.plan_id,"advance",row.status,{"jobId":job_row.job_id,"stepId":terminal_failure["stepId"]})
        elif all(s.get("state")=="succeeded" for s in steps):
            row.status="succeeded"; _add_receipt(db,row.user_key,row.plan_id,"complete","succeeded",{"jobId":job_row.job_id,"stepCount":len(steps)})
        else:
            queued=_queue_ready_steps(db,row)
            if queued: _add_receipt(db,row.user_key,row.plan_id,"advance","running",{"completedJobId":job_row.job_id,"queuedJobIds":[x["jobId"] for x in queued]})
        row.updated_at=datetime.now(timezone.utc)
        db.commit()
