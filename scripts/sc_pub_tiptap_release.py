#!/usr/bin/env python3
"""SC-PUB-TIPTAP-01: guarded Reporting Studio production operator.

Run on an SSH-capable off-host Mac checkout. Does not change Research, WordPress,
authentication policies, production databases or unrelated Docker resources.

--status: read-only
--build: archive the exact reviewed source SHA, build one candidate image on
         the existing Contabo host, test its local Tiptap bundle (no cutover)
--recover: run the existing-style independent off-host backup + isolated restore
--deploy: require verified off-host recovery, baseline match and explicit TTY
          confirmation; invoke the existing reviewed studio.sh cutover/rollback.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

SOURCE_SHA = "13b9dd34131829a5dc8f2a1ad508d613830315a3"
SHORT = SOURCE_SHA[:12]
IMAGE = f"sc-workspace-reporting:tiptap-{SHORT}"
LIVE = "sc-workspace-reporting-live"
RELEASE = "sc-pub-tiptap-" + SHORT
ROOT = Path(__file__).resolve().parent.parent
STATE = Path.home() / ".sc-pub-tiptap" / f"{RELEASE}.json"
TARGET = os.environ.get("SC_PUB_TIPTAP_SSH_TARGET", "catalystadmin@94.72.113.77")
HEALTH = "http://127.0.0.1:20080/health"
PROBE = "http://127.0.0.1:20080/v1/private-research/reporting-studio/publication/editor.bundle.js"
LEGACY_PROBE = "http://127.0.0.1:20080/v1/private-research/reporting-studio/publication"


def fail(message):
    raise RuntimeError("NO-GO: " + message)


def execute(argv, *, input_stream=None, timeout=45):
    p = subprocess.run(argv, stdin=input_stream, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=input_stream is None,
                       timeout=timeout, check=False)
    if p.returncode:
        # Never dump raw SSH/container output that may contain sensitive data.
        fail(f"Command failed ({p.returncode}): {argv[0]}")
    return p.stdout.strip() if isinstance(p.stdout, str) else p.stdout


def ssh(command, *, timeout=45):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+", TARGET):
        fail("Invalid SSH target")
    argv = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
            "-o", "ConnectTimeout=8", TARGET, "bash -lc " + shlex.quote(command)]
    return execute(argv, timeout=timeout)


def quoted(*words):
    return " ".join(shlex.quote(str(w)) for w in words)


def docker_inspect(item, is_image=False):
    if is_image:
        value = ssh(quoted("docker", "image", "inspect", item, "--format",
                           "{{.Id}}|{{index .Config.Labels \"org.opencontainers.image.revision\"}}"))
        cols = value.split("|")
        if len(cols) != 2 or not cols[0].startswith("sha256:"):
            fail("Candidate image digest/label unavailable")
        return {"image_id": cols[0], "source_sha": cols[1]}
    value = ssh(quoted("docker", "inspect", item, "--format",
                       "{{.Id}}|{{.Config.Image}}|{{.Image}}|{{.State.Running}}"))
    cols = value.split("|")
    if len(cols) != 4 or not cols[0].startswith("sha256:") and len(cols[0]) < 20:
        fail("Cannot identify live Reporting Studio")
    return dict(zip(("container_id", "image_ref", "image_id", "running"), cols))


def assert_live():
    info = docker_inspect(LIVE)
    if info["running"] != "true" or not info["image_ref"].startswith("sc-workspace-reporting:"):
        fail("Live Studio not running as expected")
    code = ssh(quoted("curl", "-sS", "-o", "/dev/null",
                      "-w", "%{http_code}", "--max-time", "8", HEALTH))
    if code != "200":
        fail("Existing Studio health endpoint did not return 200")
    if ssh("test -f \"$HOME/sc-sci02/rd/studio.sh\" && "
           "test ! -L \"$HOME/sc-sci02/rd/studio.sh\" && echo present") != "present":
        fail("Existing protected studio.sh cutover/rollback missing")
    return info


def read_state():
    if not STATE.is_file() or STATE.stat().st_mode & 0o077:
        fail("Missing or insecure candidate state: run --build first")
    state = json.loads(STATE.read_text())
    if state.get("schema") != "sc-pub-tiptap-operator-state/1.0" or state.get("source_sha") != SOURCE_SHA:
        fail("Candidate state belongs to a different source release")
    return state


def verify_source():
    sha = execute(["git", "-C", str(ROOT), "cat-file", "-t", SOURCE_SHA])
    if sha != "commit":
        fail("Reviewed source commit missing from this local Git checkout")
    try:
        execute(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", SOURCE_SHA, "HEAD"])
    except RuntimeError:
        fail("Release checkout does not descend from the reviewed source commit")


def capacity():
    free_kb = ssh("df -Pk \"$HOME\" | awk 'END {print $4}'")
    mem_kb = ssh("awk '/^MemAvailable:/ {print $2}' /proc/meminfo")
    if not free_kb.isdecimal() or int(free_kb) < 12 * 1024 * 1024:
        fail("Insufficient free disk for isolated candidate build (12GiB reserve)")
    if not mem_kb.isdecimal() or int(mem_kb) < 1536 * 1024:
        fail("Insufficient available memory for candidate build (1.5GiB reserve)")


def build():
    verify_source()
    live = assert_live()
    capacity()
    exists = ssh('docker image inspect ' + shlex.quote(IMAGE) +
                 ' >/dev/null 2>&1 && echo yes || echo no')
    if exists != 'no':
        fail("Candidate image tag already exists: refusing to overwrite an immutable release candidate")
    remote_dir = f"$HOME/sc-pub-tiptap-{SHORT}"
    command = (f'umask 077; mkdir -m 700 -p "{remote_dir}"; '
               f'test ! -e "{remote_dir}/backend" || exit 42; '
               f'tar -xf - -C "{remote_dir}"')
    archive = subprocess.Popen(["git", "-C", str(ROOT), "archive", "--format=tar",
                                SOURCE_SHA, "backend"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    try:
        args = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                "-o", "ConnectTimeout=8", TARGET, "bash -lc " + shlex.quote(command)]
        upload = subprocess.run(args, stdin=archive.stdout, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=240, check=False)
    finally:
        if archive.stdout:
            archive.stdout.close()
    if archive.wait() or upload.returncode:
        fail("Exact-source archive transfer failed; inspect the release-scoped remote staging directory")
    build_command = (f'cd "{remote_dir}/backend" && '
                     + quoted("docker", "build", "--pull=false",
                              "--label", "org.opencontainers.image.revision=" + SOURCE_SHA,
                              "-t", IMAGE, "-f", "Dockerfile.reporting", "."))
    print("Building exact reviewed source image on Contabo; no live replacement.")
    ssh(build_command, timeout=2100)
    image = docker_inspect(IMAGE, True)
    if image["source_sha"] != SOURCE_SHA:
        fail("Candidate image not labeled with the reviewed source SHA")
    test = ("test -s /app/app/reporting_publication_tiptap.bundle.js && "
            "python -m py_compile /app/app/reporting_publication.py")
    ssh(quoted("docker", "run", "--rm", "--network", "none", "--memory", "512m",
               "--entrypoint", "sh", IMAGE, "-c", test), timeout=90)
    STATE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(STATE.parent, 0o700)
    record = {
        "schema": "sc-pub-tiptap-operator-state/1.0",
        "createdUtc": datetime.now(timezone.utc).isoformat(),
        "source_sha": SOURCE_SHA,
        "candidate": IMAGE,
        "candidate_image_id": image["image_id"],
        "live_before": live,
    }
    fd = os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as out:
        json.dump(record, out, indent=2, sort_keys=True)
        out.write("\n")
    print(f"CANDIDATE READY | image={IMAGE} | digest={image['image_id']}")
    print(f"Baseline state stored privately at {STATE}")


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def verify_recovery(live):
    dir_value = os.environ.get("SC_PUB_TIPTAP_BACKUP_DIR", "")
    if not dir_value:
        fail("SC_PUB_TIPTAP_BACKUP_DIR (encrypted off-host backup directory) required")
    directory = Path(dir_value).expanduser().resolve()
    receipt_path = directory / "sc-pub-tiptap-recovery.json"
    if not receipt_path.is_file():
        fail("Independent off-host restore receipt missing; run --recover before deployment")
    receipt = json.loads(receipt_path.read_text())
    if (receipt.get("schema"), receipt.get("release"), receipt.get("outcome")) != (
        "sc-pub-tiptap-recovery/1.0", RELEASE, "PASS"
    ):
        fail("Recovery acceptance does not match this exact release")
    created = datetime.fromisoformat(receipt["createdUtc"])
    if created.tzinfo is None or not timedelta(0) <= (
        datetime.now(timezone.utc) - created.astimezone(timezone.utc)
    ) <= timedelta(hours=24):
        fail("Off-host recovery acceptance is not current within 24 hours")
    if receipt.get("studioImage") != live["image_ref"]:
        fail("Backup receipt does not match the current live Reporting Studio image")
    for key in ("offhostBackup", "databaseRestore", "dataVolumeRestore",
                "networkIsolated", "productionStudioUnchanged"):
        if receipt.get(key) is not True:
            fail("Off-host recovery evidence incomplete: " + key)
    for expected, restored in (("originalTables", "restoredTables"),
                               ("archivedFiles", "restoredFiles")):
        if (not isinstance(receipt.get(expected), int)
                or receipt[expected] < 1 or receipt[expected] != receipt.get(restored)):
            fail("Off-host restore inventory mismatch: " + expected)
    for filename, key in (("sc_workspace.dump", "dbArchiveSha256"),
                          ("sc-workspace-data.tgz", "volumeArchiveSha256")):
        path = directory / filename
        if not path.is_file() or digest(path) != receipt.get(key):
            fail("Off-host archive missing or digest mismatch: " + filename)
    print("PASS: fresh off-host PostgreSQL and data-volume restore receipts and archive hashes")


def check_probe(*, after_cutover=False):
    # Before cutover the old Studio image does not have editor.bundle.js,
    # so check the existing private Studio UI rather than requiring a new route.
    url = PROBE if after_cutover else LEGACY_PROBE
    code = ssh(quoted("curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                      "--max-time", "8", url))
    if code not in ("401", "403"):
        fail("Anonymous Studio access not denied as expected (HTTP " + code + ")")


def rollback(reason):
    print("Cutover verification failed; invoking the existing protected rollback.", file=sys.stderr)
    try:
        ssh('bash "$HOME/sc-sci02/rd/studio.sh" rollback', timeout=180)
    except Exception:
        fail("URGENT: automatic rollback unsuccessful; inspect production manually")
    fail("Rolled back after post-cutover validation failure: " + reason)


def deploy():
    state = read_state()
    live = assert_live()
    if live != state.get("live_before"):
        fail("Live Studio has changed since candidate build; refresh baseline")
    candidate = docker_inspect(IMAGE, True)
    if candidate["source_sha"] != SOURCE_SHA or candidate["image_id"] != state["candidate_image_id"]:
        fail("Candidate image no longer matches pinned build")
    verify_recovery(live)
    check_probe()
    if not sys.stdin.isatty():
        fail("Production deployment requires a real interactive operator terminal")
    print(f"READY FOR STUDIO CUTOVER | {LIVE}: {live['image_ref']} -> {IMAGE}")
    answer = input("Type DEPLOY SC-PUB-TIPTAP-01: ")
    if answer != "DEPLOY SC-PUB-TIPTAP-01":
        fail("Operator declined cutover")
    if assert_live() != live or docker_inspect(IMAGE, True) != candidate:
        fail("Image or live baseline changed immediately before cutover")
    try:
        ssh('bash "$HOME/sc-sci02/rd/studio.sh" cutover ' + shlex.quote(IMAGE), timeout=360)
    except Exception:
        fail("Protected cutover failed; inspect existing studio.sh rollback outcome")
    try:
        updated = assert_live()
        if updated["image_ref"] != IMAGE or updated["image_id"] != candidate["image_id"]:
            fail("Live container is not using the approved Tiptap image digest")
        check_probe(after_cutover=True)
        present = ssh(quoted("docker", "exec", LIVE, "sh", "-c",
                             "test -s /app/app/reporting_publication_tiptap.bundle.js && echo present"))
        if present != "present":
            fail("Published Reporting Studio image lacks the self-hosted Tiptap bundle")
    except Exception as error:
        rollback(str(error))
    print("DEPLOYED: Reporting Studio uses reviewed Tiptap image, HTTP 200 health, protected bundle.")
    print("Note: authenticated real-owner editor/export acceptance remains separate from public Research release.")


def manual_rollback():
    # Deliberately limited to the image produced by this precise release.
    current = assert_live()
    if current["image_ref"] != IMAGE:
        fail("Manual rollback refused: live Studio is not this Tiptap release image")
    if not sys.stdin.isatty():
        fail("Rollback requires an interactive operator")
    answer = input("Type ROLLBACK SC-PUB-TIPTAP-01: ")
    if answer != "ROLLBACK SC-PUB-TIPTAP-01":
        fail("Operator declined rollback")
    if assert_live() != current:
        fail("Live Studio changed before rollback")
    ssh('bash "$HOME/sc-sci02/rd/studio.sh" rollback', timeout=180)
    restored = assert_live()
    if restored["image_ref"] == IMAGE:
        fail("Rollback did not restore the previous Reporting Studio image")
    print("ROLLED BACK: previous Reporting Studio image restored and health checked")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("status", "build", "recover", "deploy", "rollback"))
    mode = p.parse_args().mode
    if mode == "status":
        info = assert_live()
        print(f"LIVE: {info['image_ref']} | image_id={info['image_id']}")
        check_probe()
        print("PASS: health and anonymous editor access denial")
    elif mode == "build":
        build()
    elif mode == "recover":
        if os.environ.get("SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION") != "READ_ONLY_PRODUCTION_TO_OFFHOST":
            fail("Set SC_PUB_TIPTAP_RECOVERY_AUTHORIZATION=READ_ONLY_PRODUCTION_TO_OFFHOST")
        execute(["python3", str(ROOT / "scripts" / "sc_pub_tiptap_recovery_gate.py")],
                timeout=1800)
        print("PASS: independent off-host backup and restore performed")
    elif mode == "deploy":
        deploy()
    elif mode == "rollback":
        manual_rollback()


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        print(str(exc) if str(exc).startswith("NO-GO:") else "NO-GO: " + str(exc),
              file=sys.stderr)
        sys.exit(1)
