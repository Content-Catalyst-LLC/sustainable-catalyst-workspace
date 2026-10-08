from __future__ import annotations
from urllib.parse import urlparse

VERSION = "3.82.3"
PROFILE_SCHEMA = "sc-shared-research-surface-profile/1.0"
CONTEXT_SCHEMA = "sc-shared-research-surface-context/1.0"

def _clean(value: str | None, limit: int = 240) -> str:
    return "".join(ch for ch in str(value or "") if ord(ch) >= 32).strip()[:limit]

def _safe_return_url(value: str | None) -> str:
    raw = _clean(value, 1000)
    if not raw:
        return ""
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        return ""
    return raw

def profile() -> dict:
    return {
        "schema": PROFILE_SCHEMA,
        "version": VERSION,
        "release": "Shared WordPress + Standalone Research Surface",
        "contextSchema": CONTEXT_SCHEMA,
        "publicGraphEndpoint": "/v1/shared-research-graph/demo",
        "surfaceProfileEndpoint": "/v1/shared-research-surface/profile",
        "contextEndpoint": "/v1/shared-research-surface/context",
        "standaloneUrl": "https://workspace.sustainablecatalyst.com",
        "wordpressRole": "public-read-only-presentation-and-entry",
        "standaloneRole": "private-full-project-environment",
        "sameRenderer": True,
        "sameTerrainRuntime": True,
        "contextPreservingHandoff": True,
        "publicSurfacePrivateDataAccess": False,
        "wordpressCanonicalAuthority": False,
        "workspaceProjectAuthorityPreserved": True,
        "databaseMigrationRequired": False,
        "automaticImport": False,
        "automaticProjectMutation": False,
    }

def context(*, source: str = "public", object_id: str = "", kind: str = "", view: str = "terrain", lens: str = "all", return_url: str = "") -> dict:
    return {
        "schema": CONTEXT_SCHEMA,
        "version": VERSION,
        "source": _clean(source) or "public",
        "objectId": _clean(object_id),
        "kind": _clean(kind),
        "view": _clean(view) or "terrain",
        "lens": _clean(lens) or "all",
        "returnUrl": _safe_return_url(return_url),
        "authoritative": False,
        "mutationRequested": False,
    }
