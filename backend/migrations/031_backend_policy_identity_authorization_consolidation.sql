BEGIN;
CREATE TABLE IF NOT EXISTS workspace_authorization_decision_receipts(
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  principal_id varchar(192) NOT NULL,
  principal_type varchar(64) NOT NULL,
  service_principal varchar(96) NOT NULL,
  action varchar(96) NOT NULL,
  resource_kind varchar(64) NOT NULL,
  resource_id varchar(160) NOT NULL DEFAULT '',
  project_id varchar(160) NOT NULL DEFAULT '',
  effect varchar(16) NOT NULL,
  reason varchar(96) NOT NULL,
  policy_id varchar(96) NOT NULL,
  policy_revision integer NOT NULL,
  decision_fingerprint varchar(64) NOT NULL,
  context_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(user_key,receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_authorization_decision_user_created_idx ON workspace_authorization_decision_receipts(user_key,created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_authorization_decision_principal_idx ON workspace_authorization_decision_receipts(user_key,principal_id,created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_authorization_decision_resource_idx ON workspace_authorization_decision_receipts(user_key,resource_kind,resource_id,created_at DESC);
GRANT SELECT,INSERT,UPDATE,DELETE ON workspace_authorization_decision_receipts TO sc_workspace;
COMMIT;
