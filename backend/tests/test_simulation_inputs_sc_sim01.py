"""SC-SIM-01 / SC-MATH-01: parameter-set inputs, pinned series, and declared reproduction tolerance.

Unit tests always run. PostgreSQL tests (real registry routes and the real polyglot executor, with only
the runtime HTTP call stubbed) run when SC_WORKSPACE_DATABASE_URL points at a disposable PostgreSQL
database. Synthetic data only.
"""
import os
from types import SimpleNamespace
from uuid import uuid4

import pytest

import tests.test_input_integrity_sc_nb01 as nb  # noqa: F401  (sets the test environment first)
from fastapi import HTTPException

from app import input_integrity as ii
from app import research_exports as rx

PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")
SERIES_ROWS = [{"t": t, "y": 10.0 + 0.5 * t} for t in (3, 1, 2, 0, 4)]


def code(exc_info) -> str:
    return exc_info.value.detail["code"]


def test_numeric_series_orders_by_key_and_refuses_gaps():
    assert ii._numeric_series(SERIES_ROWS, {"column": "y", "orderBy": "t"}) == {
        "target": "values", "values": [10.0, 10.5, 11.0, 11.5, 12.0]}
    # Without orderBy, the pinned file order is the series order.
    assert ii._numeric_series(SERIES_ROWS, {"column": "y", "target": "observations"})["values"][0] == 11.5
    dated = [{"d": "2026-01-02", "y": 2.0}, {"d": "2026-01-01", "y": 1.0}]
    assert ii._numeric_series(dated, {"column": "y", "orderBy": "d"})["values"] == [1.0, 2.0]
    for rows, spec, expected in (
        (SERIES_ROWS + [{"t": 5, "y": None}], {"column": "y", "orderBy": "t"}, "transform-non-numeric-value"),
        (SERIES_ROWS + [{"t": 4, "y": 1.0}], {"column": "y", "orderBy": "t"}, "transform-order-key-invalid"),
        ([{"t": 1, "y": 1.0}, {"t": "2", "y": 1.0}], {"column": "y", "orderBy": "t"}, "transform-order-key-invalid"),
        (SERIES_ROWS, {"column": "y", "target": "rows"}, "transform-target-unsupported"),
        (SERIES_ROWS, {"orderBy": "t"}, "transform-needs-column"),
        ([], {"column": "y"}, "transform-series-size"),
    ):
        with pytest.raises(HTTPException) as e:
            ii._numeric_series(rows, spec)
        assert code(e) == expected


def test_declared_tolerance_is_bounded_and_exported():
    assert rx.declared_tolerance({"relative": 1e-8, "absolute": 1e-10}) == {"relative": 1e-8, "absolute": 1e-10}
    assert rx.declared_tolerance({"relative": 1e-6}) == {"relative": 1e-6, "absolute": 0.0}
    for bad in ({}, {"relative": 0.2}, {"absolute": -1}, {"relative": "x"}, {"relative": 1e-6, "statistical": {}}, [1e-6]):
        assert isinstance(rx.declared_tolerance(bad), str), bad
    doc = {"result": {"remote": {"result": {"solution": [1.5, 0.25]}}}}
    mapping = {"kind": "vector", "key": "solution", "names": ["a", "b"], "tolerance": {"relative": 1e-8, "absolute": 1e-10}}
    assert rx.extract_result_values(mapping, doc)["tolerance"] == {"relative": 1e-8, "absolute": 1e-10}
    bad = rx.extract_result_values({**mapping, "tolerance": {"relative": 0.5}}, doc)
    assert bad["values"] == {} and bad["error"].startswith("tolerance:")
    assert "tolerance" not in rx.extract_result_values({k: v for k, v in mapping.items() if k != "tolerance"}, doc)


def test_parameter_binding_is_projected_into_the_export():
    b = {"schema": ii.PARAMETER_BINDING_SCHEMA, "kind": ii.PARAMETER_KIND, "lineage": ii.VERIFIED, "parameterSetId": "p",
         "parameterSetRevision": 2, "parameterSetFingerprint": "f" * 64, "modelId": "m", "parametersSha256": "a" * 64,
         "scientificClassification": "synthetic", "internal": "dropped"}
    out = rx.project_binding(b)
    assert out["parameterSetFingerprint"] == "f" * 64 and "internal" not in out and "datasetId" not in out


# ---------------------------------------------------------------------------
# PostgreSQL integration

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")
client = nb.client
hdr = nb.hdr
USER = "sim-owner-a"
PROJECT = "sim-proj"


def post(client, path, body, user=USER, expect=200):
    r = client.post(path, headers=hdr(user), json=body)
    assert r.status_code == expect, r.text
    return r.json().get("item", r.json())


