"""SC-SIM-01 G7/G8/G9: governed adapters into Workbench and Decision Studio, and result bindings checked
against ExecutionRun receipts.

Unit tests always run. PostgreSQL tests (real registry routes and the real polyglot executor, with only the
adapter HTTP call stubbed) run when SC_WORKSPACE_DATABASE_URL points at a disposable PostgreSQL database.
Synthetic data only.
"""
import os
from types import SimpleNamespace
from uuid import uuid4

os.environ.setdefault("SC_WORKSPACE_RUNTIME_WORKBENCH_URL", "http://workbench.test/v1/workspace/execute")
os.environ.setdefault("SC_WORKSPACE_RUNTIME_WORKBENCH_TOKEN", "workbench-test")
os.environ.setdefault("SC_WORKSPACE_RUNTIME_DECISION_STUDIO_URL", "http://decision-studio.test/v1/workspace/execute")
os.environ.setdefault("SC_WORKSPACE_RUNTIME_DECISION_STUDIO_TOKEN", "decision-studio-test")

import pytest  # noqa: E402

import tests.test_simulation_inputs_sc_sim01 as sim  # noqa: E402  (sets the test environment first)
from app import notebook_orchestration as nbo  # noqa: E402
from app import result_receipts as rr  # noqa: E402
from app import routing  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.input_integrity import VERIFIED  # noqa: E402
from app.polyglot import OPERATION_LANGUAGE, RUNTIMES, _runtime_route  # noqa: E402

get_settings.cache_clear()

WB_MC, WB_SIM = "workspace.workbench.uncertainty-propagation", "workspace.workbench.dynamical-simulation"
DS_CMP, DS_SENS = "workspace.decision-studio.scenario-comparison", "workspace.decision-studio.sensitivity-analysis"


# ---------------------------------------------------------------------------
# Unit


def test_adapters_are_registered_server_configured_operations():
    by_lang = {r.language: r for r in RUNTIMES}
    assert by_lang["workbench"].transport == by_lang["decision-studio"].transport == "server-configured-http"
    assert {OPERATION_LANGUAGE[op] for op in (WB_MC, WB_SIM)} == {"workbench"}
    assert {OPERATION_LANGUAGE[op] for op in (DS_CMP, DS_SENS)} == {"decision-studio"}
    assert _runtime_route("workbench")[0].endswith("/v1/workspace/execute")
    # The existing decision runtime keeps its own prefix; Decision Studio operations do not collide with it.
    assert not DS_CMP.startswith("workspace.decision.")


def test_adapter_operations_can_be_notebook_cells():
    doc = {"schema": "sc-workspace-notebook/3.0", "title": "adapter cells", "cells": [
        {"id": "wb", "type": "code", "language": "python", "source": "uncertainty",
         "execution": {"operation": WB_MC, "payload": {"parameterInput": {"parameterSetId": "p", "parameterSetRevision": 1}}}},
        {"id": "ds", "type": "code", "language": "python", "source": "scenarios", "execution": {"operation": DS_CMP, "payload": {}}},
    ]}
    assert {s["operation"] for s in nbo.compile_plan(doc)["steps"]} == {WB_MC, DS_CMP}


def test_non_run_references_are_client_asserted_and_legacy_bindings_unverified():
    v = rr.verify_result_ref(None, "u", "p", "https://example.test/forecast.json", "a" * 64)
    assert v["status"] == "client-asserted" and v["evidence"] == "exploratory"
    assert rr.verification_of({"note": "x"})["status"] == "unverified-legacy"
    # A client cannot pre-set the server verdict.
    stored = rr.with_verification({"receiptVerification": {"status": "receipt-verified"}, "k": 1}, v)
    assert stored["receiptVerification"] == v and rr.client_metadata(stored) == {"k": 1}


# ---------------------------------------------------------------------------
# PostgreSQL integration

pg = sim.pg
client = sim.client
USER, PROJECT = sim.USER, sim.PROJECT
MC = {"operation": "monte-carlo", "expression": "a*b + 2", "samples": 2000, "seed": 7,
      "inputs": [{"name": "a", "mean": 1.0, "standardDeviation": 0.1}, {"name": "b", "mean": 3.0, "standardDeviation": 0.2}]}
LIBS = {"source": "build-configuration", "runtime": "workbench 14.0.0", "numpy": "2.3.5", "precision": "ieee754-binary64"}


