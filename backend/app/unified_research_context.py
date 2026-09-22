from __future__ import annotations
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    CrossProductResearchHandoff, ProjectHead, UnifiedResearchContextSnapshot,
)
from .command_query import project_read_model
from .scientific_objects import list_objects
from .study_packages import list_packages
from .visualization_specs import list_specs
from .registry import list_execution_runs
from .platform_core_runtime import project_context as platform_core_project_context, get_mapping as get_platform_core_mapping, PlatformCoreRuntimeError
from .utils import iso, sha256_hex

CONTEXT_SCHEMA = "sc-workspace-unified-research-project-context/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-unified-research-project-context-snapshot/1.0"

class UnifiedResearchContextSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-unified-research-project-context-snapshot-request/1.0"]
    includeCoreViews: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": "sc-workspace-unified-research-project-context-profile/1.0",
        "workspaceVersion": "3.2.0",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "canonicalProjectAuthority": "workspace-postgresql",
        "crossProductContextAuthority": "platform-core-v3-linked-session",
        "referenceFirst": True,
        "objectContentReplicatedToContext": False,
        "specialistObjectAuthorityPreserved": True,
        "contextFingerprinting": True,
        "immutableContextSnapshots": True,
        "includedDomains": [
            "project", "notebooks", "artifacts", "datasets", "models",
            "scientificObjects", "executionRuns", "visualizations",
            "studyPackages", "researchHandoffs", "platformCoreSession",
        ],
        "automaticScientificInference": False,
        "automaticEvidenceRanking": False,
        "automaticDecisionAuthority": False,
    }


def _handoffs(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(CrossProductResearchHandoff)
        .where(CrossProductResearchHandoff.user_key == user_key, CrossProductResearchHandoff.project_id == project_id)
        .order_by(CrossProductResearchHandoff.created_at.desc())
        .limit(limit)
    ).all()
    return [{
        "handoffId": row.handoff_id,
        "sourceProduct": row.source_product,
        "destinationProduct": row.destination_product,
        "intent": row.intent,
        "status": row.status,
        "packageFingerprint": row.package_fingerprint,
        "objects": row.object_refs_json,
        "createdAt": iso(row.created_at),
        "acceptedAt": iso(row.accepted_at) if row.accepted_at else None,
    } for row in rows]


def build_context(db: Session, user_key: str, project_id: str, include_core_views: bool = True) -> dict[str, Any]:
    project_row = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if project_row is None:
        raise KeyError(project_id)
    base = project_read_model(db, user_key, project_id)
    scientific = list_objects(db, user_key, None, project_id, None, 250)
    runs = list_execution_runs(db, user_key, None, project_id, 250)
    visualizations = list_specs(db, user_key, project_id, 250)
    packages = list_packages(db, user_key, project_id, 250)
    handoffs = _handoffs(db, user_key, project_id, 250)
    core: dict[str, Any] | None = None
    core_error = ""
    if include_core_views:
        try:
            core = platform_core_project_context(db, user_key, project_id)
        except PlatformCoreRuntimeError as exc:
            core_error = exc.code
    else:
        mapping = get_platform_core_mapping(db, user_key, project_id)
        if mapping is not None:
            core = {
                "schema": "sc-workspace-platform-core-project-context/1.0",
                "item": {
                    "projectId": mapping.project_id,
                    "coreSessionId": mapping.core_session_id,
                    "coreSessionKey": mapping.core_session_key,
                    "coreContract": mapping.core_contract,
                    "coreRelease": mapping.core_release,
                    "status": mapping.status,
                },
                "coreSummary": None,
            }
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in scientific:
        grouped.setdefault(str(item.get("kind") or "unknown"), []).append(item)
    counts = {
        "notebooks": len(base.get("notebooks") or []),
        "artifacts": len(base.get("artifacts") or []),
        "datasets": len(base.get("datasets") or []),
        "models": len(base.get("models") or []),
        "scientificObjects": len(scientific),
        "executionRuns": len(runs),
        "visualizations": len(visualizations),
        "studyPackages": len(packages),
        "researchHandoffs": len(handoffs),
        "platformCoreSession": 1 if core else 0,
    }
    item = {
        "schema": CONTEXT_SCHEMA,
        "projectId": project_id,
        "projectRevision": project_row.revision,
        "projectFingerprint": project_row.project_fingerprint,
        "backendAuthoritative": True,
        "referenceFirst": True,
        "specialistObjectAuthorityPreserved": True,
        "counts": counts,
        "project": base.get("project"),
        "notebooks": base.get("notebooks") or [],
        "scientificObjects": scientific,
        "scientificObjectsByKind": grouped,
        "executionRuns": runs,
        "visualizations": visualizations,
        "studyPackages": packages,
        "researchHandoffs": handoffs,
        "platformCore": core,
        "platformCoreError": core_error,
    }
    fingerprint_payload = dict(item)
    fingerprint_payload.pop("platformCoreError", None)
    item["contextFingerprint"] = sha256_hex(fingerprint_payload)
    return item


def create_snapshot(db: Session, user_key: str, project_id: str, request: UnifiedResearchContextSnapshotRequest) -> dict[str, Any]:
    context = build_context(db, user_key, project_id, request.includeCoreViews)
    core_session = ((context.get("platformCore") or {}).get("item") or {}).get("coreSessionId") or ""
    row = UnifiedResearchContextSnapshot(
        user_key=user_key,
        snapshot_id="research-context-" + uuid4().hex[:24],
        project_id=project_id,
        project_revision=int(context.get("projectRevision") or 0),
        project_fingerprint=str(context.get("projectFingerprint") or ""),
        context_fingerprint=str(context["contextFingerprint"]),
        core_session_id=str(core_session),
        component_counts_json=context.get("counts") or {},
        context_json=context,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return snapshot_metadata(row)


def snapshot_metadata(row: UnifiedResearchContextSnapshot) -> dict[str, Any]:
    return {
        "schema": SNAPSHOT_SCHEMA,
        "snapshotId": row.snapshot_id,
        "projectId": row.project_id,
        "projectRevision": row.project_revision,
        "projectFingerprint": row.project_fingerprint,
        "contextFingerprint": row.context_fingerprint,
        "coreSessionId": row.core_session_id,
        "componentCounts": row.component_counts_json,
        "createdAt": iso(row.created_at),
    }


def list_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(UnifiedResearchContextSnapshot)
        .where(UnifiedResearchContextSnapshot.user_key == user_key, UnifiedResearchContextSnapshot.project_id == project_id)
        .order_by(UnifiedResearchContextSnapshot.created_at.desc())
        .limit(limit)
    ).all()
    return [snapshot_metadata(row) for row in rows]
