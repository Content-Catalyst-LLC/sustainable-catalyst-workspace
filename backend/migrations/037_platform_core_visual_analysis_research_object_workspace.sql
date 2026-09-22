-- Sustainable Catalyst Workspace v3.6.0
-- Platform Core Visual Analysis & Research Object Workspace

CREATE TABLE IF NOT EXISTS workspace_visual_research_workspace_snapshots (
    user_key VARCHAR(128) NOT NULL,
    snapshot_id VARCHAR(96) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    visualization_id VARCHAR(160) NOT NULL DEFAULT '',
    graph_fingerprint VARCHAR(64) NOT NULL,
    visualization_count INTEGER NOT NULL DEFAULT 0,
    binding_count INTEGER NOT NULL DEFAULT 0,
    node_count INTEGER NOT NULL DEFAULT 0,
    edge_count INTEGER NOT NULL DEFAULT 0,
    context_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_key, snapshot_id)
);

CREATE INDEX IF NOT EXISTS workspace_visual_research_workspace_project_idx
    ON workspace_visual_research_workspace_snapshots (user_key, project_id, created_at DESC);

CREATE INDEX IF NOT EXISTS workspace_visual_research_workspace_visualization_idx
    ON workspace_visual_research_workspace_snapshots (user_key, visualization_id, created_at DESC);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sc_workspace') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_visual_research_workspace_snapshots TO sc_workspace;
    END IF;
END $$;
