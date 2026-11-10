"""SC-NB-01 input integrity: polyglot inputs bound to exact, immutable dataset bytes.

Unit tests always run. PostgreSQL tests (real registry routes and the real polyglot executor, with
only the runtime HTTP call stubbed) run when SC_WORKSPACE_DATABASE_URL points at a disposable
PostgreSQL database. Synthetic data only.
"""
import base64
import json
import os
import secrets
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-nb01-export-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_ENABLED", "true")
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE", SEED_FILE)
os.environ.setdefault("SC_WORKSPACE_RESEARCH_EXPORT_CLIENT_TOKEN", "research-client-test")
os.environ.setdefault("SC_WORKSPACE_SERVICE_TOKEN", "workspace-service-test")
os.environ.setdefault("SC_WORKSPACE_OBJECT_STORAGE_ROOT", os.path.join(KEY_DIR, f"sc-objects-{os.getpid()}"))
os.environ["SC_WORKSPACE_RUNTIME_R_URL"] = "http://r-runtime.test/v1/execute"
os.environ["SC_WORKSPACE_RUNTIME_JULIA_URL"] = "http://julia-runtime.test/v1/execute"

from fastapi import HTTPException  # noqa: E402

from app import input_integrity as ii  # noqa: E402
from app.config import get_settings  # noqa: E402

get_settings.cache_clear()
PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")
ROWS = [{"x": float(x), "y": 1.5 + 0.25 * x + (0.01 if x % 2 else -0.01)} for x in range(0, 11)]


def test_parse_records_and_csv():
    assert ii._parse(json.dumps(ROWS).encode(), "json-records") == ROWS
    assert ii._parse(json.dumps({"rows": ROWS}).encode(), "json-records") == ROWS
    csv_rows = ii._parse(b"x,y\n1,2.5\n2,\n", "csv")
    assert csv_rows == [{"x": 1.0, "y": 2.5}, {"x": 2.0, "y": None}]
    with pytest.raises(HTTPException):
        ii._parse(b"[1,2]", "json-records")


def test_normal_equations_match_least_squares():
    d = ii._normal_equations(ROWS, {"outcome": "y", "predictors": ["x"]})
    (a, b), (_, e) = d["Q"]
    c0, c1 = d["c"]
    det = a * e - b * b
    intercept, slope = (-c0 * e + b * c1) / det, (b * c0 - a * c1) / det
    assert abs(slope - 0.25) < 0.01 and abs(intercept - 1.5) < 0.05
    with pytest.raises(HTTPException):
        ii._normal_equations([{"x": "a", "y": 1}], {"outcome": "y", "predictors": ["x"]})


def test_unbound_payloads_are_never_verified():
    assert ii.lineage_for_payload({"rows": ROWS}) == ii.INLINE
    assert ii.lineage_for_payload({"Q": [[1]], "c": [1]}) == ii.INLINE
    assert ii.lineage_for_payload({}) == ii.NONE


# ---------------------------------------------------------------------------
# PostgreSQL integration

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.db import initialize_schema
    from app.main import app
    initialize_schema()
    with TestClient(app) as c:
        yield c


def hdr(user):
    return {"Authorization": "Bearer " + get_settings().service_token, "X-SC-User-ID": user}


def put_rows(client, user, artifact_id, rows, revision=0, project="nb-proj"):
    r = client.post("/v1/artifacts", headers=hdr(user), json={"schema": "sc-workspace-artifact-store/1.0",
        "artifactId": artifact_id, "projectId": project, "filename": "rows.json", "mediaType": "application/json",
        "contentBase64": base64.b64encode(json.dumps(rows).encode()).decode(), "expectedRevision": revision, "metadata": {}})
    assert r.status_code == 200, r.text
    return r.json()["item"]


def put_dataset(client, user, dataset_id, artifact_id, revision=None, project="nb-proj", description=""):
    body = {"schema": "sc-workspace-dataset-record/1.0", "datasetId": dataset_id, "projectId": project, "name": "Synthetic",
            "datasetType": "table", "sourceKind": "artifact", "artifactId": artifact_id, "description": description,
            "metadata": {"scientificClassification": "synthetic"}}
    if revision is not None:
        body["expectedRevision"] = revision
    r = client.post("/v1/datasets", headers=hdr(user), json=body)
    assert r.status_code == 200, r.text
    return r.json()["item"]


def new_run(client, user, dataset_id, revision, project="nb-proj", operation="workspace.polyglot.r.linear-model"):
    r = client.post("/v1/runs", headers=hdr(user), json={"schema": "sc-workspace-execution-run/1.0", "projectId": project,
        "operation": operation, "datasetRefs": [{"datasetId": dataset_id, "revision": revision}]})
    assert r.status_code == 200, r.text
    return r.json()["item"]["runId"]


def setup(client, user="nb-owner-a"):
    sfx = uuid4().hex[:8]
    art = put_rows(client, user, f"rows-{sfx}", ROWS)
    ds = put_dataset(client, user, f"ds-{sfx}", f"rows-{sfx}")
    return sfx, art, ds


