from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import initialize_schema, ping_database, session_scope
from .repository import (
    delete_notebook,
    delete_project,
    get_notebook,
    get_project,
    get_project_revision,
    list_notebooks,
    list_project_revisions,
    list_projects,
    notebook_metadata,
    project_metadata,
    store_notebook,
    store_project,
)
from .schemas import (
    ArtifactStoreRequest, DatasetStoreRequest, ExecutionEnvironmentStoreRequest, ExecutionRunCreateRequest, ExecutionRunOutputRequest,
    RuntimeAdapterStoreRequest, RuntimeCompatibilityCheckRequest, ReproductionPlanCreateRequest, ReproductionVerificationCreateRequest,
    ExecutionRunUpdateRequest, JobActionRequest, JobCreateRequest, LegacyMigrationRequest, ModelStoreRequest,
    NotebookStoreRequest, ParameterSetStoreRequest, ProjectStoreRequest, RecoverySnapshotRequest,
)
from .security import ServiceIdentity, require_service_identity
from .migration import apply_migration, list_receipts, migration_plan
from .object_store import artifact_metadata, delete_artifact, get_artifact, list_artifacts, read_artifact_content, store_artifact, verify_artifact_storage
from .recovery import create_snapshot, get_snapshot, list_snapshots, snapshot_metadata
from .jobs import create_job, get_job, job_metadata, list_job_events, list_jobs, list_worker_heartbeats, request_cancel, retry_job
from .routing import configured_route_count, route_registry
from .registry import (
    create_execution_run, dataset_metadata, get_dataset, get_dataset_revision, get_execution_run, get_model,
    get_model_revision, get_parameter_set, get_parameter_set_revision, list_dataset_revisions, list_datasets,
    list_execution_runs, list_model_revisions, list_models, list_parameter_set_revisions, list_parameter_sets,
    list_run_events, list_run_outputs, model_metadata, output_metadata, parameter_set_metadata, run_metadata,
    store_dataset, store_model, store_parameter_set, store_run_output, update_execution_run,
)
from .utils import iso
from .environments import environment_metadata, get_environment, get_environment_revision, list_environment_revisions, list_environments, store_environment
from .runtime_adapters import adapter_metadata, check_environment_compatibility, get_adapter, get_adapter_revision, list_adapter_revisions, list_adapters, store_adapter
from .reproduction import create_reproduction_plan, create_verification, get_reproduction_plan, get_verification, list_reproduction_plans, list_verifications, plan_metadata, verification_metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.auto_create_schema:
        initialize_schema()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get(settings.request_id_header) or str(uuid4())
    response = await call_next(request)
    response.headers[settings.request_id_header] = request_id
    return response


@app.exception_handler(HTTPException)
async def workspace_http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        body = {"ok": False, **detail}
    else:
        body = {"ok": False, "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers)


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": settings.service_name,
        "version": settings.service_version,
        "persistence": "postgresql",
        "projectSchema": "sc-workspace-project/20.0",
        "notebookSchema": "sc-workspace-notebook/3.0",
        "localFirst": True,
        "objectStorage": "content-addressed-filesystem",
        "recoverySnapshots": True,
        "legacyMigration": True,
        "backgroundJobs": True,
        "computeOrchestration": True,
        "workerMode": "separate-process",
        "datasetRegistry": True,
        "modelRegistry": True,
        "executionRunRegistry": True,
        "reproducibilityLineage": True,
        "executionEnvironmentRegistry": True,
        "dependencyManifests": True,
        "dependencyLockArtifacts": True,
        "containerIdentityCapture": True,
        "runtimeVersionCapture": True,
        "randomSeedCapture": True,
        "runtimeAdapterRegistry": True,
        "runtimeCompatibilityChecks": True,
        "reproductionPlans": True,
        "reproductionVerification": True,
        "arbitraryCodeExecution": False,
    }


