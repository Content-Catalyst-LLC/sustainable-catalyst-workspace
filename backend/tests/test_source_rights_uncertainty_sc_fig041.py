"""SC-FIG-04.1 Workspace: trend uncertainty from the R runtime, and owner-signed source rights notices.

Unit tests always run (the R runner test needs Rscript with jsonlite). The PostgreSQL tests run when
SC_WORKSPACE_DATABASE_URL points at a disposable PostgreSQL database. Synthetic data only.
"""
import base64
import json
import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-research-export-fig041-{os.getpid()}.key")
with open(SEED_FILE, "w") as fh:
    fh.write(base64.b64encode(secrets.token_bytes(32)).decode())
os.environ["SC_WORKSPACE_RESEARCH_EXPORT_ENABLED"] = "true"
os.environ["SC_WORKSPACE_RESEARCH_EXPORT_SIGNING_KEY_FILE"] = SEED_FILE
os.environ["SC_WORKSPACE_RESEARCH_EXPORT_CLIENT_TOKEN"] = "research-client-test"
os.environ.setdefault("SC_WORKSPACE_SERVICE_TOKEN", "workspace-service-test")
os.environ.setdefault("SC_WORKSPACE_OBJECT_STORAGE_ROOT", os.path.join(KEY_DIR, f"sc-objects-{os.getpid()}"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: E402

from app import research_exports as rx  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils import canonical_bytes, sha256_hex  # noqa: E402

get_settings.cache_clear()
rx._key.cache_clear()
PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")
RUNNER = Path(__file__).resolve().parents[1] / "r-runtime" / "runner.R"
ROWS = [{"t": t, "y": y} for t, y in ((0, 1.1), (1, 2.9), (2, 5.2), (3, 6.8), (4, 9.1), (5, 10.9))]
# Student t 0.975 quantile for 4 degrees of freedom (standard table value).
T975_DF4 = 2.7764451051977987

MAPPING = {"kind": "coefficient-table", "uncertaintyField": "stdError", "intervalFields": {"lower": "confLow", "upper": "confHigh"},
           "rename": {"(Intercept)": "intercept", "t": "slope"},
           "assumptions": ["Linear mean in t", "Independent errors", "Constant error variance", "Normal errors (for t intervals)"]}


def r_doc(intervals=True, df=4, level=0.95, slope_ci=(1.8, 2.2)):
    rows = [{"term": "(Intercept)", "estimate": 1.0, "stdError": 0.1, "confLow": 0.7, "confHigh": 1.3},
            {"term": "t", "estimate": 2.0, "stdError": 0.05, "confLow": slope_ci[0], "confHigh": slope_ci[1]}]
    result = {"coefficients": rows, "metrics": {"n": 6, "dfResidual": df}}
    if intervals:
        result["interval"] = {"confidenceLevel": level, "method": "stats::confint.lm", "distribution": "Student t",
                              "degreesOfFreedom": df}
    return {"result": {"remote": {"result": result}}}


def test_intervals_come_from_the_runtime_record():
    out = rx.extract_result_values(MAPPING, r_doc())
    assert out["values"] == {"intercept": 1.0, "slope": 2.0}
    assert out["uncertainty"] == {"semantics": "standard-error", "values": {"intercept": 0.1, "slope": 0.05}}
    iv = out["intervals"]
    assert iv["values"]["slope"] == [1.8, 2.2] and iv["level"] == 0.95 and iv["degreesOfFreedom"] == 4
    assert iv["computedBy"] == "runtime" and iv["method"] == "stats::confint.lm"
    assert out["assumptions"] == {"declaredBy": "model-revision", "checked": False, "statements": MAPPING["assumptions"]}


@pytest.mark.parametrize("doc,needle", [
    (r_doc(intervals=False), "interval record"),
    (r_doc(slope_ci=(2.1, 2.3)), "does not contain the estimate"),
    (r_doc(level=0.4), "interval record"),
    (r_doc(df=0), "interval record"),
])
def test_intervals_are_never_invented_or_inconsistent(doc, needle):
    out = rx.extract_result_values(MAPPING, doc)
    assert out["values"] == {} and needle in out["error"]


def test_missing_interval_fields_fail_the_whole_mapping():
    doc = r_doc()
    del doc["result"]["remote"]["result"]["coefficients"][1]["confHigh"]
    assert "missing" in rx.extract_result_values(MAPPING, doc)["error"]
    assert "intervalFields" in rx.extract_result_values({**MAPPING, "intervalFields": {"lower": "confLow"}}, r_doc())["error"]


@pytest.mark.parametrize("bad", [[], ["x" * 241], [""], ["a"] * 13, "Linear mean", [3]])
def test_assumptions_are_bounded_statements(bad):
    assert "assumptions" in rx.extract_result_values({**MAPPING, "assumptions": bad}, r_doc())["error"]


def test_without_interval_fields_output_is_unchanged():
    out = rx.extract_result_values({"kind": "coefficient-table", "uncertaintyField": "stdError",
                                    "rename": {"(Intercept)": "intercept", "t": "slope"}}, r_doc())
    assert set(out) == {"values", "uncertainty"}


def _run_r(payload):
    with tempfile.TemporaryDirectory() as d:
        src, dst = Path(d) / "in.json", Path(d) / "out.json"
        src.write_text(json.dumps({"operation": "workspace.polyglot.r.linear-model", "payload": payload}))
        subprocess.run(["Rscript", "--vanilla", str(RUNNER), str(src), str(dst)], check=True, capture_output=True, timeout=60)
        return json.loads(dst.read_text())


def _has_r():
    if shutil.which("Rscript") is None:
        return False
    return subprocess.run(["Rscript", "--vanilla", "-e", "library(jsonlite)"], capture_output=True).returncode == 0


needs_r = pytest.mark.skipif(not _has_r(), reason="needs Rscript with jsonlite (runs in the R runtime image)")


@needs_r
def test_r_runner_reports_t_intervals_and_degrees_of_freedom():
    res = _run_r({"rows": ROWS, "outcome": "y", "predictors": ["t"], "confidenceLevel": 0.95})
    res = res.get("result", res)
    assert res["metrics"]["dfResidual"] == 4 and res["interval"]["degreesOfFreedom"] == 4
    assert res["interval"]["confidenceLevel"] == 0.95 and res["interval"]["distribution"] == "Student t"
    for row in res["coefficients"]:
        half = (row["confHigh"] - row["confLow"]) / 2
        assert abs((row["confLow"] + row["confHigh"]) / 2 - row["estimate"]) < 1e-9
        assert abs(half / row["stdError"] - T975_DF4) < 1e-9
    out = rx.extract_result_values(MAPPING, {"result": {"remote": {"result": res}}})
    assert out["intervals"]["values"]["slope"][0] < out["values"]["slope"] < out["intervals"]["values"]["slope"][1]


@needs_r
def test_r_runner_output_without_confidence_level_is_unchanged():
    res = _run_r({"rows": ROWS, "outcome": "y", "predictors": ["t"]})
    res = res.get("result", res)
    assert "interval" not in res and all("confLow" not in r for r in res["coefficients"])
    with pytest.raises(subprocess.CalledProcessError):
        _run_r({"rows": ROWS, "outcome": "y", "predictors": ["t"], "confidenceLevel": 1.5})


# ---------------------------------------------------------------------------
# Source rights notices (PostgreSQL)

pg = pytest.mark.skipif(not PG, reason="needs a disposable PostgreSQL SC_WORKSPACE_DATABASE_URL")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.db import initialize_schema
    from app.main import app
    initialize_schema()
    with TestClient(app) as c:
        yield c


def hdr(user):
    return {"Authorization": "Bearer " + get_settings().service_token, "X-SC-User-ID": user}


def verify(doc):
    body = {k: v for k, v in doc.items() if k != "signature"}
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
    pub.verify(rx._b64d(doc["signature"]["value"]), rx.SOURCE_RIGHTS_SCHEMA.encode() + b"\n" + canonical_bytes(body))


def pinned_dataset(client, user, project):
    from app.db import session_scope
    from app.object_store import store_artifact
    from app.schemas import ArtifactStoreRequest
    sfx = uuid4().hex[:8]
    raw = json.dumps({"rows": ROWS}, sort_keys=True).encode()
    with session_scope() as db:
        store_artifact(db, user, ArtifactStoreRequest.model_validate({"schema": "sc-workspace-artifact-store/1.0",
            "artifactId": f"art-{sfx}", "projectId": project, "filename": "rows.json", "mediaType": "application/json",
            "contentBase64": base64.b64encode(raw).decode(), "expectedRevision": 0, "metadata": {}}))
    r = client.post("/v1/datasets", headers=hdr(user), json={"schema": "sc-workspace-dataset-record/1.0", "datasetId": f"ds-{sfx}",
                    "projectId": project, "name": "Synthetic", "datasetType": "table", "sourceKind": "artifact",
                    "artifactId": f"art-{sfx}", "metadata": {"scientificClassification": "synthetic"}})
    assert r.status_code == 200, r.text
    return f"ds-{sfx}", r.json()["item"]["artifactSha256"]


@pg
def test_owner_signs_ordered_notices_for_exact_dataset_bytes(client):
    owner, project = f"fig041-{uuid4().hex[:6]}", f"p-{uuid4().hex[:6]}"
    ds, sha = pinned_dataset(client, owner, project)
    req = {"projectId": project, "datasetId": ds, "licenceStatus": "restricted", "reason": "Licence withdrawn (synthetic drill)"}
    n1 = client.post("/v1/research-exports/source-rights", headers=hdr(owner), json=req).json()
    verify(n1)
    assert (n1["sourceSha256"], n1["sequence"], n1["licenceStatus"], n1["previousNoticeSha256"]) == (sha, 1, "restricted", None)
    assert n1["ownerScope"] == f"workspace-user:{owner}" and n1["audience"] == "sc-research"
    # Re-sending the current status returns the same signed notice (no new sequence).
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner), json=req).json() == n1
    n2 = client.post("/v1/research-exports/source-rights", headers=hdr(owner), json={**req, "licenceStatus": "verified-for-use"}).json()
    verify(n2)
    assert n2["sequence"] == 2 and n2["previousNoticeSha256"] == sha256_hex(n1)
    listed = client.get("/v1/research-exports/source-rights", headers=hdr(owner), params={"projectId": project}).json()["items"]
    assert [x["noticeId"] for x in listed] == [n2["noticeId"], n1["noticeId"]]


