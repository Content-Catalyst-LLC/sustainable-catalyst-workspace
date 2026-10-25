"""PostgreSQL Reporting Studio smoke, synthetic fixtures only; no production URLs."""
import os
import hashlib
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app import repository, object_store, session_auth, wxr_private_projects as research, research_reporting as reporting
from app.models import Base, ProjectHead, ProjectRevision, ArtifactHead, ArtifactRevision, DomainMutationReceipt
from test_research_reporting import stage, save, url, ROOT, REPORTING, ORIGIN


def test_postgres_report_save_reopen_authorization(tmp_path, monkeypatch):
    database_url = os.environ.get("SC_RECOVERY_TEST_DATABASE_URL", "")
    assert database_url and make_url(database_url).database == "sc_recovery_test", "Only disposable sc_recovery_test allowed"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine, tables=[
        ProjectHead.__table__, ProjectRevision.__table__, ArtifactHead.__table__,
        ArtifactRevision.__table__, DomainMutationReceipt.__table__,
    ])
    settings = SimpleNamespace(
        max_project_bytes=10**6, max_account_bytes=10**7, max_projects_per_account=100,
        max_artifact_bytes=10**6, max_artifact_account_bytes=10**7,
        max_artifacts_per_account=100, object_storage_root=str(tmp_path / "postgres-report-blobs"),
    )
    monkeypatch.setattr(repository, "get_settings", lambda: settings)
    monkeypatch.setattr(object_store, "get_settings", lambda: settings)
    monkeypatch.setattr(research, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(reporting, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(session_auth, "get_settings", lambda: SimpleNamespace(
        session_signing_secret="synthetic-g1-postgres-only", service_token="",
        session_cookie_name="sc_workspace_session", session_issuer="synthetic",
        session_audience="workspace.sustainablecatalyst.com", session_ttl_seconds=3600,
    ))
    monkeypatch.setenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED", "1")
    app = FastAPI()
    app.include_router(research.router)
    app.include_router(reporting.router)
    with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as client:
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("pg-report-owner"))
        created = client.post(ROOT, json={"title": "Synthetic PG report"}, headers=ORIGIN)
        assert created.status_code == 201, created.text
        project_id = created.json()["projectId"]
        fixture = (client, engine, settings, project_id)
        reference, original_bytes = stage(fixture)
        preview = client.post(f"{REPORTING}/projects/{project_id}/preview", json=reference, headers=ORIGIN)
        assert preview.status_code == 200, preview.text
        saved = save(client, project_id, reference)
        report_url = url(project_id, saved)
        first = client.get(report_url)
        assert first.status_code == 200, first.text
        assert first.json()["view"]["source_sha256"] == reference["sha256"]
        assert client.get(f"{ROOT}/{project_id}/files/{reference['artifact_id']}/download").content == original_bytes
        client.cookies.clear()
        assert client.get(report_url).status_code == 401
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("pg-report-other"))
        assert client.get(report_url).status_code == 404
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("pg-report-owner"))
        assert client.get(report_url).json() == first.json()
    engine.dispose()


