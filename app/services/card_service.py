"""
Card operations business logic.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from scraper.models import PlayerCard


def toggle_card_in_club(db: Session, card_slug: str, in_club: bool) -> bool:
    """
    Toggle a card's in_club status.
    
    Parameters
    ----------
    db
        Database session
    card_slug
        Unique card slug identifier
    in_club
        New in_club value
    
    Returns
    -------
    bool
        True if card was found and updated, False otherwise
    """
    card = db.scalar(select(PlayerCard).where(PlayerCard.card_slug == card_slug))
    if not card:
        return False
    
    card.in_club = in_club
    db.commit()
    
    # Update player's any_in_club flag
    from scraper.storage.upserts import _refresh_any_in_club
    from scraper.storage.payloads import CardPayload
    
    # Create a minimal payload just to trigger the refresh
    # We only need player_slug for the refresh logic
    dummy_payload = CardPayload(
        player_slug=card.player.slug,
        display_name=card.player.display_name,
        card_slug=card.card_slug,
        name=card.name,
        rating=card.rating,
        version=card.version,
        card_url=card.card_url,
        image_url=card.image_url,
        in_club=in_club,
    )
    _refresh_any_in_club(db, [dummy_payload])
    db.commit()
    
    return True