#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
required = [
    "backend/r-runtime/Dockerfile",
    "backend/r-runtime/service.py",
    "backend/r-runtime/runner.R",
    "backend/migrations/013_r_statistical_econometric_runtime.sql",
    "schemas/sc-workspace-r-statistical-runtime-v1.schema.json",
    "tests/test_r_statistical_econometric_runtime_v2130.py",
    "registry/workspace-product-record-v2.13.0.json",
    "release-manifest-v2.13.0.json",
    "RELEASE_NOTES_2.13.0.md",
]
missing = [x for x in required if not (ROOT / x).is_file()]
assert not missing, f"missing v2.13 files: {missing}"
assert 'service_version: str = "2.13.0"' in (ROOT / "backend/app/config.py").read_text()
assert "Version: 2.13.0" in (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
manifest = json.loads((ROOT / "release-manifest-v2.13.0.json").read_text())
assert manifest["previous_version"] == "2.12.0"
assert manifest["r_runtime"]["operation_count"] == 8
assert manifest["r_runtime"]["arbitrary_code_execution"] is False
print("PASS — Workspace v2.13.0 R statistical/econometric runtime validated")
