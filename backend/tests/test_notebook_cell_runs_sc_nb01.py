"""SC-NB-01 notebook cells execute as ExecutionRuns with byte-bound dataset inputs.

Unit tests always run. PostgreSQL tests drive the real notebook plan routes, the real worker job
processing and the real polyglot executor; only the runtime HTTP call is stubbed. Synthetic data only.
"""
import copy
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from test_input_integrity_sc_nb01 import PG, ROWS, client, hdr, put_dataset, put_rows  # noqa: F401 (client is a fixture)

from app import notebook_orchestration as nbo  # noqa: E402

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")
R_OP, JULIA_OP = "workspace.polyglot.r.linear-model", "workspace.polyglot.julia.quadratic-optimize"
NORMAL_EQ = {"kind": "least-squares-normal-equations", "outcome": "y", "predictors": ["x"]}


def notebook(ds_id, revision=1, r_source="fit <- lm(y ~ x, data = rows)", sha=None):
    bound = {"datasetId": ds_id, "datasetRevision": revision, "format": "json-records"}
    if sha:
        bound["artifactSha256"] = sha
    return {"schema": "sc-workspace-notebook/3.0", "title": "Synthetic dose-response", "cells": [
        {"id": "q", "type": "markdown", "source": "Research question: is y linear in x? (synthetic)"},
        {"id": "fit", "type": "code", "language": "r", "source": r_source,
         "execution": {"operation": R_OP, "payload": {"datasetInput": bound, "outcome": "y", "predictors": ["x"]}}},
        {"id": "replay", "type": "code", "language": "julia", "source": "solve(Q, c)",
         "execution": {"operation": JULIA_OP, "dependsOnCellIds": ["fit"],
                       "payload": {"datasetInput": {**bound, "transform": NORMAL_EQ}}}},
    ]}


# ---------------------------------------------------------------------------
# Unit


def test_steps_declare_dataset_revisions_and_server_cell_hash():
    plan = nbo.compile_plan(notebook("ds-1"))
    fit = plan["steps"][0]
    assert plan["order"] == ["fit", "replay"]
    assert fit["datasetRefs"] == [{"datasetId": "ds-1", "revision": 1}] and fit["runId"] == ""
    assert len(fit["cellSha256"]) == 64
    changed = nbo.compile_plan(notebook("ds-1", r_source="fit <- lm(y ~ x + 0, data = rows)"))["steps"][0]
    assert changed["cellSha256"] != fit["cellSha256"]
    # A client-side fingerprint field on the cell does not influence the server hash.
    doc = notebook("ds-1")
    doc["cells"][1]["fingerprint"] = "f" * 64
    assert nbo.compile_plan(doc)["steps"][0]["cellSha256"] == fit["cellSha256"]


def test_dataset_refs_require_an_explicit_revision():
    doc = notebook("ds-1")
    del doc["cells"][1]["execution"]["payload"]["datasetInput"]["datasetRevision"]
    with pytest.raises(HTTPException) as exc:
        nbo.compile_plan(doc)
    assert exc.value.detail["code"] == "cell-dataset-ref-requires-revision"
    assert nbo.profile()["cellExecutionRuns"] is True


# ---------------------------------------------------------------------------
# PostgreSQL integration


def fake_runtime(monkeypatch):
    import app.polyglot as polyglot

    def fake_post(url, json=None, headers=None, timeout=None):
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


def run_job(job_id, user):
    """What the worker does after claim_next_job, for one specific job."""
    from app import worker
    from app.db import session_scope
    from app.models import JobRecord
    with session_scope() as db:
        row = db.get(JobRecord, {"user_key": user, "job_id": job_id})
        row.status, row.attempt = "running", row.attempt + 1
        db.commit()
        db.refresh(row)
        db.expunge(row)
    worker.process_job(row)


def store_notebook(client, user, nb_id, doc, expected=0, project="nb-proj"):
    r = client.post("/v1/notebooks", headers=hdr(user), json={
        "schema": "sc-workspace-notebook-sync-push/1.0", "sourceNotebookId": nb_id, "sourceProjectId": project,
        "expectedRevision": expected, "operationId": uuid4().hex, "notebook": doc})
    assert r.status_code == 200, r.text
    return r.json()["item"]


