-- Sustainable Catalyst Workspace Backend v2.2.0
-- Additive persistence migration, object storage metadata, and recovery snapshots.
CREATE TABLE IF NOT EXISTS workspace_migration_receipts (
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  source varchar(96) NOT NULL,
  source_fingerprint varchar(64) NOT NULL,
  project_count integer NOT NULL DEFAULT 0,
  notebook_count integer NOT NULL DEFAULT 0,
  imported_project_count integer NOT NULL DEFAULT 0,
  imported_notebook_count integer NOT NULL DEFAULT 0,
  skipped_count integer NOT NULL DEFAULT 0,
  status varchar(32) NOT NULL DEFAULT 'complete',
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS idx_workspace_migration_receipts_source
  ON workspace_migration_receipts (user_key, source_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_artifact_heads (
  user_key varchar(128) NOT NULL,
  artifact_id varchar(160) NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  filename text NOT NULL DEFAULT 'artifact',
  media_type varchar(255) NOT NULL DEFAULT 'application/octet-stream',
  bytes bigint NOT NULL,
  sha256 varchar(64) NOT NULL,
  storage_key text NOT NULL,
  revision integer NOT NULL DEFAULT 1,
  metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, artifact_id)
);
CREATE INDEX IF NOT EXISTS idx_workspace_artifact_heads_user_updated
  ON workspace_artifact_heads (user_key, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_workspace_artifact_heads_sha256
  ON workspace_artifact_heads (sha256);

CREATE TABLE IF NOT EXISTS workspace_artifact_revisions (
  user_key varchar(128) NOT NULL,
  artifact_id varchar(160) NOT NULL,
  revision integer NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  filename text NOT NULL DEFAULT 'artifact',
  media_type varchar(255) NOT NULL DEFAULT 'application/octet-stream',
  bytes bigint NOT NULL,
  sha256 varchar(64) NOT NULL,
  storage_key text NOT NULL,
  metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, artifact_id, revision)
);

CREATE TABLE IF NOT EXISTS workspace_recovery_snapshots (
  user_key varchar(128) NOT NULL,
  snapshot_id varchar(96) NOT NULL,
  reason varchar(160) NOT NULL DEFAULT 'manual',
  fingerprint varchar(64) NOT NULL,
  project_count integer NOT NULL DEFAULT 0,
  notebook_count integer NOT NULL DEFAULT 0,
  artifact_count integer NOT NULL DEFAULT 0,
  manifest jsonb NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS idx_workspace_recovery_snapshots_user_created
  ON workspace_recovery_snapshots (user_key, created_at DESC);
