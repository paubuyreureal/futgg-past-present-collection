"""
Player list endpoint (search, filter, sort).
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from app.dependencies import DbSession
from app.schemas.player import PlayerListItem
from app.services.player_service import get_players_list

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerListItem])
def list_players(
    db: DbSession,
    search: str | None = Query(None, description="Search players by name (accent-insensitive)"),
    in_club: Literal["all", "in_club", "not_in_club"] | None = Query(
        "all", description="Filter by in_club status"
    ),
    sort: Literal["asc", "desc"] = Query("desc", description="Sort by base card rating"),
) -> list[PlayerListItem]:
    """
    Get list of all players with optional search, filtering, and sorting.
    
    - **search**: Search term for player names (case and accent insensitive)
    - **in_club**: Filter to show only players with cards in club, without, or all
    - **sort**: Sort order by base card rating (ascending or descending)
    """
    in_club_filter = in_club if in_club != "all" else None
    return get_players_list(
        db,
        search=search,
        in_club_filter=in_club_filter,
        sort_by_rating=sort,
    )