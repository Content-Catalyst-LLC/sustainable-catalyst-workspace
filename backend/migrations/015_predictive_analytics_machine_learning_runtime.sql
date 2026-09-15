CREATE TABLE IF NOT EXISTS workspace_predictive_model_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    polyglot_receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    runtime VARCHAR(96) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    model_kind VARCHAR(96) NOT NULL DEFAULT '',
    task VARCHAR(32) NOT NULL DEFAULT '',
    target VARCHAR(160) NOT NULL DEFAULT '',
    features_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    preprocessing_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    hyperparameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    dataset_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    random_seed INTEGER NOT NULL DEFAULT 0,
    train_rows INTEGER NOT NULL DEFAULT 0,
    test_rows INTEGER NOT NULL DEFAULT 0,
    metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_artifact_id VARCHAR(160) NOT NULL DEFAULT '',
    model_sha256 VARCHAR(64) NOT NULL DEFAULT '',
    result_artifact_id VARCHAR(160) NOT NULL,
    result_sha256 VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_predictive_model_receipts_job_idx ON workspace_predictive_model_receipts(user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_predictive_model_receipts_model_idx ON workspace_predictive_model_receipts(user_key, model_kind, created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_model_evaluation_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    predictive_model_receipt_id VARCHAR(96) NOT NULL DEFAULT '',
    polyglot_receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    operation VARCHAR(160) NOT NULL,
    evaluation_kind VARCHAR(64) NOT NULL DEFAULT '',
    fold_count INTEGER NOT NULL DEFAULT 0,
    dataset_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_artifact_id VARCHAR(160) NOT NULL,
    result_sha256 VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_model_evaluation_receipts_job_idx ON workspace_model_evaluation_receipts(user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_model_evaluation_receipts_operation_idx ON workspace_model_evaluation_receipts(user_key, operation, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_predictive_model_receipts TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_model_evaluation_receipts TO sc_workspace;
