BEGIN;

CREATE TABLE IF NOT EXISTS workspace_compute_execution_receipts (
    user_key VARCHAR(128) NOT NULL,
    receipt_id VARCHAR(96) NOT NULL,
    job_id VARCHAR(96) NOT NULL,
    execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
    operation VARCHAR(160) NOT NULL,
    engine VARCHAR(64) NOT NULL,
    engine_version VARCHAR(64) NOT NULL DEFAULT '',
    request_fingerprint VARCHAR(64) NOT NULL,
    result_artifact_id VARCHAR(160) NOT NULL,
    result_sha256 VARCHAR(64) NOT NULL,
    result_bytes BIGINT NOT NULL DEFAULT 0,
    wall_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, receipt_id)
);

CREATE INDEX IF NOT EXISTS workspace_compute_execution_receipts_job_idx
    ON workspace_compute_execution_receipts (user_key, job_id);
CREATE INDEX IF NOT EXISTS workspace_compute_execution_receipts_run_idx
    ON workspace_compute_execution_receipts (user_key, execution_run_id);

GRANT USAGE ON SCHEMA public TO sc_workspace;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE workspace_compute_execution_receipts TO sc_workspace;

COMMIT;
