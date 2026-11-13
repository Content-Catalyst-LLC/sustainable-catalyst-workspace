-- SC-AUTH-01: replay stores, operator revocation and audit. Additive only.
-- Applied by app.migrate_security after 054; do not run on production
-- without an authorized, backed-up, tested change window.
BEGIN;

-- Single-use request nonces for private introspection and WordPress bridge
-- assertions. Rows are kept until the bound credential expires.
CREATE TABLE IF NOT EXISTS workspace_used_nonces (
    scope varchar(32) NOT NULL,
    nonce varchar(64) NOT NULL,
    expires_at timestamptz NOT NULL,
    used_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (scope, nonce)
);
CREATE INDEX IF NOT EXISTS ix_workspace_used_nonces_expiry ON workspace_used_nonces (expires_at);

-- Operator revocation of one session by its server-issued identifier.
CREATE TABLE IF NOT EXISTS workspace_revoked_session_ids (
    session_id varchar(32) PRIMARY KEY,
    user_key varchar(128) NOT NULL,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz NOT NULL DEFAULT now()
);

-- Operator revocation of every session a user was issued at or before not_before.
CREATE TABLE IF NOT EXISTS workspace_session_user_cutoffs (
    user_key varchar(128) PRIMARY KEY,
    not_before timestamptz NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workspace_session_revocation_audit (
    id bigserial PRIMARY KEY,
    action varchar(32) NOT NULL,
    user_key varchar(128) NOT NULL,
    session_id varchar(32),
    actor varchar(128) NOT NULL,
    reason varchar(500) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMIT;