def model(client, model_id, kind="simulation", mapping=None):
    return post(client, "/v1/models", {"schema": "sc-workspace-model-record/1.0", "modelId": model_id, "projectId": PROJECT,
                                       "name": "Synthetic simulation", "modelKind": kind, "framework": "Julia",
                                       "executionTarget": "workspace", "executionOperation": "workspace.polyglot.julia.monte-carlo-normal",
                                       "metadata": {"researchResultValues": mapping or {
                                           "kind": "scalar-paths", "paths": {"sampleMean": "metrics.sampleMean"},
                                           "tolerance": {"relative": 1e-12, "absolute": 1e-12}}}})


def parameter_set(client, ps_id, model_id, params, cls="synthetic", revision=None):
    body = {"schema": "sc-workspace-parameter-set/1.0", "parameterSetId": ps_id, "projectId": PROJECT, "modelId": model_id,
            "name": "Synthetic parameters", "parameters": params, "metadata": {"scientificClassification": cls}}
    if revision is not None:
        body["expectedRevision"] = revision
    return post(client, "/v1/parameter-sets", body)


def run(client, model_id, ps_id=None, ps_rev=None, datasets=()):
    body = {"schema": "sc-workspace-execution-run/1.0", "projectId": PROJECT, "operation": "workspace.polyglot.julia.monte-carlo-normal",
            "modelRef": {"modelId": model_id}, "datasetRefs": [{"datasetId": d, "revision": r} for d, r in datasets]}
    if ps_id:
        body["parameterSetRef"] = {"parameterSetId": ps_id, "revision": ps_rev}
    return post(client, "/v1/runs", body)["runId"]


def resolve_params(payload, run_id):
    from app.db import session_scope
    with session_scope() as db:
        return ii.resolve_parameter_input(db, USER, payload, run_id)


def pin(ps, **over):
    return {"parameterInput": {"parameterSetId": ps["parameterSetId"], "parameterSetRevision": ps["revision"], **over}}


def execute(monkeypatch, run_id, operation, payload, body):
    import app.polyglot as polyglot
    from app.db import session_scope
    from app.registry import sync_run_from_job
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        seen["envelope"] = json
        return SimpleNamespace(status_code=200, json=lambda: {"result": body}, text="")

    monkeypatch.setattr(polyglot.httpx, "post", fake_post)
    row = SimpleNamespace(operation=operation, payload={"executionRunId": run_id, "payload": payload}, user_key=USER,
                          job_id=f"job-{uuid4().hex[:10]}", project_id=PROJECT, request_fingerprint="d" * 64)
    with session_scope() as db:
        polyglot.execute_polyglot_operation(db, row)
        sync_run_from_job(db, USER, run_id, row.job_id, "succeeded", 100)
        db.commit()
    return seen["envelope"]


def export(client, run_id):
    g = client.post("/v1/research-exports/grants", headers=hdr(USER), json={"projectId": PROJECT, "runId": run_id}).json()
    return client.post("/v1/research-exports/fetch", headers={"Authorization": "Bearer research-client-test"},
                       json={"grant": g["grant"]}).json()


@pg
def test_parameter_only_simulation_is_bound_to_the_pinned_revision_and_exported(client, monkeypatch):
    rx._key.cache_clear()
    sfx = uuid4().hex[:8]
    m = model(client, f"sim-m-{sfx}")
    params = {"mean": 2.0, "stdDev": 0.5, "samples": 1000, "seed": 11}
    ps = parameter_set(client, f"sim-p-{sfx}", m["modelId"], params)
    run_id = run(client, m["modelId"], ps["parameterSetId"], ps["revision"])
    env = execute(monkeypatch, run_id, "workspace.polyglot.julia.monte-carlo-normal", pin(ps, fingerprint=ps["fingerprint"]),
                  {"kind": "monte-carlo-normal", "seed": 11, "metrics": {"sampleMean": 2.01}})
    assert env["payload"] == params  # the runtime saw exactly the registered parameters
    doc = export(client, run_id)
    v = doc["verification"]
    assert doc["resultValues"]["values"] == {"sampleMean": 2.01} and doc["resultValues"]["stochastic"] == {"seed": 11}
    assert doc["resultValues"]["tolerance"] == {"relative": 1e-12, "absolute": 1e-12}
    assert v["status"] == "executed-verified" and v["inputLineage"] == ii.VERIFIED
    (b,) = v["inputBindings"]
    assert b["kind"] == ii.PARAMETER_KIND and b["parameterSetFingerprint"] == ps["fingerprint"]
    assert b["parametersSha256"] == rx.sha256_hex(params) and b["scientificClassification"] == "synthetic"
    assert doc["provenance"]["inputs"]["model"]["resolved"]["modelKind"] == "simulation"


