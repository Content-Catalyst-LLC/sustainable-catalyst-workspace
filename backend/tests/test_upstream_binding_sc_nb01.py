"""SC-NB-01 verified cell-output -> cell-input binding. Synthetic data only.

Unit tests always run. PostgreSQL tests drive the real notebook plan routes, worker job processing,
polyglot executor, registry and Research export; only the runtime HTTP calls are stubbed (an OLS fit,
a normal-equations replay and a minimax-regret ranking computed from the envelope they receive).
"""
import copy
import math
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from test_input_integrity_sc_nb01 import PG, ROWS, client, hdr, put_dataset, put_rows  # noqa: F401 (client is a fixture)
from test_notebook_cell_runs_sc_nb01 import JULIA_OP, NORMAL_EQ, R_OP, export, get_plan, plan_and_dispatch, run_job, store_notebook

os.environ["SC_WORKSPACE_RUNTIME_DECISION_URL"] = "http://decision-runtime.test/v1/execute"
from app.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app import cell_bindings as cb  # noqa: E402
from app import notebook_orchestration as nbo  # noqa: E402

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")
D_OP = "workspace.decision.minimax-regret"
TRANSFORM = {"kind": "linear-scenario-scores", "rates": [10, 25, 40], "uncertaintyMultiplier": 2,
             "scenarioProbabilities": [0.25, 0.5, 0.25], "candidateUnit": "t-ha", "crossCheckTolerance": 1e-6}
UPSTREAM = {"cells": [{"cellId": "fit", "role": "primary"}, {"cellId": "replay", "role": "cross-check"}], "transform": TRANSFORM}


def chain_notebook(ds_id, m_r="", m_j="", r_source="fit <- lm(y ~ x, data = rows)", scenario_payload=None, depends=("fit", "replay")):
    bound = {"datasetId": ds_id, "datasetRevision": 1, "format": "json-records"}
    model = lambda m: {"modelRef": {"modelId": m}} if m else {}  # noqa: E731
    return {"schema": "sc-workspace-notebook/3.0", "title": "Synthetic upstream binding", "cells": [
        {"id": "fit", "type": "code", "language": "r", "source": r_source,
         "execution": {"operation": R_OP, "maxAttempts": 1, **model(m_r),
                       "payload": {"datasetInput": bound, "outcome": "y", "predictors": ["x"]}}},
        {"id": "replay", "type": "code", "language": "julia", "source": "solve(Q, c)",
         "execution": {"operation": JULIA_OP, "maxAttempts": 1, "dependsOnCellIds": ["fit"], **model(m_j),
                       "payload": {"datasetInput": {**bound, "transform": NORMAL_EQ}}}},
        {"id": "scenario", "type": "decision-studio", "source": "", "title": "Application-rate scenarios",
         "execution": {"operation": D_OP, "maxAttempts": 1, "dependsOnCellIds": list(depends),
                       "payload": copy.deepcopy(scenario_payload) if scenario_payload is not None else {"upstreamInput": copy.deepcopy(UPSTREAM)}}},
    ]}


# ---------------------------------------------------------------------------
# Unit


def test_upstream_spec_is_validated_at_plan_time():
    ok = cb.parse_spec("scenario", UPSTREAM, ["fit", "replay"])
    assert ok == [{"cellId": "fit", "role": "primary"}, {"cellId": "replay", "role": "cross-check"}]
    cases = {
        "upstream-input-malformed": ({"cells": []}, ["fit"]),
        "upstream-input-needs-one-primary": ({**UPSTREAM, "cells": [{"cellId": "fit", "role": "cross-check"}]}, ["fit"]),
        "upstream-input-not-declared-dependency": (UPSTREAM, ["fit"]),
        "upstream-transform-unsupported": ({**UPSTREAM, "transform": {"kind": "eval"}}, ["fit", "replay"]),
    }
    for code, (spec, deps) in cases.items():
        with pytest.raises(HTTPException) as exc:
            cb.parse_spec("scenario", spec, deps)
        assert exc.value.status_code == 400 and exc.value.detail["code"] == code


