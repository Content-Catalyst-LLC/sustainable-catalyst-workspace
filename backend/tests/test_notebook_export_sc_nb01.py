"""SC-NB-01 portable notebook exports (.ipynb, Quarto, reproducibility package). Synthetic data only."""
import hashlib
import json
import re
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from test_input_integrity_sc_nb01 import PG, client, hdr  # noqa: F401 (client is a fixture)
from test_notebook_cell_runs_sc_nb01 import dataset, fake_runtime, get_plan, notebook, plan_and_dispatch, run_job, store_notebook

from app import notebook_export as nx  # noqa: E402
from app.utils import sha256_hex  # noqa: E402

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")
NB_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def full_notebook(ds_id, with_scenario=True, **kw):
    doc = notebook(ds_id, **kw)
    doc["sections"] = [{"id": "s1", "title": "Question and sources", "blocks": [
        {"id": "b-q", "type": "question", "title": "", "content": "Is y linear in x for the synthetic set?"},
        {"id": "b-ref", "type": "reference", "title": "Method", "content": "Ordinary least squares.",
         "sourceTitle": "Synthetic method note", "sourceUrl": "https://example.org/ols"},
        {"id": "b-att", "type": "attachment", "title": "Field photo", "content": ""},
    ]}]
    if with_scenario:
        doc["cells"].append({"id": "scenario", "type": "decision-studio", "source": "",
                             "scenarioRef": {"authority": "decision-studio", "scenarioSetId": "synthetic"}})
    return doc


def rev(doc, notebook_id="nb-x", revision=1):
    return SimpleNamespace(package={"notebook": doc}, notebook_id=notebook_id, revision=revision,
                           fingerprint="9" * 64, title="Synthetic", project_id="nb-proj")


# ---------------------------------------------------------------------------
# Unit


def test_quarto_renders_r_and_julia_and_refuses_unrepresentable_cells():
    text = nx.build_quarto(rev(full_notebook("ds-1", with_scenario=False)))
    assert text.startswith("---\ntitle: \"Synthetic\"\n") and '"notebook-package-sha256": "' + "9" * 64 in text
    assert "```{r}\n#| label: fit\n#| sc-cell-sha256: " in text and "```{julia}\n#| label: replay" in text
    assert "**Research question:** Is y linear" in text and "*Source:* Synthetic method note — https://example.org/ols" in text
    assert "> Not representable in Quarto: Workspace attachment block `b-att`." in text
    with pytest.raises(HTTPException) as exc:
        nx.build_quarto(rev(full_notebook("ds-1")))
    assert exc.value.detail["code"] == "quarto-not-representable" and exc.value.detail["cells"][0]["id"] == "scenario"
    doc = full_notebook("ds-1", with_scenario=False)
    doc["cells"][1]["language"] = "rust"
    with pytest.raises(HTTPException):
        nx.build_quarto(rev(doc))


def test_ipynb_cell_ids_are_valid_and_unique():
    used = set()
    ids = [nx._cell_id(x, used) for x in ("fit", "fit", "a b/c", "", "x" * 90)]
    assert len(set(ids)) == len(ids) and all(NB_ID.match(i) for i in ids)


# ---------------------------------------------------------------------------
# PostgreSQL integration


def get_export(client, user, nb_id, revision, fmt, expect=200):
    r = client.get(f"/v1/notebooks/{nb_id}/revisions/{revision}/export", params={"format": fmt}, headers=hdr(user))
    assert r.status_code == expect, r.text
    return r


def executed(client, monkeypatch, with_scenario=True):
    fake_runtime(monkeypatch)
    sfx, art, ds = dataset(client, "nb-owner-a")
    nb_id = f"nbx-{sfx}"
    store_notebook(client, "nb-owner-a", nb_id, full_notebook(ds["datasetId"], with_scenario=with_scenario))
    plan = plan_and_dispatch(client, "nb-owner-a", nb_id, )
    run_job(plan["steps"][0]["jobId"], "nb-owner-a")
    plan = get_plan(client, "nb-owner-a", plan["planId"])
    run_job(plan["steps"][1]["jobId"], "nb-owner-a")
    plan = get_plan(client, "nb-owner-a", plan["planId"])
    assert plan["status"] == "succeeded"
    return nb_id, art, ds, plan


@pg
def test_ipynb_export_is_valid_deterministic_and_carries_verified_outputs(client, monkeypatch):
    nb_id, art, ds, plan = executed(client, monkeypatch)
    r = get_export(client, "nb-owner-a", nb_id, 1, "ipynb")
    assert r.headers["X-SC-Export-Sha256"] == hashlib.sha256(r.content).hexdigest()
    assert r.headers["content-type"].startswith("application/x-ipynb+json")
    assert get_export(client, "nb-owner-a", nb_id, 1, "ipynb").content == r.content  # deterministic
    nb = r.json()
    assert (nb["nbformat"], nb["nbformat_minor"]) == (4, 5)
    ids = [c["id"] for c in nb["cells"]]
    assert len(set(ids)) == len(ids) and all(NB_ID.match(i) for i in ids)
    try:
        import nbformat
        nbformat.validate(nbformat.reads(r.text, as_version=4))
    except ImportError:
        pass
    meta = nb["metadata"]["sc_workspace"]
    assert meta["notebookId"] == nb_id and meta["notebookRevision"] == 1 and meta["languages"] == ["r", "julia"]
    assert meta["fullyRepresentable"] is False
    kinds = sorted(x["kind"] for x in meta["nonRepresentable"])
    assert kinds == ["attachment", "decision-studio", "kernel"]
    code = {c["metadata"]["sc_workspace"]["cellId"]: c for c in nb["cells"] if c["cell_type"] == "code"}
    fit = code["fit"]
    assert fit["metadata"]["sc_workspace"]["run"]["runId"] == plan["steps"][0]["runId"]
    assert fit["metadata"]["sc_workspace"]["run"]["inputLineage"] == "artifact-bound-verified"
    assert fit["metadata"]["sc_workspace"]["run"]["inputBindings"][0]["artifactSha256"] == art["sha256"]
    assert '"estimate": 0.25' in json.dumps(fit["outputs"][0]["data"]["application/json"])
    assert code["replay"]["outputs"][0]["metadata"]["sc_workspace"]["inputLineage"] == "artifact-bound-verified"
    assert "".join(fit["source"]) == "fit <- lm(y ~ x, data = rows)"


