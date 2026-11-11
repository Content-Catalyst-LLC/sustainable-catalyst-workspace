-- RH-PROD-05.1: fail-closed durable revocation foundation.
-- Renumbered from 051 (SC-AUTH-01 G2): 051-053 are taken on release/sc-release-01-rc1.
-- This is an additive migration. Do not execute on production without an
-- authorized, backed-up, tested change window.
BEGIN;

CREATE TABLE IF NOT EXISTS workspace_revoked_sessions (
    token_fingerprint varchar(64) PRIMARY KEY,
    user_key varchar(128) NOT NULL,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_workspace_revoked_sessions_expiry
    ON workspace_revoked_sessions (expires_at);

COMMIT;