def test_plan_records_upstream_closure_and_inherits_dataset_revisions():
    plan = nbo.compile_plan(chain_notebook("ds-1"))
    fit, replay, scenario = plan["steps"]
    assert plan["order"] == ["fit", "replay", "scenario"]
    assert fit["upstreamCellSha256"] == {} and replay["upstreamCellSha256"] == {"fit": fit["cellSha256"]}
    assert scenario["upstreamCellSha256"] == {"fit": fit["cellSha256"], "replay": replay["cellSha256"]}
    assert scenario["datasetRefs"] == [{"datasetId": "ds-1", "revision": 1}]
    assert scenario["upstreamInputs"][0] == {"cellId": "fit", "role": "primary"}
    # Changing upstream code changes the dependent's upstream identity, not its own cell hash.
    changed = nbo.compile_plan(chain_notebook("ds-1", r_source="fit <- lm(y ~ x + 0, data = rows)"))["steps"][2]
    assert changed["cellSha256"] == scenario["cellSha256"] and changed["upstreamCellSha256"] != scenario["upstreamCellSha256"]
    assert nbo.profile()["verifiedUpstreamCellBinding"] is True


def test_cell_closure_follows_transitive_dependencies():
    cells = chain_notebook("ds-1")["cells"]
    cells[2]["execution"]["dependsOnCellIds"] = ["replay"]
    assert set(nbo._cell_closure(cells, "scenario")) == {"fit", "replay"}
    assert nbo._cell_closure(cells, "fit") == {}
    cells[1]["execution"]["dependsOnCellIds"] = ["gone"]
    assert nbo._cell_closure(cells, "scenario") is None


def test_linear_scenario_scores_are_deterministic_and_validated():
    d = cb.linear_scenario_scores({"intercept": 1.5, "slope": 0.25}, {"slope": 0.01}, TRANSFORM)
    assert [s["id"] for s in d["scenarios"]] == ["slope-low", "slope-central", "slope-high"]
    assert d["candidates"][0] == {"id": "rate-10-t-ha", "scores": [round(1.5 + 0.23 * 10, 9), 4.0, round(1.5 + 0.27 * 10, 9)]}
    assert d == cb.linear_scenario_scores({"intercept": 1.5, "slope": 0.25}, {"slope": 0.01}, TRANSFORM)
    for values, unc, t, code in (
        ({"intercept": 1.5}, {"slope": 0.01}, TRANSFORM, "upstream-values-missing"),
        ({"intercept": 1.5, "slope": 0.25}, {}, TRANSFORM, "upstream-uncertainty-missing"),
        ({"intercept": 1.5, "slope": 0.25}, {"slope": 0.01}, {**TRANSFORM, "scenarioProbabilities": [0.5, 0.5, 0.5]}, "transform-probabilities-invalid"),
        ({"intercept": 1.5, "slope": 0.25}, {"slope": 0.01}, {**TRANSFORM, "rates": ["x"]}, "transform-rates-invalid"),
    ):
        with pytest.raises(cb.InputIntegrityRefused if hasattr(cb, "InputIntegrityRefused") else HTTPException) as exc:
            cb.linear_scenario_scores(values, unc, t)
        assert exc.value.detail["code"] == code


def test_flatten_datasets_walks_nested_chains():
    ds = {"datasetId": "d", "datasetRevision": 1, "artifactId": "a", "artifactRevision": 1, "artifactSha256": "e" * 64}
    nested = {"kind": cb.KIND, "datasets": [ds]}
    assert cb.flatten_datasets([{**ds, "rowsSha256": "x"}, nested]) == [ds]


# ---------------------------------------------------------------------------
# PostgreSQL integration


def ols(rows):
    n = len(rows)
    xs, ys = [r["x"] for r in rows], [r["y"] for r in rows]
    xb, yb = sum(xs) / n, sum(ys) / n
    sxx = sum((x - xb) ** 2 for x in xs)
    slope = sum((x - xb) * (y - yb) for x, y in zip(xs, ys)) / sxx
    icpt = yb - slope * xb
    s2 = sum((y - icpt - slope * x) ** 2 for x, y in zip(xs, ys)) / (n - 2)
    return icpt, slope, math.sqrt(s2 * (1 / n + xb * xb / sxx)), math.sqrt(s2 / sxx)


