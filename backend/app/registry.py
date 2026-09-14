from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    ArtifactHead,
    DatasetHead,
    DatasetRevision,
    ExecutionRun,
    ExecutionRunEvent,
    ExecutionRunOutput,
    ModelHead,
    ModelRevision,
    ParameterSetHead,
    ParameterSetRevision,
)
from .schemas import (
    DatasetStoreRequest,
    ExecutionRunCreateRequest,
    ExecutionRunOutputRequest,
    ExecutionRunUpdateRequest,
    ModelStoreRequest,
    ParameterSetStoreRequest,
)
from .utils import iso, sha256_hex
from .environments import resolve_environment_ref

TERMINAL_RUN_STATUSES = {"succeeded", "failed", "blocked", "cancelled"}
RUN_TRANSITIONS = {
    "planned": {"planned", "queued", "running", "cancelled", "blocked", "failed"},
    "queued": {"queued", "running", "cancelled", "blocked", "failed", "succeeded"},
    "running": {"running", "succeeded", "failed", "blocked", "cancelled"},
    "failed": {"failed", "queued", "running"},
    "blocked": {"blocked", "queued", "running", "cancelled"},
    "cancelled": {"cancelled", "queued"},
    "succeeded": {"succeeded"},
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in tags:
        item = str(value).strip()
        if not item:
            continue
        item = item[:160]
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out[:50]


def dataset_metadata(row) -> dict:
    return {
        "datasetId": row.dataset_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "datasetType": row.dataset_type,
        "sourceKind": row.source_kind,
        "artifactId": row.artifact_id,
        "externalUri": row.external_uri,
        "revision": row.revision,
        "fingerprint": row.fingerprint,
        "schemaDefinition": row.schema_json,
        "lineage": row.lineage_json,
        "tags": row.tags_json,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def model_metadata(row) -> dict:
    return {
        "modelId": row.model_id,
        "projectId": row.project_id,
        "name": row.name,
        "description": row.description,
        "modelKind": row.model_kind,
        "framework": row.framework,
        "algorithm": row.algorithm,
        "versionLabel": row.version_label,
        "sourceArtifactId": row.source_artifact_id,
        "executionTarget": row.execution_target,
        "executionOperation": row.execution_operation,
        "revision": row.revision,
        "fingerprint": row.fingerprint,
        "inputSchema": row.input_schema_json,
        "outputSchema": row.output_schema_json,
        "configuration": row.configuration_json,
        "lineage": row.lineage_json,
        "tags": row.tags_json,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def parameter_set_metadata(row) -> dict:
    return {
        "parameterSetId": row.parameter_set_id,
        "projectId": row.project_id,
        "modelId": row.model_id,
        "name": row.name,
        "revision": row.revision,
        "fingerprint": row.fingerprint,
        "parameters": row.parameters_json,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
        "updatedAt": iso(getattr(row, "updated_at", row.created_at)),
    }


def run_metadata(row: ExecutionRun) -> dict:
    return {
        "runId": row.run_id,
        "projectId": row.project_id,
        "name": row.name,
        "status": row.status,
        "progress": row.progress,
        "jobId": row.job_id,
        "targetProduct": row.target_product,
        "operation": row.operation,
        "datasetRefs": row.dataset_refs,
        "modelRef": row.model_ref,
        "parameterSetRef": row.parameter_set_ref,
        "environment": row.environment_json,
        "environmentRef": row.environment_ref,
        "environmentFingerprint": row.environment_fingerprint,
        "inputFingerprint": row.input_fingerprint,
        "reproducibilityFingerprint": row.reproducibility_fingerprint,
        "resultSummary": row.result_summary,
        "errorCode": row.error_code,
        "errorMessage": row.error_message,
        "createdAt": iso(row.created_at),
        "startedAt": iso(row.started_at) if row.started_at else None,
        "finishedAt": iso(row.finished_at) if row.finished_at else None,
        "updatedAt": iso(row.updated_at),
    }


def output_metadata(row: ExecutionRunOutput) -> dict:
    return {
        "outputId": row.output_id,
        "runId": row.run_id,
        "artifactId": row.artifact_id,
        "role": row.role,
        "label": row.label,
        "mediaType": row.media_type,
        "sha256": row.sha256,
        "bytes": row.bytes,
        "metadata": row.metadata_json,
        "createdAt": iso(row.created_at),
    }


def _revision_guard(existing, expected_revision: int | None, metadata_fn, noun: str) -> int:
    current = int(existing.revision) if existing is not None else 0
    if existing is None:
        if expected_revision not in (None, 0):
            raise HTTPException(status_code=409, detail={"message": f"Workspace {noun} revision conflict.", "currentRevision": 0, "current": None})
        return current
    if expected_revision is None or expected_revision != current:
        raise HTTPException(status_code=409, detail={"message": f"Workspace {noun} revision conflict.", "currentRevision": current, "current": metadata_fn(existing)})
    return current


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def list_datasets(db: Session, user_key: str, project_id: str | None = None) -> list[dict]:
    stmt = select(DatasetHead).where(DatasetHead.user_key == user_key)
    if project_id:
        stmt = stmt.where(DatasetHead.project_id == project_id)
    rows = db.scalars(stmt.order_by(DatasetHead.updated_at.desc())).all()
    return [dataset_metadata(r) for r in rows]


def get_dataset(db: Session, user_key: str, dataset_id: str) -> DatasetHead | None:
    return db.get(DatasetHead, {"user_key": user_key, "dataset_id": dataset_id})


def get_dataset_revision(db: Session, user_key: str, dataset_id: str, revision: int):
    return db.get(DatasetRevision, {"user_key": user_key, "dataset_id": dataset_id, "revision": revision})


def list_dataset_revisions(db: Session, user_key: str, dataset_id: str) -> list[dict]:
    rows = db.scalars(select(DatasetRevision).where(DatasetRevision.user_key == user_key, DatasetRevision.dataset_id == dataset_id).order_by(DatasetRevision.revision.desc())).all()
    return [dataset_metadata(r) for r in rows]


def store_dataset(db: Session, user_key: str, payload: DatasetStoreRequest):
    settings = get_settings()
    dataset_id = payload.datasetId.strip()
    existing = get_dataset(db, user_key, dataset_id)
    tags = _clean_tags(payload.tags)
    descriptor = {
        "schema": "sc-workspace-dataset-record/1.0",
        "datasetId": dataset_id,
        "projectId": (payload.projectId or "").strip(),
        "name": payload.name.strip(),
        "description": payload.description.strip(),
        "datasetType": payload.datasetType,
        "sourceKind": payload.sourceKind,
        "artifactId": (payload.artifactId or "").strip(),
        "externalUri": (payload.externalUri or "").strip(),
        "schemaDefinition": payload.schemaDefinition,
        "lineage": payload.lineage,
        "tags": tags,
        "metadata": payload.metadata,
    }
    fingerprint = sha256_hex(descriptor)
    operation_id = (payload.operationId or "").strip()
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Dataset operationId was already used for a different record.")
        return existing, True
    current = _revision_guard(existing, payload.expectedRevision, dataset_metadata, "dataset")
    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(DatasetHead).where(DatasetHead.user_key == user_key)) or 0)
        if count >= settings.max_datasets_per_account:
            raise HTTPException(status_code=409, detail="Workspace dataset registry limit reached.")
    if descriptor["artifactId"] and db.get(ArtifactHead, {"user_key": user_key, "artifact_id": descriptor["artifactId"]}) is None:
        raise HTTPException(status_code=409, detail="Dataset artifactId does not reference an existing Workspace artifact.")
    now = _now()
    revision = current + 1
    if existing is None:
        existing = DatasetHead(user_key=user_key, dataset_id=dataset_id, created_at=now)
        db.add(existing)
    existing.project_id = descriptor["projectId"]
    existing.name = descriptor["name"]
    existing.description = descriptor["description"]
    existing.dataset_type = descriptor["datasetType"]
    existing.source_kind = descriptor["sourceKind"]
    existing.artifact_id = descriptor["artifactId"]
    existing.external_uri = descriptor["externalUri"]
    existing.revision = revision
    existing.fingerprint = fingerprint
    existing.last_operation_id = operation_id
    existing.schema_json = descriptor["schemaDefinition"]
    existing.lineage_json = descriptor["lineage"]
    existing.tags_json = tags
    existing.metadata_json = descriptor["metadata"]
    existing.updated_at = now
    db.add(DatasetRevision(
        user_key=user_key, dataset_id=dataset_id, revision=revision, project_id=existing.project_id,
        name=existing.name, description=existing.description, dataset_type=existing.dataset_type,
        source_kind=existing.source_kind, artifact_id=existing.artifact_id, external_uri=existing.external_uri,
        fingerprint=fingerprint, operation_id=operation_id, schema_json=existing.schema_json,
        lineage_json=existing.lineage_json, tags_json=tags, metadata_json=existing.metadata_json, created_at=now,
    ))
    _commit(db, "A concurrent Workspace dataset registry revision was detected.")
    db.refresh(existing)
    return existing, False


def list_models(db: Session, user_key: str, project_id: str | None = None) -> list[dict]:
    stmt = select(ModelHead).where(ModelHead.user_key == user_key)
    if project_id:
        stmt = stmt.where(ModelHead.project_id == project_id)
    rows = db.scalars(stmt.order_by(ModelHead.updated_at.desc())).all()
    return [model_metadata(r) for r in rows]


def get_model(db: Session, user_key: str, model_id: str):
    return db.get(ModelHead, {"user_key": user_key, "model_id": model_id})


def get_model_revision(db: Session, user_key: str, model_id: str, revision: int):
    return db.get(ModelRevision, {"user_key": user_key, "model_id": model_id, "revision": revision})


def list_model_revisions(db: Session, user_key: str, model_id: str) -> list[dict]:
    rows = db.scalars(select(ModelRevision).where(ModelRevision.user_key == user_key, ModelRevision.model_id == model_id).order_by(ModelRevision.revision.desc())).all()
    return [model_metadata(r) for r in rows]


def store_model(db: Session, user_key: str, payload: ModelStoreRequest):
    settings = get_settings()
    model_id = payload.modelId.strip()
    existing = get_model(db, user_key, model_id)
    tags = _clean_tags(payload.tags)
    descriptor = {
        "schema": "sc-workspace-model-record/1.0", "modelId": model_id,
        "projectId": (payload.projectId or "").strip(), "name": payload.name.strip(),
        "description": payload.description.strip(), "modelKind": payload.modelKind,
        "framework": payload.framework.strip(), "algorithm": payload.algorithm.strip(),
        "versionLabel": payload.versionLabel.strip(), "sourceArtifactId": (payload.sourceArtifactId or "").strip(),
        "executionTarget": payload.executionTarget, "executionOperation": payload.executionOperation.strip(),
        "inputSchema": payload.inputSchema, "outputSchema": payload.outputSchema,
        "configuration": payload.configuration, "lineage": payload.lineage, "tags": tags, "metadata": payload.metadata,
    }
    fingerprint = sha256_hex(descriptor)
    operation_id = (payload.operationId or "").strip()
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Model operationId was already used for a different record.")
        return existing, True
    current = _revision_guard(existing, payload.expectedRevision, model_metadata, "model")
    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(ModelHead).where(ModelHead.user_key == user_key)) or 0)
        if count >= settings.max_models_per_account:
            raise HTTPException(status_code=409, detail="Workspace model registry limit reached.")
    if descriptor["sourceArtifactId"] and db.get(ArtifactHead, {"user_key": user_key, "artifact_id": descriptor["sourceArtifactId"]}) is None:
        raise HTTPException(status_code=409, detail="Model sourceArtifactId does not reference an existing Workspace artifact.")
    now = _now(); revision = current + 1
    if existing is None:
        existing = ModelHead(user_key=user_key, model_id=model_id, created_at=now); db.add(existing)
    existing.project_id = descriptor["projectId"]; existing.name = descriptor["name"]; existing.description = descriptor["description"]
    existing.model_kind = descriptor["modelKind"]; existing.framework = descriptor["framework"]; existing.algorithm = descriptor["algorithm"]
    existing.version_label = descriptor["versionLabel"]; existing.source_artifact_id = descriptor["sourceArtifactId"]
    existing.execution_target = descriptor["executionTarget"]; existing.execution_operation = descriptor["executionOperation"]
    existing.revision = revision; existing.fingerprint = fingerprint; existing.last_operation_id = operation_id
    existing.input_schema_json = descriptor["inputSchema"]; existing.output_schema_json = descriptor["outputSchema"]
    existing.configuration_json = descriptor["configuration"]; existing.lineage_json = descriptor["lineage"]
    existing.tags_json = tags; existing.metadata_json = descriptor["metadata"]; existing.updated_at = now
    db.add(ModelRevision(
        user_key=user_key, model_id=model_id, revision=revision, project_id=existing.project_id, name=existing.name,
        description=existing.description, model_kind=existing.model_kind, framework=existing.framework, algorithm=existing.algorithm,
        version_label=existing.version_label, source_artifact_id=existing.source_artifact_id,
        execution_target=existing.execution_target, execution_operation=existing.execution_operation,
        fingerprint=fingerprint, operation_id=operation_id, input_schema_json=existing.input_schema_json,
        output_schema_json=existing.output_schema_json, configuration_json=existing.configuration_json,
        lineage_json=existing.lineage_json, tags_json=tags, metadata_json=existing.metadata_json, created_at=now,
    ))
    _commit(db, "A concurrent Workspace model registry revision was detected.")
    db.refresh(existing)
    return existing, False


