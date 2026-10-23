"""WXR-09.3 end-to-end signed-browser persistence regression, synthetic data only."""
import base64
import hashlib
import os
import shutil
import sqlite3
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import wxr_private_projects as research, repository, object_store, session_auth
from app import erw_identity_bridge
from app.schemas import ArtifactStoreRequest
from app.models import Base, ProjectHead, ProjectRevision, ArtifactHead, ArtifactRevision, DomainMutationReceipt

@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kw):
    return "JSON"

@pytest.fixture
def env(tmp_path, monkeypatch):
    engine = create_engine("sqlite:///" + str(tmp_path / "research.sqlite"), connect_args={"check_same_thread": False})
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
    app.include_router(erw_identity_bridge.router)
    app.include_router(research.router)
    client = TestClient(app, base_url="https://workspace.sustainablecatalyst.com")
    client.cookies.set("sc_workspace_session", session_auth.issue_session_token("alice"))
    return client, engine, settings

ORIGIN = {"Origin": "https://workspace.sustainablecatalyst.com"}
ROOT = "/v1/private-research/persistent-projects"

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
    # A new DB session checks persistence independently of the original request.
    with Session(engine) as db:
        assert repository.get_project(db, "alice", pid) is not None
        assert object_store.get_artifact(db, "alice", aid) is not None


def test_existing_erw_login_creates_private_project(env, monkeypatch):
    client, _, _ = env
    client.cookies.clear()
    monkeypatch.setattr(erw_identity_bridge, "ERW_BASE", "http://synthetic-erw-internal")
    monkeypatch.setattr(erw_identity_bridge, "_rate_limit", lambda *_: None)
    monkeypatch.setattr(erw_identity_bridge, "_post_json", lambda *_: {"token": "synthetic-token-long-enough", "identityId": "known-owner"})
    monkeypatch.setattr(erw_identity_bridge, "_get_json", lambda *_: {
        "ok": True, "authenticated": True, "anonymous": False, "identityId": "known-owner",
    })
    login = client.post("/v1/private-research/auth/login", json={
        "username": "existing-account", "password": "synthetic-password",
    }, headers={**ORIGIN, "X-WXR-Login": "1"})
    assert login.status_code == 200, login.text
    assert "sc_workspace_session" in client.cookies
    created = client.post(ROOT, json={"title": "Wexford ERW"}, headers=ORIGIN)
    assert created.status_code == 201, created.text
    assert client.get(ROOT).json()["projects"][0]["projectId"] == created.json()["projectId"]


