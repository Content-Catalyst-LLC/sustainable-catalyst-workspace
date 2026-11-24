"""Disposable PostgreSQL SC-CITE-01 acceptance via real Citation Studio routes.

Runs ONLY against the named local CI database and a synthetic credential.
Does not test the production repository, real identity provider, Research
editorial persistence, backup, restore, or production deployment.
"""
import hashlib
import json
import os
from types import SimpleNamespace
from urllib.parse import urlparse

import psycopg
from psycopg.types.json import Jsonb
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from app import citation_studio as cite


def _safe_url():
    if os.environ.get("SC_CITE01_DISPOSABLE_POSTGRES") != "I_UNDERSTAND_THIS_IS_SYNTHETIC":
        pytest.fail("SC_CITE01_DISPOSABLE_POSTGRES sentinel not set")
    url = os.environ.get("SC_CITE01_POSTGRES_URL", "")
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql") or parsed.hostname not in ("127.0.0.1", "localhost"):
        pytest.fail("Only loopback disposable PostgreSQL is permitted")
    if parsed.path != "/cite01_acceptance":
        pytest.fail("Database name must be cite01_acceptance")
    return url


@pytest.fixture
def postgres_app():
    url = _safe_url()
    with psycopg.connect(url) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS sc_cite01_acceptance (
              owner text NOT NULL,
              project_id text NOT NULL,
              revision integer NOT NULL,
              body jsonb NOT NULL,
              PRIMARY KEY (owner, project_id)
            )
        """)
        db.execute("DELETE FROM sc_cite01_acceptance")
        db.execute(
            "INSERT INTO sc_cite01_acceptance VALUES (%s,%s,%s,%s)",
            ("owner-a", "wexford", 1, Jsonb({"objects": []})),
        )

    def session():
        return psycopg.connect(url)

    def subject(request: Request):
        value = request.headers.get("x-test-owner")
        if value not in ("owner-a", "owner-b"):
            raise HTTPException(401, "Synthetic owner required")
        return value

    def project(db, owner, project_id, lock=False):
        result = db.execute(
            "SELECT revision,body FROM sc_cite01_acceptance WHERE owner=%s AND project_id=%s" +
            (" FOR UPDATE" if lock else ""),
            (owner, project_id),
        ).fetchone()
        if not result:
            raise HTTPException(404, "Project not found")
        return SimpleNamespace(
            revision=result[0], project_id=project_id, title="Wexford",
            package={"project": result[1]},
        )

    def locked_project(db, owner, project_id):
        return project(db, owner, project_id, lock=True)

    def store(db, owner, row, updated, operation):
        result = db.execute(
            "UPDATE sc_cite01_acceptance SET revision=revision+1, body=%s "
            "WHERE owner=%s AND project_id=%s AND revision=%s RETURNING revision",
            (Jsonb(updated), owner, row.project_id, row.revision),
        ).fetchone()
        if result is None:
            raise HTTPException(409, "Concurrent update")
        return project(db, owner, row.project_id)

    source = [{
        "type": "article-journal",
        "title": "Potential for large-scale CO2 removal via enhanced rock weathering with croplands",
        "author": [{"family": "Beerling", "given": "David J."},
                   {"family": "Kantzas", "given": "Euripides P."}],
        "issued": {"date-parts": [[2020]]},
        "DOI": "10.1038/s41586-020-2448-9",
        "container-title": "Nature",
    }]
    raw = json.dumps(source).encode()

    def original_asset(db, owner, project_id, artifact_id):
        project(db, owner, project_id)
        if artifact_id != "synthetic-csl":
            raise HTTPException(404, "Source not found")
        return {
            "artifactId": artifact_id,
            "filename": "synthetic.csl.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }, raw

    def library_record(record_id):
        if record_id != "wordpress:1:post:15670":
            raise HTTPException(404, "Synthetic Library item unavailable")
        return {
            "identity": {
                "record_id": record_id, "revision": 1, "content_hash": "c" * 64,
            },
            "descriptive": {"title": "Carbon Accumulation and Emissions Pathways"},
            "publication": {"published_at": "2026-06-16"},
            "source": {
                "source_key": "wordpress-main",
                "canonical_url": "https://sustainablecatalyst.com/carbon/",
            },
        }

    app = FastAPI()
    app.include_router(cite.build_router({
        "session": session,
        "subject": subject,
        "write": lambda request: subject(request),
        "project": project,
        "locked_project": locked_project,
        "store": store,
        "original_asset": original_asset,
        "library_record": library_record,
        "library_search": lambda q: {"results": []},
        "headers": {},
    }))
    yield TestClient(app), url
    with psycopg.connect(url) as db:
        db.execute("DELETE FROM sc_cite01_acceptance")
        db.execute("DROP TABLE sc_cite01_acceptance")


def test_postgres_source_library_bibliography_snapshot_and_owner_boundaries(postgres_app):
    client, url = postgres_app
    a, b = {"x-test-owner": "owner-a"}, {"x-test-owner": "owner-b"}
    base = "/citations/projects/wexford"
    assert client.get(base).status_code == 401
    assert client.get(base, headers=b).status_code == 404

    source = client.post(base + "/import-source", headers=a, json={
        "sourceArtifactId": "synthetic-csl", "expectedProjectRevision": 1,
    })
    assert source.status_code == 201, source.text
    assert source.json()["projectRevision"] == 2
    key = source.json()["items"][0]["key"]
    assert source.json()["items"][0]["provenance"]["sourceSha256"] is not None

    old = client.post(base + "/import-source", headers=a, json={
        "sourceArtifactId": "synthetic-csl", "expectedProjectRevision": 1,
    })
    assert old.status_code == 409

    library = client.post(base + "/import-library", headers=a, json={
        "recordId": "wordpress:1:post:15670", "expectedProjectRevision": 2,
    })
    assert library.status_code == 201, library.text
    assert library.json()["projectRevision"] == 3

    with psycopg.connect(url) as db:
        revision, stored = db.execute(
            "SELECT revision, body FROM sc_cite01_acceptance WHERE owner=%s AND project_id=%s",
            ("owner-a", "wexford"),
        ).fetchone()
        assert revision == 3
        assert len(cite.collection({"project": stored})["items"]) == 2

    fmt = client.post(base + "/bibliography", headers=a, json={"style": "harvard"})
    assert fmt.status_code == 200, fmt.text
    assert len(fmt.json()["references"]) == 2
    assert any("Beerling" in x for x in fmt.json()["references"])
    assert any("Sustainable Catalyst" in x for x in fmt.json()["references"])

    sections = {"sections": [{"heading": "Wexford", "body": f"Potential [@{key}]."}], "style": "harvard"}
    frozen = client.post(base + "/snapshot", headers=a, json=sections)
    assert frozen.status_code == 200, frozen.text
    data = frozen.json()
    assert data["bibliography"]["items"][0]["key"] == key
    assert client.post(base + "/snapshot", headers=a, json=sections).json() == data

    assert client.post(base + "/snapshot", headers=b, json=sections).status_code == 404
    assert client.post(base + "/bibliography", headers=b, json={}).status_code == 404
    assert client.post(base + "/import-library", headers=b, json={
        "recordId": "wordpress:1:post:15670", "expectedProjectRevision": 3,
    }).status_code == 404
    with psycopg.connect(url) as db:
        assert db.execute("SELECT count(*) FROM sc_cite01_acceptance").fetchone()[0] == 1