def list_parameter_sets(db: Session, user_key: str, model_id: str | None = None) -> list[dict]:
    stmt = select(ParameterSetHead).where(ParameterSetHead.user_key == user_key)
    if model_id:
        stmt = stmt.where(ParameterSetHead.model_id == model_id)
    rows = db.scalars(stmt.order_by(ParameterSetHead.updated_at.desc())).all()
    return [parameter_set_metadata(r) for r in rows]


def get_parameter_set(db: Session, user_key: str, parameter_set_id: str):
    return db.get(ParameterSetHead, {"user_key": user_key, "parameter_set_id": parameter_set_id})


def get_parameter_set_revision(db: Session, user_key: str, parameter_set_id: str, revision: int):
    return db.get(ParameterSetRevision, {"user_key": user_key, "parameter_set_id": parameter_set_id, "revision": revision})


def list_parameter_set_revisions(db: Session, user_key: str, parameter_set_id: str) -> list[dict]:
    rows = db.scalars(select(ParameterSetRevision).where(ParameterSetRevision.user_key == user_key, ParameterSetRevision.parameter_set_id == parameter_set_id).order_by(ParameterSetRevision.revision.desc())).all()
    return [parameter_set_metadata(r) for r in rows]


def store_parameter_set(db: Session, user_key: str, payload: ParameterSetStoreRequest):
    settings = get_settings(); parameter_set_id = payload.parameterSetId.strip()
    existing = get_parameter_set(db, user_key, parameter_set_id)
    descriptor = {
        "schema": "sc-workspace-parameter-set/1.0", "parameterSetId": parameter_set_id,
        "projectId": (payload.projectId or "").strip(), "modelId": (payload.modelId or "").strip(),
        "name": payload.name.strip(), "parameters": payload.parameters, "metadata": payload.metadata,
    }
    fingerprint = sha256_hex(descriptor); operation_id = (payload.operationId or "").strip()
    if existing is not None and operation_id and existing.last_operation_id == operation_id:
        if existing.fingerprint != fingerprint:
            raise HTTPException(status_code=409, detail="Parameter-set operationId was already used for a different record.")
        return existing, True
    current = _revision_guard(existing, payload.expectedRevision, parameter_set_metadata, "parameter set")
    if existing is None:
        count = int(db.scalar(select(func.count()).select_from(ParameterSetHead).where(ParameterSetHead.user_key == user_key)) or 0)
        if count >= settings.max_parameter_sets_per_account:
            raise HTTPException(status_code=409, detail="Workspace parameter-set registry limit reached.")
    if descriptor["modelId"] and get_model(db, user_key, descriptor["modelId"]) is None:
        raise HTTPException(status_code=409, detail="Parameter set modelId does not reference a registered Workspace model.")
    now = _now(); revision = current + 1
    if existing is None:
        existing = ParameterSetHead(user_key=user_key, parameter_set_id=parameter_set_id, created_at=now); db.add(existing)
    existing.project_id=descriptor["projectId"]; existing.model_id=descriptor["modelId"]; existing.name=descriptor["name"]
    existing.revision=revision; existing.fingerprint=fingerprint; existing.last_operation_id=operation_id
    existing.parameters_json=descriptor["parameters"]; existing.metadata_json=descriptor["metadata"]; existing.updated_at=now
    db.add(ParameterSetRevision(
        user_key=user_key, parameter_set_id=parameter_set_id, revision=revision, project_id=existing.project_id,
        model_id=existing.model_id, name=existing.name, fingerprint=fingerprint, operation_id=operation_id,
        parameters_json=existing.parameters_json, metadata_json=existing.metadata_json, created_at=now,
    ))
    _commit(db, "A concurrent Workspace parameter-set registry revision was detected.")
    db.refresh(existing)
    return existing, False


