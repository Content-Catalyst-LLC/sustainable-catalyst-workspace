"""SC-MODEL-01 Workspace -> Research export: grants, ownership, verification, withdrawal.

Unit tests always run. The PostgreSQL integration tests run when SC_WORKSPACE_DATABASE_URL
points at a disposable PostgreSQL database (CI service container or isolated staging).
Synthetic data only.
"""
import base64
import json
import os
import secrets
import time
from uuid import uuid4

import pytest

KEY_DIR = os.environ.setdefault("SC_TEST_KEY_DIR", "/tmp")
SEED_FILE = os.path.join(KEY_DIR, f"sc-research-export-test-{os.getpid()}.key")
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
from app.utils import canonical_bytes  # noqa: E402

get_settings.cache_clear()
rx._key.cache_clear()
PG = os.getenv("SC_WORKSPACE_DATABASE_URL", "").startswith("postgresql")


def verify(domain, doc):
    body = {k: v for k, v in doc.items() if k != "signature"}
    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(rx.public_key_info()["publicKey"]))
    pub.verify(rx._b64d(doc["signature"]["value"]), domain.encode() + b"\n" + canonical_bytes(body))


def claims(**over):
    now = int(time.time())
    base = {"schema": rx.GRANT_SCHEMA, "grantId": "rxg_x", "iss": rx.ISSUER, "aud": rx.AUDIENCE, "sub": "a",
            "ownerScope": "workspace-user:a", "projectId": "p", "runId": "r", "iat": now, "exp": now + 60}
    return {**base, **over}


def test_grant_tokens_verify_and_reject_tampering():
    token = rx.issue_grant_token(claims())
    assert rx.decode_grant_token(token)["sub"] == "a"
    body, sig = token.split(".")
    forged = rx._b64e(canonical_bytes(claims(sub="b"))) + "." + sig
    with pytest.raises(ValueError, match="signature"):
        rx.decode_grant_token(forged)
    with pytest.raises(ValueError, match="expired"):
        rx.decode_grant_token(rx.issue_grant_token(claims(exp=int(time.time()) - 1)))
    with pytest.raises(ValueError, match="scope"):
        rx.decode_grant_token(rx.issue_grant_token(claims(aud="someone-else")))


def test_signed_documents_verify_and_detect_changes():
    doc = rx.sign_document(rx.EXPORT_SCHEMA, {"schema": rx.EXPORT_SCHEMA, "runId": "r", "values": {"x": 1.0}})
    verify(rx.EXPORT_SCHEMA, doc)
    doc["values"]["x"] = 2.0
    with pytest.raises(Exception):
        verify(rx.EXPORT_SCHEMA, doc)


def test_declared_result_value_mappings():
    r_doc = {"result": {"remote": {"result": {"coefficients": [
        {"term": "(Intercept)", "estimate": 1.5, "stdError": 0.1}, {"term": "dose", "estimate": 0.25, "stdError": 0.01}]}}}}
    out = rx.extract_result_values({"kind": "coefficient-table", "uncertaintyField": "stdError",
                                    "rename": {"(Intercept)": "intercept", "dose": "slope"}}, r_doc)
    assert out["values"] == {"intercept": 1.5, "slope": 0.25}
    assert out["uncertainty"]["values"]["slope"] == 0.01
    j_doc = {"result": {"remote": {"result": {"solution": [1.5, 0.25]}}}}
    assert rx.extract_result_values({"kind": "vector", "key": "solution", "names": ["intercept", "slope"]}, j_doc)["values"] == {"intercept": 1.5, "slope": 0.25}
    assert "error" in rx.extract_result_values({}, r_doc)
    assert "error" in rx.extract_result_values({"kind": "vector", "key": "solution", "names": ["a"]}, j_doc)


# ---------------------------------------------------------------------------
# PostgreSQL integration (real Workspace routes and tables)

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


RX = {"Authorization": "Bearer research-client-test"}


