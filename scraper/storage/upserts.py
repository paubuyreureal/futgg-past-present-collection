"""
Player and card upsert operations.
"""

from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import func, insert, select, update, Integer
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .connection import session_scope
from .payloads import CardPayload
from ..models import Player, PlayerCard


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

    # Use database-agnostic boolean aggregation
    # PostgreSQL: bool_or(), SQLite: MAX() (treats True=1, False=0)
    from sqlalchemy import inspect
    dialect_name = inspect(session.bind).dialect.name
    
    if dialect_name == "postgresql":
        any_expr = func.bool_or(PlayerCard.in_club)
    else:
        # SQLite and others: use MAX() which works for booleans
        # MAX(True, False) = True, MAX(False, False) = False
        any_expr = func.max(func.cast(PlayerCard.in_club, Integer))
    
    subquery = (
        select(PlayerCard.player_id, any_expr.label("any"))
        .where(PlayerCard.player_id.in_(player_ids))
        .group_by(PlayerCard.player_id)
        .subquery()
    )
    session.execute(
        update(Player)
        .where(Player.id == subquery.c.player_id)
        .values(any_in_club=subquery.c.any)
    )