def resolve(user, payload, run_id=""):
    from app.db import session_scope
    with session_scope() as db:
        return ii.resolve_dataset_input(db, user, payload, run_id)


def spec(ds, **over):
    return {"datasetInput": {"datasetId": ds["datasetId"], "datasetRevision": ds["revision"], **over}}


@pg
def test_dataset_revision_pins_artifact_bytes_and_binding_reads_them(client):
    sfx, art, ds = setup(client)
    assert ds["artifactSha256"] == art["sha256"] and ds["artifactRevision"] == 1
    run = new_run(client, "nb-owner-a", ds["datasetId"], 1)
    payload, binding = resolve("nb-owner-a", {**spec(ds, artifactSha256=art["sha256"]), "outcome": "y", "predictors": ["x"]}, run)
    assert payload["rows"] == ROWS and payload["outcome"] == "y" and "datasetInput" not in payload
    assert binding["lineage"] == ii.VERIFIED and binding["artifactSha256"] == art["sha256"] and binding["rowCount"] == len(ROWS)


@pg
def test_modified_dataset_keeps_old_revision_on_its_own_snapshot(client):
    sfx, art, ds1 = setup(client)
    changed = [dict(r, y=r["y"] + 1.0) for r in ROWS]
    art2 = put_rows(client, "nb-owner-a", f"rows-{sfx}", changed, revision=1)
    assert art2["sha256"] != art["sha256"]
    _, b1 = resolve("nb-owner-a", spec(ds1))
    assert b1["artifactSha256"] == art["sha256"] and b1["artifactRevision"] == 1
    ds2 = put_dataset(client, "nb-owner-a", ds1["datasetId"], f"rows-{sfx}", revision=1, description="r2")
    p2, b2 = resolve("nb-owner-a", spec(ds2))
    assert b2["artifactSha256"] == art2["sha256"] and p2["rows"] == changed and b2["rowsSha256"] != b1["rowsSha256"]
    with pytest.raises(HTTPException) as exc:
        resolve("nb-owner-a", spec(ds1, artifactSha256=art2["sha256"]))
    assert exc.value.detail["code"] == "dataset-input-sha256-mismatch"


@pg
def test_refusals(client):
    from app.db import session_scope
    from app.models import DatasetRevision
    sfx, art, ds = setup(client)
    codes = {}
    for name, user, payload, run in [
        ("cross-owner", "nb-owner-b", spec(ds), ""),
        ("inline-and-bound", "nb-owner-a", {**spec(ds), "rows": ROWS}, ""),
        ("undeclared", "nb-owner-a", spec(ds), new_run(client, "nb-owner-a", setup(client)[2]["datasetId"], 1)),
        ("bad-transform", "nb-owner-a", spec(ds, transform={"kind": "anything"}), ""),
    ]:
        with pytest.raises(HTTPException) as exc:
            resolve(user, payload, run)
        codes[name] = exc.value.detail["code"]
    assert codes == {"cross-owner": "dataset-input-not-found", "inline-and-bound": "dataset-input-and-inline-rows",
                     "undeclared": "dataset-input-not-declared-by-run", "bad-transform": "dataset-input-transform-unsupported"}
    with session_scope() as db:  # a legacy revision registered before pinning existed
        row = db.get(DatasetRevision, {"user_key": "nb-owner-a", "dataset_id": ds["datasetId"], "revision": 1})
        row.artifact_sha256 = ""
        db.commit()
    with pytest.raises(HTTPException) as exc:
        resolve("nb-owner-a", spec(ds))
    assert exc.value.detail["code"] == "dataset-revision-not-byte-pinned"


@pg
def test_tampered_storage_is_detected(client):
    from app.db import session_scope
    from app.models import ArtifactRevision
    from app.object_store import _path_for_key
    sfx, art, ds = setup(client)
    with session_scope() as db:
        snap = db.get(ArtifactRevision, {"user_key": "nb-owner-a", "artifact_id": f"rows-{sfx}", "revision": 1})
        path = Path(_path_for_key(snap.storage_key))
    original = path.read_bytes()
    try:
        path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
        with pytest.raises(HTTPException) as exc:
            resolve("nb-owner-a", spec(ds))
        assert exc.value.status_code == 503
    finally:
        path.write_bytes(original)