def adapter_body(seed=7, mean=5.0, sd=0.4):
    """What the Workbench adapter returns: the unchanged v11150 body with the seed echoed."""
    return {"ok": True, "schema": "sc-workbench-workspace-adapter-result/1.0", "runtime": "workbench-calculation-engine",
            "numericalLibraries": LIBS, "result": {
                "schema": "sc-workbench-uncertainty-propagation-monte-carlo-result/1.0", "operation": "monte-carlo",
                "result": {"output": {"count": 2000, "mean": mean, "standardDeviation": sd}, "samples": 2000, "seed": seed},
                "seed": seed}}


def model(client, model_id, op, mapping):
    return sim.post(client, "/v1/models", {"schema": "sc-workspace-model-record/1.0", "modelId": model_id, "projectId": PROJECT,
                                           "name": "Adapter model", "modelKind": "simulation", "executionTarget": "workspace",
                                           "executionOperation": op, "metadata": {"researchResultValues": mapping}})


def run_adapter(monkeypatch, client, op, body, mapping, params):
    import app.polyglot as polyglot
    from app.db import session_scope
    from app.registry import sync_run_from_job
    sfx = uuid4().hex[:8]
    m = model(client, f"ad-m-{sfx}", op, mapping)
    ps = sim.parameter_set(client, f"ad-p-{sfx}", m["modelId"], params)
    run_id = sim.post(client, "/v1/runs", {"schema": "sc-workspace-execution-run/1.0", "projectId": PROJECT, "operation": op,
                                           "modelRef": {"modelId": m["modelId"]},
                                           "parameterSetRef": {"parameterSetId": ps["parameterSetId"], "revision": ps["revision"]}})["runId"]
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        seen.update(url=url, envelope=json, headers=headers)
        return SimpleNamespace(status_code=200, json=lambda: body, text="")

    monkeypatch.setattr(polyglot.httpx, "post", fake_post)
    row = SimpleNamespace(operation=op, payload={"executionRunId": run_id, "payload": sim.pin(ps)}, user_key=USER,
                          job_id=f"job-{uuid4().hex[:10]}", project_id=PROJECT, request_fingerprint="d" * 64)
    with session_scope() as db:
        polyglot.execute_polyglot_operation(db, row)
        sync_run_from_job(db, USER, run_id, row.job_id, "succeeded", 100)
        db.commit()
    return run_id, seen


@pg
def test_workbench_monte_carlo_through_the_adapter_is_executed_verified(client, monkeypatch):
    mapping = {"kind": "scalar-paths", "paths": {"mean": "result.output.mean"},
               "standardErrors": {"mean": {"sdPath": "result.output.standardDeviation", "nPath": "result.output.count"}}}
    run_id, seen = run_adapter(monkeypatch, client, WB_MC, adapter_body(), mapping, MC)
    env = seen["envelope"]
    assert seen["url"].endswith("/v1/workspace/execute") and seen["headers"]["Authorization"] == "Bearer workbench-test"
    assert env["language"] == "workbench" and env["payload"] == MC and env["arbitraryCodeExecution"] is False
    doc = sim.export(client, run_id)
    v, values = doc["verification"], doc["resultValues"]
    assert v["status"] == "executed-verified" and v["inputLineage"] == VERIFIED
    (r,) = v["runtimeReceipts"]
    assert r["language"] == "workbench" and r["runtime"] == "workbench-calculation-engine" and r["runtimeVersion"] == "workbench 14.0.0"
    assert r["numericalLibraries"] == LIBS
    assert values["values"] == {"mean": 5.0} and values["stochastic"] == {"seed": 7}
    assert values["standardErrors"]["values"]["mean"] == pytest.approx(0.4 / 2000 ** 0.5)


@pg
def test_decision_studio_scenario_comparison_through_the_adapter(client, monkeypatch):
    body = {"ok": True, "schema": "scds-workspace-adapter-result/1.0", "runtime": "decision-studio-analysis",
            "decisionObjectsChanged": False, "recommendationProduced": False,
            "numericalLibraries": {"runtime": "decision-studio 3.15.0"},
            "result": {"scenarioComparison": {"diagnostics": {"max_score_swing": 41.5},
                                              "alternative_score_ranges": [{"alternative_id": "option-a", "span": 41.5}]}}}
    mapping = {"kind": "scalar-paths", "paths": {"maxSwing": "scenarioComparison.diagnostics.max_score_swing"}}
    run_id, seen = run_adapter(monkeypatch, client, DS_CMP, body, mapping, {"criteria": [{"criterion_id": "c"}]})
    assert seen["envelope"]["language"] == "decision-studio"
    doc = sim.export(client, run_id)
    assert doc["verification"]["status"] == "executed-verified" and doc["resultValues"]["values"] == {"maxSwing": 41.5}
    assert "stochastic" not in doc["resultValues"]


