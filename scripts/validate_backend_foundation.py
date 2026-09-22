#!/usr/bin/env python3
from pathlib import Path
import json
import py_compile

ROOT = Path(__file__).resolve().parents[1]
errors = []

for rel in [
    "backend/app/main.py", "backend/app/repository.py", "backend/app/models.py",
    "backend/app/security.py", "backend/app/config.py", "backend/app/schemas.py",
]:
    try:
        py_compile.compile(str(ROOT / rel), doraise=True)
    except Exception as exc:
        errors.append(f"compile {rel}: {exc}")

plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
if "Version: 2.1.0" not in plugin:
    errors.append("WordPress plugin header is not v2.1.0")

bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
for token in ["SC_WORKSPACE_BACKEND_URL", "SC_WORKSPACE_BACKEND_TOKEN", "SC_WORKSPACE_BACKEND_MODE", "No fallback write was attempted"]:
    if token not in bridge:
        errors.append(f"backend bridge missing {token}")

manifest = json.loads((ROOT / "release-manifest-v2.1.0.json").read_text())
if manifest.get("previous_version") != "2.0.4":
    errors.append("rollback lineage is not v2.0.4")
if manifest.get("backend_foundation", {}).get("database") != "PostgreSQL":
    errors.append("backend manifest does not declare PostgreSQL")

if errors:
    print("FAIL — Workspace v2.1.0 backend foundation")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)
print("PASS — Workspace v2.1.0 backend foundation and persistence bridge validated")