def make_run(client, user, project, *, verified=True, status="succeeded"):
    """Registry records via real routes; the runtime receipt is inserted as the worker would."""
    from app.db import session_scope
    from app.models import PolyglotExecutionReceipt
    from app.object_store import store_artifact
    from app.registry import store_run_output, sync_run_from_job
    from app.schemas import ArtifactStoreRequest, ExecutionRunOutputRequest
    sfx = uuid4().hex[:8]
    assert client.post("/v1/datasets", headers=hdr(user), json={"schema": "sc-workspace-dataset-record/1.0",
        "datasetId": f"ds-{sfx}", "projectId": project, "name": "Synthetic", "datasetType": "table",
        "metadata": {"scientificClassification": "synthetic"}}).status_code == 200
    assert client.post("/v1/models", headers=hdr(user), json={"schema": "sc-workspace-model-record/1.0",
        "modelId": f"m-{sfx}", "projectId": project, "name": "OLS", "modelKind": "statistical",
        "executionTarget": "workspace", "executionOperation": "workspace.polyglot.r.linear-model",
        "metadata": {"researchResultValues": {"kind": "coefficient-table", "uncertaintyField": "stdError",
                                              "rename": {"(Intercept)": "intercept", "x": "slope"}}}}).status_code == 200
    run = client.post("/v1/runs", headers=hdr(user), json={"schema": "sc-workspace-execution-run/1.0",
        "projectId": project, "datasetRefs": [{"datasetId": f"ds-{sfx}"}], "modelRef": {"modelId": f"m-{sfx}"}}).json()["item"]
    rid, job = run["runId"], f"job-{sfx}"
    with session_scope() as db:
        doc = {"schema": "sc-workspace-polyglot-result/1.0", "result": {"remote": {"result": {"coefficients": [
            {"term": "(Intercept)", "estimate": 1.5, "stdError": 0.1}, {"term": "x", "estimate": 0.25, "stdError": 0.01}]}}}}
        art = store_artifact(db, user, ArtifactStoreRequest.model_validate({"schema": "sc-workspace-artifact-store/1.0",
            "artifactId": f"polyglot-result-{job}", "projectId": project, "filename": "r.json",
            "mediaType": "application/vnd.sc.workspace.polyglot-result+json",
            "contentBase64": base64.b64encode(json.dumps(doc).encode()).decode(), "expectedRevision": 0, "metadata": {}}))
        store_run_output(db, user, rid, ExecutionRunOutputRequest.model_validate({"schema": "sc-workspace-execution-run-output/1.0",
            "outputId": "polyglot-result", "artifactId": art.artifact_id, "role": "result"}))
        if verified:
            db.add(PolyglotExecutionReceipt(receipt_id=f"pgr_{sfx}", user_key=user, job_id=job, execution_run_id=rid,
                language="r", runtime="r-statistical-econometric", operation="workspace.polyglot.r.linear-model",
                request_fingerprint="0" * 64, result_artifact_id=art.artifact_id, result_sha256=art.sha256,
                result_bytes=art.bytes, transport="http-json", status="succeeded", details_json={}))
        sync_run_from_job(db, user, rid, job, status, 100)
        db.commit()
    return rid


def grant(client, user, project, run):
    r = client.post("/v1/research-exports/grants", headers=hdr(user), json={"projectId": project, "runId": run})
    return r


@pg
def test_verified_export_is_signed_owner_scoped_and_has_values(client):
    run = make_run(client, "owner-a", "proj-a")
    g = grant(client, "owner-a", "proj-a", run)
    assert g.status_code == 200
    out = client.post("/v1/research-exports/fetch", headers=RX, json={"grant": g.json()["grant"]})
    assert out.status_code == 200, out.text
    doc = out.json()
    verify(rx.EXPORT_SCHEMA, doc)
    assert doc["ownerScope"] == "workspace-user:owner-a" and doc["verification"]["status"] == "executed-verified"
    assert doc["resultValues"]["values"] == {"intercept": 1.5, "slope": 0.25}
    assert doc["boundaries"]["artifactBytesIncluded"] is False


@pg
def test_cross_owner_and_client_credential_are_enforced(client):
    run = make_run(client, "owner-a", "proj-a")
    assert grant(client, "owner-b", "proj-a", run).status_code == 404
    assert grant(client, "owner-a", "proj-other", run).status_code == 404
    token = grant(client, "owner-a", "proj-a", run).json()["grant"]
    assert client.post("/v1/research-exports/fetch", json={"grant": token}).status_code == 401
    assert client.post("/v1/research-exports/fetch", headers={"Authorization": "Bearer workspace-service-test"},
                       json={"grant": token}).status_code == 401
    body, sig = token.split(".")
    forged_claims = json.loads(rx._b64d(body))
    forged_claims["sub"] = "owner-b"
    forged = rx._b64e(canonical_bytes(forged_claims)) + "." + sig
    assert client.post("/v1/research-exports/fetch", headers=RX, json={"grant": forged}).status_code == 403


@pg
def test_unverified_and_failed_runs_are_not_verified(client):
    failed = make_run(client, "owner-a", "proj-a", verified=False, status="failed")
    doc = client.post("/v1/research-exports/fetch", headers=RX,
                      json={"grant": grant(client, "owner-a", "proj-a", failed).json()["grant"]}).json()
    assert doc["verification"]["status"] == "failed" and doc["resultValues"]["values"] == {}
    manual = make_run(client, "owner-a", "proj-a", verified=False, status="succeeded")
    doc = client.post("/v1/research-exports/fetch", headers=RX,
                      json={"grant": grant(client, "owner-a", "proj-a", manual).json()["grant"]}).json()
    assert doc["verification"]["status"] == "succeeded-without-runtime-receipt"


@pg
def test_revocation_and_withdrawal(client):
    run = make_run(client, "owner-a", "proj-a")
    g = grant(client, "owner-a", "proj-a", run).json()
    assert client.post(f"/v1/research-exports/grants/{g['grantId']}/revoke", headers=hdr("owner-b")).status_code == 404
    assert client.post(f"/v1/research-exports/grants/{g['grantId']}/revoke", headers=hdr("owner-a")).status_code == 200
    assert client.post("/v1/research-exports/fetch", headers=RX, json={"grant": g["grant"]}).status_code == 403
    g2 = grant(client, "owner-a", "proj-a", run).json()
    notice = client.post(f"/v1/research-exports/runs/{run}/withdraw", headers=hdr("owner-a"),
                         json={"projectId": "proj-a", "reason": "test"}).json()
    verify(rx.WITHDRAWAL_SCHEMA, notice)
    assert notice["ownerScope"] == "workspace-user:owner-a" and notice["runId"] == run
    assert client.post("/v1/research-exports/fetch", headers=RX, json={"grant": g2["grant"]}).status_code == 403
    assert grant(client, "owner-a", "proj-a", run).status_code == 410