def plan_and_dispatch(client, user, nb_id, expect=200):
    r = client.post("/v1/notebook-execution-plans", headers=hdr(user), json={
        "schema": "sc-workspace-notebook-execution-plan-request/1.0", "notebookId": nb_id})
    if r.status_code != 200:
        assert r.status_code == expect, r.text
        return None
    plan = r.json()["item"]
    d = client.post(f"/v1/notebook-execution-plans/{plan['planId']}/dispatch", headers=hdr(user), json={
        "schema": "sc-workspace-notebook-execution-dispatch-request/1.0", "idempotencyKey": uuid4().hex})
    assert d.status_code == expect, d.text
    return d.json()["item"] if d.status_code == 200 else None


def get_plan(client, user, plan_id):
    return client.get(f"/v1/notebook-execution-plans/{plan_id}", headers=hdr(user)).json()["item"]


def export(client, user, run_id, project="nb-proj"):
    from app import research_exports as rx
    rx._key.cache_clear()
    g = client.post("/v1/research-exports/grants", headers=hdr(user), json={"projectId": project, "runId": run_id})
    assert g.status_code == 200, g.text
    doc = client.post("/v1/research-exports/fetch", headers={"Authorization": "Bearer research-client-test"},
                      json={"grant": g.json()["grant"]})
    assert doc.status_code == 200, doc.text
    return doc.json()


def dataset(client, user):
    sfx = uuid4().hex[:8]
    art = put_rows(client, user, f"nb-rows-{sfx}", ROWS)
    ds = put_dataset(client, user, f"nb-ds-{sfx}", f"nb-rows-{sfx}")
    return sfx, art, ds


@pg
def test_notebook_cells_execute_as_bound_runs_and_export_verified_cells(client, monkeypatch):
    fake_runtime(monkeypatch)
    sfx, art, ds = dataset(client, "nb-owner-a")
    nb_id = f"nb-{sfx}"
    store_notebook(client, "nb-owner-a", nb_id, notebook(ds["datasetId"], sha=art["sha256"]))
    plan = plan_and_dispatch(client, "nb-owner-a", nb_id)
    fit, replay = plan["steps"]
    assert fit["state"] == "queued" and fit["runId"] and replay["state"] == "pending" and replay["runId"] == ""

    run = client.get(f"/v1/runs/{fit['runId']}", headers=hdr("nb-owner-a")).json()["item"]
    assert [(d["datasetId"], d["revision"]) for d in run["datasetRefs"]] == [(ds["datasetId"], 1)]
    job = client.get(f"/v1/jobs/{fit['jobId']}", headers=hdr("nb-owner-a")).json()["item"]
    assert job["executionRunId"] == fit["runId"]

    run_job(fit["jobId"], "nb-owner-a")
    plan = get_plan(client, "nb-owner-a", plan["planId"])
    replay = plan["steps"][1]
    assert plan["steps"][0]["state"] == "succeeded" and replay["state"] == "queued" and replay["runId"]
    run_job(replay["jobId"], "nb-owner-a")
    plan = get_plan(client, "nb-owner-a", plan["planId"])
    assert plan["status"] == "succeeded"

    doc = export(client, "nb-owner-a", fit["runId"])
    assert doc["verification"]["status"] == "executed-verified"
    assert doc["verification"]["inputLineage"] == "artifact-bound-verified"
    assert doc["verification"]["inputBindings"][0]["artifactSha256"] == art["sha256"]
    cell = doc["notebookCell"]
    assert cell["verified"] is True and cell["notebookId"] == nb_id and cell["notebookRevision"] == 1
    assert cell["cellId"] == "fit" and cell["cellSha256"] == fit["cellSha256"] and cell["language"] == "r"
    head = client.get(f"/v1/notebooks/{nb_id}", headers=hdr("nb-owner-a")).json()["item"]
    assert cell["notebookPackageSha256"] == head["fingerprint"] and "cells" not in cell
    rdoc = export(client, "nb-owner-a", replay["runId"])
    assert rdoc["verification"]["inputBindings"][0]["rowsSha256"] == doc["verification"]["inputBindings"][0]["rowsSha256"]
    assert rdoc["verification"]["inputBindings"][0]["transform"]["kind"] == NORMAL_EQ["kind"]


