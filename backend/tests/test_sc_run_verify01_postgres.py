"""Real Workspace ASGI, worker and PostgreSQL checks using disposable synthetic fixtures."""
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

import pytest


pytestmark = pytest.mark.skipif(
    not os.environ.get("SC_RUN_VERIFY_EVIDENCE"), reason="Use scripts/sc_run_verify01_local.sh"
)

PROJECT = "synthetic-run-study"
OPERATION = "workspace.compute.describe"
OWNER = {"Authorization": "Bearer local-synthetic-service-token", "X-SC-User-ID": "fixture-owner"}
OTHER = {**OWNER, "X-SC-User-ID": "fixture-other"}


def request(client, method, path, *, status=200, headers=OWNER, body=None):
    response = client.request(method, path, headers=headers, json=body)
    assert response.status_code == status, (method, path, response.status_code, response.text)
    return response.json()


def post(client, resource, schema, *, status=200, headers=OWNER, **fields):
    return request(client, "POST", "/v1/" + resource, status=status, headers=headers,
                   body={"schema": f"sc-workspace-{schema}/1.0", **fields})


def claim_and_process(client, job_id):
    from app.db import session_scope
    from app.jobs import claim_next_job
    from app.worker import process_job

    with session_scope() as db:
        row = claim_next_job(db, "sc-run-verify-local-worker")
        assert row.job_id == job_id
    assert request(client, "GET", f"/v1/jobs/{job_id}")["item"]["status"] == "running"
    process_job(row)
    return request(client, "GET", f"/v1/jobs/{job_id}")["item"]


def blob_path(digest):
    return Path(os.environ["SC_WORKSPACE_OBJECT_STORAGE_ROOT"]) / "sha256" / digest[:2] / digest[2:4] / digest


