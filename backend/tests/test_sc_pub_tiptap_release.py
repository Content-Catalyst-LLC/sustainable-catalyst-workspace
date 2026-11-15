"""SC-PUB-TIPTAP-01 release gate tests: offline, no Docker/SSH/services touched."""
import hashlib
import io
import tarfile
import time
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
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

    def test_failed_recovery_reports_sanitized_child_error(self):
        failed = SimpleNamespace(returncode=1, stdout="",
                                 stderr="internal diagnostic\nNO-GO: Encrypted backup directory already exists\n")
        with (
            patch.dict(os.environ, {
                "SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION": "READ_ONLY_PRODUCTION_TO_OFFHOST"
            }),
            patch.object(release.sys, "argv", ["operator", "recover"]),
            patch.object(release.subprocess, "run", return_value=failed),
        ):
            with self.assertRaisesRegex(
                RuntimeError, "Encrypted backup directory already exists"
            ):
                release.main()

    def test_unstructured_child_error_not_exposed(self):
        failed = SimpleNamespace(returncode=1, stdout="",
                                 stderr="password=SECRET\nTraceback: secret\n")
        with (
            patch.dict(os.environ, {
                "SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION": "READ_ONLY_PRODUCTION_TO_OFFHOST"
            }),
            patch.object(release.sys, "argv", ["operator", "recover"]),
            patch.object(release.subprocess, "run", return_value=failed),
        ):
            with self.assertRaisesRegex(RuntimeError, "without a sanitized diagnostic"):
                release.main()

    @staticmethod
    def synthetic_resume_archive(root):
        root.chmod(0o700)
        db = root / "sc_workspace.dump"
        db.write_bytes(b"PGDMP" + b"x" * 2048)
        data = root / "sc-workspace-data.tgz"
        with tarfile.open(data, "w:gz") as tf:
            payload = b"".join(hashlib.sha256(str(i).encode()).digest() for i in range(256))
            entry = tarfile.TarInfo("example.txt")
            entry.size = len(payload)
            tf.addfile(entry, io.BytesIO(payload))
        return db, data

    def test_resume_existing_archives_preserves_bytes_and_closes_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db, data = self.synthetic_resume_archive(root)
            original = (hashlib.sha256(db.read_bytes()).digest(),
                        hashlib.sha256(data.read_bytes()).digest())
            db.chmod(0o644)
            data.chmod(0o644)
            recovered = recovery.resume_existing_backup(root)
            self.assertEqual(recovered, (db, data))
            self.assertEqual(original,
                (hashlib.sha256(db.read_bytes()).digest(),
                 hashlib.sha256(data.read_bytes()).digest()))
            self.assertEqual(db.stat().st_mode & 0o077, 0)
            self.assertEqual(data.stat().st_mode & 0o077, 0)

    def test_resume_rejects_existing_receipt_and_stale_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db, data = self.synthetic_resume_archive(root)
            receipt = root / "sc-pub-tiptap-recovery.json"
            receipt.write_text('{"outcome":"PASS"}')
            with self.assertRaisesRegex(RuntimeError, "exactly the two"):
                recovery.resume_existing_backup(root)
            receipt.unlink()
            old = time.time() - (27 * 3600)
            os.utime(db, (old, old))
            with self.assertRaisesRegex(RuntimeError, "older than 24 hours"):
                recovery.resume_existing_backup(root)

    def test_resume_rejects_non_postgresql_archive_and_bad_directory_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db, _ = self.synthetic_resume_archive(root)
            root.chmod(0o755)
            with self.assertRaisesRegex(RuntimeError, "unsafe permissions"):
                recovery.resume_existing_backup(root)
            root.chmod(0o700)
            db.write_bytes(b"INVALID" + b"x" * 2048)
            with self.assertRaisesRegex(RuntimeError, "custom-format"):
                recovery.resume_existing_backup(root)

    def test_ssh_errors_identify_stage_without_remote_stderr(self):
        with (
            patch.object(recovery, "run",
                         side_effect=RuntimeError("Command failed (1): ssh -o")),
            patch.object(recovery, "TARGET", "catalystadmin@example.test", create=True),
            patch.object(recovery, "SSH_STAGE", "Restore isolated database")
        ):
            with self.assertRaisesRegex(RuntimeError, "Restore isolated database"):
                recovery.ssh("docker", "exec", "scratch-only")

    def test_resumed_release_refuses_changed_baseline_before_any_restore(self):
        live = {
            "container_id": "a" * 64, "image_ref": "sc-workspace-reporting:prod-old",
            "image_id": "sha256:" + "c" * 64, "running": "true",
        }
        state = {"live_before": {**live, "container_id": "b" * 64}}
        with (
            patch.dict(os.environ, {
                "SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION": "READ_ONLY_PRODUCTION_TO_OFFHOST",
                "SC_PUB_TIPTAP_RECOVERY_RESUME": "VERIFIED_EXISTING_ARCHIVES",
            }),
            patch.object(release.sys, "argv", ["operator", "recover"]),
            patch.object(release, "read_state", return_value=state),
            patch.object(release, "assert_live", return_value=live),
            patch.object(release.subprocess, "run") as child,
        ):
            with self.assertRaisesRegex(RuntimeError, "changed"):
                release.main()
            child.assert_not_called()

    def test_resumed_release_passes_exact_baseline_to_isolated_restore(self):
        live = {
            "container_id": "a" * 64, "image_ref": "sc-workspace-reporting:prod-old",
            "image_id": "sha256:" + "c" * 64, "running": "true",
        }
        with (
            patch.dict(os.environ, {
                "SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION": "READ_ONLY_PRODUCTION_TO_OFFHOST",
                "SC_PUB_TIPTAP_RECOVERY_RESUME": "VERIFIED_EXISTING_ARCHIVES",
            }),
            patch.object(release.sys, "argv", ["operator", "recover"]),
            patch.object(release, "read_state", return_value={"live_before": live}),
            patch.object(release, "assert_live", return_value=live),
            patch.object(release.subprocess, "run",
                         return_value=SimpleNamespace(returncode=0, stdout="", stderr="")) as child,
        ):
            release.main()
            env = child.call_args.kwargs["env"]
            self.assertEqual(env["SC_PUB_TIPTAP_RECOVERY_EXPECTED_LIVE_ID"],
                             live["container_id"])
            self.assertEqual(env["SC_PUB_TIPTAP_RECOVERY_EXPECTED_LIVE_IMAGE"],
                             live["image_ref"])

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
