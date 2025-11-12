"""API route handlers."""

from .cards import router as cards_router
from .player import router as player_router
from .players import router as players_router
from .scrape import router as scrape_router

__all__ = ["cards_router", "player_router", "players_router", "scrape_router"]