def fake_runtimes(monkeypatch, julia_bias=0.0):
    import app.polyglot as polyglot
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        p = json["payload"]
        seen.setdefault(json["language"], []).append(json)
        if json["language"] == "decision":
            probs = [s["probability"] for s in p["scenarios"]]
            best = [max(c["scores"][j] for c in p["candidates"]) for j in range(len(probs))]
            regret = {c["id"]: max(b - s for b, s in zip(best, c["scores"])) for c in p["candidates"]}
            body = {"result": {"method": "minimax-regret", "maxRegret": regret, "recommended": min(regret, key=regret.get)}}
        elif "Q" in p:
            (a, b), (_, e) = p["Q"]
            c0, c1 = p["c"]
            det = a * e - b * b
            body = {"result": {"solution": [(-c0 * e + b * c1) / det + julia_bias, (b * c0 - a * c1) / det], "solver": "test"}}
        else:
            i, s, se_i, se_s = ols(p["rows"])
            body = {"result": {"coefficients": [{"term": "(Intercept)", "estimate": i, "stdError": se_i},
                                                {"term": "x", "estimate": s, "stdError": se_s}]}}
        return SimpleNamespace(status_code=200, json=lambda: body, text="")

    monkeypatch.setattr(polyglot.httpx, "post", fake_post)
    return seen


def models(client, user, sfx, project="nb-proj"):
    def put(mid, op, kind, framework, mapping):
        r = client.post("/v1/models", headers=hdr(user), json={
            "schema": "sc-workspace-model-record/1.0", "modelId": mid, "projectId": project, "name": mid,
            "modelKind": kind, "framework": framework, "executionTarget": "workspace", "executionOperation": op,
            "metadata": {"researchResultValues": mapping}})
        assert r.status_code == 200, r.text
    put(f"m-r-{sfx}", R_OP, "statistical", "R", {"kind": "coefficient-table", "uncertaintyField": "stdError",
                                                  "rename": {"(Intercept)": "intercept", "x": "slope"}})
    put(f"m-j-{sfx}", JULIA_OP, "optimization", "Julia", {"kind": "vector", "key": "solution", "names": ["intercept", "slope"]})
    return f"m-r-{sfx}", f"m-j-{sfx}"


def setup_chain(client, user="nb-owner-a", project="nb-proj", **kw):
    sfx = uuid4().hex[:8]
    art = put_rows(client, user, f"ub-rows-{sfx}", ROWS, project=project)
    ds = put_dataset(client, user, f"ub-ds-{sfx}", f"ub-rows-{sfx}", project=project)
    m_r, m_j = models(client, user, sfx, project)
    nb_id = f"ub-{sfx}"
    store_notebook(client, user, nb_id, chain_notebook(ds["datasetId"], m_r, m_j, **kw), project=project)
    return SimpleNamespace(sfx=sfx, art=art, ds=ds, m_r=m_r, m_j=m_j, nb_id=nb_id, user=user, project=project)


def run_through(client, ctx, stop_before=None):
    plan = plan_and_dispatch(client, ctx.user, ctx.nb_id)
    for cid in ("fit", "replay", "scenario"):
        plan = get_plan(client, ctx.user, plan["planId"])
        step = next(s for s in plan["steps"] if s["cellId"] == cid)
        if cid == stop_before or step["state"] != "queued":
            return plan
        run_job(step["jobId"], ctx.user)
    return get_plan(client, ctx.user, plan["planId"])


def step_of(plan, cid):
    return next(s for s in plan["steps"] if s["cellId"] == cid)


def job_of(client, user, step):
    return client.get(f"/v1/jobs/{step['jobId']}", headers=hdr(user)).json()["item"]