def project(client, project_id):
    sim.post(client, "/v1/projects", {"schema": "sc-workspace-cloud-backup/1.0", "sourceProjectId": project_id, "projectTitle": project_id,
                                      "project": {"schema": "sc-workspace-project/20.0", "id": project_id, "title": project_id, "objects": []}})


def scenario(client, project_id):
    return sim.post(client, "/v1/predictive-investigation-workspace/scenarios", {
        "schema": "sc-workspace-predictive-scenario-request/1.0", "projectId": project_id, "title": "Synthetic forecast scenario"})


def bind(client, scenario_id, ref, fingerprint, expect=200, metadata=None):
    r = client.post("/v1/predictive-investigation-workspace/result-bindings", headers=sim.hdr(USER), json={
        "schema": "sc-workspace-predictive-forecast-result-binding-request/1.0", "scenarioId": scenario_id,
        "resultKind": "forecast", "resultRef": ref, "resultFingerprint": fingerprint, "metadata": metadata or {}})
    assert r.status_code == expect, r.text
    return r.json().get("item", r.json())


@pg
def test_predictive_result_bindings_are_checked_against_run_receipts(client, monkeypatch):
    project(client, PROJECT)
    sc = scenario(client, PROJECT)["scenarioId"]
    mapping = {"kind": "scalar-paths", "paths": {"mean": "result.output.mean"}}
    run_id, _ = run_adapter(monkeypatch, client, WB_MC, adapter_body(), mapping, MC)
    receipt = sim.export(client, run_id)["verification"]["runtimeReceipts"][0]
    ok = bind(client, sc, f"workspace-run:{run_id}", receipt["resultSha256"],
              metadata={"receiptVerification": {"status": "receipt-verified", "forged": True}, "note": "client"})
    v = ok["receiptVerification"]
    assert v["status"] == "receipt-verified" and v["runId"] == run_id and v["receiptId"] == receipt["receiptId"]
    assert v["inputLineage"] == VERIFIED and "forged" not in v and ok["metadata"] == {"note": "client"}
    # Wrong fingerprint, unknown run, and a run that has not executed are refused.
    assert bind(client, sc, f"workspace-run:{run_id}", "e" * 64, expect=409)["detail"]["code"] == "result-fingerprint-does-not-match-receipt"
    assert bind(client, sc, "workspace-run:run-missing", "e" * 64, expect=404)["detail"]["code"] == "result-run-not-found"
    idle = sim.post(client, "/v1/runs", {"schema": "sc-workspace-execution-run/1.0", "projectId": PROJECT, "operation": WB_MC})["runId"]
    assert bind(client, sc, f"workspace-run:{idle}", "e" * 64, expect=409)["detail"]["code"] == "result-run-not-executed-verified"
    # Anything else is recorded, but only as a client assertion.
    ext = bind(client, sc, "https://example.test/forecast.csv", "f" * 64)
    assert ext["receiptVerification"]["status"] == "client-asserted"
    listed = client.get(f"/v1/predictive-investigation-workspace/result-bindings?scenarioId={sc}", headers=sim.hdr(USER)).json()
    statuses = sorted(x["receiptVerification"]["status"] for x in listed.get("items", listed.get("item", [])))
    assert statuses == ["client-asserted", "receipt-verified"]


@pg
def test_another_owners_run_cannot_be_bound(client, monkeypatch):
    project(client, PROJECT)
    mapping = {"kind": "scalar-paths", "paths": {"mean": "result.output.mean"}}
    run_id, _ = run_adapter(monkeypatch, client, WB_MC, adapter_body(), mapping, MC)
    receipt = sim.export(client, run_id)["verification"]["runtimeReceipts"][0]
    other = "sim-owner-b"
    sim.post(client, "/v1/projects", {"schema": "sc-workspace-cloud-backup/1.0", "sourceProjectId": PROJECT, "projectTitle": PROJECT,
                                      "project": {"schema": "sc-workspace-project/20.0", "id": PROJECT, "title": PROJECT, "objects": []}},
             user=other)
    sc = sim.post(client, "/v1/predictive-investigation-workspace/scenarios", {
        "schema": "sc-workspace-predictive-scenario-request/1.0", "projectId": PROJECT, "title": "B"}, user=other)["scenarioId"]
    r = client.post("/v1/predictive-investigation-workspace/result-bindings", headers=sim.hdr(other), json={
        "schema": "sc-workspace-predictive-forecast-result-binding-request/1.0", "scenarioId": sc, "resultKind": "forecast",
        "resultRef": f"workspace-run:{run_id}", "resultFingerprint": receipt["resultSha256"]})
    assert r.status_code == 404 and r.json()["detail"]["code"] == "result-run-not-found"
