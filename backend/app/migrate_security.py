"""Explicit additive security migrations; run only after backup/restore acceptance."""
from pathlib import Path
import hashlib
from sqlalchemy import text
from .db import get_engine

# Ordered. 054 was 051 before SC-AUTH-01 G2 (051-053 are used on the release line).
MIGRATIONS = ("054_workspace_session_revocation", "055_workspace_auth_hardening")
MIGRATION = MIGRATIONS[0]
REQUIRED_TABLES = (
    "workspace_revoked_sessions",
    "workspace_used_nonces",
    "workspace_revoked_session_ids",
    "workspace_session_user_cutoffs",
    "workspace_session_revocation_audit",
)

def _read(migration_id):
    raw = (Path(__file__).resolve().parents[1] / "migrations" / (migration_id + ".sql")).read_text()
    checksum = hashlib.sha256(raw.encode()).hexdigest()
    sql = "\n".join(line for line in raw.splitlines() if line.strip().upper() not in {"BEGIN;", "COMMIT;"})
    return sql, checksum

def migrate(engine=None):
    engine = engine or get_engine()
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Workspace security migration requires PostgreSQL")
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(510501)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS workspace_security_migrations (migration_id varchar(100) PRIMARY KEY, checksum varchar(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())"))
        for migration_id in MIGRATIONS:
            sql, checksum = _read(migration_id)
            previous = conn.execute(text("SELECT checksum FROM workspace_security_migrations WHERE migration_id=:id"), {"id": migration_id}).scalar()
            if previous and previous != checksum:
                raise RuntimeError(f"Workspace security migration checksum mismatch: {migration_id}")
            conn.exec_driver_sql(sql)
            conn.execute(text("INSERT INTO workspace_security_migrations(migration_id,checksum) VALUES(:id,:checksum) ON CONFLICT DO NOTHING"), {"id": migration_id, "checksum": checksum})

def require_schema(engine=None):
    engine = engine or get_engine()
    with engine.connect() as conn:
        applied = set(conn.execute(text("SELECT migration_id FROM workspace_security_migrations")).scalars())
        missing = [m for m in MIGRATIONS if m not in applied]
        if missing:
            raise RuntimeError("Workspace security migration required: " + ", ".join(missing))
        for table in REQUIRED_TABLES:
            conn.execute(text(f"SELECT 1 FROM {table} LIMIT 0"))

if __name__ == "__main__":
    migrate()
    print("Workspace security migrations " + ", ".join(m[:3] for m in MIGRATIONS) + " applied; no destructive downgrade")