@pg
def test_scenario_consumes_verified_upstream_results_with_full_lineage(client, monkeypatch):
    seen = fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan = run_through(client, ctx)
    assert plan["status"] == "succeeded", plan
    fit, replay, scenario = (step_of(plan, c) for c in ("fit", "replay", "scenario"))

    # The decision runtime received values derived server-side from the R fit, not caller input.
    i, s, _, se = ols(ROWS)
    expected = cb.linear_scenario_scores({"intercept": i, "slope": s}, {"slope": se}, TRANSFORM)
    env = seen["decision"][0]
    assert env["payload"]["candidates"] == expected["candidates"] and env["payload"]["scenarios"] == expected["scenarios"]
    assert "upstreamInput" not in env["payload"]

    sc = export(client, ctx.user, scenario["runId"])
    v = sc["verification"]
    assert v["status"] == "executed-verified" and v["inputLineage"] == "artifact-bound-verified"
    b = v["inputBindings"][0]
    assert b["kind"] == "upstream-cell" and b["cellId"] == "scenario" and b["planId"] == plan["planId"]
    assert [(u["cellId"], u["role"], u["runId"]) for u in b["upstream"]] == [
        ("fit", "primary", fit["runId"]), ("replay", "cross-check", replay["runId"])]
    fit_exp = export(client, ctx.user, fit["runId"])
    up_fit = b["upstream"][0]
    assert up_fit["resultSha256"] == fit_exp["verification"]["runtimeReceipts"][0]["resultSha256"]
    assert up_fit["cellSha256"] == fit["cellSha256"] and up_fit["modelRef"]["modelId"] == ctx.m_r
    assert up_fit["environmentFingerprint"] and up_fit["inputBindings"][0]["artifactSha256"] == ctx.art["sha256"]
    assert b["datasets"] == [{"datasetId": ctx.ds["datasetId"], "datasetRevision": 1, "artifactId": ctx.art["artifactId"],
                              "artifactRevision": 1, "artifactSha256": ctx.art["sha256"]}]
    assert b["crossChecks"][0]["cellId"] == "replay" and b["crossChecks"][0]["maxAbsDifference"] < 1e-9
    assert b["upstreamValues"]["fit"] == pytest.approx({"intercept": i, "slope": s})
    assert len(b["chainSha256"]) == 64 and b["derivedPayloadSha256"] == cb.sha256_hex(expected)
    cell = sc["notebookCell"]
    assert cell["verified"] is True and cell["upstreamCellSha256"] == {"fit": fit["cellSha256"], "replay": replay["cellSha256"]}
    assert cell["currency"] == {"headRevision": 1, "current": True, "reasons": []}
    run = client.get(f"/v1/runs/{scenario['runId']}", headers=hdr(ctx.user)).json()["item"]
    assert [(d["datasetId"], d["revision"]) for d in run["datasetRefs"]] == [(ctx.ds["datasetId"], 1)]


@pg
def test_caller_supplied_intermediates_are_refused(client, monkeypatch):
    fake_runtimes(monkeypatch)
    payload = {"upstreamInput": copy.deepcopy(UPSTREAM), "candidates": [{"id": "forged", "scores": [9, 9, 9]}]}
    ctx = setup_chain(client, scenario_payload=payload)
    plan = run_through(client, ctx)
    sc = step_of(plan, "scenario")
    assert plan["status"] == "failed" and sc["state"] == "failed"
    assert job_of(client, ctx.user, sc)["errorCode"] == "upstream-input-and-inline-values"


@pg
def test_undeclared_upstream_is_refused_before_execution(client, monkeypatch):
    # Refused when the notebook is stored (strict cell validation); compile_plan repeats the check
    # (test_upstream_spec_is_validated_at_plan_time) for revisions stored before validation existed.
    fake_runtimes(monkeypatch)
    sfx = uuid4().hex[:8]
    r = client.post("/v1/notebooks", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-notebook-sync-push/1.0", "sourceNotebookId": f"ub-{sfx}", "sourceProjectId": "nb-proj",
        "expectedRevision": 0, "operationId": uuid4().hex, "notebook": chain_notebook("ds-1", depends=("fit",))})
    assert r.status_code == 400 and r.json()["code"] == "invalid-notebook-cell"
    assert r.json()["path"] == "notebook.cells[2].execution.payload.upstreamInput"


@pg
def test_cross_check_disagreement_is_refused(client, monkeypatch):
    fake_runtimes(monkeypatch, julia_bias=0.5)
    ctx = setup_chain(client)
    plan = run_through(client, ctx)
    sc = step_of(plan, "scenario")
    assert sc["state"] == "failed" and job_of(client, ctx.user, sc)["errorCode"] == "upstream-cross-check-failed"


