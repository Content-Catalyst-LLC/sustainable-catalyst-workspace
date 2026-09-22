-- Workspace v3.5.0 — Catalyst Analytics R Runtime Adapter
CREATE TABLE IF NOT EXISTS workspace_analytical_provider_receipts (
  user_key VARCHAR(128) NOT NULL,
  receipt_id VARCHAR(96) NOT NULL,
  request_key VARCHAR(255) NOT NULL,
  provider_key VARCHAR(96) NOT NULL,
  provider_version VARCHAR(32) NOT NULL,
  core_contract VARCHAR(160) NOT NULL,
  analysis_type VARCHAR(128) NOT NULL,
  method_ref VARCHAR(160) NOT NULL,
  status VARCHAR(32) NOT NULL,
  external_execution_ref VARCHAR(255) NOT NULL,
  environment_ref VARCHAR(255) NOT NULL,
  request_fingerprint VARCHAR(64) NOT NULL,
  result_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
  request_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  result_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  error TEXT NOT NULL DEFAULT '',
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ NULL,
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_analytical_provider_receipts_request_idx
  ON workspace_analytical_provider_receipts (user_key, request_key, started_at DESC);
CREATE INDEX IF NOT EXISTS workspace_analytical_provider_receipts_provider_idx
  ON workspace_analytical_provider_receipts (user_key, provider_key, provider_version, started_at DESC);
CREATE INDEX IF NOT EXISTS workspace_analytical_provider_receipts_execution_idx
  ON workspace_analytical_provider_receipts (user_key, external_execution_ref);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_analytical_provider_receipts TO sc_workspace;