@pg
def test_forged_cell_claim_changed_code_and_owner_isolation(client, monkeypatch):
    fake_runtime(monkeypatch)
    sfx, art, ds = dataset(client, "nb-owner-a")
    nb_id = f"nb-{sfx}"
    store_notebook(client, "nb-owner-a", nb_id, notebook(ds["datasetId"]))
    plan = plan_and_dispatch(client, "nb-owner-a", nb_id)
    fit = plan["steps"][0]
    run_job(fit["jobId"], "nb-owner-a")

    # A run created directly, copying a real cell claim into its inline environment, is not verified.
    claim = {"schema": nbo.CELL_RUN_SCHEMA, "planId": plan["planId"], "notebookId": nb_id, "notebookRevision": 1,
             "cellId": "fit", "cellSha256": fit["cellSha256"]}
    r = client.post("/v1/runs", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-execution-run/1.0", "projectId": "nb-proj", "operation": R_OP,
        "datasetRefs": [{"datasetId": ds["datasetId"], "revision": 1}], "environment": {"notebookCell": claim}})
    forged = r.json()["item"]["runId"]
    assert export(client, "nb-owner-a", forged)["notebookCell"]["verified"] is False

    # Changed code: revision 2 of the notebook gives the cell a new hash and a new run input fingerprint.
    store_notebook(client, "nb-owner-a", nb_id, notebook(ds["datasetId"], r_source="fit <- lm(y ~ x + 0, data = rows)"), expected=1)
    plan2 = plan_and_dispatch(client, "nb-owner-a", nb_id)
    fit2 = plan2["steps"][0]
    assert fit2["cellSha256"] != fit["cellSha256"]
    runs = [client.get(f"/v1/runs/{x}", headers=hdr("nb-owner-a")).json()["item"] for x in (fit["runId"], fit2["runId"])]
    assert runs[0]["inputFingerprint"] != runs[1]["inputFingerprint"]
    run_job(fit2["jobId"], "nb-owner-a")
    cell2 = export(client, "nb-owner-a", fit2["runId"])["notebookCell"]
    assert cell2["verified"] is True and cell2["notebookRevision"] == 2
    # The revision-1 run still verifies against the immutable revision 1, not the new head.
    assert export(client, "nb-owner-a", fit["runId"])["notebookCell"]["verified"] is True

    # Owner B can neither plan A's notebook nor bind A's dataset from its own notebook.
    plan_and_dispatch(client, "nb-owner-b", nb_id, expect=404)
    store_notebook(client, "nb-owner-b", f"nb-b-{sfx}", notebook(ds["datasetId"]))
    plan_and_dispatch(client, "nb-owner-b", f"nb-b-{sfx}", expect=409)


@pg
def test_failed_cell_stops_downstream_and_reports_refusal(client, monkeypatch):
    fake_runtime(monkeypatch)
    sfx, art, ds = dataset(client, "nb-owner-a")
    nb_id = f"nb-{sfx}"
    store_notebook(client, "nb-owner-a", nb_id, notebook(ds["datasetId"], sha="0" * 64))
    plan = plan_and_dispatch(client, "nb-owner-a", nb_id)
    fit = plan["steps"][0]
    # One attempt is enough to show the refusal; the cell's default retry budget would re-queue it.
    for _ in range(3):
        run_job(fit["jobId"], "nb-owner-a")
        job = client.get(f"/v1/jobs/{fit['jobId']}", headers=hdr("nb-owner-a")).json()["item"]
        if job["status"] == "failed":
            break
    assert job["status"] == "failed" and job["errorCode"] == "dataset-input-sha256-mismatch"
    plan = get_plan(client, "nb-owner-a", plan["planId"])
    assert plan["status"] == "failed" and plan["steps"][1]["state"] == "pending" and plan["steps"][1]["runId"] == ""
    run = client.get(f"/v1/runs/{fit['runId']}", headers=hdr("nb-owner-a")).json()["item"]
    assert run["status"] == "failed"
    doc = export(client, "nb-owner-a", fit["runId"])
    assert doc["verification"]["status"] == "failed" and doc["verification"]["inputLineage"] == "not-executed"
    assert doc["resultValues"]["values"] == {}


@pg
def test_notebook_plan_replays_are_idempotent(client, monkeypatch):
    fake_runtime(monkeypatch)
    sfx, art, ds = dataset(client, "nb-owner-a")
    nb_id = f"nb-{sfx}"
    store_notebook(client, "nb-owner-a", nb_id, notebook(ds["datasetId"]))
    plan = plan_and_dispatch(client, "nb-owner-a", nb_id)
    again = client.post(f"/v1/notebook-execution-plans/{plan['planId']}/dispatch", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-notebook-execution-dispatch-request/1.0", "idempotencyKey": uuid4().hex}).json()["item"]
    assert copy.deepcopy(again["steps"]) == plan["steps"]
