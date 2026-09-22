-- Workspace v3.2.0 — Unified Research Project Context
CREATE TABLE IF NOT EXISTS workspace_unified_research_context_snapshots (
  user_key VARCHAR(128) NOT NULL,
  snapshot_id VARCHAR(96) NOT NULL,
  project_id VARCHAR(160) NOT NULL,
  project_revision INTEGER NOT NULL DEFAULT 0,
  project_fingerprint VARCHAR(128) NOT NULL DEFAULT '',
  context_fingerprint VARCHAR(64) NOT NULL,
  core_session_id VARCHAR(96) NOT NULL DEFAULT '',
  component_counts_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_research_context_project_idx
  ON workspace_unified_research_context_snapshots (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_research_context_fingerprint_idx
  ON workspace_unified_research_context_snapshots (user_key, context_fingerprint);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_unified_research_context_snapshots TO sc_workspace;
