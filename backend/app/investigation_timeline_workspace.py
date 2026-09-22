from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .investigation_graph_workspace import build_graph as build_investigation_graph
from .investigative_research_workspace import get_statement
from .models import (
    InvestigationEventHead,
    InvestigationEventRelation,
    InvestigationEventRevision,
    InvestigationEventStatementLink,
    InvestigationTimelineSnapshot,
    ProjectHead,
)
from .utils import iso, sha256_hex

TIMELINE_WORKSPACE_SCHEMA = "sc-workspace-timeline-event-reconstruction-workspace/1.0"
EVENT_REQUEST_SCHEMA = "sc-workspace-investigation-event-request/1.0"
EVENT_SCHEMA = "sc-workspace-investigation-event/1.0"
EVENT_STATEMENT_LINK_REQUEST_SCHEMA = "sc-workspace-investigation-event-statement-link-request/1.0"
EVENT_RELATION_REQUEST_SCHEMA = "sc-workspace-investigation-event-relation-request/1.0"
TIMELINE_SCHEMA = "sc-workspace-investigation-timeline/1.0"
RECONSTRUCTION_GRAPH_SCHEMA = "sc-workspace-investigation-reconstruction-graph/1.0"
TEMPORAL_DIAGNOSTICS_SCHEMA = "sc-workspace-investigation-temporal-diagnostics/1.0"
TIMELINE_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-investigation-timeline-snapshot-request/1.0"
TIMELINE_SNAPSHOT_SCHEMA = "sc-workspace-investigation-timeline-snapshot/1.0"

EVENT_REVIEW_STATES = ("open", "under-review", "documented", "contested", "unresolved", "closed")
TIME_PRECISIONS = ("exact", "minute", "hour", "day", "month", "year", "approximate", "range", "unknown")
TIME_STATUSES = ("recorded", "reported", "estimated", "disputed", "unknown")
EVENT_STATEMENT_RELATIONS = ("describes", "supports", "contradicts", "contextualizes", "questions", "source-of")
EVENT_RELATIONS = ("precedes", "follows", "overlaps", "contains", "same-event-as", "sequence-related")


class InvestigationEventRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-event-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    eventId: str = Field(default="", max_length=160)
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=20000)
    startAt: datetime | None = None
    endAt: datetime | None = None
    timePrecision: Literal["exact", "minute", "hour", "day", "month", "year", "approximate", "range", "unknown"] = "unknown"
    timeStatus: Literal["recorded", "reported", "estimated", "disputed", "unknown"] = "unknown"
    locationRef: str = Field(default="", max_length=1200)
    reviewState: Literal["open", "under-review", "documented", "contested", "unresolved", "closed"] = "open"
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_range(self):
        if self.startAt is not None and self.endAt is not None and self.endAt < self.startAt:
            raise ValueError("endAt must not precede startAt")
        return self


class InvestigationEventStatementLinkRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-event-statement-link-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    eventId: str = Field(min_length=1, max_length=160)
    statementId: str = Field(min_length=1, max_length=160)
    relation: Literal["describes", "supports", "contradicts", "contextualizes", "questions", "source-of"]
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEventRelationRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-event-relation-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    fromEventId: str = Field(min_length=1, max_length=160)
    toEventId: str = Field(min_length=1, max_length=160)
    relation: Literal["precedes", "follows", "overlaps", "contains", "same-event-as", "sequence-related"]
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def no_self_relation(self):
        if self.fromEventId == self.toEventId:
            raise ValueError("event relation endpoints must differ")
        return self


class InvestigationTimelineSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-timeline-snapshot-request/1.0"]
    includeInvestigationGraph: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": TIMELINE_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.9.0",
        "release": "Timeline, Event Reconstruction & Investigative Sequence Workspace",
        "backendAuthoritative": True,
        "referenceFirst": True,
        "eventRevisionHistory": True,
        "humanAssertedTemporalRelations": True,
        "deterministicTimelineOrdering": True,
        "temporalConsistencyDiagnostics": True,
        "reconstructionGraphOverlay": True,
        "immutableTimelineSnapshots": True,
        "specialistObjectAuthorityPreserved": True,
        "automaticCausalityInference": False,
        "automaticMotiveInference": False,
        "automaticCulpabilityInference": False,
        "automaticNarrativeSelection": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "supportedTimePrecisions": list(TIME_PRECISIONS),
        "supportedTimeStatuses": list(TIME_STATUSES),
        "supportedEventStatementRelations": list(EVENT_STATEMENT_RELATIONS),
        "supportedEventRelations": list(EVENT_RELATIONS),
    }


