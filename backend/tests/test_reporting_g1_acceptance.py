"""One synthetic G1 journey through native persistence and paired restore.

This deliberately does not assert real-account login or production deployment.
"""
import hashlib
import shutil
import sqlite3

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import object_store, research_reporting, session_auth, wxr_private_projects
from test_research_reporting import ORIGIN, REPORTING, ROOT, setup, stage, url
from test_wxr_private_projects import env


def test_g1_signed_project_report_and_paired_restore(setup, monkeypatch, tmp_path):
    client, engine, settings, project_id = setup
    reference, source_bytes = stage(setup)
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    assert reference["sha256"] == source_digest

    preview_path = f"{REPORTING}/projects/{project_id}/preview"
    save_path = f"{REPORTING}/projects/{project_id}/reports"
    assert client.post(preview_path, json=reference, headers=ORIGIN).status_code == 200
    assert client.post(save_path, json=reference).status_code == 403
    first = client.post(save_path, json=reference, headers=ORIGIN)
    assert first.status_code == 201, first.text
    saved = first.json()["report"]
    assert client.post(save_path, json=reference, headers=ORIGIN).status_code == 409
    report_path = url(project_id, saved)
    original = client.get(report_path)
    assert original.status_code == 200
    assert original.json()["view"]["source_sha256"] == source_digest
    assert client.get(f"{ROOT}/{project_id}/files/{reference['artifact_id']}/download").content == source_bytes

    other_project = client.post(ROOT, json={"title": "Other synthetic project"}, headers=ORIGIN).json()["projectId"]
    assert client.post(f"{REPORTING}/projects/{other_project}/reports", json=reference, headers=ORIGIN).status_code == 404
    client.cookies.clear()
    assert client.get(report_path).status_code == 401
    client.cookies.set("sc_workspace_session", session_auth.issue_session_token("bob"))
    assert client.get(report_path).status_code == 404

    # SQLite backup API and a separate object copy form a disposable pair.
    backup_db = tmp_path / "restored.sqlite"
    with sqlite3.connect(engine.url.database) as source, sqlite3.connect(backup_db) as target:
        source.backup(target)
    backup_objects = tmp_path / "restored-objects"
    shutil.copytree(settings.object_storage_root, backup_objects)
    engine.dispose()

    restored_engine = create_engine("sqlite:///" + str(backup_db), connect_args={"check_same_thread": False})
    monkeypatch.setattr(wxr_private_projects, "session_scope", lambda: Session(restored_engine, expire_on_commit=False))
    monkeypatch.setattr(research_reporting, "session_scope", lambda: Session(restored_engine, expire_on_commit=False))
    settings.object_storage_root = str(backup_objects)
    restored_app = FastAPI()
    restored_app.include_router(wxr_private_projects.router)
    restored_app.include_router(research_reporting.router)
    with TestClient(restored_app, base_url="https://workspace.sustainablecatalyst.com") as reopened:
        reopened.cookies.set("sc_workspace_session", session_auth.issue_session_token("alice"))
        assert reopened.get(f"{ROOT}/{project_id}").status_code == 200
        assert reopened.get(report_path).json() == original.json()
        downloaded = reopened.get(f"{ROOT}/{project_id}/files/{reference['artifact_id']}/download")
        assert downloaded.status_code == 200
        assert hashlib.sha256(downloaded.content).hexdigest() == source_digest
        assert downloaded.headers["x-research-sha256"] == source_digest
        reopened.cookies.clear()
        reopened.cookies.set("sc_workspace_session", session_auth.issue_session_token("bob"))
        assert reopened.get(report_path).status_code == 404
    with Session(restored_engine) as db:
        artifact = object_store.get_artifact(db, "alice", reference["artifact_id"])
        assert object_store.read_artifact_content(artifact) == source_bytes
    restored_engine.dispose()
