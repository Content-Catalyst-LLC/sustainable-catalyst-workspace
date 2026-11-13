"""SC-SCI-01 notebook workspace: the page, and the owner's per-cell status read. Synthetic data only.

PostgreSQL tests drive the real notebook plan routes, worker job processing, registry and receipts; only the
runtime HTTP calls are stubbed (the SC-NB-01 upstream-binding fakes: an OLS fit, a normal-equations replay and
a minimax-regret ranking).
"""
import re
from pathlib import Path

import pytest

from test_input_integrity_sc_nb01 import client, hdr  # noqa: F401 (client is a fixture)
from test_notebook_cell_runs_sc_nb01 import store_notebook
from test_upstream_binding_sc_nb01 import chain_notebook, fake_runtimes, pg, run_through, setup_chain

from app import notebook_desk as nd  # noqa: E402

STATIC = Path(nd.__file__).resolve().parent / "static" / "notebook_desk"


def status(client, user, nb_id, expect=200):
    r = client.get(f"/v1/notebooks/{nb_id}/cell-status", headers=hdr(user))
    assert r.status_code == expect, r.text
    return r.json()


def by_cell(doc):
    return {c["cellId"]: c for c in doc["cells"]}


# ---------------------------------------------------------------------------
# Unit


@pytest.mark.parametrize("step,plan_status,verification,claim,expected", [
    (None, "", None, None, "not-run"),
    ({"state": "queued", "runId": "r1"}, "running", {"status": "incomplete"}, None, "running"),
    ({"state": "pending", "runId": ""}, "running", None, None, "running"),
    ({"state": "pending", "runId": ""}, "failed", None, None, "not-run"),
    ({"state": "failed", "runId": "r1"}, "failed", {"status": "failed"}, {"verified": True}, "failed"),
    ({"state": "succeeded", "runId": "r1"}, "succeeded", {"status": "succeeded-without-runtime-receipt"}, {"verified": True}, "unverified"),
    ({"state": "succeeded", "runId": "r1"}, "succeeded", {"status": "executed-verified"}, {"verified": False}, "unverified"),
    ({"state": "succeeded", "runId": "r1"}, "succeeded", {"status": "executed-verified"},
     {"verified": True, "currency": {"current": False}}, "stale"),
    ({"state": "succeeded", "runId": "r1"}, "succeeded", {"status": "executed-verified"},
     {"verified": True, "currency": {"current": True}}, "verified"),
])
def test_state_labels(step, plan_status, verification, claim, expected):
    assert nd._state(step, plan_status, verification, claim) == expected


def test_page_and_assets_are_static_same_origin_with_a_strict_policy(client):
    page = client.get("/v1/desk/notebooks")
    assert page.status_code == 200 and page.headers["content-type"].startswith("text/html")
    csp = page.headers["content-security-policy"]
    assert "script-src 'self'" in csp and "connect-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert "<script type=\"module\" src=\"/v1/desk/notebook-assets/notebook-desk.js\"></script>" in page.text
    assert "<script>" not in page.text and not re.search(r"\son[a-z]+=", page.text)  # no inline script or handlers
    for name in nd.ASSETS:
        r = client.get(f"/v1/desk/notebook-assets/{name}")
        assert r.status_code == 200 and r.headers["x-content-type-options"] == "nosniff", name
    for bad in ("index.html", "../notebook_desk.py", "approval-desk.js", "%2e%2e%2fnotebook_desk.py"):
        assert client.get(f"/v1/desk/notebook-assets/{bad}").status_code == 404, bad


def test_page_holds_no_credential_and_uses_only_same_origin_calls():
    js = (STATIC / "notebook-desk.js").read_text() + (STATIC / "notebook-recipes.js").read_text()
    for forbidden in ("Authorization", "X-SC-User-ID", "localStorage", "sessionStorage", "innerHTML", "eval(", "http://", "https://"):
        assert forbidden not in js, forbidden
    assert 'credentials: "same-origin"' in js


