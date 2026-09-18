CREATE TABLE IF NOT EXISTS workspace_optimization_receipts (
  user_key VARCHAR(128) NOT NULL,
  receipt_id VARCHAR(96) NOT NULL,
  polyglot_receipt_id VARCHAR(96) NOT NULL,
  job_id VARCHAR(96) NOT NULL,
  execution_run_id VARCHAR(96) NOT NULL DEFAULT '',
  runtime VARCHAR(96) NOT NULL,
  operation VARCHAR(160) NOT NULL,
  optimization_kind VARCHAR(96) NOT NULL DEFAULT '',
  objective_kind VARCHAR(64) NOT NULL DEFAULT '',
  direction VARCHAR(16) NOT NULL DEFAULT 'minimize',
  best_value DOUBLE PRECISION NOT NULL DEFAULT 0,
  best_parameters_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  evaluation_count INTEGER NOT NULL DEFAULT 0,
  iteration_count INTEGER NOT NULL DEFAULT 0,
  random_seed INTEGER NOT NULL DEFAULT 0,
  converged BOOLEAN NOT NULL DEFAULT FALSE,
  request_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
  result_artifact_id VARCHAR(160) NOT NULL,
  result_sha256 VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_optimization_receipts_user_created_idx ON workspace_optimization_receipts(user_key, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_optimization_receipts_job_idx ON workspace_optimization_receipts(user_key, job_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_optimization_receipts TO sc_workspace;
