from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import JobEvent, JobRecord, WorkerHeartbeat
from .registry import link_job_to_run, sync_run_from_job
from .schemas import JobCreateRequest
from .utils import sha256_hex, iso

TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}
REQUEUEABLE_STATUSES = {"failed", "blocked", "cancelled"}


def _advance_notebook_orchestration(db: Session, row: JobRecord) -> None:
    try:
        from .notebook_orchestration import advance_for_job
        advance_for_job(db, row)
    except Exception as exc:
        # Job completion is authoritative; orchestration advancement may be retried/inspected separately.
        add_event(db, row, "orchestration-advance-error", {"error": f"{exc.__class__.__name__}: {exc}"[:1000]})
        db.commit()


def _now():
    return datetime.now(timezone.utc)


def job_metadata(row: JobRecord) -> dict:
    return {
        "jobId": row.job_id,
        "jobType": row.job_type,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "projectId": row.project_id,
        "executionRunId": row.execution_run_id,
        "status": row.status,
        "priority": row.priority,
        "attempt": row.attempt,
        "maxAttempts": row.max_attempts,
        "progress": row.progress,
        "idempotencyKey": row.idempotency_key,
        "requestFingerprint": row.request_fingerprint,
        "cancellationRequested": row.cancellation_requested,
        "workerId": row.worker_id,
        "errorCode": row.error_code,
        "errorMessage": row.error_message,
        "createdAt": iso(row.created_at),
        "queuedAt": iso(row.queued_at),
        "startedAt": iso(row.started_at) if row.started_at else None,
        "finishedAt": iso(row.finished_at) if row.finished_at else None,
        "updatedAt": iso(row.updated_at),
    }


def _next_sequence(db: Session, user_key: str, job_id: str) -> int:
    current = db.scalar(select(func.max(JobEvent.sequence)).where(JobEvent.user_key == user_key, JobEvent.job_id == job_id))
    return int(current or 0) + 1


def add_event(db: Session, row: JobRecord, event_type: str, details: dict | None = None) -> None:
    db.add(JobEvent(
        user_key=row.user_key,
        job_id=row.job_id,
        sequence=_next_sequence(db, row.user_key, row.job_id),
        event_type=event_type,
        status=row.status,
        progress=row.progress,
        details=details or {},
    ))


def create_job(db: Session, user_key: str, payload: JobCreateRequest) -> tuple[JobRecord, bool]:
    settings = get_settings()
    idempotency_key = (payload.idempotencyKey or "").strip()
    request_doc = payload.model_dump(mode="json", by_alias=True)
    request_fingerprint = sha256_hex(request_doc)
    if idempotency_key:
        existing = db.scalar(select(JobRecord).where(JobRecord.user_key == user_key, JobRecord.idempotency_key == idempotency_key).order_by(JobRecord.created_at.desc()))
        if existing is not None:
            if existing.request_fingerprint != request_fingerprint:
                raise HTTPException(status_code=409, detail="Workspace job idempotency key was already used for a different request.")
            return existing, True

    count = int(db.scalar(select(func.count()).select_from(JobRecord).where(JobRecord.user_key == user_key)) or 0)
    if count >= settings.max_jobs_per_account:
        raise HTTPException(status_code=409, detail="Workspace job count limit reached.")

    now = _now()
    row = JobRecord(
        user_key=user_key,
        job_id=f"job-{uuid4()}",
        job_type=payload.jobType,
        target_product=payload.targetProduct,
        operation=payload.operation.strip(),
        project_id=(payload.projectId or "").strip(),
        execution_run_id=(payload.executionRunId or "").strip(),
        status="queued",
        priority=payload.priority,
        attempt=0,
        max_attempts=payload.maxAttempts,
        progress=0,
        idempotency_key=idempotency_key,
        request_fingerprint=request_fingerprint,
        payload=request_doc,
        result={},
        created_at=now,
        queued_at=now,
        updated_at=now,
    )
    db.add(row)
    if row.execution_run_id:
        link_job_to_run(db, user_key, row.execution_run_id, row.job_id, row.target_product, row.operation)
    add_event(db, row, "queued", {"targetProduct": row.target_product, "operation": row.operation, "executionRunId": row.execution_run_id})
    db.commit()
    db.refresh(row)
    return row, False


