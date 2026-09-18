BEGIN;
CREATE TABLE IF NOT EXISTS workspace_local_first_sync_receipts (
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  envelope_id varchar(96) NOT NULL,
  operation_id varchar(160) NOT NULL,
  device_id varchar(160) NOT NULL,
  object_kind varchar(32) NOT NULL,
  object_id varchar(160) NOT NULL,
  base_revision integer NOT NULL DEFAULT 0,
  server_revision integer NOT NULL DEFAULT 0,
  status varchar(32) NOT NULL,
  request_fingerprint varchar(64) NOT NULL,
  canonical_fingerprint varchar(128) NOT NULL DEFAULT '',
  envelope_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  result_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_sync_envelope_unique_idx ON workspace_local_first_sync_receipts(user_key,envelope_id);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_sync_operation_unique_idx ON workspace_local_first_sync_receipts(user_key,operation_id);
CREATE INDEX IF NOT EXISTS workspace_sync_object_idx ON workspace_local_first_sync_receipts(user_key,object_kind,object_id,created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_local_first_sync_receipts TO sc_workspace;
COMMIT;
