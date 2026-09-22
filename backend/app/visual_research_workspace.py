from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ProjectHead, ResearchSessionObjectBinding, VisualResearchWorkspaceSnapshot, VisualizationSpecHead
from .platform_core_runtime import PlatformCoreRuntimeError, get_mapping
from .research_session_bindings import ResearchSessionBindingRequest, bind_reference, list_bindings
from .utils import iso, sha256_hex

VISUAL_RESEARCH_WORKSPACE_SCHEMA = "sc-workspace-platform-core-visual-analysis-research-object-workspace/1.0"
VISUAL_RESEARCH_GRAPH_SCHEMA = "sc-workspace-visual-research-object-graph/1.0"
VISUAL_RESEARCH_BIND_REQUEST_SCHEMA = "sc-workspace-visual-research-binding-request/1.0"
VISUAL_RESEARCH_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-visual-research-workspace-snapshot-request/1.0"
VISUAL_RESEARCH_SNAPSHOT_SCHEMA = "sc-workspace-visual-research-workspace-snapshot/1.0"


class VisualResearchBindingRequest(BaseModel):
    schema: Literal["sc-workspace-visual-research-binding-request/1.0"]
    includeSources: bool = True
    ensureSession: bool = True
    role: str = Field(default="analysis", min_length=1, max_length=120)
    sourceRole: str = Field(default="evidence", min_length=1, max_length=120)
    visibility: Literal["internal", "public"] = "internal"
    stopOnError: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisualResearchWorkspaceSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-visual-research-workspace-snapshot-request/1.0"]
    visualizationId: str = Field(default="", max_length=160)


def profile() -> dict[str, Any]:
    return {
        "schema": VISUAL_RESEARCH_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.6.0",
        "release": "Platform Core Visual Analysis & Research Object Workspace",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "referenceFirst": True,
        "workspaceVisualizationAuthority": "workspace-postgresql",
        "platformCoreSessionRegistryAuthority": "platform-core-v3",
        "specialistObjectAuthorityPreserved": True,
        "objectContentReplicatedToCore": False,
        "sceneGraphProjection": True,
        "researchObjectBindingProjection": True,
        "sourceProvenancePinning": True,
        "linkedViewGraph": True,
        "durableVisualWorkspaceSnapshots": True,
        "explicitCoreBinding": True,
        "automaticMassBinding": False,
        "automaticScientificInterpretation": False,
        "automaticEvidenceRanking": False,
        "automaticDecisionAuthority": False,
    }


def _visual_rows(db: Session, user_key: str, project_id: str, visualization_id: str = "") -> list[VisualizationSpecHead]:
    query = select(VisualizationSpecHead).where(
        VisualizationSpecHead.user_key == user_key,
        VisualizationSpecHead.project_id == project_id,
    )
    if visualization_id:
        query = query.where(VisualizationSpecHead.visualization_id == visualization_id)
    return list(db.scalars(query.order_by(VisualizationSpecHead.updated_at.desc())).all())


def _binding_index(db: Session, user_key: str, project_id: str) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    bindings = list_bindings(db, user_key, project_id, None, 500)
    return bindings, {str(item.get("workspaceRef") or ""): item for item in bindings}


def _source_ref(source: dict[str, Any]) -> str:
    kind = str(source.get("kind") or "")
    ref = str(source.get("ref") or "")
    sid = str(source.get("id") or "")
    if kind == "inline":
        fp = str(source.get("sourceFingerprint") or "")
        return f"workspace:inline:{sid}:{fp}"[:1000]
    return f"workspace:{kind}:{ref}"[:1000]


def _node(node_id: str, kind: str, **props: Any) -> dict[str, Any]:
    return {"id": node_id, "kind": kind, **props}


def _edge(source: str, target: str, relation: str, **props: Any) -> dict[str, Any]:
    return {"source": source, "target": target, "relation": relation, **props}


