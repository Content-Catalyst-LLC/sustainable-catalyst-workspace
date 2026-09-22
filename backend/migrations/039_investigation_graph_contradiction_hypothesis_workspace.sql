BEGIN;
CREATE TABLE IF NOT EXISTS workspace_investigation_hypothesis_sets (
 user_key VARCHAR(128) NOT NULL,
 hypothesis_set_id VARCHAR(160) NOT NULL,
 project_id VARCHAR(160) NOT NULL,
 title VARCHAR(500) NOT NULL,
 description TEXT NOT NULL DEFAULT '',
 question_statement_id VARCHAR(160) NOT NULL DEFAULT '',
 hypothesis_ids_json JSONB NOT NULL DEFAULT '[]'::jsonb,
 status VARCHAR(32) NOT NULL DEFAULT 'open',
 set_fingerprint VARCHAR(64) NOT NULL,
 metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (user_key,hypothesis_set_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_hypothesis_set_project_idx ON workspace_investigation_hypothesis_sets (user_key,project_id,updated_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS workspace_investigation_hypothesis_set_fingerprint_idx ON workspace_investigation_hypothesis_sets (user_key,project_id,set_fingerprint);
CREATE TABLE IF NOT EXISTS workspace_investigation_graph_snapshots (
 user_key VARCHAR(128) NOT NULL,
 snapshot_id VARCHAR(96) NOT NULL,
 project_id VARCHAR(160) NOT NULL,
 graph_fingerprint VARCHAR(64) NOT NULL,
 contradiction_cluster_count INTEGER NOT NULL DEFAULT 0,
 hypothesis_set_count INTEGER NOT NULL DEFAULT 0,
 node_count INTEGER NOT NULL DEFAULT 0,
 edge_count INTEGER NOT NULL DEFAULT 0,
 graph_json JSONB NOT NULL DEFAULT '{}'::jsonb,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (user_key,snapshot_id)
);
CREATE INDEX IF NOT EXISTS workspace_investigation_graph_snapshot_project_idx ON workspace_investigation_graph_snapshots (user_key,project_id,created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_investigation_graph_snapshot_fingerprint_idx ON workspace_investigation_graph_snapshots (user_key,graph_fingerprint);
DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='sc_workspace') THEN
  GRANT SELECT,INSERT,UPDATE ON workspace_investigation_hypothesis_sets TO sc_workspace;
  GRANT SELECT,INSERT ON workspace_investigation_graph_snapshots TO sc_workspace;
 END IF;
END $$;
COMMIT;