@pg
def test_parameter_input_refusals(client):
    sfx = uuid4().hex[:8]
    m = model(client, f"sim-m-{sfx}")
    ps1 = parameter_set(client, f"sim-p-{sfx}", m["modelId"], {"mean": 1.0, "seed": 1})
    ps2 = parameter_set(client, f"sim-p-{sfx}", m["modelId"], {"mean": 2.0, "seed": 1}, revision=1)
    run_id = run(client, m["modelId"], ps1["parameterSetId"], 1)
    ok, _ = resolve_params(pin(ps1), run_id)
    assert ok == {"mean": 1.0, "seed": 1}
    cases = (
        ({**pin(ps1), "mean": 9.0}, run_id, "parameter-input-inline-keys"),
        (pin(ps2), run_id, "parameter-input-not-declared-by-run"),          # revision 2 is not what the run pinned
        (pin(ps1, fingerprint="0" * 64), run_id, "parameter-input-fingerprint-mismatch"),
        (pin(ps1), "", "parameter-input-needs-run"),
        ({"parameterInput": {"parameterSetId": ps1["parameterSetId"]}}, run_id, "parameter-input-revision-required"),
        ({"parameterInput": "x"}, run_id, "parameter-input-malformed"),
    )
    for payload, rid, expected in cases:
        with pytest.raises(HTTPException) as e:
            resolve_params(payload, rid)
        assert code(e) == expected, (payload, code(e))
    # Another user's run cannot be used.
    from app.db import session_scope
    with session_scope() as db, pytest.raises(HTTPException) as e:
        ii.resolve_parameter_input(db, "sim-intruder", pin(ps1), run_id)
    assert code(e) == "parameter-input-run-not-found"


@pg
def test_tampered_parameter_revision_is_detected(client):
    from sqlalchemy import text
    from app.db import session_scope
    sfx = uuid4().hex[:8]
    m = model(client, f"sim-m-{sfx}")
    ps = parameter_set(client, f"sim-p-{sfx}", m["modelId"], {"mean": 1.0})
    run_id = run(client, m["modelId"], ps["parameterSetId"], 1)
    with session_scope() as db:
        db.execute(text("UPDATE workspace_parameter_set_revisions SET parameters_json = '{\"mean\": 5.0}'::jsonb "
                        "WHERE user_key = :u AND parameter_set_id = :p AND revision = 1"), {"u": USER, "p": ps["parameterSetId"]})
        db.commit()
    with pytest.raises(HTTPException) as e:
        resolve_params(pin(ps), run_id)
    assert code(e) == "parameter-set-integrity-failed"


@pg
def test_parameters_and_pinned_series_combine_with_verified_lineage(client, monkeypatch):
    sfx = uuid4().hex[:8]
    nb.put_rows(client, USER, f"series-{sfx}", SERIES_ROWS, project=PROJECT)
    ds = nb.put_dataset(client, USER, f"series-ds-{sfx}", f"series-{sfx}", project=PROJECT)
    m = model(client, f"fc-m-{sfx}", kind="forecasting", mapping={"kind": "vector", "key": "point", "names": ["h1", "h2"]})
    ps = parameter_set(client, f"fc-p-{sfx}", m["modelId"], {"horizon": 2})
    run_id = run(client, m["modelId"], ps["parameterSetId"], 1, datasets=[(ds["datasetId"], ds["revision"])])
    series = {"datasetId": ds["datasetId"], "datasetRevision": ds["revision"],
              "transform": {"kind": "numeric-series", "column": "y", "orderBy": "t"}}
    env = execute(monkeypatch, run_id, "workspace.polyglot.forecast.linear-trend", {**pin(ps), "datasetInput": series},
                  {"kind": "linear-trend", "point": [12.5, 13.0]})
    assert env["payload"] == {"horizon": 2, "values": [10.0, 10.5, 11.0, 11.5, 12.0]}
    kinds = [b.get("kind") for b in env["inputBindings"]]
    assert kinds == [ii.PARAMETER_KIND, None]
    assert env["inputBindings"][1]["derivedPayloadSha256"] == rx.sha256_hex({"values": [10.0, 10.5, 11.0, 11.5, 12.0]})
    doc = export(client, run_id)
    assert doc["verification"]["inputLineage"] == ii.VERIFIED and len(doc["verification"]["inputBindings"]) == 2
    # A series key sent inline alongside the pinned series is refused.
    with pytest.raises(HTTPException) as e:
        nb.resolve(USER, {"datasetInput": series, "values": [1.0]}, run_id)
    assert code(e) == "dataset-input-and-inline-series"
