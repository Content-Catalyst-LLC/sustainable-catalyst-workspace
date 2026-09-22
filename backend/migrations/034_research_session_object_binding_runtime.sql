-- Workspace v3.3.0 — Research Session & Object Binding Runtime
CREATE TABLE IF NOT EXISTS workspace_research_session_object_bindings (
  user_key VARCHAR(128) NOT NULL,
  binding_id VARCHAR(96) NOT NULL,
  project_id VARCHAR(160) NOT NULL,
  core_session_id VARCHAR(96) NOT NULL,
  binding_type VARCHAR(48) NOT NULL,
  workspace_ref VARCHAR(1000) NOT NULL,
  workspace_kind VARCHAR(96) NOT NULL DEFAULT '',
  workspace_object_id VARCHAR(160) NOT NULL DEFAULT '',
  workspace_revision INTEGER NOT NULL DEFAULT 0,
  workspace_fingerprint VARCHAR(128) NOT NULL DEFAULT '',
  core_binding_id VARCHAR(96) NOT NULL DEFAULT '',
  role VARCHAR(120) NOT NULL DEFAULT 'context',
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  request_fingerprint VARCHAR(64) NOT NULL DEFAULT '',
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  response_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_key, binding_id)
);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_research_session_binding_unique_idx
  ON workspace_research_session_object_bindings (user_key, project_id, binding_type, workspace_ref);
CREATE INDEX IF NOT EXISTS workspace_research_session_binding_project_idx
  ON workspace_research_session_object_bindings (user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_research_session_binding_session_idx
  ON workspace_research_session_object_bindings (user_key, core_session_id, updated_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_research_session_object_bindings TO sc_workspace;