@pytest.mark.parametrize("filename,data", [
    ("paper.pdf", b"%PDF-1.7 synthetic"),
    ("report.docx", b"PK synthetic docx"),
    ("analysis.ipynb", b'{"cells":[],"nbformat":4,"nbformat_minor":5}'),
    ("figure.svg", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"),
    ("figure.png", b"\x89PNG\r\n\x1a\nsynthetic"),
    ("data.csv", b"x,y\n1,2\n"),
    ("manifest.json", b'{"synthetic":true}'),
])
def test_supported_research_files_round_trip(env, filename, data):
    client, _, _ = env
    pid = client.post(ROOT, json={"title": "Wexford"}, headers=ORIGIN).json()["projectId"]
    item = client.post(f"{ROOT}/{pid}/files", json={
        "filename": filename, "contentBase64": base64.b64encode(data).decode(),
    }, headers=ORIGIN)
    assert item.status_code == 201, item.text
    assert item.json()["projectId"] == pid
    assert item.json()["sha256"] == hashlib.sha256(data).hexdigest()
    downloaded = client.get(f"{ROOT}/{pid}/files/{item.json()['artifactId']}/download")
    assert downloaded.status_code == 200
    assert downloaded.content == data
    assert downloaded.headers["x-research-sha256"] == hashlib.sha256(data).hexdigest()
    assert downloaded.headers["content-disposition"].startswith("attachment;")


def test_restart_and_backup_restore_keep_project_and_bytes(env, monkeypatch, tmp_path):
    client, engine, settings = env
    pid = client.post(ROOT, json={"title": "Wexford"}, headers=ORIGIN).json()["projectId"]
    data = b"synthetic reproducibility notebook"
    uploaded = client.post(f"{ROOT}/{pid}/files", json={
        "filename": "model.ipynb", "contentBase64": base64.b64encode(data).decode(),
    }, headers=ORIGIN).json()
    database = Path(engine.url.database)
    backup_db = tmp_path / "backup.sqlite"
    with sqlite3.connect(database) as source, sqlite3.connect(backup_db) as destination:
        source.backup(destination)
    backup_blobs = tmp_path / "backup-blobs"
    shutil.copytree(settings.object_storage_root, backup_blobs)
    client.close()
    engine.dispose()
    database.unlink()
    shutil.rmtree(settings.object_storage_root)
    shutil.copy2(backup_db, database)
    shutil.copytree(backup_blobs, settings.object_storage_root)
    restarted = create_engine("sqlite:///" + str(database), connect_args={"check_same_thread": False})
    monkeypatch.setattr(research, "session_scope", lambda: Session(restarted, expire_on_commit=False))
    app = FastAPI()
    app.include_router(research.router)
    with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as reopened:
        reopened.cookies.set("sc_workspace_session", session_auth.issue_session_token("alice"))
        assert reopened.get(f"{ROOT}/{pid}").json()["files"][0]["artifactId"] == uploaded["artifactId"]
        fetched = reopened.get(f"{ROOT}/{pid}/files/{uploaded['artifactId']}/download")
        assert fetched.status_code == 200
        assert hashlib.sha256(fetched.content).hexdigest() == uploaded["sha256"]
    restarted.dispose()

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


def test_cross_project_download_and_generic_replacement_are_denied(env):
    client, engine, _ = env
    first = client.post(ROOT, json={"title": "First"}, headers=ORIGIN).json()["projectId"]
    second = client.post(ROOT, json={"title": "Second"}, headers=ORIGIN).json()["projectId"]
    data = b"synthetic research source"
    payload = {"filename": "source.pdf", "contentBase64": base64.b64encode(data).decode()}
    artifact = client.post(f"{ROOT}/{first}/files", json=payload, headers=ORIGIN).json()
    artifact_id = artifact["artifactId"]
    assert client.get(f"{ROOT}/{second}/files/{artifact_id}/download").status_code == 404
    with Session(engine) as db:
        attempted = ArtifactStoreRequest.model_validate({
            "schema": "sc-workspace-artifact-store/1.0", "artifactId": artifact_id,
            "projectId": second, "filename": "replacement.pdf",
            "mediaType": "application/pdf", "contentBase64": base64.b64encode(b"replacement").decode(),
            "expectedRevision": 1,
        })
        with pytest.raises(HTTPException) as caught:
            object_store.store_artifact(db, "alice", attempted)
        assert caught.value.status_code == 409
    downloaded = client.get(f"{ROOT}/{first}/files/{artifact_id}/download")
    assert downloaded.content == data
    assert downloaded.headers["x-research-sha256"] == artifact["sha256"]

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


@pytest.mark.skipif(not os.getenv("SC_RECOVERY_TEST_DATABASE_URL"), reason="Requires isolated PostgreSQL CI")
def test_postgres_concurrent_duplicate_upload_serializes(tmp_path, monkeypatch):
    url = os.environ["SC_RECOVERY_TEST_DATABASE_URL"]
    assert url.rsplit("/", 1)[-1] == "sc_recovery_test"
    engine = create_engine(url)
    Base.metadata.create_all(engine, tables=[
        ProjectHead.__table__, ProjectRevision.__table__, ArtifactHead.__table__,
        ArtifactRevision.__table__, DomainMutationReceipt.__table__,
    ])
    settings = SimpleNamespace(
        max_project_bytes=10**6, max_account_bytes=10**7, max_projects_per_account=100,
        max_artifact_bytes=10**6, max_artifact_account_bytes=10**7,
        max_artifacts_per_account=100, object_storage_root=str(tmp_path / "pg-blobs"),
    )
    monkeypatch.setattr(repository, "get_settings", lambda: settings)
    monkeypatch.setattr(object_store, "get_settings", lambda: settings)
    monkeypatch.setattr(research, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(session_auth, "get_settings", lambda: SimpleNamespace(
        session_signing_secret="synthetic-postgres-only", service_token="",
        session_cookie_name="sc_workspace_session", session_issuer="synthetic",
        session_audience="workspace.sustainablecatalyst.com", session_ttl_seconds=3600,
    ))
    monkeypatch.setattr(__import__("app.config", fromlist=["get_settings"]), "get_settings", lambda: settings)
    app = FastAPI()
    app.include_router(research.router)
    with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as client:
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("concurrent-test"))
        pid = client.post(ROOT, json={"title": "Synthetic concurrency"}, headers=ORIGIN).json()["projectId"]
    original_files = research._files

    def widen_race_window(db, subject, project_id):
        result = original_files(db, subject, project_id)
        if not result:
            time.sleep(0.15)
        return result

    monkeypatch.setattr(research, "_files", widen_race_window)
    start = threading.Barrier(2)
    payload = {"filename": "simultaneous.pdf", "contentBase64": base64.b64encode(b"%PDF synthetic race").decode()}

    def upload():
        with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as client:
            client.cookies.set("sc_workspace_session", session_auth.issue_session_token("concurrent-test"))
            start.wait(timeout=5)
            return client.post(f"{ROOT}/{pid}/files", json=payload, headers=ORIGIN).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = sorted(pool.map(lambda _: upload(), range(2)))
    assert statuses == [201, 409]
    with Session(engine) as db:
        assert len([item for item in object_store.list_artifacts(db, "concurrent-test") if item["projectId"] == pid]) == 1
    if container := os.getenv("SC_RECOVERY_PG_CONTAINER"):
        backup = tmp_path / "research.backup"
        with backup.open("wb") as stream:
            subprocess.run(
                ["docker", "exec", container, "pg_dump", "-U", "recovery_test", "-d", "sc_recovery_test", "-Fc"],
                stdout=stream, check=True,
            )
        blob_backup = tmp_path / "blob-backup"
        shutil.copytree(settings.object_storage_root, blob_backup)
        subprocess.run(
            ["docker", "exec", "-i", container, "pg_restore", "-U", "recovery_test", "--clean", "--if-exists", "--no-owner", "-d", "sc_recovery_rehearsal"],
            input=backup.read_bytes(), capture_output=True, check=True,
        )
        shutil.rmtree(settings.object_storage_root)
        shutil.copytree(blob_backup, settings.object_storage_root)
        restored_url = url.rsplit("/", 1)[0] + "/sc_recovery_rehearsal"
        restarted = create_engine(restored_url)
        monkeypatch.setattr(research, "session_scope", lambda: Session(restarted, expire_on_commit=False))
        reopened_app = FastAPI()
        reopened_app.include_router(research.router)
        with TestClient(reopened_app, base_url="https://workspace.sustainablecatalyst.com") as reopened:
            reopened.cookies.set("sc_workspace_session", session_auth.issue_session_token("concurrent-test"))
            project = reopened.get(f"{ROOT}/{pid}")
            assert project.status_code == 200
            artifact_id = project.json()["files"][0]["artifactId"]
            downloaded = reopened.get(f"{ROOT}/{pid}/files/{artifact_id}/download")
            assert downloaded.status_code == 200
            assert downloaded.content == b"%PDF synthetic race"
            assert downloaded.headers["x-research-sha256"] == hashlib.sha256(downloaded.content).hexdigest()
        restarted.dispose()
    engine.dispose()