@pg
def test_notices_are_owner_isolated_and_need_pinned_bytes(client):
    owner, other, project = f"fig041-{uuid4().hex[:6]}", f"fig041-{uuid4().hex[:6]}", f"p-{uuid4().hex[:6]}"
    ds, _ = pinned_dataset(client, owner, project)
    req = {"projectId": project, "datasetId": ds, "licenceStatus": "restricted"}
    assert client.post("/v1/research-exports/source-rights", headers=hdr(other), json=req).status_code == 404
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner), json={**req, "projectId": "other"}).status_code == 404
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner), json={**req, "datasetRevision": 9}).status_code == 404
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner), json={**req, "licenceStatus": "pending"}).status_code == 422
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner), json={**req, "ownerScope": "x"}).status_code == 422
    assert client.post("/v1/research-exports/source-rights", json=req).status_code in (401, 403)
    meta = f"meta-{uuid4().hex[:6]}"
    assert client.post("/v1/datasets", headers=hdr(owner), json={"schema": "sc-workspace-dataset-record/1.0", "datasetId": meta,
                       "projectId": project, "name": "Unpinned", "datasetType": "table"}).status_code == 200
    assert client.post("/v1/research-exports/source-rights", headers=hdr(owner),
                       json={**req, "datasetId": meta}).status_code == 404
    client.post("/v1/research-exports/source-rights", headers=hdr(owner), json=req)
    assert client.get("/v1/research-exports/source-rights", headers=hdr(other), params={"projectId": project}).json()["items"] == []


@pg
def test_notices_are_append_only_in_the_database(client):
    from sqlalchemy import text
    from app.db import session_scope
    owner, project = f"fig041-{uuid4().hex[:6]}", f"p-{uuid4().hex[:6]}"
    ds, _ = pinned_dataset(client, owner, project)
    n = client.post("/v1/research-exports/source-rights", headers=hdr(owner),
                    json={"projectId": project, "datasetId": ds, "licenceStatus": "restricted"}).json()
    for stmt in ("UPDATE workspace_research_source_rights_notices SET licence_status = 'verified-for-use' WHERE notice_id = :i",
                 "DELETE FROM workspace_research_source_rights_notices WHERE notice_id = :i"):
        with session_scope() as db, pytest.raises(Exception, match="append-only"):
            db.execute(text(stmt), {"i": n["noticeId"]})
            db.commit()
