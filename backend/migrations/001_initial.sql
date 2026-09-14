-- Sustainable Catalyst Workspace Backend v2.1.0
-- Reference DDL. The container also initializes these tables idempotently through SQLAlchemy metadata.
CREATE TABLE IF NOT EXISTS workspace_project_heads (
  user_key varchar(128) NOT NULL,
  project_id varchar(160) NOT NULL,
  title text NOT NULL,
  client_updated_at varchar(96) NOT NULL DEFAULT '',
  backed_up_at timestamptz NOT NULL,
  fingerprint varchar(64) NOT NULL,
  project_fingerprint varchar(64) NOT NULL,
  revision integer NOT NULL,
  storage_mode varchar(32) NOT NULL,
  bytes bigint NOT NULL,
  object_count integer NOT NULL DEFAULT 0,
  last_operation_id varchar(160) NOT NULL DEFAULT '',
  package jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, project_id)
);
CREATE TABLE IF NOT EXISTS workspace_project_revisions (
  user_key varchar(128) NOT NULL,
  project_id varchar(160) NOT NULL,
  revision integer NOT NULL,
  title text NOT NULL,
  backed_up_at timestamptz NOT NULL,
  fingerprint varchar(64) NOT NULL,
  project_fingerprint varchar(64) NOT NULL,
  storage_mode varchar(32) NOT NULL,
  bytes bigint NOT NULL,
  object_count integer NOT NULL DEFAULT 0,
  operation_id varchar(160) NOT NULL DEFAULT '',
  package jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, project_id, revision)
);
CREATE INDEX IF NOT EXISTS idx_workspace_project_heads_user_backed_up ON workspace_project_heads (user_key, backed_up_at DESC);
CREATE INDEX IF NOT EXISTS idx_workspace_project_revisions_lookup ON workspace_project_revisions (user_key, project_id, revision DESC);
CREATE TABLE IF NOT EXISTS workspace_notebook_heads (
  user_key varchar(128) NOT NULL,
  notebook_id varchar(160) NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  title text NOT NULL,
  client_updated_at varchar(96) NOT NULL DEFAULT '',
  backed_up_at timestamptz NOT NULL,
  fingerprint varchar(64) NOT NULL,
  notebook_fingerprint varchar(64) NOT NULL,
  revision integer NOT NULL,
  storage_mode varchar(32) NOT NULL,
  bytes bigint NOT NULL,
  last_operation_id varchar(160) NOT NULL DEFAULT '',
  package jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, notebook_id)
);
CREATE TABLE IF NOT EXISTS workspace_notebook_revisions (
  user_key varchar(128) NOT NULL,
  notebook_id varchar(160) NOT NULL,
  revision integer NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  title text NOT NULL,
  backed_up_at timestamptz NOT NULL,
  fingerprint varchar(64) NOT NULL,
  notebook_fingerprint varchar(64) NOT NULL,
  storage_mode varchar(32) NOT NULL,
  bytes bigint NOT NULL,
  operation_id varchar(160) NOT NULL DEFAULT '',
  package jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, notebook_id, revision)
);
CREATE INDEX IF NOT EXISTS idx_workspace_notebook_heads_user_backed_up ON workspace_notebook_heads (user_key, backed_up_at DESC);
