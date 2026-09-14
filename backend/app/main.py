from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
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
from .schemas import ArtifactStoreRequest, LegacyMigrationRequest, NotebookStoreRequest, ProjectStoreRequest, RecoverySnapshotRequest
from .security import ServiceIdentity, require_service_identity
from .migration import apply_migration, list_receipts, migration_plan
from .object_store import artifact_metadata, delete_artifact, get_artifact, list_artifacts, read_artifact_content, store_artifact, verify_artifact_storage
from .recovery import create_snapshot, get_snapshot, list_snapshots, snapshot_metadata
from .utils import iso


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
        "backgroundJobs": False,
        "computeOrchestration": False,
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
