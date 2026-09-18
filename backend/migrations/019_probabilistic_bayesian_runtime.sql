BEGIN;
CREATE TABLE IF NOT EXISTS workspace_probabilistic_inference_receipts (
 user_key varchar(128) NOT NULL, receipt_id varchar(96) NOT NULL, polyglot_receipt_id varchar(96) NOT NULL,
 job_id varchar(96) NOT NULL, execution_run_id varchar(96) NOT NULL DEFAULT '', runtime varchar(96) NOT NULL,
 operation varchar(160) NOT NULL, inference_kind varchar(96) NOT NULL DEFAULT '', request_fingerprint varchar(64) NOT NULL DEFAULT '',
 posterior_json jsonb NOT NULL DEFAULT '{}'::jsonb, interval_json jsonb NOT NULL DEFAULT '{}'::jsonb,
 result_artifact_id varchar(160) NOT NULL, result_sha256 varchar(64) NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY (user_key, receipt_id));
CREATE INDEX IF NOT EXISTS workspace_probabilistic_inference_receipts_user_created_idx ON workspace_probabilistic_inference_receipts(user_key, created_at DESC);
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_probabilistic_inference_receipts TO sc_workspace;
COMMIT;
