"""SC-FIG-02B: sc.figure-bundle.v1 + Vega-Lite view from a verified notebook cell run. Synthetic data only.

Set SC_FIG02B_PACKAGE_OUT to a directory to also write the integration package there (files plus
EXPECTED.json) for the Lab Graph Studio cross-check (Lab tests/staging/fig02b_wordpress_acceptance.py --package).
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from test_input_integrity_sc_nb01 import client, hdr  # noqa: F401 (client is a fixture)
from test_notebook_export_sc_nb01 import executed, pg

from app import notebook_figure_bundle as fb  # noqa: E402

COEFFICIENTS = {"coefficients": [{"term": "(Intercept)", "estimate": 1.5, "stdError": 0.1},
                                 {"term": "x", "estimate": 0.25, "stdError": 0.01}]}


def request(**kw):
    body = {
        "figureId": "SYN-NB-coefficients", "title": "SYNTHETIC regression coefficients with 95% intervals",
        "rowsPath": "coefficients", "mark": "point",
        "x": {"field": "term", "label": "Model term", "unit": "category", "type": "nominal"},
        "y": {"field": "estimate", "label": "Coefficient estimate", "unit": "1"},
        "uncertainty": {"kind": "ci95", "spreadField": "stdError", "multiplier": 1.959964},
        "evidenceClass": "modelled",
        "caption": "SYNTHETIC: fitted coefficients of y ~ x with 95% confidence intervals.",
        "altText": "Two points, intercept 1.5 and slope 0.25, each with a short 95% interval bar.",
        "interpretation": "Synthetic regression output used to exercise the notebook figure path.",
        "limitations": ["Synthetic data with no scientific meaning"],
    }
    body.update(kw)
    return fb.FigureRequest(**body)


def evidence(bindings=None, lineage="artifact-bound-verified"):
    run = SimpleNamespace(finished_at=datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc), created_at=None,
                          input_fingerprint="a" * 64, project_id="nb-proj")
    return {"runId": "run-1", "_run": run, "verification": {
        "status": "executed-verified", "inputLineage": lineage,
        "inputBindings": bindings if bindings is not None else [
            {"datasetId": "ds-1", "datasetRevision": 1, "artifactSha256": "b" * 64}],
        "runtimeReceipts": [{"receiptId": "rcpt-1", "language": "r", "runtime": "R 4.5", "operation": "regression.lm",
                             "resultSha256": "c" * 64}]}}


REV = SimpleNamespace(notebook_id="nb-x", revision=1, project_id="nb-proj")


def files(pkg):
    return {f["role"]: f for f in pkg["files"]}


# ---------------------------------------------------------------------------
# Unit


def test_package_binds_view_dataset_run_and_sources():
    pkg = fb.build_package(REV, "fit", "d" * 64, evidence(), COEFFICIENTS, request())
    f = files(pkg)
    bundle, view = json.loads(f["bundle"]["text"]), json.loads(f["view"]["text"])
    assert pkg["bundleSha256"] == hashlib.sha256(f["bundle"]["text"].encode()).hexdigest() == f["bundle"]["sha256"]
    assert bundle["artifacts"][0]["sha256"] == fb.canonical_sha256(view) == bundle["rendering"]["visualizationSpecSha256"]
    sc = view["usermeta"]["sc"]
    assert sc["profile"] == "sc-vega-lite-v1" and sc["datasetSha256"] == fb.canonical_sha256(view["data"]["values"])
    run_calc, projection = bundle["calculationRefs"]
    assert run_calc["outputSha256"] == "c" * 64 and "receipt rcpt-1" in run_calc["method"] and "cell fit" in run_calc["method"]
    assert projection["outputSha256"] == sc["datasetSha256"] and projection["assumptionRefs"] == ["workspace-run:run-1"]
    assert "lower = estimate − 1.959964 × stdError, upper = estimate + 1.959964 × stdError" in projection["method"]
    rows = view["data"]["values"]
    assert rows[1] == {"term": "x", "estimate": 0.25, "lower": 0.23040036, "upper": 0.26959964, "evidenceClass": "modelled"}
    assert bundle["evidenceClass"] == "modelled" and bundle["scientificContext"]["measurementStatus"] == "computed-from-specified-inputs"
    assert bundle["provenance"]["reproducibility"] == "not-tested" and bundle["provenance"]["generatedAt"] == "2026-11-11T12:00:00Z"
    src = bundle["sourceRefs"][0]
    assert src["sha256"] == "b" * 64 and src["identityStatus"] == "source-hash-verified"
    assert src["licenceStatus"] == "pending" and src["qualityStatus"] == "pending"
    assert bundle["publication"]["bindingStatus"] == "unbound" and set(bundle["review"].values()) == {"pending"}
    assert pkg["stored"] is False and pkg["published"] is False
    layers = view["layer"]
    assert layers[0]["mark"] == {"type": "errorbar", "ticks": False} and layers[0]["encoding"]["y"]["field"] == "lower"
    assert layers[1]["mark"]["type"] == "point"
    assert sc["fields"]["lower"]["unit"] == sc["fields"]["estimate"]["unit"] == "1" and sc["uncertainty"]["kind"] == "ci95"
    # Lab requires the per-row evidence field to be described like any other field.
    assert sc["evidenceField"] == "evidenceClass" and sc["fields"]["evidenceClass"] == {"label": "Evidence class", "unit": "category"}


def test_package_is_deterministic():
    a = fb.build_package(REV, "fit", "d" * 64, evidence(), COEFFICIENTS, request())
    b = fb.build_package(REV, "fit", "d" * 64, evidence(), json.loads(json.dumps(COEFFICIENTS)), request())
    assert a == b


def test_never_observed_or_literature():
    for cls in ("observed", "literature-derived", "conceptual"):
        with pytest.raises(ValidationError):
            request(evidenceClass=cls)


def test_unverified_input_is_only_source_identified_and_a_figure_needs_a_source():
    pkg = fb.build_package(REV, "fit", "d" * 64, evidence(lineage="inline-unverified"), COEFFICIENTS, request())
    assert json.loads(files(pkg)["bundle"]["text"])["sourceRefs"][0]["identityStatus"] == "source-identified"
    with pytest.raises(HTTPException) as exc:
        fb.build_package(REV, "fit", "d" * 64, evidence(bindings=[]), COEFFICIENTS, request())
    assert exc.value.detail["code"] == "figure-no-source"


@pytest.mark.parametrize("kw,result,code", [
    ({"rowsPath": "missing"}, COEFFICIENTS, "figure-rows-not-found"),
    ({}, {"coefficients": {"term": "x"}}, "figure-rows-invalid"),
    ({}, {"coefficients": [{"term": "x", "estimate": "high", "stdError": 0.1}]}, "figure-field-not-numeric"),
    ({}, {"coefficients": [{"term": "x", "stdError": 0.1}]}, "figure-field-missing"),
    ({"uncertainty": {"kind": "ci95", "spreadField": "stdError"}}, COEFFICIENTS, "figure-uncertainty-invalid"),
    ({"uncertainty": {"kind": "none", "spreadField": "stdError"}}, COEFFICIENTS, "figure-uncertainty-invalid"),
    ({"y": {"field": "term", "label": "Term", "unit": "category", "type": "nominal"}}, COEFFICIENTS, "figure-fields-invalid"),
    ({"x": {"field": "evidenceClass", "label": "Class", "unit": "category", "type": "nominal"}}, COEFFICIENTS, "figure-fields-invalid"),
])
def test_refusals(kw, result, code):
    with pytest.raises(HTTPException) as exc:
        fb.build_package(REV, "fit", "d" * 64, evidence(), result, request(**kw))
    assert exc.value.status_code == 422 and exc.value.detail["code"] == code


def test_polyglot_envelope_is_unwrapped():
    wrapped = {"schema": "sc-workspace-polyglot-result/1.0", "language": "r",
               "result": {"envelopeFingerprint": "e" * 64, "remote": {"result": COEFFICIENTS}}}
    assert fb.build_package(REV, "fit", "d" * 64, evidence(), wrapped, request()) == \
        fb.build_package(REV, "fit", "d" * 64, evidence(), COEFFICIENTS, request())


def test_line_figures_draw_an_error_band_and_explicit_bounds_are_kept():
    rows = {"series": [{"t": 0, "v": 1.0, "lo": 0.8, "hi": 1.2}, {"t": 1, "v": 1.4, "lo": 1.1, "hi": 1.7}]}
    req = request(rowsPath="series", mark="line", x={"field": "t", "label": "Time", "unit": "year"},
                  y={"field": "v", "label": "Value", "unit": "t ha-1"},
                  uncertainty={"kind": "pi95", "lowerField": "lo", "upperField": "hi", "statement": "Synthetic 95% prediction interval."},
                  evidenceClass="hypothetical")
    pkg = fb.build_package(REV, "fit", "d" * 64, evidence(), rows, req)
    view = json.loads(files(pkg)["view"]["text"])
    assert view["layer"][0]["mark"]["type"] == "errorband" and view["layer"][0]["encoding"]["y"]["title"] == "Value (t ha-1)"
    assert view["data"]["values"][0]["lower"] == 0.8 and view["usermeta"]["sc"]["uncertainty"]["statement"] == "Synthetic 95% prediction interval."
    assert json.loads(files(pkg)["bundle"]["text"])["scientificContext"]["measurementStatus"] == "hypothetical-only"


# ---------------------------------------------------------------------------
# PostgreSQL integration

BODY = request().model_dump(exclude_none=True)


def post(client, user, nb_id, cell, body=BODY, revision=1, expect=200):
    r = client.post(f"/v1/notebooks/{nb_id}/revisions/{revision}/cells/{cell}/figure-bundle", json=body, headers=hdr(user))
    assert r.status_code == expect, r.text
    return r


@pg
def test_verified_run_becomes_a_figure_package(client, monkeypatch):
    nb_id, art, ds, plan = executed(client, monkeypatch, with_scenario=False)
    r = post(client, "nb-owner-a", nb_id, "fit")
    pkg = r.json()
    assert r.headers["X-SC-Figure-Bundle-Sha256"] == pkg["bundleSha256"] and r.headers["Cache-Control"] == "no-store"
    assert post(client, "nb-owner-a", nb_id, "fit").content == r.content  # deterministic
    fit = plan["steps"][0]
    assert pkg["run"]["runId"] == fit["runId"] and pkg["run"]["verification"] == "executed-verified"
    assert pkg["run"]["inputLineage"] == "artifact-bound-verified"
    f = files(pkg)
    bundle, view = json.loads(f["bundle"]["text"]), json.loads(f["view"]["text"])
    assert bundle["sourceRefs"][0]["sha256"] == art["sha256"] and bundle["sourceRefs"][0]["sourceId"] == f"workspace-dataset:{ds['datasetId']}@r1"
    assert bundle["calculationRefs"][0]["outputSha256"] == pkg["run"]["resultSha256"]
    assert [r["term"] for r in view["data"]["values"]] == ["(Intercept)", "x"]
    assert bundle["project"] == {"projectRef": "workspace-project:nb-proj", "ownerScope": "authenticated",
                                 "environment": bundle["project"]["environment"]}
    out = os.getenv("SC_FIG02B_PACKAGE_OUT")
    if out:
        d = Path(out)
        d.mkdir(parents=True, exist_ok=True)
        for item in pkg["files"]:
            (d / item["name"]).write_text(item["text"], encoding="utf-8")
        (d / "EXPECTED.json").write_text(json.dumps({"bundle": f["bundle"]["name"], "bundleSha256": pkg["bundleSha256"]}) + "\n")


@pg
def test_figure_package_refusals_and_owner_scope(client, monkeypatch):
    nb_id, *_ = executed(client, monkeypatch, with_scenario=False)
    post(client, "nb-owner-b", nb_id, "fit", expect=404)  # foreign notebook looks absent
    post(client, "nb-owner-a", nb_id, "q", expect=404)  # markdown cell
    post(client, "nb-owner-a", nb_id, "nope", expect=404)
    post(client, "nb-owner-a", nb_id, "fit", revision=9, expect=404)
    r = post(client, "nb-owner-a", nb_id, "replay", expect=422)  # Julia result is a solution vector, not records
    assert r.json()["code"] == "figure-rows-not-found"
    post(client, "nb-owner-a", nb_id, "fit", body={**BODY, "evidenceClass": "observed"}, expect=422)
    post(client, "nb-owner-a", nb_id, "fit", body={**BODY, "script": "<script>"}, expect=422)
