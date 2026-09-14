-- Workspace v2.7.0 — Reproduction Execution Plans & Controlled Runtime Handoffs

CREATE TABLE IF NOT EXISTS workspace_reproduction_execution_plans (
    user_key VARCHAR(128) NOT NULL,
    execution_plan_id VARCHAR(96) NOT NULL,
    reproduction_plan_id VARCHAR(96) NOT NULL,
    original_run_id VARCHAR(96) NOT NULL,
    reproduction_run_id VARCHAR(96) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'planned',
    target_product VARCHAR(64) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    fingerprint VARCHAR(64) NOT NULL,
    input_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    environment_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    runtime_adapter_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    environment_ref JSONB NOT NULL DEFAULT '{}'::jsonb,
    runtime_adapter_ref JSONB NOT NULL DEFAULT '{}'::jsonb,
    job_request_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    readiness_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    policy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, execution_plan_id)
);

CREATE TABLE IF NOT EXISTS workspace_runtime_handoff_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    execution_plan_id VARCHAR(96) NOT NULL,
    reproduction_run_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    target_product VARCHAR(64) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    route_transport VARCHAR(64) NOT NULL,
    request_fingerprint VARCHAR(64) NOT NULL,
    fingerprint VARCHAR(64) NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);

CREATE INDEX IF NOT EXISTS workspace_repro_execution_plan_run_idx ON workspace_reproduction_execution_plans (user_key, reproduction_run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_runtime_handoff_plan_idx ON workspace_runtime_handoff_receipts (user_key, execution_plan_id, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_runtime_handoff_one_per_plan_idx ON workspace_runtime_handoff_receipts (user_key, execution_plan_id);

GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    workspace_reproduction_execution_plans, workspace_runtime_handoff_receipts,
    workspace_runtime_adapter_heads, workspace_runtime_adapter_revisions,
    workspace_reproduction_plans, workspace_reproduction_verifications,
    workspace_execution_environment_heads, workspace_execution_environment_revisions,
    workspace_execution_runs, workspace_execution_run_outputs, workspace_execution_run_events,
    workspace_jobs, workspace_job_events, workspace_worker_heartbeats
TO sc_workspace;
