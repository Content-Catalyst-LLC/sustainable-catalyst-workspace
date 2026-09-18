CREATE TABLE IF NOT EXISTS workspace_reliability_analysis_receipts (
  user_key VARCHAR(128) NOT NULL,
  receipt_id VARCHAR(96) NOT NULL,
  polyglot_receipt_id VARCHAR(96) NOT NULL,
  job_id VARCHAR(96) NOT NULL,
  execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
  runtime VARCHAR(96) NOT NULL,
  operation VARCHAR(160) NOT NULL,
  analysis_kind VARCHAR(96) NOT NULL DEFAULT '',
  model_kind VARCHAR(96) NOT NULL DEFAULT '',
  sample_count INTEGER NOT NULL DEFAULT 0,
  event_count INTEGER NOT NULL DEFAULT 0,
  horizon DOUBLE PRECISION NOT NULL DEFAULT 0,
  request_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  result_artifact_id VARCHAR(160) NOT NULL,
  result_sha256 VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_reliability_analysis_receipts_user_created_idx ON workspace_reliability_analysis_receipts(user_key, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_reliability_analysis_receipts_job_idx ON workspace_reliability_analysis_receipts(user_key, job_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_reliability_analysis_receipts TO sc_workspace;
