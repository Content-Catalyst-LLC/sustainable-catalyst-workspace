CREATE TABLE IF NOT EXISTS workspace_visualization_specs (
  user_key varchar(128) NOT NULL,
  visualization_id varchar(96) NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  title text NOT NULL DEFAULT 'Visualization',
  revision integer NOT NULL DEFAULT 1,
  spec_fingerprint varchar(64) NOT NULL,
  scene_kind varchar(32) NOT NULL DEFAULT 'single',
  view_count integer NOT NULL DEFAULT 0,
  source_count integer NOT NULL DEFAULT 0,
  spec_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, visualization_id)
);
CREATE INDEX IF NOT EXISTS workspace_visualization_specs_project_idx ON workspace_visualization_specs(user_key, project_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS workspace_visualization_specs_fingerprint_idx ON workspace_visualization_specs(user_key, spec_fingerprint);

CREATE TABLE IF NOT EXISTS workspace_visualization_spec_revisions (
  user_key varchar(128) NOT NULL,
  visualization_id varchar(96) NOT NULL,
  revision integer NOT NULL,
  project_id varchar(160) NOT NULL DEFAULT '',
  title text NOT NULL DEFAULT 'Visualization',
  spec_fingerprint varchar(64) NOT NULL,
  scene_kind varchar(32) NOT NULL DEFAULT 'single',
  view_count integer NOT NULL DEFAULT 0,
  source_count integer NOT NULL DEFAULT 0,
  operation_id varchar(160) NOT NULL DEFAULT '',
  spec_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, visualization_id, revision)
);
CREATE INDEX IF NOT EXISTS workspace_visualization_spec_revisions_lookup_idx ON workspace_visualization_spec_revisions(user_key, visualization_id, revision DESC);

CREATE TABLE IF NOT EXISTS workspace_visualization_spec_receipts (
  user_key varchar(128) NOT NULL,
  receipt_id varchar(96) NOT NULL,
  visualization_id varchar(96) NOT NULL,
  action varchar(64) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'applied',
  revision integer NOT NULL DEFAULT 0,
  spec_fingerprint varchar(64) NOT NULL DEFAULT '',
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_visualization_spec_receipts_viz_idx ON workspace_visualization_spec_receipts(user_key, visualization_id, created_at DESC);

GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_visualization_specs TO sc_workspace;
GRANT SELECT, INSERT ON workspace_visualization_spec_revisions TO sc_workspace;
GRANT SELECT, INSERT ON workspace_visualization_spec_receipts TO sc_workspace;