def build_project_workspace(db: Session, user_key: str, project_id: str, visualization_id: str = "") -> dict[str, Any]:
    project = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if project is None:
        raise KeyError(project_id)
    rows = _visual_rows(db, user_key, project_id, visualization_id)
    if visualization_id and not rows:
        raise LookupError(visualization_id)
    bindings, binding_by_ref = _binding_index(db, user_key, project_id)
    mapping = get_mapping(db, user_key, project_id)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    project_node = f"workspace:project:{project_id}"
    nodes[project_node] = _node(project_node, "project", title=project.title, revision=project.revision, fingerprint=project.project_fingerprint)
    core_node = ""
    if mapping is not None:
        core_node = f"platform-core:research-session:{mapping.core_session_id}"
        nodes[core_node] = _node(core_node, "platform-core-research-session", coreSessionId=mapping.core_session_id, status=mapping.status, coreContract=mapping.core_contract)
        edges.append(_edge(project_node, core_node, "registered-in-core"))

    visualization_items: list[dict[str, Any]] = []
    source_refs: set[str] = set()
    linked_view_edges = 0
    for row in rows:
        spec = row.spec_json or {}
        viz_node = f"workspace:visualization-spec:{row.visualization_id}"
        nodes[viz_node] = _node(
            viz_node, "visualization-spec", visualizationId=row.visualization_id, title=row.title,
            revision=row.revision, specFingerprint=row.spec_fingerprint, sceneKind=row.scene_kind,
        )
        edges.append(_edge(project_node, viz_node, "contains-visualization"))
        binding = binding_by_ref.get(viz_node)
        if binding and core_node:
            edges.append(_edge(viz_node, core_node, "bound-to-core", coreBindingId=binding.get("coreBindingId", ""), role=binding.get("role", "")))

        sources = list(spec.get("sources") or [])
        source_by_id: dict[str, str] = {}
        for src in sources:
            if not isinstance(src, dict):
                continue
            sid = str(src.get("id") or "")
            sref = _source_ref(src)
            source_refs.add(sref)
            source_by_id[sid] = sref
            nodes.setdefault(sref, _node(
                sref, "research-source", sourceId=sid, sourceKind=str(src.get("kind") or ""),
                sourceRef=str(src.get("ref") or ""), sourceFingerprint=str(src.get("sourceFingerprint") or ""),
                projectId=str(src.get("projectId") or ""), revision=int(src.get("revision") or 0),
            ))
            edges.append(_edge(sref, viz_node, "source-for-visualization", sourceId=sid))

        view_nodes: dict[str, str] = {}
        for view in ((spec.get("scene") or {}).get("views") or []):
            if not isinstance(view, dict):
                continue
            view_id = str(view.get("id") or "")
            view_node = f"{viz_node}:view:{view_id}"
            view_nodes[view_id] = view_node
            nodes[view_node] = _node(view_node, "visual-view", viewId=view_id, viewType=str(view.get("type") or ""), title=str(view.get("title") or ""))
            edges.append(_edge(viz_node, view_node, "contains-view"))
            source_id = str(view.get("source") or "")
            if source_id and source_id in source_by_id:
                edges.append(_edge(source_by_id[source_id], view_node, "feeds-view", sourceId=source_id))

        for link in spec.get("links") or []:
            if not isinstance(link, dict):
                continue
            source_view = view_nodes.get(str(link.get("sourceViewId") or ""))
            target_view = view_nodes.get(str(link.get("targetViewId") or ""))
            if source_view and target_view:
                edges.append(_edge(source_view, target_view, f"linked-{str(link.get('mode') or 'filter')}", field=str(link.get("field") or "")))
                linked_view_edges += 1

        visualization_items.append({
            "visualizationId": row.visualization_id,
            "title": row.title,
            "revision": row.revision,
            "specFingerprint": row.spec_fingerprint,
            "sceneKind": row.scene_kind,
            "viewCount": row.view_count,
            "sourceCount": row.source_count,
            "sourceRefs": [_source_ref(src) for src in sources if isinstance(src, dict)],
            "coreBinding": binding,
            "createdAt": iso(row.created_at),
            "updatedAt": iso(row.updated_at),
        })

    graph = {
        "schema": VISUAL_RESEARCH_GRAPH_SCHEMA,
        "nodes": sorted(nodes.values(), key=lambda x: x["id"]),
        "edges": sorted(edges, key=lambda x: (x["source"], x["target"], x["relation"])),
    }
    graph["graphFingerprint"] = sha256_hex(graph)
    selected_bindings = [b for b in bindings if str(b.get("bindingType") or "") in ("visualization", "scientific-object", "execution")]
    item = {
        "schema": VISUAL_RESEARCH_WORKSPACE_SCHEMA,
        "projectId": project_id,
        "visualizationId": visualization_id,
        "projectRevision": project.revision,
        "projectFingerprint": project.project_fingerprint,
        "backendAuthoritative": True,
        "referenceFirst": True,
        "specialistObjectAuthorityPreserved": True,
        "platformCore": {
            "sessionBound": mapping is not None,
            "coreSessionId": mapping.core_session_id if mapping else "",
            "coreContract": mapping.core_contract if mapping else "",
            "objectContentReplicated": False,
        },
        "visualizations": visualization_items,
        "bindings": selected_bindings,
        "sourceRefs": sorted(source_refs),
        "counts": {
            "visualizations": len(visualization_items),
            "bindings": len(selected_bindings),
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "linkedViews": linked_view_edges,
            "sources": len(source_refs),
        },
        "graph": graph,
        "graphFingerprint": graph["graphFingerprint"],
    }
    item["workspaceFingerprint"] = sha256_hex(item)
    return item


