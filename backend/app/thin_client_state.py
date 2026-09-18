from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from .command_query import workspace_overview, project_read_model
from .utils import sha256_hex

PROFILE_SCHEMA = "sc-workspace-thin-client-state/1.0"
BOOTSTRAP_SCHEMA = "sc-workspace-thin-client-bootstrap/1.0"

TRANSIENT_STATE_KEYS = (
    "activeRoute",
    "activeProjectId",
    "activeNotebookId",
    "activeObjectId",
    "selection",
    "openPanels",
    "draftBuffers",
    "filters",
    "sort",
    "viewport",
    "density",
    "optimisticRequests",
    "offlineQueueMetadata",
)

CANONICAL_STATE_KINDS = (
    "projects",
    "notebooks",
    "artifacts",
    "datasets",
    "models",
    "parameterSets",
    "executionRuns",
    "jobs",
    "receipts",
    "studyPackages",
    "visualizationSpecifications",
)


def profile() -> dict[str, Any]:
    return {
        "schema": PROFILE_SCHEMA,
        "mode": "backend-authoritative-thin-client",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "canonicalStore": "postgresql",
        "canonicalCache": "memory-only-rehydratable",
        "canonicalCachePersistent": False,
        "persistentBrowserState": "transient-only",
        "transientStorage": "browser-local",
        "transientStateKeys": list(TRANSIENT_STATE_KEYS),
        "canonicalStateKinds": list(CANONICAL_STATE_KINDS),
        "canonicalMutations": "command-api-only",
        "canonicalReads": "server-read-models-only",
        "offlineCacheAuthoritative": False,
        "offlineQueueCarriesCanonicalPayloads": False,
        "guestLocalFirstCompatibility": True,
        "signedInBackendAuthority": True,
        "serverProjectionFingerprint": "SHA-256",
        "arbitraryCodeExecution": False,
    }


def bootstrap(db: Session, user_key: str, project_id: str | None = None) -> dict[str, Any]:
    overview = workspace_overview(db, user_key)
    project = project_read_model(db, user_key, project_id) if project_id else None
    revision_vector = {
        str(item.get("projectId")): int(item.get("revision") or 0)
        for item in overview.get("projects", [])
        if item.get("projectId")
    }
    canonical = {
        "overview": overview,
        "project": project,
        "revisionVector": revision_vector,
    }
    return {
        "schema": BOOTSTRAP_SCHEMA,
        "generatedServerSide": True,
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "canonicalStore": "postgresql",
        "canonical": canonical,
        "projectionFingerprint": sha256_hex(canonical),
        "clientPolicy": {
            "persistCanonicalCache": False,
            "persistTransientStateOnly": True,
            "mutateThroughCommandsOnly": True,
            "rehydrateCanonicalState": True,
        },
    }
