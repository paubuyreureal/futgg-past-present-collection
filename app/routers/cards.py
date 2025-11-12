"""
Card operations (toggle in_club).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.dependencies import DbSession
from app.schemas.card import CardUpdate
from app.services.card_service import toggle_card_in_club

router = APIRouter(prefix="/cards", tags=["cards"])


@router.patch("/{card_slug}/club", status_code=204)
def update_card_club_status(
    card_slug: str,
    update: CardUpdate,
    db: DbSession,
) -> None:
    """
    Toggle a card's in_club status.
    
    - **card_slug**: Unique card slug identifier
    - **update**: Request body with new in_club boolean value
    
    Automatically updates the player's any_in_club flag.
    """
    success = toggle_card_in_club(db, card_slug, update.in_club)
    if not success:
        raise HTTPException(
            status_code=404, detail=f"Card with slug '{card_slug}' not found"
        )