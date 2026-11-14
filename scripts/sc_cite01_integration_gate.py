#!/usr/bin/env python3
"""SC-CITE-01 live *staging* Workspace -> Research acceptance.

This is an opt-in destructive-to-SYNTHETIC-DATA-only operator check. It creates a
Research *draft* (never publishes) and imports two citations into a pre-existing
synthetic Workspace project. There is no production fallback and no secret in
the receipt. Two distinct real staging sessions are supplied in chmod-600 JSON
header files. Do not use production accounts or production URLs.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import secrets
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCHEMA = "sc-cite01-live-integration/1.0"
PREFIX = "/v1/private-research/reporting-studio/publication/citations"
RESEARCH = "/api/research/v1/editorial"


def require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def stage_url(name: str) -> str:
    url = require(name).rstrip("/")
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise RuntimeError(f"{name} cannot contain credentials, query or fragment")
    if not ((parsed.scheme == "https" and "staging" in host) or
            (parsed.scheme == "http" and host in ("127.0.0.1", "localhost"))):
        raise RuntimeError(f"{name} must use a named HTTPS staging host or a loopback SSH tunnel")
    return url


def synthetic(name: str) -> str:
    value = require(name)
    if not value.startswith("synthetic-") or not all(c.isalnum() or c in "-_" for c in value):
        raise RuntimeError(f"{name} must identify an explicitly synthetic resource")
    return value


def headers(name: str) -> dict:
    path = Path(require(name))
    if not path.is_file() or path.stat().st_mode & 0o077:
        raise RuntimeError(f"{name}: header file must exist and be mode 0600")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not any(k.lower() in ("authorization", "cookie") for k in data):
        raise RuntimeError(f"{name}: supply a real staging Authorization or Cookie header")
    if any(k.lower() in ("host", "content-length") for k in data):
        raise RuntimeError(f"{name}: cannot override Host or Content-Length")
    return {str(k): str(v) for k, v in data.items()}


def call(base: str, method: str, route: str, auth: dict | None = None, body=None,
         allowed=(200,)) -> tuple[int, dict]:
    data = json.dumps(body, separators=(",", ":")).encode() if body is not None else None
    req = Request(base + route, data=data, method=method,
                  headers={"Accept": "application/json",
                           **({"Content-Type": "application/json"} if body is not None else {}),
                           **(auth or {})})
    try:
        with urlopen(req, timeout=20) as response:
            status = response.status
            payload = response.read(2_000_000)
    except HTTPError as exc:
        status = exc.code
        payload = b"{}"
    except URLError as exc:
        raise RuntimeError(f"Cannot reach staging endpoint {route}") from exc
    if status not in allowed:
        raise RuntimeError(f"{method} {route}: HTTP {status}, expected {allowed}")
    try:
        result = json.loads(payload) if payload else {}
    except ValueError as exc:
        raise RuntimeError(f"{method} {route}: invalid JSON response") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"{method} {route}: expected JSON object")
    return status, result


def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def main() -> int:
    if require("SC_CITE01_ACCEPT_STAGING") != "SYNTHETIC_STAGING_ONLY":
        raise RuntimeError("Explicit SYNTHETIC_STAGING_ONLY authorization required")
    workspace, research = stage_url("SC_CITE01_WORKSPACE_URL"), stage_url("SC_CITE01_RESEARCH_URL")
    if workspace == research:
        raise RuntimeError("Workspace and Research must be distinct service origins")
    project = synthetic("SC_CITE01_SYNTHETIC_PROJECT_ID")
    source = synthetic("SC_CITE01_SYNTHETIC_SOURCE_ID")
    area = synthetic("SC_CITE01_SYNTHETIC_RESEARCH_AREA")
    project_key = synthetic("SC_CITE01_SYNTHETIC_RESEARCH_PROJECT_KEY")
    library_id = require("SC_CITE01_VERIFIED_PUBLIC_LIBRARY_ID")
    owner_w = headers("SC_CITE01_WS_OWNER_A_HEADERS")
    other_w = headers("SC_CITE01_WS_OWNER_B_HEADERS")
    owner_r = headers("SC_CITE01_RH_OWNER_A_HEADERS")
    other_r = headers("SC_CITE01_RH_OWNER_B_HEADERS")
    if owner_w == other_w or owner_r == other_r:
        raise RuntimeError("Owner A and owner B must use distinct real staging credentials")
    receipt = Path(require("SC_CITE01_INTEGRATION_RECEIPT"))
    if receipt.exists():
        raise RuntimeError("Refusing to overwrite an existing acceptance receipt")

    checks = []
    collection_route = f"{PREFIX}/projects/{project}"
    status, _ = call(workspace, "GET", collection_route, allowed=(401, 403))
    checks.append("anonymous_workspace_denied")
    status, _ = call(workspace, "GET", collection_route, other_w, allowed=(403, 404))
    checks.append("cross_owner_workspace_denied")
    _, initial = call(workspace, "GET", collection_route, owner_w)
    rev = initial.get("projectRevision")
    if not isinstance(rev, int) or rev < 1:
        raise RuntimeError("No valid synthetic Workspace project revision")
    _, imported = call(workspace, "POST", collection_route + "/import-source", owner_w,
                       {"sourceArtifactId": source, "expectedProjectRevision": rev}, (200, 201))
    if not imported.get("items") or not imported.get("import"):
        raise RuntimeError("Source import returned no verifiable items/report")
    rev = imported["projectRevision"]
    checks.append("owner_source_import")

    _, imported_lib = call(workspace, "POST", collection_route + "/import-library", owner_w,
                           {"recordId": library_id, "expectedProjectRevision": rev}, (200, 201))
    items = imported_lib.get("items", [])
    if not any(x.get("provenance", {}).get("libraryRecordId") == library_id for x in items):
        raise RuntimeError("Library source provenance not preserved")
    checks.append("verified_library_import")
    key = next((x.get("key") for x in items
                if x.get("provenance", {}).get("sourceArtifactId") == source), None)
    if not key:
        raise RuntimeError("Imported source ID not preserved in item provenance")

    _, bib = call(workspace, "POST", collection_route + "/bibliography", owner_w,
                  {"style": "harvard"})
    if bib.get("style") != "harvard" or not bib.get("references"):
        raise RuntimeError("Harvard bibliography missing")
    checks.append("harvard_bibliography")

    section = {"heading": "Synthetic citation acceptance", "body": f"Research [@{key}, p. 2]."}
    payload = {"sections": [section], "style": "harvard"}
    _, snap = call(workspace, "POST", collection_route + "/snapshot", owner_w, payload)
    frozen = snap.get("bibliography")
    if snap.get("schema") != "sc-citation-snapshot/1.0" or not frozen or not frozen.get("markers"):
        raise RuntimeError("Workspace citation snapshot missing frozen marker rendering")
    _, replay = call(workspace, "POST", collection_route + "/snapshot", owner_w, payload)
    if replay != snap:
        raise RuntimeError("Workspace snapshot not replay-stable")
    checks.append("snapshot_replay")

    # Creates a new private draft only. No submission, approval or publication.
    slug = "synthetic-cite01-" + secrets.token_hex(7)
    _, created = call(research, "POST", RESEARCH + "/articles", owner_r,
                      {"areaSlug": area, "projectKey": project_key, "workspaceProjectId": project,
                       "slug": slug, "title": "Synthetic Citation Studio acceptance",
                       "summary": "Non-public, synthetic release evidence"}, (200, 201))
    if created.get("slug") != slug:
        raise RuntimeError("Research article creation did not return the synthetic slug")
    _, saved = call(research, "POST", RESEARCH + f"/articles/{slug}/revisions", owner_r,
                    {"baseRevision": 0, "title": "Synthetic Citation Studio acceptance",
                     "summary": "Synthetic-only", "sections": [section],
                     "references": [], "publication": {"type": "report", "bibliography": frozen},
                     "changeSummary": "SC-CITE-01 synthetic snapshot handoff"}, (200, 201))
    revision = saved.get("revision")
    if revision != 1 or not saved.get("documentSha256"):
        raise RuntimeError("Research failed to create revision 1 with a content digest")
    _, stored = call(research, "GET", RESEARCH + f"/articles/{slug}", owner_r)
    head = stored.get("head") or {}
    if (stored.get("headRevision") != 1 or
            (head.get("publication") or {}).get("bibliography") != frozen or
            head.get("sections", [{}])[0].get("body") != section["body"]):
        raise RuntimeError("Research did not persist the exact Workspace bibliography and source markers")
    _, revision_view = call(research, "GET", RESEARCH + f"/articles/{slug}/revisions/1", owner_r)
    if (revision_view.get("documentSha256") != saved["documentSha256"] or
            (revision_view.get("document") or {}).get("publication", {}).get("bibliography") != frozen):
        raise RuntimeError("Research revision replay differs from original frozen bibliography")
    call(research, "GET", RESEARCH + f"/articles/{slug}", other_r, allowed=(403, 404))
    checks.extend(["research_editorial_revision_persisted", "research_revision_replay",
                   "research_cross_owner_denied"])

    body = {"schema": SCHEMA, "release": "sc-cite01-43be67f",
            "createdUtc": datetime.now(timezone.utc).isoformat(),
            "outcome": "PASS", "checks": checks,
            "workspaceOrigin": workspace, "researchOrigin": research,
            "syntheticProjectId": project, "syntheticResearchSlug": slug,
            "researchDocumentSha256": saved["documentSha256"],
            "bibliographySha256": hashlib.sha256(canonical(frozen)).hexdigest()}
    receipt.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        json.dump(body, out, sort_keys=True, indent=2)
        out.write("\n")
    print(f"PASS: {len(checks)} live staging checks; evidence {receipt}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Never echo header values, authentication responses, or secrets.
        print(f"NO-GO: {exc}", file=sys.stderr)
        sys.exit(1)
