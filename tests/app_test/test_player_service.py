"""
Tests for player service functions.
"""

import pytest
from sqlalchemy.orm import Session

from app.services.player_service import get_players_list, get_player_by_slug
from scraper.models import Player, PlayerCard


def test_get_players_list_empty(db_session: Session):
    """Test getting players list when database is empty."""
    result = get_players_list(db_session)
    assert result == []


def test_get_players_list_with_players(db_session: Session, sample_player: Player):
    """Test getting players list with one player."""
    result = get_players_list(db_session)
    assert len(result) == 1
    assert result[0].slug == "test-player"
    assert result[0].display_name == "Test Player"
    assert result[0].total_cards == 0
    assert result[0].in_club_count == 0


def test_get_players_list_with_cards(
    db_session: Session, sample_player: Player, sample_cards: list[PlayerCard]
):
    """Test getting players list with cards and counts."""
    result = get_players_list(db_session)
    assert len(result) == 1
    assert result[0].total_cards == 2
    assert result[0].in_club_count == 1  # One card has in_club=True


def test_get_players_list_search(db_session: Session, sample_player: Player):
    """Test searching players by name."""
    result = get_players_list(db_session, search="test")
    assert len(result) == 1
    
    result = get_players_list(db_session, search="nonexistent")
    assert len(result) == 0


def test_get_players_list_filter_in_club(
    db_session: Session, sample_player: Player, sample_cards: list[PlayerCard]
):
    """Test filtering players by in_club status."""
    # Update player's any_in_club flag
    sample_player.any_in_club = True
    db_session.commit()
    
    result = get_players_list(db_session, in_club_filter="in_club")
    assert len(result) == 1
    
    sample_player.any_in_club = False
    db_session.commit()
    
    result = get_players_list(db_session, in_club_filter="in_club")
    assert len(result) == 0


def test_get_players_list_sort_by_rating(
    db_session: Session, sample_player: Player
):
    """Test sorting players by rating."""
    # Create another player with different rating
    player2 = Player(
        slug="test-player-2",
        display_name="Test Player 2",
        any_in_club=False,
        base_card_slug="test-card-2",
        base_card_rating=90,
        base_card_version="Rare",
        base_card_image_url="https://example.com/image2.jpg",
    )
    db_session.add(player2)
    db_session.commit()
    
    result = get_players_list(db_session, sort_by_rating="desc")
    assert result[0].base_card_rating == 90
    assert result[1].base_card_rating == 85
    
    result = get_players_list(db_session, sort_by_rating="asc")
    assert result[0].base_card_rating == 85
    assert result[1].base_card_rating == 90


def test_get_player_by_slug_found(
    db_session: Session, sample_player: Player, sample_cards: list[PlayerCard]
):
    """Test getting a player by slug when found."""
    result = get_player_by_slug(db_session, "test-player")
    assert result is not None
    assert result.slug == "test-player"
    assert result.display_name == "Test Player"
    assert result.total_cards == 2
    assert result.in_club_count == 1
    assert len(result.cards) == 2


def test_get_player_by_slug_not_found(db_session: Session):
    """Test getting a player by slug when not found."""
    result = get_player_by_slug(db_session, "nonexistent")
    assert result is None