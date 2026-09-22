from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    InvestigationDocumentHead,
    InvestigationDocumentRevision,
    InvestigationDocumentExcerpt,
    InvestigationTestimonyHead,
    InvestigationTestimonyRevision,
    InvestigationDocumentaryContextLink,
    InvestigationTestimonyRelation,
    InvestigationDocumentarySnapshot,
    InvestigationEntityHead,
    InvestigationEventHead,
    InvestigationStatementHead,
    ProjectHead,
)
from .investigation_entity_workspace import build_entity_graph
from .utils import iso, sha256_hex

DOCUMENTARY_WORKSPACE_SCHEMA = "sc-workspace-documentary-evidence-testimony-statement-analysis-workspace/1.0"
DOCUMENT_SCHEMA = "sc-workspace-investigation-document/1.0"
DOCUMENT_REQUEST_SCHEMA = "sc-workspace-investigation-document-request/1.0"
DOCUMENT_EXCERPT_REQUEST_SCHEMA = "sc-workspace-investigation-document-excerpt-request/1.0"
TESTIMONY_SCHEMA = "sc-workspace-investigation-testimony/1.0"
TESTIMONY_REQUEST_SCHEMA = "sc-workspace-investigation-testimony-request/1.0"
DOCUMENTARY_CONTEXT_LINK_REQUEST_SCHEMA = "sc-workspace-investigation-documentary-context-link-request/1.0"
TESTIMONY_RELATION_REQUEST_SCHEMA = "sc-workspace-investigation-testimony-relation-request/1.0"
DOCUMENTARY_GRAPH_SCHEMA = "sc-workspace-investigation-documentary-graph/1.0"
DOCUMENTARY_ANALYSIS_SCHEMA = "sc-workspace-investigation-documentary-analysis/1.0"
DOCUMENTARY_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-investigation-documentary-snapshot-request/1.0"
DOCUMENTARY_SNAPSHOT_SCHEMA = "sc-workspace-investigation-documentary-snapshot/1.0"

DOCUMENT_TYPES = (
    "report", "filing", "transcript", "correspondence", "memorandum", "contract",
    "record", "dataset-document", "article", "book", "web-page", "image-record",
    "audio-record", "video-record", "other",
)
TESTIMONY_TYPES = (
    "interview", "deposition", "affidavit", "hearing", "declaration",
    "witness-statement", "press-statement", "correspondence", "transcript-excerpt", "other",
)
REVIEW_STATES = ("open", "under-review", "documented", "contested", "unresolved", "closed")
CONTEXT_SOURCE_KINDS = ("document", "excerpt", "testimony")
CONTEXT_TARGET_KINDS = ("statement", "event", "entity", "evidence-ref", "scientific-object-ref")
CONTEXT_RELATIONS = (
    "mentions", "supports", "contradicts", "contextualizes", "challenges", "corroborates",
    "source-of", "subject-of", "describes", "related-to",
)
TESTIMONY_RELATIONS = ("corroborates", "contradicts", "contextualizes", "challenges", "duplicates", "related-to")


class InvestigationDocumentRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-document-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    documentId: str = Field(default="", max_length=160)
    documentType: Literal["report", "filing", "transcript", "correspondence", "memorandum", "contract", "record", "dataset-document", "article", "book", "web-page", "image-record", "audio-record", "video-record", "other"]
    title: str = Field(min_length=1, max_length=1000)
    description: str = Field(default="", max_length=20000)
    sourceRef: str = Field(min_length=1, max_length=2000)
    sourceFingerprint: str = Field(min_length=8, max_length=128)
    authority: str = Field(default="", max_length=500)
    publishedAt: str = Field(default="", max_length=64)
    reviewState: Literal["open", "under-review", "documented", "contested", "unresolved", "closed"] = "open"
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationDocumentExcerptRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-document-excerpt-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    documentId: str = Field(min_length=1, max_length=160)
    text: str = Field(min_length=1, max_length=50000)
    locator: str = Field(min_length=1, max_length=1000)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationTestimonyRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-testimony-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    testimonyId: str = Field(default="", max_length=160)
    testimonyType: Literal["interview", "deposition", "affidavit", "hearing", "declaration", "witness-statement", "press-statement", "correspondence", "transcript-excerpt", "other"]
    title: str = Field(min_length=1, max_length=1000)
    text: str = Field(min_length=1, max_length=100000)
    speakerEntityId: str = Field(default="", max_length=160)
    sourceDocumentId: str = Field(default="", max_length=160)
    sourceRef: str = Field(default="", max_length=2000)
    sourceFingerprint: str = Field(default="", max_length=128)
    occurredAt: str = Field(default="", max_length=64)
    reviewState: Literal["open", "under-review", "documented", "contested", "unresolved", "closed"] = "open"
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def source_is_preserved(self):
        if not self.sourceDocumentId and not (self.sourceRef and self.sourceFingerprint):
            raise ValueError("testimony requires sourceDocumentId or sourceRef with sourceFingerprint")
        return self


class InvestigationDocumentaryContextLinkRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-documentary-context-link-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    sourceKind: Literal["document", "excerpt", "testimony"]
    sourceId: str = Field(min_length=1, max_length=160)
    targetKind: Literal["statement", "event", "entity", "evidence-ref", "scientific-object-ref"]
    targetRef: str = Field(min_length=1, max_length=2000)
    relation: Literal["mentions", "supports", "contradicts", "contextualizes", "challenges", "corroborates", "source-of", "subject-of", "describes", "related-to"]
    sourceFingerprint: str = Field(default="", max_length=128)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def external_targets_are_fingerprinted(self):
        if self.targetKind in {"evidence-ref", "scientific-object-ref"} and not self.sourceFingerprint:
            raise ValueError("external documentary context links require sourceFingerprint")
        return self


class InvestigationTestimonyRelationRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-testimony-relation-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    fromTestimonyId: str = Field(min_length=1, max_length=160)
    toTestimonyId: str = Field(min_length=1, max_length=160)
    relation: Literal["corroborates", "contradicts", "contextualizes", "challenges", "duplicates", "related-to"]
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.fromTestimonyId == self.toTestimonyId:
            raise ValueError("testimony relation endpoints must differ")
        return self


class InvestigationDocumentarySnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-documentary-snapshot-request/1.0"]
    includeEntityGraph: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": DOCUMENTARY_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.11.0",
        "release": "Documentary Evidence, Testimony & Statement Analysis Workspace",
        "backendAuthoritative": True,
        "referenceFirst": True,
        "versionedDocuments": True,
        "locatorPreservingExcerpts": True,
        "versionedTestimony": True,
        "humanAssertedContextLinks": True,
        "humanAssertedTestimonyRelations": True,
        "entityGraphOverlay": True,
        "descriptiveDocumentaryAnalysis": True,
        "immutableDocumentarySnapshots": True,
        "automaticCredibilityScoring": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "automaticCulpabilityInference": False,
        "automaticMotiveInference": False,
        "automaticNarrativeSelection": False,
        "supportedDocumentTypes": list(DOCUMENT_TYPES),
        "supportedTestimonyTypes": list(TESTIMONY_TYPES),
        "supportedTestimonyRelations": list(TESTIMONY_RELATIONS),
    }


def _project(db: Session, user_key: str, project_id: str) -> ProjectHead:
    row = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if row is None:
        raise KeyError(project_id)
    return row


def _document(db: Session, user_key: str, document_id: str) -> InvestigationDocumentHead | None:
    return db.get(InvestigationDocumentHead, {"user_key": user_key, "document_id": document_id})


def _testimony(db: Session, user_key: str, testimony_id: str) -> InvestigationTestimonyHead | None:
    return db.get(InvestigationTestimonyHead, {"user_key": user_key, "testimony_id": testimony_id})


