from __future__ import annotations
from typing import Any
from sqlalchemy.orm import Session

from .repository import list_projects, list_notebooks, get_project
from .local_first_sync import profile as local_first_sync_profile

SCHEMA="sc-workspace-unified-user-workspace/1.0"
BOOTSTRAP_SCHEMA="sc-workspace-unified-user-workspace-bootstrap/1.0"

def profile() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "3.72.0",
        "serverAuthoritativeWhenAuthenticated": True,
        "anonymousLocalFirstSupported": True,
        "projectStore": "workspace-backend-postgresql",
        "projectRevisionHistory": True,
        "crossBrowserContinuity": True,
        "crossDeviceContinuity": True,
        "localStatePreserved": True,
        "automaticDestructiveMerge": False,
        "automaticConflictOverwrite": False,
        "explicitReconciliation": True,
        "sessionRequiredForServerWorkspace": True,
        "wordpressRequired": False,
        "databaseMigrationRequired": False,
        "projectSchemaMigrationRequired": False,
    }

def bootstrap(db: Session, user_key: str) -> dict[str, Any]:
    projects=list_projects(db,user_key)
    notebooks=list_notebooks(db,user_key)
    return {
        "schema": BOOTSTRAP_SCHEMA,
        "version": "3.72.0",
        "userKey": user_key,
        "projectCount": len(projects),
        "notebookCount": len(notebooks),
        "projects": projects,
        "notebooks": notebooks,
        "sync": local_first_sync_profile(),
        "serverAuthoritativeWhenAuthenticated": True,
        "hydrateMode": "metadata-first-explicit-package-fetch",
        "automaticDestructiveMerge": False,
        "automaticConflictOverwrite": False,
    }

def project_package(db: Session, user_key: str, project_id: str) -> dict[str, Any] | None:
    row=get_project(db,user_key,project_id)
    if row is None: return None
    return {
        "schema":"sc-workspace-unified-user-workspace-project/1.0",
        "version":"3.72.0",
        "metadata":{
            "projectId":row.project_id,
            "title":row.title,
            "revision":row.revision,
            "fingerprint":row.fingerprint,
            "projectFingerprint":row.project_fingerprint,
            "storageMode":row.storage_mode,
            "clientUpdatedAt":row.client_updated_at,
        },
        "package":row.package,
        "serverAuthoritative":True,
    }
