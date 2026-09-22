from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    InvestigationEntityAlias,
    InvestigationEntityContextLink,
    InvestigationEntityHead,
    InvestigationEntityIdentifier,
    InvestigationEntityMatchCandidate,
    InvestigationEntityMatchReview,
    InvestigationEntityRelationship,
    InvestigationEntityResolutionSnapshot,
    InvestigationEntityRevision,
    InvestigationEventHead,
    InvestigationStatementHead,
    ProjectHead,
)
from .investigation_timeline_workspace import build_reconstruction_graph as build_timeline_reconstruction_graph
from .utils import iso, sha256_hex

ENTITY_WORKSPACE_SCHEMA = "sc-workspace-entity-actor-relationship-resolution-workspace/1.0"
ENTITY_SCHEMA = "sc-workspace-investigation-entity/1.0"
ENTITY_REQUEST_SCHEMA = "sc-workspace-investigation-entity-request/1.0"
ENTITY_ALIAS_REQUEST_SCHEMA = "sc-workspace-investigation-entity-alias-request/1.0"
ENTITY_IDENTIFIER_REQUEST_SCHEMA = "sc-workspace-investigation-entity-identifier-request/1.0"
ENTITY_RELATIONSHIP_REQUEST_SCHEMA = "sc-workspace-investigation-entity-relationship-request/1.0"
ENTITY_CONTEXT_LINK_REQUEST_SCHEMA = "sc-workspace-investigation-entity-context-link-request/1.0"
ENTITY_MATCH_CANDIDATE_REQUEST_SCHEMA = "sc-workspace-investigation-entity-match-candidate-request/1.0"
ENTITY_MATCH_REVIEW_REQUEST_SCHEMA = "sc-workspace-investigation-entity-match-review-request/1.0"
ENTITY_GRAPH_SCHEMA = "sc-workspace-investigation-entity-resolution-graph/1.0"
ENTITY_DIAGNOSTICS_SCHEMA = "sc-workspace-investigation-entity-resolution-diagnostics/1.0"
ENTITY_SNAPSHOT_REQUEST_SCHEMA = "sc-workspace-investigation-entity-resolution-snapshot-request/1.0"
ENTITY_SNAPSHOT_SCHEMA = "sc-workspace-investigation-entity-resolution-snapshot/1.0"

ENTITY_TYPES = (
    "person", "organization", "institution", "agency", "company", "location",
    "account", "document", "event", "system", "other",
)
ENTITY_REVIEW_STATES = ("open", "under-review", "documented", "contested", "unresolved", "closed")
ALIAS_TYPES = ("name", "former-name", "abbreviation", "username", "transliteration", "alternate-spelling", "other")
IDENTIFIER_STATUSES = ("observed", "verified", "disputed", "retired", "unknown")
RELATIONSHIP_TYPES = (
    "same-as", "member-of", "employed-by", "owns", "controlled-by", "controls",
    "affiliated-with", "associated-with", "communicates-with", "located-at",
    "participated-in", "authored", "represented-by", "related-to",
)
CONTEXT_TARGET_KINDS = ("statement", "event", "evidence-ref", "document-ref", "scientific-object-ref")
CONTEXT_RELATIONS = ("mentioned-in", "subject-of", "participant-in", "author-of", "source-of", "located-in", "related-to")
MATCH_STATES = ("pending", "confirmed", "rejected", "unresolved")


class InvestigationEntityRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    entityId: str = Field(default="", max_length=160)
    entityType: Literal["person", "organization", "institution", "agency", "company", "location", "account", "document", "event", "system", "other"]
    canonicalName: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=20000)
    reviewState: Literal["open", "under-review", "documented", "contested", "unresolved", "closed"] = "open"
    expectedRevision: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEntityAliasRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-alias-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    entityId: str = Field(min_length=1, max_length=160)
    alias: str = Field(min_length=1, max_length=500)
    aliasType: Literal["name", "former-name", "abbreviation", "username", "transliteration", "alternate-spelling", "other"] = "name"
    language: str = Field(default="", max_length=32)
    sourceRef: str = Field(default="", max_length=1200)
    sourceFingerprint: str = Field(default="", max_length=128)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEntityIdentifierRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-identifier-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    entityId: str = Field(min_length=1, max_length=160)
    namespace: str = Field(min_length=1, max_length=160)
    value: str = Field(min_length=1, max_length=1000)
    status: Literal["observed", "verified", "disputed", "retired", "unknown"] = "observed"
    sourceRef: str = Field(default="", max_length=1200)
    sourceFingerprint: str = Field(default="", max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEntityRelationshipRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-relationship-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    fromEntityId: str = Field(min_length=1, max_length=160)
    toEntityId: str = Field(min_length=1, max_length=160)
    relation: Literal["same-as", "member-of", "employed-by", "owns", "controlled-by", "controls", "affiliated-with", "associated-with", "communicates-with", "located-at", "participated-in", "authored", "represented-by", "related-to"]
    evidenceRef: str = Field(default="", max_length=1200)
    sourceFingerprint: str = Field(default="", max_length=128)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.fromEntityId == self.toEntityId:
            raise ValueError("entity relationship endpoints must differ")
        return self


class InvestigationEntityContextLinkRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-context-link-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    entityId: str = Field(min_length=1, max_length=160)
    targetKind: Literal["statement", "event", "evidence-ref", "document-ref", "scientific-object-ref"]
    targetRef: str = Field(min_length=1, max_length=1200)
    relation: Literal["mentioned-in", "subject-of", "participant-in", "author-of", "source-of", "located-in", "related-to"]
    sourceFingerprint: str = Field(default="", max_length=128)
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def external_refs_are_fingerprinted(self):
        if self.targetKind in {"evidence-ref", "document-ref", "scientific-object-ref"} and not self.sourceFingerprint:
            raise ValueError("external context links require sourceFingerprint")
        return self


class InvestigationEntityMatchCandidateRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-match-candidate-request/1.0"]
    projectId: str = Field(min_length=1, max_length=160)
    leftEntityId: str = Field(min_length=1, max_length=160)
    rightEntityId: str = Field(min_length=1, max_length=160)
    basis: list[str] = Field(default_factory=list, max_length=50)
    signals: dict[str, Any] = Field(default_factory=dict)
    sourceRef: str = Field(default="", max_length=1200)
    sourceFingerprint: str = Field(default="", max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def endpoints_differ(self):
        if self.leftEntityId == self.rightEntityId:
            raise ValueError("match candidate endpoints must differ")
        return self


class InvestigationEntityMatchReviewRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-match-review-request/1.0"]
    reviewState: Literal["pending", "confirmed", "rejected", "unresolved"]
    note: str = Field(default="", max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InvestigationEntityResolutionSnapshotRequest(BaseModel):
    schema: Literal["sc-workspace-investigation-entity-resolution-snapshot-request/1.0"]
    includeTimelineGraph: bool = True


def profile() -> dict[str, Any]:
    return {
        "schema": ENTITY_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.10.0",
        "release": "Entity, Actor & Relationship Resolution Workspace",
        "backendAuthoritative": True,
        "referenceFirst": True,
        "versionedEntityRecords": True,
        "aliasesAndIdentifiers": True,
        "humanAssertedRelationships": True,
        "contextLinks": True,
        "candidateMatchReview": True,
        "immutableResolutionSnapshots": True,
        "timelineGraphOverlay": True,
        "descriptiveResolutionDiagnostics": True,
        "automaticEntityMerge": False,
        "automaticIdentityConfirmation": False,
        "automaticRelationshipInference": False,
        "automaticCulpabilityInference": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
        "supportedEntityTypes": list(ENTITY_TYPES),
        "supportedRelationshipTypes": list(RELATIONSHIP_TYPES),
        "supportedMatchStates": list(MATCH_STATES),
    }


def _project(db: Session, user_key: str, project_id: str) -> ProjectHead:
    row = db.get(ProjectHead, {"user_key": user_key, "project_id": project_id})
    if row is None:
        raise KeyError(project_id)
    return row


def _entity(db: Session, user_key: str, entity_id: str) -> InvestigationEntityHead | None:
    return db.get(InvestigationEntityHead, {"user_key": user_key, "entity_id": entity_id})


def entity_metadata(row: InvestigationEntityHead) -> dict[str, Any]:
    return {
        "schema": ENTITY_SCHEMA,
        "entityId": row.entity_id,
        "projectId": row.project_id,
        "entityType": row.entity_type,
        "canonicalName": row.canonical_name,
        "description": row.description,
        "reviewState": row.review_state,
        "revision": row.revision,
        "entityFingerprint": row.entity_fingerprint,
        "metadata": row.metadata_json or {},
        "createdAt": iso(row.created_at),
        "updatedAt": iso(row.updated_at),
    }


def _entity_fingerprint(payload: InvestigationEntityRequest, entity_id: str, revision: int) -> str:
    return sha256_hex({
        "entityId": entity_id,
        "projectId": payload.projectId,
        "entityType": payload.entityType,
        "canonicalName": payload.canonicalName,
        "description": payload.description,
        "reviewState": payload.reviewState,
        "revision": revision,
        "metadata": payload.metadata,
    })


def store_entity(db: Session, user_key: str, payload: InvestigationEntityRequest) -> tuple[dict[str, Any], bool]:
    _project(db, user_key, payload.projectId)
    entity_id = payload.entityId or ("entity-" + uuid4().hex[:24])
    row = _entity(db, user_key, entity_id)
    created = row is None
    if row is not None:
        if row.project_id != payload.projectId:
            raise ValueError("entity belongs to a different project")
        if payload.expectedRevision is not None and payload.expectedRevision != row.revision:
            raise RuntimeError("entity revision conflict")
        revision = row.revision + 1
    else:
        revision = 1
        row = InvestigationEntityHead(user_key=user_key, entity_id=entity_id, project_id=payload.projectId)
        db.add(row)
    fp = _entity_fingerprint(payload, entity_id, revision)
    row.entity_type = payload.entityType
    row.canonical_name = payload.canonicalName
    row.description = payload.description
    row.review_state = payload.reviewState
    row.revision = revision
    row.entity_fingerprint = fp
    row.metadata_json = payload.metadata
    db.add(InvestigationEntityRevision(
        user_key=user_key, entity_id=entity_id, revision=revision, project_id=payload.projectId,
        entity_type=payload.entityType, canonical_name=payload.canonicalName, description=payload.description,
        review_state=payload.reviewState, entity_fingerprint=fp, metadata_json=payload.metadata,
    ))
    db.commit(); db.refresh(row)
    return entity_metadata(row), created


def list_entities(db: Session, user_key: str, project_id: str | None = None, entity_type: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    q = select(InvestigationEntityHead).where(InvestigationEntityHead.user_key == user_key)
    if project_id:
        q = q.where(InvestigationEntityHead.project_id == project_id)
    if entity_type:
        q = q.where(InvestigationEntityHead.entity_type == entity_type)
    rows = db.scalars(q.order_by(InvestigationEntityHead.updated_at.desc()).limit(limit)).all()
    return [entity_metadata(x) for x in rows]


def get_entity(db: Session, user_key: str, entity_id: str) -> dict[str, Any] | None:
    row = _entity(db, user_key, entity_id)
    return entity_metadata(row) if row else None


def list_entity_revisions(db: Session, user_key: str, entity_id: str, limit: int = 100) -> list[dict[str, Any]]:
    rows = db.scalars(select(InvestigationEntityRevision).where(
        InvestigationEntityRevision.user_key == user_key,
        InvestigationEntityRevision.entity_id == entity_id,
    ).order_by(InvestigationEntityRevision.revision.desc()).limit(limit)).all()
    return [{
        "schema":"sc-workspace-investigation-entity-revision/1.0", "entityId":x.entity_id,
        "projectId":x.project_id, "entityType":x.entity_type, "canonicalName":x.canonical_name,
        "description":x.description, "reviewState":x.review_state, "revision":x.revision,
        "entityFingerprint":x.entity_fingerprint, "metadata":x.metadata_json or {}, "createdAt":iso(x.created_at),
    } for x in rows]


def create_alias(db: Session, user_key: str, payload: InvestigationEntityAliasRequest) -> dict[str, Any]:
    _project(db, user_key, payload.projectId)
    entity = _entity(db, user_key, payload.entityId)
    if entity is None or entity.project_id != payload.projectId:
        raise LookupError(payload.entityId)
    normalized = " ".join(payload.alias.casefold().split())
    fp = sha256_hex({"projectId":payload.projectId,"entityId":payload.entityId,"alias":normalized,"aliasType":payload.aliasType,"language":payload.language,"sourceRef":payload.sourceRef,"sourceFingerprint":payload.sourceFingerprint})
    row = db.scalar(select(InvestigationEntityAlias).where(InvestigationEntityAlias.user_key==user_key, InvestigationEntityAlias.project_id==payload.projectId, InvestigationEntityAlias.alias_fingerprint==fp))
    if row is None:
        row=InvestigationEntityAlias(user_key=user_key,alias_id="entity-alias-"+uuid4().hex[:24],project_id=payload.projectId,entity_id=payload.entityId,alias=payload.alias,normalized_alias=normalized,alias_type=payload.aliasType,language=payload.language,source_ref=payload.sourceRef,source_fingerprint=payload.sourceFingerprint,alias_fingerprint=fp,note=payload.note,metadata_json=payload.metadata)
        db.add(row); db.commit(); db.refresh(row)
    return {"schema":"sc-workspace-investigation-entity-alias/1.0","aliasId":row.alias_id,"projectId":row.project_id,"entityId":row.entity_id,"alias":row.alias,"normalizedAlias":row.normalized_alias,"aliasType":row.alias_type,"language":row.language,"sourceRef":row.source_ref,"sourceFingerprint":row.source_fingerprint,"aliasFingerprint":row.alias_fingerprint,"note":row.note,"metadata":row.metadata_json or {},"createdAt":iso(row.created_at)}


def list_aliases(db: Session, user_key: str, project_id: str | None=None, entity_id: str | None=None, limit: int=1000) -> list[dict[str, Any]]:
    q=select(InvestigationEntityAlias).where(InvestigationEntityAlias.user_key==user_key)
    if project_id: q=q.where(InvestigationEntityAlias.project_id==project_id)
    if entity_id: q=q.where(InvestigationEntityAlias.entity_id==entity_id)
    rows=db.scalars(q.order_by(InvestigationEntityAlias.created_at.desc()).limit(limit)).all()
    return [{"schema":"sc-workspace-investigation-entity-alias/1.0","aliasId":x.alias_id,"projectId":x.project_id,"entityId":x.entity_id,"alias":x.alias,"normalizedAlias":x.normalized_alias,"aliasType":x.alias_type,"language":x.language,"sourceRef":x.source_ref,"sourceFingerprint":x.source_fingerprint,"aliasFingerprint":x.alias_fingerprint,"note":x.note,"metadata":x.metadata_json or {},"createdAt":iso(x.created_at)} for x in rows]


def create_identifier(db: Session, user_key: str, payload: InvestigationEntityIdentifierRequest) -> dict[str, Any]:
    _project(db,user_key,payload.projectId)
    entity=_entity(db,user_key,payload.entityId)
    if entity is None or entity.project_id != payload.projectId: raise LookupError(payload.entityId)
    normalized_value=" ".join(payload.value.strip().split())
    fp=sha256_hex({"projectId":payload.projectId,"entityId":payload.entityId,"namespace":payload.namespace.casefold(),"value":normalized_value,"status":payload.status,"sourceRef":payload.sourceRef,"sourceFingerprint":payload.sourceFingerprint})
    row=db.scalar(select(InvestigationEntityIdentifier).where(InvestigationEntityIdentifier.user_key==user_key, InvestigationEntityIdentifier.project_id==payload.projectId, InvestigationEntityIdentifier.identifier_fingerprint==fp))
    if row is None:
        row=InvestigationEntityIdentifier(user_key=user_key,identifier_id="entity-identifier-"+uuid4().hex[:24],project_id=payload.projectId,entity_id=payload.entityId,namespace=payload.namespace,value=payload.value,normalized_value=normalized_value,status=payload.status,source_ref=payload.sourceRef,source_fingerprint=payload.sourceFingerprint,identifier_fingerprint=fp,metadata_json=payload.metadata)
        db.add(row); db.commit(); db.refresh(row)
    return {"schema":"sc-workspace-investigation-entity-identifier/1.0","identifierId":row.identifier_id,"projectId":row.project_id,"entityId":row.entity_id,"namespace":row.namespace,"value":row.value,"normalizedValue":row.normalized_value,"status":row.status,"sourceRef":row.source_ref,"sourceFingerprint":row.source_fingerprint,"identifierFingerprint":row.identifier_fingerprint,"metadata":row.metadata_json or {},"createdAt":iso(row.created_at)}


def list_identifiers(db: Session,user_key: str,project_id: str | None=None,entity_id: str | None=None,limit: int=1000) -> list[dict[str,Any]]:
    q=select(InvestigationEntityIdentifier).where(InvestigationEntityIdentifier.user_key==user_key)
    if project_id: q=q.where(InvestigationEntityIdentifier.project_id==project_id)
    if entity_id: q=q.where(InvestigationEntityIdentifier.entity_id==entity_id)
    rows=db.scalars(q.order_by(InvestigationEntityIdentifier.created_at.desc()).limit(limit)).all()
    return [{"schema":"sc-workspace-investigation-entity-identifier/1.0","identifierId":x.identifier_id,"projectId":x.project_id,"entityId":x.entity_id,"namespace":x.namespace,"value":x.value,"normalizedValue":x.normalized_value,"status":x.status,"sourceRef":x.source_ref,"sourceFingerprint":x.source_fingerprint,"identifierFingerprint":x.identifier_fingerprint,"metadata":x.metadata_json or {},"createdAt":iso(x.created_at)} for x in rows]


def create_relationship(db: Session,user_key: str,payload: InvestigationEntityRelationshipRequest) -> dict[str,Any]:
    _project(db,user_key,payload.projectId)
    a=_entity(db,user_key,payload.fromEntityId); b=_entity(db,user_key,payload.toEntityId)
    if a is None: raise LookupError(payload.fromEntityId)
    if b is None: raise LookupError(payload.toEntityId)
    if a.project_id!=payload.projectId or b.project_id!=payload.projectId: raise ValueError("relationship entity belongs to a different project")
    fp=sha256_hex({"projectId":payload.projectId,"fromEntityId":payload.fromEntityId,"toEntityId":payload.toEntityId,"relation":payload.relation,"evidenceRef":payload.evidenceRef,"sourceFingerprint":payload.sourceFingerprint,"note":payload.note,"metadata":payload.metadata})
    row=db.scalar(select(InvestigationEntityRelationship).where(InvestigationEntityRelationship.user_key==user_key,InvestigationEntityRelationship.project_id==payload.projectId,InvestigationEntityRelationship.relationship_fingerprint==fp))
    if row is None:
        row=InvestigationEntityRelationship(user_key=user_key,relationship_id="entity-relationship-"+uuid4().hex[:24],project_id=payload.projectId,from_entity_id=payload.fromEntityId,to_entity_id=payload.toEntityId,relation=payload.relation,evidence_ref=payload.evidenceRef,source_fingerprint=payload.sourceFingerprint,note=payload.note,relationship_fingerprint=fp,metadata_json=payload.metadata)
        db.add(row); db.commit(); db.refresh(row)
    return relationship_metadata(row)


def relationship_metadata(row: InvestigationEntityRelationship) -> dict[str,Any]:
    return {"schema":"sc-workspace-investigation-entity-relationship/1.0","relationshipId":row.relationship_id,"projectId":row.project_id,"fromEntityId":row.from_entity_id,"toEntityId":row.to_entity_id,"relation":row.relation,"evidenceRef":row.evidence_ref,"sourceFingerprint":row.source_fingerprint,"note":row.note,"relationshipFingerprint":row.relationship_fingerprint,"metadata":row.metadata_json or {},"humanAsserted":True,"createdAt":iso(row.created_at)}


def list_relationships(db: Session,user_key: str,project_id: str | None=None,entity_id: str | None=None,limit: int=1000) -> list[dict[str,Any]]:
    q=select(InvestigationEntityRelationship).where(InvestigationEntityRelationship.user_key==user_key)
    if project_id: q=q.where(InvestigationEntityRelationship.project_id==project_id)
    if entity_id: q=q.where((InvestigationEntityRelationship.from_entity_id==entity_id)|(InvestigationEntityRelationship.to_entity_id==entity_id))
    rows=db.scalars(q.order_by(InvestigationEntityRelationship.created_at.desc()).limit(limit)).all()
    return [relationship_metadata(x) for x in rows]


def create_context_link(db: Session,user_key: str,payload: InvestigationEntityContextLinkRequest) -> dict[str,Any]:
    _project(db,user_key,payload.projectId)
    entity=_entity(db,user_key,payload.entityId)
    if entity is None or entity.project_id!=payload.projectId: raise LookupError(payload.entityId)
    if payload.targetKind=="statement":
        t=db.get(InvestigationStatementHead,{"user_key":user_key,"statement_id":payload.targetRef})
        if t is None or t.project_id!=payload.projectId: raise LookupError(payload.targetRef)
    elif payload.targetKind=="event":
        t=db.get(InvestigationEventHead,{"user_key":user_key,"event_id":payload.targetRef})
        if t is None or t.project_id!=payload.projectId: raise LookupError(payload.targetRef)
    fp=sha256_hex({"projectId":payload.projectId,"entityId":payload.entityId,"targetKind":payload.targetKind,"targetRef":payload.targetRef,"relation":payload.relation,"sourceFingerprint":payload.sourceFingerprint,"note":payload.note,"metadata":payload.metadata})
    row=db.scalar(select(InvestigationEntityContextLink).where(InvestigationEntityContextLink.user_key==user_key,InvestigationEntityContextLink.project_id==payload.projectId,InvestigationEntityContextLink.link_fingerprint==fp))
    if row is None:
        row=InvestigationEntityContextLink(user_key=user_key,link_id="entity-context-"+uuid4().hex[:24],project_id=payload.projectId,entity_id=payload.entityId,target_kind=payload.targetKind,target_ref=payload.targetRef,relation=payload.relation,source_fingerprint=payload.sourceFingerprint,note=payload.note,link_fingerprint=fp,metadata_json=payload.metadata)
        db.add(row); db.commit(); db.refresh(row)
    return context_link_metadata(row)


def context_link_metadata(row: InvestigationEntityContextLink) -> dict[str,Any]:
    return {"schema":"sc-workspace-investigation-entity-context-link/1.0","linkId":row.link_id,"projectId":row.project_id,"entityId":row.entity_id,"targetKind":row.target_kind,"targetRef":row.target_ref,"relation":row.relation,"sourceFingerprint":row.source_fingerprint,"note":row.note,"linkFingerprint":row.link_fingerprint,"metadata":row.metadata_json or {},"humanAsserted":True,"createdAt":iso(row.created_at)}


def list_context_links(db: Session,user_key: str,project_id: str | None=None,entity_id: str | None=None,limit: int=1000) -> list[dict[str,Any]]:
    q=select(InvestigationEntityContextLink).where(InvestigationEntityContextLink.user_key==user_key)
    if project_id: q=q.where(InvestigationEntityContextLink.project_id==project_id)
    if entity_id: q=q.where(InvestigationEntityContextLink.entity_id==entity_id)
    rows=db.scalars(q.order_by(InvestigationEntityContextLink.created_at.desc()).limit(limit)).all()
    return [context_link_metadata(x) for x in rows]


def create_match_candidate(db: Session,user_key: str,payload: InvestigationEntityMatchCandidateRequest) -> dict[str,Any]:
    _project(db,user_key,payload.projectId)
    left=_entity(db,user_key,payload.leftEntityId); right=_entity(db,user_key,payload.rightEntityId)
    if left is None: raise LookupError(payload.leftEntityId)
    if right is None: raise LookupError(payload.rightEntityId)
    if left.project_id!=payload.projectId or right.project_id!=payload.projectId: raise ValueError("candidate entity belongs to a different project")
    ordered=sorted([payload.leftEntityId,payload.rightEntityId])
    fp=sha256_hex({"projectId":payload.projectId,"entities":ordered,"basis":payload.basis,"signals":payload.signals,"sourceRef":payload.sourceRef,"sourceFingerprint":payload.sourceFingerprint})
    row=db.scalar(select(InvestigationEntityMatchCandidate).where(InvestigationEntityMatchCandidate.user_key==user_key,InvestigationEntityMatchCandidate.project_id==payload.projectId,InvestigationEntityMatchCandidate.candidate_fingerprint==fp))
    if row is None:
        row=InvestigationEntityMatchCandidate(user_key=user_key,candidate_id="entity-match-"+uuid4().hex[:24],project_id=payload.projectId,left_entity_id=ordered[0],right_entity_id=ordered[1],basis_json=payload.basis,signals_json=payload.signals,source_ref=payload.sourceRef,source_fingerprint=payload.sourceFingerprint,review_state="pending",review_note="",candidate_fingerprint=fp,metadata_json=payload.metadata)
        db.add(row); db.commit(); db.refresh(row)
    return match_candidate_metadata(row)


def match_candidate_metadata(row: InvestigationEntityMatchCandidate) -> dict[str,Any]:
    return {"schema":"sc-workspace-investigation-entity-match-candidate/1.0","candidateId":row.candidate_id,"projectId":row.project_id,"leftEntityId":row.left_entity_id,"rightEntityId":row.right_entity_id,"basis":row.basis_json or [],"signals":row.signals_json or {},"sourceRef":row.source_ref,"sourceFingerprint":row.source_fingerprint,"reviewState":row.review_state,"reviewNote":row.review_note,"candidateFingerprint":row.candidate_fingerprint,"metadata":row.metadata_json or {},"automaticMerge":False,"createdAt":iso(row.created_at),"updatedAt":iso(row.updated_at)}


def list_match_candidates(db: Session,user_key: str,project_id: str | None=None,review_state: str | None=None,limit: int=1000) -> list[dict[str,Any]]:
    q=select(InvestigationEntityMatchCandidate).where(InvestigationEntityMatchCandidate.user_key==user_key)
    if project_id: q=q.where(InvestigationEntityMatchCandidate.project_id==project_id)
    if review_state: q=q.where(InvestigationEntityMatchCandidate.review_state==review_state)
    rows=db.scalars(q.order_by(InvestigationEntityMatchCandidate.updated_at.desc()).limit(limit)).all()
    return [match_candidate_metadata(x) for x in rows]


def review_match_candidate(db: Session,user_key: str,candidate_id: str,payload: InvestigationEntityMatchReviewRequest) -> dict[str,Any]:
    row=db.get(InvestigationEntityMatchCandidate,{"user_key":user_key,"candidate_id":candidate_id})
    if row is None: raise LookupError(candidate_id)
    row.review_state=payload.reviewState; row.review_note=payload.note
    review=InvestigationEntityMatchReview(user_key=user_key,review_id="entity-match-review-"+uuid4().hex[:24],candidate_id=candidate_id,project_id=row.project_id,review_state=payload.reviewState,note=payload.note,review_fingerprint=sha256_hex({"candidateId":candidate_id,"reviewState":payload.reviewState,"note":payload.note,"metadata":payload.metadata}),metadata_json=payload.metadata)
    db.add(review); db.commit(); db.refresh(row)
    out=match_candidate_metadata(row)
    out["review"]={"reviewId":review.review_id,"reviewState":review.review_state,"note":review.note,"reviewFingerprint":review.review_fingerprint,"metadata":review.metadata_json or {},"createdAt":iso(review.created_at)}
    return out


def build_entity_graph(db: Session,user_key: str,project_id: str,include_timeline_graph: bool=True) -> dict[str,Any]:
    _project(db,user_key,project_id)
    if include_timeline_graph:
        base=build_timeline_reconstruction_graph(db,user_key,project_id,True)
        nodes=list(base.get("nodes") or []); edges=list(base.get("edges") or [])
    else:
        nodes=[]; edges=[]
    entities=list_entities(db,user_key,project_id,None,5000)
    aliases=list_aliases(db,user_key,project_id,None,5000)
    identifiers=list_identifiers(db,user_key,project_id,None,5000)
    relationships=list_relationships(db,user_key,project_id,None,5000)
    context_links=list_context_links(db,user_key,project_id,None,5000)
    alias_by_entity: dict[str,list[str]]={}
    identifier_by_entity: dict[str,list[dict[str,str]]]={}
    for a in aliases: alias_by_entity.setdefault(a["entityId"],[]).append(a["alias"])
    for i in identifiers: identifier_by_entity.setdefault(i["entityId"],[]).append({"namespace":i["namespace"],"value":i["value"],"status":i["status"]})
    for e in entities:
        nodes.append({"id":"workspace:investigation-entity:"+e["entityId"],"kind":"investigation-entity","entityId":e["entityId"],"entityType":e["entityType"],"label":e["canonicalName"],"reviewState":e["reviewState"],"fingerprint":e["entityFingerprint"],"aliases":sorted(alias_by_entity.get(e["entityId"],[])),"identifiers":identifier_by_entity.get(e["entityId"],[])})
    for r in relationships:
        edges.append({"source":"workspace:investigation-entity:"+r["fromEntityId"],"target":"workspace:investigation-entity:"+r["toEntityId"],"relation":"entity-"+r["relation"],"humanAsserted":True,"fingerprint":r["relationshipFingerprint"],"evidenceRef":r["evidenceRef"]})
    for link in context_links:
        if link["targetKind"]=="statement": target="workspace:investigation-statement:"+link["targetRef"]
        elif link["targetKind"]=="event": target="workspace:investigation-event:"+link["targetRef"]
        else: target="external:"+link["targetKind"]+":"+sha256_hex(link["targetRef"])[:24]
        edges.append({"source":"workspace:investigation-entity:"+link["entityId"],"target":target,"relation":"entity-context-"+link["relation"],"humanAsserted":True,"fingerprint":link["linkFingerprint"],"targetRef":link["targetRef"]})
    nodes=sorted(nodes,key=lambda x:str(x.get("id") or "")); edges=sorted(edges,key=lambda x:(str(x.get("source") or ""),str(x.get("target") or ""),str(x.get("relation") or "")))
    out={"schema":ENTITY_GRAPH_SCHEMA,"projectId":project_id,"nodes":nodes,"edges":edges,"entityCount":len(entities),"relationshipCount":len(relationships),"contextLinkCount":len(context_links),"automaticRelationshipInference":False,"automaticIdentityConfirmation":False}
    out["graphFingerprint"]=sha256_hex(out)
    return out


def resolution_diagnostics(db: Session,user_key: str,project_id: str) -> dict[str,Any]:
    _project(db,user_key,project_id)
    aliases=list_aliases(db,user_key,project_id,None,5000); identifiers=list_identifiers(db,user_key,project_id,None,5000); candidates=list_match_candidates(db,user_key,project_id,None,5000); relationships=list_relationships(db,user_key,project_id,None,5000)
    alias_map: dict[str,set[str]]={}; identifier_map: dict[tuple[str,str],set[str]]={}
    for a in aliases: alias_map.setdefault(a["normalizedAlias"],set()).add(a["entityId"])
    for i in identifiers: identifier_map.setdefault((i["namespace"].casefold(),i["normalizedValue"]),set()).add(i["entityId"])
    alias_collisions=[{"normalizedAlias":k,"entityIds":sorted(v),"count":len(v)} for k,v in sorted(alias_map.items()) if k and len(v)>1]
    identifier_collisions=[{"namespace":k[0],"normalizedValue":k[1],"entityIds":sorted(v),"count":len(v)} for k,v in sorted(identifier_map.items()) if len(v)>1]
    explicit_same_as={tuple(sorted([r["fromEntityId"],r["toEntityId"]])) for r in relationships if r["relation"]=="same-as"}
    confirmed_without_same_as=[]
    for c in candidates:
        pair=tuple(sorted([c["leftEntityId"],c["rightEntityId"]]))
        if c["reviewState"]=="confirmed" and pair not in explicit_same_as: confirmed_without_same_as.append(c["candidateId"])
    issues=[]
    if alias_collisions: issues.append({"code":"shared-aliases","count":len(alias_collisions)})
    if identifier_collisions: issues.append({"code":"shared-identifiers","count":len(identifier_collisions)})
    pending=[c["candidateId"] for c in candidates if c["reviewState"] in {"pending","unresolved"}]
    if pending: issues.append({"code":"unresolved-match-candidates","count":len(pending)})
    if confirmed_without_same_as: issues.append({"code":"confirmed-candidates-without-explicit-same-as","count":len(confirmed_without_same_as)})
    out={"schema":ENTITY_DIAGNOSTICS_SCHEMA,"projectId":project_id,"issues":issues,"count":len(issues),"aliasCollisions":alias_collisions,"identifierCollisions":identifier_collisions,"unresolvedCandidateIds":pending,"confirmedWithoutExplicitSameAs":confirmed_without_same_as,"automaticEntityMerge":False,"automaticIdentityConfirmation":False,"automaticResolution":False,"diagnosticsAreDescriptive":True}
    out["diagnosticsFingerprint"]=sha256_hex(out)
    return out


def create_resolution_snapshot(db: Session,user_key: str,project_id: str,payload: InvestigationEntityResolutionSnapshotRequest) -> dict[str,Any]:
    graph=build_entity_graph(db,user_key,project_id,payload.includeTimelineGraph); diagnostics=resolution_diagnostics(db,user_key,project_id); candidates=list_match_candidates(db,user_key,project_id,None,5000)
    context={"graph":graph,"diagnostics":diagnostics,"candidateStates":{"pending":sum(1 for c in candidates if c["reviewState"]=="pending"),"confirmed":sum(1 for c in candidates if c["reviewState"]=="confirmed"),"rejected":sum(1 for c in candidates if c["reviewState"]=="rejected"),"unresolved":sum(1 for c in candidates if c["reviewState"]=="unresolved")}}
    fp=sha256_hex(context)
    row=InvestigationEntityResolutionSnapshot(user_key=user_key,snapshot_id="entity-resolution-"+uuid4().hex[:24],project_id=project_id,graph_fingerprint=graph["graphFingerprint"],diagnostics_fingerprint=diagnostics["diagnosticsFingerprint"],snapshot_fingerprint=fp,entity_count=int(graph["entityCount"]),relationship_count=int(graph["relationshipCount"]),context_link_count=int(graph["contextLinkCount"]),match_candidate_count=len(candidates),unresolved_match_count=len(diagnostics["unresolvedCandidateIds"]),context_json=context)
    db.add(row); db.commit(); db.refresh(row)
    return snapshot_metadata(row)


def snapshot_metadata(row: InvestigationEntityResolutionSnapshot) -> dict[str,Any]:
    return {"schema":ENTITY_SNAPSHOT_SCHEMA,"snapshotId":row.snapshot_id,"projectId":row.project_id,"graphFingerprint":row.graph_fingerprint,"diagnosticsFingerprint":row.diagnostics_fingerprint,"snapshotFingerprint":row.snapshot_fingerprint,"entityCount":row.entity_count,"relationshipCount":row.relationship_count,"contextLinkCount":row.context_link_count,"matchCandidateCount":row.match_candidate_count,"unresolvedMatchCount":row.unresolved_match_count,"createdAt":iso(row.created_at)}


def list_resolution_snapshots(db: Session,user_key: str,project_id: str,limit: int=100) -> list[dict[str,Any]]:
    rows=db.scalars(select(InvestigationEntityResolutionSnapshot).where(InvestigationEntityResolutionSnapshot.user_key==user_key,InvestigationEntityResolutionSnapshot.project_id==project_id).order_by(InvestigationEntityResolutionSnapshot.created_at.desc()).limit(limit)).all()
    return [snapshot_metadata(x) for x in rows]
