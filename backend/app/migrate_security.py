"""Explicit additive security migration; run only after backup/restore acceptance."""
from pathlib import Path
import hashlib
from sqlalchemy import text
from .db import get_engine

MIGRATION = "051_workspace_session_revocation"

def migrate(engine=None):
    engine = engine or get_engine()
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Workspace security migration requires PostgreSQL")
    raw=(Path(__file__).resolve().parents[1]/"migrations"/(MIGRATION+".sql")).read_text()
    checksum=hashlib.sha256(raw.encode()).hexdigest()
    sql="\n".join(line for line in raw.splitlines() if line.strip().upper() not in {"BEGIN;", "COMMIT;"})
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(510501)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS workspace_security_migrations (migration_id varchar(100) PRIMARY KEY, checksum varchar(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())"))
        previous=conn.execute(text("SELECT checksum FROM workspace_security_migrations WHERE migration_id=:id"),{"id":MIGRATION}).scalar()
        if previous and previous!=checksum:
            raise RuntimeError("Workspace security migration checksum mismatch")
        conn.exec_driver_sql(sql)
        conn.execute(text("INSERT INTO workspace_security_migrations(migration_id,checksum) VALUES(:id,:checksum) ON CONFLICT DO NOTHING"),{"id":MIGRATION,"checksum":checksum})

def require_schema(engine=None):
    engine=engine or get_engine()
    with engine.connect() as conn:
        if conn.execute(text("SELECT migration_id FROM workspace_security_migrations WHERE migration_id=:id"),{"id":MIGRATION}).scalar()!=MIGRATION:
            raise RuntimeError("Workspace security migration required")
        conn.execute(text("SELECT token_fingerprint FROM workspace_revoked_sessions LIMIT 0"))

if __name__=="__main__":
    migrate()
    print("Workspace security migration 051 applied; no destructive downgrade")
