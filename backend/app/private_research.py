"""WXR-08.1.1. Session-only, existing-project-backed private research records.

This module deliberately does NOT accept service identities or X-SC-User-ID.
Apply the bundled SQL migration before enabling the router.
"""
from __future__ import annotations
import base64
import binascii
import hashlib
import os
import secrets
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import get_settings
from .db import session_scope
from .repository import get_project
from .session_auth import session_payload_from_request

router = APIRouter(prefix="/v1/private-research", tags=["private-research"])
MAX_BYTES = 25 * 1024 * 1024


def session_owner(request: Request) -> str:
    """Only an existing, validated, signed Workspace session establishes ownership."""
    payload = session_payload_from_request(request)
    if not payload:
        raise HTTPException(401, "A valid Workspace browser session is required.")
    user_key = str(payload.get("sub") or "").strip()
    if not user_key or len(user_key) > 128:
        raise HTTPException(401, "Invalid Workspace session subject.")
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        # Workspace uses SameSite=Lax cookies; additionally restrict unsafe requests to the
        # configured same-origin frontend. Missing Origin/Referer is fail-closed.
        allowed = {v.strip().rstrip("/") for v in get_settings().cors_allowed_origins.split(",") if v.strip()}
        origin = (request.headers.get("origin") or "").rstrip("/")
        if origin not in allowed:
            raise HTTPException(403, "Private Research requires an approved browser origin.")
    return user_key


def db_session():
    db = session_scope()
    try:
        yield db
    finally:
        db.close()


def workspace_project(db: Session, owner: str, project_id: str):
    if not get_project(db, owner, project_id):
        raise HTTPException(404, "Research project not found.")


def research_project(db: Session, owner: str, project_id: str):
    workspace_project(db, owner, project_id)
    row = db.execute(text("SELECT title FROM workspace_private_research_projects WHERE user_key=:u AND project_id=:p"), {"u":owner,"p":project_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Private Research project not found.")
    return row


class ResearchCreate(BaseModel):
    projectId: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=500)

class BranchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)

class ArtifactCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    mediaType: str = Field(default="application/octet-stream", max_length=160)
    contentBase64: str
    evidenceStatus: str = Field(default="unreviewed", max_length=80)


def private_root() -> Path:
    root = (Path(get_settings().object_storage_root) / "private-research").resolve()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    return root


def private_blob(content: bytes) -> tuple[str, int]:
    digest = hashlib.sha256(content).hexdigest()
    root = private_root()
    directory = root / digest[:2]
    directory.mkdir(mode=0o700, exist_ok=True)
    path = directory / digest
    if not path.exists():
        import tempfile
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as f:
            tmp = Path(f.name)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        try:
            # Atomic create without ever replacing existing blob.
            os.link(tmp, path)
        except FileExistsError:
            pass
        finally:
            tmp.unlink(missing_ok=True)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise HTTPException(503, "Private artifact integrity failure.")
    return digest, len(content)


def branch_exists(db: Session, owner: str, project_id: str, branch_id: str):
    row = db.execute(text("SELECT 1 FROM workspace_private_research_branches WHERE user_key=:u AND project_id=:p AND branch_id=:b"),{"u":owner,"p":project_id,"b":branch_id}).first()
    if not row:
        raise HTTPException(404, "Research branch not found.")

@router.post("/projects", status_code=201)
def attach_project(payload: ResearchCreate, owner: str = Depends(session_owner), db: Session = Depends(db_session)):
    workspace_project(db, owner, payload.projectId)
    db.execute(text("INSERT INTO workspace_private_research_projects(user_key,project_id,title) VALUES (:u,:p,:t) ON CONFLICT (user_key,project_id) DO NOTHING"),{"u":owner,"p":payload.projectId,"t":payload.title})
    db.commit()
    return {"projectId":payload.projectId,"status":"attached-or-existing"}

@router.get("/projects")
def list_research(owner: str = Depends(session_owner), db: Session = Depends(db_session)):
    rows = db.execute(text("SELECT r.project_id,r.title FROM workspace_private_research_projects r JOIN workspace_project_heads p ON p.user_key=r.user_key AND p.project_id=r.project_id WHERE r.user_key=:u ORDER BY r.created_at DESC"),{"u":owner}).mappings()
    return {"projects":[dict(r) for r in rows]}