def _resolve_dataset_ref(db: Session, user_key: str, ref) -> dict:
    if ref.revision:
        row = get_dataset_revision(db, user_key, ref.datasetId, ref.revision)
    else:
        row = get_dataset(db, user_key, ref.datasetId)
    if row is None:
        raise HTTPException(status_code=409, detail=f"Execution run dataset reference not found: {ref.datasetId}")
    return {"datasetId": row.dataset_id, "revision": row.revision, "fingerprint": row.fingerprint}


def _resolve_model_ref(db: Session, user_key: str, ref):
    if ref is None:
        return {}, None
    row = get_model_revision(db, user_key, ref.modelId, ref.revision) if ref.revision else get_model(db, user_key, ref.modelId)
    if row is None:
        raise HTTPException(status_code=409, detail=f"Execution run model reference not found: {ref.modelId}")
    return {"modelId": row.model_id, "revision": row.revision, "fingerprint": row.fingerprint}, row


def _resolve_parameter_ref(db: Session, user_key: str, ref):
    if ref is None:
        return {}, None
    row = get_parameter_set_revision(db, user_key, ref.parameterSetId, ref.revision) if ref.revision else get_parameter_set(db, user_key, ref.parameterSetId)
    if row is None:
        raise HTTPException(status_code=409, detail=f"Execution run parameter-set reference not found: {ref.parameterSetId}")
    return {"parameterSetId": row.parameter_set_id, "revision": row.revision, "fingerprint": row.fingerprint}, row


