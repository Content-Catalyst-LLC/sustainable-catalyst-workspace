"""Run against a newly created disposable PostgreSQL database and object store."""
import base64
import hashlib
import os
from pathlib import Path
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("SC_REPRODUCTION_TEST_POSTGRES") != "1",
    reason="Requires an explicitly opted-in disposable PostgreSQL database",
)

STANDARD = "reproduction-verifications"
CROSS_RUNTIME = "reproduction/cross-runtime/verifications"


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from app.db import get_engine, initialize_schema
    from app.main import app

    assert get_engine().dialect.name == "postgresql"
    initialize_schema()
    with TestClient(app) as http:
        yield http


def api(client, method, path, headers, body=None):
    response = client.request(method, f"/v1/{path}", headers=headers, json=body)
    assert response.status_code == 200, response.text
    return response.json()


def create(client, path, schema, headers, **body):
    return api(client, "POST", path, headers, {"schema": f"sc-workspace-{schema}/1.0", **body})["item"]


def artifact(client, headers, name, raw, revision=0):
    return create(client, "artifacts", "artifact-store", headers, artifactId=name,
                  expectedRevision=revision, mediaType="application/json",
                  contentBase64=base64.b64encode(raw).decode())


def completed_runs(client, case):
    from app.db import session_scope
    from app.jobs import claim_next_job
    from app.worker import process_job

    user = f"replay-{case}-{uuid4().hex}"
    headers = {"Authorization": f"Bearer {os.environ['SC_WORKSPACE_SERVICE_TOKEN']}", "X-SC-User-ID": user}
    raw = b'{"value":2.5}'
    digest = hashlib.sha256(raw).hexdigest()
    for run in ("original", "replay"):
        create(client, "runs", "execution-run", headers, runId=run, operation="workspace.echo")
        job = create(client, "jobs", "job-request", headers, executionRunId=run, operation="workspace.echo")
        with session_scope() as db:
            row = claim_next_job(db, "isolated-reproduction-test")
            assert row.job_id == job["jobId"]
        process_job(row)
        assert api(client, "GET", f"runs/{run}", headers)["item"]["status"] == "succeeded"
        if case == "digest-only":
            output = {"sha256": digest, "bytes": len(raw)}
        else:
            content = b'{"value":2.50000000001}' if case == "tolerance" and run == "replay" else raw
            artifact(client, headers, run + "-" + user, content)
            output = {"artifactId": run + "-" + user}
        create(client, f"runs/{run}/outputs", "execution-run-output", headers, outputId="output", **output)
    return headers, raw, digest


def verify(client, path, headers, **overrides):
    schema = "reproduction-verification" if path == STANDARD else "cross-runtime-verification"
    return create(client, path, schema, headers,
                  originalRunId="original", reproductionRunId="replay", **overrides)


@pytest.mark.parametrize(("case", "artifact_status", "reason"), [
    ("intact", "verified", None),
    ("changed-head", "verified", None),
    ("corrupted", "corrupted", "registered-content-mismatch"),
    ("missing-blob", "missing", "artifact-blob-missing"),
    ("missing-record", "missing", "registered-artifact-revision-missing"),
    ("unavailable", "unavailable", "artifact-storage-unavailable"),
    ("digest-only", "unavailable", "unverifiable-reference"),
])
def test_registered_equivalence_and_byte_integrity(client, case, artifact_status, reason):
    headers, raw, digest = completed_runs(client, case)
    name = "original-" + headers["X-SC-User-ID"]
    blob = Path(os.environ["SC_WORKSPACE_OBJECT_STORAGE_ROOT"]) / "sha256" / digest[:2] / digest[2:4] / digest
    if case == "changed-head":
        artifact(client, headers, name, b'{"value":42}', revision=1)
    elif case == "corrupted":
        blob.write_bytes(b"!" + raw[1:])
    elif case == "missing-blob":
        blob.unlink()
    elif case == "missing-record":
        api(client, "DELETE", f"artifacts/{name}", headers)
    elif case == "unavailable":
        blob.unlink()
        blob.mkdir()

    try:
        for path in (STANDARD, CROSS_RUNTIME):
            item = verify(client, path, headers)
            details = item["details"]
            verified = artifact_status == "verified"
            assert details["registeredDigestsMatch"] is True
            assert details["scientificValidationPerformed"] is False
            assert item["classification"] == ("exact" if verified else "incomplete")
            assert item["exactOutputs"] is verified
            assert details["artifactIntegrity"]["status"] == ("verified" if verified else "incomplete")
            if path == STANDARD:
                assert details["comparisonExecuted"] is verified
                check = details["artifactIntegrity"]["original"][0]
                identifier = item["verificationId"]
            else:
                assert item["equivalentOutputs"] is verified
                check = details["comparisons"][0]["originalArtifactCheck"]
                identifier = item["receiptId"]
            assert check["status"] == artifact_status
            assert check.get("reason") == reason
            if verified:
                assert (check["artifactRevision"], check["observedSha256"], check["observedBytes"]) == (1, digest, len(raw))
            if case == "corrupted":
                assert check["observedSha256"] != digest
                assert check["observedBytes"] == len(raw)
            assert api(client, "GET", f"{path}/{identifier}", headers)["item"] == item
            assert item in api(client, "GET", path, headers)["items"]
    finally:
        if case == "unavailable":
            blob.rmdir()
        if case in {"corrupted", "missing-blob", "unavailable"}:
            blob.write_bytes(raw)


def test_cross_runtime_compares_only_checked_json(client):
    headers, _, _ = completed_runs(client, "tolerance")
    item = verify(client, CROSS_RUNTIME, headers, comparisonMode="tolerance-aware-json",
                  absoluteTolerance=1e-9, relativeTolerance=0)
    assert item["classification"] == "equivalent"
    assert item["exactOutputs"] is False
    assert item["equivalentOutputs"] is True
    assert item["details"]["registeredDigestsMatch"] is False
    assert item["details"]["comparisons"][0]["stats"]["numericComparisons"] == 1
    assert verify(client, CROSS_RUNTIME, headers, comparisonMode="exact-digest")["classification"] == "divergent"


@pytest.mark.parametrize(("path", "key"), [(STANDARD, "verificationId"), (CROSS_RUNTIME, "receiptId")])
def test_legacy_exact_receipt_is_retained_without_byte_claim(client, path, key):
    from app.db import session_scope
    from app.models import CrossRuntimeVerificationReceipt, ReproductionVerification

    headers, _, _ = completed_runs(client, "legacy")
    item = verify(client, path, headers)
    model = ReproductionVerification if path == STANDARD else CrossRuntimeVerificationReceipt
    legacy_details = {"comparisonExecuted": False, "comparisonMode": "metadata-and-content-digests"}
    with session_scope() as db:
        row = db.get(model, (headers["X-SC-User-ID"], item[key]))
        row.details_json = legacy_details
        db.commit()

    legacy = api(client, "GET", f"{path}/{item[key]}", headers)["item"]
    assert legacy["classification"] == "incomplete"
    assert legacy["exactOutputs"] is False
    assert legacy["fingerprint"] == item["fingerprint"]
    assert legacy["details"]["registeredClassification"] == "exact"
    assert legacy["details"]["artifactIntegrity"]["status"] == "not-checked"
    with session_scope() as db:
        row = db.get(model, (headers["X-SC-User-ID"], item[key]))
        assert row.classification == "exact"
        assert row.details_json == legacy_details
