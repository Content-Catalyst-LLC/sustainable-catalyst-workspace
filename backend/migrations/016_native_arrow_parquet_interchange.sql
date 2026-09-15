CREATE TABLE IF NOT EXISTS workspace_interchange_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    operation VARCHAR(160) NOT NULL,
    source_format VARCHAR(64) NOT NULL DEFAULT '',
    result_format VARCHAR(64) NOT NULL DEFAULT '',
    source_artifact_id VARCHAR(160) NOT NULL DEFAULT '',
    result_artifact_id VARCHAR(160) NOT NULL DEFAULT '',
    source_sha256 VARCHAR(64) NOT NULL DEFAULT '',
    result_sha256 VARCHAR(64) NOT NULL DEFAULT '',
    schema_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
    row_count INTEGER NOT NULL DEFAULT 0,
    column_count INTEGER NOT NULL DEFAULT 0,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_interchange_receipts_job_idx ON workspace_interchange_receipts(user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_interchange_receipts_schema_idx ON workspace_interchange_receipts(user_key, schema_fingerprint, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_interchange_receipts TO sc_workspace;