def _next_run_event_sequence(db: Session, user_key: str, run_id: str) -> int:
    current = db.scalar(select(func.max(ExecutionRunEvent.sequence)).where(ExecutionRunEvent.user_key == user_key, ExecutionRunEvent.run_id == run_id))
    return int(current or 0) + 1


def add_run_event(db: Session, row: ExecutionRun, event_type: str, details: dict | None = None) -> None:
    db.add(ExecutionRunEvent(
        user_key=row.user_key, run_id=row.run_id, sequence=_next_run_event_sequence(db, row.user_key, row.run_id),
        event_type=event_type, status=row.status, progress=row.progress, details=details or {},
    ))


def _run_output_fingerprint(db: Session, row: ExecutionRun) -> str:
    outputs = db.scalars(select(ExecutionRunOutput).where(ExecutionRunOutput.user_key == row.user_key, ExecutionRunOutput.run_id == row.run_id).order_by(ExecutionRunOutput.output_id.asc())).all()
    evidence = [{"outputId": x.output_id, "artifactId": x.artifact_id, "sha256": x.sha256, "bytes": x.bytes, "role": x.role} for x in outputs]
    return sha256_hex({"inputFingerprint": row.input_fingerprint, "outputs": evidence})


def create_execution_run(db: Session, user_key: str, payload: ExecutionRunCreateRequest):
    settings = get_settings(); idem = (payload.idempotencyKey or "").strip()
    dataset_refs = [_resolve_dataset_ref(db, user_key, r) for r in payload.datasetRefs]
    model_ref, model_row = _resolve_model_ref(db, user_key, payload.modelRef)
    parameter_ref, parameter_row = _resolve_parameter_ref(db, user_key, payload.parameterSetRef)
    environment_ref, environment_row = resolve_environment_ref(db, user_key, payload.environmentRef)
    if parameter_row is not None and model_row is not None and parameter_row.model_id and parameter_row.model_id != model_row.model_id:
        raise HTTPException(status_code=409, detail="Execution run parameter set is registered to a different model.")
    target = payload.targetProduct or (model_row.execution_target if model_row is not None else "") or "workspace"
    operation = payload.operation.strip() or (model_row.execution_operation if model_row is not None else "")
    if not operation:
        raise HTTPException(status_code=400, detail="Execution run requires an operation or a model with an executionOperation.")
    input_doc = {
        "datasets": dataset_refs,
        "model": model_ref,
        "parameterSet": parameter_ref,
        "environmentRef": environment_ref,
        "environmentFingerprint": environment_row.fingerprint if environment_row is not None else sha256_hex({"inlineEnvironment": payload.environment}),
        "inlineEnvironment": payload.environment,
        "targetProduct": target,
        "operation": operation,
    }
    input_fingerprint = sha256_hex(input_doc)
    if idem:
        existing = db.scalar(select(ExecutionRun).where(ExecutionRun.user_key == user_key, ExecutionRun.idempotency_key == idem).order_by(ExecutionRun.created_at.desc()))
        if existing is not None:
            if existing.input_fingerprint != input_fingerprint:
                raise HTTPException(status_code=409, detail="Execution-run idempotency key was already used for different resolved inputs.")
            return existing, True
    count = int(db.scalar(select(func.count()).select_from(ExecutionRun).where(ExecutionRun.user_key == user_key)) or 0)
    if count >= settings.max_execution_runs_per_account:
        raise HTTPException(status_code=409, detail="Workspace execution-run registry limit reached.")
    run_id = (payload.runId or f"run-{uuid4()}").strip()
    if db.get(ExecutionRun, {"user_key": user_key, "run_id": run_id}) is not None:
        raise HTTPException(status_code=409, detail="Workspace execution run id already exists.")
    now = _now()
    row = ExecutionRun(
        user_key=user_key, run_id=run_id, project_id=(payload.projectId or "").strip(), name=payload.name.strip() or "Execution run",
        status="planned", progress=0, job_id="", target_product=target, operation=operation,
        dataset_refs=dataset_refs, model_ref=model_ref, parameter_set_ref=parameter_ref, environment_json=payload.environment,
        environment_ref=environment_ref, environment_fingerprint=(environment_row.fingerprint if environment_row is not None else sha256_hex({"inlineEnvironment": payload.environment})),
        input_fingerprint=input_fingerprint, reproducibility_fingerprint=sha256_hex({"inputFingerprint": input_fingerprint, "outputs": []}),
        result_summary={}, idempotency_key=idem, created_at=now, updated_at=now,
    )
    db.add(row); add_run_event(db, row, "created", {"inputFingerprint": input_fingerprint})
    _commit(db, "A concurrent Workspace execution run was detected.")
    db.refresh(row)
    return row, False


