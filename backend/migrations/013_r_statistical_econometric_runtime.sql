CREATE TABLE IF NOT EXISTS workspace_statistical_model_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    polyglot_receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    language VARCHAR(32) NOT NULL DEFAULT 'r',
    runtime VARCHAR(96) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    model_kind VARCHAR(96) NOT NULL DEFAULT '',
    outcome VARCHAR(160) NOT NULL DEFAULT '',
    predictors_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    request_fingerprint VARCHAR(64) NOT NULL,
    result_artifact_id VARCHAR(160) NOT NULL,
    result_sha256 VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_statistical_model_receipts_job_idx ON workspace_statistical_model_receipts(user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_statistical_model_receipts_run_idx ON workspace_statistical_model_receipts(user_key, execution_run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_statistical_model_receipts_operation_idx ON workspace_statistical_model_receipts(user_key, operation, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_statistical_model_receipts TO sc_workspace;
