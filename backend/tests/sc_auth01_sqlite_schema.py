"""SQLite equivalents of migrations 055/056 tables for isolated SC-AUTH-01/02 unit tests."""
from sqlalchemy import text

AUTH_HARDENING_TABLES = (
    "CREATE TABLE IF NOT EXISTS workspace_used_nonces (scope varchar(32) NOT NULL, nonce varchar(64) NOT NULL, "
    "expires_at timestamp NOT NULL, used_at timestamp DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (scope, nonce))",
    "CREATE TABLE IF NOT EXISTS workspace_revoked_session_ids (session_id varchar(32) PRIMARY KEY, "
    "user_key varchar(128) NOT NULL, expires_at timestamp NOT NULL, revoked_at timestamp DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS workspace_session_user_cutoffs (user_key varchar(128) PRIMARY KEY, "
    "not_before timestamp NOT NULL, updated_at timestamp DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS workspace_session_revocation_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "action varchar(32) NOT NULL, user_key varchar(128) NOT NULL, session_id varchar(32), actor varchar(128) NOT NULL, "
    "reason varchar(500) NOT NULL, created_at timestamp DEFAULT CURRENT_TIMESTAMP)",
    # 056 (SC-AUTH-02)
    "CREATE TABLE IF NOT EXISTS workspace_identity_links (issuer varchar(255) NOT NULL, subject varchar(255) NOT NULL, "
    "user_key varchar(128) NOT NULL, status varchar(16) NOT NULL DEFAULT 'active', link_method varchar(32) NOT NULL, "
    "evidence_sha256 varchar(64), created_by varchar(128) NOT NULL, created_at timestamp DEFAULT CURRENT_TIMESTAMP, "
    "updated_at timestamp DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (issuer, subject), UNIQUE (issuer, user_key))",
    "CREATE TABLE IF NOT EXISTS workspace_identity_link_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, action varchar(32) NOT NULL, "
    "issuer varchar(255) NOT NULL, subject varchar(255) NOT NULL, user_key varchar(128) NOT NULL, actor varchar(128) NOT NULL, "
    "reason varchar(500) NOT NULL, evidence_sha256 varchar(64), created_at timestamp DEFAULT CURRENT_TIMESTAMP)",
    "CREATE TABLE IF NOT EXISTS workspace_revoked_idp_sessions (issuer varchar(255) NOT NULL, idp_sid varchar(255) NOT NULL, "
    "expires_at timestamp NOT NULL, revoked_at timestamp DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (issuer, idp_sid))",
)


def create_auth_hardening_tables(conn):
    for ddl in AUTH_HARDENING_TABLES:
        conn.execute(text(ddl))