def document_metadata(row: InvestigationDocumentHead) -> dict[str, Any]:
    return {
        "schema": DOCUMENT_SCHEMA,
        "documentId": row.document_id,
        "projectId": row.project_id,
        "documentType": row.document_type,
        "title": row.title,
        "description": row.description,
        "sourceRef": row.source_ref,
        "sourceFingerprint": row.source_fingerprint,
        "authority": row.authority,
        "publishedAt": row.published_at,
        "reviewState": row.review_state,
        "revision": row.revision,
        "documentFingerprint": row.document_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _document_fingerprint(payload: InvestigationDocumentRequest, document_id: str, revision: int) -> str:
    return sha256_hex({
        "documentId": document_id,
        "projectId": payload.projectId,
        "documentType": payload.documentType,
        "title": payload.title,
        "description": payload.description,
        "sourceRef": payload.sourceRef,
        "sourceFingerprint": payload.sourceFingerprint,
        "authority": payload.authority,
        "publishedAt": payload.publishedAt,
        "reviewState": payload.reviewState,
        "revision": revision,
        "metadata": payload.metadata,
    })


def store_document(db: Session, user_key: str, payload: InvestigationDocumentRequest) -> tuple[dict[str, Any], bool]:
    _project(db, user_key, payload.projectId)
    document_id = payload.documentId or ("document-" + uuid4().hex[:24])
    row = _document(db, user_key, document_id)
    created = row is None
    if row is not None:
        if row.project_id != payload.projectId:
            raise ValueError("document belongs to a different project")
        if payload.expectedRevision is not None and payload.expectedRevision != row.revision:
            raise RuntimeError("document revision conflict")
        revision = row.revision + 1
    else:
        revision = 1
        row = InvestigationDocumentHead(user_key=user_key, document_id=document_id, project_id=payload.projectId)
        db.add(row)
    fp = _document_fingerprint(payload, document_id, revision)
    row.document_type = payload.documentType
    row.title = payload.title
    row.description = payload.description
    row.source_ref = payload.sourceRef
    row.source_fingerprint = payload.sourceFingerprint
    row.authority = payload.authority
    row.published_at = payload.publishedAt
    row.review_state = payload.reviewState
    row.revision = revision
    row.document_fingerprint = fp
    row.metadata_json = payload.metadata
    db.add(InvestigationDocumentRevision(
        user_key=user_key, document_id=document_id, revision=revision, project_id=payload.projectId,
        document_type=payload.documentType, title=payload.title, description=payload.description,
        source_ref=payload.sourceRef, source_fingerprint=payload.sourceFingerprint, authority=payload.authority,
        published_at=payload.publishedAt, review_state=payload.reviewState, document_fingerprint=fp,
        metadata_json=payload.metadata,
    ))
    db.flush()
    return document_metadata(row), created


def list_documents(db: Session, user_key: str, project_id: str | None = None, document_type: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    q = select(InvestigationDocumentHead).where(InvestigationDocumentHead.user_key == user_key)
    if project_id:
        q = q.where(InvestigationDocumentHead.project_id == project_id)
    if document_type:
        q = q.where(InvestigationDocumentHead.document_type == document_type)
    q = q.order_by(InvestigationDocumentHead.updated_at.desc()).limit(limit)
    return [document_metadata(x) for x in db.scalars(q).all()]


def get_document(db: Session, user_key: str, document_id: str) -> dict[str, Any] | None:
    row = _document(db, user_key, document_id)
    return document_metadata(row) if row else None


def list_document_revisions(db: Session, user_key: str, document_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationDocumentRevision)
        .where(InvestigationDocumentRevision.user_key == user_key, InvestigationDocumentRevision.document_id == document_id)
        .order_by(InvestigationDocumentRevision.revision.desc()).limit(limit)
    ).all()
    return [{
        "documentId": r.document_id, "projectId": r.project_id, "revision": r.revision,
        "documentType": r.document_type, "title": r.title, "description": r.description,
        "sourceRef": r.source_ref, "sourceFingerprint": r.source_fingerprint,
        "authority": r.authority, "publishedAt": r.published_at, "reviewState": r.review_state,
        "documentFingerprint": r.document_fingerprint, "metadata": r.metadata_json or {}, "createdAt": iso(r.created_at),
    } for r in rows]


def create_excerpt(db: Session, user_key: str, payload: InvestigationDocumentExcerptRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    doc = _document(db, user_key, payload.documentId)
    if doc is None or doc.project_id != payload.projectId:
        raise LookupError(payload.documentId)
    fp = sha256_hex({
        "projectId": payload.projectId, "documentId": payload.documentId, "text": payload.text,
        "locator": payload.locator, "documentFingerprint": doc.document_fingerprint,
    })
    existing = db.scalar(select(InvestigationDocumentExcerpt).where(
        InvestigationDocumentExcerpt.user_key == user_key,
        InvestigationDocumentExcerpt.project_id == payload.projectId,
        InvestigationDocumentExcerpt.excerpt_fingerprint == fp,
    ))
    if existing:
        return excerpt_metadata(existing)
    row = InvestigationDocumentExcerpt(
        user_key=user_key, excerpt_id="excerpt-" + uuid4().hex[:24], project_id=payload.projectId,
        document_id=payload.documentId, text=payload.text, locator=payload.locator,
        document_fingerprint=doc.document_fingerprint, excerpt_fingerprint=fp,
        note=payload.note, metadata_json=payload.metadata,
    )
    db.add(row); db.flush()
    return excerpt_metadata(row)


def excerpt_metadata(row: InvestigationDocumentExcerpt) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-document-excerpt/1.0",
        "excerptId": row.excerpt_id, "projectId": row.project_id, "documentId": row.document_id,
        "text": row.text, "locator": row.locator, "documentFingerprint": row.document_fingerprint,
        "excerptFingerprint": row.excerpt_fingerprint, "note": row.note, "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
    }


def list_excerpts(db: Session, user_key: str, project_id: str | None = None, document_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
    q = select(InvestigationDocumentExcerpt).where(InvestigationDocumentExcerpt.user_key == user_key)
    if project_id:
        q = q.where(InvestigationDocumentExcerpt.project_id == project_id)
    if document_id:
        q = q.where(InvestigationDocumentExcerpt.document_id == document_id)
    q = q.order_by(InvestigationDocumentExcerpt.created_at.desc()).limit(limit)
    return [excerpt_metadata(x) for x in db.scalars(q).all()]


def testimony_metadata(row: InvestigationTestimonyHead) -> dict[str, Any]:
    return {
        "schema": TESTIMONY_SCHEMA,
        "testimonyId": row.testimony_id, "projectId": row.project_id, "testimonyType": row.testimony_type,
        "title": row.title, "text": row.text, "speakerEntityId": row.speaker_entity_id,
        "sourceDocumentId": row.source_document_id, "sourceRef": row.source_ref,
        "sourceFingerprint": row.source_fingerprint, "occurredAt": row.occurred_at,
        "reviewState": row.review_state, "revision": row.revision, "testimonyFingerprint": row.testimony_fingerprint,
        "metadata": row.metadata_json or {}, "createdAt": iso(row.created_at), "updatedAt": iso(row.updated_at),
    }


def _testimony_fingerprint(payload: InvestigationTestimonyRequest, testimony_id: str, revision: int, source_fp: str) -> str:
    return sha256_hex({
        "testimonyId": testimony_id, "projectId": payload.projectId, "testimonyType": payload.testimonyType,
        "title": payload.title, "text": payload.text, "speakerEntityId": payload.speakerEntityId,
        "sourceDocumentId": payload.sourceDocumentId, "sourceRef": payload.sourceRef,
        "sourceFingerprint": source_fp, "occurredAt": payload.occurredAt,
        "reviewState": payload.reviewState, "revision": revision, "metadata": payload.metadata,
    })


def store_testimony(db: Session, user_key: str, payload: InvestigationTestimonyRequest) -> tuple[dict[str, Any], bool]:
    _project(db, user_key, payload.projectId)
    source_fp = payload.sourceFingerprint
    if payload.sourceDocumentId:
        doc = _document(db, user_key, payload.sourceDocumentId)
        if doc is None or doc.project_id != payload.projectId:
            raise LookupError(payload.sourceDocumentId)
        source_fp = doc.document_fingerprint
    if payload.speakerEntityId:
        ent = db.get(InvestigationEntityHead, {"user_key": user_key, "entity_id": payload.speakerEntityId})
        if ent is None or ent.project_id != payload.projectId:
            raise LookupError(payload.speakerEntityId)
    testimony_id = payload.testimonyId or ("testimony-" + uuid4().hex[:24])
    row = _testimony(db, user_key, testimony_id)
    created = row is None
    if row is not None:
        if row.project_id != payload.projectId:
            raise ValueError("testimony belongs to a different project")
        if payload.expectedRevision is not None and payload.expectedRevision != row.revision:
            raise RuntimeError("testimony revision conflict")
        revision = row.revision + 1
    else:
        revision = 1
        row = InvestigationTestimonyHead(user_key=user_key, testimony_id=testimony_id, project_id=payload.projectId)
        db.add(row)
    fp = _testimony_fingerprint(payload, testimony_id, revision, source_fp)
    row.testimony_type = payload.testimonyType
    row.title = payload.title
    row.text = payload.text
    row.speaker_entity_id = payload.speakerEntityId
    row.source_document_id = payload.sourceDocumentId
    row.source_ref = payload.sourceRef
    row.source_fingerprint = source_fp
    row.occurred_at = payload.occurredAt
    row.review_state = payload.reviewState
    row.revision = revision
    row.testimony_fingerprint = fp
    row.metadata_json = payload.metadata
    db.add(InvestigationTestimonyRevision(
        user_key=user_key, testimony_id=testimony_id, revision=revision, project_id=payload.projectId,
        testimony_type=payload.testimonyType, title=payload.title, text=payload.text,
        speaker_entity_id=payload.speakerEntityId, source_document_id=payload.sourceDocumentId,
        source_ref=payload.sourceRef, source_fingerprint=source_fp, occurred_at=payload.occurredAt,
        review_state=payload.reviewState, testimony_fingerprint=fp, metadata_json=payload.metadata,
    ))
    db.flush()
    return testimony_metadata(row), created


def list_testimonies(db: Session, user_key: str, project_id: str | None = None, speaker_entity_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    q = select(InvestigationTestimonyHead).where(InvestigationTestimonyHead.user_key == user_key)
    if project_id:
        q = q.where(InvestigationTestimonyHead.project_id == project_id)
    if speaker_entity_id:
        q = q.where(InvestigationTestimonyHead.speaker_entity_id == speaker_entity_id)
    q = q.order_by(InvestigationTestimonyHead.updated_at.desc()).limit(limit)
    return [testimony_metadata(x) for x in db.scalars(q).all()]


def get_testimony(db: Session, user_key: str, testimony_id: str) -> dict[str, Any] | None:
    row = _testimony(db, user_key, testimony_id)
    return testimony_metadata(row) if row else None


def list_testimony_revisions(db: Session, user_key: str, testimony_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationTestimonyRevision)
        .where(InvestigationTestimonyRevision.user_key == user_key, InvestigationTestimonyRevision.testimony_id == testimony_id)
        .order_by(InvestigationTestimonyRevision.revision.desc()).limit(limit)
    ).all()
    return [{
        "testimonyId": r.testimony_id, "projectId": r.project_id, "revision": r.revision,
        "testimonyType": r.testimony_type, "title": r.title, "text": r.text,
        "speakerEntityId": r.speaker_entity_id, "sourceDocumentId": r.source_document_id,
        "sourceRef": r.source_ref, "sourceFingerprint": r.source_fingerprint, "occurredAt": r.occurred_at,
        "reviewState": r.review_state, "testimonyFingerprint": r.testimony_fingerprint,
        "metadata": r.metadata_json or {}, "createdAt": iso(r.created_at),
    } for r in rows]


def _validate_source_object(db: Session, user_key: str, project_id: str, source_kind: str, source_id: str) -> None:
    if source_kind == "document":
        row = _document(db, user_key, source_id)
    elif source_kind == "testimony":
        row = _testimony(db, user_key, source_id)
    else:
        row = db.get(InvestigationDocumentExcerpt, {"user_key": user_key, "excerpt_id": source_id})
    if row is None or row.project_id != project_id:
        raise LookupError(source_id)


def _validate_target(db: Session, user_key: str, project_id: str, target_kind: str, target_ref: str) -> None:
    if target_kind == "statement":
        row = db.get(InvestigationStatementHead, {"user_key": user_key, "statement_id": target_ref})
        if row is None or row.project_id != project_id:
            raise LookupError(target_ref)
    elif target_kind == "event":
        row = db.get(InvestigationEventHead, {"user_key": user_key, "event_id": target_ref})
        if row is None or row.project_id != project_id:
            raise LookupError(target_ref)
    elif target_kind == "entity":
        row = db.get(InvestigationEntityHead, {"user_key": user_key, "entity_id": target_ref})
        if row is None or row.project_id != project_id:
            raise LookupError(target_ref)


def create_context_link(db: Session, user_key: str, payload: InvestigationDocumentaryContextLinkRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    _validate_source_object(db, user_key, payload.projectId, payload.sourceKind, payload.sourceId)
    _validate_target(db, user_key, payload.projectId, payload.targetKind, payload.targetRef)
    fp = sha256_hex({
        "projectId": payload.projectId, "sourceKind": payload.sourceKind, "sourceId": payload.sourceId,
        "targetKind": payload.targetKind, "targetRef": payload.targetRef, "relation": payload.relation,
        "sourceFingerprint": payload.sourceFingerprint, "note": payload.note,
    })
    existing = db.scalar(select(InvestigationDocumentaryContextLink).where(
        InvestigationDocumentaryContextLink.user_key == user_key,
        InvestigationDocumentaryContextLink.project_id == payload.projectId,
        InvestigationDocumentaryContextLink.link_fingerprint == fp,
    ))
    if existing:
        return context_link_metadata(existing)
    row = InvestigationDocumentaryContextLink(
        user_key=user_key, link_id="document-link-" + uuid4().hex[:24], project_id=payload.projectId,
        source_kind=payload.sourceKind, source_id=payload.sourceId, target_kind=payload.targetKind,
        target_ref=payload.targetRef, relation=payload.relation, source_fingerprint=payload.sourceFingerprint,
        note=payload.note, link_fingerprint=fp, metadata_json=payload.metadata,
    )
    db.add(row); db.flush()
    return context_link_metadata(row)


def context_link_metadata(row: InvestigationDocumentaryContextLink) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-documentary-context-link/1.0",
        "linkId": row.link_id, "projectId": row.project_id, "sourceKind": row.source_kind,
        "sourceId": row.source_id, "targetKind": row.target_kind, "targetRef": row.target_ref,
        "relation": row.relation, "sourceFingerprint": row.source_fingerprint, "note": row.note,
        "linkFingerprint": row.link_fingerprint, "metadata": row.metadata_json or {}, "createdAt": iso(row.created_at),
    }


def list_context_links(db: Session, user_key: str, project_id: str | None = None, source_id: str | None = None, target_ref: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
    q = select(InvestigationDocumentaryContextLink).where(InvestigationDocumentaryContextLink.user_key == user_key)
    if project_id:
        q = q.where(InvestigationDocumentaryContextLink.project_id == project_id)
    if source_id:
        q = q.where(InvestigationDocumentaryContextLink.source_id == source_id)
    if target_ref:
        q = q.where(InvestigationDocumentaryContextLink.target_ref == target_ref)
    q = q.order_by(InvestigationDocumentaryContextLink.created_at.desc()).limit(limit)
    return [context_link_metadata(x) for x in db.scalars(q).all()]


def create_testimony_relation(db: Session, user_key: str, payload: InvestigationTestimonyRelationRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    left = _testimony(db, user_key, payload.fromTestimonyId)
    right = _testimony(db, user_key, payload.toTestimonyId)
    if left is None or right is None or left.project_id != payload.projectId or right.project_id != payload.projectId:
        raise LookupError("testimony relation endpoint")
    fp = sha256_hex({
        "projectId": payload.projectId, "from": payload.fromTestimonyId, "to": payload.toTestimonyId,
        "relation": payload.relation, "note": payload.note,
    })
    existing = db.scalar(select(InvestigationTestimonyRelation).where(
        InvestigationTestimonyRelation.user_key == user_key,
        InvestigationTestimonyRelation.project_id == payload.projectId,
        InvestigationTestimonyRelation.relation_fingerprint == fp,
    ))
    if existing:
        return testimony_relation_metadata(existing)
    row = InvestigationTestimonyRelation(
        user_key=user_key, relation_id="testimony-relation-" + uuid4().hex[:24], project_id=payload.projectId,
        from_testimony_id=payload.fromTestimonyId, to_testimony_id=payload.toTestimonyId,
        relation=payload.relation, note=payload.note, relation_fingerprint=fp, metadata_json=payload.metadata,
    )
    db.add(row); db.flush()
    return testimony_relation_metadata(row)


def testimony_relation_metadata(row: InvestigationTestimonyRelation) -> dict[str, Any]:
    return {
        "schema": "sc-workspace-investigation-testimony-relation/1.0",
        "relationId": row.relation_id, "projectId": row.project_id,
        "fromTestimonyId": row.from_testimony_id, "toTestimonyId": row.to_testimony_id,
        "relation": row.relation, "note": row.note, "relationFingerprint": row.relation_fingerprint,
        "metadata": row.metadata_json or {}, "createdAt": iso(row.created_at),
    }


def list_testimony_relations(db: Session, user_key: str, project_id: str | None = None, testimony_id: str | None = None, limit: int = 1000) -> list[dict[str, Any]]:
    q = select(InvestigationTestimonyRelation).where(InvestigationTestimonyRelation.user_key == user_key)
    if project_id:
        q = q.where(InvestigationTestimonyRelation.project_id == project_id)
    if testimony_id:
        q = q.where(
            (InvestigationTestimonyRelation.from_testimony_id == testimony_id) |
            (InvestigationTestimonyRelation.to_testimony_id == testimony_id)
        )
    q = q.order_by(InvestigationTestimonyRelation.created_at.desc()).limit(limit)
    return [testimony_relation_metadata(x) for x in db.scalars(q).all()]


def build_documentary_graph(db: Session, user_key: str, project_id: str, include_entity_graph: bool = True) -> dict[str, Any]:
    _project(db, user_key, project_id)
    documents = list_documents(db, user_key, project_id, limit=5000)
    excerpts = list_excerpts(db, user_key, project_id, limit=10000)
    testimonies = list_testimonies(db, user_key, project_id, limit=5000)
    links = list_context_links(db, user_key, project_id, limit=20000)
    relations = list_testimony_relations(db, user_key, project_id, limit=20000)
    base = build_entity_graph(db, user_key, project_id, True) if include_entity_graph else {"nodes": [], "edges": []}
    nodes = list(base.get("nodes") or [])
    edges = list(base.get("edges") or [])
    nodes += [{"id":"document:"+d["documentId"],"kind":"document","label":d["title"],"documentType":d["documentType"],"fingerprint":d["documentFingerprint"]} for d in documents]
    nodes += [{"id":"excerpt:"+x["excerptId"],"kind":"document-excerpt","label":x["locator"],"documentId":x["documentId"],"fingerprint":x["excerptFingerprint"]} for x in excerpts]
    nodes += [{"id":"testimony:"+t["testimonyId"],"kind":"testimony","label":t["title"],"testimonyType":t["testimonyType"],"fingerprint":t["testimonyFingerprint"]} for t in testimonies]
    edges += [{"id":"document-excerpt:"+x["excerptId"],"from":"document:"+x["documentId"],"to":"excerpt:"+x["excerptId"],"relation":"contains-excerpt","humanAsserted":False} for x in excerpts]
    def node_ref(kind: str, ref: str) -> str:
        if kind in {"document","excerpt","testimony"}:
            return kind + ":" + ref
        return kind + ":" + ref
    edges += [{"id":"documentary-link:"+x["linkId"],"from":node_ref(x["sourceKind"],x["sourceId"]),"to":node_ref(x["targetKind"],x["targetRef"]),"relation":x["relation"],"humanAsserted":True} for x in links]
    edges += [{"id":"testimony-relation:"+x["relationId"],"from":"testimony:"+x["fromTestimonyId"],"to":"testimony:"+x["toTestimonyId"],"relation":x["relation"],"humanAsserted":True} for x in relations]
    fp = sha256_hex({"projectId":project_id,"nodes":nodes,"edges":edges})
    return {
        "schema": DOCUMENTARY_GRAPH_SCHEMA, "projectId": project_id,
        "nodes": nodes, "edges": edges, "documentCount": len(documents), "excerptCount": len(excerpts),
        "testimonyCount": len(testimonies), "contextLinkCount": len(links), "testimonyRelationCount": len(relations),
        "graphFingerprint": fp, "referenceFirst": True, "automaticRelationshipInference": False,
        "automaticCredibilityScoring": False, "automaticNarrativeSelection": False,
    }


def documentary_analysis(db: Session, user_key: str, project_id: str) -> dict[str, Any]:
    _project(db, user_key, project_id)
    documents = list_documents(db, user_key, project_id, limit=5000)
    excerpts = list_excerpts(db, user_key, project_id, limit=10000)
    testimonies = list_testimonies(db, user_key, project_id, limit=5000)
    links = list_context_links(db, user_key, project_id, limit=20000)
    relations = list_testimony_relations(db, user_key, project_id, limit=20000)
    source_ids = {x["sourceId"] for x in links}
    linked_doc_ids = {x["documentId"] for x in excerpts}
    issues: list[dict[str, Any]] = []
    for d in documents:
        if d["documentId"] not in source_ids and d["documentId"] not in linked_doc_ids:
            issues.append({"kind":"document-without-context","documentId":d["documentId"]})
    for t in testimonies:
        if not t["speakerEntityId"]:
            issues.append({"kind":"testimony-without-speaker-entity","testimonyId":t["testimonyId"]})
        if t["testimonyId"] not in source_ids:
            issues.append({"kind":"testimony-without-context-link","testimonyId":t["testimonyId"]})
    counts = {r: 0 for r in TESTIMONY_RELATIONS}
    for r in relations:
        counts[r["relation"]] = counts.get(r["relation"], 0) + 1
    context_counts: dict[str, int] = {}
    for l in links:
        context_counts[l["relation"]] = context_counts.get(l["relation"], 0) + 1
    fp = sha256_hex({"projectId":project_id,"issues":issues,"testimonyRelations":counts,"contextRelations":context_counts})
    return {
        "schema": DOCUMENTARY_ANALYSIS_SCHEMA, "projectId": project_id,
        "documentCount": len(documents), "excerptCount": len(excerpts), "testimonyCount": len(testimonies),
        "contextLinkCount": len(links), "testimonyRelationCount": len(relations),
        "issues": issues, "issueCount": len(issues), "testimonyRelationCounts": counts,
        "contextRelationCounts": context_counts, "analysisFingerprint": fp,
        "descriptiveOnly": True, "automaticCredibilityScoring": False, "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False, "preferredNarrativeSelection": False,
    }


def create_documentary_snapshot(db: Session, user_key: str, project_id: str, payload: InvestigationDocumentarySnapshotRequest) -> dict[str, Any]:
    graph = build_documentary_graph(db, user_key, project_id, payload.includeEntityGraph)
    analysis = documentary_analysis(db, user_key, project_id)
    snapshot_id = "documentary-snapshot-" + uuid4().hex[:24]
    snapshot_fp = sha256_hex({
        "projectId":project_id, "graphFingerprint":graph["graphFingerprint"],
        "analysisFingerprint":analysis["analysisFingerprint"], "includeEntityGraph":payload.includeEntityGraph,
    })
    row = InvestigationDocumentarySnapshot(
        user_key=user_key, snapshot_id=snapshot_id, project_id=project_id,
        graph_fingerprint=graph["graphFingerprint"], analysis_fingerprint=analysis["analysisFingerprint"],
        snapshot_fingerprint=snapshot_fp, document_count=graph["documentCount"], excerpt_count=graph["excerptCount"],
        testimony_count=graph["testimonyCount"], context_link_count=graph["contextLinkCount"],
        testimony_relation_count=graph["testimonyRelationCount"], issue_count=analysis["issueCount"],
        context_json={"includeEntityGraph": payload.includeEntityGraph},
    )
    db.add(row); db.flush()
    return snapshot_metadata(row)


def snapshot_metadata(row: InvestigationDocumentarySnapshot) -> dict[str, Any]:
    return {
        "schema": DOCUMENTARY_SNAPSHOT_SCHEMA, "snapshotId": row.snapshot_id, "projectId": row.project_id,
        "graphFingerprint": row.graph_fingerprint, "analysisFingerprint": row.analysis_fingerprint,
        "snapshotFingerprint": row.snapshot_fingerprint, "documentCount": row.document_count,
        "excerptCount": row.excerpt_count, "testimonyCount": row.testimony_count,
        "contextLinkCount": row.context_link_count, "testimonyRelationCount": row.testimony_relation_count,
        "issueCount": row.issue_count, "context": row.context_json or {}, "createdAt": iso(row.created_at),
    }


def list_documentary_snapshots(db: Session, user_key: str, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(InvestigationDocumentarySnapshot)
        .where(InvestigationDocumentarySnapshot.user_key == user_key, InvestigationDocumentarySnapshot.project_id == project_id)
        .order_by(InvestigationDocumentarySnapshot.created_at.desc()).limit(limit)
    ).all()
    return [snapshot_metadata(x) for x in rows]
