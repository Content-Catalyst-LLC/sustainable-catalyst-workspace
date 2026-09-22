from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    InvestigationEvidenceLink,
    InvestigationStatementHead,
    InvestigationStatementRelation,
    InvestigationStatementRevision,
    InvestigativeResearchWorkspaceSnapshot,
    ProjectHead,
)
from .scientific_objects import OBJECT_KINDS, get_object
from .visual_research_workspace import build_project_workspace as build_visual_research_workspace
from .utils import iso, sha256_hex

INVESTIGATIVE_RESEARCH_WORKSPACE_SCHEMA = "sc-workspace-claims-evidence-investigative-research-workspace/1.0"
INVESTIGATIVE_GRAPH_SCHEMA = "sc-workspace-investigative-research-graph/1.0"
STATEMENT_REQUEST_SCHEMA = "sc-workspace-investigation-statement-request/1.0"
EVIDENCE_LINK_REQUEST_SCHEMA = "sc-workspace-investigation-evidence-link-request/1.0"
STATEMENT_RELATION_REQUEST_SCHEMA = "sc-workspace-investigation-statement-relation-request/1.0"
SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-investigative-research-snapshot-request/1.0"
SNAPSHOT_SCHEMA = "sc-workspace-investigative-research-snapshot/1.0"

STATEMENT_TYPES = ("claim", "finding", "hypothesis", "question")
REVIEW_STATES = ("open", "under-review", "documented", "contested", "unresolved", "closed")
EVIDENCE_RELATIONS = ("supports", "contradicts", "contextualizes", "challenges", "derived-from", "corroborates")
STATEMENT_RELATIONS = ("contradicts", "competes-with", "supports", "depends-on", "refines", "duplicates", "related")


class InvestigationStatementRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-statement-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    statementId: str = Field(default="", max_length=160)
    statementType: Literal["claim", "finding", "hypothesis", "question"] = "claim"
    title: str = Field(default="", max_length=500)
    text: str = Field(min_length=1, max_length=20000)
    reviewState: Literal["open", "under-review", "documented", "contested", "unresolved", "closed"] = "open"
    tags: list[str] = Field(default_factory=list, max_length=100)
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEvidenceLinkRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-evidence-link-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    statementId: str = Field(min_length=1, max_length=160)
    evidenceRef: str = Field(min_length=1, max_length=1200)
    evidenceKind: str = Field(default="external-reference", max_length=120)
    relation: Literal["supports", "contradicts", "contextualizes", "challenges", "derived-from", "corroborates"]
    sourceFingerprint: str = Field(default="", max_length=128)
    locator: str = Field(default="", max_length=1000)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_external_reference_fingerprint(self):
        if not self.evidenceRef.startswith("workspace:") and not self.sourceFingerprint:
            raise ValueError("non-Workspace evidence references require sourceFingerprint")
        return self


class InvestigationStatementRelationRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-statement-relation-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    fromStatementId: str = Field(min_length=1, max_length=160)
    toStatementId: str = Field(min_length=1, max_length=160)
    relation: Literal["contradicts", "competes-with", "supports", "depends-on", "refines", "duplicates", "related"]
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def no_self_relation(self):
        if self.fromStatementId == self.toStatementId:
            raise ValueError("statement relation endpoints must differ")
        return self


class InvestigativeResearchSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-investigative-research-snapshot-request/1.0"]
    includeVisualGraph: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": INVESTIGATIVE_RESEARCH_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.7.0",
        "release": "Claims, Evidence & Investigative Research Workspace",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "referenceFirst": True,
        "statementRevisionHistory": True,
        "immutableEvidenceLinks": True,
        "immutableStatementRelations": True,
        "sourceFingerprintPinning": True,
        "visualResearchGraphOverlay": True,
        "platformCoreSessionProjection": True,
        "specialistObjectAuthorityPreserved": True,
        "objectContentReplicatedToCore": False,
        "explicitHumanEvidenceRelationships": True,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticClaimScoring": False,
        "automaticDecisionAuthority": False,
        "supportedStatementTypes": list(STATEMENT_TYPES),
        "supportedReviewStates": list(REVIEW_STATES),
        "supportedEvidenceRelations": list(EVIDENCE_RELATIONS),
        "supportedStatementRelations": list(STATEMENT_RELATIONS),
    }


