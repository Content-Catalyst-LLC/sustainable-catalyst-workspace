#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

SCHEMA = "sc-workspace-build-asset-manifest/1.0"
RUNTIME_SCHEMA = "sc-workspace-runtime-asset-manifest/1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(repo: Path) -> dict:
    path = repo / "build/workspace-runtime-assets-v3510.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise SystemExit(f"ERROR: unexpected build manifest schema: {data.get('schema')}")
    if data.get("version") != "3.51.0":
        raise SystemExit(f"ERROR: unexpected build manifest version: {data.get('version')}")
    return data


def runtime_manifest(repo: Path, manifest: dict, host: str) -> dict:
    assets = {}
    ordered = []
    for item in sorted(manifest["assets"], key=lambda x: (int(x.get("order", 1000)), x["id"])):
        target = (item.get("targets") or {}).get(host)
        if not target or not item.get("runtime", True):
            continue
        source = repo / item["source"]
        if not source.is_file():
            raise SystemExit(f"ERROR: canonical asset missing: {source}")
        file_name = Path(target).name
        assets[item["id"]] = {
            "file": file_name,
            "sha256": sha256(source),
            "shared": bool(item.get("shared")),
            "order": int(item.get("order", 1000)),
        }
        if item.get("autoload", True):
            ordered.append(item["id"])
    return {
        "schema": RUNTIME_SCHEMA,
        "version": manifest["version"],
        "host": host,
        "assets": assets,
        "loadOrder": ordered,
        "generatedFrom": "build/workspace-runtime-assets-v3510.json",
        "wordpressRequired": False,
    }


def manifest_js(data: dict) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return (
        "(function(root){'use strict';"
        f"const manifest={encoded};"
        "root.SCWorkspaceRuntimeAssetManifest=Object.freeze(manifest);"
        "})(typeof globalThis!=='undefined'?globalThis:this);"
    )


def expected_outputs(repo: Path, manifest: dict):
    outputs = []
    for item in manifest["assets"]:
        source = repo / item["source"]
        if not source.is_file():
            raise SystemExit(f"ERROR: canonical asset missing: {source}")
        for host, target in (item.get("targets") or {}).items():
            outputs.append((source, repo / target, item))
    return outputs


def build(repo: Path, check: bool = False) -> None:
    manifest = load_manifest(repo)
    outputs = expected_outputs(repo, manifest)

    drift = []
    for source, target, item in outputs:
        if check:
            if not target.is_file() or target.read_bytes() != source.read_bytes():
                drift.append(f"{item['id']}:{target.relative_to(repo)}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    host_targets = {
        "wordpress": (
            repo / "wordpress/sustainable-catalyst-workspace/assets/manifests/workspace-runtime-assets-v3510.json",
            repo / "wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-runtime-asset-manifest-v3510.js",
        ),
        "standalone": (
            repo / "standalone/asset-manifest-v3510.json",
            repo / "standalone/assets/sc-workspace-runtime-asset-manifest-v3510.js",
        ),
    }

    manifests = {}
    for host, (json_target, js_target) in host_targets.items():
        data = runtime_manifest(repo, manifest, host)
        manifests[host] = data
        expected_json = json.dumps(data, indent=2, sort_keys=True) + "\n"
        expected_js = manifest_js(data) + "\n"
        if check:
            if not json_target.is_file() or json_target.read_text(encoding="utf-8") != expected_json:
                drift.append(str(json_target.relative_to(repo)))
            if not js_target.is_file() or js_target.read_text(encoding="utf-8") != expected_js:
                drift.append(str(js_target.relative_to(repo)))
        else:
            json_target.parent.mkdir(parents=True, exist_ok=True)
            js_target.parent.mkdir(parents=True, exist_ok=True)
            json_target.write_text(expected_json, encoding="utf-8")
            js_target.write_text(expected_js, encoding="utf-8")

    wp = manifests["wordpress"]["assets"]
    standalone = manifests["standalone"]["assets"]
    for item in manifest["assets"]:
        if not item.get("shared"):
            continue
        asset_id = item["id"]
        if asset_id not in wp or asset_id not in standalone:
            raise SystemExit(f"ERROR: shared asset missing host target: {asset_id}")
        if wp[asset_id]["sha256"] != standalone[asset_id]["sha256"]:
            raise SystemExit(f"ERROR: shared asset checksum parity failed: {asset_id}")

    if drift:
        for item in drift:
            print("ASSET_DRIFT=" + item)
        raise SystemExit("ERROR: generated host assets differ from canonical sources")

    print("WORKSPACE_HOST_AGNOSTIC_ASSET_PIPELINE=PASS")
    print("WORKSPACE_WORDPRESS_ASSET_MANIFEST=PASS")
    print("WORKSPACE_STANDALONE_ASSET_MANIFEST=PASS")
    print("WORKSPACE_SHARED_ASSET_CHECKSUM_PARITY=PASS")
    print("WORKSPACE_GENERATED_ASSET_DRIFT=NONE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    build(Path(args.repo).resolve(), check=args.check)


if __name__ == "__main__":
    main()