def get_execution_run(db: Session, user_key: str, run_id: str):
    return db.get(ExecutionRun, {"user_key": user_key, "run_id": run_id})


def list_execution_runs(db: Session, user_key: str, status_value: str | None = None, project_id: str | None = None, limit: int = 100) -> list[dict]:
    stmt = select(ExecutionRun).where(ExecutionRun.user_key == user_key)
    if status_value: stmt = stmt.where(ExecutionRun.status == status_value)
    if project_id: stmt = stmt.where(ExecutionRun.project_id == project_id)
    rows = db.scalars(stmt.order_by(ExecutionRun.created_at.desc()).limit(max(1, min(limit, 250)))).all()
    return [run_metadata(r) for r in rows]


def list_run_events(db: Session, user_key: str, run_id: str) -> list[dict]:
    rows = db.scalars(select(ExecutionRunEvent).where(ExecutionRunEvent.user_key == user_key, ExecutionRunEvent.run_id == run_id).order_by(ExecutionRunEvent.sequence.asc())).all()
    return [{"sequence": r.sequence, "eventType": r.event_type, "status": r.status, "progress": r.progress, "details": r.details, "createdAt": iso(r.created_at)} for r in rows]


def update_execution_run(db: Session, user_key: str, run_id: str, payload: ExecutionRunUpdateRequest, event_type: str = "state-updated"):
    row = get_execution_run(db, user_key, run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Workspace execution run not found.")
    if payload.status not in RUN_TRANSITIONS.get(row.status, {row.status}):
        raise HTTPException(status_code=409, detail=f"Invalid execution-run transition: {row.status} -> {payload.status}")
    now = _now(); old_status = row.status
    row.status = payload.status; row.progress = payload.progress; row.updated_at = now
    if payload.jobId is not None: row.job_id = payload.jobId.strip()
    if payload.resultSummary: row.result_summary = payload.resultSummary
    row.error_code = payload.errorCode.strip(); row.error_message = payload.errorMessage.strip()
    if row.status == "running" and row.started_at is None: row.started_at = now
    if row.status in TERMINAL_RUN_STATUSES: row.finished_at = now
    if row.status in {"planned", "queued", "running"}: row.finished_at = None
    row.reproducibility_fingerprint = _run_output_fingerprint(db, row)
    add_run_event(db, row, event_type, {"from": old_status, "to": row.status})
    db.commit(); db.refresh(row); return row


def link_job_to_run(db: Session, user_key: str, run_id: str, job_id: str, target_product: str = "", operation: str = "") -> ExecutionRun:
    row = get_execution_run(db, user_key, run_id)
    if row is None:
        raise HTTPException(status_code=409, detail="executionRunId does not reference a registered Workspace execution run.")
    if row.job_id and row.job_id != job_id:
        raise HTTPException(status_code=409, detail="Execution run is already linked to another job.")
    if target_product and row.target_product != target_product:
        raise HTTPException(status_code=409, detail="Job targetProduct does not match the registered execution run.")
    if operation and row.operation != operation:
        raise HTTPException(status_code=409, detail="Job operation does not match the registered execution run.")
    row.job_id = job_id; row.status = "queued"; row.progress = 0; row.finished_at = None; row.updated_at = _now()
    add_run_event(db, row, "job-linked", {"jobId": job_id})
    return row


def sync_run_from_job(db: Session, user_key: str, run_id: str, job_id: str, status_value: str, progress: int, result: dict | None = None, error_code: str = "", error_message: str = "") -> None:
    if not run_id:
        return
    row = get_execution_run(db, user_key, run_id)
    if row is None:
        return
    now = _now(); old = row.status
    row.job_id = job_id; row.status = status_value; row.progress = max(0, min(100, int(progress))); row.updated_at = now
    if status_value == "running" and row.started_at is None: row.started_at = now
    if status_value in TERMINAL_RUN_STATUSES:
        row.finished_at = now
    elif status_value in {"planned", "queued", "running"}:
        row.finished_at = None
    if result is not None: row.result_summary = result
    row.error_code = error_code[:96]; row.error_message = error_message[:4000]
    row.reproducibility_fingerprint = _run_output_fingerprint(db, row)
    add_run_event(db, row, "job-state", {"jobId": job_id, "from": old, "to": status_value})


def store_run_output(db: Session, user_key: str, run_id: str, payload: ExecutionRunOutputRequest):
    run = get_execution_run(db, user_key, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workspace execution run not found.")
    existing = db.get(ExecutionRunOutput, {"user_key": user_key, "run_id": run_id, "output_id": payload.outputId})
    if existing is not None:
        return existing, True
    artifact_id = (payload.artifactId or "").strip(); digest = (payload.sha256 or "").lower(); media_type = payload.mediaType; byte_count = payload.bytes
    if artifact_id:
        artifact = db.get(ArtifactHead, {"user_key": user_key, "artifact_id": artifact_id})
        if artifact is None:
            raise HTTPException(status_code=409, detail="Run output artifactId does not reference an existing Workspace artifact.")
        digest = artifact.sha256; media_type = artifact.media_type; byte_count = artifact.bytes
    if not artifact_id and not digest:
        raise HTTPException(status_code=400, detail="Run output requires an artifactId or SHA-256 digest.")
    row = ExecutionRunOutput(
        user_key=user_key, run_id=run_id, output_id=payload.outputId.strip(), artifact_id=artifact_id,
        role=payload.role.strip() or "result", label=payload.label.strip(), media_type=media_type,
        sha256=digest, bytes=byte_count, metadata_json=payload.metadata,
    )
    db.add(row); db.flush(); run.reproducibility_fingerprint = _run_output_fingerprint(db, run); run.updated_at = _now()
    add_run_event(db, run, "output-registered", {"outputId": row.output_id, "artifactId": artifact_id, "sha256": digest})
    db.commit(); db.refresh(row); return row, False


def list_run_outputs(db: Session, user_key: str, run_id: str) -> list[dict]:
    if get_execution_run(db, user_key, run_id) is None:
        raise HTTPException(status_code=404, detail="Workspace execution run not found.")
    rows = db.scalars(select(ExecutionRunOutput).where(ExecutionRunOutput.user_key == user_key, ExecutionRunOutput.run_id == run_id).order_by(ExecutionRunOutput.created_at.asc())).all()
    return [output_metadata(r) for r in rows]
