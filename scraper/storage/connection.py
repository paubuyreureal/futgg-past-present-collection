"""
Database connection and session management.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings
from ..models import Base

_settings = get_settings()
_ENGINE: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    """Lazily create and cache the SQLAlchemy engine and session factory."""
    global _ENGINE, SessionLocal  # pylint: disable=global-statement
    if _ENGINE is None:
        engine = create_engine(
            _settings.database_url,
            pool_pre_ping=True,
        )
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        Base.metadata.bind = engine
        _ENGINE = engine
    return _ENGINE


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    if SessionLocal is None:
        get_engine()
    assert SessionLocal is not None  # for type checkers
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()