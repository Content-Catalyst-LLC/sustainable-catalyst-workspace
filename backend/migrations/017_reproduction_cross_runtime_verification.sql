CREATE TABLE IF NOT EXISTS workspace_cross_runtime_verification_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    original_run_id VARCHAR(96) NOT NULL,
    reproduction_run_id VARCHAR(96) NOT NULL,
    source_runtime VARCHAR(96) NOT NULL DEFAULT '',
    target_runtime VARCHAR(96) NOT NULL DEFAULT '',
    comparison_mode VARCHAR(64) NOT NULL DEFAULT 'auto',
    classification VARCHAR(32) NOT NULL,
    exact_inputs BOOLEAN NOT NULL DEFAULT FALSE,
    exact_environment BOOLEAN NOT NULL DEFAULT FALSE,
    exact_runtime BOOLEAN NOT NULL DEFAULT FALSE,
    exact_outputs BOOLEAN NOT NULL DEFAULT FALSE,
    equivalent_outputs BOOLEAN NOT NULL DEFAULT FALSE,
    absolute_tolerance DOUBLE PRECISION NOT NULL DEFAULT 1e-9,
    relative_tolerance DOUBLE PRECISION NOT NULL DEFAULT 1e-7,
    compared_output_count INTEGER NOT NULL DEFAULT 0,
    result_artifact_id VARCHAR(160) NOT NULL DEFAULT '',
    result_sha256 VARCHAR(64) NOT NULL DEFAULT '',
    fingerprint VARCHAR(64) NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_cross_runtime_verification_runs_idx
    ON workspace_cross_runtime_verification_receipts(user_key, original_run_id, reproduction_run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_cross_runtime_verification_class_idx
    ON workspace_cross_runtime_verification_receipts(user_key, classification, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_cross_runtime_verification_receipts TO sc_workspace;
