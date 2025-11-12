"""
Base card assignment logic.
"""

from __future__ import annotations

from .connection import session_scope
from ..models import Player

BASE_CARD_PRIORITY = ["Common", "Rare", "UT Heroes", "Icon"]


def assign_base_cards() -> int:
    """
    For each player, choose a base card according to the priority rules:
    1. Prefer versions in BASE_CARD_PRIORITY (in that order).
    2. If none found, pick the lowest rating card; tie-break by slug.
    Returns number of players updated.
    """
    updated = 0

    with session_scope() as session:
        players = session.query(Player).all()
        for player in players:
            cards = sorted(
                player.cards,
                key=lambda c: (
                    BASE_CARD_PRIORITY.index(c.version)
                    if c.version in BASE_CARD_PRIORITY else len(BASE_CARD_PRIORITY),
                    c.rating if c.version in BASE_CARD_PRIORITY else float("inf"),
                    c.card_slug,
                )
            )

            if not cards:
                continue

            # First, try to find best version card
            preferred = [
                card for card in cards if card.version in BASE_CARD_PRIORITY
            ]
            if preferred:
                base = sorted(
                    preferred,
                    key=lambda c: (
                        BASE_CARD_PRIORITY.index(c.version),
                        c.card_slug,
                    ),
                )[0]
            else:
                base = sorted(
                    cards,
                    key=lambda c: (c.rating, c.card_slug),
                )[0]

            if (
                player.base_card_slug != base.card_slug
                or player.base_card_rating != base.rating
                or player.base_card_version != base.version
                or player.base_card_image_url != base.image_url
            ):
                player.base_card_slug = base.card_slug
                player.base_card_rating = base.rating
                player.base_card_version = base.version
                player.base_card_image_url = base.image_url
                updated += 1

    return updated