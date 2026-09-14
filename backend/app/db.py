from functools import lru_cache
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .models import Base


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(
        settings.database_url,
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


def ping_database() -> None:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