def _execute(monkeypatch, user, run_id, operation, payload):
    """Real polyglot executor and registry writes; only the runtime HTTP call is stubbed."""
    import app.polyglot as polyglot
    from app.db import session_scope
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        seen["envelope"] = json
        p = json["payload"]
        if "Q" in p:
            (a, b), (_, e) = p["Q"]
            c0, c1 = p["c"]
            det = a * e - b * b
            body = {"result": {"solution": [(-c0 * e + b * c1) / det, (b * c0 - a * c1) / det], "solver": "test"}}
        else:
            body = {"result": {"coefficients": [{"term": "(Intercept)", "estimate": 1.5, "stdError": 0.1},
                                                {"term": "x", "estimate": 0.25, "stdError": 0.01}]}}
        return SimpleNamespace(status_code=200, json=lambda: body, text="")

    monkeypatch.setattr(polyglot.httpx, "post", fake_post)
    row = SimpleNamespace(operation=operation, payload={"executionRunId": run_id, "payload": payload}, user_key=user,
                          job_id=f"job-{uuid4().hex[:10]}", project_id="nb-proj", request_fingerprint="c" * 64)
    with session_scope() as db:
        polyglot.execute_polyglot_operation(db, row)
    return row.job_id, seen["envelope"]


@pg
def test_executor_records_verified_binding_and_export_reports_lineage(client, monkeypatch):
    from sqlalchemy import select
    from app import research_exports as rx
    from app.db import session_scope
    from app.models import PolyglotExecutionReceipt
    from app.registry import sync_run_from_job
    rx._key.cache_clear()
    sfx, art, ds = setup(client)
    run = new_run(client, "nb-owner-a", ds["datasetId"], 1)
    job, env = _execute(monkeypatch, "nb-owner-a", run, "workspace.polyglot.r.linear-model",
                        {**spec(ds), "outcome": "y", "predictors": ["x"]})
    assert env["payload"]["rows"] == ROWS and env["inputBindings"][0]["artifactSha256"] == art["sha256"]
    with session_scope() as db:
        rec = db.scalars(select(PolyglotExecutionReceipt).where(PolyglotExecutionReceipt.job_id == job)).one()
        assert rec.details_json["inputLineage"] == ii.VERIFIED
        sync_run_from_job(db, "nb-owner-a", run, job, "succeeded", 100)
        db.commit()
    g = client.post("/v1/research-exports/grants", headers=hdr("nb-owner-a"), json={"projectId": "nb-proj", "runId": run}).json()
    doc = client.post("/v1/research-exports/fetch", headers={"Authorization": "Bearer research-client-test"}, json={"grant": g["grant"]}).json()
    assert doc["verification"]["status"] == "executed-verified" and doc["verification"]["inputLineage"] == ii.VERIFIED
    assert doc["verification"]["inputBindings"][0]["artifactSha256"] == art["sha256"]

    # Julia through the declared server-side transform over the same verified bytes.
    run_j = new_run(client, "nb-owner-a", ds["datasetId"], 1)
    _, env_j = _execute(monkeypatch, "nb-owner-a", run_j, "workspace.polyglot.julia.quadratic-optimize",
                        spec(ds, transform={"kind": "least-squares-normal-equations", "outcome": "y", "predictors": ["x"]}))
    assert "rows" not in env_j["payload"] and len(env_j["payload"]["Q"]) == 2
    assert env_j["inputBindings"][0]["rowsSha256"] == env["inputBindings"][0]["rowsSha256"]

    # Inline rows still run, but are labelled unverified end to end.
    run_i = new_run(client, "nb-owner-a", ds["datasetId"], 1)
    job_i, _ = _execute(monkeypatch, "nb-owner-a", run_i, "workspace.polyglot.r.linear-model",
                        {"rows": ROWS, "outcome": "y", "predictors": ["x"]})
    with session_scope() as db:
        sync_run_from_job(db, "nb-owner-a", run_i, job_i, "succeeded", 100)
        db.commit()
    g = client.post("/v1/research-exports/grants", headers=hdr("nb-owner-a"), json={"projectId": "nb-proj", "runId": run_i}).json()
    doc = client.post("/v1/research-exports/fetch", headers={"Authorization": "Bearer research-client-test"}, json={"grant": g["grant"]}).json()
    assert doc["verification"]["status"] == "executed-verified" and doc["verification"]["inputLineage"] == ii.INLINE
    assert doc["verification"]["inputBindings"] == []


@pg
def test_worker_reports_integrity_refusal_code(client):
    from app import worker
    from app.db import session_scope
    from app.models import JobRecord
    sfx, art, ds = setup(client)
    run = new_run(client, "nb-owner-a", ds["datasetId"], 1)
    r = client.post("/v1/jobs", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-job-request/1.0", "operation": "workspace.polyglot.r.linear-model", "projectId": "nb-proj",
        "executionRunId": run, "maxAttempts": 1,
        "payload": {**spec(ds, artifactSha256="0" * 64), "outcome": "y", "predictors": ["x"]}})
    assert r.status_code == 200, r.text
    job_id = r.json()["item"]["jobId"]
    with session_scope() as db:
        row = db.get(JobRecord, {"user_key": "nb-owner-a", "job_id": job_id})
        db.expunge(row)
    worker.process_job(row)
    item = client.get(f"/v1/jobs/{job_id}", headers=hdr("nb-owner-a")).json()["item"]
    assert item["status"] == "failed" and item["errorCode"] == "dataset-input-sha256-mismatch", item
    assert art["sha256"] in item["errorMessage"]
