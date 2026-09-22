BEGIN;
CREATE TABLE IF NOT EXISTS workspace_platform_core_research_sessions (
  user_key varchar(128) NOT NULL,
  project_id varchar(160) NOT NULL,
  core_session_id varchar(96) NOT NULL,
  core_session_key varchar(180) NOT NULL,
  core_contract varchar(160) NOT NULL,
  core_release varchar(32) NOT NULL DEFAULT '3.0.0',
  core_product_binding_id varchar(96) NOT NULL DEFAULT '',
  status varchar(32) NOT NULL DEFAULT 'active',
  project_revision integer NOT NULL DEFAULT 0,
  project_fingerprint varchar(128) NOT NULL DEFAULT '',
  core_session_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  last_error text NOT NULL DEFAULT '',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(user_key,project_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_platform_core_session_user_session_idx ON workspace_platform_core_research_sessions(user_key,core_session_id);
CREATE INDEX IF NOT EXISTS workspace_platform_core_session_created_idx ON workspace_platform_core_research_sessions(user_key,created_at DESC);

CREATE TABLE IF NOT EXISTS workspace_platform_core_runtime_receipts (
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  project_id varchar(160) NOT NULL,
  core_session_id varchar(96) NOT NULL,
  action varchar(64) NOT NULL,
  binding_kind varchar(48) NOT NULL DEFAULT '',
  workspace_ref varchar(1000) NOT NULL DEFAULT '',
  core_ref varchar(1000) NOT NULL DEFAULT '',
  status varchar(32) NOT NULL DEFAULT 'recorded',
  request_fingerprint varchar(64) NOT NULL,
  response_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(user_key,receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_platform_core_receipt_project_idx ON workspace_platform_core_runtime_receipts(user_key,project_id,created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_platform_core_receipt_session_idx ON workspace_platform_core_runtime_receipts(user_key,core_session_id,created_at DESC);

GRANT SELECT,INSERT,UPDATE,DELETE ON workspace_platform_core_research_sessions TO sc_workspace;
GRANT SELECT,INSERT,UPDATE,DELETE ON workspace_platform_core_runtime_receipts TO sc_workspace;
COMMIT;