# ---------------------------------------------------------------------------
# PostgreSQL


@pg
def test_cell_status_reports_verified_values_and_then_staleness_after_an_upstream_edit(client, monkeypatch):
    fake_runtimes(monkeypatch)
    ctx = setup_chain(client)
    before = by_cell(status(client, ctx.user, ctx.nb_id))
    assert {c: before[c]["state"] for c in before} == {"fit": "not-run", "replay": "not-run", "scenario": "not-run"}

    plan = run_through(client, ctx)
    assert plan["status"] == "succeeded", plan
    doc = status(client, ctx.user, ctx.nb_id)
    assert doc["schema"] == "sc-workspace-notebook-cell-status/1.0" and doc["headRevision"] == 1
    cells = by_cell(doc)
    assert {c: cells[c]["state"] for c in cells} == {"fit": "verified", "replay": "verified", "scenario": "verified"}
    fit, replay = cells["fit"], cells["replay"]
    assert fit["run"]["verification"]["status"] == "executed-verified"
    assert fit["run"]["verification"]["inputLineage"] == "artifact-bound-verified"
    assert fit["run"]["verification"]["inputBindings"][0]["artifactSha256"] == ctx.art["sha256"]
    assert set(fit["run"]["resultValues"]["values"]) == {"intercept", "slope"}
    assert set(fit["run"]["resultValues"]["uncertainty"]["values"]) == {"intercept", "slope"}
    assert fit["run"]["resultValues"]["values"]["slope"] == pytest.approx(replay["run"]["resultValues"]["values"]["slope"], rel=1e-9)
    assert cells["scenario"]["run"]["verification"]["inputBindings"][0]["kind"] == "upstream-cell"
    assert cells["scenario"]["run"]["upstreamCellSha256"] == {"fit": fit["cellSha256"], "replay": replay["cellSha256"]}

    # Editing the upstream fit makes the fit and every cell planned after it stale (here the replay is ordered after the fit).
    store_notebook(client, ctx.user, ctx.nb_id, chain_notebook(
        ctx.ds["datasetId"], ctx.m_r, ctx.m_j, r_source="# documented\nfit <- lm(y ~ x, data = rows)"), expected=1)
    cells = by_cell(status(client, ctx.user, ctx.nb_id))
    assert cells["fit"]["state"] == "stale" and cells["fit"]["currency"]["reasons"] == ["cell-changed"]
    assert cells["scenario"]["state"] == "stale"
    assert cells["scenario"]["currency"]["reasons"] == ["upstream-changed"]
    assert cells["scenario"]["currency"]["changedUpstreamCells"] == ["fit"]
    assert cells["replay"]["state"] == "stale" and cells["replay"]["currency"]["changedUpstreamCells"] == ["fit"]

    # Rerunning revision 2 makes everything current again.
    assert run_through(client, ctx)["status"] == "succeeded"
    cells = by_cell(status(client, ctx.user, ctx.nb_id))
    assert {c: cells[c]["state"] for c in cells} == {"fit": "verified", "replay": "verified", "scenario": "verified"}
    assert all(cells[c]["plan"]["notebookRevision"] == 2 for c in cells)


@pg
def test_cell_status_is_owner_scoped_and_reports_failures(client, monkeypatch):
    fake_runtimes(monkeypatch, julia_bias=0.5)  # the cross-check disagrees, so the scenario refuses to bind
    ctx = setup_chain(client)
    status(client, "nb-owner-b", ctx.nb_id, expect=404)
    status(client, ctx.user, "no-such-notebook", expect=404)
    run_through(client, ctx)
    cells = by_cell(status(client, ctx.user, ctx.nb_id))
    assert cells["fit"]["state"] == "verified" and cells["replay"]["state"] == "verified"
    assert cells["scenario"]["state"] == "failed" and cells["scenario"]["run"]["runStatus"] == "failed"
    assert cells["scenario"]["run"]["resultValues"] is None
