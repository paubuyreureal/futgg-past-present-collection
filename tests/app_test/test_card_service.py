"""
Tests for card service functions.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.card_service import toggle_card_in_club
from scraper.models import Player, PlayerCard


def test_toggle_card_in_club_found(db_session: Session):
    """Test toggling a card's in_club status when card exists."""
    player = Player(
        slug="test-player",
        display_name="Test Player",
        any_in_club=False,
        base_card_slug="test-card",
        base_card_rating=85,
        base_card_version="Rare",
        base_card_image_url="https://example.com/image.jpg",
    )
    db_session.add(player)
    db_session.commit()
    
    card = PlayerCard(
        player_id=player.id,
        card_slug="test-card-1",
        name="Test Player",
        rating=85,
        version="Rare",
        card_url="https://www.fut.gg/test-card-1",
        image_url="https://example.com/card1.jpg",
        in_club=False,
    )
    db_session.add(card)
    db_session.commit()
    
    result = toggle_card_in_club(db_session, "test-card-1", True)
    assert result is True
    
    db_session.refresh(card)
    assert card.in_club is True


def test_toggle_card_in_club_not_found(db_session: Session):
    """Test toggling a card's in_club status when card doesn't exist."""
    result = toggle_card_in_club(db_session, "nonexistent-card", True)
    assert result is False