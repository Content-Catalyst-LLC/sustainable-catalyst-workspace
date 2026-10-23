"""Synthetic end-to-end HTTP check for the isolated WXR-09.4 Caddy/backend pair."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.session_auth import issue_session_token


BASE = "http://127.0.0.1:18080"
ROOT = "/v1/private-research/persistent-projects"
ORIGIN = "https://workspace.sustainablecatalyst.com"
FILES = {
    "report.pdf": b"%PDF-1.7 synthetic",
    "notebook.ipynb": b'{"cells":[],"nbformat":4,"nbformat_minor":5}',
    "figure.svg": b"<svg xmlns='http://www.w3.org/2000/svg'></svg>",
    "figure.png": b"\x89PNG\r\n\x1a\nsynthetic",
    "measurements.csv": b"x,y\n1,2\n",
    "provenance.json": b'{"synthetic":true}',
    "map.geojson": b'{"type":"FeatureCollection","features":[]}',
}


def call(path: str, subject: str | None = "alice", method: str = "GET", payload=None,
         origin: bool = False):
    headers = {}
    if subject is not None:
        headers["Cookie"] = "sc_workspace_session=" + issue_session_token(subject)
    if origin:
        headers["Origin"] = ORIGIN
    if payload is not None:
        headers["Content-Type"] = "application/json"
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, response.read(), response.headers
    except HTTPError as exc:
        return exc.code, exc.read(), exc.headers


def create(state_path: Path) -> None:
    status, body, _ = call(ROOT, method="POST", payload={"title": "Synthetic Wexford"}, origin=True)
    assert status == 201, (status, body)
    project_id = json.loads(body)["projectId"]
    items = []
    for name, content in FILES.items():
        payload = {"filename": name, "contentBase64": base64.b64encode(content).decode()}
        status, body, _ = call(f"{ROOT}/{project_id}/files", method="POST", payload=payload, origin=True)
        assert status == 201, (name, status, body)
        item = json.loads(body)
        assert item["sha256"] == hashlib.sha256(content).hexdigest()
        items.append({"artifactId": item["artifactId"], "filename": name, "sha256": item["sha256"]})
    status, _, _ = call(f"{ROOT}/{project_id}/files", method="POST", payload={
        "filename": "report.pdf", "contentBase64": base64.b64encode(FILES["report.pdf"]).decode(),
    }, origin=True)
    assert status == 409
    state_path.write_text(json.dumps({"projectId": project_id, "files": items}))


def verify(state_path: Path) -> None:
    state = json.loads(state_path.read_text())
    project_id = state["projectId"]
    status, body, _ = call(f"{ROOT}/{project_id}")
    assert status == 200 and len(json.loads(body)["files"]) == len(state["files"])
    for item in state["files"]:
        status, content, headers = call(
            f"{ROOT}/{project_id}/files/{item['artifactId']}/download")
        assert status == 200
        assert content == FILES[item["filename"]]
        assert hashlib.sha256(content).hexdigest() == item["sha256"]
        assert headers.get("X-Research-SHA256") == item["sha256"]
        assert headers.get("Content-Disposition", "").startswith("attachment;")
    for subject in (None, "bob"):
        status, _, _ = call(f"{ROOT}/{project_id}", subject=subject)
        assert status == (401 if subject is None else 404)
        status, _, _ = call(f"{ROOT}/{project_id}/files/{state['files'][0]['artifactId']}/download",
                            subject=subject)
        assert status == (401 if subject is None else 404)
    status, _, _ = call("/v1/session", method="DELETE")
    assert status == 200
    status, _, _ = call(f"{ROOT}/{project_id}", subject=None)
    assert status == 401


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["create", "verify"])
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    (create if args.phase == "create" else verify)(args.state)
    print(f"Isolated HTTP {args.phase} phase passed")


if __name__ == "__main__":
    main()
