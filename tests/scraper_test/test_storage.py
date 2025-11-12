"""
Unit tests for storage operations.

Note: These tests use a test database or in-memory SQLite.
You may want to set up pytest fixtures for database isolation.
"""

import pytest
from datetime import datetime, timezone

from scraper.storage import (
    CardPayload,
    upsert_players_and_cards,
    normalize_duplicate_display_names,
    assign_base_cards,
)
from scraper.models import Player, PlayerCard
from scraper.storage.connection import session_scope


@pytest.fixture
def sample_payloads():
    return [
        CardPayload(
            player_slug="test-player",
            display_name="Test Player",
            card_slug="123-test-player/26-123",
            name="Test Player",
            rating=85,
            version="Rare",
            card_url="https://www.fut.gg/players/123-test-player/26-123/",
            image_url="https://example.com/image.webp",
        ),
        CardPayload(
            player_slug="test-player",
            display_name="Test Player",
            card_slug="123-test-player/26-456",
            name="Test Player",
            rating=87,
            version="Icon",
            card_url="https://www.fut.gg/players/123-test-player/26-456/",
            image_url="https://example.com/image2.webp",
        ),
    ]


def test_card_payload_immutable():
    payload = CardPayload(
        player_slug="test",
        display_name="Test",
        card_slug="test/26-1",
        name="Test",
        rating=85,
        version="Rare",
        card_url="https://example.com",
        image_url=None,
    )
    with pytest.raises(Exception):  # dataclass frozen
        payload.rating = 90


def test_normalize_duplicate_display_names():
    # This test requires a test database setup
    # You'd create duplicate players, run the function, then verify
    pass  # Implement when you have test DB fixtures


def test_assign_base_cards_priority():
    # This test requires a test database setup
    # Create a player with multiple cards, verify base card selection
    pass  # Implement when you have test DB fixtures