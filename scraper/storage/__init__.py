"""
Database storage package for ScrapeFutGG.

Public API:
- CardPayload: Data transfer object for card data
- session_scope: Context manager for database sessions
- upsert_players_and_cards: Main upsert function
- normalize_duplicate_display_names: Display name cleanup
- assign_base_cards: Base card assignment
"""

from .connection import session_scope
from .payloads import CardPayload
from .upserts import upsert_players_and_cards
from .normalization import normalize_duplicate_display_names
from .base_cards import assign_base_cards

__all__ = [
    "CardPayload",
    "session_scope",
    "upsert_players_and_cards",
    "normalize_duplicate_display_names",
    "assign_base_cards",
]