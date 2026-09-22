#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    "backend/app/compute.py",
    "backend/migrations/011_python_scientific_compute_runtime.sql",
    "schemas/sc-workspace-scientific-compute-v1.schema.json",
    "tests/test_python_scientific_compute_v2110.py",
    "scripts/deploy_workspace_backend_v2_11_0_vps.sh",
    "release-manifest-v2.11.0.json",
    "registry/workspace-product-record-v2.11.0.json",
    "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.11.0.js",
    "wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.11.0.css",
]
for rel in required:
    path = ROOT / rel
    assert path.is_file(), f"missing {rel}"

config = (ROOT / "backend/app/config.py").read_text()
main = (ROOT / "backend/app/main.py").read_text()
compute = (ROOT / "backend/app/compute.py").read_text()
routing = (ROOT / "backend/app/routing.py").read_text()
compose = (ROOT / "backend/docker-compose.example.yml").read_text()
plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
dep = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php").read_text()
cert = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php").read_text()
requirements = (ROOT / "backend/requirements.txt").read_text()

assert 'service_version: str = "2.11.0"' in config
assert "Version: 2.11.0" in plugin
assert "define('SC_WORKSPACE_VERSION', '2.11.0')" in plugin
assert "const PREVIOUS_RELEASE = '2.10.0';" in dep and "const ROLLBACK_RELEASE = '2.10.0';" in dep
assert "const PREVIOUS_RELEASE = '2.10.0';" in cert and "const ROLLBACK_RELEASE = '2.10.0';" in cert
for token in [
    '"pythonScientificComputeRuntime": True',
    '"scientificComputeOperationRegistry": True',
    '"computeResultArtifacts": True',
    '"computeExecutionReceipts": True',
    '"boundedScientificOperationsOnly": True',
    '@app.get("/v1/compute/operations")',
    '@app.get("/v1/compute/receipts")',
]:
    assert token in main, token
for op in [
    "workspace.compute.describe",
    "workspace.compute.transform",
    "workspace.compute.linear-algebra",
    "workspace.compute.symbolic",
    "workspace.compute.integrate-series",
    "workspace.compute.optimize-quadratic",
    "workspace.compute.roots-polynomial",
]:
    assert op in compute, op
assert 'row.operation.startswith("workspace.compute.")' in routing
assert "subprocess" not in compute
assert "os.system" not in compute
assert "exec(" not in compute
assert "eval(" not in compute
for dep_name in ["numpy==", "pandas==", "scipy==", "sympy=="]:
    assert dep_name in requirements
for token in ["read_only: true", "cap_drop:", "- ALL", "no-new-privileges:true", "cpus: 2.0", "mem_limit: 2g", "pids_limit: 256"]:
    assert token in compose, token
for token in ["pythonScientificComputeRuntime", "scientificComputeOperationRegistry", "computeResultArtifacts", "computeExecutionReceipts", "boundedScientificOperationsOnly"]:
    assert token in bridge, token
for token in ["backend-compute-operations", "backend-compute-receipts", "workspace-v2.11.0.js", "workspace-v2.11.0.css", "python-scientific-compute-runtime-execution-engine"]:
    assert token in workspace, token
schema = json.loads((ROOT / "schemas/sc-workspace-scientific-compute-v1.schema.json").read_text())
assert schema["properties"]["version"]["const"] == "2.11.0"
assert schema["properties"]["boundedOperationsOnly"]["const"] is True
assert schema["properties"]["arbitraryCodeExecution"]["const"] is False
manifest = json.loads((ROOT / "release-manifest-v2.11.0.json").read_text())
assert manifest["version"] == "2.11.0" and manifest["previous_version"] == "2.10.0"
assert manifest["python_scientific_compute"]["arbitrary_code_execution"] is False
registry = json.loads((ROOT / "registry/workspace-product-record-v2.11.0.json").read_text())
assert registry["version"] == "2.11.0"
assert registry["python_scientific_compute"]["enabled"] is True
print("PASS — Workspace v2.11.0 Python scientific compute runtime validated")
