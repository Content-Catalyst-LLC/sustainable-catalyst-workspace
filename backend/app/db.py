from functools import lru_cache
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base


@lru_cache
def get_engine():
    settings = get_settings()
    database_url = settings.database_url
    secret_file = getattr(settings, "database_url_file", "").strip()
    if secret_file:
        database_url = Path(secret_file).read_text(encoding="utf-8").strip()
        if not database_url.startswith("postgresql+psycopg://"):
            raise RuntimeError("Private Workspace database credential invalid")
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
    )


@lru_cache
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session)


def session_scope():
    return get_session_factory()()


def initialize_schema() -> None:
    Base.metadata.create_all(bind=get_engine())
    settings = get_settings()
    if settings.session_revocation_enforced or getattr(settings, "sc_identity_required", False):
        from .migrate_security import require_schema
        require_schema(get_engine())


def ping_database() -> None:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
