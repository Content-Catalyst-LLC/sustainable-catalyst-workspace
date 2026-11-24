-- SC-MODEL-01: owner-issued Research export grants and run withdrawals.
CREATE TABLE IF NOT EXISTS workspace_research_export_grants (
    grant_id VARCHAR(96) PRIMARY KEY,
    user_key VARCHAR(128) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    run_id VARCHAR(96) NOT NULL,
    audience VARCHAR(64) NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL,
    export_count INTEGER NOT NULL DEFAULT 0,
    last_export_sha256 VARCHAR(64) NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS ix_workspace_research_export_grants_user_key ON workspace_research_export_grants (user_key);

CREATE TABLE IF NOT EXISTS workspace_research_export_withdrawals (
    user_key VARCHAR(128) NOT NULL,
    run_id VARCHAR(96) NOT NULL,
    project_id VARCHAR(160) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    notice_sha256 VARCHAR(64) NOT NULL,
    withdrawn_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_key, run_id)
);
