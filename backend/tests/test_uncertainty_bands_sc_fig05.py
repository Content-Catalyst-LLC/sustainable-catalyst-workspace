"""SC-FIG-05.3 Workspace: runtime-computed regression bands (R) and ensemble quantile fans (uncertainty runtime),
exported to Research only as the runtime computed them.

The independent recomputation checks use NumPy/SciPy, not the runtimes' own code. Synthetic data only.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from scipy import stats

os.environ.setdefault("SC_WORKSPACE_SERVICE_TOKEN", "workspace-service-test")

from app import research_exports as rx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests" / "fixtures" / "sc_fig05_r_linear_bands.json").read_text())
FAN_OP = "workspace.uncertainty.ensemble-quantile-bands"
BAND_MAPPING = {"kind": "coefficient-table", "uncertaintyField": "stdError", "intervalFields": {"lower": "confLow", "upper": "confHigh"},
                "rename": {"(Intercept)": "intercept", "t": "slope"}, "bands": ["confidence-band", "prediction-band"],
                "assumptions": ["Linear mean in t", "Independent errors", "Constant error variance", "Normal errors"]}
FAN_MAPPING = {"kind": "scalar-paths", "paths": {"memberCount": "memberCount"}, "quantileBands": True}


def _service():
    spec = importlib.util.spec_from_file_location("sc_uncertainty_service_fig05", ROOT / "uncertainty-runtime" / "service.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _r_doc():
    return {"result": {"remote": copy.deepcopy(FIXTURE["output"])}}


def _ensemble(n=40, steps=12, seed=5):
    rng = np.random.default_rng(seed)
    x = np.arange(steps, dtype=float)
    return x, [{"name": f"m{i}", "values": (1.5 + 0.3 * x + np.cumsum(rng.normal(0, 0.4, steps))).round(6).tolist()} for i in range(n)]


def _fan(levels=(0.5, 0.8, 0.95), **kw):
    x, members = _ensemble(**kw)
    c = TestClient(_service().app)
    r = c.post("/v1/execute", json={"operation": FAN_OP, "payload": {"steps": x.tolist(), "members": members, "centralLevels": list(levels)}})
    assert r.status_code == 200, r.text
    return x, members, r.json()


# --- R bands: independent recomputation ------------------------------------------------------------------------

def test_r_bands_match_an_independent_ols_recomputation():
    rows = FIXTURE["input"]["payload"]["rows"]
    level = FIXTURE["input"]["payload"]["confidenceLevel"]
    t = np.array([r["t"] for r in rows], float)
    y = np.array([r["y"] for r in rows], float)
    X = np.column_stack([np.ones_like(t), t])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    dof = len(y) - 2
    s2 = float(((y - X @ beta) ** 2).sum() / dof)
    xtx_inv = np.linalg.inv(X.T @ X)
    q = stats.t.ppf((1 + level) / 2, dof)
    bands = {b["semantics"]: b for b in FIXTURE["output"]["result"]["bands"]}
    assert set(bands) == {"confidence-band", "prediction-band"}
    for sem, extra in (("confidence-band", 0.0), ("prediction-band", 1.0)):
        b = bands[sem]
        assert b["computedBy"] == "runtime" and b["degreesOfFreedom"] == dof and b["confidenceLevel"] == level
        assert [p["x"] for p in b["points"]] == sorted(set(t.tolist()))  # observed values only: no extrapolation
        for p in b["points"]:
            x0 = np.array([1.0, p["x"]])
            fit = float(x0 @ beta)
            half = q * np.sqrt(s2 * (float(x0 @ xtx_inv @ x0) + extra))
            assert abs(p["fit"] - fit) < 1e-9
            assert abs(p["lower"] - (fit - half)) < 1e-9 and abs(p["upper"] - (fit + half)) < 1e-9


def test_r_bands_export_with_the_runtime_record():
    out = rx.extract_result_values(BAND_MAPPING, _r_doc())
    assert out["intervals"]["level"] == 0.9 and out["intervals"]["computedBy"] == "runtime"
    conf, pred = out["bands"]
    assert conf["semantics"] == "confidence-band" and pred["semantics"] == "prediction-band"
    assert conf["level"] == 0.9 and conf["degreesOfFreedom"] == 10 and conf["distribution"] == "Student t"
    assert "predict.lm" in conf["method"] and conf["evaluatedAt"] == "observed predictor values"
    assert len(conf["points"]) == 12 and all(len(p) == 4 for p in conf["points"])
    assert out["assumptions"]["checked"] is False


def _band_doc(mutate):
    doc = _r_doc()
    mutate(doc["result"]["remote"]["result"])
    return doc


@pytest.mark.parametrize("mutate,needle", [
    (lambda r: r.pop("bands"), "no band record"),
    (lambda r: r["bands"].pop(1), "no prediction-band"),
    (lambda r: r["bands"][0].update(computedBy="workbench"), "runtime's record"),
    (lambda r: r["bands"][0].pop("degreesOfFreedom"), "runtime's record"),
    (lambda r: r["bands"][0].update(confidenceLevel=1.2), "runtime's record"),
    (lambda r: r["bands"][0]["points"][3].update(lower=99.0), "does not contain its fit"),
    (lambda r: r["bands"][0]["points"][3].pop("upper"), "missing a value"),
    (lambda r: r["bands"][0]["points"].reverse(), "strictly increasing"),
    (lambda r: r["bands"][1].update(confidenceLevel=0.95), "share level"),
    (lambda r: r["bands"][1]["points"][2].update(upper=r["bands"][0]["points"][2]["upper"] - 1e-6), "must contain the confidence band"),
])
def test_r_bands_are_never_invented_or_inconsistent(mutate, needle):
    out = rx.extract_result_values(BAND_MAPPING, _band_doc(mutate))
    assert out["values"] == {} and needle in out["error"]


@pytest.mark.parametrize("bad", [[], ["band"], "confidence-band", ["confidence-band", "confidence-band"]])
def test_declared_band_list_is_strict(bad):
    assert "bands" in rx.extract_result_values({**BAND_MAPPING, "bands": bad}, _r_doc())["error"]


def test_without_band_declarations_export_is_unchanged():
    mapping = {k: v for k, v in BAND_MAPPING.items() if k != "bands"}
    out = rx.extract_result_values(mapping, _r_doc())
    assert "bands" not in out and "quantileBands" not in out
    assert out["intervals"]["method"].startswith("stats::confint.lm")  # interval record, not a band record


# --- Ensemble quantile fan --------------------------------------------------------------------------------------

def test_fan_matches_numpy_type7_quantiles():
    x, members, res = _fan()
    fan = res["result"]["quantileBands"]
    assert fan["computedBy"] == "runtime" and fan["memberCount"] == 40 and fan["centralLevels"] == [0.5, 0.8, 0.95]
    m = np.array([mm["values"] for mm in members])
    for j, st in enumerate(fan["steps"]):
        col = m[:, j]
        assert st["x"] == x[j] and abs(st["median"] - np.quantile(col, 0.5)) < 1e-12
        assert st["min"] == col.min() and st["max"] == col.max()
        for lv, b in zip(fan["centralLevels"], st["bands"]):
            assert abs(b["lower"] - np.quantile(col, (1 - lv) / 2, method="linear")) < 1e-12
            assert abs(b["upper"] - np.quantile(col, (1 + lv) / 2, method="linear")) < 1e-12


def test_fan_is_deterministic_and_exports_nested_bands():
    _, _, a = _fan()
    _, _, b = _fan()
    assert a == b
    out = rx.extract_result_values(FAN_MAPPING, {"result": {"remote": a}})
    fan = out["quantileBands"]
    assert out["values"] == {"memberCount": 40.0} and fan["semantics"] == "ensemble-quantile-fan"
    for st in fan["steps"]:
        los, his = [b[0] for b in st["bands"]], [b[1] for b in st["bands"]]
        assert st["min"] <= los[-1] <= los[0] <= st["median"] <= his[0] <= his[-1] <= st["max"]


@pytest.mark.parametrize("payload,needle", [
    ({"steps": [0, 1, 1, 2]}, "strictly increasing"),
    ({"steps": [0]}, "2..500"),
    ({"members": [{"values": [1, 2]}] * 4}, "5..1000"),
    ({"members": [{"values": [1, 2, 3]}] * 6}, "one value per step"),
    ({"members": [{"values": [1, "x"]}] * 6}, "numeric"),
    ({"centralLevels": [0.999]}, "between 0.1 and 0.99"),
    ({"centralLevels": [0.1, 0.2, 0.3, 0.4, 0.5]}, "1..4"),
])
def test_fan_runtime_refuses_bad_ensembles(payload, needle):
    base = {"steps": [0, 1], "members": [{"values": [1, 2]}] * 6}
    r = TestClient(_service().app).post("/v1/execute", json={"operation": FAN_OP, "payload": {**base, **payload}})
    assert r.status_code == 400 and needle in r.json()["detail"]


def _fan_doc(mutate):
    _, _, res = _fan()
    mutate(res["result"]["quantileBands"])
    return {"result": {"remote": res}}


@pytest.mark.parametrize("mutate,needle", [
    (lambda q: q.update(computedBy="lab"), "no quantile band record"),
    (lambda q: q.update(memberCount=3), "member count"),
    (lambda q: q.update(centralLevels=[0.95, 0.5, 0.8]), "increasing central levels"),
    (lambda q: q["steps"][4]["bands"][1].update(lower=q["steps"][4]["bands"][0]["lower"] + 1), "not nested"),
    (lambda q: q["steps"][4]["bands"][2].update(upper=q["steps"][4]["max"] + 1), "not nested"),
    (lambda q: q["steps"].reverse(), "strictly increasing"),
    (lambda q: q["steps"][0].pop("median"), "missing a value"),
])
def test_fan_export_refuses_tampered_or_inconsistent_records(mutate, needle):
    out = rx.extract_result_values(FAN_MAPPING, _fan_doc(mutate))
    assert out["values"] == {} and needle in out["error"]


def test_fan_declared_without_a_runtime_fan_is_unavailable_not_invented():
    doc = {"result": {"remote": {"result": {"memberCount": 40}}}}
    assert "no quantile band record" in rx.extract_result_values(FAN_MAPPING, doc)["error"]


# --- R runner (needs Rscript with jsonlite: runs in the R runtime image) ---------------------------------------

from tests.test_source_rights_uncertainty_sc_fig041 import _run_r, needs_r  # noqa: E402


@needs_r
def test_r_runner_reproduces_the_fixture():
    res = _run_r(FIXTURE["input"]["payload"])
    assert res["result"]["bands"] == FIXTURE["output"]["result"]["bands"]


@needs_r
@pytest.mark.parametrize("extra", [
    {"bands": ["confidence"], "confidenceLevel": None},
    {"bands": ["smoothed"]},
    {"bands": ["confidence"], "predictors": ["t", "year"]},
])
def test_r_runner_refuses_bands_it_cannot_compute(extra):
    import subprocess
    payload = {**FIXTURE["input"]["payload"], **extra}
    payload = {k: v for k, v in payload.items() if v is not None}
    with pytest.raises(subprocess.CalledProcessError):
        _run_r(payload)