def test_run_lifecycle_and_independent_replay():
    from fastapi.testclient import TestClient
    from app.db import get_engine
    from app.main import app

    numbers = [1.25, 2.5, 4.75, 8.0]
    raw_input = json.dumps([{"value": x} for x in numbers]).encode()
    with TestClient(app, base_url="https://workspace.test") as client:
        service_version = request(client, "GET", "/health", headers={})["version"]
        def put_artifact(raw, revision):
            return post(client, "artifacts", "artifact-store", projectId=PROJECT, artifactId="rows",
                        contentBase64=base64.b64encode(raw).decode(), expectedRevision=revision)["item"]

        original_artifact = put_artifact(raw_input, 0)
        records = [
            ("datasets", "dataset-record", "datasetId", "data",
             {"sourceKind": "artifact", "artifactId": "rows", "datasetType": "table"}),
            ("models", "model-record", "modelId", "model",
             {"executionTarget": "workspace", "executionOperation": OPERATION}),
            ("parameter-sets", "parameter-set", "parameterSetId", "params",
             {"modelId": "model", "parameters": {"columns": ["value"]}}),
            ("execution-environments", "execution-environment", "environmentId", "env",
             {"runtime": {"language": "python", "version": "3.12"}}),
        ]
        first = {}
        for resource, schema, key, identifier, fields in records:
            first[resource] = post(client, resource, schema, projectId=PROJECT, name="Initial",
                                   expectedRevision=0, **{key: identifier}, **fields)["item"]
            assert first[resource]["revision"] == 1

        descriptor = {"schema": "sc-workspace-parameter-set/1.0", "parameterSetId": "params",
                      "projectId": PROJECT, "modelId": "model", "name": "Initial",
                      "parameters": {"columns": ["value"]}, "metadata": {}}
        fingerprint = hashlib.sha256(json.dumps(descriptor, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        assert first["parameter-sets"]["fingerprint"] == fingerprint
        refs = dict(datasetRefs=[{"datasetId": "data", "revision": 1}],
                    modelRef={"modelId": "model", "revision": 1},
                    parameterSetRef={"parameterSetId": "params", "revision": 1},
                    environmentRef={"environmentId": "env", "revision": 1})

        def make_run(run_id, **overrides):
            fields = dict(projectId=PROJECT, runId=run_id, idempotencyKey=run_id, **refs)
            return post(client, "runs", "execution-run", **{**fields, **overrides})

        original = make_run("original")["item"]
        assert original["status"] == "planned"
        assert make_run("original")["replayed"]
        make_run("original", operation="workspace.echo", status=409)
        make_run("missing-revision", datasetRefs=[{"datasetId": "data", "revision": 99}], status=409)
        request(client, "GET", "/v1/runs/original", headers={}, status=401)
        request(client, "GET", "/v1/runs/original", headers=OTHER, status=404)
        post(client, "runs/original/outputs", "execution-run-output", headers=OTHER, status=404,
             outputId="denied", sha256="a" * 64)

        put_artifact(b'[{"value":999}]', 1)
        for resource, schema, key, identifier, fields in records:
            update = {"projectId": PROJECT, "name": "Updated", key: identifier, **fields}
            if resource == "parameter-sets":
                update["parameters"] = {"columns": ["missing"]}
            revised = post(client, resource, schema, expectedRevision=1, **update)["item"]
            assert revised["revision"] == 2 and revised["fingerprint"] != first[resource]["fingerprint"]
            post(client, resource, schema, status=409, expectedRevision=1, **update)
            historic = request(client, "GET", f"/v1/{resource}/{identifier}/revisions/1")["item"]
            assert historic["fingerprint"] == first[resource]["fingerprint"]

        def submit(run_id):
            job_body = dict(operation=OPERATION, projectId=PROJECT, executionRunId=run_id,
                            idempotencyKey=run_id, maxAttempts=1,
                            payload={"parameterInput": {"parameterSetId": "params", "parameterSetRevision": 1,
                                                        "fingerprint": fingerprint},
                                     "datasetInput": {"datasetId": "data", "datasetRevision": 1}})
            created = post(client, "jobs", "job-request", **job_body)
            assert created["item"]["status"] == "queued"
            assert post(client, "jobs", "job-request", **job_body)["replayed"]
            post(client, "jobs", "job-request", status=409, **{**job_body, "priority": 6})
            return created["item"]["jobId"]

        original_job = submit("original")
        source_blob = blob_path(original_artifact["sha256"])
        source_blob.write_bytes(b"!" + raw_input[1:])
        try:
            failed = claim_and_process(client, original_job)
            assert failed["status"] == "failed"
            assert failed["errorCode"] == "worker-exception"
            assert "failed integrity verification" in failed["errorMessage"]
            assert request(client, "GET", "/v1/runs/original")["item"]["status"] == "failed"
            assert request(client, "GET", "/v1/runs/original/outputs")["items"] == []
        finally:
            source_blob.write_bytes(raw_input)
        retried = post(client, f"jobs/{original_job}/retry", "job-action")["item"]
        assert retried["status"] == "queued"

        def finish(run_id, job_id):
            job = claim_and_process(client, job_id)
            assert job["status"] == "succeeded", job
            run = request(client, "GET", f"/v1/runs/{run_id}")["item"]
            assert run["status"] == "succeeded" and run["progress"] == 100
            assert run["inputFingerprint"] == original["inputFingerprint"]
            output, = request(client, "GET", f"/v1/runs/{run_id}/outputs")["items"]
            path = f"/v1/artifacts/{output['artifactId']}"
            artifact = request(client, "GET", path)
            raw = base64.b64decode(artifact["contentBase64"], validate=True)
            assert output["sha256"] == artifact["item"]["sha256"] == hashlib.sha256(raw).hexdigest()
            assert output["bytes"] == len(raw)
            request(client, "GET", path, headers=OTHER, status=404)
            return run, output, raw

        original_done, output, raw = finish("original", original_job)
        assert original_done["reproducibilityFingerprint"] != original["reproducibilityFingerprint"]
        request(client, "POST", "/v1/runs/original/state", status=409,
                body={"schema": "sc-workspace-execution-run-update/1.0", "status": "queued"})
        make_run("replay")
        replay, replay_output, replay_raw = finish("replay", submit("replay"))
        assert replay["jobId"] != original_job
        oracle = {"mean": statistics.mean(numbers), "std": statistics.stdev(numbers),
                  "median": statistics.median(numbers), "min": min(numbers), "max": max(numbers)}
        absolute, relative = 1e-12, 1e-12
        observed = [json.loads(item)["result"]["columns"]["value"]["numeric"] for item in (raw, replay_raw)]
        for field, expected in oracle.items():
            assert all(math.isclose(result[field], expected, rel_tol=relative, abs_tol=absolute)
                       for result in observed)
            assert math.isclose(observed[0][field], observed[1][field], rel_tol=relative, abs_tol=absolute)

        def verify(original_id, replay_id):
            return post(client, "reproduction-verifications", "reproduction-verification",
                        originalRunId=original_id, reproductionRunId=replay_id)["item"]

        verification = verify("original", "replay")
        assert verification["classification"] == "exact"
        assert verification["details"]["comparisonExecuted"] is False

        provenance_path = f"/v1/execution-provenance/projects/{PROJECT}"
        provenance = request(client, "GET", provenance_path + "/runs/original")["item"]
        assert provenance["inputs"]["datasets"][0]["ref"]["revision"] == 1
        assert provenance["inputs"]["parameterSet"]["ref"]["fingerprint"] == fingerprint
        assert provenance["outputs"][0]["sha256"] == output["sha256"]
        assert provenance["scientificReceipts"]
        snapshot = post(client, f"execution-provenance/projects/{PROJECT}/snapshots",
                        "scientific-execution-provenance-snapshot-request", runId="original")["item"]

        blob = blob_path(output["sha256"])
        blob.write_bytes(b"!" + raw[1:])
        try:
            request(client, "GET", f"/v1/artifacts/{output['artifactId']}", status=503)
            assert verify("original", "replay")["classification"] == "exact"
        finally:
            blob.write_bytes(raw)

    # New client and database connections, against the same disposable database and object store.
    get_engine().dispose()
    with TestClient(app, base_url="https://workspace.test") as client:
        assert request(client, "GET", "/v1/runs/original")["item"] == original_done
        assert request(client, "GET", provenance_path + "/snapshots")["items"] == [snapshot]
        assert request(client, "GET", "/v1/runs/original/outputs")["items"] == [output]
        events = request(client, "GET", "/v1/runs/original/events")["items"]
        statuses = [event["status"] for event in events]
        assert list(dict.fromkeys(statuses)) == ["planned", "queued", "running", "failed", "succeeded"]
        assert statuses.index("queued", statuses.index("failed")) < statuses.index("succeeded")
        job_events = request(client, "GET", f"/v1/jobs/{original_job}/events")["items"]
        assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
        assert [event["sequence"] for event in job_events] == list(range(1, len(job_events) + 1))

    evidence = {
        "backend_version": service_version, "input_fingerprint": original["inputFingerprint"],
        "parameter_fingerprint": fingerprint, "output_sha256": [output["sha256"], replay_output["sha256"]],
        "original_worker_failure": failed["errorCode"], "run_event_statuses": statuses,
        "job_event_types": [event["eventType"] for event in job_events],
        "snapshot_fingerprint": snapshot["provenanceFingerprint"],
        "replay": {"oracle": oracle, "observed": observed, "absolute_tolerance": absolute,
                   "relative_tolerance": relative, "workspace_classification": verification["classification"]},
        "corrupted_output": {"artifact_read_http": 503, "reproduction_metadata_classification": "exact"},
    }
    path = Path(os.environ["SC_RUN_VERIFY_EVIDENCE"]) / "lifecycle.json"
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def test_revoked_session_cannot_read_or_create_runs():
    from fastapi.testclient import TestClient
    from app.main import app

    origin = {"Origin": "https://workspace.test"}
    with TestClient(app, base_url="https://workspace.test") as client:
        request(client, "POST", "/v1/session/exchange", headers=OWNER)
        token = client.cookies["sc_workspace_session"]
        request(client, "GET", "/v1/runs", headers={})
        request(client, "DELETE", "/v1/session", headers=origin)
    with TestClient(app, base_url="https://workspace.test") as client:
        client.cookies.set("sc_workspace_session", token, domain="workspace.test", path="/")
        request(client, "GET", "/v1/runs", headers={}, status=401)
        post(client, "runs", "execution-run", operation="workspace.echo", headers=origin, status=401)
