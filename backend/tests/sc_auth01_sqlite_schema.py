"""SQLite equivalents of migration 055 tables for isolated SC-AUTH-01 unit tests."""
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
)


def create_auth_hardening_tables(conn):
    for ddl in AUTH_HARDENING_TABLES:
        conn.execute(text(ddl))
