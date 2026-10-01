#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
import argparse
import contextlib
import functools
import hashlib
import json
import socket
import threading
import time


VERSION = "3.48.0"
MANIFEST_SCHEMA = "sc-workspace-runtime-asset-manifest/1.0"
REPORT_SCHEMA = "sc-workspace-standalone-production-certification-report/1.0"
FORBIDDEN_COUPLING = (
    "wp-content",
    "wp-json",
    "wp-admin",
    "sc-workspace-wordpress-host-adapter",
    "sc-workspace-wordpress-transport-adapter",
    "sc-workspace-wordpress-auth-adapter",
    "sc-workspace-wordpress-thin-adapter",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(name: str, ok: bool, detail: str = "") -> dict:
    if ok:
        print(f"{name}=PASS")
    else:
        print(f"{name}=FAIL" + (f" :: {detail}" if detail else ""))
    return {"name": name, "ok": bool(ok), "detail": str(detail or "")}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


@contextlib.contextmanager
def local_server(root: Path):
    handler = functools.partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Sustainable-Catalyst-Workspace-Certification/3.48.0"})
    with urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read()


def certify(root: Path, backend_url: str = "") -> dict:
    root = root.resolve()
    gates = []

    manifest_path = root / "asset-manifest-v3480.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    gates.append(emit(
        "WORKSPACE_STANDALONE_CERT_MANIFEST",
        manifest.get("schema") == MANIFEST_SCHEMA
        and manifest.get("version") == VERSION
        and manifest.get("host") == "standalone"
        and manifest.get("wordpressRequired") is False,
        json.dumps({
            "schema": manifest.get("schema"),
            "version": manifest.get("version"),
            "host": manifest.get("host"),
            "wordpressRequired": manifest.get("wordpressRequired"),
        }, sort_keys=True),
    ))

    missing = []
    mismatches = []
    for asset_id, entry in manifest.get("assets", {}).items():
        path = root / "assets" / entry["file"]
        if not path.is_file():
            missing.append(f"{asset_id}:{entry['file']}")
            continue
        expected = str(entry.get("sha256") or "")
        actual = digest(path)
        if expected and actual != expected:
            mismatches.append(f"{asset_id}:{actual}!={expected}")

    gates.append(emit("WORKSPACE_STANDALONE_ASSET_COMPLETENESS", not missing, ";".join(missing)))
    gates.append(emit("WORKSPACE_STANDALONE_ASSET_SHA256_INTEGRITY", not mismatches, ";".join(mismatches)))

    text_paths = [
        root / "index.html",
        root / "config.js",
        root / "bootstrap.js",
    ]
    text_paths.extend(
        root / "assets" / entry["file"]
        for entry in manifest.get("assets", {}).values()
        if str(entry.get("file", "")).endswith((".js", ".css", ".json"))
    )

    coupling_hits = []
    for path in text_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in FORBIDDEN_COUPLING:
            if marker in text:
                coupling_hits.append(f"{path.relative_to(root)}:{marker}")
    gates.append(emit("WORKSPACE_WORDPRESS_ABSENT_CERTIFICATION", not coupling_hits, ";".join(coupling_hits)))

    bootstrap = (root / "bootstrap.js").read_text(encoding="utf-8")
    gates.append(emit(
        "WORKSPACE_STANDALONE_MANIFEST_DRIVEN_BOOT",
        "manifest.loadOrder" in bootstrap
        and "manifest.assets[id]" in bootstrap
        and "sc-workspace-application-kernel-v3480.js" not in bootstrap,
    ))

    served = []
    with local_server(root) as base:
        required_urls = [
            "/",
            "/index.html",
            "/config.js",
            "/bootstrap.js",
            "/asset-manifest-v3480.json",
            "/assets/sc-workspace-runtime-asset-manifest-v3480.js",
        ]
        for rel in required_urls:
            try:
                body = fetch(base + rel)
                served.append((rel, len(body)))
            except Exception as exc:
                served.append((rel, 0, str(exc)))

    http_ok = all(len(item) == 2 and item[1] > 0 for item in served)
    gates.append(emit("WORKSPACE_STANDALONE_STATIC_HTTP_SERVE", http_ok, json.dumps(served)))

    config_text = (root / "config.js").read_text(encoding="utf-8")
    gates.append(emit(
        "WORKSPACE_STANDALONE_DIRECT_BACKEND_CONFIG",
        "https://workspace-api.sustainablecatalyst.com" in config_text
        and "wordpressRequired: false" in config_text,
    ))

    live_backend = None
    if backend_url:
        health_url = backend_url.rstrip("/") + "/health"
        try:
            body = fetch(health_url)
            data = json.loads(body)
            live_backend = {
                "url": health_url,
                "ok": data.get("ok") is True and data.get("version") == VERSION,
                "version": data.get("version"),
            }
            gates.append(emit(
                "WORKSPACE_STANDALONE_LIVE_BACKEND_HEALTH",
                live_backend["ok"],
                json.dumps(live_backend, sort_keys=True),
            ))
        except Exception as exc:
            live_backend = {"url": health_url, "ok": False, "error": str(exc)}
            gates.append(emit(
                "WORKSPACE_STANDALONE_LIVE_BACKEND_HEALTH",
                False,
                json.dumps(live_backend, sort_keys=True),
            ))

    passed = all(gate["ok"] for gate in gates)
    report = {
        "schema": REPORT_SCHEMA,
        "version": VERSION,
        "passed": passed,
        "gateCount": len(gates),
        "gates": gates,
        "backendProbe": live_backend,
        "wordpressRequired": False,
        "directBackendTransport": True,
        "hostAgnosticAssetPipeline": True,
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Certify the Workspace v3.48.0 standalone production distribution.")
    parser.add_argument("--root", default=None, help="Standalone distribution root. Defaults to the script directory.")
    parser.add_argument("--backend-url", default="", help="Optional live backend base URL.")
    parser.add_argument("--write-report", default="", help="Optional report JSON output path.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent
    report = certify(root, args.backend_url)

    if args.write_report:
        output = Path(args.write_report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not report["passed"]:
        raise SystemExit(1)

    print("WORKSPACE_STANDALONE_RUNTIME_PRODUCTION_CERTIFICATION=PASS")


if __name__ == "__main__":
    main()