def _project(db: Session, user_key: str, project_id: str) -> ProjectHead:
    row = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if row is None:
        raise KeyError(project_id)
    return row


def _statement(db: Session, user_key: str, statement_id: str) -> InvestigationStatementHead | None:
    return db.get(InvestigationStatementHead, {"user_key": user_key, "statement_id": statement_id})


def statement_metadata(row: InvestigationStatementHead) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-statement/1.0",
        "statementId": row.statement_id,
        "projectId": row.project_id,
        "statementType": row.statement_type,
        "title": row.title,
        "text": row.statement_text,
        "reviewState": row.review_state,
        "revision": row.revision,
        "statementFingerprint": row.statement_fingerprint,
        "tags": row.tags_json or [],
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _statement_fingerprint(payload: InvestigationStatementRequest, statement_id: str, revision: int) -> str:
    return sha256_hex({
        "statementId": statement_id,
        "projectId": payload.projectId,
        "statementType": payload.statementType,
        "title": payload.title,
        "text": payload.text,
        "reviewState": payload.reviewState,
        "revision": revision,
        "tags": sorted(set(payload.tags)),
        "metadata": payload.metadata,
    })


def store_statement(db: Session, user_key: str, payload: InvestigationStatementRequest) -> tuple[dict[str, Any], bool]:
    _project(db, user_key, payload.projectId)
    statement_id = payload.statementId or ("statement-" + uuid4().hex[:24])
    row = _statement(db, user_key, statement_id)
    created = row is None
    if row is not None:
        if row.project_id != payload.projectId:
            raise ValueError("statement belongs to a different project")
        if payload.expectedRevision is not None and payload.expectedRevision != row.revision:
            raise RuntimeError("statement revision conflict")
        revision = row.revision + 1
    else:
        revision = 1
        row = InvestigationStatementHead(user_key=user_key, statement_id=statement_id, project_id=payload.projectId)
        db.add(row)
    fp = _statement_fingerprint(payload, statement_id, revision)
    row.statement_type = payload.statementType
    row.title = payload.title
    row.statement_text = payload.text
    row.review_state = payload.reviewState
    row.revision = revision
    row.statement_fingerprint = fp
    row.tags_json = sorted(set(payload.tags))
    row.metadata_json = payload.metadata
    revision_row = InvestigationStatementRevision(
        user_key=user_key,
        statement_id=statement_id,
        revision=revision,
        project_id=payload.projectId,
        statement_type=payload.statementType,
        title=payload.title,
        statement_text=payload.text,
        review_state=payload.reviewState,
        statement_fingerprint=fp,
        tags_json=sorted(set(payload.tags)),
        metadata_json=payload.metadata,
    )
    db.add(revision_row)
    db.commit()
    db.refresh(row)
    return statement_metadata(row), created


def list_statements(db: Session, user_key: str, project_id: str | None = None, statement_type: str | None = None, limit: int = 250) -> list[dict[str, Any]]:
    query = select(InvestigationStatementHead).where(InvestigationStatementHead.user_key == user_key)
    if project_id:
        query = query.where(InvestigationStatementHead.project_id == project_id)
    if statement_type:
        query = query.where(InvestigationStatementHead.statement_type == statement_type)
    rows = db.scalars(query.order_by(InvestigationStatementHead.updated_at.desc()).limit(limit)).all()
    return [statement_metadata(row) for row in rows]


def get_statement(db: Session, user_key: str, statement_id: str) -> dict[str, Any] | None:
    row = _statement(db, user_key, statement_id)
    return statement_metadata(row) if row else None


def list_statement_revisions(db: Session, user_key: str, statement_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationStatementRevision)
        .where(InvestigationStatementRevision.user_key == user_key, InvestigationStatementRevision.statement_id == statement_id)
        .order_by(InvestigationStatementRevision.revision.desc()).limit(limit)
    ).all()
    return [{
        "schema": "sc-workspace-investigation-statement-revision/1.0",
        "statementId": row.statement_id,
        "projectId": row.project_id,
        "revision": row.revision,
        "statementType": row.statement_type,
        "title": row.title,
        "text": row.statement_text,
        "reviewState": row.review_state,
        "statementFingerprint": row.statement_fingerprint,
        "tags": row.tags_json or [],
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    } for row in rows]


