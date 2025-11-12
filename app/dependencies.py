"""
FastAPI dependencies (DB sessions, etc.).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from scraper.storage.connection import get_engine

# Reuse the same engine/session factory from scraper
_engine = get_engine()
_SessionLocal = None

def get_session_local():
    """Lazy initialization of session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _SessionLocal


def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.
    
    The session is automatically closed after the request completes.
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Type alias for convenience in route handlers
DbSession = Annotated[Session, Depends(get_db)]