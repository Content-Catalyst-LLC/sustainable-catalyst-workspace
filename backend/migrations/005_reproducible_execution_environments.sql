-- Workspace v2.5.0 — Reproducible Execution Environments & Dependency Manifests

CREATE TABLE IF NOT EXISTS workspace_execution_environment_heads (
    user_key VARCHAR(128) NOT NULL,
    environment_id VARCHAR(160) NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    fingerprint VARCHAR(64) NOT NULL,
    last_operation_id VARCHAR(160) NOT NULL DEFAULT '',
    runtime_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    dependencies_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    lock_artifacts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    container_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    system_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    hardware_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    random_seeds_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    env_var_names_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    configuration_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, environment_id)
);

CREATE TABLE IF NOT EXISTS workspace_execution_environment_revisions (
    user_key VARCHAR(128) NOT NULL,
    environment_id VARCHAR(160) NOT NULL,
    revision INTEGER NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    fingerprint VARCHAR(64) NOT NULL,
    operation_id VARCHAR(160) NOT NULL DEFAULT '',
    runtime_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    dependencies_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    lock_artifacts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    container_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    system_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    hardware_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    random_seeds_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    env_var_names_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    configuration_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, environment_id, revision)
);

ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS environment_ref JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS environment_fingerprint VARCHAR(64) NOT NULL DEFAULT '';

CREATE INDEX IF NOT EXISTS workspace_execution_environment_project_idx ON workspace_execution_environment_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_environment_revision_idx ON workspace_execution_environment_revisions (user_key, environment_id, revision DESC);

-- v2.4.0 deployment repair plus v2.5.0 grants. Migrations are applied by the PostgreSQL admin role.
GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    workspace_dataset_heads, workspace_dataset_revisions,
    workspace_model_heads, workspace_model_revisions,
    workspace_parameter_set_heads, workspace_parameter_set_revisions,
    workspace_execution_runs, workspace_execution_run_outputs, workspace_execution_run_events,
    workspace_jobs, workspace_job_events, workspace_worker_heartbeats,
    workspace_execution_environment_heads, workspace_execution_environment_revisions
TO sc_workspace;
