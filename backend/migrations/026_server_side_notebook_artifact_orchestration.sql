CREATE TABLE IF NOT EXISTS workspace_notebook_execution_plans (
  user_key varchar(128) NOT NULL, plan_id varchar(96) NOT NULL, notebook_id varchar(160) NOT NULL, notebook_revision integer NOT NULL,
  notebook_fingerprint varchar(128) NOT NULL DEFAULT '', project_id varchar(160) NOT NULL DEFAULT '', status varchar(32) NOT NULL DEFAULT 'ready',
  request_fingerprint varchar(64) NOT NULL, dependency_graph_json jsonb NOT NULL DEFAULT '{}'::jsonb, artifact_bindings_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  steps_json jsonb NOT NULL DEFAULT '[]'::jsonb, job_ids_json jsonb NOT NULL DEFAULT '[]'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_key, plan_id)
);
CREATE INDEX IF NOT EXISTS workspace_notebook_execution_plans_notebook_idx ON workspace_notebook_execution_plans(user_key, notebook_id, created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_notebook_execution_plans_status_idx ON workspace_notebook_execution_plans(user_key, status, updated_at DESC);
CREATE TABLE IF NOT EXISTS workspace_notebook_orchestration_receipts (
  user_key varchar(128) NOT NULL, receipt_id varchar(96) NOT NULL, plan_id varchar(96) NOT NULL, action varchar(64) NOT NULL, status varchar(32) NOT NULL,
  request_fingerprint varchar(64) NOT NULL, details_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_key, receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_notebook_orchestration_receipts_plan_idx ON workspace_notebook_orchestration_receipts(user_key, plan_id, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_notebook_execution_plans TO sc_workspace;
GRANT SELECT, INSERT ON workspace_notebook_orchestration_receipts TO sc_workspace;