@pg
def test_withdrawn_upstream_is_refused(client, monkeypatch):
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan = run_through(client, ctx, stop_before="scenario")
    fit = step_of(plan, "fit")
    w = client.post(f"/v1/research-exports/runs/{fit['runId']}/withdraw", headers=hdr(ctx.user),
                    json={"projectId": ctx.project, "reason": "synthetic withdrawal test"})
    assert w.status_code == 200, w.text
    run_job(step_of(plan, "scenario")["jobId"], ctx.user)
    sc = step_of(get_plan(client, ctx.user, plan["planId"]), "scenario")
    assert sc["state"] == "failed" and job_of(client, ctx.user, sc)["errorCode"] == "upstream-run-withdrawn"


@pg
def test_tampered_upstream_result_is_refused(client, monkeypatch):
    from app.db import session_scope
    from app.models import ArtifactRevision
    from app.object_store import _path_for_key
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan = run_through(client, ctx, stop_before="scenario")
    fit_exp = export(client, ctx.user, step_of(plan, "fit")["runId"])
    receipt = fit_exp["verification"]["runtimeReceipts"][0]
    with session_scope() as db:
        snap = db.query(ArtifactRevision).filter_by(user_key=ctx.user, artifact_id=receipt["resultArtifactId"]).one()
        path = Path(_path_for_key(snap.storage_key))
    original = path.read_bytes()
    try:
        path.write_bytes(original.replace(b"(Intercept)", b"(Intercept!"))
        run_job(step_of(plan, "scenario")["jobId"], ctx.user)
    finally:
        path.write_bytes(original)
    sc = step_of(get_plan(client, ctx.user, plan["planId"]), "scenario")
    assert sc["state"] == "failed" and job_of(client, ctx.user, sc)["errorCode"] in (
        "upstream-result-integrity-failed", "upstream-run-not-verified")


@pg
def test_failed_or_unverifiable_upstream_is_refused(client, monkeypatch):
    from app.db import session_scope
    from app.models import ExecutionRun
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan = run_through(client, ctx, stop_before="scenario")
    fit = step_of(plan, "fit")
    with session_scope() as db:
        db.get(ExecutionRun, {"user_key": ctx.user, "run_id": fit["runId"]}).status = "failed"
        db.commit()
    run_job(step_of(plan, "scenario")["jobId"], ctx.user)
    sc = step_of(get_plan(client, ctx.user, plan["planId"]), "scenario")
    assert job_of(client, ctx.user, sc)["errorCode"] == "upstream-run-not-verified"

    # An upstream fit on inline rows has unverified lineage, so nothing downstream can bind to it.
    ctx2 = setup_chain(client)
    doc = chain_notebook(ctx2.ds["datasetId"], ctx2.m_r, ctx2.m_j)
    del doc["cells"][0]["execution"]["payload"]["datasetInput"]
    doc["cells"][0]["execution"]["payload"]["rows"] = ROWS
    store_notebook(client, ctx2.user, ctx2.nb_id, doc, expected=1)
    plan2 = run_through(client, ctx2)
    sc2 = step_of(plan2, "scenario")
    assert job_of(client, ctx2.user, sc2)["errorCode"] == "upstream-lineage-unverified"


@pg
def test_upstream_without_result_mapping_is_refused(client, monkeypatch):
    fake_runtimes(monkeypatch)
    sfx = uuid4().hex[:8]
    put_rows(client, "nb-owner-a", f"ub-rows-{sfx}", ROWS)
    ds = put_dataset(client, "nb-owner-a", f"ub-ds-{sfx}", f"ub-rows-{sfx}")
    ctx = SimpleNamespace(user="nb-owner-a", nb_id=f"ub-{sfx}")
    store_notebook(client, ctx.user, ctx.nb_id, chain_notebook(ds["datasetId"]))  # no modelRef on the upstream cells
    plan = run_through(client, ctx)
    sc = step_of(plan, "scenario")
    assert job_of(client, ctx.user, sc)["errorCode"] == "upstream-model-declares-no-result-values"


