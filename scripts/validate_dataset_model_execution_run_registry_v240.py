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
    "backend/app/registry.py",
]:
    try:
        py_compile.compile(str(ROOT / rel), doraise=True)
    except Exception as exc:
        errors.append(f"compile {rel}: {exc}")

plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
if "Version: 2.4.0" not in plugin or "SC_WORKSPACE_VERSION', '2.4.0" not in plugin:
    errors.append("WordPress plugin version is not v2.4.0")

workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
for token in ["backend-datasets", "backend-models", "backend-parameter-sets", "backend-runs", "backend_run_output_store"]:
    if token not in workspace:
        errors.append(f"Workspace REST bridge missing {token}")

bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
for token in ["datasetRegistry", "datasetRevisionHistory", "modelRegistry", "modelRevisionHistory", "parameterSetRegistry", "executionRunRegistry", "jobExecutionRunLinkage", "reproducibilityFingerprints"]:
    if token not in bridge:
        errors.append(f"backend bridge missing {token}")

models = (ROOT / "backend/app/models.py").read_text()
for token in ["workspace_dataset_heads", "workspace_dataset_revisions", "workspace_model_heads", "workspace_model_revisions", "workspace_parameter_set_heads", "workspace_execution_runs", "workspace_execution_run_outputs", "workspace_execution_run_events", "execution_run_id"]:
    if token not in models:
        errors.append(f"backend models missing {token}")

main = (ROOT / "backend/app/main.py").read_text()
for route in ["/v1/datasets", "/v1/models", "/v1/parameter-sets", "/v1/runs", "/v1/runs/{run_id}/outputs"]:
    if route not in main:
        errors.append(f"backend route missing {route}")

registry = (ROOT / "backend/app/registry.py").read_text()
for token in ["input_fingerprint", "reproducibility_fingerprint", "_resolve_dataset_ref", "_resolve_model_ref", "_resolve_parameter_ref", "link_job_to_run", "sync_run_from_job"]:
    if token not in registry:
        errors.append(f"registry runtime missing {token}")

migration = (ROOT / "backend/migrations/004_dataset_model_execution_run_registry.sql").read_text()
for token in ["workspace_dataset_heads", "workspace_model_heads", "workspace_parameter_set_heads", "workspace_execution_runs", "workspace_execution_run_outputs", "ALTER TABLE workspace_jobs ADD COLUMN IF NOT EXISTS execution_run_id"]:
    if token not in migration:
        errors.append(f"registry migration missing {token}")

manifest = json.loads((ROOT / "release-manifest-v2.4.0.json").read_text())
if manifest.get("version") != "2.4.0":
    errors.append("release manifest version mismatch")
if manifest.get("previous_version") != "2.3.0":
    errors.append("rollback lineage is not v2.3.0")
backend = manifest.get("backend_foundation", {})
for field in ["dataset_registry", "dataset_revision_history", "model_registry", "model_revision_history", "parameter_set_registry", "execution_run_registry", "execution_run_events", "execution_run_outputs", "job_execution_run_linkage", "reproducibility_fingerprints"]:
    if backend.get(field) is not True:
        errors.append(f"backend manifest missing {field}")

schema = json.loads((ROOT / "schemas/sc-workspace-dataset-model-run-registry-v1.schema.json").read_text())
props = schema.get("properties", {})
if props.get("version", {}).get("const") != "2.4.0":
    errors.append("registry schema version mismatch")
if props.get("automaticModelExecution", {}).get("const") is not False:
    errors.append("registry schema must prohibit automatic model execution")
if props.get("browserSuppliedRouteUrlsAllowed", {}).get("const") is not False:
    errors.append("registry schema must prohibit browser-supplied route URLs")

for asset in [
    ROOT / "wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.4.0.js",
    ROOT / "wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.4.0.css",
]:
    if not asset.is_file() or asset.stat().st_size < 1000:
        errors.append(f"versioned asset missing or unexpectedly small: {asset.name}")

if errors:
    print("FAIL — Workspace v2.4.0 Dataset, Model & Execution Run Registry")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)
print("PASS — Workspace v2.4.0 Dataset, Model & Execution Run Registry validated")
