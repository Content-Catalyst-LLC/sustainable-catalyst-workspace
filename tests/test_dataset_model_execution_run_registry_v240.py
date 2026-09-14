from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_v240_identity_and_lineage():
    plugin = (ROOT / "wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php").read_text()
    assert "Version: 2.4.0" in plugin
    manifest = json.loads((ROOT / "release-manifest-v2.4.0.json").read_text())
    assert manifest["version"] == "2.4.0"
    assert manifest["previous_version"] == "2.3.0"
    assert manifest["release_name"] == "Dataset, Model & Execution Run Registry"


def test_registry_database_contract_is_present():
    models = (ROOT / "backend/app/models.py").read_text()
    for token in [
        "workspace_dataset_heads", "workspace_dataset_revisions", "workspace_model_heads", "workspace_model_revisions",
        "workspace_parameter_set_heads", "workspace_execution_runs", "workspace_execution_run_outputs", "workspace_execution_run_events",
    ]:
        assert token in models
    migration = (ROOT / "backend/migrations/004_dataset_model_execution_run_registry.sql").read_text()
    assert "ALTER TABLE workspace_jobs ADD COLUMN IF NOT EXISTS execution_run_id" in migration


def test_registry_routes_are_present():
    main = (ROOT / "backend/app/main.py").read_text()
    for route in ["/v1/datasets", "/v1/models", "/v1/parameter-sets", "/v1/runs", "/v1/runs/{run_id}/outputs"]:
        assert route in main


def test_registry_freezes_references_and_hashes_lineage():
    registry = (ROOT / "backend/app/registry.py").read_text()
    for token in ["input_fingerprint", "reproducibility_fingerprint", "_resolve_dataset_ref", "_resolve_model_ref", "_resolve_parameter_ref"]:
        assert token in registry
    assert "later edits" not in registry.lower()  # behavior is structural rather than commentary-only


def test_jobs_link_to_execution_runs():
    jobs = (ROOT / "backend/app/jobs.py").read_text()
    models = (ROOT / "backend/app/models.py").read_text()
    schemas = (ROOT / "backend/app/schemas.py").read_text()
    assert "execution_run_id" in models
    assert "executionRunId" in schemas
    assert "sync_run_from_job" in jobs
    assert "link_job_to_run" in jobs


def test_wordpress_registry_proxy_routes_exist():
    workspace = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    bridge = (ROOT / "wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php").read_text()
    for route in ["backend-datasets", "backend-models", "backend-parameter-sets", "backend-runs"]:
        assert route in workspace
    for flag in ["datasetRegistry", "modelRegistry", "parameterSetRegistry", "executionRunRegistry", "reproducibilityFingerprints"]:
        assert flag in bridge


def test_registry_schema_contract_is_bounded():
    contract = json.loads((ROOT / "schemas/sc-workspace-dataset-model-run-registry-v1.schema.json").read_text())
    props = contract["properties"]
    assert props["version"]["const"] == "2.4.0"
    assert props["inputReferencesFrozenAtRunCreation"]["const"] is True
    assert props["automaticModelExecution"]["const"] is False
    assert props["browserSuppliedRouteUrlsAllowed"]["const"] is False