def get_job(db: Session, user_key: str, job_id: str) -> JobRecord | None:
    return db.get(JobRecord, {"user_key": user_key, "job_id": job_id})


def list_jobs(db: Session, user_key: str, status: str | None = None, target_product: str | None = None, limit: int = 100) -> list[dict]:
    stmt = select(JobRecord).where(JobRecord.user_key == user_key)
    if status:
        stmt = stmt.where(JobRecord.status == status)
    if target_product:
        stmt = stmt.where(JobRecord.target_product == target_product)
    rows = db.scalars(stmt.order_by(JobRecord.created_at.desc()).limit(max(1, min(limit, 250)))).all()
    return [job_metadata(row) for row in rows]


def list_job_events(db: Session, user_key: str, job_id: str) -> list[dict]:
    rows = db.scalars(select(JobEvent).where(JobEvent.user_key == user_key, JobEvent.job_id == job_id).order_by(JobEvent.sequence.asc())).all()
    return [{
        "sequence": row.sequence,
        "eventType": row.event_type,
        "status": row.status,
        "progress": row.progress,
        "details": row.details,
        "createdAt": iso(row.created_at),
    } for row in rows]


def update_job_progress(db: Session, user_key: str, job_id: str, progress: int, details: dict | None = None) -> bool:
    row = get_job(db, user_key, job_id)
    if row is None:
        return True
    try:
        db.refresh(row)
    except Exception:
        pass
    bounded = max(1, min(99, int(progress)))
    if row.status == "running" and bounded > row.progress:
        row.progress = bounded
        row.updated_at = _now()
        if row.execution_run_id:
            sync_run_from_job(db, row.user_key, row.execution_run_id, row.job_id, "running", row.progress)
        add_event(db, row, "progress", details or {})
        db.commit()
    return bool(row.cancellation_requested)


