#!/usr/bin/env python3
from pathlib import Path
import json
import py_compile

ROOT = Path(__file__).resolve().parents[1]
errors = []

for rel in [
    "backend/app/main.py", "backend/app/repository.py", "backend/app/models.py",
    "backend/app/security.py", "backend/app/config.py", "backend/app/schemas.py",
    "backend/app/migration.py", "backend/app/object_store.py", "backend/app/recovery.py",
]:
    try:
        py_compile.compile(str(ROOT / rel), doraise=True)
    except Exception as exc:
        errors.append(f"compile {rel}: {exc}")

plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
if "Version: 2.2.0" not in plugin or "SC_WORKSPACE_VERSION', '2.2.0" not in plugin:
    errors.append("WordPress plugin version is not v2.2.0")

bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
for token in ["configured_request", "legacyMigrationPlanApply", "content-addressed-filesystem", "recoverySnapshots", "No fallback write was attempted"]:
    if token not in bridge:
        errors.append(f"backend bridge missing {token}")

workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
for token in ["backend-migration/plan", "backend-migration/apply", "backend-migration/receipts", "backend-storage-integrity", "backend-recovery-snapshots"]:
    if token not in workspace:
        errors.append(f"Workspace REST bridge missing {token}")

compose = (ROOT / "backend/docker-compose.example.yml").read_text()
for token in ['127.0.0.1:8094:8089', 'sc-workspace-data:/data', 'name: sc-workspace-data']:
    if token not in compose:
        errors.append(f"compose persistence contract missing {token}")

manifest = json.loads((ROOT / "release-manifest-v2.2.0.json").read_text())
if manifest.get("previous_version") != "2.1.0":
    errors.append("rollback lineage is not v2.1.0")
backend = manifest.get("backend_foundation", {})
for field in ["legacy_migration_plan_apply", "migration_receipts", "object_storage", "recovery_snapshots", "storage_integrity_checks"]:
    if backend.get(field) is not True:
        errors.append(f"backend manifest missing {field}")

schema = json.loads((ROOT / "schemas/sc-workspace-backend-persistence-v2.schema.json").read_text())
if schema.get("properties", {}).get("version", {}).get("const") != "2.2.0":
    errors.append("persistence schema version mismatch")

if errors:
    print("FAIL — Workspace v2.2.0 persistence hardening")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)
print("PASS — Workspace v2.2.0 persistence migration, object storage, and recovery hardening validated")
