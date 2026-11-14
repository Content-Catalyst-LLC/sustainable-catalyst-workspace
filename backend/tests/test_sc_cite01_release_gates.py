"""SC-CITE-01 release tooling tests; no production calls and no old 28-test rerun."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
REQUIRED = [
    "anonymous_workspace_denied", "cross_owner_workspace_denied",
    "owner_source_import", "verified_library_import", "harvard_bibliography",
    "snapshot_replay", "research_editorial_revision_persisted",
    "research_revision_replay", "research_cross_owner_denied",
]


def check(root, env):
    return subprocess.run([sys.executable, str(SCRIPTS / "sc_cite01_verify_receipts.py")],
                          env={**os.environ, **env}, capture_output=True, text=True)


def test_gates_refuse_missing_receipts(tmp_path):
    result = check(tmp_path, {
        "SC_CITE01_INTEGRATION_RECEIPT": str(tmp_path / "missing-integration.json"),
        "SC_CITE01_RECOVERY_RECEIPT": str(tmp_path / "missing-recovery.json"),
    })
    assert result.returncode != 0 and "NO-GO" in result.stderr


def test_gates_require_real_checks_and_verified_archives(tmp_path):
    now = datetime.now(timezone.utc).isoformat()
    i = {"schema": "sc-cite01-live-integration/1.0", "release": "sc-cite01-43be67f",
         "createdUtc": now, "outcome": "PASS", "checks": REQUIRED,
         "syntheticProjectId": "synthetic-wexford",
         "syntheticResearchSlug": "synthetic-cite01-example",
         "researchDocumentSha256": "1" * 64, "bibliographySha256": "2" * 64}
    r = {"schema": "sc-cite01-recovery/1.0", "release": "sc-cite01-43be67f",
         "createdUtc": now, "outcome": "PASS",
         "offhostBackup": True, "databaseRestore": True, "dataVolumeRestore": True,
         "networkIsolated": True, "productionStudioUnchanged": True,
         "originalTables": 3, "restoredTables": 3,
         "archivedFiles": 2, "restoredFiles": 2}
    for name, key in (("sc_workspace.dump", "dbArchiveSha256"),
                      ("sc-workspace-data.tgz", "volumeArchiveSha256")):
        data = f"synthetic {name}".encode()
        (tmp_path / name).write_bytes(data)
        r[key] = hashlib.sha256(data).hexdigest()
    ipath, rpath = tmp_path / "integration.json", tmp_path / "sc-cite01-recovery.json"
    ipath.write_text(json.dumps(i))
    rpath.write_text(json.dumps(r))
    env = {"SC_CITE01_INTEGRATION_RECEIPT": str(ipath),
           "SC_CITE01_RECOVERY_RECEIPT": str(rpath)}
    assert check(tmp_path, env).returncode == 0
    i["checks"] = REQUIRED[:-1]
    ipath.write_text(json.dumps(i))
    assert check(tmp_path, env).returncode != 0
    i["checks"] = REQUIRED
    ipath.write_text(json.dumps(i))
    (tmp_path / "sc_workspace.dump").write_bytes(b"tampered")
    assert check(tmp_path, env).returncode != 0


def test_python_and_bash_release_scripts_parse():
    for name in ("sc_cite01_integration_gate.py", "sc_cite01_recovery_gate.py",
                 "sc_cite01_verify_receipts.py"):
        source = (SCRIPTS / name).read_text()
        compile(source, str(SCRIPTS / name), "exec")
    for name in ("sc_cite01_release.sh", "sc_cite01_operator.sh"):
        out = subprocess.run(["bash", "-n", str(SCRIPTS / name)],
                             capture_output=True)
        assert out.returncode == 0, out.stderr.decode()
