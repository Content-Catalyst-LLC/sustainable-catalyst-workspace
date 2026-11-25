"""SC-WS-PR-02: private-research source files stay immutable through the generic
artifact routes that production serves (POST/DELETE /v1/artifacts).

The research file is uploaded through its own owner-scoped project route, exactly
as SC-RESEARCH-PROJECT-01 stores it; the generic routes are then exercised with the
same owner. Synthetic data only.
"""
import base64

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from test_wxr_private_projects import env, ORIGIN, ROOT  # noqa: F401 - pytest fixture
from app import main as workspace_main, object_store
from app.security import ServiceIdentity, require_service_identity


def _generic_client(engine, monkeypatch, owner="alice"):
    monkeypatch.setattr(workspace_main, "session_scope", lambda: Session(engine, expire_on_commit=False))
    workspace_main.app.dependency_overrides[require_service_identity] = lambda: ServiceIdentity(
        user_key=owner, principal_id=f"session:{owner}", principal_type="user",
        service_principal="synthetic-test", authentication_method="synthetic")
    return TestClient(workspace_main.app)


def _research_file(client):
    project = client.post(ROOT, json={"title": "Immutable sources"}, headers=ORIGIN).json()["projectId"]
    raw = b"synthetic published source bytes"
    created = client.post(f"{ROOT}/{project}/files", headers=ORIGIN, json={
        "filename": "source.pdf", "contentBase64": base64.b64encode(raw).decode()})
    assert created.status_code == 201, created.text
    return project, created.json()["artifactId"], raw


def test_generic_routes_cannot_replace_or_delete_a_private_research_file(env, monkeypatch):
    client, engine, _ = env
    project, artifact_id, raw = _research_file(client)
    generic = _generic_client(engine, monkeypatch)
    try:
        replaced = generic.post("/v1/artifacts", json={
            "schema": "sc-workspace-artifact-store/1.0", "artifactId": artifact_id, "projectId": project,
            "filename": "source.pdf", "mediaType": "application/pdf",
            "contentBase64": base64.b64encode(b"different bytes").decode(), "expectedRevision": 1})
        assert replaced.status_code == 409, replaced.text
        deleted = generic.delete(f"/v1/artifacts/{artifact_id}")
        assert deleted.status_code == 409, deleted.text
    finally:
        workspace_main.app.dependency_overrides.clear()
    with Session(engine) as db:
        row = object_store.get_artifact(db, "alice", artifact_id)
        assert row is not None and row.revision == 1
        assert object_store.read_artifact_content(row) == raw
    assert client.get(f"{ROOT}/{project}/files/{artifact_id}/download").content == raw


def test_ordinary_artifacts_keep_their_generic_replace_and_delete(env, monkeypatch):
    _, engine, _ = env
    generic = _generic_client(engine, monkeypatch)
    try:
        body = {"schema": "sc-workspace-artifact-store/1.0", "artifactId": "ordinary-note",
                "filename": "note.txt", "mediaType": "text/plain",
                "contentBase64": base64.b64encode(b"v1").decode()}
        assert generic.post("/v1/artifacts", json=body).status_code == 200
        body.update(contentBase64=base64.b64encode(b"v2").decode(), expectedRevision=1)
        assert generic.post("/v1/artifacts", json=body).json()["item"]["revision"] == 2
        assert generic.delete("/v1/artifacts/ordinary-note").json()["deleted"] is True
    finally:
        workspace_main.app.dependency_overrides.clear()
