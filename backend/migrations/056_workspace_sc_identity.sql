-- SC-AUTH-02: Sustainable Catalyst Identity links and IdP-session revocation.
-- Additive only. Applied by app.migrate_security after 055; do not run on
-- production without an authorized, backed-up, tested change window.
BEGIN;

-- Explicit, audited mapping from a Platform Core identity (issuer, subject)
-- to the existing Workspace user_key. Projects are never rekeyed; one active
-- subject per user_key per issuer; ambiguous links are refused by the CLI.
CREATE TABLE IF NOT EXISTS workspace_identity_links (
    issuer varchar(255) NOT NULL,
    subject varchar(255) NOT NULL,
    user_key varchar(128) NOT NULL,
    status varchar(16) NOT NULL DEFAULT 'active',
    link_method varchar(32) NOT NULL,
    evidence_sha256 varchar(64),
    created_by varchar(128) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (issuer, subject),
    CONSTRAINT uq_workspace_identity_links_user UNIQUE (issuer, user_key),
    CONSTRAINT ck_workspace_identity_links_status CHECK (status IN ('active', 'suspended')),
    CONSTRAINT ck_workspace_identity_links_method CHECK (link_method IN ('verified-existing-owner', 'new-enrollment'))
);

CREATE TABLE IF NOT EXISTS workspace_identity_link_audit (
    id bigserial PRIMARY KEY,
    action varchar(32) NOT NULL,
    issuer varchar(255) NOT NULL,
    subject varchar(255) NOT NULL,
    user_key varchar(128) NOT NULL,
    actor varchar(128) NOT NULL,
    reason varchar(500) NOT NULL,
    evidence_sha256 varchar(64),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Back-channel logout: every Workspace session bound to a revoked IdP session.
CREATE TABLE IF NOT EXISTS workspace_revoked_idp_sessions (
    issuer varchar(255) NOT NULL,
    idp_sid varchar(255) NOT NULL,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (issuer, idp_sid)
);
CREATE INDEX IF NOT EXISTS ix_workspace_revoked_idp_sessions_expiry ON workspace_revoked_idp_sessions (expires_at);

-- IdP logout-token jti values can exceed the 055 nonce width.
ALTER TABLE workspace_used_nonces ALTER COLUMN nonce TYPE varchar(128);

COMMIT;
