#!/usr/bin/env python3
"""SC-SCI-02: vendor the Lab Graph Studio renderer into the Notebook Desk.

Workspace has no figure renderer of its own. The desk serves byte-identical copies of the Lab
sc.figure-bundle.v1 renderer, its FIG-02A policy and FIG-02B Vega-Lite modules, and the pinned Vega
libraries, taken from one Lab commit (the same approach as Research's sync_figure_renderer.py). The lock
records each file's SHA-256 and Subresource Integrity value; the page loads them with integrity
attributes, so the browser refuses any file whose bytes differ.

    python3 scripts/sync_graph_studio_renderer.py --lab <Lab checkout> --rev <Lab commit>   # copy + lock
    python3 scripts/sync_graph_studio_renderer.py --check                                    # verify only

Files are read with `git show <rev>:<path>`, so a dirty Lab working tree is never vendored.
"""
import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESK = ROOT / "backend" / "app" / "static" / "notebook_desk"
VENDOR = DESK / "graph-studio"
LOCK = VENDOR / "RENDERER_LOCK.json"
PAGE = DESK / "index.html"
LOCK_SCHEMA = "sc-workspace-graph-studio-lock/1.0"
URL_PREFIX = "/v1/desk/notebook-assets/graph-studio/"

# Load order: libraries, FIG-02A policy, FIG-02B Vega-Lite module, then the generic renderer.
SCRIPTS = (
    ("vega", "assets/lib/vega-6.4.0/vega.min.js"),
    ("vega-lite", "assets/lib/vega-lite-6.5.0/vega-lite.min.js"),
    ("vega-interpreter", "assets/lib/vega-interpreter-2.3.2/vega-interpreter.classic.js"),
    ("fig02a-policy", "assets/js/modules/graph-studio-plotly-preview-fig02a.js"),
    ("fig02b-vega-lite", "assets/js/modules/graph-studio-vega-lite-fig02b.js"),
    ("renderer", "assets/js/modules/graph-studio-figure-bundle-renderer.js"),
)
STYLES = (
    ("fig02a-style", "assets/css/sc-lab-graph-studio-plotly-preview-fig02a.css"),
    ("renderer-style", "assets/css/sc-lab-graph-studio-figure-bundle-renderer.css"),
)
LICENSES = (
    "assets/lib/vega-6.4.0/LICENSE", "assets/lib/vega-6.4.0/SOURCE.json",
    "assets/lib/vega-lite-6.5.0/LICENSE", "assets/lib/vega-lite-6.5.0/SOURCE.json",
    "assets/lib/vega-interpreter-2.3.2/LICENSE", "assets/lib/vega-interpreter-2.3.2/SOURCE.json",
)
BEGIN, END = "<!-- BEGIN GRAPH STUDIO LOCK (scripts/sync_graph_studio_renderer.py) -->", "<!-- END GRAPH STUDIO LOCK -->"


def sri(data: bytes) -> str:
    return "sha384-" + base64.b64encode(hashlib.sha384(data).digest()).decode()


def target(path: str) -> str:
    return path.removeprefix("assets/")


def show(lab: Path, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(lab), "show", f"{rev}:{path}"], check=True, capture_output=True).stdout


def page_block(lock: dict) -> str:
    lines = [BEGIN]
    for f in lock["files"]:
        url = URL_PREFIX + f["path"]
        if f["kind"] == "style":
            lines.append(f'  <link rel="stylesheet" href="{url}" integrity="{f["integrity"]}">')
        elif f["kind"] == "script":
            lines.append(f'  <script defer src="{url}" integrity="{f["integrity"]}"></script>')
    lines.append("  " + END)
    return "\n".join(lines)


def with_block(page: str, block: str) -> str:
    start, end = page.index(BEGIN), page.index(END) + len(END)
    return page[:start] + block + page[end:]


def sync(lab: Path, rev: str) -> None:
    commit = subprocess.run(["git", "-C", str(lab), "rev-parse", rev], check=True, capture_output=True, text=True).stdout.strip()
    header = show(lab, commit, "sustainable-catalyst-lab.php").decode()
    version = (re.search(r"^\s*\*\s*Version:\s*(\S+)", header, re.M) or [None, "unknown"])[1]
    files = []
    for kind, items in (("script", SCRIPTS), ("style", STYLES), ("license", tuple((None, p) for p in LICENSES))):
        for role, path in items:
            data = show(lab, commit, path)
            out = VENDOR / target(path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            entry = {"kind": kind, "path": target(path), "labPath": path, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            if role:
                entry = {"role": role, **entry, "integrity": sri(data)}
            files.append(entry)
    lock = {"schema": LOCK_SCHEMA, "labRepository": "Content-Catalyst-LLC/sustainable-catalyst-lab", "labCommit": commit,
            "labRelease": version, "note": "Byte-identical copies of the Lab Graph Studio renderer; update only with this script.",
            "files": files}
    LOCK.write_text(json.dumps(lock, indent=1) + "\n")
    PAGE.write_text(with_block(PAGE.read_text(), page_block(lock)))
    print(f"vendored Lab {version} ({commit[:12]}): {len(files)} files")


def check() -> list[str]:
    lock = json.loads(LOCK.read_text())
    errors = []
    if lock.get("schema") != LOCK_SCHEMA:
        errors.append("lock schema")
    for f in lock["files"]:
        p = VENDOR / f["path"]
        data = p.read_bytes() if p.is_file() else b""
        if hashlib.sha256(data).hexdigest() != f["sha256"] or len(data) != f["bytes"]:
            errors.append(f"{f['path']}: bytes differ from the lock")
        if "integrity" in f and sri(data) != f["integrity"]:
            errors.append(f"{f['path']}: integrity differs from the lock")
    if page_block(lock) not in PAGE.read_text():
        errors.append("index.html script and style tags differ from the lock")
    listed = {f["path"] for f in lock["files"]} | {LOCK.name}
    extra = sorted(str(p.relative_to(VENDOR)) for p in VENDOR.rglob("*") if p.is_file() and str(p.relative_to(VENDOR)) not in listed)
    if extra:
        errors.append(f"unlisted files in graph-studio/: {extra}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", type=Path)
    ap.add_argument("--rev")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if not args.check:
        if not args.lab or not args.rev:
            ap.error("--lab and --rev are required to sync")
        sync(args.lab, args.rev)
    errors = check()
    for e in errors:
        print("FAIL", e)
    if not errors:
        print("renderer lock OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
