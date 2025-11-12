"""
Data transfer objects for storage operations.
"""

from __future__ import annotations

from dataclasses import dataclass


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