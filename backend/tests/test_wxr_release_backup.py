"""Synthetic backup/restore safety checks; no production or external data."""

import subprocess
from pathlib import Path

import pytest

from tools import wxr_release_backup as backup


URL = "postgresql+psycopg://synthetic:synthetic@127.0.0.1/sc_wxr094_synthetic"
RESTORE_URL = "postgresql+psycopg://synthetic:synthetic@127.0.0.1/sc_wxr094_restore_test"


def test_paired_capture_verify_restore_and_tamper_detection(tmp_path, monkeypatch):
    calls = []

    def fake_pg(args, **kwargs):
        calls.append(args[0])
        if args[0] == "pg_dump":
            Path(args[args.index("-f") + 1]).write_bytes(b"synthetic-pg18-dump")
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(backup.subprocess, "run", fake_pg)
    objects = tmp_path / "objects"
    (objects / "a").mkdir(parents=True)
    (objects / "a" / "hash").write_bytes(b"synthetic research object")
    destination = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="quiescence"):
        backup.capture(URL, objects, destination, False)
    assert not destination.exists()
    captured = backup.capture(URL, objects, destination, True)
    assert captured["objects"][0]["sha256"] == backup.digest(objects / "a" / "hash")
    assert backup.verify(destination) == captured
    with pytest.raises(ValueError, match="restricted"):
        backup.restore(destination, URL, tmp_path / "forbidden")
    restored = tmp_path / "restored"
    backup.restore(destination, RESTORE_URL, restored)
    assert (restored / "a" / "hash").read_bytes() == b"synthetic research object"
    assert calls == ["pg_dump", "pg_restore", "pg_restore", "pg_restore", "pg_restore"]
    (destination / "objects.tar.gz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="SHA-256"):
        backup.verify(destination)


def test_symlink_and_existing_destination_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(backup.subprocess, "run", lambda args, **kw: (
        Path(args[args.index("-f") + 1]).write_bytes(b"synthetic")
        if args[0] == "pg_dump" else None
    ))
    objects = tmp_path / "objects"
    objects.mkdir()
    (objects / "link").symlink_to(tmp_path / "elsewhere")
    with pytest.raises(ValueError, match="Symlink"):
        backup.capture(URL, objects, tmp_path / "snapshot", True)
    assert not (tmp_path / "snapshot").exists()
    (tmp_path / "snapshot").mkdir()
    with pytest.raises(FileExistsError):
        backup.capture(URL, objects, tmp_path / "snapshot", True)