@app.get("/ready")
def ready():
    try:
        ping_database()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc.__class__.__name__}")
    if not settings.token_configured:
        raise HTTPException(status_code=503, detail="Service token is not configured.")
    return {"ok": True, "database": "ready", "serviceAuth": "ready"}


@app.get("/v1/capabilities")
def capabilities(identity: ServiceIdentity = Depends(require_service_identity)):
    return {
        "schema": "sc-workspace-backend-capabilities/1.0",
        "version": settings.service_version,
        "userScoped": True,
        "browserDirectAccess": False,
        "wordpressProxyRequired": True,
        "projectPersistence": True,
        "notebookPersistence": True,
        "projectRevisionHistory": True,
        "notebookRevisionHistory": True,
        "revisionPreconditions": True,
        "idempotentOperations": True,
        "integrityAlgorithm": "SHA-256",
        "database": "PostgreSQL",
        "objectStorage": True,
        "objectStorageMode": "content-addressed-filesystem",
        "legacyUserMetaMigration": True,
        "migrationReceipts": True,
        "recoverySnapshots": True,
        "storageIntegrityChecks": True,
        "backgroundJobs": True,
        "durableJobQueue": True,
        "workerProcess": True,
        "jobEventHistory": True,
        "jobRetryAndCancel": True,
        "computeOrchestration": True,
        "orchestrationContract": "sc-workspace-compute-handoff/1.0",
        "serverConfiguredRoutesOnly": True,
        "configuredRouteCount": configured_route_count(),
        "datasetRegistry": True,
        "datasetRevisionHistory": True,
        "modelRegistry": True,
        "modelRevisionHistory": True,
        "parameterSetRegistry": True,
        "executionRunRegistry": True,
        "executionRunEvents": True,
        "executionRunOutputs": True,
        "jobExecutionRunLinkage": True,
        "reproducibilityFingerprints": True,
        "executionEnvironmentRegistry": True,
        "executionEnvironmentRevisionHistory": True,
        "dependencyManifests": True,
        "dependencyLockArtifacts": True,
        "containerIdentityCapture": True,
        "runtimeVersionCapture": True,
        "randomSeedCapture": True,
        "runtimeAdapterRegistry": True,
        "runtimeAdapterRevisionHistory": True,
        "runtimeCompatibilityChecks": True,
        "reproductionPlans": True,
        "reproductionVerification": True,
        "deterministicRerunComparison": True,
        "comparisonMode": "metadata-and-content-digests",
        "arbitraryCodeExecution": False,
        "secretEnvironmentValuesCaptured": False,
        "limits": {
            "projectsPerAccount": settings.max_projects_per_account,
            "projectBytes": settings.max_project_bytes,
            "accountBytes": settings.max_account_bytes,
            "notebooksPerAccount": settings.max_notebooks_per_account,
            "notebookBytes": settings.max_notebook_bytes,
            "artifactsPerAccount": settings.max_artifacts_per_account,
            "artifactBytes": settings.max_artifact_bytes,
            "artifactAccountBytes": settings.max_artifact_account_bytes,
            "recoverySnapshotsPerAccount": settings.max_recovery_snapshots_per_account,
            "datasetsPerAccount": settings.max_datasets_per_account,
            "modelsPerAccount": settings.max_models_per_account,
            "parameterSetsPerAccount": settings.max_parameter_sets_per_account,
            "executionRunsPerAccount": settings.max_execution_runs_per_account,
            "executionEnvironmentsPerAccount": settings.max_execution_environments_per_account,
            "runtimeAdaptersPerAccount": settings.max_runtime_adapters_per_account,
            "jobsPerAccount": settings.max_jobs_per_account,
            "defaultJobMaxAttempts": settings.default_job_max_attempts,
        },
    }


@app.get("/v1/projects")
def projects_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-cloud-index/1.1", "items": list_projects(db, identity.user_key), "automaticSync": False, "explicitSync": True, "store": "workspace-backend-postgresql"}


