"""RH-PUB-01 — the original manuscript behind a Studio publication, as a signed record for Research.

A Studio publication imported from a Word file keeps that file untouched in the project's private store. To let Research
cite the original (its submission rule needs at least one pinned run, figure or source), the person signed in to
Sustainable Catalyst asks this backend, which alone holds the Workspace Research key, to sign what it has verified
itself: their own project and saved Studio revision, the original's bytes re-read and re-hashed from the private store,
and their rights declaration. Research verifies the signature and keeps the record as private provenance; the bytes
never leave Workspace and nothing here makes anything public.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .db import session_scope
from .research_access import accepted_methods
from .research_exports import AUDIENCE, ISSUER, _signing_key, sign_document
from .security import ServiceIdentity, require_service_identity

SOURCE_SCHEMA = "sc-workspace-research-source/1.0"
MEDIA_TYPES = {".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
               ".pdf": "application/pdf"}
router = APIRouter(prefix="/v1/research-access", tags=["RH-PUB-01 Research sources"])


class SourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    projectId: str = Field(min_length=1, max_length=160)
    documentId: str = Field(min_length=1, max_length=160)
    studioRevision: int = Field(ge=1)
    rightsBasis: Literal["author-owned", "licensed", "public-domain", "other"]
    rightsHolder: str = Field(min_length=1, max_length=300)
    rightsStatement: str = Field(min_length=20, max_length=2000)


@router.post("/source-documents")
def source_document_route(body: SourceRequest, identity: ServiceIdentity = Depends(require_service_identity)):
    return issue_source_record(identity, body)


def issue_source_record(identity: ServiceIdentity, body: SourceRequest) -> dict:
    """The signed source record for ``identity``'s own saved Studio revision; also used in-process by the Studio."""
    from .reporting_publication import _original_asset, _saved
    if identity.authentication_method not in accepted_methods():
        raise HTTPException(status_code=403, detail={
            "code": "sc-identity-required", "message": "Sign in to Sustainable Catalyst to use Research."})
    if not body.rightsStatement.strip() or not body.rightsHolder.strip():
        raise HTTPException(422, "Describe who holds the rights and on what basis.")
    _signing_key()
    with session_scope() as db:
        _, pub = _saved(db, identity.user_key, body.projectId, body.documentId, body.studioRevision)
        source = pub.get("source") or {}
        if not source.get("artifactId"):
            raise HTTPException(409, "This publication was not imported from an original file.")
        meta, raw = _original_asset(db, identity.user_key, body.projectId, source["artifactId"])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != meta["sha256"] or len(raw) != meta["bytes"] or digest != source.get("sha256"):
        raise HTTPException(409, "The original file no longer matches the one this publication was imported from.")
    if hashlib.sha256(pub["markdown"].encode()).hexdigest() != pub["markdownSHA256"]:
        raise HTTPException(409, "This Studio revision does not match its recorded hash.")
    suffix = "." + meta["filename"].rsplit(".", 1)[-1].lower() if "." in meta["filename"] else ""
    if suffix not in MEDIA_TYPES:
        raise HTTPException(422, "Only a Word (.docx) or PDF original can be registered with Research.")
    return sign_document(SOURCE_SCHEMA, {
        "schema": SOURCE_SCHEMA, "issuer": ISSUER, "audience": AUDIENCE,
        "ownerScope": f"workspace-user:{identity.user_key}", "projectId": body.projectId,
        "title": f"Original manuscript: {pub['title']}"[:300],
        "original": {"artifactId": meta["artifactId"], "sha256": digest, "byteCount": len(raw),
                     "mediaType": MEDIA_TYPES[suffix], "filename": meta["filename"]},
        "studioRevision": {"documentId": pub["documentId"], "revision": pub["revision"],
                           "markdownSHA256": pub["markdownSHA256"]},
        "rights": {"basis": body.rightsBasis, "holder": body.rightsHolder.strip(),
                   "statement": body.rightsStatement.strip()},
        "issuedAt": datetime.now(timezone.utc).isoformat()})
