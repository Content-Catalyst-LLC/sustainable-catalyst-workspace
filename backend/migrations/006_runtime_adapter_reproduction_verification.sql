-- Workspace v2.6.0 — Runtime Adapter Registry & Reproduction Verification

CREATE TABLE IF NOT EXISTS workspace_runtime_adapter_heads (
    user_key VARCHAR(128) NOT NULL,
    adapter_id VARCHAR(160) NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    runtime_family VARCHAR(64) NOT NULL DEFAULT 'custom',
    runtime_version VARCHAR(96) NOT NULL DEFAULT '',
    adapter_type VARCHAR(64) NOT NULL DEFAULT 'metadata',
    revision INTEGER NOT NULL DEFAULT 1,
    fingerprint VARCHAR(64) NOT NULL,
    last_operation_id VARCHAR(160) NOT NULL DEFAULT '',
    dependency_managers_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    container_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    platform_constraints_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    capabilities_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    configuration_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, adapter_id)
);

CREATE TABLE IF NOT EXISTS workspace_runtime_adapter_revisions (
    user_key VARCHAR(128) NOT NULL,
    adapter_id VARCHAR(160) NOT NULL,
    revision INTEGER NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    runtime_family VARCHAR(64) NOT NULL DEFAULT 'custom',
    runtime_version VARCHAR(96) NOT NULL DEFAULT '',
    adapter_type VARCHAR(64) NOT NULL DEFAULT 'metadata',
    fingerprint VARCHAR(64) NOT NULL,
    operation_id VARCHAR(160) NOT NULL DEFAULT '',
    dependency_managers_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    container_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    platform_constraints_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    capabilities_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    configuration_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, adapter_id, revision)
);

ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS runtime_adapter_ref JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE workspace_execution_runs ADD COLUMN IF NOT EXISTS runtime_adapter_fingerprint VARCHAR(64) NOT NULL DEFAULT '';

CREATE TABLE IF NOT EXISTS workspace_reproduction_plans (
    user_key VARCHAR(128) NOT NULL,
    plan_id VARCHAR(96) NOT NULL,
    original_run_id VARCHAR(96) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'planned',
    fingerprint VARCHAR(64) NOT NULL,
    runtime_adapter_ref JSONB NOT NULL DEFAULT '{}'::jsonb,
    environment_ref JSONB NOT NULL DEFAULT '{}'::jsonb,
    expected_outputs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    compatibility_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, plan_id)
);

CREATE TABLE IF NOT EXISTS workspace_reproduction_verifications (
    user_key VARCHAR(128) NOT NULL,
    verification_id VARCHAR(96) NOT NULL,
    original_run_id VARCHAR(96) NOT NULL,
    reproduction_run_id VARCHAR(96) NOT NULL,
    classification VARCHAR(32) NOT NULL,
    exact_inputs BOOLEAN NOT NULL DEFAULT FALSE,
    exact_environment BOOLEAN NOT NULL DEFAULT FALSE,
    exact_runtime_adapter BOOLEAN NOT NULL DEFAULT FALSE,
    exact_outputs BOOLEAN NOT NULL DEFAULT FALSE,
    fingerprint VARCHAR(64) NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, verification_id)
);

CREATE INDEX IF NOT EXISTS workspace_runtime_adapter_project_idx ON workspace_runtime_adapter_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_runtime_adapter_revision_idx ON workspace_runtime_adapter_revisions (user_key, adapter_id, revision DESC);
CREATE INDEX IF NOT EXISTS workspace_reproduction_plan_run_idx ON workspace_reproduction_plans (user_key, original_run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_reproduction_verification_run_idx ON workspace_reproduction_verifications (user_key, original_run_id, reproduction_run_id, created_at DESC);

GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    workspace_runtime_adapter_heads, workspace_runtime_adapter_revisions,
    workspace_reproduction_plans, workspace_reproduction_verifications,
    workspace_execution_runs
TO sc_workspace;