def test_postgres_concurrent_reports_and_paired_restore(tmp_path, monkeypatch):
    """Two saves race for one revision; a separately restored pair retains the winner."""
    database_url = os.environ.get("SC_RECOVERY_TEST_DATABASE_URL", "")
    container = os.environ.get("SC_RECOVERY_PG_CONTAINER", "")
    assert database_url and make_url(database_url).database == "sc_recovery_test"
    assert container, "A disposable PostgreSQL 18 container is required"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine, tables=[
        ProjectHead.__table__, ProjectRevision.__table__, ArtifactHead.__table__,
        ArtifactRevision.__table__, DomainMutationReceipt.__table__,
    ])
    settings = SimpleNamespace(
        max_project_bytes=10**6, max_account_bytes=10**7, max_projects_per_account=100,
        max_artifact_bytes=10**6, max_artifact_account_bytes=10**7,
        max_artifacts_per_account=100, object_storage_root=str(tmp_path / "g1-original-objects"),
    )
    monkeypatch.setattr(repository, "get_settings", lambda: settings)
    monkeypatch.setattr(object_store, "get_settings", lambda: settings)
    monkeypatch.setattr(research, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(reporting, "session_scope", lambda: Session(engine, expire_on_commit=False))
    monkeypatch.setattr(session_auth, "get_settings", lambda: SimpleNamespace(
        session_signing_secret="synthetic-g1-pg-restore-only", service_token="",
        session_cookie_name="sc_workspace_session", session_issuer="synthetic",
        session_audience="workspace.sustainablecatalyst.com", session_ttl_seconds=3600,
    ))
    monkeypatch.setenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED", "1")
    app = FastAPI()
    app.include_router(research.router)
    app.include_router(reporting.router)

    with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as client:
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("g1-pg-owner"))
        created = client.post(ROOT, json={"title": "Disposable G1 race"}, headers=ORIGIN)
        assert created.status_code == 201, created.text
        project_id = created.json()["projectId"]
        reference, original_bytes = stage((client, engine, settings, project_id))

    barrier = threading.Barrier(2)

    def race_save(color):
        body = {**reference, "display": {**reference["display"], "color": color}}
        with TestClient(app, base_url="https://workspace.sustainablecatalyst.com") as client:
            client.cookies.set("sc_workspace_session", session_auth.issue_session_token("g1-pg-owner"))
            barrier.wait(timeout=10)
            response = client.post(f"{REPORTING}/projects/{project_id}/reports", json=body, headers=ORIGIN)
            return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(race_save, ("#175a3b", "#ab182b")))
    assert sorted(status for status, _ in results) == [201, 409], results
    winning_report = next(payload["report"] for status, payload in results if status == 201)
    report_path = url(project_id, winning_report)

    with Session(engine) as db:
        assert repository.get_project(db, "g1-pg-owner", project_id).revision == 2
        assert len(repository.list_project_revisions(db, "g1-pg-owner", project_id)) == 2
    engine.dispose()

    backup = tmp_path / "g1-paired.backup"
    with backup.open("wb") as stream:
        subprocess.run(
            ["docker", "exec", container, "pg_dump", "-U", "recovery_test", "-d", "sc_recovery_test", "-Fc"],
            stdout=stream, check=True,
        )
    assert backup.stat().st_size > 0
    restored_objects = tmp_path / "g1-restored-objects"
    shutil.copytree(settings.object_storage_root, restored_objects)
    subprocess.run(
        ["docker", "exec", "-i", container, "pg_restore", "-U", "recovery_test", "--clean", "--if-exists", "--no-owner", "-d", "sc_g1_restore_test"],
        input=backup.read_bytes(), capture_output=True, check=True,
    )
    restored_url = database_url.rsplit("/", 1)[0] + "/sc_g1_restore_test"
    restored_engine = create_engine(restored_url)
    settings.object_storage_root = str(restored_objects)
    monkeypatch.setattr(research, "session_scope", lambda: Session(restored_engine, expire_on_commit=False))
    monkeypatch.setattr(reporting, "session_scope", lambda: Session(restored_engine, expire_on_commit=False))
    restored_app = FastAPI()
    restored_app.include_router(research.router)
    restored_app.include_router(reporting.router)
    with TestClient(restored_app, base_url="https://workspace.sustainablecatalyst.com") as client:
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("g1-pg-owner"))
        assert client.get(f"{ROOT}/{project_id}").status_code == 200
        reopened = client.get(report_path)
        assert reopened.status_code == 200, reopened.text
        assert reopened.json()["view"]["source_sha256"] == reference["sha256"]
        download = client.get(f"{ROOT}/{project_id}/files/{reference['artifact_id']}/download")
        assert download.status_code == 200
        assert download.content == original_bytes
        assert download.headers["x-research-sha256"] == hashlib.sha256(original_bytes).hexdigest()
        client.cookies.clear()
        assert client.get(report_path).status_code == 401
        client.cookies.set("sc_workspace_session", session_auth.issue_session_token("g1-pg-other"))
        assert client.get(report_path).status_code == 404
    restored_engine.dispose()
