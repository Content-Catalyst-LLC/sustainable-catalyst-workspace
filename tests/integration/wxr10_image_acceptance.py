"""Synthetic HTTP acceptance for the isolated WXR-10 image replacement rehearsal."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from app import session_auth


ROOT = "/v1/private-research/persistent-projects"
REPORTING = "/v1/private-research/reporting-studio"
ORIGIN = "https://workspace.sustainablecatalyst.com"
SOURCE = {
    "schema": "sc-lab-scientific-visualization/1.0",
    "kind": "heatmap",
    "title": "Synthetic WXR-10 matrix",
    "description": "Synthetic CI fixture; no Wexford measurement",
    "xLabel": "x", "yLabel": "y",
    "xValues": [1, 2], "yValues": [3, 4],
    "cells": [
        {"x": 1, "y": 3, "z": -1, "xIndex": 0, "yIndex": 0},
        {"x": 2, "y": 4, "z": 1, "xIndex": 1, "yIndex": 1},
    ],
}


def request(base, path, subject=None, payload=None, origin=True):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if subject:
        token = session_auth.issue_session_token(subject)
        headers["Cookie"] = f"sc_workspace_session={token}"
    if body is not None and origin:
        headers["Origin"] = ORIGIN
    req = urllib.request.Request(base + path, data=body, headers=headers,
                                 method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
    except urllib.error.HTTPError as error:
        return error.code, {key.lower(): value for key, value in error.headers.items()}, error.read()


def expected(status, result, label):
    assert result[0] == status, f"{label}: expected {status}, got {result[0]}: {result[2][:300]!r}"
    return result


def create(base, state_path):
    status, _, data = expected(201, request(base, ROOT, "wxr10-owner", {"title": "Synthetic WXR-10 project"}), "create project")
    project_id = json.loads(data)["projectId"]
    raw = json.dumps(SOURCE, ensure_ascii=False, separators=(",", ":")).encode()
    status, _, data = expected(201, request(base, f"{ROOT}/{project_id}/files", "wxr10-owner", {
        "filename": "synthetic-lab-heatmap.json", "contentBase64": base64.b64encode(raw).decode(),
    }), "upload source")
    file_record = json.loads(data)
    digest = hashlib.sha256(raw).hexdigest()
    assert file_record["sha256"] == digest
    ref = {
        "artifact_id": file_record["artifactId"], "sha256": digest,
        "source_revision": file_record["revision"], "expected_project_revision": 1,
        "dataset_refs": ["synthetic:unitless"], "computation_refs": ["synthetic:none"],
        "evidence_refs": ["synthetic:no-field-evidence"],
        "rights_ref": "Synthetic CI only", "reproduction": "This source fixture is synthetic.",
        "heatmap_unit": "unitless", "evidence_classification": "design-sensitivity",
        "display": {"color": "#175a3b", "line_width": 3, "frame_index": 0},
    }
    expected(200, request(base, f"{REPORTING}/projects/{project_id}/preview", "wxr10-owner", ref), "preview")
    status, _, data = expected(201, request(base, f"{REPORTING}/projects/{project_id}/reports", "wxr10-owner", ref), "save report")
    report = json.loads(data)["report"]
    state = {"project_id": project_id, "artifact_id": file_record["artifactId"],
             "report_id": report["asset_id"], "report_revision": report["revision_id"],
             "source_sha256": digest}
    state_path.write_text(json.dumps(state, sort_keys=True))
    verify(base, state_path)


def verify(base, state_path):
    state = json.loads(state_path.read_text())
    pid = state["project_id"]
    expected(200, request(base, f"{ROOT}/{pid}", "wxr10-owner"), "reopen project")
    report_path = (f"{REPORTING}/projects/{pid}/revisions/{state['report_revision']}"
                   f"/reports/{state['report_id']}")
    status, _, data = expected(200, request(base, report_path, "wxr10-owner"), "reopen report")
    view = json.loads(data)["view"]
    assert view["source_sha256"] == state["source_sha256"] and view["svg"]
    status, headers, data = expected(200, request(base, f"{ROOT}/{pid}/files/{state['artifact_id']}/download", "wxr10-owner"), "download source")
    assert hashlib.sha256(data).hexdigest() == state["source_sha256"]
    assert headers.get("x-research-sha256") == state["source_sha256"]
    status, _, data = expected(200, request(base, report_path + "/export.pdf", "wxr10-owner"), "export PDF")
    assert data.startswith(b"%PDF-")
    expected(401, request(base, report_path), "anonymous denial")
    expected(404, request(base, report_path, "wxr10-other"), "cross-owner denial")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("create", "verify"))
    parser.add_argument("--base", default="http://127.0.0.1:18089")
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    assert os.getenv("SC_WORKSPACE_SESSION_SIGNING_SECRET") == "synthetic-wxr10-ci-only"
    (create if args.mode == "create" else verify)(args.base, Path(args.state))
    print(f"WXR-10 isolated image {args.mode}: PASS")
