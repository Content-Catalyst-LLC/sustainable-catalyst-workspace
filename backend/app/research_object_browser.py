from typing import Any
from sqlalchemy.orm import Session
from .repository import list_projects, list_notebooks
from .scientific_objects import OBJECT_KINDS, list_objects as list_scientific_objects

SCHEMA = "sc-workspace-unified-research-object-browser/1.0"
KINDS = ("project", "notebook", *OBJECT_KINDS)

def profile() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": "3.74.0",
        "mode": "backend-authoritative-read-model",
        "unifiedDiscovery": True,
        "projectScopedFiltering": True,
        "textSearch": True,
        "kindFiltering": True,
        "facets": True,
        "typeAwareCards": True,
        "deepLinkSafe": True,
        "genericMutation": False,
        "databaseMigrationRequired": False,
        "supportedKinds": list(KINDS),
        "authorities": {
            "project": "workspace-project-api",
            "notebook": "workspace-notebook-api",
            "scientificObjects": "scientific-object-api",
        },
    }

def _project(row: dict[str, Any]) -> dict[str, Any]:
    oid = str(row.get("projectId") or row.get("id") or "")
    return {
        "schema": "sc-workspace-unified-research-object/1.0",
        "kind": "project", "objectId": oid, "projectId": oid,
        "name": str(row.get("title") or row.get("name") or oid),
        "status": str(row.get("status") or ""),
        "createdAt": row.get("createdAt"),
        "updatedAt": row.get("updatedAt") or row.get("clientUpdatedAt"),
        "summary": {"description": row.get("description"), "archivedAt": row.get("archivedAt")},
        "authority": "workspace-project-api",
    }

def _notebook(row: dict[str, Any]) -> dict[str, Any]:
    oid = str(row.get("notebookId") or row.get("id") or "")
    return {
        "schema": "sc-workspace-unified-research-object/1.0",
        "kind": "notebook", "objectId": oid,
        "projectId": str(row.get("projectId") or ""),
        "name": str(row.get("title") or row.get("name") or oid),
        "status": str(row.get("status") or ""),
        "createdAt": row.get("createdAt"), "updatedAt": row.get("updatedAt"),
        "summary": {"language": row.get("language"), "cellCount": row.get("cellCount")},
        "authority": "workspace-notebook-api",
    }

def _matches(item: dict[str, Any], query: str) -> bool:
    needle = (query or "").strip().casefold()
    if not needle:
        return True
    haystack = " ".join(str(item.get(key) or "") for key in ("kind", "objectId", "name", "projectId", "status"))
    haystack += " " + str(item.get("summary") or "")
    return needle in haystack.casefold()

def browse(db: Session, user_key: str, kind: str | None = None, project_id: str | None = None, q: str | None = None, limit: int = 100) -> dict[str, Any]:
    if kind and kind not in KINDS:
        raise ValueError(f"unsupported research object kind: {kind}")
    items: list[dict[str, Any]] = []
    if kind in (None, "project"):
        items.extend(_project(row) for row in list_projects(db, user_key))
    if kind in (None, "notebook"):
        items.extend(_notebook(row) for row in list_notebooks(db, user_key))
    if kind not in ("project", "notebook"):
        scientific_kind = kind if kind in OBJECT_KINDS else None
        for row in list_scientific_objects(db, user_key, scientific_kind, project_id, q, max(1, min(limit, 500))):
            item = dict(row)
            item["schema"] = "sc-workspace-unified-research-object/1.0"
            item["authority"] = "scientific-object-api"
            items.append(item)
    if project_id:
        items = [item for item in items if str(item.get("projectId") or "") == str(project_id) or (item.get("kind") == "project" and str(item.get("objectId") or "") == str(project_id))]
    if q:
        items = [item for item in items if _matches(item, q)]
    items.sort(key=lambda item: str(item.get("updatedAt") or item.get("createdAt") or ""), reverse=True)
    items = items[:max(1, min(limit, 500))]
    facets: dict[str, int] = {}
    for item in items:
        facets[item["kind"]] = facets.get(item["kind"], 0) + 1
    return {
        "schema": "sc-workspace-unified-research-object-index/1.0",
        "version": "3.74.0", "backendAuthoritative": True,
        "items": items, "count": len(items), "facets": {"kind": facets},
        "filters": {"kind": kind or "all", "projectId": project_id or "", "q": q or ""},
    }
