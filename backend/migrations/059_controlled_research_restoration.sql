-- Additive only. Deployment and migration require separate approval.
BEGIN;
CREATE TABLE IF NOT EXISTS workspace_recovery_restoration_receipts (
    user_key varchar(128) NOT NULL,
    batch_id varchar(96) NOT NULL,
    project_id varchar(160) NOT NULL,
    manifest_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, batch_id)
);
COMMIT;
-- Rollback application first. Retain this audit table and all original records.
-- No destructive DOWN migration is provided.