def _project(db: Session, user_key: str, project_id: str) -> ProjectHead:
    row = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if row is None:
        raise KeyError(project_id)
    return row


def _event(db: Session, user_key: str, event_id: str) -> InvestigationEventHead | None:
    return db.get(InvestigationEventHead, {"user_key": user_key, "event_id": event_id})


def event_metadata(row: InvestigationEventHead) -> dict[str, Any]:
    return {
        "schema": EVENT_SCHEMA,
        "eventId": row.event_id,
        "projectId": row.project_id,
        "title": row.title,
        "description": row.description,
        "startAt": iso(row.start_at) if row.start_at else "",
        "endAt": iso(row.end_at) if row.end_at else "",
        "timePrecision": row.time_precision,
        "timeStatus": row.time_status,
        "locationRef": row.location_ref,
        "reviewState": row.review_state,
        "revision": row.revision,
        "eventFingerprint": row.event_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _event_fingerprint(payload: InvestigationEventRequest, event_id: str, revision: int) -> str:
    return sha256_hex({
        "eventId": event_id,
        "projectId": payload.projectId,
        "title": payload.title,
        "description": payload.description,
        "startAt": iso(payload.startAt) if payload.startAt else "",
        "endAt": iso(payload.endAt) if payload.endAt else "",
        "timePrecision": payload.timePrecision,
        "timeStatus": payload.timeStatus,
        "locationRef": payload.locationRef,
        "reviewState": payload.reviewState,
        "revision": revision,
        "metadata": payload.metadata,
    })


def store_event(db: Session, user_key: str, payload: InvestigationEventRequest) -> tuple[dict[str, Any], bool]:
    _project(db, user_key, payload.projectId)
    event_id = payload.eventId or ("event-" + uuid4().hex[:24])
    row = _event(db, user_key, event_id)
    created = row is None
    if row is not None:
        if row.project_id != payload.projectId:
            raise ValueError("event belongs to a different project")
        if payload.expectedRevision is not None and payload.expectedRevision != row.revision:
            raise RuntimeError("event revision conflict")
        revision = row.revision + 1
    else:
        revision = 1
        row = InvestigationEventHead(user_key=user_key, event_id=event_id, project_id=payload.projectId)
        db.add(row)
    fp = _event_fingerprint(payload, event_id, revision)
    row.title = payload.title
    row.description = payload.description
    row.start_at = payload.startAt
    row.end_at = payload.endAt
    row.time_precision = payload.timePrecision
    row.time_status = payload.timeStatus
    row.location_ref = payload.locationRef
    row.review_state = payload.reviewState
    row.revision = revision
    row.event_fingerprint = fp
    row.metadata_json = payload.metadata
    db.add(InvestigationEventRevision(
        user_key=user_key,
        event_id=event_id,
        revision=revision,
        project_id=payload.projectId,
        title=payload.title,
        description=payload.description,
        start_at=payload.startAt,
        end_at=payload.endAt,
        time_precision=payload.timePrecision,
        time_status=payload.timeStatus,
        location_ref=payload.locationRef,
        review_state=payload.reviewState,
        event_fingerprint=fp,
        metadata_json=payload.metadata,
    ))
    db.commit(); db.refresh(row)
    return event_metadata(row), created


def list_events(db: Session, user_key: str, project_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    query = select(InvestigationEventHead).where(InvestigationEventHead.user_key == user_key)
    if project_id:
        query = query.where(InvestigationEventHead.project_id == project_id)
    rows = db.scalars(query.order_by(InvestigationEventHead.updated_at.desc()).limit(limit)).all()
    return [event_metadata(row) for row in rows]


def get_event(db: Session, user_key: str, event_id: str) -> dict[str, Any] | None:
    row = _event(db, user_key, event_id)
    return event_metadata(row) if row else None


def list_event_revisions(db: Session, user_key: str, event_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationEventRevision)
        .where(InvestigationEventRevision.user_key == user_key, InvestigationEventRevision.event_id == event_id)
        .order_by(InvestigationEventRevision.revision.desc()).limit(limit)
    ).all()
    return [{
        "schema": "sc-workspace-investigation-event-revision/1.0",
        "eventId": row.event_id,
        "projectId": row.project_id,
        "revision": row.revision,
        "title": row.title,
        "description": row.description,
        "startAt": iso(row.start_at) if row.start_at else "",
        "endAt": iso(row.end_at) if row.end_at else "",
        "timePrecision": row.time_precision,
        "timeStatus": row.time_status,
        "locationRef": row.location_ref,
        "reviewState": row.review_state,
        "eventFingerprint": row.event_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    } for row in rows]


def event_statement_link_metadata(row: InvestigationEventStatementLink) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-event-statement-link/1.0",
        "linkId": row.link_id,
        "projectId": row.project_id,
        "eventId": row.event_id,
        "statementId": row.statement_id,
        "relation": row.relation,
        "note": row.note,
        "humanAsserted": True,
        "linkFingerprint": row.link_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    }


