"""
Database session management and persistence helpers (upserts, queries).
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

from sqlalchemy import create_engine, func, insert, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.dialects.postgresql import insert 

from .config import get_settings
from .models import Base, Player, PlayerCard

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


@dataclass(frozen=True)
class CardPayload:
    player_slug: str
    display_name: str
    card_slug: str
    name: str
    rating: int
    version: str
    card_url: str
    image_url: str | None
    in_club: bool = False


def upsert_players_and_cards(cards: Iterable[CardPayload]) -> None:
    payloads = list(cards)
    if not payloads:
        return

    with session_scope() as session:
        _ensure_players(session, payloads)
        _upsert_cards(session, payloads)
        _refresh_any_in_club(session, payloads)


def _ensure_players(session: Session, payloads: Sequence[CardPayload]) -> None:
    slugs = {payload.player_slug for payload in payloads}
    existing = {
        slug.lower()
        for (slug,) in session.execute(
            select(Player.slug).where(Player.slug.in_(slugs))
        )
    }

    new_players = []
    seen = set(existing)
    for payload in payloads:
        slug = payload.player_slug.lower()
        if slug in seen:
            continue
        seen.add(slug)
        new_players.append(
            {"slug": payload.player_slug, "display_name": payload.display_name}
        )

    if new_players:
        stmt = insert(Player).values(new_players)
        session.execute(stmt.on_conflict_do_nothing(index_elements=["slug"]))


def _upsert_cards(session: Session, payloads: Sequence[CardPayload]) -> None:
    unique_payloads: dict[str, CardPayload] = {}
    for payload in payloads:
        unique_payloads[payload.card_slug] = payload
    payloads = list(unique_payloads.values())
    player_id_map = {
        slug: player_id
        for slug, player_id in session.execute(
            select(Player.slug, Player.id).where(
                Player.slug.in_({payload.player_slug for payload in payloads})
            )
        )
    }

    insert_stmt = insert(PlayerCard).values(
        [
            {
                "player_id": player_id_map[payload.player_slug],
                "card_slug": payload.card_slug,
                "name": payload.name,
                "rating": payload.rating,
                "version": payload.version,
                "card_url": payload.card_url,
                "image_url": payload.image_url,
                "in_club": payload.in_club,
            }
            for payload in payloads
        ]
    )
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["card_slug"],
        set_={
            "name": insert_stmt.excluded.name,
            "rating": insert_stmt.excluded.rating,
            "version": insert_stmt.excluded.version,
            "card_url": insert_stmt.excluded.card_url,
            "image_url": insert_stmt.excluded.image_url,
            "last_seen_at": func.now(),
        },
    )
    session.execute(upsert_stmt)


def _refresh_any_in_club(session: Session, payloads: Sequence[CardPayload]) -> None:
    player_ids = list(
    session.scalars(
        select(Player.id).where(
            Player.slug.in_({payload.player_slug for payload in payloads})
        )
    )
)
    if not player_ids:
        return

    subquery = (
        select(PlayerCard.player_id, func.bool_or(PlayerCard.in_club).label("any"))
        .where(PlayerCard.player_id.in_(player_ids))
        .group_by(PlayerCard.player_id)
        .subquery()
    )
    session.execute(
        update(Player)
        .where(Player.id == subquery.c.player_id)
        .values(any_in_club=subquery.c.any)
    )