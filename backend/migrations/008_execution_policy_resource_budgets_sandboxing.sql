-- Workspace v2.8.0 — Execution Policy, Resource Budgets & Runtime Sandboxing

ALTER TABLE workspace_runtime_adapter_heads
    ADD COLUMN IF NOT EXISTS trust_level VARCHAR(32) NOT NULL DEFAULT 'bounded';
ALTER TABLE workspace_runtime_adapter_revisions
    ADD COLUMN IF NOT EXISTS trust_level VARCHAR(32) NOT NULL DEFAULT 'bounded';

CREATE TABLE IF NOT EXISTS workspace_execution_policy_heads (
    user_key VARCHAR(128) NOT NULL,
    policy_id VARCHAR(160) NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    fingerprint VARCHAR(64) NOT NULL,
    last_operation_id VARCHAR(160) NOT NULL DEFAULT '',
    allowed_targets_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_operations_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    minimum_adapter_trust VARCHAR(32) NOT NULL DEFAULT 'bounded',
    resource_limits_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    sandbox_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, policy_id)
);

CREATE TABLE IF NOT EXISTS workspace_execution_policy_revisions (
    user_key VARCHAR(128) NOT NULL,
    policy_id VARCHAR(160) NOT NULL,
    revision INTEGER NOT NULL,
    project_id VARCHAR(160) NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    fingerprint VARCHAR(64) NOT NULL,
    operation_id VARCHAR(160) NOT NULL DEFAULT '',
    allowed_targets_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_operations_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    minimum_adapter_trust VARCHAR(32) NOT NULL DEFAULT 'bounded',
    resource_limits_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    sandbox_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, policy_id, revision)
);

CREATE TABLE IF NOT EXISTS workspace_execution_policy_decisions (
    user_key VARCHAR(128) NOT NULL,
    decision_id VARCHAR(96) NOT NULL,
    execution_plan_id VARCHAR(96) NOT NULL,
    policy_id VARCHAR(160) NOT NULL,
    policy_revision INTEGER NOT NULL,
    policy_fingerprint VARCHAR(64) NOT NULL,
    eligible BOOLEAN NOT NULL DEFAULT FALSE,
    classification VARCHAR(32) NOT NULL DEFAULT 'blocked',
    resource_budget_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    sandbox_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    checks_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    fingerprint VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, decision_id)
);

CREATE INDEX IF NOT EXISTS workspace_execution_policy_project_idx
    ON workspace_execution_policy_heads (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_policy_decision_plan_idx
    ON workspace_execution_policy_decisions (user_key, execution_plan_id, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_execution_policy_decision_one_per_plan_idx
    ON workspace_execution_policy_decisions (user_key, execution_plan_id);

GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    workspace_execution_policy_heads,
    workspace_execution_policy_revisions,
    workspace_execution_policy_decisions,
    workspace_runtime_adapter_heads,
    workspace_runtime_adapter_revisions,
    workspace_reproduction_execution_plans,
    workspace_runtime_handoff_receipts,
    workspace_execution_runs,
    workspace_execution_run_outputs,
    workspace_execution_run_events,
    workspace_jobs,
    workspace_job_events,
    workspace_worker_heartbeats
TO sc_workspace;