@pg
def test_cross_owner_and_unplanned_runs_cannot_bind(client, monkeypatch):
    from app.db import session_scope
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan = run_through(client, ctx, stop_before="scenario")
    sc_run = step_of(plan, "scenario")["runId"]
    with session_scope() as db:
        with pytest.raises(HTTPException) as exc:
            cb.resolve_upstream_input(db, "nb-owner-b", {"upstreamInput": UPSTREAM}, sc_run)
    assert exc.value.detail["code"] == "upstream-input-requires-notebook-plan"
    r = client.post("/v1/runs", headers=hdr(ctx.user), json={"schema": "sc-workspace-execution-run/1.0",
                                                             "projectId": "nb-proj", "operation": D_OP})
    with session_scope() as db:
        with pytest.raises(HTTPException) as exc:
            cb.resolve_upstream_input(db, ctx.user, {"upstreamInput": UPSTREAM}, r.json()["item"]["runId"])
    assert exc.value.detail["code"] == "upstream-input-requires-notebook-plan"


@pg
def test_upstream_change_invalidates_dependents_until_rerun(client, monkeypatch):
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    plan1 = run_through(client, ctx)
    sc1 = step_of(plan1, "scenario")
    store_notebook(client, ctx.user, ctx.nb_id, chain_notebook(
        ctx.ds["datasetId"], ctx.m_r, ctx.m_j, r_source="# documented\nfit <- lm(y ~ x, data = rows)"), expected=1)
    stale = export(client, ctx.user, sc1["runId"])["notebookCell"]
    assert stale["verified"] is True  # still a true record of revision 1
    assert stale["currency"] == {"headRevision": 2, "current": False, "reasons": ["upstream-changed"], "changedUpstreamCells": ["fit"]}
    # Revision 2 carries no scenario execution until it is rerun; then the new claim is current.
    pkg = client.get(f"/v1/notebooks/{ctx.nb_id}/revisions/2/export", params={"format": "package"}, headers=hdr(ctx.user)).json()
    assert pkg["related"]["reproducibility"]["executions"] == []
    plan2 = run_through(client, ctx)
    sc2 = step_of(plan2, "scenario")
    assert sc2["cellSha256"] == sc1["cellSha256"] and sc2["upstreamCellSha256"] != sc1["upstreamCellSha256"]
    assert export(client, ctx.user, sc2["runId"])["notebookCell"]["currency"]["current"] is True
    pkg = client.get(f"/v1/notebooks/{ctx.nb_id}/revisions/2/export", params={"format": "package"}, headers=hdr(ctx.user)).json()
    ex = {e["cellId"]: e for e in pkg["related"]["reproducibility"]["executions"]}
    assert ex["scenario"]["upstreamCellSha256"] == sc2["upstreamCellSha256"]
    assert ex["scenario"]["verification"]["inputBindings"][0]["kind"] == "upstream-cell"


@pg
def test_study_package_preserves_upstream_lineage(client, monkeypatch):
    fake_runtimes(monkeypatch)
    project = f"ub-proj-{uuid4().hex[:6]}"
    r = client.post("/v1/projects", headers=hdr("nb-owner-a"), json={
        "schema": "sc-workspace-cloud-backup/1.0", "sourceProjectId": project, "projectTitle": "Synthetic",
        "project": {"schema": "sc-workspace-project/20.0", "id": project, "title": "Synthetic", "objects": []}})
    assert r.status_code == 200, r.text
    ctx = setup_chain(client, project=project)
    plan = run_through(client, ctx)
    assert plan["status"] == "succeeded"
    r = client.post("/v1/scientific-study-packages", headers=hdr(ctx.user), json={
        "schema": "sc-workspace-scientific-study-package-request/1.0", "projectId": project, "includeArtifactBlobs": False})
    assert r.status_code == 200, r.text
    from app.db import session_scope
    from app.models import ScientificStudyPackage
    with session_scope() as db:
        row = db.get(ScientificStudyPackage, {"user_key": ctx.user, "package_id": r.json()["item"]["packageId"]})
        lineage = {x["runId"]: x for x in row.manifest_json["executionLineage"]}
    sc = lineage[step_of(plan, "scenario")["runId"]]
    assert sc["verificationStatus"] == "executed-verified" and sc["inputLineage"] == "artifact-bound-verified"
    assert sc["inputBindings"][0]["kind"] == "upstream-cell" and sc["notebookCell"]["verified"] is True
    assert "currency" not in sc["notebookCell"]
