"""SC-PUB-TIPTAP-01 release gate tests: offline, no Docker/SSH/services touched."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import importlib.util
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]


def imported(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


release = imported("sc_pub_tiptap_release", "sc_pub_tiptap_release.py")
recovery = imported("sc_pub_tiptap_recovery_gate", "sc_pub_tiptap_recovery_gate.py")


class ReleaseGateTests(unittest.TestCase):
    def test_release_targets_merged_tiptap_commit_and_existing_studio_only(self):
        self.assertEqual(release.SOURCE_SHA,
                         "13b9dd34131829a5dc8f2a1ad508d613830315a3")
        self.assertEqual(release.LIVE, "sc-workspace-reporting-live")
        self.assertIn("tiptap-13b9dd341318", release.IMAGE)
        self.assertNotIn("sc-cite01-43be67f", release.IMAGE)
        self.assertEqual(recovery.require_scratch.__name__, "require_scratch")
        with self.assertRaises(RuntimeError):
            recovery.require_scratch("sc-workspace-data")

    def receipt_fixture(self, directory):
        db = directory / "sc_workspace.dump"
        volume = directory / "sc-workspace-data.tgz"
        db.write_bytes(b"offline-fixture-postgres" * 80)
        volume.write_bytes(b"offline-fixture-files" * 80)
        return {
            "schema": "sc-pub-tiptap-recovery/1.0",
            "release": release.RELEASE,
            "outcome": "PASS",
            "createdUtc": datetime.now(timezone.utc).isoformat(),
            "studioImage": "sc-workspace-reporting:prod-old",
            "offhostBackup": True, "databaseRestore": True, "dataVolumeRestore": True,
            "networkIsolated": True, "productionStudioUnchanged": True,
            "originalTables": 5, "restoredTables": 5,
            "archivedFiles": 3, "restoredFiles": 3,
            "dbArchiveSha256": hashlib.sha256(db.read_bytes()).hexdigest(),
            "volumeArchiveSha256": hashlib.sha256(volume.read_bytes()).hexdigest(),
        }

    def test_current_matching_offhost_archives_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = self.receipt_fixture(root)
            (root / "sc-pub-tiptap-recovery.json").write_text(json.dumps(receipt))
            with patch.dict(os.environ, {"SC_PUB_TIPTAP_BACKUP_DIR": temp}):
                release.verify_recovery({"image_ref": "sc-workspace-reporting:prod-old"})

    def test_backup_mismatch_is_nogo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = self.receipt_fixture(root)
            (root / "sc-pub-tiptap-recovery.json").write_text(json.dumps(receipt))
            with patch.dict(os.environ, {"SC_PUB_TIPTAP_BACKUP_DIR": temp}):
                with self.assertRaisesRegex(RuntimeError, "match"):
                    release.verify_recovery({"image_ref": "sc-workspace-reporting:other"})
                (root / "sc_workspace.dump").write_bytes(b"tampered")
                with self.assertRaisesRegex(RuntimeError, "digest mismatch"):
                    release.verify_recovery({"image_ref": "sc-workspace-reporting:prod-old"})

    def test_expired_receipt_is_nogo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = self.receipt_fixture(root)
            receipt["createdUtc"] = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            (root / "sc-pub-tiptap-recovery.json").write_text(json.dumps(receipt))
            with patch.dict(os.environ, {"SC_PUB_TIPTAP_BACKUP_DIR": temp}):
                with self.assertRaisesRegex(RuntimeError, "24 hours"):
                    release.verify_recovery({"image_ref": "sc-workspace-reporting:prod-old"})

    def test_cutover_refuses_if_live_baseline_changed(self):
        baseline = {
            "container_id": "a" * 64, "image_ref": "sc-workspace-reporting:prod-old",
            "image_id": "sha256:" + "c" * 64, "running": "true",
        }
        state = {
            "live_before": {**baseline, "container_id": "b" * 64},
            "candidate_image_id": "sha256:" + "e" * 64,
        }
        with patch.object(release, "read_state", return_value=state), \
             patch.object(release, "assert_live", return_value=baseline), \
             patch.object(release, "ssh") as shell:
            with self.assertRaisesRegex(RuntimeError, "changed"):
                release.deploy()
            shell.assert_not_called()


if __name__ == "__main__":
    unittest.main()