def _source_binding_request(source: dict[str, Any], request: VisualResearchBindingRequest) -> ResearchSessionBindingRequest | None:
    kind = str(source.get("kind") or "")
    ref = str(source.get("ref") or "")
    if not ref or kind == "inline" or kind == "receipt":
        return None
    if kind == "execution-run":
        return ResearchSessionBindingRequest(
            schema="sc-workspace-research-session-binding-request/1.0", bindingType="execution", objectId=ref,
            role=request.sourceRole, visibility=request.visibility, ensureSession=request.ensureSession,
            metadata={"visualResearchWorkspace": "3.5.0", "sourceOfVisualization": True, **request.metadata},
        )
    if kind in ("artifact", "dataset"):
        return ResearchSessionBindingRequest(
            schema="sc-workspace-research-session-binding-request/1.0", bindingType="scientific-object", objectId=ref,
            objectKind=kind, role=request.sourceRole, visibility=request.visibility, ensureSession=request.ensureSession,
            metadata={"visualResearchWorkspace": "3.5.0", "sourceOfVisualization": True, **request.metadata},
        )
    return None


def bind_visualization(db: Session, user_key: str, project_id: str, visualization_id: str, request: VisualResearchBindingRequest) -> dict[str, Any]:
    rows = _visual_rows(db, user_key, project_id, visualization_id)
    if not rows:
        raise LookupError(visualization_id)
    row = rows[0]
    spec = row.spec_json or {}
    sources = [s for s in (spec.get("sources") or []) if isinstance(s, dict)]
    source_refs = [_source_ref(s) for s in sources]
    viz_request = ResearchSessionBindingRequest(
        schema="sc-workspace-research-session-binding-request/1.0", bindingType="visualization", objectId=visualization_id,
        role=request.role, visibility=request.visibility, ensureSession=request.ensureSession,
        metadata={
            "visualResearchWorkspace": "3.5.0", "specFingerprint": row.spec_fingerprint,
            "sourceRefs": source_refs, "viewCount": row.view_count, "sourceCount": row.source_count,
            **request.metadata,
        },
    )
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    results.append(bind_reference(db, user_key, project_id, viz_request))
    if request.includeSources:
        for source in sources:
            source_request = _source_binding_request(source, request)
            if source_request is None:
                continue
            try:
                results.append(bind_reference(db, user_key, project_id, source_request))
            except PlatformCoreRuntimeError as exc:
                failures.append({"source": _source_ref(source), "code": exc.code, "message": str(exc)})
                if request.stopOnError:
                    raise
    workspace = build_project_workspace(db, user_key, project_id, visualization_id)
    return {
        "ok": len(failures) == 0,
        "schema": "sc-workspace-visual-research-binding-result/1.0",
        "projectId": project_id,
        "visualizationId": visualization_id,
        "requestedSources": len(sources) if request.includeSources else 0,
        "succeeded": len(results),
        "failed": len(failures),
        "results": results,
        "failures": failures,
        "workspace": workspace,
    }


def create_snapshot(db: Session, user_key: str, project_id: str, request: VisualResearchWorkspaceSnapshotRequest) -> dict[str, Any]:
    context = build_project_workspace(db, user_key, project_id, request.visualizationId)
    counts = context.get("counts") or {}
    row = VisualResearchWorkspaceSnapshot(
        user_key=user_key,
        snapshot_id="visual-research-" + uuid4().hex[:24],
        project_id=project_id,
        visualization_id=request.visualizationId,
        graph_fingerprint=str(context.get("graphFingerprint") or ""),
        visualization_count=int(counts.get("visualizations") or 0),
        binding_count=int(counts.get("bindings") or 0),
        node_count=int(counts.get("nodes") or 0),
        edge_count=int(counts.get("edges") or 0),
        context_json=context,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return snapshot_metadata(row)


def snapshot_metadata(row: VisualResearchWorkspaceSnapshot) -> dict[str, Any]:
    return {
        "schema": VISUAL_RESEARCH_SNAPSHOT_SCHEMA,
        "snapshotId": row.snapshot_id,
        "projectId": row.project_id,
        "visualizationId": row.visualization_id,
        "graphFingerprint": row.graph_fingerprint,
        "visualizationCount": row.visualization_count,
        "bindingCount": row.binding_count,
        "nodeCount": row.node_count,
        "edgeCount": row.edge_count,
        "createdAt": iso(row.created_at),
    }


def list_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(VisualResearchWorkspaceSnapshot)
        .where(VisualResearchWorkspaceSnapshot.user_key == user_key, VisualResearchWorkspaceSnapshot.project_id == project_id)
        .order_by(VisualResearchWorkspaceSnapshot.created_at.desc())
        .limit(limit)
    ).all()
    return [snapshot_metadata(row) for row in rows]