@app.post("/v1/projects")
def project_store(payload: ProjectStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_project(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": project_metadata(row)}


@app.get("/v1/projects/{project_id}")
def project_get(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_project(db, identity.user_key, project_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace account project copy not found.")
        return {"schema": "sc-workspace-cloud-backup-response/1.1", "item": project_metadata(row), "package": row.package}


@app.delete("/v1/projects/{project_id}")
def project_delete(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_project(db, identity.user_key, project_id)}


@app.get("/v1/projects/{project_id}/revisions")
def project_revisions(project_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-backend-project-revisions/1.0", "projectId": project_id, "items": list_project_revisions(db, identity.user_key, project_id)}


@app.get("/v1/projects/{project_id}/revisions/{revision}")
def project_revision_get(project_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_project_revision(db, identity.user_key, project_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace project revision not found.")
        return {"schema": "sc-workspace-backend-project-revision/1.0", "projectId": project_id, "revision": revision, "backedUpAt": iso(row.backed_up_at), "fingerprint": row.fingerprint, "package": row.package}


@app.get("/v1/notebooks")
def notebooks_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-notebook-cloud-index/1.0", "items": list_notebooks(db, identity.user_key), "automaticSync": False, "explicitSync": True, "store": "workspace-backend-postgresql"}


@app.post("/v1/notebooks")
def notebook_store_route(payload: NotebookStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_notebook(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": notebook_metadata(row)}


@app.get("/v1/notebooks/{notebook_id}")
def notebook_get_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_notebook(db, identity.user_key, notebook_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Notebook account copy not found.")
        return {"schema": "sc-workspace-notebook-cloud-backup-response/1.0", "item": notebook_metadata(row), "package": row.package}


@app.delete("/v1/notebooks/{notebook_id}")
def notebook_delete_route(notebook_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_notebook(db, identity.user_key, notebook_id)}


@app.post("/v1/migrations/legacy-user-meta/plan")
def legacy_migration_plan(payload: LegacyMigrationRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return migration_plan(db, identity.user_key, payload)


@app.post("/v1/migrations/legacy-user-meta/apply")
def legacy_migration_apply(payload: LegacyMigrationRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    payload.dryRun = False
    with session_scope() as db:
        return apply_migration(db, identity.user_key, payload)


@app.get("/v1/migrations/receipts")
def migration_receipts(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-migration-receipt-index/1.0", "items": list_receipts(db, identity.user_key)}


@app.get("/v1/artifacts")
def artifacts_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-artifact-index/1.0", "items": list_artifacts(db, identity.user_key)}


@app.post("/v1/artifacts")
def artifact_store_route(payload: ArtifactStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = store_artifact(db, identity.user_key, payload)
        return {"ok": True, "item": artifact_metadata(row)}


@app.get("/v1/artifacts/{artifact_id}")
def artifact_get_route(artifact_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    import base64
    with session_scope() as db:
        row = get_artifact(db, identity.user_key, artifact_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace artifact not found.")
        content = read_artifact_content(row)
        return {"schema": "sc-workspace-artifact-response/1.0", "item": artifact_metadata(row), "contentBase64": base64.b64encode(content).decode("ascii")}


@app.delete("/v1/artifacts/{artifact_id}")
def artifact_delete_route(artifact_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok": True, "deleted": delete_artifact(db, identity.user_key, artifact_id)}


@app.get("/v1/storage/integrity")
def storage_integrity(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        result = verify_artifact_storage(db, identity.user_key)
        return {"schema": "sc-workspace-storage-integrity/1.0", **result}


@app.post("/v1/recovery/snapshots")
def recovery_snapshot_create(payload: RecoverySnapshotRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = create_snapshot(db, identity.user_key, payload.reason)
        return {"ok": True, "item": snapshot_metadata(row)}


@app.get("/v1/recovery/snapshots")
def recovery_snapshot_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-recovery-snapshot-index/1.0", "items": list_snapshots(db, identity.user_key)}


@app.get("/v1/recovery/snapshots/{snapshot_id}")
def recovery_snapshot_get(snapshot_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_snapshot(db, identity.user_key, snapshot_id)
        return {"schema": "sc-workspace-recovery-snapshot/1.0", "item": snapshot_metadata(row), "manifest": row.manifest}


@app.get("/v1/orchestration/routes")
def orchestration_routes(identity: ServiceIdentity = Depends(require_service_identity)):
    return {
        "schema": "sc-workspace-orchestration-route-registry/1.0",
        "items": list(route_registry().values()),
        "serverConfiguredOnly": True,
        "browserSuppliedUrlsAllowed": False,
    }


@app.get("/v1/worker/status")
def worker_status(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-worker-status/1.0", "items": list_worker_heartbeats(db)}


@app.get("/v1/jobs")
def jobs_index(
    status: str | None = Query(default=None, max_length=32),
    targetProduct: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=250),
    identity: ServiceIdentity = Depends(require_service_identity),
):
    with session_scope() as db:
        return {
            "schema": "sc-workspace-job-index/1.0",
            "items": list_jobs(db, identity.user_key, status, targetProduct, limit),
            "durable": True,
            "pollingSupported": True,
        }


@app.post("/v1/jobs")
def job_create_route(payload: JobCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = create_job(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": job_metadata(row)}


@app.get("/v1/jobs/{job_id}")
def job_get_route(job_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_job(db, identity.user_key, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace job not found.")
        return {"schema": "sc-workspace-job/1.0", "item": job_metadata(row), "result": row.result}


@app.get("/v1/jobs/{job_id}/events")
def job_events_route(job_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_job(db, identity.user_key, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace job not found.")
        return {"schema": "sc-workspace-job-event-index/1.0", "jobId": job_id, "items": list_job_events(db, identity.user_key, job_id)}


@app.post("/v1/jobs/{job_id}/cancel")
def job_cancel_route(job_id: str, payload: JobActionRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = request_cancel(db, identity.user_key, job_id, payload.reason)
        return {"ok": True, "item": job_metadata(row)}


@app.post("/v1/jobs/{job_id}/retry")
def job_retry_route(job_id: str, payload: JobActionRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = retry_job(db, identity.user_key, job_id, payload.reason)
        return {"ok": True, "item": job_metadata(row)}


@app.get("/v1/datasets")
def datasets_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-dataset-index/1.0", "items": list_datasets(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/datasets")
def dataset_store_route(payload: DatasetStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_dataset(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": dataset_metadata(row)}


@app.get("/v1/datasets/{dataset_id}")
def dataset_get_route(dataset_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_dataset(db, identity.user_key, dataset_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace dataset not found.")
        return {"schema": "sc-workspace-dataset-response/1.0", "item": dataset_metadata(row)}


@app.get("/v1/datasets/{dataset_id}/revisions")
def dataset_revisions_route(dataset_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-dataset-revision-index/1.0", "datasetId": dataset_id, "items": list_dataset_revisions(db, identity.user_key, dataset_id)}


@app.get("/v1/datasets/{dataset_id}/revisions/{revision}")
def dataset_revision_get_route(dataset_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_dataset_revision(db, identity.user_key, dataset_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace dataset revision not found.")
        return {"schema": "sc-workspace-dataset-revision/1.0", "item": dataset_metadata(row)}


@app.get("/v1/models")
def models_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-model-index/1.0", "items": list_models(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/models")
def model_store_route(payload: ModelStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_model(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": model_metadata(row)}


@app.get("/v1/models/{model_id}")
def model_get_route(model_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_model(db, identity.user_key, model_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace model not found.")
        return {"schema": "sc-workspace-model-response/1.0", "item": model_metadata(row)}


@app.get("/v1/models/{model_id}/revisions")
def model_revisions_route(model_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-model-revision-index/1.0", "modelId": model_id, "items": list_model_revisions(db, identity.user_key, model_id)}


@app.get("/v1/models/{model_id}/revisions/{revision}")
def model_revision_get_route(model_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_model_revision(db, identity.user_key, model_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace model revision not found.")
        return {"schema": "sc-workspace-model-revision/1.0", "item": model_metadata(row)}


@app.get("/v1/parameter-sets")
def parameter_sets_index(modelId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-parameter-set-index/1.0", "items": list_parameter_sets(db, identity.user_key, modelId), "revisioned": True}


@app.post("/v1/parameter-sets")
def parameter_set_store_route(payload: ParameterSetStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_parameter_set(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": parameter_set_metadata(row)}


@app.get("/v1/parameter-sets/{parameter_set_id}")
def parameter_set_get_route(parameter_set_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_parameter_set(db, identity.user_key, parameter_set_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace parameter set not found.")
        return {"schema": "sc-workspace-parameter-set-response/1.0", "item": parameter_set_metadata(row)}


@app.get("/v1/parameter-sets/{parameter_set_id}/revisions")
def parameter_set_revisions_route(parameter_set_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-parameter-set-revision-index/1.0", "parameterSetId": parameter_set_id, "items": list_parameter_set_revisions(db, identity.user_key, parameter_set_id)}


@app.get("/v1/parameter-sets/{parameter_set_id}/revisions/{revision}")
def parameter_set_revision_get_route(parameter_set_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_parameter_set_revision(db, identity.user_key, parameter_set_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace parameter-set revision not found.")
        return {"schema": "sc-workspace-parameter-set-revision/1.0", "item": parameter_set_metadata(row)}


@app.get("/v1/execution-environments")
def execution_environments_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-environment-index/1.0", "items": list_environments(db, identity.user_key, projectId), "revisioned": True}


@app.post("/v1/execution-environments")
def execution_environment_store_route(payload: ExecutionEnvironmentStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_environment(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": environment_metadata(row)}


@app.get("/v1/execution-environments/{environment_id}")
def execution_environment_get_route(environment_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_environment(db, identity.user_key, environment_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution environment not found.")
        return {"schema": "sc-workspace-execution-environment-response/1.0", "item": environment_metadata(row)}


@app.get("/v1/execution-environments/{environment_id}/revisions")
def execution_environment_revisions_route(environment_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-environment-revision-index/1.0", "environmentId": environment_id, "items": list_environment_revisions(db, identity.user_key, environment_id)}


@app.get("/v1/execution-environments/{environment_id}/revisions/{revision}")
def execution_environment_revision_get_route(environment_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_environment_revision(db, identity.user_key, environment_id, revision)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution-environment revision not found.")
        return {"schema": "sc-workspace-execution-environment-revision/1.0", "item": environment_metadata(row)}



@app.get("/v1/runtime-adapters")
def runtime_adapters_index(projectId: str | None = Query(default=None, max_length=160), identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-adapter-index/1.0","items":list_adapters(db,identity.user_key,projectId),"revisioned":True}


@app.post("/v1/runtime-adapters")
def runtime_adapter_store_route(payload: RuntimeAdapterStoreRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row,replayed=store_adapter(db,identity.user_key,payload)
        return {"ok":True,"replayed":replayed,"item":adapter_metadata(row)}


@app.get("/v1/runtime-adapters/{adapter_id}")
def runtime_adapter_get_route(adapter_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter(db,identity.user_key,adapter_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime adapter not found.")
        return {"schema":"sc-workspace-runtime-adapter-response/1.0","item":adapter_metadata(row)}


@app.get("/v1/runtime-adapters/{adapter_id}/revisions")
def runtime_adapter_revisions_route(adapter_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-runtime-adapter-revision-index/1.0","adapterId":adapter_id,"items":list_adapter_revisions(db,identity.user_key,adapter_id)}


@app.get("/v1/runtime-adapters/{adapter_id}/revisions/{revision}")
def runtime_adapter_revision_get_route(adapter_id: str, revision: int, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter_revision(db,identity.user_key,adapter_id,revision)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime-adapter revision not found.")
        return {"schema":"sc-workspace-runtime-adapter-revision/1.0","item":adapter_metadata(row)}


@app.post("/v1/runtime-adapters/{adapter_id}/compatibility")
def runtime_adapter_compatibility_route(adapter_id: str, payload: RuntimeCompatibilityCheckRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_adapter(db,identity.user_key,adapter_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace runtime adapter not found.")
        return check_environment_compatibility(db,identity.user_key,row,payload.environmentRef)


@app.get("/v1/reproduction-plans")
def reproduction_plans_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-reproduction-plan-index/1.0","items":list_reproduction_plans(db,identity.user_key)}


@app.post("/v1/reproduction-plans")
def reproduction_plan_create_route(payload: ReproductionPlanCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":plan_metadata(create_reproduction_plan(db,identity.user_key,payload))}


@app.get("/v1/reproduction-plans/{plan_id}")
def reproduction_plan_get_route(plan_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_reproduction_plan(db,identity.user_key,plan_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reproduction plan not found.")
        return {"schema":"sc-workspace-reproduction-plan-response/1.0","item":plan_metadata(row)}


@app.get("/v1/reproduction-verifications")
def reproduction_verifications_index(identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema":"sc-workspace-reproduction-verification-index/1.0","items":list_verifications(db,identity.user_key)}


@app.post("/v1/reproduction-verifications")
def reproduction_verification_create_route(payload: ReproductionVerificationCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"ok":True,"item":verification_metadata(create_verification(db,identity.user_key,payload))}


@app.get("/v1/reproduction-verifications/{verification_id}")
def reproduction_verification_get_route(verification_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row=get_verification(db,identity.user_key,verification_id)
        if row is None: raise HTTPException(status_code=404,detail="Workspace reproduction verification not found.")
        return {"schema":"sc-workspace-reproduction-verification-response/1.0","item":verification_metadata(row)}


@app.get("/v1/runs")
def execution_runs_index(
    status: str | None = Query(default=None, max_length=32),
    projectId: str | None = Query(default=None, max_length=160),
    limit: int = Query(default=100, ge=1, le=250),
    identity: ServiceIdentity = Depends(require_service_identity),
):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-run-index/1.0", "items": list_execution_runs(db, identity.user_key, status, projectId, limit)}


@app.post("/v1/runs")
def execution_run_create_route(payload: ExecutionRunCreateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = create_execution_run(db, identity.user_key, payload)
        return {"ok": True, "replayed": replayed, "item": run_metadata(row)}


@app.get("/v1/runs/{run_id}")
def execution_run_get_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_execution_run(db, identity.user_key, run_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution run not found.")
        return {"schema": "sc-workspace-execution-run-response/1.0", "item": run_metadata(row)}


@app.post("/v1/runs/{run_id}/state")
def execution_run_update_route(run_id: str, payload: ExecutionRunUpdateRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = update_execution_run(db, identity.user_key, run_id, payload)
        return {"ok": True, "item": run_metadata(row)}


@app.get("/v1/runs/{run_id}/events")
def execution_run_events_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row = get_execution_run(db, identity.user_key, run_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Workspace execution run not found.")
        return {"schema": "sc-workspace-execution-run-event-index/1.0", "runId": run_id, "items": list_run_events(db, identity.user_key, run_id)}


@app.get("/v1/runs/{run_id}/outputs")
def execution_run_outputs_route(run_id: str, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        return {"schema": "sc-workspace-execution-run-output-index/1.0", "runId": run_id, "items": list_run_outputs(db, identity.user_key, run_id)}


@app.post("/v1/runs/{run_id}/outputs")
def execution_run_output_store_route(run_id: str, payload: ExecutionRunOutputRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    with session_scope() as db:
        row, replayed = store_run_output(db, identity.user_key, run_id, payload)
        return {"ok": True, "replayed": replayed, "item": output_metadata(row)}
