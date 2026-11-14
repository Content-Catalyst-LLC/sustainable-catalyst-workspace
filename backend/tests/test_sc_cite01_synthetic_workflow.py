"""SC-CITE-01 synthetic full-route acceptance.

Exercises real FastAPI citation endpoints against a disposable, owner-scoped,
in-memory persistence adapter. This is NOT a PostgreSQL or production acceptance
test. Research editorial persistence and backup/restore remain separate gates.
"""
from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from app import citation_studio as cite


@pytest.fixture
def client_and_store():
    projects = {
        ("owner-a", "wexford"): {
            "revision": 1,
            "project": {"objects": []},
        }
    }

    class DisposableSession:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def subject(request: Request):
        owner = request.headers.get("x-test-owner", "")
        if owner not in ("owner-a", "owner-b"):
            raise HTTPException(401, "Synthetic session required")
        return owner

    def project(db, owner, project_id):
        value = projects.get((owner, project_id))
        if value is None:
            raise HTTPException(404, "Project not found")
        return SimpleNamespace(
            revision=value["revision"],
            project_id=project_id,
            title="Wexford",
            package={"project": deepcopy(value["project"])},
        )

    def store(db, owner, row, updated, operation):
        key = (owner, row.project_id)
        original = projects[key]
        if row.revision != original["revision"]:
            raise HTTPException(409, "Stale project revision")
        original["revision"] += 1
        original["project"] = deepcopy(updated)
        return project(db, owner, row.project_id)

    source = [{
        "DOI": "10.1038/s41586-020-2448-9",
        "title": "Potential for large-scale CO2 removal via enhanced rock weathering with croplands",
        "author": [{"family": "Beerling", "given": "David J."},
                   {"family": "Kantzas", "given": "Euripides P."},
                   {"family": "Lomas", "given": "Mark R."}],
        "issued": {"date-parts": [[2020]]},
        "container-title": "Nature",
        "volume": "583",
        "page": "242-248",
        "type": "article-journal",
    }]
    raw = json.dumps(source).encode()

    def original_asset(db, owner, project_id, artifact_id):
        project(db, owner, project_id)
        if artifact_id != "synthetic-references":
            raise HTTPException(404, "Synthetic source not found")
        return {
            "artifactId": artifact_id,
            "filename": "synthetic-references.csl.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }, raw

    library = {
        "identity": {
            "record_id": "wordpress:1:post:15670",
            "revision": 1,
            "content_hash": "c" * 64,
        },
        "descriptive": {"title": "Carbon Accumulation and Emissions Pathways"},
        "publication": {"published_at": "2026-06-16T08:56:50Z"},
        "source": {
            "source_key": "wordpress-main",
            "canonical_url": "https://sustainablecatalyst.com/carbon/",
        },
    }

    def library_record(record_id):
        if record_id != library["identity"]["record_id"]:
            raise HTTPException(404, "Synthetic verified Library item not found")
        return deepcopy(library)

    deps = {
        "subject": subject,
        "write": lambda request: subject(request),
        "project": project,
        "locked_project": project,
        "original_asset": original_asset,
        "store": store,
        "session": DisposableSession,
        "headers": {},
        "library_record": library_record,
        "library_search": lambda q: {"results": []},
    }
    app = FastAPI()
    app.include_router(cite.build_router(deps))
    return TestClient(app), projects


def test_authenticated_import_bibliography_snapshot_replay_and_owner_isolation(client_and_store):
    client, store = client_and_store
    own = {"x-test-owner": "owner-a"}
    other = {"x-test-owner": "owner-b"}
    base = "/citations/projects/wexford"

    anonymous = client.get(base)
    assert anonymous.status_code == 401
    assert client.get(base, headers=other).status_code == 404
    assert client.post(base + "/snapshot", json={
        "sections": [{"body": "Test [@beerling2020potential]."}]
    }).status_code == 401

    imported = client.post(base + "/import-source", headers=own, json={
        "sourceArtifactId": "synthetic-references",
        "expectedProjectRevision": 1,
    })
    assert imported.status_code == 201, imported.text
    assert imported.json()["projectRevision"] == 2
    record = imported.json()["items"][0]
    assert record["provenance"]["sourceSha256"] == hashlib.sha256(
        json.dumps([{
            "DOI": "10.1038/s41586-020-2448-9",
            "title": "Potential for large-scale CO2 removal via enhanced rock weathering with croplands",
            "author": [{"family": "Beerling", "given": "David J."},
                       {"family": "Kantzas", "given": "Euripides P."},
                       {"family": "Lomas", "given": "Mark R."}],
            "issued": {"date-parts": [[2020]]},
            "container-title": "Nature", "volume": "583",
            "page": "242-248", "type": "article-journal",
        }]).encode()
    ).hexdigest()
    key = record["key"]

    stale = client.post(base + "/import-library", headers=own, json={
        "recordId": "wordpress:1:post:15670",
        "expectedProjectRevision": 1,
    })
    assert stale.status_code == 409

    lib = client.post(base + "/import-library", headers=own, json={
        "recordId": "wordpress:1:post:15670",
        "expectedProjectRevision": 2,
    })
    assert lib.status_code == 201, lib.text
    assert lib.json()["projectRevision"] == 3
    assert len(lib.json()["items"]) == 2

    fmt = client.post(base + "/bibliography", headers=own, json={"style": "harvard"})
    assert fmt.status_code == 200, fmt.text
    references = fmt.json()["references"]
    assert len(references) == 2
    assert any("Beerling" in ref and "2020" in ref for ref in references)
    assert any("Sustainable Catalyst" in ref and "2026" in ref for ref in references)

    payload = {
        "style": "harvard",
        "sections": [{"heading": "Wexford", "body": f"Potential [@{key}]."}],
    }
    snapshot = client.post(base + "/snapshot", headers=own, json=payload)
    assert snapshot.status_code == 200, snapshot.text
    body = snapshot.json()
    assert body["schema"] == "sc-citation-snapshot/1.0"
    assert body["bibliography"]["style"] == "harvard"
    assert body["bibliography"]["items"][0]["key"] == key
    assert client.post(base + "/snapshot", headers=own, json=payload).json() == body

    assert client.post(base + "/snapshot", headers=other, json=payload).status_code == 404
    assert client.post(base + "/bibliography", headers=other, json={}).status_code == 404
    assert client.post(base + "/import-library", headers=other, json={
        "recordId": "wordpress:1:post:15670", "expectedProjectRevision": 3
    }).status_code == 404
    assert store[("owner-a", "wexford")]["revision"] == 3
    assert len(store[("owner-a", "wexford")]["project"]["objects"]) == 1


def test_snapshot_validation_and_missing_source_do_not_mutate_project(client_and_store):
    client, projects = client_and_store
    own = {"x-test-owner": "owner-a"}
    base = "/citations/projects/wexford"
    assert client.post(base + "/snapshot", headers=own, json={}).status_code == 422
    assert client.post(base + "/import-source", headers=own, json={
        "sourceArtifactId": "unknown", "expectedProjectRevision": 1,
    }).status_code == 404
    assert projects[("owner-a", "wexford")]["revision"] == 1
