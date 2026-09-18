CREATE TABLE IF NOT EXISTS workspace_command_receipts (
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  command_id varchar(96) NOT NULL,
  idempotency_key varchar(160) NOT NULL DEFAULT '',
  command varchar(96) NOT NULL,
  target_kind varchar(32) NOT NULL DEFAULT '',
  target_id varchar(160) NOT NULL DEFAULT '',
  status varchar(32) NOT NULL DEFAULT 'applied',
  request_fingerprint varchar(64) NOT NULL,
  linked_mutation_receipt_id varchar(96) NOT NULL DEFAULT '',
  result_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_command_receipts_user_created_idx ON workspace_command_receipts(user_key, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_command_receipts_target_idx ON workspace_command_receipts(user_key, target_kind, target_id, created_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_command_receipts_idempotency_idx ON workspace_command_receipts(user_key, idempotency_key) WHERE idempotency_key <> '';
GRANT SELECT, INSERT ON workspace_command_receipts TO sc_workspace;
