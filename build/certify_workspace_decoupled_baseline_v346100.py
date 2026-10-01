#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json


VERSION = "3.46.10.0"
SCHEMA = "sc-workspace-decoupled-production-baseline-certification/1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(name: str, ok: bool, detail: str = "") -> dict:
    print(f"{name}={'PASS' if ok else 'FAIL'}" + (f" :: {detail}" if detail and not ok else ""))
    return {"name": name, "ok": bool(ok), "detail": str(detail or "")}


def certify(repo: Path) -> dict:
    repo = repo.resolve()
    wp = repo / "wordpress/sustainable-catalyst-workspace"
    gates = []

    contract_path = repo / "production/decoupled-workspace-production-baseline-v3.46.10.0.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    gates.append(gate(
        "WORKSPACE_DECOUPLED_BASELINE_CONTRACT",
        contract.get("schema") == "sc-workspace-decoupled-production-baseline-contract/1.0"
        and contract.get("version") == VERSION
        and contract.get("productionBaseline") is True
        and contract.get("rollbackRelease") == "3.46.9.0",
    ))

    plugin = (wp / "sustainable-catalyst-workspace.php").read_text(encoding="utf-8")
    backend_config = (repo / "backend/app/config.py").read_text(encoding="utf-8")
    gates.append(gate(
        "WORKSPACE_DECOUPLED_BASELINE_RELEASE_IDENTITY",
        "Version: 3.46.10.0" in plugin
        and "define('SC_WORKSPACE_VERSION', '3.46.10.0');" in plugin
        and 'service_version: str = "3.46.10.0"' in backend_config,
    ))

    class_text = (wp / "includes/class-sc-workspace.php").read_text(encoding="utf-8")
    enqueue = class_text.split("private function enqueue_assets()", 1)[1].split("private function tools()", 1)[0]
    gates.append(gate(
        "WORKSPACE_WORDPRESS_THIN_HOST_BASELINE",
        enqueue.count("wp_enqueue_script(") == 1
        and "'sc-workspace-wordpress-thin-adapter-v346100'" in enqueue
        and "'assetManifestUrl'" in enqueue
        and "'applicationKernelUrl'" not in enqueue
        and "'projectRuntimeUrl'" not in enqueue
        and "'entryPointUrl'" not in enqueue,
    ))

    thin = (repo / "adapters/wordpress/workspace-wordpress-thin-adapter-v346100.js").read_text(encoding="utf-8")
    forbidden_thin = ("localStorage", "createProject(", "deleteProject(", "registerProjectLifecycle(")
    gates.append(gate(
        "WORKSPACE_WORDPRESS_ZERO_APPLICATION_OWNERSHIP",
        all(marker not in thin for marker in forbidden_thin),
        ",".join(marker for marker in forbidden_thin if marker in thin),
    ))

    standalone_report_path = repo / "standalone/production-certification-v346100.json"
    standalone_report = json.loads(standalone_report_path.read_text(encoding="utf-8"))
    gates.append(gate(
        "WORKSPACE_STANDALONE_PRODUCTION_CERTIFIED",
        standalone_report.get("schema") == "sc-workspace-standalone-production-certification-report/1.0"
        and standalone_report.get("version") == VERSION
        and standalone_report.get("passed") is True
        and standalone_report.get("wordpressRequired") is False,
    ))

    build_manifest = json.loads((repo / "build/workspace-runtime-assets-v346100.json").read_text(encoding="utf-8"))
    wp_manifest = json.loads((wp / "assets/manifests/workspace-runtime-assets-v346100.json").read_text(encoding="utf-8"))
    standalone_manifest = json.loads((repo / "standalone/asset-manifest-v346100.json").read_text(encoding="utf-8"))

    gates.append(gate(
        "WORKSPACE_HOST_AGNOSTIC_ASSET_PIPELINE_BASELINE",
        build_manifest.get("version") == VERSION
        and wp_manifest.get("version") == VERSION
        and standalone_manifest.get("version") == VERSION,
    ))

    parity_errors = []
    for item in build_manifest.get("assets", []):
        if not item.get("shared"):
            continue
        asset_id = item["id"]
        wp_entry = wp_manifest.get("assets", {}).get(asset_id)
        st_entry = standalone_manifest.get("assets", {}).get(asset_id)
        if not wp_entry or not st_entry or wp_entry.get("sha256") != st_entry.get("sha256"):
            parity_errors.append(asset_id)

    gates.append(gate(
        "WORKSPACE_SHARED_ASSET_CHECKSUM_PARITY",
        not parity_errors,
        ",".join(parity_errors),
    ))

    baseline_asset = repo / "app/core/workspace-decoupled-production-baseline-v346100.js"
    wp_baseline_asset = wp / "assets/js/sc-workspace-decoupled-production-baseline-v346100.js"
    st_baseline_asset = repo / "standalone/assets/sc-workspace-decoupled-production-baseline-v346100.js"
    gates.append(gate(
        "WORKSPACE_DECOUPLED_BASELINE_ASSET_PARITY",
        baseline_asset.is_file()
        and wp_baseline_asset.is_file()
        and st_baseline_asset.is_file()
        and sha256(baseline_asset) == sha256(wp_baseline_asset) == sha256(st_baseline_asset),
    ))

    kernel = (repo / "app/core/workspace-application-kernel-v346100.js").read_text(encoding="utf-8")
    runtime = (repo / "app/standalone/workspace-standalone-runtime-v346100.js").read_text(encoding="utf-8")
    registry = (repo / "app/core/workspace-module-registry-v34650.js").read_text(encoding="utf-8")
    gates.append(gate(
        "WORKSPACE_CORE_DECOUPLING_INVARIANTS",
        "decoupledProductionBaseline: true" in kernel
        and "wordpressRequired: false" in kernel
        and "productionCertificationContract: 'sc-workspace-standalone-production-certification/1.0'" in runtime
        and "decoupledProductionBaseline: '3.46.10.0'" in runtime
        and "optionalFailureIsolation: true" in registry,
    ))

    deployment = (wp / "includes/class-sc-workspace-deployment.php").read_text(encoding="utf-8")
    gates.append(gate(
        "WORKSPACE_DECOUPLED_BASELINE_ROLLBACK_CONTINUITY",
        "const PREVIOUS_RELEASE = '3.46.9.0';" in deployment
        and "const ROLLBACK_RELEASE = '3.46.9.0';" in deployment
        and "sc-workspace-decoupled-production-baseline-v346100.js" in deployment,
    ))

    gates.append(gate(
        "WORKSPACE_DECOUPLED_BASELINE_NO_MIGRATIONS",
        contract.get("databaseMigration") is False
        and contract.get("storageSchemaMigration") is False,
    ))

    passed = all(item["ok"] for item in gates)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "passed": passed,
        "gateCount": len(gates),
        "gates": gates,
        "productionBaseline": True,
        "rollbackRelease": "3.46.9.0",
        "databaseMigration": False,
        "storageSchemaMigration": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    report = certify(Path(args.repo))
    if args.write_report:
        target = Path(args.write_report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not report["passed"]:
        raise SystemExit(1)

    print("WORKSPACE_DECOUPLED_PRODUCTION_BASELINE_CERTIFICATION=PASS")


if __name__ == "__main__":
    main()
