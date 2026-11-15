#!/usr/bin/env python3
"""SC-PUB-TIPTAP-01 operator-driven off-host backup and isolated restore acceptance.

Run on an off-host machine with SSH access and enough free disk space.
Reads production using pg_dump and a read-only volume mount. Retains backup
files OFF-HOST. Restores into newly created disposable Docker resources on
Contabo with --network none and deletes ONLY those generated resources.

This is not a disaster-recovery drill for every Sustainable Catalyst service.
It validates the Workspace DB archive and the Studio-owned data volume.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from uuid import uuid4


def fail(msg):
    raise RuntimeError(msg)


SSH_STAGE = "Remote recovery initialization"


def resume_existing_backup(dest: Path) -> tuple[Path, Path]:
    """Strictly reuse only the two off-host archives left by this failed gate.

    Never trust a hand-edited PASS receipt or claim this is completed recovery.
    Source authorization, baseline checks, archive verification and isolated
    restores remain mandatory.
    """
    if not dest.is_dir() or dest.is_symlink():
        fail("Resume destination must be an existing non-symlink backup directory")
    if dest.stat().st_mode & 0o077:
        fail("Resume directory has unsafe permissions; require 0700")
    expected = {"sc_workspace.dump", "sc-workspace-data.tgz"}
    found = {p.name for p in dest.iterdir()}
    if found != expected:
        fail("Resume directory must contain exactly the two original backup archives and no receipt")
    dbdump = dest / "sc_workspace.dump"
    archive = dest / "sc-workspace-data.tgz"
    for p in (dbdump, archive):
        if p.is_symlink() or not p.is_file() or p.stat().st_size < 1000:
            fail("Resume archive missing, symlinked or unexpectedly small")
        if not 0 <= time.time() - p.stat().st_mtime < 24 * 3600:
            fail("Retained backup archive is older than 24 hours; start a new recovery")
        os.chmod(p, 0o600)
    with dbdump.open("rb") as stream:
        if stream.read(5) != b"PGDMP":
            fail("Resume PostgreSQL archive is not a valid custom-format dump header")
    verify_tar(archive)
    return dbdump, archive


def run(argv, *, stdin=None, stdout=subprocess.PIPE):
    p = subprocess.run(argv, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE, check=False)
    if p.returncode:
        # Do not include raw process stderr: dump and PostgreSQL details can be sensitive.
        fail(f"Command failed ({p.returncode}): {argv[0]} {argv[1] if len(argv)>1 else ''}")
    return p.stdout.decode().strip() if stdout == subprocess.PIPE else None


def ssh(*args, stdin=None, stdout=subprocess.PIPE):
    try:
        return run(["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                    TARGET, " ".join(shlex.quote(str(arg)) for arg in args)],
                   stdin=stdin, stdout=stdout)
    except RuntimeError as error:
        # Stage is authored here, never from remote output or a potentially
        # secret-bearing command line. Do not expose DB/SSH stderr.
        fail(f"{SSH_STAGE}: {error}")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def remote_psql(container, database):
    sql = ("SELECT count(*) FROM information_schema.tables "
           "WHERE table_schema NOT IN ('pg_catalog','information_schema') "
           "AND table_type='BASE TABLE'")
    result = ssh("docker", "exec", container, "psql", "-U", "postgres",
                 "-d", database, "-tAc", sql)
    try:
        return int(result.strip())
    except ValueError:
        fail("Restored database table-count query did not return an integer")


def verify_tar(path):
    count = 0
    with tarfile.open(path, mode="r:gz") as tf:
        for entry in tf:
            name = PurePosixPath(entry.name)
            if name.is_absolute() or ".." in name.parts:
                fail("Data archive includes unsafe paths")
            if entry.issym() or entry.islnk():
                fail("Data archive contains a link; manual security review required")
            if entry.isfile():
                count += 1
    if count < 1:
        fail("Data volume archive is empty")
    return count


def require_scratch(name):
    if not re.fullmatch(r"sc-pub-tiptap-(restore|files)-[a-f0-9]{12}", name):
        fail("Refusing an operation on a non-scratch Docker resource")


def main():
    global TARGET, SSH_STAGE
    if os.environ.get("SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION") != "READ_ONLY_PRODUCTION_TO_OFFHOST":
        fail("Explicit READ_ONLY_PRODUCTION_TO_OFFHOST authorization required")
    TARGET = os.environ.get("SC_PUB_TIPTAP_SSH_TARGET", "catalystadmin@94.72.113.77")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+", TARGET):
        fail("Unsafe SSH target")
    raw_dest = os.environ.get("SC_PUB_TIPTAP_BACKUP_DIR", "")
    if not raw_dest:
        fail("SC_PUB_TIPTAP_BACKUP_DIR must be an encrypted off-host backup path")
    dest = Path(raw_dest).expanduser()
    resume = os.environ.get("SC_PUB_TIPTAP_RECOVERY_RESUME") == "VERIFIED_EXISTING_ARCHIVES"
    if resume:
        dbdump, archive = resume_existing_backup(dest)
    else:
        if dest.exists():
            fail("SC_PUB_TIPTAP_BACKUP_DIR must be a NEW off-host directory")
        dest.mkdir(mode=0o700, parents=True, exist_ok=False)
        os.chmod(dest, 0o700)
        dbdump = dest / "sc_workspace.dump"
        archive = dest / "sc-workspace-data.tgz"
    receipt = dest / "sc-pub-tiptap-recovery.json"
    suffix = uuid4().hex[:12]
    container = f"sc-pub-tiptap-restore-{suffix}"
    pgvolume = f"sc-pub-tiptap-restore-{suffix}"  # same label, distinct Docker resource type
    datavolume = f"sc-pub-tiptap-files-{suffix}"
    for item in (container, pgvolume, datavolume):
        require_scratch(item)
    started = False
    pgcreated = False
    filescreated = False
    SSH_STAGE = "Inspect live Reporting Studio container"
    live_before = ssh("docker", "inspect", "sc-workspace-reporting-live",
                      "--format", "{{.Id}} {{.Config.Image}}")
    if not live_before or len(live_before.split()) != 2:
        fail("Cannot identify live Reporting Studio image")
    if resume:
        expected_id = os.environ.get("SC_PUB_TIPTAP_RECOVERY_EXPECTED_LIVE_ID")
        expected_image = os.environ.get("SC_PUB_TIPTAP_RECOVERY_EXPECTED_LIVE_IMAGE")
        if not expected_id or not expected_image or live_before.split() != [expected_id, expected_image]:
            fail("Retained archive cannot be tied to the built candidate's current live baseline")
    studioimage = live_before.split()[1]
    if not re.fullmatch(r"[A-Za-z0-9_./:@-]+", studioimage):
        fail("Unexpected live Studio image reference")
    if not studioimage.startswith("sc-workspace-reporting:"):
        fail("This recovery gate is limited to the existing Reporting Studio service")
    SSH_STAGE = "Inspect live production PostgreSQL image"
    pgimage = ssh("docker", "inspect", "sc-postgres", "--format", "{{.Config.Image}}")
    if not re.fullmatch(r"[A-Za-z0-9_./:@-]+", pgimage):
        fail("Cannot safely identify production PostgreSQL image")

    try:
        if resume:
            # No production export is repeated. The original archives remain
            # in place; their hashes are rechecked in the final PASS receipt.
            nfiles = verify_tar(archive)
        else:
            SSH_STAGE = "Export read-only production PostgreSQL backup"
            with dbdump.open("xb") as out:
                ssh("docker", "exec", "sc-postgres", "sh", "-c",
                    "pg_dump -U ${POSTGRES_USER:-postgres} -d sc_workspace -Fc",
                    stdout=out)
            if dbdump.stat().st_size < 1000:
                fail("Workspace dump is unexpectedly small")
            os.chmod(dbdump, 0o600)

            # Export ONLY the named production data volume as read-only.
            SSH_STAGE = "Export read-only production data-volume backup"
            with archive.open("xb") as out:
                ssh("docker", "run", "--rm", "--network", "none",
                    "--mount", "type=volume,src=sc-workspace-data,dst=/data,readonly",
                    "--entrypoint", "tar", studioimage, "czf", "-", "-C", "/data", ".",
                    stdout=out)
            os.chmod(archive, 0o600)
            nfiles = verify_tar(archive)

        # Restore into freshly named, network-disconnected Docker resources.
        SSH_STAGE = "Create isolated PostgreSQL scratch volume"
        ssh("docker", "volume", "create", pgvolume)
        pgcreated = True
        SSH_STAGE = "Create isolated data-volume scratch space"
        ssh("docker", "volume", "create", datavolume)
        filescreated = True
        SSH_STAGE = "Start network-isolated PostgreSQL restore container"
        ssh("docker", "run", "-d", "--name", container, "--network", "none",
            "--mount", f"type=volume,src={pgvolume},dst=/var/lib/postgresql",
            "-e", "PGDATA=/var/lib/postgresql/data",
            "-e", "POSTGRES_HOST_AUTH_METHOD=trust", pgimage)
        started = True
        SSH_STAGE = "Verify PostgreSQL restore container network isolation"
        network_mode = ssh("docker", "inspect", container,
                           "--format", "{{.HostConfig.NetworkMode}}")
        if network_mode != "none":
            fail("Restored PostgreSQL container unexpectedly has network access")
        ready = False
        for _ in range(30):
            p = subprocess.run(["ssh", "-o", "BatchMode=yes", TARGET,
                                "docker", "exec", container, "pg_isready", "-U", "postgres"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if p.returncode == 0:
                ready = True
                break
            import time
            time.sleep(1)
        if not ready:
            fail("Isolated PostgreSQL never became ready")
        SSH_STAGE = "Restore PostgreSQL database from off-host archive"
        # No network connection to the isolated PostgreSQL container: stdin
        # flows into docker exec over SSH and the local Unix socket.
        with dbdump.open("rb") as input_file:
            ssh("docker", "exec", "-i", container, "pg_restore", "-U", "postgres",
                "-d", "postgres", "-C", "--no-owner", "--no-acl",
                stdin=input_file)
        SSH_STAGE = "Count tables in original production PostgreSQL database"
        origin_tables = ssh("docker", "exec", "sc-postgres", "sh", "-c",
            """psql -U ${POSTGRES_USER:-postgres} -d sc_workspace -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') AND table_type='BASE TABLE'" """)
        if not origin_tables.strip().isdigit() or int(origin_tables) < 1:
            fail("Original DB table count invalid")
        SSH_STAGE = "Count tables in isolated restored PostgreSQL database"
        restored_tables = remote_psql(container, "sc_workspace")
        if restored_tables != int(origin_tables):
            fail(f"Table count mismatch: original={origin_tables}, restored={restored_tables}")

        SSH_STAGE = "Restore archived files into isolated data volume"
        # Restore file archive into a separate blank volume using tar's stdin.
        with archive.open("rb") as input_file:
            ssh("docker", "run", "--rm", "-i", "--network", "none",
                "--mount", f"type=volume,src={datavolume},dst=/restore",
                "--entrypoint", "tar", studioimage, "xzf", "-", "-C", "/restore",
                stdin=input_file)
        SSH_STAGE = "Verify isolated restored data-volume file count"
        restored_file_count = ssh("docker", "run", "--rm", "--network", "none",
            "--mount", f"type=volume,src={datavolume},dst=/restore,readonly",
            "--entrypoint", "sh", studioimage, "-c",
            "find /restore -type f | wc -l")
        if not restored_file_count.strip().isdigit() or int(restored_file_count) != nfiles:
            fail("Restored volume file count differs from off-host archive")

        SSH_STAGE = "Confirm production Reporting Studio unchanged by recovery"
        live_after = ssh("docker", "inspect", "sc-workspace-reporting-live",
                         "--format", "{{.Id}} {{.Config.Image}}")
        if live_before != live_after:
            fail("Production Studio changed during recovery acceptance")

        record = {
            "schema": "sc-pub-tiptap-recovery/1.0",
            "release": "sc-pub-tiptap-13b9dd341318",
            "createdUtc": datetime.now(timezone.utc).isoformat(),
            "outcome": "PASS", "offhostBackup": True,
            "databaseRestore": True, "dataVolumeRestore": True,
            "networkIsolated": True, "productionStudioUnchanged": True,
            "dbArchiveSha256": digest(dbdump),
            "volumeArchiveSha256": digest(archive),
            "originalTables": int(origin_tables),
            "restoredTables": restored_tables,
            "archivedFiles": nfiles,
            "restoredFiles": int(restored_file_count),
            "studioImage": studioimage,
            "postgreSQLImage": pgimage,
        }
        fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as out:
            json.dump(record, out, sort_keys=True, indent=2)
            out.write("\n")
        print(f"PASS: off-host backup and isolated restores; receipt: {receipt}")
        return 0
    finally:
        # Only scratch resources created above; never prune, stop, or rename production.
        if started:
            SSH_STAGE = "Remove temporary restored PostgreSQL container"
            ssh("docker", "rm", "-f", container)
        if pgcreated:
            SSH_STAGE = "Remove temporary PostgreSQL restore volume"
            ssh("docker", "volume", "rm", pgvolume)
        if filescreated:
            SSH_STAGE = "Remove temporary data restore volume"
            ssh("docker", "volume", "rm", datavolume)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"NO-GO: {exc}", file=sys.stderr)
        sys.exit(1)