def request_cancel(db: Session, user_key: str, job_id: str, reason: str) -> JobRecord:
    row = get_job(db, user_key, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace job not found.")
    if row.status in TERMINAL_STATUSES:
        return row
    row.cancellation_requested = True
    if row.status in {"queued", "blocked"}:
        row.status = "cancelled"
        row.finished_at = _now()
        row.progress = min(row.progress, 99)
    row.updated_at = _now()
    add_event(db, row, "cancel-requested", {"reason": reason})
    if row.execution_run_id and row.status == "cancelled":
        sync_run_from_job(db, row.user_key, row.execution_run_id, row.job_id, "cancelled", row.progress, error_code="cancelled", error_message=reason)
    db.commit()
    db.refresh(row)
    if row.status == "cancelled":
        _advance_notebook_orchestration(db, row)
    return row


def retry_job(db: Session, user_key: str, job_id: str, reason: str) -> JobRecord:
    row = get_job(db, user_key, job_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace job not found.")
    if row.status not in REQUEUEABLE_STATUSES:
        raise HTTPException(status_code=409, detail="Only failed, blocked, or cancelled jobs can be retried.")
    row.status = "queued"
    row.progress = 0
    row.cancellation_requested = False
    row.worker_id = ""
    row.error_code = ""
    row.error_message = ""
    row.result = {}
    row.queued_at = _now()
    row.started_at = None
    row.finished_at = None
    row.updated_at = _now()
    if row.execution_run_id:
        sync_run_from_job(db, row.user_key, row.execution_run_id, row.job_id, "queued", 0)
    add_event(db, row, "retried", {"reason": reason})
    db.commit()
    db.refresh(row)
    return row


def claim_next_job(db: Session, worker_id: str) -> JobRecord | None:
    stmt = (
        select(JobRecord)
        .where(JobRecord.status == "queued", JobRecord.cancellation_requested.is_(False))
        .order_by(JobRecord.priority.desc(), JobRecord.queued_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    row = db.scalar(stmt)
    if row is None:
        db.rollback()
        return None
    row.status = "running"
    row.attempt += 1
    row.progress = max(row.progress, 1)
    row.worker_id = worker_id
    row.started_at = _now()
    row.updated_at = _now()
    if row.execution_run_id:
        sync_run_from_job(db, row.user_key, row.execution_run_id, row.job_id, "running", row.progress)
    add_event(db, row, "started", {"workerId": worker_id, "attempt": row.attempt})
    db.commit()
    db.refresh(row)
    return row


def complete_job(db: Session, row: JobRecord, result: dict) -> JobRecord:
    current = get_job(db, row.user_key, row.job_id)
    if current is None:
        raise RuntimeError("Job disappeared during execution.")
    if current.cancellation_requested:
        current.status = "cancelled"
        current.progress = min(current.progress, 99)
        current.result = {}
        event = "cancelled"
    else:
        current.status = "succeeded"
        current.progress = 100
        current.result = result
        event = "succeeded"
    current.finished_at = _now()
    current.updated_at = _now()
    if current.execution_run_id:
        sync_run_from_job(db, current.user_key, current.execution_run_id, current.job_id, current.status, current.progress, result=current.result)
    add_event(db, current, event, {"attempt": current.attempt})
    db.commit()
    db.refresh(current)
    _advance_notebook_orchestration(db, current)
    return current


def block_job(db: Session, row: JobRecord, code: str, message: str) -> JobRecord:
    current = get_job(db, row.user_key, row.job_id)
    current.status = "blocked"
    current.error_code = code[:96]
    current.error_message = message[:4000]
    current.finished_at = _now()
    current.updated_at = _now()
    if current.execution_run_id:
        sync_run_from_job(db, current.user_key, current.execution_run_id, current.job_id, "blocked", current.progress, error_code=current.error_code, error_message=current.error_message)
    add_event(db, current, "blocked", {"code": current.error_code})
    db.commit()
    db.refresh(current)
    _advance_notebook_orchestration(db, current)
    return current


def fail_or_requeue_job(db: Session, row: JobRecord, code: str, message: str) -> JobRecord:
    current = get_job(db, row.user_key, row.job_id)
    current.error_code = code[:96]
    current.error_message = message[:4000]
    current.updated_at = _now()
    if current.cancellation_requested:
        current.status = "cancelled"
        current.finished_at = _now()
        event = "cancelled"
    elif current.attempt < current.max_attempts:
        current.status = "queued"
        current.queued_at = _now()
        current.started_at = None
        current.worker_id = ""
        current.progress = 0
        event = "retry-queued"
    else:
        current.status = "failed"
        current.finished_at = _now()
        event = "failed"
    if current.execution_run_id:
        sync_run_from_job(db, current.user_key, current.execution_run_id, current.job_id, current.status, current.progress, error_code=current.error_code, error_message=current.error_message)
    add_event(db, current, event, {"code": current.error_code, "attempt": current.attempt, "maxAttempts": current.max_attempts})
    db.commit()
    db.refresh(current)
    if current.status in TERMINAL_STATUSES or current.status == "blocked":
        _advance_notebook_orchestration(db, current)
    return current


def update_heartbeat(db: Session, worker_id: str, version: str, status: str = "idle", active_job_id: str = "") -> None:
    row = db.get(WorkerHeartbeat, worker_id)
    if row is None:
        row = WorkerHeartbeat(worker_id=worker_id, version=version)
        db.add(row)
    row.version = version
    row.status = status
    row.active_job_id = active_job_id
    row.last_seen_at = _now()
    db.commit()


def list_worker_heartbeats(db: Session) -> list[dict]:
    rows = db.scalars(select(WorkerHeartbeat).order_by(WorkerHeartbeat.last_seen_at.desc())).all()
    return [{
        "workerId": row.worker_id,
        "version": row.version,
        "status": row.status,
        "activeJobId": row.active_job_id,
        "lastSeenAt": iso(row.last_seen_at),
    } for row in rows]
