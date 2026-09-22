#!/usr/bin/env python3
from pathlib import Path
import json
import py_compile

ROOT = Path(__file__).resolve().parents[1]
errors = []

for rel in [
    "backend/app/main.py", "backend/app/jobs.py", "backend/app/routing.py", "backend/app/worker.py",
    "backend/app/repository.py", "backend/app/models.py", "backend/app/security.py", "backend/app/config.py",
    "backend/app/schemas.py", "backend/app/migration.py", "backend/app/object_store.py", "backend/app/recovery.py",
]:
    try:
        py_compile.compile(str(ROOT / rel), doraise=True)
    except Exception as exc:
        errors.append(f"compile {rel}: {exc}")

plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
if "Version: 2.3.0" not in plugin or "SC_WORKSPACE_VERSION', '2.3.0" not in plugin:
    errors.append("WordPress plugin version is not v2.3.0")

bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
for token in ["durableJobQueue", "workerProcess", "jobEventHistory", "jobRetryAndCancel", "computeOrchestration", "serverConfiguredRoutesOnly"]:
    if token not in bridge:
        errors.append(f"backend bridge missing {token}")

workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
for token in ["backend-jobs", "backend-worker-status", "backend-orchestration-routes", "backend_job_cancel", "backend_job_retry"]:
    if token not in workspace:
        errors.append(f"Workspace REST bridge missing {token}")

compose = (ROOT / "backend/docker-compose.example.yml").read_text()
for token in ["sc-workspace-worker", 'command: ["python", "-m", "app.worker"]', "127.0.0.1:8094:8089", "sc-workspace-data:/data"]:
    if token not in compose:
        errors.append(f"compose worker contract missing {token}")

migration = (ROOT / "backend/migrations/003_background_jobs_orchestration.sql").read_text()
for token in ["workspace_jobs", "workspace_job_events", "workspace_worker_heartbeats", "SKIP LOCKED" if False else "workspace_jobs_queue_idx"]:
    if token not in migration:
        errors.append(f"job migration missing {token}")

manifest = json.loads((ROOT / "release-manifest-v2.3.0.json").read_text())
if manifest.get("previous_version") != "2.2.0":
    errors.append("rollback lineage is not v2.2.0")
backend = manifest.get("backend_foundation", {})
for field in ["durable_background_jobs", "separate_worker_process", "job_event_history", "job_retry_cancel", "compute_orchestration", "server_configured_routes_only"]:
    if backend.get(field) is not True:
        errors.append(f"backend manifest missing {field}")

schema = json.loads((ROOT / "schemas/sc-workspace-background-jobs-v1.schema.json").read_text())
if schema.get("properties", {}).get("version", {}).get("const") != "2.3.0":
    errors.append("background jobs schema version mismatch")

if errors:
    print("FAIL — Workspace v2.3.0 background jobs and compute orchestration")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)
print("PASS — Workspace v2.3.0 background jobs and compute orchestration foundation validated")