def create_event_statement_link(db: Session, user_key: str, payload: InvestigationEventStatementLinkRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    event = _event(db, user_key, payload.eventId)
    statement = get_statement(db, user_key, payload.statementId)
    if event is None or event.project_id != payload.projectId:
        raise LookupError(payload.eventId)
    if statement is None or statement.get("projectId") != payload.projectId:
        raise LookupError(payload.statementId)
    canonical = {
        "projectId": payload.projectId,
        "eventId": payload.eventId,
        "statementId": payload.statementId,
        "relation": payload.relation,
        "note": payload.note,
        "metadata": payload.metadata,
        "humanAsserted": True,
    }
    fp = sha256_hex(canonical)
    existing = db.scalar(select(InvestigationEventStatementLink).where(
        InvestigationEventStatementLink.user_key == user_key,
        InvestigationEventStatementLink.project_id == payload.projectId,
        InvestigationEventStatementLink.link_fingerprint == fp,
    ).limit(1))
    if existing is not None:
        return event_statement_link_metadata(existing)
    row = InvestigationEventStatementLink(
        user_key=user_key,
        link_id="event-statement-link-" + uuid4().hex[:24],
        project_id=payload.projectId,
        event_id=payload.eventId,
        statement_id=payload.statementId,
        relation=payload.relation,
        note=payload.note,
        link_fingerprint=fp,
        metadata_json=payload.metadata,
    )
    db.add(row); db.commit(); db.refresh(row)
    return event_statement_link_metadata(row)


def list_event_statement_links(db: Session, user_key: str, project_id: str | None = None, event_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
    query = select(InvestigationEventStatementLink).where(InvestigationEventStatementLink.user_key == user_key)
    if project_id:
        query = query.where(InvestigationEventStatementLink.project_id == project_id)
    if event_id:
        query = query.where(InvestigationEventStatementLink.event_id == event_id)
    rows = db.scalars(query.order_by(InvestigationEventStatementLink.created_at.desc()).limit(limit)).all()
    return [event_statement_link_metadata(row) for row in rows]


def event_relation_metadata(row: InvestigationEventRelation) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-event-relation/1.0",
        "relationId": row.relation_id,
        "projectId": row.project_id,
        "fromEventId": row.from_event_id,
        "toEventId": row.to_event_id,
        "relation": row.relation,
        "note": row.note,
        "humanAsserted": True,
        "relationFingerprint": row.relation_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    }


def create_event_relation(db: Session, user_key: str, payload: InvestigationEventRelationRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    left = _event(db, user_key, payload.fromEventId)
    right = _event(db, user_key, payload.toEventId)
    if left is None or right is None or left.project_id != payload.projectId or right.project_id != payload.projectId:
        raise LookupError("event")
    canonical = {
        "projectId": payload.projectId,
        "fromEventId": payload.fromEventId,
        "toEventId": payload.toEventId,
        "relation": payload.relation,
        "note": payload.note,
        "metadata": payload.metadata,
        "humanAsserted": True,
    }
    fp = sha256_hex(canonical)
    existing = db.scalar(select(InvestigationEventRelation).where(
        InvestigationEventRelation.user_key == user_key,
        InvestigationEventRelation.project_id == payload.projectId,
        InvestigationEventRelation.relation_fingerprint == fp,
    ).limit(1))
    if existing is not None:
        return event_relation_metadata(existing)
    row = InvestigationEventRelation(
        user_key=user_key,
        relation_id="event-relation-" + uuid4().hex[:24],
        project_id=payload.projectId,
        from_event_id=payload.fromEventId,
        to_event_id=payload.toEventId,
        relation=payload.relation,
        note=payload.note,
        relation_fingerprint=fp,
        metadata_json=payload.metadata,
    )
    db.add(row); db.commit(); db.refresh(row)
    return event_relation_metadata(row)


def list_event_relations(db: Session, user_key: str, project_id: str | None = None, event_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
    query = select(InvestigationEventRelation).where(InvestigationEventRelation.user_key == user_key)
    if project_id:
        query = query.where(InvestigationEventRelation.project_id == project_id)
    if event_id:
        query = query.where((InvestigationEventRelation.from_event_id == event_id) | (InvestigationEventRelation.to_event_id == event_id))
    rows = db.scalars(query.order_by(InvestigationEventRelation.created_at.desc()).limit(limit)).all()
    return [event_relation_metadata(row) for row in rows]


def _timeline_sort_key(item: dict[str, Any]) -> tuple[int, str, str, str]:
    start = str(item.get("startAt") or "")
    end = str(item.get("endAt") or "")
    return (0 if start else 1, start, end, str(item.get("eventId") or ""))


def build_timeline(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    _project(db, user_key, project_id)
    events = sorted(list_events(db, user_key, project_id, 5000), key=_timeline_sort_key)
    relations = list_event_relations(db, user_key, project_id, None, 5000)
    statement_links = list_event_statement_links(db, user_key, project_id, None, 5000)
    timed = [x for x in events if x.get("startAt")]
    undated = [x for x in events if not x.get("startAt")]
    item = {
        "schema": TIMELINE_SCHEMA,
        "projectId": project_id,
        "events": events,
        "timedEventCount": len(timed),
        "undatedEventCount": len(undated),
        "eventRelationCount": len(relations),
        "eventStatementLinkCount": len(statement_links),
        "deterministicOrdering": True,
        "automaticGapFilling": False,
        "automaticCausalityInference": False,
    }
    item["timelineFingerprint"] = sha256_hex(item)
    return item


def temporal_diagnostics(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    _project(db, user_key, project_id)
    rows = db.scalars(select(InvestigationEventHead).where(
        InvestigationEventHead.user_key == user_key,
        InvestigationEventHead.project_id == project_id,
    )).all()
    events = {row.event_id: row for row in rows}
    relations = list_event_relations(db, user_key, project_id, None, 5000)
    issues: list[dict[str, Any]] = []
    for rel in relations:
        left = events.get(str(rel.get("fromEventId") or ""))
        right = events.get(str(rel.get("toEventId") or ""))
        if left is None or right is None:
            continue
        relation = str(rel.get("relation") or "")
        inconsistent = False
        basis = ""
        if relation == "precedes" and left.start_at and right.start_at and left.start_at > right.start_at:
            inconsistent = True; basis = "fromEvent.startAt is later than toEvent.startAt"
        elif relation == "follows" and left.start_at and right.start_at and left.start_at < right.start_at:
            inconsistent = True; basis = "fromEvent.startAt is earlier than toEvent.startAt"
        elif relation == "overlaps" and left.start_at and right.start_at:
            left_end = left.end_at or left.start_at
            right_end = right.end_at or right.start_at
            if left_end < right.start_at or right_end < left.start_at:
                inconsistent = True; basis = "recorded event intervals do not overlap"
        elif relation == "contains" and left.start_at and right.start_at:
            left_end = left.end_at or left.start_at
            right_end = right.end_at or right.start_at
            if left.start_at > right.start_at or left_end < right_end:
                inconsistent = True; basis = "recorded fromEvent interval does not contain toEvent interval"
        elif relation == "same-event-as" and left.start_at and right.start_at:
            left_end = left.end_at or left.start_at
            right_end = right.end_at or right.start_at
            if left_end < right.start_at or right_end < left.start_at:
                inconsistent = True; basis = "recorded intervals are disjoint"
        if inconsistent:
            issues.append({
                "diagnosticId": "temporal-diagnostic-" + sha256_hex({"relation": rel, "basis": basis})[:20],
                "severity": "review",
                "relationId": rel.get("relationId"),
                "fromEventId": rel.get("fromEventId"),
                "toEventId": rel.get("toEventId"),
                "relation": relation,
                "basis": basis,
                "automaticResolution": False,
            })
    return {
        "schema": TEMPORAL_DIAGNOSTICS_SCHEMA,
        "projectId": project_id,
        "issues": issues,
        "count": len(issues),
        "diagnosticScope": "recorded-time-vs-human-asserted-temporal-relation",
        "automaticResolution": False,
        "automaticNarrativeSelection": False,
        "automaticTruthDetermination": False,
    }


def build_reconstruction_graph(db: Session, user_key: str, project_id: str, include_investigation_graph: bool = True) -> dict[str, Any]:
    _project(db, user_key, project_id)
    if include_investigation_graph:
        base = build_investigation_graph(db, user_key, project_id, True)
        nodes = list(base.get("nodes") or [])
        edges = list(base.get("edges") or [])
    else:
        base = {"graphFingerprint": ""}
        nodes = []
        edges = []
    events = list_events(db, user_key, project_id, 5000)
    links = list_event_statement_links(db, user_key, project_id, None, 5000)
    relations = list_event_relations(db, user_key, project_id, None, 5000)
    for event in events:
        nodes.append({
            "id": f"workspace:investigation-event:{event['eventId']}",
            "kind": "investigation-event",
            "eventId": event["eventId"],
            "title": event["title"],
            "startAt": event.get("startAt") or "",
            "endAt": event.get("endAt") or "",
            "timePrecision": event.get("timePrecision"),
            "timeStatus": event.get("timeStatus"),
            "reviewState": event.get("reviewState"),
            "fingerprint": event.get("eventFingerprint"),
        })
    for link in links:
        edges.append({
            "source": f"workspace:investigation-event:{link['eventId']}",
            "target": f"workspace:investigation-statement:{link['statementId']}",
            "relation": link["relation"],
            "edgeKind": "event-statement",
            "humanAsserted": True,
            "fingerprint": link["linkFingerprint"],
        })
    for rel in relations:
        edges.append({
            "source": f"workspace:investigation-event:{rel['fromEventId']}",
            "target": f"workspace:investigation-event:{rel['toEventId']}",
            "relation": rel["relation"],
            "edgeKind": "event-temporal-relation",
            "humanAsserted": True,
            "fingerprint": rel["relationFingerprint"],
        })
    nodes = sorted(nodes, key=lambda x: str(x.get("id") or ""))
    edges = sorted(edges, key=lambda x: (str(x.get("source") or ""), str(x.get("target") or ""), str(x.get("relation") or "")))
    item = {
        "schema": RECONSTRUCTION_GRAPH_SCHEMA,
        "projectId": project_id,
        "baseInvestigationGraphFingerprint": base.get("graphFingerprint") or "",
        "nodes": nodes,
        "edges": edges,
        "eventCount": len(events),
        "eventStatementLinkCount": len(links),
        "eventRelationCount": len(relations),
        "automaticCausalityInference": False,
    }
    item["graphFingerprint"] = sha256_hex(item)
    return item


def create_timeline_snapshot(db: Session, user_key: str, project_id: str, payload: InvestigationTimelineSnapshotRequest) -> dict[str, Any]:
    timeline = build_timeline(db, user_key, project_id)
    graph = build_reconstruction_graph(db, user_key, project_id, payload.includeInvestigationGraph)
    diagnostics = temporal_diagnostics(db, user_key, project_id)
    snapshot_id = "timeline-snapshot-" + uuid4().hex[:24]
    snapshot_payload = {
        "schema": TIMELINE_SNAPSHOT_SCHEMA,
        "snapshotId": snapshot_id,
        "projectId": project_id,
        "timeline": timeline,
        "reconstructionGraph": graph,
        "temporalDiagnostics": diagnostics,
    }
    fp = sha256_hex(snapshot_payload)
    row = InvestigationTimelineSnapshot(
        user_key=user_key,
        snapshot_id=snapshot_id,
        project_id=project_id,
        timeline_fingerprint=str(timeline.get("timelineFingerprint") or ""),
        graph_fingerprint=str(graph.get("graphFingerprint") or ""),
        snapshot_fingerprint=fp,
        event_count=int(graph.get("eventCount") or 0),
        event_statement_link_count=int(graph.get("eventStatementLinkCount") or 0),
        event_relation_count=int(graph.get("eventRelationCount") or 0),
        temporal_issue_count=int(diagnostics.get("count") or 0),
        context_json=snapshot_payload,
    )
    db.add(row); db.commit(); db.refresh(row)
    return timeline_snapshot_metadata(row)


def timeline_snapshot_metadata(row: InvestigationTimelineSnapshot) -> dict[str, Any]:
    return {
        "schema": TIMELINE_SNAPSHOT_SCHEMA,
        "snapshotId": row.snapshot_id,
        "projectId": row.project_id,
        "timelineFingerprint": row.timeline_fingerprint,
        "graphFingerprint": row.graph_fingerprint,
        "snapshotFingerprint": row.snapshot_fingerprint,
        "eventCount": row.event_count,
        "eventStatementLinkCount": row.event_statement_link_count,
        "eventRelationCount": row.event_relation_count,
        "temporalIssueCount": row.temporal_issue_count,
        "createdAt": iso(row.created_at),
    }


def list_timeline_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationTimelineSnapshot)
        .where(InvestigationTimelineSnapshot.user_key == user_key, InvestigationTimelineSnapshot.project_id == project_id)
        .order_by(InvestigationTimelineSnapshot.created_at.desc()).limit(limit)
    ).all()
    return [timeline_snapshot_metadata(row) for row in rows]
