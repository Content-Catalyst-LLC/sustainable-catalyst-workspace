BEGIN;
CREATE TABLE IF NOT EXISTS workspace_cross_product_research_handoffs (
  user_key varchar(128) NOT NULL, handoff_id varchar(96) NOT NULL, project_id varchar(160) NOT NULL DEFAULT '',
  source_product varchar(96) NOT NULL, destination_product varchar(96) NOT NULL, intent varchar(64) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'prepared', request_fingerprint varchar(64) NOT NULL, package_fingerprint varchar(64) NOT NULL,
  object_refs_json jsonb NOT NULL DEFAULT '[]'::jsonb, context_json jsonb NOT NULL DEFAULT '{}'::jsonb, destination_result_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(), accepted_at timestamptz NULL, PRIMARY KEY(user_key,handoff_id)
);
CREATE INDEX IF NOT EXISTS workspace_handoff_project_idx ON workspace_cross_product_research_handoffs(user_key,project_id,created_at DESC);
CREATE INDEX IF NOT EXISTS workspace_handoff_route_idx ON workspace_cross_product_research_handoffs(user_key,source_product,destination_product,created_at DESC);
CREATE TABLE IF NOT EXISTS workspace_cross_product_research_handoff_receipts (
  user_key varchar(128) NOT NULL, receipt_id varchar(96) NOT NULL, handoff_id varchar(96) NOT NULL, action varchar(32) NOT NULL,
  source_product varchar(96) NOT NULL, destination_product varchar(96) NOT NULL, status varchar(32) NOT NULL, package_fingerprint varchar(64) NOT NULL,
  details_json jsonb NOT NULL DEFAULT '{}'::jsonb, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(user_key,receipt_id)
);
CREATE INDEX IF NOT EXISTS workspace_handoff_receipt_handoff_idx ON workspace_cross_product_research_handoff_receipts(user_key,handoff_id,created_at DESC);
GRANT SELECT,INSERT,UPDATE,DELETE ON workspace_cross_product_research_handoffs TO sc_workspace;
GRANT SELECT,INSERT,UPDATE,DELETE ON workspace_cross_product_research_handoff_receipts TO sc_workspace;
COMMIT;
