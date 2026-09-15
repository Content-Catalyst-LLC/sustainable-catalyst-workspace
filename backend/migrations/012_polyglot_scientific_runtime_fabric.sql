CREATE TABLE IF NOT EXISTS workspace_polyglot_execution_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    language VARCHAR(32) NOT NULL,
    runtime VARCHAR(96) NOT NULL,
    operation VARCHAR(160) NOT NULL,
    request_fingerprint VARCHAR(64) NOT NULL,
    result_artifact_id VARCHAR(160) NOT NULL,
    result_sha256 VARCHAR(64) NOT NULL,
    result_bytes BIGINT NOT NULL DEFAULT 0,
    transport VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'succeeded',
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_polyglot_receipts_job_idx ON workspace_polyglot_execution_receipts(user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_polyglot_receipts_language_idx ON workspace_polyglot_execution_receipts(user_key, language, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_polyglot_execution_receipts TO sc_workspace;
