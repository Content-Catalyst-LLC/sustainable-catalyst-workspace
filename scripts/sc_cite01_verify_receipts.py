#!/usr/bin/env python3
"""Verify independently produced SC-CITE-01 integration/recovery receipts.

A receipt is NOT evidence merely because it contains PASS: enforce required
checks, freshness, independent off-host archive digests, release identity and
archive content. Exit nonzero on any incomplete gate.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone, timedelta

RELEASE = "sc-cite01-43be67f"
CHECKS = {
    "anonymous_workspace_denied", "cross_owner_workspace_denied",
    "owner_source_import", "verified_library_import", "harvard_bibliography",
    "snapshot_replay", "research_editorial_revision_persisted",
    "research_revision_replay", "research_cross_owner_denied",
}


def verify(path: Path, schema: str):
    if not path.is_file():
        raise ValueError(f"Missing {schema} receipt")
    doc = json.loads(path.read_text())
    if (doc.get("schema"), doc.get("release"), doc.get("outcome")) != (schema, RELEASE, "PASS"):
        raise ValueError(f"Wrong release/schema or unsuccessful {schema} gate")
    created = datetime.fromisoformat(doc["createdUtc"])
    if created.tzinfo is None:
        raise ValueError("Receipt timestamp must include timezone")
    age = datetime.now(timezone.utc) - created.astimezone(timezone.utc)
    if not timedelta(0) <= age <= timedelta(hours=24):
        raise ValueError(f"{schema} receipt older than 24 hours or dated in the future")
    return doc


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    integration = Path(os.environ["SC_CITE01_INTEGRATION_RECEIPT"]).expanduser()
    recovery = Path(os.environ["SC_CITE01_RECOVERY_RECEIPT"]).expanduser()
    live = verify(integration, "sc-cite01-live-integration/1.0")
    if not CHECKS.issubset(set(live.get("checks") or [])):
        raise ValueError("Live integration receipt does not cover every required check")
    if not live.get("researchDocumentSha256") or not live.get("bibliographySha256"):
        raise ValueError("Missing Research revision and Workspace bibliography digests")
    if not live.get("syntheticProjectId", "").startswith("synthetic-"):
        raise ValueError("Integration was not synthetic-scope")
    restore = verify(recovery, "sc-cite01-recovery/1.0")
    for key in ("offhostBackup", "databaseRestore", "dataVolumeRestore",
                "networkIsolated", "productionStudioUnchanged"):
        if restore.get(key) is not True:
            raise ValueError(f"Recovery failed: {key}")
    if (restore.get("originalTables", 0) < 1 or
            restore["originalTables"] != restore.get("restoredTables")):
        raise ValueError("PostgreSQL restore table counts not verified")
    if (restore.get("archivedFiles", 0) < 1 or
            restore["archivedFiles"] != restore.get("restoredFiles")):
        raise ValueError("Data-volume restore file counts not verified")
    # Recovery script creates its receipt next to these two persistent off-host archives.
    for filename, key in (("sc_workspace.dump", "dbArchiveSha256"),
                          ("sc-workspace-data.tgz", "volumeArchiveSha256")):
        path = recovery.parent / filename
        if not path.is_file() or sha(path) != restore.get(key):
            raise ValueError(f"Off-host archive missing or digest mismatch: {filename}")
    print("GO-CANDIDATE: independent live integration and off-host restore evidence verified")
    print(f"Research draft: {live['syntheticResearchSlug']}")
    print(f"Recovery archives: {recovery.parent}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, ValueError, TypeError) as exc:
        print(f"NO-GO: {exc}", file=sys.stderr)
        sys.exit(1)
