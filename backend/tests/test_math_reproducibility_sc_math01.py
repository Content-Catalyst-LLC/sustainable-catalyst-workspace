"""SC-MATH-01: symbolic identity checks at declared points, canonical root/eigenvalue order, and numerical
library identity on receipts.

Unit tests always run. The Julia cross-check runs the real runner when SC_TEST_JULIA_PROJECT names a Julia
project with JSON3. PostgreSQL tests (real registry routes and the real executors, with only the Julia HTTP
call stubbed) run when SC_WORKSPACE_DATABASE_URL points at a disposable PostgreSQL database. Synthetic data only.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import numpy as np
import pytest

import tests.test_simulation_inputs_sc_sim01 as sim  # noqa: F401  (sets the test environment first)
from fastapi import HTTPException

from app import compute as c
from app import research_exports as rx
from app.input_integrity import VERIFIED
from app.polyglot import JULIA_MODEL_OPERATIONS, RUNTIMES

BACKEND = Path(__file__).resolve().parents[1]
RUNNER = BACKEND / "julia-runtime" / "runner.jl"
EXPR = "x^3 - 2*sin(x)*exp(y) + sqrt(x)/y"
POINTS = [{"x": 1.5, "y": 0.5}, {"x": 2, "y": -1.25}, {"x": 0.25, "y": 3}]


def symbolic(**over):
    return c._symbolic({"expression": EXPR, "variables": ["x", "y"], "action": "differentiate", "variable": "x",
                        "evaluateAt": POINTS, **over}, None)


# ---------------------------------------------------------------------------
# M2: canonical ordering


def test_canonical_order_sorts_real_then_imaginary_with_a_real_tie_band():
    vals = [1 + 0j, -0.5 + 0.866j, -0.5 - 0.866j, -2 + 0j]
    assert c.canonical_order(vals) == [3, 2, 1, 0]
    # Rounding noise in the real part of a conjugate pair must not reorder it.
    noisy = [complex(-0.5 + 1e-15, 0.866), complex(-0.5, -0.866)]
    assert c.canonical_order(noisy) == [1, 0]


def test_roots_and_eigen_are_canonically_ordered_and_say_so():
    roots = c._roots_polynomial({"coefficients": [1, 0, 0, -1]}, None)
    assert [r["imag"] < 0 for r in roots["roots"]] == [True, False, False]
    assert roots["ordering"] == c.ORDERING
    a = np.array([[0, -1, 0], [1, 0, 0], [0, 0, -2]], dtype=float)
    eig = c._linear_algebra({"action": "eigen", "a": a.tolist()}, None)
    vals = [complex(v["real"], v["imag"]) for v in eig["eigenvalues"]]
    assert vals == sorted(vals, key=lambda z: (z.real, z.imag)) and eig["ordering"] == c.ORDERING
    # Eigenvectors are permuted with their eigenvalues (columns).
    vecs = np.array([[complex(v["real"], v["imag"]) for v in row] for row in eig["eigenvectors"]])
    for k, lam in enumerate(vals):
        assert np.allclose(a @ vecs[:, k], lam * vecs[:, k])


# ---------------------------------------------------------------------------
# M1: symbolic identity at declared points


def test_symbolic_result_is_evaluated_at_declared_points_and_never_called_a_proof():
    out = symbolic()
    assert out["identityCheck"]["method"] == c.IDENTITY_METHOD and out["identityCheck"]["proof"] is False
    assert out["identityCheck"]["pointCount"] == 3 and out["identityCheck"]["variable"] == "x"
    x, y = 1.5, 0.5
    expected = 3 * x**2 - 2 * np.cos(x) * np.exp(y) + 1 / (2 * np.sqrt(x) * y)
    assert out["values"][0] == pytest.approx(expected, rel=1e-14)
    assert c._symbolic({"expression": "(x+1)^2 - x^2 - 2*x", "variables": ["x"], "action": "simplify",
                        "evaluateAt": [{"x": 3.0}]}, None)["values"] == [1.0]
    # Without evaluateAt the operation is unchanged.
    assert "identityCheck" not in c._symbolic({"expression": "x^2", "variables": ["x"], "action": "simplify"}, None)


@pytest.mark.parametrize("over,status", [
    ({"action": "integrate"}, 400), ({"action": "solve"}, 400), ({"order": 2}, 400),
    ({"evaluateAt": []}, 400), ({"evaluateAt": [{"x": 1.0}]}, 400), ({"evaluateAt": [{"x": 1.0, "y": True}]}, 400),
    ({"evaluateAt": [{"x": float("inf"), "y": 1.0}]}, 400), ({"evaluateAt": [{"x": -1.0, "y": 1.0}]}, 422),
    ({"evaluateAt": [{"x": 1.0, "y": 1.0}] * (c.MAX_IDENTITY_POINTS + 1)}, 400),
])
def test_identity_check_refusals(over, status):
    with pytest.raises(HTTPException) as e:
        symbolic(**over)
    assert e.value.status_code == status


# ---------------------------------------------------------------------------
# M4: numerical library identity


def test_numerical_libraries_name_versions_blas_lapack_and_precision():
    libs = c.numerical_libraries()
    assert libs["numpy"] == np.__version__ and libs["precision"] == "ieee754-binary64"
    assert libs["source"] == "build-configuration" and set(libs["blas"]) == {"name", "version"} and "lapack" in libs


def test_export_carries_identity_check_and_ordering_but_forces_proof_false():
    doc = {"result": {"values": [1.0, 2.0], "identityCheck": {"method": c.IDENTITY_METHOD, "proof": True, "pointCount": 2,
                                                               "action": "evaluate", "variable": "", "extra": "x"}}}
    mapping = {"kind": "scalar-paths", "paths": {"f0": "result.values.0", "f1": "result.values.1"}}
    out = rx.extract_result_values(mapping, doc)
    assert out["values"] == {"f0": 1.0, "f1": 2.0}
    assert out["identityCheck"] == {"method": c.IDENTITY_METHOD, "proof": False, "action": "evaluate", "pointCount": 2, "variable": ""}
    jdoc = {"result": {"remote": {"result": {"roots": [[-1.0, 0.0]], "ordering": c.ORDERING}}}}
    out = rx.extract_result_values({"kind": "scalar-paths", "paths": {"r0": "roots.0.0"}}, jdoc)
    assert out["ordering"] == {"method": "real-then-imaginary", "realTieRelative": 1e-9}
    assert "identityCheck" not in rx.extract_result_values(
        mapping, {"result": {"values": [1.0, 2.0], "identityCheck": {"method": "proof"}}})


def test_compute_receipt_projects_as_an_in_process_python_receipt():
    row = SimpleNamespace(receipt_id="compute-receipt-j", job_id="j", operation="workspace.compute.symbolic", engine="sympy",
                          engine_version="1.14.0", request_fingerprint="f" * 64, result_artifact_id="a", result_sha256="s" * 64,
                          metadata_json={"inputLineage": VERIFIED, "numericalLibraries": {"sympy": "1.14.0"}})
    r = rx._compute_receipt(row)
    assert (r.language, r.runtime, r.transport, r.status) == ("python", "cpython-scientific", "in-process", "succeeded")
    assert r.runtime_version == "sympy 1.14.0" and r.numerical_libraries == {"sympy": "1.14.0"}
    assert r.details_json["inputLineage"] == VERIFIED


# ---------------------------------------------------------------------------
# Julia runner: registration, static safety, and a real cross-implementation check


def test_expression_evaluate_is_registered_everywhere():
    op = "workspace.polyglot.julia.expression-evaluate"
    assert op in next(r for r in RUNTIMES if r.language == "julia").operations and op in JULIA_MODEL_OPERATIONS
    assert f'"{op}"' in (BACKEND / "julia-runtime" / "service.py").read_text()
    schema = json.loads((BACKEND.parent / "schemas" / "sc-workspace-julia-simulation-runtime-v1.schema.json").read_text())
    assert op in json.dumps(schema)


def test_julia_runner_never_parses_or_evaluates_julia_code():
    runner = RUNNER.read_text()
    for unsafe in ("eval(", "Meta.parse(", "include_string", "run(`", "pipeline(", "ccall"):
        assert unsafe not in runner
    assert "recursive-descent" in runner and '"numericalLibraries"=>numerical_libraries()' in runner


def run_julia(tmp_path, operation, payload):
    project = os.environ.get("SC_TEST_JULIA_PROJECT", "")
    julia = shutil.which("julia")
    if not project or not julia:
        pytest.skip("needs julia and SC_TEST_JULIA_PROJECT with JSON3")
    src, dst = tmp_path / "in.json", tmp_path / "out.json"
    src.write_text(json.dumps({"operation": operation, "payload": payload}))
    done = subprocess.run([julia, "--startup-file=no", f"--project={project}", str(RUNNER), str(src), str(dst)],
                          capture_output=True, text=True, timeout=300, check=False)
    if done.returncode != 0:
        return {"error": done.stderr}
    return json.loads(dst.read_text())


def test_julia_and_sympy_agree_at_declared_points(tmp_path):
    payload = {"expression": EXPR, "variables": ["x", "y"], "action": "differentiate", "variable": "x", "evaluateAt": POINTS}
    out = run_julia(tmp_path, "workspace.polyglot.julia.expression-evaluate", payload)
    julia_vals, sympy_vals = out["result"]["values"], symbolic()["values"]
    assert out["result"]["identityCheck"]["proof"] is False and out["result"]["solver"] == "forward-mode-dual"
    for a, b in zip(julia_vals, sympy_vals):
        assert a == pytest.approx(b, rel=1e-12)
    libs = out["numericalLibraries"]
    assert libs["source"] == "runtime-loaded" and libs["julia"] and libs["precision"] == "ieee754-binary64"


@pytest.mark.parametrize("expression", ["run(x)", "x; rm", "x.y", "1.5e-3*x", "log(x, 2)", "x[1]", "`x`"])
def test_julia_refuses_outside_the_shared_grammar(tmp_path, expression):
    out = run_julia(tmp_path, "workspace.polyglot.julia.expression-evaluate",
                    {"expression": expression, "variables": ["x"], "evaluateAt": [{"x": 1.0}]})
    assert "error" in out


def test_julia_and_numpy_roots_share_one_order(tmp_path):
    out = run_julia(tmp_path, "workspace.polyglot.julia.polynomial-roots", {"coefficients": [1, -2, 3, -4, 5]})
    py = c._roots_polynomial({"coefficients": [1, -2, 3, -4, 5]}, None)["roots"]
    for (re_, im_), p in zip(out["result"]["roots"], py):
        assert re_ == pytest.approx(p["real"], abs=1e-12) and im_ == pytest.approx(p["imag"], abs=1e-12)


# ---------------------------------------------------------------------------
# PostgreSQL: an in-process SymPy result bound to a ParameterSet becomes exportable


pg = sim.pg
client = sim.client
USER, PROJECT = sim.USER, sim.PROJECT


def math_model(client, model_id, operation, mapping):
    return sim.post(client, "/v1/models", {"schema": "sc-workspace-model-record/1.0", "modelId": model_id, "projectId": PROJECT,
                                           "name": "Symbolic identity check", "modelKind": "symbolic",
                                           "executionTarget": "workspace", "executionOperation": operation,
                                           "metadata": {"researchResultValues": mapping}})


def math_run(client, model_id, operation, ps):
    return sim.post(client, "/v1/runs", {"schema": "sc-workspace-execution-run/1.0", "projectId": PROJECT, "operation": operation,
                                         "modelRef": {"modelId": model_id},
                                         "parameterSetRef": {"parameterSetId": ps["parameterSetId"], "revision": ps["revision"]}})["runId"]


def run_compute(run_id, operation, payload):
    from app.db import session_scope
    from app.registry import sync_run_from_job
    row = SimpleNamespace(operation=operation, payload={"executionRunId": run_id, "payload": payload}, user_key=USER,
                          job_id=f"job-{uuid4().hex[:10]}", project_id=PROJECT, execution_run_id=run_id)
    with session_scope() as db:
        c.execute_scientific_operation(db, row)
        sync_run_from_job(db, USER, run_id, row.job_id, "succeeded", 100)
        db.commit()


@pg
def test_sympy_identity_check_is_executed_verified_with_bound_inputs(client):
    rx._key.cache_clear()
    sfx = uuid4().hex[:8]
    op = "workspace.compute.symbolic"
    mapping = {"kind": "scalar-paths", "paths": {f"d{i}": f"result.values.{i}" for i in range(3)},
               "tolerance": {"relative": 1e-12, "absolute": 1e-14}}
    m = math_model(client, f"math-m-{sfx}", op, mapping)
    params = {"expression": EXPR, "variables": ["x", "y"], "action": "differentiate", "variable": "x", "evaluateAt": POINTS}
    ps = sim.parameter_set(client, f"math-p-{sfx}", m["modelId"], params)
    run_id = math_run(client, m["modelId"], op, ps)
    run_compute(run_id, op, sim.pin(ps))
    doc = sim.export(client, run_id)
    v, values = doc["verification"], doc["resultValues"]
    assert v["status"] == "executed-verified" and v["inputLineage"] == VERIFIED
    (r,) = v["runtimeReceipts"]
    assert r["language"] == "python" and r["transport"] == "in-process" and r["runtimeVersion"].startswith("sympy ")
    assert r["numericalLibraries"]["sympy"] and r["numericalLibraries"]["precision"] == "ieee754-binary64"
    assert values["values"]["d0"] == pytest.approx(symbolic()["values"][0], rel=1e-15)
    assert values["identityCheck"]["proof"] is False and values["identityCheck"]["pointCount"] == 3
    assert v["inputBindings"][0]["parameterSetFingerprint"] == ps["fingerprint"]


@pg
def test_inline_compute_input_stays_unverified(client):
    rx._key.cache_clear()
    sfx = uuid4().hex[:8]
    op = "workspace.compute.roots-polynomial"
    m = math_model(client, f"math-r-{sfx}", op, {"kind": "scalar-paths", "paths": {"r0": "result.roots.0.real"}})
    ps = sim.parameter_set(client, f"math-q-{sfx}", m["modelId"], {"coefficients": [1, 0, -1]})
    run_id = math_run(client, m["modelId"], op, ps)
    run_compute(run_id, op, {"coefficients": [1, 0, -1]})  # inline: same numbers, but not the attested revision
    doc = sim.export(client, run_id)
    assert doc["verification"]["status"] == "executed-verified"
    assert doc["verification"]["inputLineage"] == "inline-unverified" and doc["resultValues"]["values"] == {"r0": -1.0}
    assert doc["resultValues"]["ordering"]["method"] == "real-then-imaginary"


@pg
def test_julia_receipt_keeps_reported_library_identity(client, monkeypatch):
    import app.polyglot as polyglot
    from app.db import session_scope
    from app.registry import sync_run_from_job
    rx._key.cache_clear()
    sfx = uuid4().hex[:8]
    op = "workspace.polyglot.julia.expression-evaluate"
    m = math_model(client, f"math-j-{sfx}", op, {"kind": "scalar-paths", "paths": {"d0": "values.0"}})
    ps = sim.parameter_set(client, f"math-k-{sfx}", m["modelId"], {"expression": "x^2", "variables": ["x"], "evaluateAt": [{"x": 3}]})
    run_id = math_run(client, m["modelId"], op, ps)
    libs = {"source": "runtime-loaded", "julia": "1.11.5", "blasVendor": "lbt", "precision": "ieee754-binary64"}
    body = {"kind": "expression-evaluation", "values": [9.0],
            "identityCheck": {"method": c.IDENTITY_METHOD, "proof": False, "action": "evaluate", "pointCount": 1, "variable": ""}}
    monkeypatch.setattr(polyglot.httpx, "post", lambda url, json=None, headers=None, timeout=None: SimpleNamespace(
        status_code=200, json=lambda: {"result": body, "numericalLibraries": libs}, text=""))
    row = SimpleNamespace(operation=op, payload={"executionRunId": run_id, "payload": sim.pin(ps)}, user_key=USER,
                          job_id=f"job-{uuid4().hex[:10]}", project_id=PROJECT, request_fingerprint="d" * 64)
    with session_scope() as db:
        polyglot.execute_polyglot_operation(db, row)
        sync_run_from_job(db, USER, run_id, row.job_id, "succeeded", 100)
        db.commit()
    doc = sim.export(client, run_id)
    (r,) = doc["verification"]["runtimeReceipts"]
    assert r["runtimeVersion"] == "1.11.5" and r["numericalLibraries"] == libs
    assert doc["resultValues"]["values"] == {"d0": 9.0} and doc["resultValues"]["identityCheck"]["proof"] is False


# ---------------------------------------------------------------------------
# SC-NB-01: a ParameterSet-bound symbolic check and its Julia replay as verified notebook cells


def identity_notebook(ps, m_sym, m_jl):
    pin = {"parameterInput": {"parameterSetId": ps["parameterSetId"], "parameterSetRevision": ps["revision"]}}
    return {"schema": "sc-workspace-notebook/3.0", "title": "Symbolic identity check (synthetic)", "cells": [
        {"id": "sympy", "type": "code", "language": "python", "source": "diff(f, x) evaluated at the declared points",
         "execution": {"operation": "workspace.compute.symbolic", "modelRef": {"modelId": m_sym}, "maxAttempts": 1, "payload": pin}},
        {"id": "julia", "type": "code", "language": "julia", "source": "forward-mode dual evaluation of f'",
         "execution": {"operation": "workspace.polyglot.julia.expression-evaluate", "modelRef": {"modelId": m_jl},
                       "maxAttempts": 1, "dependsOnCellIds": ["sympy"], "payload": pin}},
    ]}


def test_notebook_steps_declare_the_bound_parameter_revision():
    from app import notebook_orchestration as nbo
    ps = {"parameterSetId": "ps-1", "revision": 2}
    steps = nbo.compile_plan(identity_notebook(ps, "m-s", "m-j"))["steps"]
    assert [s["parameterSetRef"] for s in steps] == [{"parameterSetId": "ps-1", "revision": 2}] * 2
    for bad in ({"parameterSetId": "ps-1"}, {"parameterSetId": "", "parameterSetRevision": 1}, {"parameterSetId": "p", "parameterSetRevision": True}, "ps-1"):
        doc = identity_notebook(ps, "m-s", "m-j")
        doc["cells"][0]["execution"]["payload"] = {"parameterInput": bad}
        with pytest.raises(HTTPException) as e:
            nbo.compile_plan(doc)
        assert e.value.detail["code"] == "cell-parameter-ref-requires-revision"


@pg
def test_identity_check_runs_as_verified_notebook_cells(client, monkeypatch):
    import app.polyglot as polyglot
    import tests.test_notebook_cell_runs_sc_nb01 as cells
    sfx = uuid4().hex[:8]
    paths = {f"d{i}": f"result.values.{i}" for i in range(3)}
    m_s = math_model(client, f"nb-sym-{sfx}", "workspace.compute.symbolic", {"kind": "scalar-paths", "paths": paths})
    m_j = math_model(client, f"nb-jl-{sfx}", "workspace.polyglot.julia.expression-evaluate",
                     {"kind": "scalar-paths", "paths": {k: v.replace("result.", "") for k, v in paths.items()}})
    params = {"expression": EXPR, "variables": ["x", "y"], "action": "differentiate", "variable": "x", "evaluateAt": POINTS}
    ps = sim.post(client, "/v1/parameter-sets", {"schema": "sc-workspace-parameter-set/1.0", "parameterSetId": f"nb-ps-{sfx}",
                                                 "projectId": "nb-proj", "modelId": "", "name": "Identity check points",
                                                 "parameters": params, "metadata": {"scientificClassification": "synthetic"}})
    expected = symbolic()["values"]
    seen = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        seen["payload"] = json["payload"]
        return SimpleNamespace(status_code=200, text="", json=lambda: {
            "result": {"kind": "expression-evaluation", "values": expected,
                       "identityCheck": {"method": c.IDENTITY_METHOD, "proof": False, "action": "differentiate",
                                         "pointCount": 3, "variable": "x"}},
            "numericalLibraries": {"source": "runtime-loaded", "julia": "1.11.5"}})

    monkeypatch.setattr(polyglot.httpx, "post", fake_post)
    nb_id = f"nb-math-{sfx}"
    cells.store_notebook(client, USER, nb_id, identity_notebook(ps, m_s["modelId"], m_j["modelId"]))
    plan = cells.plan_and_dispatch(client, USER, nb_id)
    cells.run_job(plan["steps"][0]["jobId"], USER)
    plan = cells.get_plan(client, USER, plan["planId"])
    cells.run_job(plan["steps"][1]["jobId"], USER)
    plan = cells.get_plan(client, USER, plan["planId"])
    assert plan["status"] == "succeeded", plan
    assert seen["payload"] == params  # Julia received exactly the attested revision
    for step, language in zip(plan["steps"], ("python", "julia")):
        doc = cells.export(client, USER, step["runId"])
        assert doc["verification"]["status"] == "executed-verified" and doc["verification"]["inputLineage"] == VERIFIED
        assert doc["notebookCell"]["verified"] is True and doc["notebookCell"]["cellId"] == step["cellId"]
        assert doc["verification"]["runtimeReceipts"][0]["language"] == language
        assert doc["resultValues"]["identityCheck"]["proof"] is False
        assert [doc["resultValues"]["values"][f"d{i}"] for i in range(3)] == expected
