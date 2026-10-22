"""WXR-09.3 end-to-end signed-browser persistence regression, synthetic data only."""
import base64
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import wxr_private_projects as research, repository, object_store, session_auth
from app.models import Base, ProjectHead, ProjectRevision, ArtifactHead, ArtifactRevision, DomainMutationReceipt

@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kw):
    return "JSON"

@pytest.fixture
def env(tmp_path, monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        ProjectHead.__table__, ProjectRevision.__table__, ArtifactHead.__table__,
        ArtifactRevision.__table__, DomainMutationReceipt.__table__,
    ])
    settings = SimpleNamespace(
        max_project_bytes=10**6, max_account_bytes=10**7, max_projects_per_account=100,
        max_artifact_bytes=10**6, max_artifact_account_bytes=10**7,
        max_artifacts_per_account=100, object_storage_root=str(tmp_path / "blobs"),
    )
    monkeypatch.setattr(repository, "get_settings", lambda: settings)
    monkeypatch.setattr(object_store, "get_settings", lambda: settings)
    monkeypatch.setattr(research, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(session_auth, "get_settings", lambda: SimpleNamespace(
        session_signing_secret="synthetic-private-test-only",
        service_token="", session_cookie_name="sc_workspace_session",
        session_issuer="synthetic", session_audience="workspace.sustainablecatalyst.com",
        session_ttl_seconds=3600,
    ))
    monkeypatch.setattr(__import__("app.config", fromlist=["get_settings"]), "get_settings", lambda: settings)
    app = FastAPI()
    app.include_router(research.router)
    client = TestClient(app, base_url="https://workspace.sustainablecatalyst.com")
    client.cookies.set("sc_workspace_session", session_auth.issue_session_token("alice"))
    return client, engine, settings

ORIGIN = {"Origin": "https://workspace.sustainablecatalyst.com"}
ROOT = "/v1/private-research/projects"

def test_complete_save_logout_relogin_reopen_download(env):
    client, engine, _ = env
    created = client.post(ROOT, json={"title": "Wexford ERW"}, headers=ORIGIN)
    assert created.status_code == 201, created.text
    pid = created.json()["projectId"]
    data = b'{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}'
    uploaded = client.post(f"{ROOT}/{pid}/files", headers=ORIGIN, json={
        "filename": "analysis.ipynb",
        "contentBase64": base64.b64encode(data).decode("ascii")
    })
    assert uploaded.status_code == 201, uploaded.text
    aid = uploaded.json()["artifactId"]
    assert uploaded.json()["sha256"] == hashlib.sha256(data).hexdigest()
    client.cookies.clear()
    assert client.get(f"{ROOT}/{pid}").status_code == 401
    client.cookies.set("sc_workspace_session", session_auth.issue_session_token("alice"))
    found = client.get(f"{ROOT}/{pid}")
    assert found.status_code == 200
    assert found.json()["files"][0]["artifactId"] == aid
    downloaded = client.get(f"{ROOT}/{pid}/files/{aid}/download")
    assert downloaded.status_code == 200
    assert downloaded.content == data
    assert downloaded.headers["x-research-sha256"] == hashlib.sha256(data).hexdigest()
    # New DB session simulates a server-side request after browser refresh/restart.
    with Session(engine) as db:
        assert repository.get_project(db, "alice", pid) is not None
        assert object_store.get_artifact(db, "alice", aid) is not None

def test_cross_user_and_duplicate_denial(env):
    client, _, _ = env
    pid = client.post(ROOT, json={"title": "Wexford"}, headers=ORIGIN).json()["projectId"]
    payload = {"filename": "source.pdf", "contentBase64": base64.b64encode(b"%PDF-1.7 test").decode()}
    item = client.post(f"{ROOT}/{pid}/files", json=payload, headers=ORIGIN)
    assert item.status_code == 201
    assert client.post(f"{ROOT}/{pid}/files", json=payload, headers=ORIGIN).status_code == 409
    aid = item.json()["artifactId"]
    client.cookies.clear()
    client.cookies.set("sc_workspace_session", session_auth.issue_session_token("bob"))
    assert client.get(f"{ROOT}/{pid}").status_code == 404
    assert client.get(f"{ROOT}/{pid}/files/{aid}/download").status_code == 404
    assert client.post(f"{ROOT}/{pid}/files", json=payload, headers=ORIGIN).status_code == 404

def test_origin_filename_and_session_guards(env):
    client, _, _ = env
    assert client.post(ROOT, json={"title": "Unsafe"}).status_code == 403
    assert client.post(ROOT, json={"title": "Safe"}, headers=ORIGIN).status_code == 201
    pid = client.get(ROOT).json()["projects"][0]["projectId"]
    base = {"contentBase64": base64.b64encode(b"content").decode()}
    for name in ["../escape.pdf", "folder/file.pdf", "test.exe", "bad\\name.csv"]:
        assert client.post(f"{ROOT}/{pid}/files", json={**base, "filename": name}, headers=ORIGIN).status_code in (400, 415)
    client.cookies.clear()
    assert client.get(ROOT).status_code == 401
    assert client.get(ROOT+"/ui").status_code == 401
    assert client.post(ROOT, json={"title": "Denied"}, headers=ORIGIN).status_code == 401
