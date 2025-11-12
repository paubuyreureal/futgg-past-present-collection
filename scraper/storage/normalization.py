"""
Display name normalization utilities.
"""

from __future__ import annotations

from sqlalchemy import func, select

from .connection import session_scope
from ..models import Player


def normalize_duplicate_display_names() -> int:
    """
    For any display_name shared by multiple players, rewrite the display_name
    using the player's slug converted to title case (e.g., 'ronald-araujo' → 'Ronald Araujo').
    Returns the number of players that were updated.
    """
    with session_scope() as session:
        duplicates = [
            name for (name,) in session.execute(
                select(Player.display_name)
                .group_by(Player.display_name)
                .having(func.count(Player.id) > 1)
            )
        ]

        if not duplicates:
            return 0

        updated = 0
        for name in duplicates:
            players = session.execute(
                select(Player).where(Player.display_name == name)
            ).scalars()

            for player in players:
                pretty_name = player.slug.replace("-", " ").title()
                if player.display_name != pretty_name:
                    player.display_name = pretty_name
                    updated += 1

        return updated