@router.post("/projects/{project_id}/branches", status_code=201)
def create_branch(project_id: str, payload: BranchCreate, owner: str=Depends(session_owner), db:Session=Depends(db_session)):
    research_project(db,owner,project_id)
    branch_id=uuid4().hex
    db.execute(text("INSERT INTO workspace_private_research_branches(user_key,project_id,branch_id,name) VALUES (:u,:p,:b,:n)"),{"u":owner,"p":project_id,"b":branch_id,"n":payload.name})
    db.commit()
    return {"branchId":branch_id,"name":payload.name}

@router.get("/projects/{project_id}/branches")
def list_branches(project_id:str,owner:str=Depends(session_owner),db:Session=Depends(db_session)):
    research_project(db,owner,project_id)
    rows=db.execute(text("SELECT branch_id,name FROM workspace_private_research_branches WHERE user_key=:u AND project_id=:p ORDER BY created_at"),{"u":owner,"p":project_id}).mappings()
    return {"branches":[dict(r) for r in rows]}

@router.post("/projects/{project_id}/branches/{branch_id}/artifacts", status_code=201)
def add_artifact(project_id:str,branch_id:str,payload:ArtifactCreate,owner:str=Depends(session_owner),db:Session=Depends(db_session)):
    research_project(db,owner,project_id)
    branch_exists(db,owner,project_id,branch_id)
    # Check length before decoding to avoid unbounded memory growth.
    if len(payload.contentBase64)> 4 * ((MAX_BYTES + 2)//3) + 4:
        raise HTTPException(413,"Private artifact exceeds size limit.")
    try:
        content=base64.b64decode(payload.contentBase64,validate=True)
    except (ValueError,binascii.Error):
        raise HTTPException(400,"Invalid artifact base64.")
    if len(content)>MAX_BYTES:
        raise HTTPException(413,"Private artifact exceeds size limit.")
    artifact_id=uuid4().hex
    digest, size=private_blob(content)
    db.execute(text("INSERT INTO workspace_private_research_artifacts(user_key,project_id,branch_id,artifact_id,filename,media_type,sha256,byte_count,evidence_status) VALUES (:u,:p,:b,:a,:f,:m,:h,:s,:e)"),{"u":owner,"p":project_id,"b":branch_id,"a":artifact_id,"f":payload.filename,"m":payload.mediaType,"h":digest,"s":size,"e":payload.evidenceStatus})
    db.commit()
    return {"artifactId":artifact_id,"sha256":digest,"bytes":size,"immutable":True,"evidenceStatus":payload.evidenceStatus}

@router.get("/projects/{project_id}/branches/{branch_id}/artifacts")
def list_branch_artifacts(project_id:str,branch_id:str,owner:str=Depends(session_owner),db:Session=Depends(db_session)):
    research_project(db,owner,project_id)
    branch_exists(db,owner,project_id,branch_id)
    rows=db.execute(text("SELECT artifact_id,filename,media_type,sha256,byte_count,evidence_status,created_at FROM workspace_private_research_artifacts WHERE user_key=:u AND project_id=:p AND branch_id=:b ORDER BY created_at"),{"u":owner,"p":project_id,"b":branch_id}).mappings()
    return {"artifacts":[dict(r) for r in rows]}

@router.get("/projects/{project_id}/artifacts/{artifact_id}")
def download_artifact(project_id:str,artifact_id:str,owner:str=Depends(session_owner),db:Session=Depends(db_session)):
    from fastapi.responses import Response
    research_project(db,owner,project_id)
    row=db.execute(text("SELECT filename,media_type,sha256,byte_count FROM workspace_private_research_artifacts WHERE user_key=:u AND project_id=:p AND artifact_id=:a"),{"u":owner,"p":project_id,"a":artifact_id}).mappings().first()
    if row is None: raise HTTPException(404,"Private artifact not found.")
    path=private_root()/row["sha256"][:2]/row["sha256"]
    if not path.is_file(): raise HTTPException(503,"Private artifact blob missing.")
    content=path.read_bytes()
    if len(content)!=row["byte_count"] or not secrets.compare_digest(hashlib.sha256(content).hexdigest(),row["sha256"]):
        raise HTTPException(503,"Private artifact integrity failure.")
    # Force attachment and eliminate content sniffing and cache persistence.
    from urllib.parse import quote
    return Response(content,media_type="application/octet-stream",headers={"Content-Disposition":f"attachment; filename*=UTF-8''{quote(row['filename'])}","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})
