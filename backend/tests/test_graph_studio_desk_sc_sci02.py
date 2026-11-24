"""SC-SCI-02: a verified notebook result opens in Graph Studio on the Notebook Desk.

The desk serves byte-identical copies of the Lab renderer listed in graph-studio/RENDERER_LOCK.json and
nothing else under that path; the page loads them with Subresource Integrity. The figure view carries a
unit-titled tooltip and still passes Lab's own FIG-02B contract.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app import approval_desk, notebook_desk, notebook_figure_bundle as fb

sys.path.insert(0, str(Path(__file__).parent))
import test_notebook_figure_bundle_sc_fig02b as figs  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LOCK = json.loads((notebook_desk.GRAPH_STUDIO / "RENDERER_LOCK.json").read_text())


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(notebook_desk.page_router)
    return TestClient(app)


def test_vendored_renderer_matches_its_lock_and_the_page_tags():
    run = subprocess.run([sys.executable, str(REPO / "scripts/sync_graph_studio_renderer.py"), "--check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert LOCK["labRelease"] == "0.163.1.10" and len(LOCK["labCommit"]) == 40
    roles = [f["role"] for f in LOCK["files"] if f["kind"] == "script"]
    assert roles == ["vega", "vega-lite", "vega-interpreter", "fig02a-policy", "fig02b-vega-lite", "renderer"]


def test_only_locked_renderer_files_are_served(client):
    for f in LOCK["files"]:
        r = client.get(f"/v1/desk/notebook-assets/graph-studio/{f['path']}")
        if f["kind"] == "license":
            assert r.status_code == 404
            continue
        assert r.status_code == 200 and len(r.content) == f["bytes"]
        assert r.headers["content-type"].startswith("text/javascript" if f["kind"] == "script" else "text/css")
    for bad in ("RENDERER_LOCK.json", "js/x.js", "lib/vega-6.4.0/LICENSE"):
        assert client.get(f"/v1/desk/notebook-assets/graph-studio/{bad}").status_code == 404
    # Paths are looked up in the lock, never joined first, so traversal never reaches the filesystem.
    for bad in ("../notebook-desk.js", "../../notebook_desk.py", "lib/vega-6.4.0/../../../index.html", "/etc/passwd"):
        with pytest.raises(HTTPException) as e:
            notebook_desk.graph_studio_asset(bad)
        assert e.value.status_code == 404


def test_desk_policy_allows_vega_styles_and_local_exports_only(client):
    csp = client.get("/v1/desk/notebooks").headers["content-security-policy"]
    assert "script-src 'self';" in csp and "'unsafe-eval'" not in csp and "connect-src 'self'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp and "img-src 'self' blob: data:" in csp
    # The approval desk keeps its stricter policy.
    assert "unsafe-inline" not in approval_desk.CSP and "blob:" not in approval_desk.CSP


def test_desk_opens_the_package_in_graph_studio_pinned_to_the_bundle_hash():
    js = (notebook_desk.STATIC / "notebook-desk.js").read_text()
    body = js.split("async function openGraphStudio(pkg)", 1)[1].split("\n}\n", 1)[0]
    assert "R.render(out, files, pkg.bundleSha256)" in body and "new TextEncoder().encode(f.text)" in body


def test_view_tooltip_names_every_value_with_its_unit():
    rows = {"series": [{"t": 2020, "v": 1.0, "lo": 0.8, "hi": 1.2}]}
    req = figs.request(rowsPath="series", mark="line", x={"field": "t", "label": "Time", "unit": "year", "type": "quantitative"},
                       y={"field": "v", "label": "Value", "unit": "t ha-1"},
                       uncertainty={"kind": "pi95", "lowerField": "lo", "upperField": "hi", "statement": "Synthetic 95% prediction interval."},
                       evidenceClass="hypothetical")
    view = json.loads(figs.files(fb.build_package(figs.REV, "fit", "d" * 64, figs.evidence(), rows, req))["view"]["text"])
    tip = {t["field"]: (t["type"], t["title"]) for t in view["layer"][-1]["encoding"]["tooltip"]}
    assert tip == {"t": ("quantitative", "Time (year)"), "v": ("quantitative", "Value (t ha-1)"), "evidenceClass": ("nominal", "Evidence class"),
                   "lower": ("quantitative", "Lower bound (95% prediction interval) (t ha-1)"),
                   "upper": ("quantitative", "Upper bound (95% prediction interval) (t ha-1)")}
    assert set(tip) == set(view["usermeta"]["sc"]["fields"])


NODE = r"""
const fs = require('fs'), path = require('path');
const [dir, pkgs] = [process.argv[1], JSON.parse(process.argv[2])];
globalThis.SCLabPlotlyPreviewFIG02A = require(path.join(dir, 'js/modules/graph-studio-plotly-preview-fig02a.js'));
globalThis.SCLabVegaLiteFIG02B = require(path.join(dir, 'js/modules/graph-studio-vega-lite-fig02b.js'));
const R = require(path.join(dir, 'js/modules/graph-studio-figure-bundle-renderer.js'));
Promise.all(pkgs.map(p => R.verifyPackage(p.files.map(f => ({ name: f.name, bytes: new TextEncoder().encode(f.text) })), undefined, p.bundleSha256)
  .then(ok => ok.views.map(v => v.state).join(','), e => 'refused ' + JSON.stringify(e)))).then(r => console.log(JSON.stringify(r)));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_packages_pass_the_vendored_lab_contract():
    point = fb.build_package(figs.REV, "fit", "d" * 64, figs.evidence(), figs.COEFFICIENTS, figs.request())
    line = fb.build_package(figs.REV, "fit", "d" * 64, figs.evidence(), {"series": [{"t": 1, "v": 2.0}, {"t": 2, "v": 2.5}]},
                            figs.request(rowsPath="series", mark="line", x={"field": "t", "label": "Year", "unit": "year", "type": "quantitative"},
                                         y={"field": "v", "label": "Value", "unit": "t ha-1"}, uncertainty={"kind": "none", "statement": "No uncertainty reported."}))
    out = subprocess.run(["node", "-e", NODE, str(notebook_desk.GRAPH_STUDIO), json.dumps([point, line])],
                         capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == ["rendered-vega-lite", "rendered-vega-lite"]