def _validate_workspace_evidence(db: Session, user_key: str, project_id: str, evidence_ref: str) -> tuple[str, str]:
    if not evidence_ref.startswith("workspace:"):
        return "", ""
    parts = evidence_ref.split(":", 2)
    if len(parts) != 3:
        return "", ""
    kind, object_id = parts[1], parts[2]
    if kind not in OBJECT_KINDS:
        return "", ""
    item = get_object(db, user_key, kind, object_id)
    if item is None:
        raise LookupError(evidence_ref)
    object_project = str(item.get("projectId") or "")
    if object_project not in ("", project_id):
        raise ValueError("evidence reference belongs to a different project")
    return str(item.get("objectFingerprint") or item.get("fingerprint") or ""), kind


def evidence_link_metadata(row: InvestigationEvidenceLink) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-evidence-link/1.0",
        "evidenceLinkId": row.evidence_link_id,
        "projectId": row.project_id,
        "statementId": row.statement_id,
        "evidenceRef": row.evidence_ref,
        "evidenceKind": row.evidence_kind,
        "relation": row.relation,
        "sourceFingerprint": row.source_fingerprint,
        "locator": row.locator,
        "note": row.note,
        "humanAsserted": True,
        "linkFingerprint": row.link_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    }


def create_evidence_link(db: Session, user_key: str, payload: InvestigationEvidenceLinkRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    statement = _statement(db, user_key, payload.statementId)
    if statement is None or statement.project_id != payload.projectId:
        raise LookupError(payload.statementId)
    discovered_fp, discovered_kind = _validate_workspace_evidence(db, user_key, payload.projectId, payload.evidenceRef)
    source_fp = payload.sourceFingerprint or discovered_fp
    kind = payload.evidenceKind if payload.evidenceKind != "external-reference" or not discovered_kind else discovered_kind
    canonical = {
        "projectId": payload.projectId,
        "statementId": payload.statementId,
        "evidenceRef": payload.evidenceRef,
        "evidenceKind": kind,
        "relation": payload.relation,
        "sourceFingerprint": source_fp,
        "locator": payload.locator,
        "note": payload.note,
        "metadata": payload.metadata,
        "humanAsserted": True,
    }
    fp = sha256_hex(canonical)
    existing = db.scalar(select(InvestigationEvidenceLink).where(
        InvestigationEvidenceLink.user_key == user_key,
        InvestigationEvidenceLink.project_id == payload.projectId,
        InvestigationEvidenceLink.link_fingerprint == fp,
    ).limit(1))
    if existing is not None:
        return evidence_link_metadata(existing)
    row = InvestigationEvidenceLink(
        user_key=user_key,
        evidence_link_id="evidence-link-" + uuid4().hex[:24],
        project_id=payload.projectId,
        statement_id=payload.statementId,
        evidence_ref=payload.evidenceRef,
        evidence_kind=kind,
        relation=payload.relation,
        source_fingerprint=source_fp,
        locator=payload.locator,
        note=payload.note,
        link_fingerprint=fp,
        metadata_json=payload.metadata,
    )
    db.add(row); db.commit(); db.refresh(row)
    return evidence_link_metadata(row)


def list_evidence_links(db: Session, user_key: str, project_id: str | None = None, statement_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    query = select(InvestigationEvidenceLink).where(InvestigationEvidenceLink.user_key == user_key)
    if project_id:
        query = query.where(InvestigationEvidenceLink.project_id == project_id)
    if statement_id:
        query = query.where(InvestigationEvidenceLink.statement_id == statement_id)
    rows = db.scalars(query.order_by(InvestigationEvidenceLink.created_at.desc()).limit(limit)).all()
    return [evidence_link_metadata(row) for row in rows]


def statement_relation_metadata(row: InvestigationStatementRelation) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-statement-relation/1.0",
        "relationId": row.relation_id,
        "projectId": row.project_id,
        "fromStatementId": row.from_statement_id,
        "toStatementId": row.to_statement_id,
        "relation": row.relation,
        "note": row.note,
        "humanAsserted": True,
        "relationFingerprint": row.relation_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    }


def create_statement_relation(db: Session, user_key: str, payload: InvestigationStatementRelationRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    left = _statement(db, user_key, payload.fromStatementId)
    right = _statement(db, user_key, payload.toStatementId)
    if left is None or right is None or left.project_id != payload.projectId or right.project_id != payload.projectId:
        raise LookupError("statement")
    canonical = {
        "projectId": payload.projectId,
        "fromStatementId": payload.fromStatementId,
        "toStatementId": payload.toStatementId,
        "relation": payload.relation,
        "note": payload.note,
        "metadata": payload.metadata,
        "humanAsserted": True,
    }
    fp = sha256_hex(canonical)
    existing = db.scalar(select(InvestigationStatementRelation).where(
        InvestigationStatementRelation.user_key == user_key,
        InvestigationStatementRelation.project_id == payload.projectId,
        InvestigationStatementRelation.relation_fingerprint == fp,
    ).limit(1))
    if existing is not None:
        return statement_relation_metadata(existing)
    row = InvestigationStatementRelation(
        user_key=user_key,
        relation_id="statement-relation-" + uuid4().hex[:24],
        project_id=payload.projectId,
        from_statement_id=payload.fromStatementId,
        to_statement_id=payload.toStatementId,
        relation=payload.relation,
        note=payload.note,
        relation_fingerprint=fp,
        metadata_json=payload.metadata,
    )
    db.add(row); db.commit(); db.refresh(row)
    return statement_relation_metadata(row)


def list_statement_relations(db: Session, user_key: str, project_id: str | None = None, statement_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    query = select(InvestigationStatementRelation).where(InvestigationStatementRelation.user_key == user_key)
    if project_id:
        query = query.where(InvestigationStatementRelation.project_id == project_id)
    if statement_id:
        query = query.where(
            (InvestigationStatementRelation.from_statement_id == statement_id) |
            (InvestigationStatementRelation.to_statement_id == statement_id)
        )
    rows = db.scalars(query.order_by(InvestigationStatementRelation.created_at.desc()).limit(limit)).all()
    return [statement_relation_metadata(row) for row in rows]


def build_project_workspace(db: Session, user_key: str, project_id: str, include_visual_graph: bool = True) -> dict[str, Any]:
    project = _project(db, user_key, project_id)
    statements = list_statements(db, user_key, project_id, None, 1000)
    evidence = list_evidence_links(db, user_key, project_id, None, 2000)
    relations = list_statement_relations(db, user_key, project_id, None, 2000)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    project_node = f"workspace:project:{project_id}"
    nodes[project_node] = {"id": project_node, "kind": "project", "title": project.title, "revision": project.revision, "fingerprint": project.project_fingerprint}

    visual: dict[str, Any] | None = None
    if include_visual_graph:
        visual = build_visual_research_workspace(db, user_key, project_id)
        visual_graph = visual.get("graph") or {}
        for node in visual_graph.get("nodes") or []:
            if isinstance(node, dict) and node.get("id"):
                nodes[str(node["id"])] = node
        for edge in visual_graph.get("edges") or []:
            if isinstance(edge, dict):
                edges.append(edge)

    type_counts = {kind: 0 for kind in STATEMENT_TYPES}
    for item in statements:
        sid = str(item["statementId"])
        node_id = f"workspace:investigation-statement:{sid}"
        stype = str(item["statementType"])
        if stype in type_counts:
            type_counts[stype] += 1
        nodes[node_id] = {
            "id": node_id,
            "kind": f"investigation-{stype}",
            "statementId": sid,
            "title": item.get("title") or "",
            "reviewState": item.get("reviewState") or "open",
            "revision": item.get("revision") or 0,
            "fingerprint": item.get("statementFingerprint") or "",
        }
        edges.append({"source": project_node, "target": node_id, "relation": "contains-investigative-statement"})

    evidence_relation_counts = {kind: 0 for kind in EVIDENCE_RELATIONS}
    for link in evidence:
        evidence_ref = str(link["evidenceRef"])
        statement_node = f"workspace:investigation-statement:{link['statementId']}"
        evidence_node = evidence_ref
        if evidence_node not in nodes:
            nodes[evidence_node] = {
                "id": evidence_node,
                "kind": "investigative-evidence-reference",
                "evidenceKind": link.get("evidenceKind") or "external-reference",
                "sourceFingerprint": link.get("sourceFingerprint") or "",
                "locator": link.get("locator") or "",
            }
        relation = str(link["relation"])
        if relation in evidence_relation_counts:
            evidence_relation_counts[relation] += 1
        edges.append({
            "source": evidence_node,
            "target": statement_node,
            "relation": f"evidence-{relation}",
            "evidenceLinkId": link["evidenceLinkId"],
            "humanAsserted": True,
        })

    statement_relation_counts = {kind: 0 for kind in STATEMENT_RELATIONS}
    for rel in relations:
        relation = str(rel["relation"])
        if relation in statement_relation_counts:
            statement_relation_counts[relation] += 1
        edges.append({
            "source": f"workspace:investigation-statement:{rel['fromStatementId']}",
            "target": f"workspace:investigation-statement:{rel['toStatementId']}",
            "relation": f"statement-{relation}",
            "relationId": rel["relationId"],
            "humanAsserted": True,
        })

    graph = {
        "schema": INVESTIGATIVE_GRAPH_SCHEMA,
        "nodes": sorted(nodes.values(), key=lambda x: str(x.get("id") or "")),
        "edges": sorted(edges, key=lambda x: (str(x.get("source") or ""), str(x.get("target") or ""), str(x.get("relation") or ""))),
    }
    graph["graphFingerprint"] = sha256_hex(graph)
    item = {
        "schema": INVESTIGATIVE_RESEARCH_WORKSPACE_SCHEMA,
        "projectId": project_id,
        "projectRevision": project.revision,
        "projectFingerprint": project.project_fingerprint,
        "backendAuthoritative": True,
        "referenceFirst": True,
        "specialistObjectAuthorityPreserved": True,
        "humanAssertedRelationships": True,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "statements": statements,
        "evidenceLinks": evidence,
        "statementRelations": relations,
        "visualResearchGraphIncluded": include_visual_graph,
        "visualResearchGraphFingerprint": ((visual or {}).get("graph") or {}).get("graphFingerprint", ""),
        "counts": {
            "statements": len(statements),
            "evidenceLinks": len(evidence),
            "statementRelations": len(relations),
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            **{f"{key}s": value for key, value in type_counts.items()},
            "evidenceContradictions": evidence_relation_counts.get("contradicts", 0),
            "statementContradictions": statement_relation_counts.get("contradicts", 0),
            "competingHypotheses": statement_relation_counts.get("competes-with", 0),
        },
        "graph": graph,
    }
    item["workspaceFingerprint"] = sha256_hex({
        "projectId": project_id,
        "projectRevision": project.revision,
        "graphFingerprint": graph["graphFingerprint"],
        "statementFingerprints": sorted(str(x.get("statementFingerprint") or "") for x in statements),
    })
    return item


def snapshot_metadata(row: InvestigativeResearchWorkspaceSnapshot) -> dict[str, Any]:
    return {
        "schema": SNAPSHOT_SCHEMA,
        "snapshotId": row.snapshot_id,
        "projectId": row.project_id,
        "graphFingerprint": row.graph_fingerprint,
        "workspaceFingerprint": row.workspace_fingerprint,
        "statementCount": row.statement_count,
        "evidenceLinkCount": row.evidence_link_count,
        "statementRelationCount": row.statement_relation_count,
        "nodeCount": row.node_count,
        "edgeCount": row.edge_count,
        "createdAt": iso(row.created_at),
    }


def create_snapshot(db: Session, user_key: str, project_id: str, payload: InvestigativeResearchSnapshotRequest) -> dict[str, Any]:
    context = build_project_workspace(db, user_key, project_id, payload.includeVisualGraph)
    counts = context.get("counts") or {}
    row = InvestigativeResearchWorkspaceSnapshot(
        user_key=user_key,
        snapshot_id="investigation-snapshot-" + uuid4().hex[:24],
        project_id=project_id,
        graph_fingerprint=str((context.get("graph") or {}).get("graphFingerprint") or ""),
        workspace_fingerprint=str(context.get("workspaceFingerprint") or ""),
        statement_count=int(counts.get("statements") or 0),
        evidence_link_count=int(counts.get("evidenceLinks") or 0),
        statement_relation_count=int(counts.get("statementRelations") or 0),
        node_count=int(counts.get("nodes") or 0),
        edge_count=int(counts.get("edges") or 0),
        context_json=context,
    )
    db.add(row); db.commit(); db.refresh(row)
    return snapshot_metadata(row)


def list_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigativeResearchWorkspaceSnapshot)
        .where(InvestigativeResearchWorkspaceSnapshot.user_key == user_key, InvestigativeResearchWorkspaceSnapshot.project_id == project_id)
        .order_by(InvestigativeResearchWorkspaceSnapshot.created_at.desc()).limit(limit)
    ).all()
    return [snapshot_metadata(row) for row in rows]