@pg
def test_changed_code_has_no_borrowed_outputs_and_old_revision_keeps_its_own(client, monkeypatch):
    nb_id, art, ds, plan = executed(client, monkeypatch)
    store_notebook(client, "nb-owner-a", nb_id,
                   full_notebook(ds["datasetId"], r_source="fit <- lm(y ~ x + 0, data = rows)"), expected=1)
    nb2 = get_export(client, "nb-owner-a", nb_id, 2, "ipynb").json()
    code2 = {c["metadata"]["sc_workspace"]["cellId"]: c for c in nb2["cells"] if c["cell_type"] == "code"}
    assert code2["fit"]["outputs"] == [] and "run" not in code2["fit"]["metadata"]["sc_workspace"]
    nb1 = get_export(client, "nb-owner-a", nb_id, 1, "ipynb").json()
    code1 = {c["metadata"]["sc_workspace"]["cellId"]: c for c in nb1["cells"] if c["cell_type"] == "code"}
    assert code1["fit"]["outputs"] and code1["fit"]["metadata"]["sc_workspace"]["cellSha256"] != code2["fit"]["metadata"]["sc_workspace"]["cellSha256"]


@pg
def test_quarto_and_reproducibility_package(client, monkeypatch):
    nb_id, art, ds, plan = executed(client, monkeypatch, with_scenario=False)
    q = get_export(client, "nb-owner-a", nb_id, 1, "qmd")
    assert "```{r}" in q.text and "```{julia}" in q.text
    ipynb_sha = get_export(client, "nb-owner-a", nb_id, 1, "ipynb").headers["X-SC-Export-Sha256"]
    pkg = get_export(client, "nb-owner-a", nb_id, 1, "package").json()
    assert pkg["schema"] == "sc-workspace-notebook-portable-package/1.0" and pkg["notebook"]["schema"] == "sc-workspace-notebook/3.0"
    rep = pkg["related"]["reproducibility"]
    assert rep["notebookRef"]["notebookId"] == nb_id and rep["exports"]["ipynb"]["sha256"] == ipynb_sha
    assert rep["exports"]["quarto"] == {"sha256": hashlib.sha256(q.content).hexdigest(), "representable": True}
    assert {e["cellId"]: e["verification"]["status"] for e in rep["executions"]} == {"fit": "executed-verified", "replay": "executed-verified"}
    assert all(e["cellUnchanged"] and e["verification"]["inputLineage"] == "artifact-bound-verified" for e in rep["executions"])
    assert rep["datasets"] == [{"datasetId": ds["datasetId"], "datasetRevision": 1, "artifactId": art["artifactId"],
                                "artifactRevision": 1, "artifactSha256": art["sha256"],
                                "rowsSha256": rep["executions"][0]["verification"]["inputBindings"][0]["rowsSha256"]}]
    assert pkg["governance"]["publicationApproved"] is False
    body = {k: v for k, v in pkg.items() if k not in ("integrity", "exportedAt", "signature")}
    assert pkg["integrity"]["contentSha256"] == sha256_hex(body)
    assert pkg["signature"]["alg"] == "Ed25519"
    # Signed with the Workspace export key: verifiable with its published public key.
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from app.utils import canonical_bytes
    pub = client.get("/v1/research-exports/public-key").json()["publicKey"]
    sig = pkg["signature"]["value"]
    Ed25519PublicKey.from_public_bytes(base64.b64decode(pub)).verify(
        base64.urlsafe_b64decode(sig + "=" * (-len(sig) % 4)),
        nx.PACKAGE_SCHEMA.encode() + b"\n" + canonical_bytes({k: v for k, v in pkg.items() if k != "signature"}))
    # A Decision Studio cell makes Quarto unrepresentable; the package says so instead of failing.
    get_export(client, "nb-owner-a", nb_id, 1, "qmd")


@pg
def test_exports_are_owner_scoped(client, monkeypatch):
    nb_id, *_ = executed(client, monkeypatch)
    for fmt in ("ipynb", "qmd", "package"):
        get_export(client, "nb-owner-b", nb_id, 1, fmt, expect=404)
    get_export(client, "nb-owner-a", nb_id, 9, "ipynb", expect=404)
    get_export(client, "nb-owner-a", nb_id, 1, "html", expect=422)
    assert get_export(client, "nb-owner-a", nb_id, 1, "qmd", expect=409).json()["code"] == "quarto-not-representable"
    pkg = get_export(client, "nb-owner-a", nb_id, 1, "package").json()
    assert pkg["related"]["reproducibility"]["exports"]["quarto"]["representable"] is False
