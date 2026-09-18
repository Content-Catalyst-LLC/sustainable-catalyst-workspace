CREATE TABLE IF NOT EXISTS workspace_domain_mutation_receipts (
  user_key VARCHAR(128) NOT NULL,
  receipt_id VARCHAR(96) NOT NULL,
  object_kind VARCHAR(32) NOT NULL,
  object_id VARCHAR(160) NOT NULL,
  command VARCHAR(96) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'applied',
  from_revision INTEGER NOT NULL DEFAULT 0,
  to_revision INTEGER NOT NULL DEFAULT 0,
  request_fingerprint VARCHAR(64) NOT NULL,
  canonical_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
  validation_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  policy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_domain_mutation_receipts_user_created_idx
  ON workspace_domain_mutation_receipts(user_key, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_domain_mutation_receipts_object_idx
  ON workspace_domain_mutation_receipts(user_key, object_kind, object_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_domain_mutation_receipts_command_idx
  ON workspace_domain_mutation_receipts(user_key, command, created_at DESC);
GRANT SELECT, INSERT ON workspace_domain_mutation_receipts TO sc_workspace;
