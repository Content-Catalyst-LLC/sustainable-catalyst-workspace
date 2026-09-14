-- Workspace v2.9.0 — Runtime Enforcement Telemetry, Budget Accounting & Execution Attestations

CREATE TABLE IF NOT EXISTS workspace_runtime_execution_attestations (
    user_key VARCHAR(128) NOT NULL,
    attestation_id VARCHAR(96) NOT NULL,
    handoff_receipt_id VARCHAR(96) NOT NULL,
    execution_plan_id VARCHAR(96) NOT NULL,
    reproduction_run_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    policy_decision_id VARCHAR(96) NOT NULL,
    policy_decision_fingerprint VARCHAR(64) NOT NULL,
    source VARCHAR(64) NOT NULL,
    classification VARCHAR(32) NOT NULL,
    execution_succeeded BOOLEAN NOT NULL DEFAULT FALSE,
    budget_compliant BOOLEAN NOT NULL DEFAULT FALSE,
    sandbox_compliant BOOLEAN NOT NULL DEFAULT FALSE,
    observed_usage_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    budget_accounting_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    sandbox_attestation_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    checks_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT NOT NULL DEFAULT '',
    fingerprint VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, attestation_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS workspace_runtime_execution_attestation_receipt_idx
    ON workspace_runtime_execution_attestations (user_key, handoff_receipt_id);
CREATE INDEX IF NOT EXISTS workspace_runtime_execution_attestation_run_idx
    ON workspace_runtime_execution_attestations (user_key, reproduction_run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_runtime_execution_attestation_job_idx
    ON workspace_runtime_execution_attestations (user_key, job_id, created_at DESC);

GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
    workspace_runtime_execution_attestations,
    workspace_execution_policy_decisions,
    workspace_reproduction_execution_plans,
    workspace_runtime_handoff_receipts,
    workspace_jobs
TO sc_workspace;
