-- Workspace v3.4.0 — Scientific Execution & Provenance Workspace
CREATE TABLE IF NOT EXISTS workspace_scientific_execution_provenance_snapshots (
  user_key VARCHAR(128) NOT NULL,
  snapshot_id VARCHAR(96) NOT NULL,
  project_id VARCHAR(160) NOT NULL,
  run_id VARCHAR(96) NOT NULL DEFAULT '',
  provenance_fingerprint VARCHAR(64) NOT NULL,
  execution_count INTEGER NOT NULL DEFAULT 0,
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_execution_provenance_project_idx
  ON workspace_scientific_execution_provenance_snapshots (user_key, project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_provenance_run_idx
  ON workspace_scientific_execution_provenance_snapshots (user_key, run_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_execution_provenance_fingerprint_idx
  ON workspace_scientific_execution_provenance_snapshots (user_key, provenance_fingerprint);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_scientific_execution_provenance_snapshots TO sc_workspace;
