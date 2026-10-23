"""Paired Workspace PostgreSQL/object backup and isolated restore tooling.

Capture requires quiesced writers: pg_dump and an object copy are not an atomic
cross-store transaction. This tool deliberately never starts/stops services.
"""

import argparse
import hashlib
import json
import os
import subprocess
import tarfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


SCHEMA = "sc-workspace-paired-backup/1.0"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def pg_env(database_url: str) -> tuple[dict[str, str], str, str]:
    parsed = urlsplit(database_url.replace("postgresql+psycopg://", "postgresql://", 1))
    if parsed.scheme != "postgresql" or not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("A PostgreSQL URL with host and database is required")
    env = os.environ.copy()
    env.update(PGHOST=parsed.hostname, PGPORT=str(parsed.port or 5432),
               PGUSER=unquote(parsed.username or ""), PGDATABASE=unquote(parsed.path[1:]))
    if parsed.password is not None:
        env["PGPASSWORD"] = unquote(parsed.password)
    return env, parsed.hostname, unquote(parsed.path[1:])


def pg_dump_to(path: Path, env: dict[str, str], database: str) -> None:
    container = env.get("SC_WXR_PG_CONTAINER")
    if container:
        with path.open("wb") as output:
            subprocess.run(["docker", "exec", container, "pg_dump", "-U", env["PGUSER"],
                            "-d", database, "-Fc"], stdout=output, check=True)
    else:
        subprocess.run(["pg_dump", "-Fc", "-f", str(path)], env=env, check=True)


def pg_restore_from(path: Path, env: dict[str, str], database: str | None) -> None:
    container = env.get("SC_WXR_PG_CONTAINER")
    if container:
        command = ["docker", "exec", "-i", container, "pg_restore"]
        if database is None:
            command += ["--list"]
        else:
            command += ["-U", env["PGUSER"], "--exit-on-error", "--no-owner",
                        "--no-privileges", "-d", database]
        with path.open("rb") as source:
            subprocess.run(command, stdin=source, check=True,
                           stdout=subprocess.DEVNULL if database is None else None)
    else:
        command = ["pg_restore", "--list", str(path)] if database is None else [
            "pg_restore", "--exit-on-error", "--no-owner", "--no-privileges",
            "-d", database, str(path)]
        subprocess.run(command, env=env, check=True,
                       stdout=subprocess.DEVNULL if database is None else None)


def object_files(root: Path):
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Object root must be an existing directory, not a symlink")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlink in object root is unsupported")
        if path.is_file():
            yield path, path.relative_to(root).as_posix()
        elif not path.is_dir():
            raise ValueError("Unsupported object-root entry")


def capture(database_url: str, object_root: Path, destination: Path, quiesced: bool) -> dict:
    if not quiesced:
        raise ValueError("Capture requires documented writer quiescence")
    env, host, database = pg_env(database_url)
    if destination.exists():
        raise FileExistsError("Backup destination must not exist")
    destination.mkdir(mode=0o700, parents=True)
    dump = destination / "database.dump"
    archive = destination / "objects.tar.gz"
    entries = []
    try:
        pg_dump_to(dump, env, database)
        with tarfile.open(archive, "w:gz") as bundle:
            for path, relative in object_files(object_root):
                item = {"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)}
                entries.append(item)
                info = tarfile.TarInfo(relative)
                info.size = item["bytes"]
                info.mode = 0o600
                with path.open("rb") as source:
                    bundle.addfile(info, source)
                if digest(path) != item["sha256"]:
                    raise RuntimeError("Object changed while backup was being captured")
        manifest = {"schema": SCHEMA, "database_name": database,
                    "database_host": host, "quiescence_confirmed": True,
                    "database_dump": {"bytes": dump.stat().st_size, "sha256": digest(dump)},
                    "object_archive": {"bytes": archive.stat().st_size, "sha256": digest(archive)},
                    "objects": entries}
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        os.chmod(destination / "manifest.json", 0o600)
        return manifest
    except BaseException:
        for path in (dump, archive, destination / "manifest.json"):
            path.unlink(missing_ok=True)
        destination.rmdir()
        raise


def verify(source: Path) -> dict:
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("schema") != SCHEMA:
        raise ValueError("Unsupported backup manifest")
    for name, key in (("database.dump", "database_dump"), ("objects.tar.gz", "object_archive")):
        path = source / name
        if path.stat().st_size != manifest[key]["bytes"] or digest(path) != manifest[key]["sha256"]:
            raise ValueError(f"Backup component failed SHA-256 verification: {name}")
    pg_restore_from(source / "database.dump", os.environ.copy(), None)
    expected = {item["path"]: item for item in manifest["objects"]}
    if len(expected) != len(manifest["objects"]):
        raise ValueError("Duplicate object paths in backup manifest")
    seen = set()
    with tarfile.open(source / "objects.tar.gz", "r:gz") as bundle:
        for member in bundle:
            path = Path(member.name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts or member.name in seen:
                raise ValueError("Unsafe or duplicate object archive entry")
            expected_item = expected.get(member.name)
            if expected_item is None or member.size != expected_item["bytes"]:
                raise ValueError("Object archive and manifest disagree")
            stream = bundle.extractfile(member)
            if stream is None:
                raise ValueError("Unreadable object archive entry")
            value = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                value.update(chunk)
            if value.hexdigest() != expected_item["sha256"]:
                raise ValueError("Object failed SHA-256 verification")
            seen.add(member.name)
    if seen != set(expected):
        raise ValueError("Object archive is incomplete")
    return manifest


def restore(source: Path, database_url: str, object_destination: Path) -> dict:
    manifest = verify(source)
    env, host, database = pg_env(database_url)
    if host not in {"localhost", "127.0.0.1", "::1"} or not database.startswith("sc_wxr094_restore"):
        raise ValueError("Restore is restricted to a local sc_wxr094_restore* database")
    if object_destination.exists():
        raise FileExistsError("Restore object destination must not exist")
    object_destination.mkdir(mode=0o700, parents=True)
    try:
        pg_restore_from(source / "database.dump", env, database)
        with tarfile.open(source / "objects.tar.gz", "r:gz") as bundle:
            for member in bundle:
                target = object_destination / member.name
                target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                stream = bundle.extractfile(member)
                if stream is None:
                    raise ValueError("Unreadable object archive entry")
                with target.open("xb") as output:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        output.write(chunk)
        for item in manifest["objects"]:
            if digest(object_destination / item["path"]) != item["sha256"]:
                raise ValueError("Restored object failed SHA-256 verification")
    except BaseException:
        # Keep partial restore for diagnosis; never delete database contents here.
        raise
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    backup = commands.add_parser("capture")
    backup.add_argument("--object-root", type=Path, required=True)
    backup.add_argument("--destination", type=Path, required=True)
    backup.add_argument("--confirm-writes-quiesced", action="store_true")
    check = commands.add_parser("verify")
    check.add_argument("--source", type=Path, required=True)
    recovery = commands.add_parser("restore")
    recovery.add_argument("--source", type=Path, required=True)
    recovery.add_argument("--object-destination", type=Path, required=True)
    args = parser.parse_args()
    database_url = os.environ.get("SC_WXR_RELEASE_DATABASE_URL", "")
    if args.action == "capture":
        result = capture(database_url, args.object_root, args.destination,
                         args.confirm_writes_quiesced)
    elif args.action == "verify":
        result = verify(args.source)
    else:
        result = restore(args.source, database_url, args.object_destination)
    print(json.dumps({"schema": result["schema"], "database_name": result["database_name"],
                      "object_count": len(result["objects"]), "verified": True}))


if __name__ == "__main__":
    main()
