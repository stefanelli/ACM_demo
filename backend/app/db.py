"""Database engine, session factory, and declarative base.

The engine is created lazily so that importing `app.db` does not require a live
database connection (important for tests, CLI tools, and Alembic).
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


_engine = None
_session_factory = None


def get_engine():
    """Return (and cache) the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return (and cache) a session factory bound to the shared engine."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _session_factory


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a session and closes it afterwards."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
