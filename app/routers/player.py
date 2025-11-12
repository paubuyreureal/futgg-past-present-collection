"""
Single player detail endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.dependencies import DbSession
from app.schemas.player import PlayerDetail
from app.services.player_service import get_player_by_slug

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/{slug}", response_model=PlayerDetail)
def get_player(slug: str, db: DbSession) -> PlayerDetail:
    """
    Get detailed information about a specific player including all their cards.
    
    - **slug**: Player slug identifier (e.g., "ronald-araujo")
    """
    player = get_player_by_slug(db, slug)
    if not player:
        raise HTTPException(status_code=404, detail=f"Player with slug '{slug}' not found")
    return player